"""Field study: loop across random high-profile repos, pick 5 PRs from a random day, analyze."""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import config as cfg
from lib.profiler import profile, parse_job_graph
from lib.classifier import classify
from lib.optimizer import propose, simulate
from llm.client import LLMClient
from tools.github import GitHubClient

import random

TARGET_REPOS = [
    "react/react",
    "golang/go",
    "python/cpython",
    "nodejs/node",
    "flutter/flutter",
    "pytorch/pytorch",
    "apache/airflow",
    "grafana/grafana",
    "prometheus/prometheus",
    "rails/rails",
    "django/django",
    "openai/openai-python",
    "huggingface/transformers",
    "langchain-ai/langchain",
    "containerd/containerd",
    "istio/istio",
    "envoyproxy/envoy",
    "apache/kafka",
    "etcd-io/etcd",
    "ansible/ansible",
]

OUTPUT_DIR = "llm-output"


def fetch_prs_last_week(client: GitHubClient, repo: str, limit: int = 5) -> list[dict]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)

    date_filter = f"updated:{start.strftime('%Y-%m-%dT%H:%M:%SZ')}..{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    query = f"repo:{repo}+is:pr+{date_filter}"
    path = f"/search/issues?q={query}&sort=updated&order=desc&per_page={limit}"

    resp = client._request("GET", path)
    if not resp or "items" not in resp:
        return []

    return resp["items"]


def run():
    c = cfg.load_config()
    token = c["github"]["token"]
    gh = GitHubClient(token)

    llm_cfg = c.get("llm", {})
    llm = LLMClient(c) if llm_cfg and llm_cfg.get("local") else None

    selected = TARGET_REPOS[:]
    random.shuffle(selected)

    print("=" * 60)
    print("CI/CD Bottleneck Optimizer — Field Study")
    print(f"Repos: {len(selected)} selected")
    print("=" * 60)

    for repo in selected:
        print(f"\n{'─' * 60}")
        print(f"  Repo: {repo}")
        print(f"  Range: last 7 days")

        ci = gh.detect_ci_system(repo)
        if ci != "github_actions":
            print(f"  Skipping — CI system: {ci}")
            continue

        prs = fetch_prs_last_week(gh, repo)
        print(f"  PRs found: {len(prs)}")

        if not prs:
            continue

        for pr in prs:
            pr_number = pr["number"]
            pr_title = pr.get("title", "")[:80]
            print(f"\n  --- PR #{pr_number}: {pr_title} ---")

            print(f"  [1/6] Fetching CI runs...", end=" ", flush=True)
            runs = gh.fetch_pr_runs(repo, pr_number)
            if not runs:
                print("none found")
                continue
            print(f"got {len(runs)}")

            print(f"  [2/6] Fetching job details...", end=" ", flush=True)
            for run in runs:
                run_id = run.get("id")
                if run_id:
                    jobs = gh.fetch_jobs(repo, run_id)
                    run["jobs"] = jobs
                run["run_id"] = run.get("id", 0)
            total_jobs = sum(len(r.get("jobs", [])) for r in runs)
            print(f"{total_jobs} jobs")

            normalized = []
            for r in runs:
                njobs = []
                for j in r.get("jobs", []):
                    njobs.append({
                        "name": j.get("name", "unknown"),
                        "status": j.get("conclusion", j.get("status", "unknown")),
                        "started_at": j.get("started_at", ""),
                        "completed_at": j.get("completed_at", ""),
                        "duration_sec": j.get("duration_sec", 0),
                    })
                normalized.append({
                    "run_id": r.get("id", 0),
                    "status": r.get("conclusion", r.get("status", "unknown")),
                    "created_at": r.get("created_at", ""),
                    "updated_at": r.get("updated_at", ""),
                    "run_started_at": r.get("run_started_at", ""),
                    "jobs": njobs,
                })

            print(f"  [3/6] Fetching workflow YAMLs...", end=" ", flush=True)
            flows = gh.fetch_workflows(repo)
            workflows = []
            for wf in flows:
                filename = wf.get("path", "").replace(".github/workflows/", "")
                content = gh.fetch_workflow_file(repo, wf["id"])
                if content is None:
                    continue
                wf_data = {"filename": filename, "content": content, "jobs": []}
                wf_data["jobs"] = parse_job_graph(wf_data)
                workflows.append(wf_data)
            print(f"got {len(workflows)}")

            print(f"  [4/6] Profiling jobs + classifying...", end=" ", flush=True)
            profiles = profile(normalized, workflows)
            bottlenecks = classify(profiles, workflows, llm)
            print(f"{len(profiles)} profiles, {len(bottlenecks)} bottlenecks")

            print(f"  [5/6] Proposing optimizations...", end=" ", flush=True)
            optimizations = propose(bottlenecks, profiles, llm) if bottlenecks else []
            total_saved = simulate(optimizations)
            print(f"{len(optimizations)} opts, saves ~{total_saved}m")

            for b in bottlenecks[:3]:
                print(f"    - [{b['severity']}] {b['type']} in {b['job_name']}")
            if optimizations:
                for o in optimizations[:3]:
                    print(f"    + {o['description'][:100]}")

            print(f"  [6/6] Saving report...", end=" ", flush=True)
            repo_dir = repo.replace("/", "-")
            os.makedirs(os.path.join(OUTPUT_DIR, repo_dir), exist_ok=True)
            report = {
                "repo": repo,
                "pr": pr_number,
                "title": pr_title,
                "window_days": 7,
                "profiles": profiles,
                "bottlenecks": bottlenecks,
                "optimizations": optimizations,
                "total_saved_min": total_saved,
            }
            out_path = os.path.join(OUTPUT_DIR, repo_dir, f"pr-{pr_number}.json")
            with open(out_path, "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"done → {out_path}")

    print(f"\n{'=' * 60}")
    print("Done.")

    if llm and hasattr(llm, "token_usage"):
        total_tokens = sum(llm.token_usage.values())
        print(f"Total LLM tokens: {total_tokens}")


if __name__ == "__main__":
    run()
