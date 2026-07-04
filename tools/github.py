import json
import logging
import re
import time
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
MAX_RETRIES = 4
INITIAL_BACKOFF = 1


class GitHubClient:
    def __init__(self, token: str, base_url: str = GITHUB_API_BASE):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "cicd-bottleneck-optimizer",
        }

    def _request(self, method: str, path: str, body: dict | None = None) -> Any:
        url = f"{self.base_url}{path}"
        backoff = INITIAL_BACKOFF

        for attempt in range(MAX_RETRIES + 1):
            try:
                data = json.dumps(body).encode() if body else None
                req = urllib.request.Request(url, data=data, headers=self._headers, method=method)
                resp = urllib.request.urlopen(req, timeout=30)
                return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 403 and attempt < MAX_RETRIES:
                    logger.warning("Rate limited (403). Retrying in %ds (attempt %d/%d)...", backoff, attempt + 1, MAX_RETRIES)
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                if e.code == 404:
                    return None
                if e.code == 422:
                    logger.warning("422 on %s — %s", url, e.read().decode())
                    return None
                raise
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < MAX_RETRIES:
                    logger.warning("Network error: %s. Retrying in %ds...", e, backoff)
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                logger.error("Network error after %d retries: %s", MAX_RETRIES, e)
                raise

    def _paginate(self, path: str) -> list[dict]:
        items = []
        url = f"{self.base_url}{path}"

        while url:
            try:
                req = urllib.request.Request(url, headers=self._headers)
                resp = urllib.request.urlopen(req, timeout=30)
                page = json.loads(resp.read().decode())
                if isinstance(page, list):
                    items.extend(page)
                else:
                    items.append(page)

                link_header = resp.headers.get("Link", "")
                next_url = self._parse_next_link(link_header)
                url = next_url if next_url else None
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    logger.warning("Rate limited during pagination. Backing off...")
                    time.sleep(INITIAL_BACKOFF)
                    continue
                logger.warning("HTTP %d during pagination — stopping", e.code)
                break
        return items

    @staticmethod
    def _parse_next_link(link_header: str) -> str | None:
        if not link_header:
            return None
        for part in link_header.split(","):
            match = re.search(r'<([^>]+)>;\s*rel="next"', part.strip())
            if match:
                return match.group(1)
        return None

    def fetch_workflows(self, repo: str) -> list[dict]:
        data = self._request("GET", f"/repos/{repo}/actions/workflows")
        if not data:
            return []
        return data.get("workflows", [])

    def fetch_workflow_file(self, repo: str, workflow_id: int) -> str | None:
        import urllib.error

        path = f"/repos/{repo}/actions/workflows/{workflow_id}"
        data = self._request("GET", path)
        if not data:
            return None
        file_path = data.get("path", "")
        if not file_path.endswith(".yml") and not file_path.endswith(".yaml"):
            return None
        try:
            contents = self._request("GET", f"/repos/{repo}/contents/{file_path}")
        except urllib.error.HTTPError:
            return None
        if not contents:
            return None
        import base64
        raw = base64.b64decode(contents.get("content", ""))
        return raw.decode("utf-8")

    def fetch_runs(self, repo: str, workflow_id: int, limit: int = 50) -> list[dict]:
        data = self._request("GET", f"/repos/{repo}/actions/workflows/{workflow_id}/runs?per_page={limit}")
        if not data:
            return []
        return data.get("workflow_runs", [])

    def fetch_jobs(self, repo: str, run_id: int) -> list[dict]:
        data = self._request("GET", f"/repos/{repo}/actions/runs/{run_id}/jobs")
        if not data:
            return []
        return data.get("jobs", [])

    def fetch_prs(self, repos: list[str], limit: int, since_days: int) -> list[dict]:
        all_prs = []
        import datetime
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=since_days)

        for repo in repos:
            data = self._request("GET", f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page={limit}")
            if not data or not isinstance(data, list):
                continue
            filtered = [pr for pr in data if pr.get("updated_at") and self._parse_iso(pr["updated_at"]) >= cutoff]
            all_prs.extend(filtered[:limit])
        return all_prs

    def fetch_pr_runs(self, repo: str, pr_number: int) -> list[dict]:
        pr = self._request("GET", f"/repos/{repo}/pulls/{pr_number}")
        if not pr:
            return []
        head_sha = pr.get("head", {}).get("sha", "")
        if not head_sha:
            return []
        data = self._request("GET", f"/repos/{repo}/actions/runs?event=pull_request&head_sha={head_sha}")
        if not data:
            return []
        return data.get("workflow_runs", [])

    def detect_ci_system(self, repo: str) -> str:
        data = self._request("GET", f"/repos/{repo}/actions/workflows?per_page=1")
        if data and data.get("total_count", 0) > 0:
            return "github_actions"
        return "other"

    def check_write_access(self, repo: str) -> bool:
        try:
            self._request("GET", f"/repos/{repo}")
            return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 401):
                return False
            if e.code == 404:
                logger.warning("Repo %s not found", repo)
                return False
            raise

    def create_branch(self, repo: str, branch_name: str) -> str | None:
        repo_data = self._request("GET", f"/repos/{repo}")
        if not repo_data:
            return None
        default_branch = repo_data.get("default_branch", "main")

        ref_data = self._request("GET", f"/repos/{repo}/git/ref/heads/{default_branch}")
        if not ref_data:
            return None
        sha = ref_data.get("object", {}).get("sha", "")

        result = self._request("POST", f"/repos/{repo}/git/refs", {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha,
        })
        return result.get("ref") if result else None

    def create_commit(self, repo: str, branch: str, path: str, content: str) -> dict | None:
        import base64
        encoded = base64.b64encode(content.encode()).decode()

        result = self._request("PUT", f"/repos/{repo}/contents/{path}", {
            "message": f"ci-optimizer: optimize workflow {path}",
            "content": encoded,
            "branch": branch,
        })
        return result

    def create_pr(self, repo: str, head: str, title: str, body: str) -> str | None:
        repo_data = self._request("GET", f"/repos/{repo}")
        if not repo_data:
            return None
        default_branch = repo_data.get("default_branch", "main")

        result = self._request("POST", f"/repos/{repo}/pulls", {
            "title": title,
            "body": body,
            "head": head,
            "base": default_branch,
        })
        return result.get("html_url") if result else None

    @staticmethod
    def _parse_iso(ts: str) -> Any:
        from datetime import datetime, timezone
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)
