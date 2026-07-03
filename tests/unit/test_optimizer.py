"""Unit tests for optimizer.py — optimization proposals + cost calculation."""
import pytest


class TestProposeOptimizations:
    """Generating candidate optimizations from bottlenecks."""

    def test_one_optimization_per_bottleneck(self):
        """Each bottleneck yields at least one optimization proposal."""

    def test_optimization_has_all_fields(self):
        """Output includes id, description, time_saved, cost, risk, yaml_diff_hint."""

    def test_empty_bottlenecks_returns_empty_optimizations(self):
        """No bottlenecks → no optimizations."""

    def test_multiple_optimizations_for_complex_bottleneck(self):
        """A single bottleneck may yield multiple alternative optimizations."""

    def test_optimization_id_is_unique(self):
        """Each optimization gets a unique ID."""

    def test_yaml_diff_hint_describes_change(self):
        """yaml_diff_hint explains what changes in the YAML (not just 'add cache')."""


class TestCostCalculation:
    """Cost estimation using hardcoded GitHub Actions rates."""

    def test_runner_cost_matches_rate(self):
        """5 min on runner → $0.04 (5 * $0.008/min)."""

    def test_cache_cost_matches_rate(self):
        """2 GB cache for 1 month → $0.014 (2 * $0.007/GB-month)."""

    def test_zero_time_saved_has_zero_runner_cost(self):
        """0 min saved → $0.00 cost."""

    def test_cost_per_run_formatted_as_float(self):
        """Cost is a float with 2 decimal places (e.g., 0.02)."""


class TestRiskAssessment:
    """Risk level assignment per optimization."""

    def test_add_cache_is_low_risk(self):
        """Adding cache directive → risk = low."""

    def test_parallelize_jobs_is_medium_risk(self):
        """Parallelizing independent jobs → risk = medium."""

    def test_reduce_matrix_is_high_risk(self):
        """Reducing matrix dimensions → risk = high (may skip coverage)."""

    def test_split_monolithic_job_is_high_risk(self):
        """Splitting a job into multiple → risk = high."""


class TestSimulateSavings:
    """Simulating total time savings across selected optimizations."""

    def test_simulate_sums_selected_optimizations(self):
        """3 optimizations with 5, 3, 2 min → total = 10 min."""

    def test_simulate_with_no_selections_returns_zero(self):
        """No optimizations selected → 0 min saved."""

    def test_simulate_does_not_double_count_overlapping(self):
        """Optimizations on same job don't stack savings beyond actual."""
