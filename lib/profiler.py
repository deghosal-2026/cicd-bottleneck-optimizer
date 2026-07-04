import statistics
from typing import Any


def parse_job_graph(workflow: dict) -> list[dict]:
    content = workflow.get("content", "")
    if not content:
        return []

    import yaml
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML: {e}")

    if not parsed:
        return []

    jobs = parsed.get("jobs", {})
    if not jobs:
        return []

    result = []
    for name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        result.append({
            "name": name,
            "steps": job.get("steps", []),
            "needs": job.get("needs", []),
            "runs_on": job.get("runs-on", "ubuntu-latest"),
            "matrix": job.get("strategy", {}).get("matrix") if isinstance(job.get("strategy"), dict) else None,
        })

    return result


def profile(runs: list[dict], workflows: list[dict]) -> list[dict]:
    if not runs or not workflows:
        return []

    job_durations: dict[str, list[int]] = {}
    job_failures: dict[str, int] = {}
    job_totals: dict[str, int] = {}

    for run in runs:
        jobs_list = run.get("jobs", [])
        if not jobs_list:
            for job_run in run.get("jobs_list", []):
                _accumulate_job(job_run, job_durations, job_failures, job_totals)
        else:
            for job_run in jobs_list:
                _accumulate_job(job_run, job_durations, job_failures, job_totals)

    if not job_durations:
        return []

    profiles = []
    for job_name in job_durations:
        durations = sorted(job_durations[job_name])
        n = len(durations)
        if n == 0:
            continue
        profiles.append({
            "job_name": job_name,
            "median_sec": int(statistics.median(durations)),
            "p90_sec": _percentile(durations, 90),
            "p99_sec": _percentile(durations, 99),
            "failure_rate": round(job_failures.get(job_name, 0) / max(job_totals.get(job_name, 1), 1), 2),
            "cache_hit_ratio": None,
        })

    return profiles


def estimate_cache_hit_ratio(run: dict) -> float | None:
    logs = run.get("logs", [])
    if not logs:
        return None

    hits = 0
    misses = 0
    total = 0

    for line in logs:
        if not isinstance(line, str):
            continue
        lower = line.lower()
        if "cache hit" in lower or "cache restored" in lower or "cache @ " in lower:
            hits += 1
            total += 1
        elif "cache miss" in lower or "no cache found" in lower or "cache not found" in lower:
            misses += 1
            total += 1

    if total == 0:
        return None

    return round(hits / total, 2)


def _accumulate_job(job_run: dict, durations: dict, failures: dict, totals: dict) -> None:
    name = job_run.get("name", "unknown")
    duration = job_run.get("duration_sec")
    if duration is None:
        started = job_run.get("started_at")
        completed = job_run.get("completed_at")
        if started and completed:
            from datetime import datetime
            try:
                t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                duration = int((t1 - t0).total_seconds())
            except (ValueError, TypeError):
                return
        else:
            return

    if name not in durations:
        durations[name] = []
        failures[name] = 0
        totals[name] = 0

    durations[name].append(duration)
    totals[name] += 1
    status = job_run.get("status", "")
    if status in ("failure", "cancelled"):
        failures[name] += 1


def _percentile(sorted_values: list[int], p: int) -> int:
    if not sorted_values:
        return 0
    n = len(sorted_values)
    k = (p / 100.0) * (n - 1)
    f = int(k)
    c = f + 1
    if c >= n:
        return sorted_values[-1]
    return int(sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f]))
