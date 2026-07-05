"""Graph integration tests: full optimize path end-to-end (mocked)."""

import pytest
from unittest.mock import patch, Mock
from langgraph.checkpoint.memory import MemorySaver

from graph import build_graph
from lib.classifier import classify


def mock_propose(bottlenecks, profiles, llm_client=None):
    return [
        {
            "id": "opt-1",
            "description": "Add cache to build job",
            "job_name": "build",
            "bottleneck_type": "missing_cache",
            "estimated_time_saved_min": 2,
            "estimated_cost_per_run": 0.01,
            "risk_level": "low",
        },
        {
            "id": "opt-2",
            "description": "Add cache to lint job",
            "job_name": "lint",
            "bottleneck_type": "missing_cache",
            "estimated_time_saved_min": 1,
            "estimated_cost_per_run": 0.01,
            "risk_level": "low",
        },
    ]


class TestOptimizePath:
    """M3.4: Full optimize path — fetch → profile → classify → propose → simulate → interrupt → generate → validate → open_pr."""

    def test_full_optimize_path(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state, thread_config):
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())

        with patch("nodes.optimize.propose", side_effect=mock_propose):
            result = g.invoke(initial_state, thread_config)

        assert len(result.get("workflows", [])) >= 1
        assert result["workflows"][0]["filename"] == "ci.yml"
        assert len(result.get("profiles", [])) == 2
        assert result["profiles"][0]["job_name"] == "build"
        assert result["profiles"][1]["job_name"] == "lint"

        bottlenecks = result.get("bottlenecks", [])
        assert len(bottlenecks) >= 1
        assert bottlenecks[0]["type"] == "missing_cache"

        assert len(result.get("optimizations", [])) == 2
        assert result.get("simulated_total_saved_min", 0) == 3

        assert result.get("human_approved") is True
        assert result.get("selected_optimizations") == ["opt-1", "opt-2"]

        assert len(result.get("rewritten_yaml", "")) > 100
        assert "CI/CD Bottleneck Optimizer" in result["rewritten_yaml"]
        assert "actions/cache@v4" in result["rewritten_yaml"]

        assert result.get("validation_attempts", 0) >= 0

    def test_end_to_end_state_schema(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state, thread_config):
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())

        with patch("nodes.optimize.propose", side_effect=mock_propose):
            result = g.invoke(initial_state, thread_config)

        for key in ("repo_url", "mode", "workflows", "runs", "profiles",
                    "bottlenecks", "optimizations", "simulated_total_saved_min",
                    "selected_optimizations", "human_approved", "rewritten_yaml",
                    "pr_url", "errors"):
            assert key in result, f"Missing key: {key}"

    def test_multiple_runs_produce_valid_yaml(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state):
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())

        for _ in range(3):
            state = dict(initial_state)
            tc = {"configurable": {"thread_id": f"multi-{_}"}}
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                result = g.invoke(state, tc)

            assert len(result["rewritten_yaml"]) > 0
            assert "CI/CD Bottleneck Optimizer" in result["rewritten_yaml"]
