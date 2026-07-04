#!/usr/bin/env python3
"""
Run the full optimize pipeline on cached PRs from the last 7 days.
Reads from data/, saves results to output/. No live API calls to public repos.

Usage:
  python3 tools/run_pipeline.py
  python3 tools/run_pipeline.py --max 10
  python3 tools/run_pipeline.py --no-llm
  python3 tools/run_pipeline.py --since 30
"""

import argparse
import json
import glob
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.profiler import parse_job_graph
from lib.classifier import classify
from lib.optimizer import propose, simulate
from lib.generator import rewrite
from lib.validator import validate
from nodes.pr import _make_title, _make_pr_body
from llm.client import LLMClient
import config as cfg


def parse_args():
    p = argparse.ArgumentParser(description="Run pipeline on cached PRs")
    p.add_argument("--data", default="data", help="Dataset directory")
    p.add_argument("--output", default="output", help="Output directory")
    p.add_argument("--since", type=int, default=7, help="Days to filter (default: 7)")
    p.add_argument("--max", type=int, default=0, help="Max PRs to process")
    p.add_argument("--no-llm", action="store_true", help="Rules only")
    p.add_argument("--config", help="Path to config.yaml")
    return p.parse_args()


def main():
    args = parse_args()
    c = cfg.load_config(args.config)

    llm_client = None
    if not args.no_llm:
        llm_cfg = c.get("llm", {})
        if llm_cfg and llm_cfg.get("local"):
            llm_client = LLMClient(c)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.since)
    pr_files = sorted(glob.glob(os.path.join(args.data, "*", "prs", "*.json")))
    filtered = []
    for f in pr_files:
        with open(f) as fh:
            pr = json.load(fh)
        created = pr.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt >= cutoff:
                    filtered.append(f)
            except ValueError:
                continue
    if args.max > 0:
        filtered = filtered[: args.max]

    proc = 0
    errors = 0

    print(f"Cached PRs: {len(filtered)} (last {args.since}d)")
    print(f"LLM:        {'enabled' if llm_client else 'disabled'}")
    print(f"Output:     {args.output}/")
    print()

    for i, path in enumerate(filtered):
        try:
            with open(path) as f:
                pr = json.load(f)

            repo_dir = os.path.dirname(os.path.dirname(path))
            repo_label = os.path.basename(repo_dir).replace("-", "/")
            pr_num = pr["pr_number"]

            # Parse profiles from CI runs
            profs = []
            for run in pr.get("ci_runs", []):
                for job in run.get("jobs", []):
                    if job.get("duration_sec", 0) > 0:
                        profs.append({
                            "job_name": job["name"],
                            "median_sec": job["duration_sec"],
                            "p90_sec": job["duration_sec"],
                            "p99_sec": job["duration_sec"],
                            "failure_rate": 0.0 if job.get("status") == "success" else 0.5,
                            "cache_hit_ratio": None,
                        })

            # Parse workflow YAML files matching CI runs
            wf_ids = {run.get("workflow_id") for run in pr.get("ci_runs", []) if run.get("workflow_id")}
            wfs = []
            for wf_ref in pr.get("workflows", []):
                wf_path = os.path.join(repo_dir, "workflows", f'{wf_ref["hash"]}.yml')
                content = ""
                if os.path.exists(wf_path):
                    with open(wf_path) as f:
                        content = f.read()
                wf = {"filename": wf_ref["filename"], "content": content, "jobs": []}
                if content:
                    wf["jobs"] = parse_job_graph(wf)
                wfs.append(wf)

            if not profs or not any(w["jobs"] for w in wfs):
                continue

            # Classify + propose
            bottlenecks = classify(profs, wfs, llm_client=llm_client)
            optimizations = propose(bottlenecks, profs, llm_client=llm_client)
            total_saved = simulate(optimizations)

            if not optimizations:
                continue

            # Generate YAML
            selected_ids = [o["id"] for o in optimizations]
            rewritten = rewrite(wfs, selected_ids, optimizations)
            is_valid, _ = validate(rewritten)

            # Save locally
            out_dir = os.path.join(args.output, os.path.basename(repo_dir))
            os.makedirs(os.path.join(out_dir, "workflows"), exist_ok=True)

            yaml_path = os.path.join(out_dir, "workflows", f"pr-{pr_num}-optimized.yml")
            with open(yaml_path, "w") as f:
                f.write(rewritten)

            title = _make_title(optimizations)
            body = _make_pr_body(repo_label, optimizations, bottlenecks, profs, rewritten, f"pr-{pr_num}")
            pr_path = os.path.join(out_dir, f"PR-{pr_num}.md")
            with open(pr_path, "w") as f:
                f.write(f"# {title}\n\n{body}")

            proc += 1
            print(f"  [{i+1}/{len(filtered)}] {repo_label:<25s} PR #{pr_num:<6d} {len(bottlenecks)} bottlenecks, {total_saved}m saved")

        except Exception as e:
            errors += 1
            print(f"  [{i+1}/{len(filtered)}] ERROR: {e}")

    print(f"\nDone. {proc} PRs processed, {errors} errors")
    print(f"Output: {args.output}/")


if __name__ == "__main__":
    main()
