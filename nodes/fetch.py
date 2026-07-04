"""LangGraph nodes for fetching workflows, runs, PRs, and PR runs."""

from tools.github import GitHubClient


def fetch_workflows_node(state: dict, client: GitHubClient) -> dict:
    repo = state.get("repo_url", "")
    workflows_data = client.fetch_workflows(repo)
    workflows = []

    for wf in workflows_data:
        filename = wf.get("path", "").replace(".github/workflows/", "")
        content = client.fetch_workflow_file(repo, wf["id"])
        if content is None:
            continue
        workflows.append({
            "filename": filename,
            "content": content,
            "jobs": [],
        })

    if not workflows:
        print("No GitHub Actions workflows found in this repo.")

    return {"workflows": workflows, "errors": state.get("errors", [])}


def fetch_runs_node(state: dict, client: GitHubClient) -> dict:
    repo = state.get("repo_url", "")
    workflows = state.get("workflows", [])
    runs = []
    errors = list(state.get("errors", []))

    for wf in workflows:
        filename = wf.get("filename", "")
        wf_id = _find_workflow_id(client, repo, filename)
        if wf_id is None:
            continue
        try:
            wf_runs = client.fetch_runs(repo, wf_id, limit=50)
            for run in wf_runs:
                run_id = run.get("id")
                if run_id:
                    jobs = client.fetch_jobs(repo, run_id)
                    run["jobs"] = jobs
                runs.append(_normalize_run(run))
        except Exception as e:
            errors.append(f"Failed to fetch runs for {filename}: {e}")

    return {"runs": runs, "errors": errors}


def fetch_prs_node(state: dict, client: GitHubClient) -> dict:
    repos = state.get("field_study_repos", [])
    pr_limit = state.get("pr_limit", 10)
    since_days = state.get("since_days", 30)

    prs = client.fetch_prs(repos, pr_limit, since_days)
    return {"prs": prs, "errors": state.get("errors", [])}


def fetch_pr_runs_node(state: dict, client: GitHubClient) -> dict:
    repos = state.get("field_study_repos", [])
    prs = state.get("prs", [])
    pr_to_repo = {}

    for pr in prs:
        repo_url = pr.get("base", {}).get("repo", {}).get("full_name", "")
        if not repo_url:
            continue
        pr_number = pr.get("number")
        pr_to_repo[pr_number] = repo_url

    pr_runs: dict = {}
    for pr_number, repo in pr_to_repo.items():
        try:
            runs = client.fetch_pr_runs(repo, pr_number)
            for run in runs:
                run_id = run.get("id")
                if run_id:
                    jobs = client.fetch_jobs(repo, run_id)
                    run["jobs"] = jobs
            pr_runs[str(pr_number)] = [_normalize_run(r) for r in runs]
        except Exception as e:
            print(f"  Warning: Failed to fetch runs for PR #{pr_number}: {e}")

    return {"pr_runs": pr_runs, "errors": state.get("errors", [])}


def _find_workflow_id(client: GitHubClient, repo: str, filename: str) -> int | None:
    try:
        workflows = client.fetch_workflows(repo)
        for wf in workflows:
            if wf.get("path", "").endswith(filename):
                return wf.get("id")
    except Exception:
        pass
    return None


def _normalize_run(run: dict) -> dict:
    jobs_list = run.get("jobs", [])
    normalized_jobs = []
    for job in jobs_list:
        normalized_jobs.append({
            "name": job.get("name", "unknown"),
            "status": job.get("conclusion", job.get("status", "unknown")),
            "started_at": job.get("started_at", ""),
            "completed_at": job.get("completed_at", ""),
            "duration_sec": job.get("duration_sec", 0),
        })
    return {
        "run_id": run.get("id", 0),
        "status": run.get("conclusion", run.get("status", "unknown")),
        "created_at": run.get("created_at", ""),
        "updated_at": run.get("updated_at", ""),
        "run_started_at": run.get("run_started_at", ""),
        "jobs": normalized_jobs,
    }
