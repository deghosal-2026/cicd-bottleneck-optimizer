"""LangGraph node for profiling job timing from run data."""

from lib.profiler import profile, parse_job_graph


def profile_jobs_node(state: dict) -> dict:
    runs = state.get("runs", [])
    workflows = state.get("workflows", [])

    for wf in workflows:
        wf["jobs"] = parse_job_graph(wf)

    profiles = profile(runs, workflows)
    if not profiles:
        print("  No job timing data to profile.")

    return {"profiles": profiles, "workflows": workflows, "errors": state.get("errors", [])}
