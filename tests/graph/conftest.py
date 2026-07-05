"""Shared fixtures for graph integration tests."""

import uuid
import pytest
from unittest.mock import Mock, patch
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def thread_config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


@pytest.fixture
def mock_gh_client():
    gh = Mock()
    gh.fetch_workflows.return_value = [{"id": 1, "path": ".github/workflows/ci.yml"}]
    gh.fetch_workflow_file.return_value = """name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm install
      - run: npm test
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
"""
    gh.fetch_runs.return_value = [
        {
            "id": 1,
            "conclusion": "success",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:05:00Z",
            "run_started_at": "2026-01-01T00:00:00Z",
        },
    ]
    gh.fetch_jobs.return_value = [
        {
            "name": "build",
            "conclusion": "success",
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:02:30Z",
            "duration_sec": 150,
        },
        {
            "name": "lint",
            "conclusion": "success",
            "started_at": "2026-01-01T00:02:30Z",
            "completed_at": "2026-01-01T00:03:00Z",
            "duration_sec": 30,
        },
    ]
    gh.create_branch.return_value = "refs/heads/ci-optimizer/test-abc123"
    gh.create_commit.return_value = {"sha": "abc123"}
    gh.create_pr.return_value = "https://github.com/test/repo/pull/1"
    return gh


@pytest.fixture
def mock_llm_client():
    llm = Mock()
    llm.call_local.return_value = "[]"
    return llm


@pytest.fixture
def mock_trade_off_approve():
    with patch("nodes.pr.trade_off_table", return_value=(["opt-1", "opt-2"], True)):
        yield


@pytest.fixture
def mock_trade_off_reject():
    with patch("nodes.pr.trade_off_table", return_value=([], False)):
        yield


@pytest.fixture
def checkpointer():
    return MemorySaver()


@pytest.fixture
def initial_state():
    return {
        "repo_url": "test/repo",
        "mode": "optimize",
        "field_study_repos": [],
        "pr_limit": 10,
        "since_days": 30,
        "workflow_limit": 5,
        "workflows": [],
        "runs": [],
        "prs": [],
        "pr_runs": {},
        "profiles": [],
        "bottlenecks": [],
        "optimizations": [],
        "simulated_total_saved_min": 0,
        "selected_optimizations": [],
        "human_approved": False,
        "rewritten_yaml": "",
        "rewritten_yaml_path": "",
        "pr_url": None,
        "report_path": None,
        "validation_attempts": 0,
        "token_usage": {},
        "errors": [],
        "llm_client": None,
        "github_client": None,
    }
