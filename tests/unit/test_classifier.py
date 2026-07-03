"""Unit tests for classifier.py — bottleneck detection (rules + LLM hybrid)."""
import pytest


class TestRuleBasedClassification:
    """Rule-based bottleneck detection — no LLM required."""

    def test_missing_cache_detected(self):
        """Job with no `cache:` directive → missing_cache bottleneck."""

    def test_missing_cache_not_flagged_when_present(self):
        """Job with `cache: pip` → no missing_cache bottleneck."""

    def test_serial_parallel_detected(self):
        """Two jobs with no `needs:` running sequentially → serial_parallel."""

    def test_serial_parallel_not_flagged_when_needs_present(self):
        """Job with `needs: [build]` → correctly serialized, no bottleneck."""

    def test_redundant_matrix_detected(self):
        """Matrix with overlapping dimensions → redundant_matrix."""

    def test_no_bottlenecks_in_clean_workflow(self):
        """Well-optimized workflow → empty bottlenecks list."""

    def test_severity_high_for_long_wasted_time(self):
        """Job wasting > 10 min → severity = high."""

    def test_severity_medium_for_moderate_waste(self):
        """Job wasting 3–10 min → severity = medium."""

    def test_severity_low_for_small_waste(self):
        """Job wasting < 3 min → severity = low."""

    def test_empty_profiles_returns_empty_bottlenecks(self):
        """No profiles → no bottlenecks."""

    def test_rule_based_pass_runs_without_llm(self):
        """Rule-based classifications work even when no LLM is configured."""


class TestLLMClassification:
    """LLM-assisted bottleneck detection (OMLX or cloud)."""

    def test_redundant_rebuild_detected_by_llm(self):
        """Same artifact built in 2 jobs → LLM flags redundant_rebuild."""

    def test_oversized_context_detected_by_llm(self):
        """Large build context, no .dockerignore → LLM flags oversized_context."""

    def test_llm_returns_structured_bottleneck(self):
        """LLM output parsed into Bottleneck TypedDict with all fields."""

    def test_omlx_unavailable_falls_back_to_cloud(self):
        """OMLX down → prompt user → cloud LLM used for classification."""

    def test_omlx_unavailable_user_declines_cloud(self):
        """OMLX down → prompt user → n → fail with clear message."""

    def test_llm_returns_no_bottlenecks(self):
        """LLM determines no issues → empty list, no crash."""


class TestHybridFlow:
    """Rule-based + LLM pass combined."""

    def test_rules_and_llm_bottlenecks_merged(self):
        """Both passes run; results combined into single bottlenecks list."""

    def test_no_duplicate_bottlenecks(self):
        """Same job not flagged twice for same bottleneck type."""

    def test_evidence_is_data_backed(self):
        """Each bottleneck includes evidence with real timing data, not opinion."""
