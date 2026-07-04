import json
import uuid
from typing import Any

RUNNER_COST_PER_MIN = 0.008
CACHE_COST_PER_GB_MONTH = 0.007


def propose(bottlenecks: list[dict], profiles: list[dict], llm_client=None) -> list[dict]:
    if not bottlenecks:
        return []

    optimizations: list[dict] = []

    for b in bottlenecks:
        btype = b["type"]
        job_name = b["job_name"]
        median_sec = _get_median(profiles, job_name)

        if btype == "missing_cache":
            saved = max(median_sec // 60, 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Add cache directive to '{job_name}' to avoid re-downloading dependencies every run.",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "low",
                "yaml_diff_hint": f"Add `- uses: actions/cache@v4` step before dependency install in '{job_name}'",
            })

        elif btype == "serial_parallel":
            saved = max(median_sec // 60, 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Run '{job_name}' in parallel with other independent jobs to reduce wall-clock time.",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": 0.0,
                "risk_level": "medium",
                "yaml_diff_hint": f"Ensure '{job_name}' has no `needs:` blocking parallel execution",
            })

        elif btype == "redundant_matrix":
            saved = max(int(median_sec // 60 * 0.5), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Reduce matrix dimensions in '{job_name}' to eliminate redundant combinations.",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "high",
                "yaml_diff_hint": f"Reduce `strategy.matrix` dimensions in '{job_name}' to remove overlap",
            })

        elif btype == "redundant_rebuild":
            saved = max(int(median_sec // 60 * 0.4), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Use cached artifacts or shared workspace to avoid rebuilding in '{job_name}'.",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "medium",
                "yaml_diff_hint": f"Add `actions/upload-artifact` to build job and `actions/download-artifact` to '{job_name}'",
            })

        elif btype == "oversized_context":
            saved = max(int(median_sec // 60 * 0.3), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Add .dockerignore to '{job_name}' to exclude unnecessary files from build context.",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "low",
                "yaml_diff_hint": f"Create `.dockerignore` excluding node_modules, .git, and other build artifacts",
            })

    if llm_client and optimizations:
        _enhance_with_llm(optimizations, bottlenecks, profiles, llm_client)

    return optimizations


def simulate(optimizations: list[dict]) -> int:
    return sum(o.get("estimated_time_saved_min", 0) for o in optimizations)


def _get_median(profiles: list[dict], job_name: str) -> int:
    for p in profiles:
        if p.get("job_name") == job_name:
            return p.get("median_sec", 0)
    return 0


def _make_id(btype: str, job_name: str) -> str:
    short = job_name.replace(" ", "-").lower()[:20]
    return f"{btype}-{short}-{uuid.uuid4().hex[:6]}"


def _enhance_with_llm(optimizations: list[dict], bottlenecks: list[dict], profiles: list[dict], llm_client) -> None:
    prompt_parts = ["Refine these CI/CD optimizations with better descriptions and time estimates:"]
    for opt in optimizations:
        prompt_parts.append(
            f"- {opt['bottleneck_type']} on {opt['job_name']}: "
            f"saves ~{opt['estimated_time_saved_min']}min, "
            f"cost ${opt['estimated_cost_per_run']}/run, "
            f"risk={opt['risk_level']}"
        )
    prompt_parts.append(
        '\nReturn a JSON array of refined optimizations. Each object must have: '
        'description, estimated_time_saved_min, risk_level. '
        'Example: [{"description":"Add pip cache to build job","estimated_time_saved_min":5,"risk_level":"low"}]'
    )

    try:
        raw = llm_client.call_local("\n".join(prompt_parts))
    except ConnectionError:
        return

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        refinements = json.loads(cleaned)
        if not isinstance(refinements, list):
            return
        for i, ref in enumerate(refinements):
            if i < len(optimizations) and isinstance(ref, dict):
                if "description" in ref:
                    optimizations[i]["description"] = ref["description"]
                if "estimated_time_saved_min" in ref:
                    optimizations[i]["estimated_time_saved_min"] = ref["estimated_time_saved_min"]
                if "risk_level" in ref:
                    optimizations[i]["risk_level"] = ref["risk_level"]
    except (json.JSONDecodeError, TypeError):
        pass
