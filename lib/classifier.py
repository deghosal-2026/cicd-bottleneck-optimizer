import json
from typing import Any

RUNNER_COST_PER_MIN = 0.008
CACHE_COST_PER_GB_MONTH = 0.007

CLASSIFY_LLM_PROMPT = """You are a CI/CD workflow analyzer. Identify bottlenecks.

Valid types: "redundant_rebuild" (same artifact rebuilt across jobs), "oversized_context" (large context, no .dockerignore).

Return ONLY valid JSON array. Example response:
[{"type":"redundant_rebuild","job_name":"build","evidence":"npm install runs in both build and test jobs (300s each).","severity":"high"}]

If no issues, return [].
No markdown, no explanation, no code fences. Only raw JSON array."""


def classify(profiles: list[dict], workflows: list[dict], llm_client=None) -> list[dict]:
    if not profiles:
        return []

    bottlenecks: list[dict] = []

    for wf in workflows:
        jobs = wf.get("jobs", [])
        if not jobs:
            continue

        bottlenecks.extend(_check_missing_cache(jobs, profiles))
        bottlenecks.extend(_check_serial_parallel(jobs, profiles))
        bottlenecks.extend(_check_redundant_matrix(jobs, profiles))

    if llm_client is not None:
        llm_bottlenecks = _classify_with_llm(llm_client, workflows, profiles)
        bottlenecks = _merge_bottlenecks(bottlenecks, llm_bottlenecks)

    return bottlenecks


def _check_missing_cache(jobs: list[dict], profiles: list[dict]) -> list[dict]:
    bottlenecks = []
    profile_map = {p["job_name"]: p for p in profiles}

    for job in jobs:
        name = job["name"]
        steps = job.get("steps", [])

        has_cache = any(
            isinstance(s, dict) and "cache" in str(s.get("uses", "")).lower()
            for s in steps
        )

        if not has_cache:
            profile = profile_map.get(name)
            median_time = profile["median_sec"] if profile else 0
            severity = _assign_severity(median_time)

            bottlenecks.append({
                "type": "missing_cache",
                "job_name": name,
                "evidence": (
                    f"No `cache:` directive found in job '{name}'. "
                    f"Median time: {_fmt_time(median_time)}. "
                    f"Adding cache would reduce dependency download time."
                ),
                "severity": severity,
            })

    return bottlenecks


def _check_serial_parallel(jobs: list[dict], profiles: list[dict]) -> list[dict]:
    bottlenecks = []
    profile_map = {p["job_name"]: p for p in profiles}

    independent_jobs = [j for j in jobs if not j.get("needs")]
    if len(independent_jobs) < 2:
        return []

    for job in independent_jobs:
        name = job["name"]
        profile = profile_map.get(name)
        median_time = profile["median_sec"] if profile else 0
        severity = _assign_severity(median_time)

        bottlenecks.append({
            "type": "serial_parallel",
            "job_name": name,
            "evidence": (
                f"Job '{name}' has no dependencies (`needs:`) but runs "
                f"sequentially with other independent jobs. "
                f"Median time: {_fmt_time(median_time)}. "
                f"Moving to parallel would reduce wall-clock time."
            ),
            "severity": severity,
        })

    return bottlenecks


def _check_redundant_matrix(jobs: list[dict], profiles: list[dict]) -> list[dict]:
    bottlenecks = []
    profile_map = {p["job_name"]: p for p in profiles}

    for job in jobs:
        name = job["name"]
        matrix = job.get("matrix")
        if not matrix:
            continue

        dimensions = {k: v for k, v in matrix.items() if isinstance(v, list)}
        if len(dimensions) < 2:
            continue

        profile = profile_map.get(name)
        median_time = profile["median_sec"] if profile else 0
        severity = _assign_severity(median_time)

        combos = 1
        for vals in dimensions.values():
            combos *= len(vals)

        bottlenecks.append({
            "type": "redundant_matrix",
            "job_name": name,
            "evidence": (
                f"Job '{name}' uses {len(dimensions)} matrix dimensions "
                f"({_fmt_dims(dimensions)}) producing {combos} combinations. "
                f"Median time: {_fmt_time(median_time)}. "
                f"Reducing dimensions would cut runner time linearly."
            ),
            "severity": severity,
        })

    return bottlenecks


def _assign_severity(median_sec: int) -> str:
    if median_sec >= 600:
        return "high"
    if median_sec >= 180:
        return "medium"
    return "low"


def _fmt_time(sec: int) -> str:
    if sec >= 60:
        return f"{sec // 60}m {sec % 60}s"
    return f"{sec}s"


def _fmt_dims(dims: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in dims.items())


def _classify_with_llm(llm_client, workflows: list[dict], profiles: list[dict]) -> list[dict]:
    profile_map = {p["job_name"]: p for p in profiles}

    workflow_summary = []
    for wf in workflows:
        jobs = wf.get("jobs", [])
        for job in jobs:
            p = profile_map.get(job["name"], {})
            workflow_summary.append({
                "name": job["name"],
                "steps": [s.get("uses", s.get("run", "")) for s in job.get("steps", [])[:10]],
                "median_sec": p.get("median_sec", 0),
                "needs": job.get("needs", []),
                "has_dockerignore": False,
            })

    prompt_parts = ["Analyze these workflow jobs for redundant rebuilds or oversized build context:\n"]
    for job in workflow_summary:
        prompt_parts.append(
            f"- {job['name']} ({job['median_sec']}s median): steps={job['steps']}, "
            f"needs={job['needs']}"
        )
    prompt_parts.append(
        "\nReturn ONLY a JSON array of bottlenecks (redundant_rebuild, oversized_context). "
        "If none found, return []."
    )

    try:
        raw = llm_client.call_local("\n".join(prompt_parts))
    except ConnectionError:
        print("OMLX down. Use cloud? (y/n): ", end="")
        choice = input().strip().lower()
        if choice == "y":
            try:
                raw = llm_client.call_openai("\n".join(prompt_parts))
            except ConnectionError:
                print("Cloud LLM also unavailable. Skipping LLM classification.")
                return []
        else:
            print("LLM classification skipped.")
            return []

    return _parse_llm_bottlenecks(raw)


def _parse_llm_bottlenecks(raw: str) -> list[dict]:
    VALID_TYPES = {"redundant_rebuild", "oversized_context"}
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    results = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        btype = item.get("type", "")
        if btype not in VALID_TYPES:
            continue
        item.setdefault("severity", "medium")
        item.setdefault("evidence", "Identified by LLM analysis.")
        results.append(item)

    return results


def _merge_bottlenecks(rules: list[dict], llm: list[dict]) -> list[dict]:
    seen = set()
    merged = []

    for b in rules + llm:
        key = (b["type"], b["job_name"])
        if key not in seen:
            seen.add(key)
            merged.append(b)

    return merged
