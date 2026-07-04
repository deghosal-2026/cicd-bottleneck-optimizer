#!/usr/bin/env python3
"""
Analyze downloaded PR dataset — run classifier + optimizer, save reports.

Usage:
  python3 tools/analyze.py                    # analyze all PRs
  python3 tools/analyze.py --max 10           # first 10 PRs only
  python3 tools/analyze.py --no-llm           # skip LLM, rules only
  python3 tools/analyze.py --resume           # skip already-analyzed PRs
"""

import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.profiler import parse_job_graph
from lib.classifier import classify
from lib.optimizer import propose, simulate
from llm.client import LLMClient


def parse_args():
    p = argparse.ArgumentParser(description="Analyze downloaded PR dataset")
    p.add_argument("--data", default="data", help="Dataset directory")
    p.add_argument("--out", default="reports", help="Reports directory")
    p.add_argument("--max", type=int, default=0, help="Max PRs to process (0=all)")
    p.add_argument("--no-llm", action="store_true", help="Rules only, no LLM")
    p.add_argument("--resume", action="store_true", help="Skip already-analyzed PRs")
    return p.parse_args()


def report_path(out_dir: str, repo_label: str, pr_number: int) -> str:
    d = os.path.join(out_dir, repo_label)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{pr_number}-analysis.md")


def report_exists(out_dir: str, repo_label: str, pr_number: int) -> bool:
    return os.path.exists(report_path(out_dir, repo_label, pr_number))


def parse_workflows(pr: dict, pr_path: str) -> list[dict]:
    repo_dir = os.path.dirname(os.path.dirname(pr_path))
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


def parse_profiles(pr: dict) -> list[dict]:
    jobs = []
    for run in pr.get("ci_runs", []):
        for job in run.get("jobs", []):
            if job.get("duration_sec", 0) > 0:
                jobs.append(job)
    if not jobs:
        return []
    return [
        {
            "job_name": j["name"],
            "median_sec": j["duration_sec"],
            "p90_sec": j["duration_sec"],
            "p99_sec": j["duration_sec"],
            "failure_rate": 0.0 if j.get("status") == "success" else 0.5,
            "cache_hit_ratio": None,
        }
        for j in jobs
    ]


def write_report(path: str, pr: dict, repo_label: str, profiles: list, bottlenecks: list, optimizations: list) -> None:
    lines = [
        f"# PR #{pr['pr_number']} — {pr.get('title', '')}",
        "",
        f"- **Repo:** {repo_label}",
        f"- **Author:** {pr.get('author', '')}",
        f"- **State:** {pr.get('state', '')}",
        f"- **Created:** {pr.get('created_at', '')[:10]}",
        f"- **CI runs:** {len(pr.get('ci_runs', []))}",
        "",
    ]
    if profiles:
        lines += ["## Job Profiles", "", "| Job | Duration | Status |", "|---|---|---|"]
        for p in profiles:
            lines.append(f"| {p['job_name']} | {p['median_sec']}s | {'pass' if p['failure_rate'] < 0.5 else 'fail'} |")
        lines.append("")

    if bottlenecks:
        lines += ["## Bottlenecks", "", "| Type | Job | Severity | Source |", "|---|---|---|---|"]
        for b in bottlenecks:
            src = "LLM" if b["type"] in ("redundant_rebuild", "oversized_context") else "Rule"
            lines.append(f"| {b['type']} | {b['job_name']} | {b['severity']} | {src} |")
        lines.append("")

    if optimizations:
        lines += ["## Recommendations", "", "| Opt | Job | Saved | Cost | Risk |", "|---|---|---|---|---|"]
        for o in optimizations:
            lines.append(f"| {o['description'][:50]} | {o['job_name']} | {o['estimated_time_saved_min']}m | ${o['estimated_cost_per_run']:.2f} | {o['risk_level']} |")
        lines.append("")

    lines.append(f"**Total savings: {simulate(optimizations)} min/run**")
    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    args = parse_args()

    llm = None if args.no_llm else LLMClient({
        "llm": {
            "local": {
                "base_url": "http://127.0.0.1:8000/v1",
                "api_key": "omlx-test",
                "model": "DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
            }
        }
    })

    pr_files = sorted(glob.glob(os.path.join(args.data, "*", "prs", "*.json")))
    if args.max > 0:
        pr_files = pr_files[: args.max]

    skipped = 0
    processed = 0
    total_b = 0
    total_s = 0
    start = time.time()

    print(f"Dataset: {len(pr_files)} PRs")
    print(f"LLM:     {'DeepSeek-Coder (local)' if llm else 'disabled'}")
    print(f"Resume:  {'yes' if args.resume else 'no'}")
    print(f"Output:  {args.out}/")
    print()

    for i, path in enumerate(pr_files):
        with open(path) as f:
            pr = json.load(f)

        repo = path.split("/prs/")[0].split("/")[-1].replace("-", "/")

        if args.resume and report_exists(args.out, repo, pr["pr_number"]):
            skipped += 1
            continue

        wfs = parse_workflows(pr, path)
        profs = parse_profiles(pr)

        if not profs or not any(w["jobs"] for w in wfs):
            print(f"  [{i+1}/{len(pr_files)}] {repo} PR #{pr['pr_number']} — no data, skipped")
            skipped += 1
            continue

        bott = classify(profs, wfs, llm_client=llm)
        opts = propose(bott, profs, llm_client=llm)
        saved = simulate(opts)

        rpath = report_path(args.out, repo, pr["pr_number"])
        write_report(rpath, pr, repo, profs, bott, opts)

        processed += 1
        total_b += len(bott)
        total_s += saved

        print(f"  [{i+1}/{len(pr_files)}] {repo:<25s} PR #{pr['pr_number']:<6d} {len(bott)} bottlenecks, {saved}m saved")

    elapsed = int(time.time() - start)
    print()
    print(f"Done. {processed} analyzed, {skipped} skipped, {elapsed}s")
    print(f"Total: {total_b} bottlenecks, {total_s}m saved")
    print(f"Reports: {args.out}/")


if __name__ == "__main__":
    main()
