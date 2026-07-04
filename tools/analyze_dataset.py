import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.profiler import parse_job_graph, profile
from lib.classifier import classify
from lib.optimizer import propose, simulate
from llm.client import LLMClient


def parse_args():
    parser = argparse.ArgumentParser(description="Run analysis on downloaded dataset")
    parser.add_argument("--data-dir", default="data", help="Dataset directory")
    parser.add_argument("--output-dir", default="reports", help="Reports output directory")
    parser.add_argument("--max-prs", type=int, default=0, help="Max PRs to process (0=all)")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM classification")
    return parser.parse_args()


def load_pr(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def build_workflows(pr: dict, pr_path: str) -> list[dict]:
    repo_dir = os.path.dirname(os.path.dirname(pr_path))  # data/<repo>/
    workflows = []
    for wf_ref in pr.get("workflows", []):
        wf_path = os.path.join(repo_dir, "workflows", f'{wf_ref["hash"]}.yml')
        content = ""
        if os.path.exists(wf_path):
            with open(wf_path) as f:
                content = f.read()
        wf = {"filename": wf_ref["filename"], "content": content, "jobs": []}
        if content:
            wf["jobs"] = parse_job_graph(wf)
        workflows.append(wf)
    return workflows


def build_profiles(pr: dict) -> list[dict]:
    all_jobs = []
    for run in pr.get("ci_runs", []):
        for job in run.get("jobs", []):
            if job.get("duration_sec", 0) > 0:
                all_jobs.append(job)
    if not all_jobs:
        return []

    profiles_data = [
        {
            "job_name": j["name"],
            "median_sec": j["duration_sec"],
            "p90_sec": j["duration_sec"],
            "p99_sec": j["duration_sec"],
            "failure_rate": 0.0 if j.get("status") == "success" else 0.5,
            "cache_hit_ratio": None,
        }
        for j in all_jobs
    ]
    return profiles_data


def save_report(repo_label: str, pr: dict, profiles: list, bottlenecks: list, optimizations: list, output_dir: str) -> str:
    pr_num = pr["pr_number"]
    report_dir = os.path.join(output_dir, repo_label)
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{pr_num}-analysis.md")

    lines = [
        f"# PR #{pr_num} — {pr.get('title', '')}",
        f"",
        f"- **Repo:** {repo_label}",
        f"- **Author:** {pr.get('author', '')}",
        f"- **State:** {pr.get('state', '')}",
        f"- **Head SHA:** {pr.get('head_sha', '')[:12]}",
        f"- **Created:** {pr.get('created_at', '')[:10]}",
        f"- **CI runs:** {len(pr.get('ci_runs', []))}",
        f"",
    ]

    if profiles:
        lines.append("## Job Profiles")
        lines.append("")
        lines.append("| Job | Median | Status |")
        lines.append("|---|---|---|")
        for p in profiles:
            lines.append(f"| {p['job_name']} | {p['median_sec']}s | {'pass' if p['failure_rate'] < 0.5 else 'fail'} |")
        lines.append("")

    if bottlenecks:
        lines.append("## Bottlenecks Found")
        lines.append("")
        lines.append("| Type | Job | Severity | Source |")
        lines.append("|---|---|---|---|")
        for b in bottlenecks:
            src = "LLM" if b["type"] in ("redundant_rebuild", "oversized_context") else "Rule"
            lines.append(f"| {b['type']} | {b['job_name']} | {b['severity']} | {src} |")
        lines.append("")

    if optimizations:
        lines.append("## Recommendations")
        lines.append("")
        lines.append("| Optimization | Job | Saved | Cost/Run | Risk |")
        lines.append("|---|---|---|---|---|")
        for o in optimizations:
            lines.append(f"| {o['description'][:50]} | {o['job_name']} | {o['estimated_time_saved_min']}m | ${o['estimated_cost_per_run']:.2f} | {o['risk_level']} |")
        lines.append("")

    total_saved = simulate(optimizations)
    lines.append(f"**Total estimated savings: {total_saved} minutes per run**")
    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path


def print_summary(results: list[dict]) -> None:
    print()
    print(f"{'='*70}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"  {'Repo':<30s} {'PR #':<8s} {'Bottlenecks':<12s} {'Min Saved':<10s} {'Top Rec'}")
    print(f"  {'-'*30} {'-'*8} {'-'*12} {'-'*10} {'-'*20}")

    for r in sorted(results, key=lambda x: -x["total_saved"]):
        print(f"  {r['repo']:<30s} {r['pr_number']:<8d} {r['bottleneck_count']:<12d} {r['total_saved']:<10d} {r['top_rec'][:25]}")

    total_b = sum(r["bottleneck_count"] for r in results)
    total_s = sum(r["total_saved"] for r in results)
    print(f"  {'-'*30} {'-'*8} {'-'*12} {'-'*10} {'-'*20}")
    print(f"  {'TOTAL':<30s} {len(results):<8d} {total_b:<12d} {total_s:<10d}")
    print(f"  Reports saved to reports/ ({len(results)} files)")


def main():
    args = parse_args()

    config = {
        "llm": {
            "local": {
                "base_url": "http://127.0.0.1:8000/v1",
                "api_key": "omlx-test",
                "model": "DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
            }
        }
    }
    llm_client = None if args.no_llm else LLMClient(config)

    import glob
    pr_files = sorted(glob.glob(os.path.join(args.data_dir, "*", "prs", "*.json")))
    if args.max_prs > 0:
        pr_files = pr_files[: args.max_prs]

    print(f"Analyzing {len(pr_files)} PRs from {args.data_dir}/...")
    if llm_client:
        print(f"  LLM: DeepSeek-Coder-V2-Lite (local)")
    else:
        print(f"  LLM: disabled")
    print(f"  Reports: {args.output_dir}/")
    print()

    results = []
    start_time = time.time()

    for i, path in enumerate(pr_files):
        pr = load_pr(path)
        repo_label = path.split("/prs/")[0].split("/")[-1].replace("-", "/")

        workflows = build_workflows(pr, path)
        profiles_data = build_profiles(pr)

        if not profiles_data or not any(w["jobs"] for w in workflows):
            continue

        bottlenecks = classify(profiles_data, workflows, llm_client=llm_client)
        optimizations = propose(bottlenecks, profiles_data, llm_client=llm_client)
        total_saved = simulate(optimizations)

        report_path = save_report(repo_label, pr, profiles_data, bottlenecks, optimizations, args.output_dir)

        bcount = len(bottlenecks)
        top_rec = optimizations[0]["description"][:25] if optimizations else "none"
        print(f"  [{i+1:3d}/{len(pr_files)}] {repo_label:<25s} PR #{pr['pr_number']:<6d} {bcount} bottlenecks, {total_saved}m saved")

        results.append({
            "repo": repo_label,
            "pr_number": pr["pr_number"],
            "bottleneck_count": bcount,
            "total_saved": total_saved,
            "top_rec": top_rec,
        })

    elapsed = int(time.time() - start_time)
    print_summary(results)
    print(f"\n  Duration: {elapsed}s")
    print(f"  Reports: reports/ ({len(results)} files)")


if __name__ == "__main__":
    main()
