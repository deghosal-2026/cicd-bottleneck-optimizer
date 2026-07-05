"""Graph integration tests: resume from checkpoint."""

import uuid
import pytest
from unittest.mock import patch, Mock

from graph import build_graph


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
    ]


class TestResume:
    """M3.4: Resume from checkpoint preserves state."""

    def test_resume_with_same_thread_id(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state):
        from langgraph.checkpoint.memory import MemorySaver

        checkpointer = MemorySaver()
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=checkpointer)

        thread_id = str(uuid.uuid4())
        thread_config = {"configurable": {"thread_id": thread_id}}

        with patch("lib.optimizer.propose", side_effect=mock_propose):
            result1 = g.invoke(initial_state, thread_config)

        assert len(result1.get("workflows", [])) == 1
        assert result1.get("human_approved") is True

        snapshot = g.get_state(thread_config)
        assert snapshot.values, "Checkpoint should exist"

        # Resume — should pick up completed state
        result2 = g.invoke(None, thread_config)

        assert result2.get("repo_url") == "test/repo"
        assert result2.get("human_approved") is True

    def test_resume_preserves_bottleneck_state(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state):
        from langgraph.checkpoint.memory import MemorySaver

        checkpointer = MemorySaver()
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=checkpointer)

        thread_id = str(uuid.uuid4())
        thread_config = {"configurable": {"thread_id": thread_id}}

        with patch("lib.optimizer.propose", side_effect=mock_propose):
            result = g.invoke(initial_state, thread_config)

        bottlenecks = result.get("bottlenecks", [])
        assert len(bottlenecks) > 0

        snapshot = g.get_state(thread_config)
        assert len(snapshot.values.get("bottlenecks", [])) == len(bottlenecks)

        result2 = g.invoke(None, thread_config)
        assert len(result2.get("bottlenecks", [])) == len(bottlenecks)

    def test_resume_after_interrupt_during_optimize(self, mock_gh_client, mock_llm_client, initial_state):
        from langgraph.checkpoint.memory import MemorySaver
        from langgraph.errors import GraphRecursionError

        checkpointer = MemorySaver()
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=checkpointer)

        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}

        # Run up to interrupt — user rejects (reanalyze). Hits recursion limit after loop.
        with patch("nodes.pr.trade_off_table", return_value=([], False)):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                try:
                    g.invoke(initial_state, config)
                except GraphRecursionError:
                    pass

        state = g.get_state(config)
        assert state.values.get("human_approved") is False

        # Resume with approval this time
        config2 = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
        with patch("nodes.pr.trade_off_table", return_value=(["opt-1"], True)):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                result2 = g.invoke(None, config2)

        assert result2.get("human_approved") is True
        assert len(result2.get("rewritten_yaml", "")) > 0
