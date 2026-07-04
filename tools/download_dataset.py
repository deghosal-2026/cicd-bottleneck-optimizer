import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.github import GitHubClient


REPOS = [
    "kubernetes/kubernetes",
    "tensorflow/tensorflow",
    "moby/moby",
    "vercel/next.js",
    "microsoft/vscode",
    "angular/angular",
    "facebook/react-native",
    "apache/spark",
    "elastic/elasticsearch",
    "hashicorp/terraform",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Download PR + CI dataset from public repos")
    parser.add_argument("--repos-file", default="repos.txt", help="File with repos (one per line)")
    parser.add_argument("--pr-limit", type=int, default=50, help="PRs per repo")
    parser.add_argument("--since", type=int, default=60, help="Days to look back")
    parser.add_argument("--output-dir", default="data", help="Output directory")
    parser.add_argument("--token", default="", help="GitHub token (or GITHUB_TOKEN env)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between repos")
    return parser.parse_args()


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def ensure_dirs(base: str, repo: str) -> tuple[str, str]:
    repo_dir = repo.replace("/", "-")
    prs_dir = os.path.join(base, repo_dir, "prs")
    workflows_dir = os.path.join(base, repo_dir, "workflows")
    os.makedirs(prs_dir, exist_ok=True)
    os.makedirs(workflows_dir, exist_ok=True)
    return prs_dir, workflows_dir


def store_workflow(workflows_dir: str, filename: str, content: str) -> dict:
    h = hash_content(content)
    dest = os.path.join(workflows_dir, f"{h}.yml")
    if not os.path.exists(dest):
        with open(dest, "w") as f:
            f.write(content)
    return {"filename": filename, "hash": h}


def main():
    args = parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("Error: GitHub token required. Set GITHUB_TOKEN env var or pass --token.")
        sys.exit(1)

    client = GitHubClient(token)
    repos = _load_repos(args.repos_file)
    random.shuffle(repos)

    random_offset = random.randint(5, args.since)
    since_date = datetime.now(timezone.utc) - timedelta(days=random_offset)
    start_time = time.time()

    print(f"Dataset downloader")
    print(f"  Repos: {len(repos)}")
    print(f"  PR limit per repo: {args.pr_limit}")
    print(f"  Since: {args.since} days")
    print(f"  Randomized start: {since_date.date()} (last {random_offset}d)")
    print(f"  Output: {args.output_dir}/")
    print(f"  Delay between repos: {args.delay}s")
    print()

    total_prs = 0
    total_api_calls = 0
    skipped_no_ci = 0
    skipped_non_actions = 0

    for repo_idx, repo in enumerate(repos):
        repo_label = repo.replace("/", "-")
        repo_api_start = total_api_calls
        elapsed = int(time.time() - start_time)
        print(f"\n{'='*60}")
        print(f"  [{repo_idx+1}/{len(repos)}] {repo}  (elapsed: {elapsed}s, API calls: {total_api_calls})")
        print(f"{'='*60}")

        print(f"  ● Checking CI system...")
        ci_system = client.detect_ci_system(repo)
        total_api_calls += 1

        if ci_system != "github_actions":
            print(f"  ✗ Skipping — not GitHub Actions (detected: {ci_system})")
            skipped_non_actions += 1
            continue

        prs_dir, workflows_dir = ensure_dirs(args.output_dir, repo)
        repo_prs = 0

        print(f"  ● Fetching PR list...")
        try:
            prs = client.fetch_prs([repo], args.pr_limit, args.since)
            total_api_calls += 1
        except Exception as e:
            print(f"  ✗ Failed to fetch PRs: {e}")
            continue

        print(f"  ● Found {len(prs)} PRs in last {args.since}d")
        random.shuffle(prs)

        repo_workflow_cache: dict[str, dict] = {}

        for i, pr in enumerate(prs):
            pr_number = pr.get("number")
            if not isinstance(pr_number, int):
                continue
            pr_title = pr.get("title", "")
            head_sha = pr.get("head", {}).get("sha", "")

            if not head_sha:
                continue

            print(f"  [{i+1}/{len(prs)}] PR #{pr_number} — fetching CI runs...", end="", flush=True)
            ci_runs = _fetch_ci_runs(client, repo, head_sha, pr_number)
            total_api_calls += ci_runs["api_calls"]

            if not ci_runs["runs"]:
                skipped_no_ci += 1
                print(f" no CI runs, skipped")
                continue

            print(f" {len(ci_runs['runs'])} runs, fetching workflows...", end="", flush=True)

            workflows = _fetch_workflow_files(client, repo, workflows_dir, repo_workflow_cache)
            total_api_calls += workflows["api_calls"]

            pr_data = {
                "pr_number": pr_number,
                "title": pr_title,
                "state": pr.get("state", ""),
                "author": pr.get("user", {}).get("login", ""),
                "created_at": pr.get("created_at", ""),
                "updated_at": pr.get("updated_at", ""),
                "merged_at": pr.get("merged_at"),
                "head_sha": head_sha,
                "labels": [l.get("name", "") for l in pr.get("labels", [])],
                "ci_runs": ci_runs["runs"],
                "workflows": workflows["files"],
            }

            pr_file = os.path.join(prs_dir, f"{pr_number}.json")
            with open(pr_file, "w") as f:
                json.dump(pr_data, f, indent=2)

            repo_prs += 1
            job_count = sum(len(r.get("jobs", [])) for r in ci_runs["runs"])
            print(f" saved ({job_count} jobs)")

        repo_api_calls = total_api_calls - repo_api_start
        total_prs += repo_prs
        print(f"  ✓ Repo done: {repo_prs} PRs saved, {len(prs) - repo_prs} skipped (no CI)")
        print(f"    API calls: {repo_api_calls}")

        if repo_idx < len(repos) - 1:
            print(f"  ○ Waiting {args.delay}s before next repo...")
            time.sleep(args.delay)

    _print_summary(total_prs, total_api_calls, skipped_no_ci, skipped_non_actions, repos, start_time)


def _fetch_ci_runs(client: GitHubClient, repo: str, head_sha: str, pr_number: int) -> dict:
    result = {"runs": [], "api_calls": 0}
    try:
        runs = client.fetch_pr_runs(repo, pr_number)
        result["api_calls"] += 1
    except Exception:
        return result

    for run in runs:
        run_id = run.get("id")
        if not run_id:
            continue

        try:
            jobs = client.fetch_jobs(repo, run_id)
            result["api_calls"] += 1
        except Exception:
            jobs = []

        normalized_jobs = []
        for job in jobs:
            normalized_jobs.append({
                "name": job.get("name", "unknown"),
                "status": job.get("conclusion", job.get("status", "unknown")),
                "started_at": job.get("started_at", ""),
                "completed_at": job.get("completed_at", ""),
                "duration_sec": _compute_duration(job),
            })

        result["runs"].append({
            "run_id": run_id,
            "workflow_id": run.get("workflow_id", 0),
            "workflow_name": run.get("name", ""),
            "status": run.get("conclusion", run.get("status", "unknown")),
            "head_sha": run.get("head_sha", ""),
            "created_at": run.get("created_at", ""),
            "updated_at": run.get("updated_at", ""),
            "run_started_at": run.get("run_started_at", ""),
            "jobs": normalized_jobs,
        })

    return result


def _fetch_workflow_files(
    client: GitHubClient, repo: str, workflows_dir: str, cache: dict[str, dict]
) -> dict:
    result = {"files": [], "api_calls": 0}

    try:
        workflows = client.fetch_workflows(repo)
        result["api_calls"] += 1
    except Exception:
        return result

    for wf in workflows[:5]:
        wf_id = wf.get("id")
        if not isinstance(wf_id, int):
            continue
        filename = wf.get("path", "").replace(".github/workflows/", "")

        if filename in cache:
            result["files"].append(cache[filename])
            continue

        try:
            content = client.fetch_workflow_file(repo, wf_id)
            result["api_calls"] += 1
        except Exception:
            continue

        if content is None:
            continue

        entry = store_workflow(workflows_dir, filename, content)
        cache[filename] = entry
        result["files"].append(entry)

    return result


def _compute_duration(job: dict) -> int:
    started = job.get("started_at")
    completed = job.get("completed_at")
    duration = job.get("duration_sec")
    if duration:
        return int(duration)
    if started and completed:
        try:
            t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(completed.replace("Z", "+00:00"))
            return int((t1 - t0).total_seconds())
        except (ValueError, TypeError):
            pass
    return 0


def _load_repos(path: str) -> list[str]:
    if not os.path.exists(path):
        print(f"No {path} found. Using default repo list.")
        return REPOS
    with open(path) as f:
        repos = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return repos or REPOS


def _print_summary(total_prs: int, api_calls: int, skipped_no_ci: int, skipped_non_actions: int, repos: list, start_time: float) -> None:
    elapsed = int(time.time() - start_time)
    print(f"\n{'='*60}")
    print(f"  DOWNLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"  Duration:        {elapsed}s")
    print(f"  Repos processed: {len(repos) - skipped_non_actions}/{len(repos)}")
    print(f"  PRs saved:       {total_prs}")
    print(f"  Skipped (no CI): {skipped_no_ci}")
    print(f"  Skipped (other): {skipped_non_actions}")
    print(f"  API calls made:  {api_calls}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
