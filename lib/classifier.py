import hashlib
import json
from typing import Any

RUNNER_COST_PER_MIN = 0.008
CACHE_COST_PER_GB_MONTH = 0.007

_LLM_CACHE: dict[str, list[dict]] = {}

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
    cached_jobs: set[str] = set()

    for wf in workflows:
        jobs = wf.get("jobs", [])
        if jobs:
            bottlenecks.extend(_check_missing_cache(jobs, profiles))
            bottlenecks.extend(_check_serial_parallel(jobs, profiles))
            bottlenecks.extend(_check_redundant_matrix(jobs, profiles))
            for job in jobs:
                steps = job.get("steps", [])
                if any(isinstance(s, dict) and "cache" in str(s.get("uses", "")).lower() for s in steps):
                    cached_jobs.add(job["name"])

    if not bottlenecks:
        bottlenecks.extend(_check_profiles_only(profiles, cached_jobs))

    if llm_client is not None:
        llm_bottlenecks = _classify_with_llm(llm_client, workflows, profiles)
        bottlenecks = _merge_bottlenecks(bottlenecks, llm_bottlenecks)

    return bottlenecks


def _check_profiles_only(profiles: list[dict], cached_jobs: set[str] | None = None) -> list[dict]:
    if cached_jobs is None:
        cached_jobs = set()
    bottlenecks = []
    BUILD_KEYWORDS = ("build", "test", "lint", "deploy", "compile", "bundle", "package")
    seen = set()

    for p in profiles:
        name = p["job_name"]
        if name in cached_jobs:
            continue
        lower = name.lower()
        median = p.get("median_sec", 0)

        if median < 30:
            continue

        if any(kw in lower for kw in BUILD_KEYWORDS):
            key = ("missing_cache", name)
            if key not in seen:
                seen.add(key)
                bottlenecks.append({
                    "type": "missing_cache",
                    "job_name": name,
                    "evidence": f"Job '{name}' ({median}s median) builds dependencies but has no cache directive.",
                    "severity": _assign_severity(median),
                })

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

        if has_cache:
            continue

        # Only flag jobs that have install/build steps (not meta jobs like label automation)
        has_install = any(
            isinstance(s, dict) and any(
                kw in str(s.get("run", "")).lower()
                for kw in ("install", "build", "npm ", "pip ", "cargo ", "go build", "make")
            )
            for s in steps
        )
        if not has_install:
            continue

        profile = profile_map.get(name)
        median_time = profile["median_sec"] if profile else 0

        # Skip very short jobs — not worth optimizing
        if median_time > 0 and median_time < 30:
            continue

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

    # Flag jobs that HAVE needs: dependencies — they run sequentially after deps.
    # In GitHub Actions, jobs without needs: already run in parallel.
    for job in jobs:
        needs = job.get("needs")
        if not needs:
            continue

        steps = job.get("steps", [])
        has_real_work = any(
            isinstance(s, dict) and any(
                kw in str(s.get("run", "")).lower()
                for kw in ("install", "build", "test", "npm ", "pip ", "cargo ", "go ", "make")
            )
            for s in steps
        )
        if not has_real_work:
            continue

        name = job["name"]
        profile = profile_map.get(name)
        median_time = profile["median_sec"] if profile else 0
        if median_time > 0 and median_time < 30:
            continue
        severity = _assign_severity(median_time)

        deps = needs if isinstance(needs, list) else [needs]
        bottlenecks.append({
            "type": "serial_parallel",
            "job_name": name,
            "evidence": (
                f"Job '{name}' depends on {deps} via `needs:` and waits for them to complete. "
                f"Median time: {_fmt_time(median_time)}. "
                f"If this job doesn't use their outputs, removing `needs:` would let it run in parallel."
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
        if not matrix or not isinstance(matrix, dict):
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

    cache_key = _workflow_cache_key(workflows)
    if cache_key in _LLM_CACHE:
        print(f"    → LLM classify: cache hit ({len(workflows)} workflow(s))", flush=True)
        return _LLM_CACHE[cache_key]

    prompt_parts = [
        "You are a CI/CD expert. Analyze these GitHub Actions workflow YAML files for bottlenecks.",
        "",
    ]

    MAX_WORKFLOWS = 2
    wf_count = 0
    for wf in workflows:
        content = wf.get("content", "")
        if not content:
            continue
        wf_count += 1
        if wf_count > MAX_WORKFLOWS:
            break
        jobs = wf.get("jobs", [])
        job_timings = []
        for job in jobs:
            p = profile_map.get(job["name"], {})
            job_timings.append(f"  {job['name']}: {p.get('median_sec', 0)}s median")
        
        prompt_parts.append(f"### Workflow: {wf.get('filename', 'unknown')}")
        if job_timings:
            prompt_parts.append("Job timings:")
            prompt_parts.extend(job_timings)
        prompt_parts.append("")
        prompt_parts.append("```yaml")
        prompt_parts.append(content)
        prompt_parts.append("```")
        prompt_parts.append("")

    prompt_parts.extend([
        "Find these bottleneck types:",
        "- redundant_rebuild: same dependency/artifact built from scratch in multiple jobs instead of shared",
        "- oversized_context: docker build with no .dockerignore, or checkout fetching entire repo history",
        "- missing_cache: no actions/cache or cache directive (but only flag if job > 120s)",
        "",
        "Return ONLY a JSON array. Each object must have: type, job_name, evidence, severity.",
        "Example:",
        '[{"type":"redundant_rebuild","job_name":"build","evidence":"npm install runs in both build (420s) and test (360s) jobs independently. Sharing artifacts would save 360s.","severity":"high"}]',
        "",
        "If no issues, return []",
    ])

    print(f"    → LLM classify ({len(workflows)} workflow(s))...", flush=True)
    try:
        raw = llm_client.call_local("\n".join(prompt_parts))
    except ConnectionError:
        print("    → OMLX not reachable. Skipping LLM classification.", flush=True)
        return []

    bottlenecks = _parse_llm_bottlenecks(raw)
    if cache_key:
        _LLM_CACHE[cache_key] = bottlenecks
    return bottlenecks


def _workflow_cache_key(workflows: list[dict]) -> str:
    h = hashlib.sha256()
    for wf in workflows:
        content = wf.get("content", "")
        if content:
            h.update(content.encode())
            h.update(b"\x00")
    return h.hexdigest()[:16] if h.digest() != b"\x00" * 32 else ""


def _parse_llm_bottlenecks(raw: str) -> list[dict]:
    VALID_TYPES = {"redundant_rebuild", "oversized_context", "missing_cache"}
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
        job_name = item.get("job_name", "")
        if btype not in VALID_TYPES or not job_name:
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
