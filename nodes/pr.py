"""LangGraph nodes for human-in-the-loop and PR operations."""

import uuid
from datetime import datetime
from lib.cli import trade_off_table, prompt_re_analyze_or_recompute, summary_table
from tools.github import GitHubClient


def interrupt_node(state: dict) -> dict:
    optimizations = state.get("optimizations", [])
    bottlenecks = state.get("bottlenecks", [])

    selected_ids, approved = trade_off_table(optimizations, bottlenecks)

    return {
        "selected_optimizations": selected_ids,
        "human_approved": approved,
        "errors": state.get("errors", []),
    }


def open_pr_node(state: dict, client: GitHubClient) -> dict:
    repo = state.get("repo_url", "")
    rewritten = state.get("rewritten_yaml", "")
    optimizations = state.get("optimizations", [])
    selected_ids = state.get("selected_optimizations", [])
    bottlenecks = state.get("bottlenecks", [])
    profiles = state.get("profiles", [])
    workflows = state.get("workflows", [])

    if not rewritten or not repo:
        return {**state, "pr_url": None, "errors": state.get("errors", []) + ["No YAML to commit"]}

    selected = [o for o in optimizations if o["id"] in selected_ids]
    slug = _make_slug(selected)
    branch = f"ci-optimizer/{slug}-{uuid.uuid4().hex[:6]}"

    workflow_path = workflows[0].get("filename", "workflow.yml") if workflows else "workflow.yml"
    if not workflow_path.endswith(".yml"):
        workflow_path += ".yml"

    try:
        client.create_branch(repo, branch)
        client.create_commit(repo, branch, f".github/workflows/{workflow_path}", rewritten)
    except Exception as e:
        return {**state, "pr_url": None, "errors": state.get("errors", []) + [f"Failed to create branch/commit: {e}"]}

    title = _make_title(selected)
    body = _make_pr_body(repo, selected, bottlenecks, profiles, rewritten, branch)

    try:
        pr_url = client.create_pr(repo, branch, title, body)
    except Exception as e:
        return {**state, "pr_url": None, "errors": state.get("errors", []) + [f"Failed to create PR: {e}"]}

    print(f"  PR opened: {pr_url}")

    return {
        "pr_url": pr_url,
        "rewritten_yaml_path": f".github/workflows/{workflow_path}",
        "errors": state.get("errors", []),
    }


def _make_slug(optimizations: list[dict]) -> str:
    if not optimizations:
        return "optimize"
    desc = optimizations[0].get("description", "optimize")
    slug = desc.lower().replace(" ", "-")[:30]
    import re
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug.strip("-")


def _make_title(optimizations: list[dict]) -> str:
    if not optimizations:
        return "ci-optimizer: workflow optimization"
    types = list({o.get("bottleneck_type", "optimize") for o in optimizations})
    return f"ci-optimizer: {', '.join(types)} — {len(optimizations)} optimizations"


def _make_pr_body(repo: str, optimizations: list[dict], bottlenecks: list[dict],
                  profiles: list[dict], rewritten_yaml: str, branch: str) -> str:
    lines = [
        f"## CI/CD Optimization Report for {repo}",
        "",
        f"**Branch:** `{branch}`",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    if bottlenecks:
        lines += ["### Bottlenecks Found", "", "| Type | Job | Severity |", "|---|---|---|"]
        for b in bottlenecks:
            lines.append(f"| {b['type']} | {b['job_name']} | {b['severity']} |")
        lines.append("")

    if optimizations:
        total_saved = sum(o.get("estimated_time_saved_min", 0) for o in optimizations)
        total_cost = sum(o.get("estimated_cost_per_run", 0) for o in optimizations)

        lines += ["### Optimizations Applied", "", "| Description | Job | Saved | Cost/Run | Risk |", "|---|---|---|---|---|"]
        for o in optimizations:
            lines.append(f"| {o['description'][:60]} | {o['job_name']} | {o['estimated_time_saved_min']}m | ${o['estimated_cost_per_run']:.2f} | {o['risk_level']} |")
        lines.append("")

        if profiles:
            lines += ["### Before/After Timing", "", "| Job | Before | After (estimated) | Savings |", "|---|---|---|---|"]
            for p in profiles:
                before = f"{p['median_sec']}s"
                # Find matching optimization to estimate savings
                matching = [o for o in optimizations if o['job_name'] == p['job_name']]
                saved_sec = sum(o['estimated_time_saved_min'] * 60 for o in matching) if matching else 0
                after = f"{max(p['median_sec'] - saved_sec, 0)}s"
                savings = f"{p['median_sec'] - max(p['median_sec'] - saved_sec, 0)}s"
                lines.append(f"| {p['job_name']} | {before} | {after} | {savings} |")
            lines.append("")

        lines += [
            "### Trade-offs",
            "",
            f"- **Total time saved:** ~{total_saved} min per run",
            f"- **Additional cost:** ${total_cost:.2f} per run (cache storage)",
            f"- **Risk:** {_max_risk(optimizations)}",
            "- Human review required before merging",
            "",
        ]

    lines += [
        "### Validation",
        "",
        "- ✅ YAML syntax validated",
        "- ⏳ `act` dry-run (optional, requires local setup)",
        "",
        "---",
        f"_Generated by [CI/CD Bottleneck Optimizer](https://github.com/deghosal-2026/cicd-bottleneck-optimizer)_",
        "",
    ]

    return "\n".join(lines)


def _max_risk(optimizations: list[dict]) -> str:
    risks = [o.get("risk_level", "low") for o in optimizations]
    if "high" in risks:
        return "high"
    if "medium" in risks:
        return "medium"
    return "low"
