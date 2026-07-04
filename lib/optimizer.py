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
            saved = max(median_sec // 120, 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Add actions/cache to '{job_name}' to cache dependencies and avoid re-downloading every run",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * CACHE_COST_PER_GB_MONTH * 10, 2),
                "risk_level": "low",
                "yaml_diff_hint": f"Add `- uses: actions/cache@v4` step before dependency install in '{job_name}'",
            })

        elif btype == "serial_parallel":
            saved = max(median_sec // 90, 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Remove 'needs:' from '{job_name}' so it runs in parallel with other independent jobs",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": 0.0,
                "risk_level": "medium",
                "yaml_diff_hint": f"Ensure '{job_name}' has no `needs:` blocking parallel execution",
            })

        elif btype == "redundant_matrix":
            saved = max(int(median_sec // 180), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Reduce matrix dimensions in '{job_name}' to eliminate redundant OS/language combinations",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "high",
                "yaml_diff_hint": f"Reduce `strategy.matrix` dimensions in '{job_name}' to remove overlap",
            })

        elif btype == "redundant_rebuild":
            saved = max(int(median_sec // 150), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Use actions/upload-artifact and actions/download-artifact in '{job_name}' to reuse build outputs",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": round(saved * RUNNER_COST_PER_MIN, 2),
                "risk_level": "medium",
                "yaml_diff_hint": f"Add `actions/upload-artifact` to build job and `actions/download-artifact` to '{job_name}'",
            })

        elif btype == "oversized_context":
            saved = max(int(median_sec // 200), 1)
            optimizations.append({
                "id": _make_id(btype, job_name),
                "bottleneck_type": btype,
                "job_name": job_name,
                "description": f"Add .dockerignore to '{job_name}' to exclude node_modules, .git, and build artifacts from Docker context",
                "estimated_time_saved_min": saved,
                "estimated_cost_per_run": 0.0,
                "risk_level": "low",
                "yaml_diff_hint": f"Create `.dockerignore` excluding node_modules, .git, and other build artifacts",
            })

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
