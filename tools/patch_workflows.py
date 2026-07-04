#!/usr/bin/env python3
"""
Patch workflow YAML files in cached dataset by fetching the correct ones
matching CI run workflow_ids.

Usage:
  python3 tools/patch_workflows.py
  python3 tools/patch_workflows.py --max 50
"""

import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.github import GitHubClient
from lib.profiler import parse_job_graph


def parse_args():
    p = argparse.ArgumentParser(description="Patch workflow YAMLs in cached dataset")
    p.add_argument("--data", default="data")
    p.add_argument("--max", type=int, default=0)
    p.add_argument("--delay", type=float, default=0.5)
    return p.parse_args()


def main():
    args = parse_args()

    token = open(os.path.expanduser("~/.zshrc")).read().split("export GITHUB_TOKEN=")[1].split()[0].strip('"')
    client = GitHubClient(token)

    pr_files = sorted(glob.glob(os.path.join(args.data, "*", "prs", "*.json")))
    if args.max > 0:
        pr_files = pr_files[:args.max]

    wf_cache: dict[tuple[str, int], dict] = {}
    patched = 0
    skipped = 0
    api_calls = 0
    errors = 0

    print(f"Patching workflows for {len(pr_files)} PRs...")
    print()

    for i, path in enumerate(pr_files):
        with open(path) as f:
            pr = json.load(f)

        repo = os.path.dirname(os.path.dirname(path)).split("/")[-1].replace("-", "/")
        repo_dir = os.path.dirname(os.path.dirname(path))
        workflows_dir = os.path.join(repo_dir, "workflows")
        os.makedirs(workflows_dir, exist_ok=True)

        # Get unique workflow_ids from CI runs
        wf_ids = set()
        for run in pr.get("ci_runs", []):
            wf_id = run.get("workflow_id")
            if wf_id:
                wf_ids.add(wf_id)

        if not wf_ids:
            skipped += 1
            continue

        # Check if already patched — workflow YAML contains CI run job names
        already_patched = False
        ci_job_names = {job.get("name") for run in pr.get("ci_runs", []) for job in run.get("jobs", [])}
        for wf_ref in pr.get("workflows", []):
            wf_path = os.path.join(workflows_dir, f'{wf_ref.get("hash", "")}.yml')
            if os.path.exists(wf_path):
                with open(wf_path) as wf_file:
                    content = wf_file.read()
                parsed = parse_job_graph({"content": content, "jobs": []})
                if any(j["name"] in ci_job_names for j in parsed):
                    already_patched = True
                    break

        if already_patched:
            skipped += 1
            continue

        # Fetch correct workflows by workflow_id (cached per repo)
        new_workflows = []
        for wf_id in wf_ids:
            cache_key = (repo, wf_id)
            if cache_key in wf_cache:
                new_workflows.append(wf_cache[cache_key])
                continue

            try:
                wf_data = client._request("GET", f"/repos/{repo}/actions/workflows/{wf_id}")
                api_calls += 1
                if not wf_data:
                    continue
                filename = wf_data.get("path", "").replace(".github/workflows/", "")
                content = client.fetch_workflow_file(repo, wf_id)
                api_calls += 1
            except Exception:
                errors += 1
                continue

            if not content or not filename.endswith((".yml", ".yaml")):
                continue

            import hashlib
            h = hashlib.sha256(content.encode()).hexdigest()
            wf_path = os.path.join(workflows_dir, f"{h}.yml")
            if not os.path.exists(wf_path):
                with open(wf_path, "w") as f:
                    f.write(content)

            entry = {"filename": filename, "hash": h}
            wf_cache[cache_key] = entry
            new_workflows.append(entry)

        if new_workflows:
            pr["workflows"] = new_workflows
            with open(path, "w") as f:
                json.dump(pr, f, indent=2)
            patched += 1
            print(f"  [{i+1}/{len(pr_files)}] {repo:<25s} PR #{pr['pr_number']:<6d} patched ({len(new_workflows)} workflows)")

        time.sleep(args.delay)

    print()
    print(f"Done. {patched} PRs patched, {skipped} skipped, {errors} errors, {api_calls} API calls")


if __name__ == "__main__":
    main()
