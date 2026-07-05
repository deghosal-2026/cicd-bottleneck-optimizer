"""Graph integration tests: LLM routing + fallback behaviour."""

import pytest
from unittest.mock import patch, Mock
from langgraph.checkpoint.memory import MemorySaver

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


class TestLLMRouting:
    """M3.4: LLM routing — classify with LLM, LLM unavailable, token tracking."""

    def test_llm_classify_called_during_graph(self, mock_gh_client, mock_llm_client, mock_trade_off_approve, initial_state, thread_config):
        mock_llm_client.call_local.return_value = '[{"type":"oversized_context","job_name":"build","evidence":"Test","severity":"medium"}]'
        g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())

        with patch("nodes.optimize.propose", side_effect=mock_propose):
            result = g.invoke(initial_state, thread_config)

        assert mock_llm_client.call_local.call_count >= 1
        bottlenecks = result.get("bottlenecks", [])
        types = {b["type"] for b in bottlenecks}
        assert "oversized_context" in types
        assert "missing_cache" in types

    def test_llm_unavailable_does_not_break_graph(self, mock_gh_client, initial_state, thread_config):
        llm = Mock()
        llm.call_local.side_effect = ConnectionError("OMLX not reachable")

        with patch("nodes.pr.trade_off_table", return_value=(["opt-1"], True)):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                g = build_graph(gh_client=mock_gh_client, llm_client=llm, checkpointer=MemorySaver())
                result = g.invoke(initial_state, thread_config)

        assert result.get("human_approved") is True
        assert len(result.get("rewritten_yaml", "")) > 0

    def test_no_llm_client_still_completes(self, mock_gh_client, mock_trade_off_approve, initial_state, thread_config):
        with patch("nodes.optimize.propose", side_effect=mock_propose):
            g = build_graph(gh_client=mock_gh_client, llm_client=None, checkpointer=MemorySaver())
            result = g.invoke(initial_state, thread_config)

        assert result.get("human_approved") is True

    def test_llm_generates_yaml_when_rule_rewrite_empty(self, mock_gh_client, mock_llm_client, initial_state, thread_config):
        mock_llm_client.call_local.return_value = "name: LLM Generated\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n"

        with patch("nodes.pr.trade_off_table", return_value=(["opt-1"], True)):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                with patch("nodes.generate.rewrite", return_value=""):
                    g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())
                    result = g.invoke(initial_state, thread_config)

        assert "LLM Generated" in result.get("rewritten_yaml", "")

    def test_validation_retry_stops_after_three_failures(self, mock_gh_client, mock_llm_client, initial_state, thread_config):
        with patch("nodes.pr.trade_off_table", return_value=(["opt-1"], True)):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                with patch("nodes.generate.validate", return_value=(False, "bad yaml")):
                    g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())
                    result = g.invoke(initial_state, thread_config)

        assert result.get("validation_attempts", 0) >= 3
        assert result.get("rewritten_yaml", "") == ""

    def test_reanalyze_cycle_loops_correctly(self, mock_gh_client, mock_llm_client, initial_state, thread_config):
        call_count = [0]

        def progressive_trade_off(optimizations, bottlenecks):
            call_count[0] += 1
            if call_count[0] == 1:
                return [], False
            else:
                return ["opt-1"], True

        with patch("nodes.pr.trade_off_table", side_effect=progressive_trade_off):
            with patch("nodes.optimize.propose", side_effect=mock_propose):
                g = build_graph(gh_client=mock_gh_client, llm_client=mock_llm_client, checkpointer=MemorySaver())
                result = g.invoke(initial_state, thread_config)

        assert call_count[0] == 2
        assert result.get("human_approved") is True
        assert len(result.get("rewritten_yaml", "")) > 0
