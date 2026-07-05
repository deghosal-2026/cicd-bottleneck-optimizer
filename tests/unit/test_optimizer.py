"""Unit tests for optimizer.py — optimization proposals + cost calculation."""
import pytest
from lib.optimizer import propose, simulate, _make_id, RUNNER_COST_PER_MIN, CACHE_COST_PER_GB_MONTH


REQUIRED_FIELDS = {
    "id", "bottleneck_type", "job_name", "description",
    "estimated_time_saved_min", "estimated_cost_per_run",
    "risk_level", "yaml_diff_hint",
}


class TestProposeOptimizations:
    def test_one_optimization_per_bottleneck(self):
        bottlenecks = [
            {"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"},
            {"type": "serial_parallel", "job_name": "test", "evidence": "...", "severity": "medium"},
        ]
        profiles = [
            {"job_name": "build", "median_sec": 600},
            {"job_name": "test", "median_sec": 300},
        ]
        result = propose(bottlenecks, profiles)
        assert len(result) == 2

    def test_optimization_has_all_fields(self):
        bottlenecks = [{"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "build", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        assert len(result) == 1
        for field in REQUIRED_FIELDS:
            assert field in result[0], f"Missing field: {field}"

    def test_empty_bottlenecks_returns_empty_optimizations(self):
        assert propose([], []) == []

    def test_each_bottleneck_yields_exactly_one_optimization(self):
        bottlenecks = [
            {"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"},
            {"type": "missing_cache", "job_name": "test", "evidence": "...", "severity": "medium"},
            {"type": "serial_parallel", "job_name": "lint", "evidence": "...", "severity": "low"},
        ]
        profiles = [
            {"job_name": "build", "median_sec": 600},
            {"job_name": "test", "median_sec": 300},
            {"job_name": "lint", "median_sec": 180},
        ]
        result = propose(bottlenecks, profiles)
        assert len(result) == 3

    def test_optimization_id_is_unique(self):
        bottlenecks = [
            {"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"},
            {"type": "serial_parallel", "job_name": "test", "evidence": "...", "severity": "medium"},
            {"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"},
        ]
        profiles = [
            {"job_name": "build", "median_sec": 600},
            {"job_name": "test", "median_sec": 300},
        ]
        result = propose(bottlenecks, profiles)
        ids = [o["id"] for o in result]
        assert len(ids) == len(set(ids))

    def test_yaml_diff_hint_describes_change(self):
        bottlenecks = [{"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "build", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        hint = result[0]["yaml_diff_hint"]
        assert isinstance(hint, str) and len(hint) > 10
        assert "cache" in hint.lower()

    def test_make_id_format(self):
        oid = _make_id("missing_cache", "my-build-job")
        assert oid.startswith("missing_cache-")
        parts = oid.split("-")
        assert len(parts) >= 3

    def test_optimization_bottleneck_type_matches(self):
        bottlenecks = [{"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "test", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        assert result[0]["bottleneck_type"] == "redundant_matrix"


class TestCostCalculation:
    def test_runner_cost_matches_rate_exactly(self):
        """redundant_matrix: median 900s → saved=5 → cost = 5 * $0.008 = $0.04."""
        bottlenecks = [{"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "test", "median_sec": 900}]
        result = propose(bottlenecks, profiles)
        assert result[0]["estimated_cost_per_run"] == 0.04
        assert result[0]["estimated_time_saved_min"] == 5

    def test_redundant_rebuild_cost_matches_rate_exactly(self):
        """redundant_rebuild: median 600s → saved=4 → cost = 4 * $0.008 = $0.032 → $0.03."""
        bottlenecks = [{"type": "redundant_rebuild", "job_name": "build", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "build", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        assert result[0]["estimated_cost_per_run"] == round(4 * RUNNER_COST_PER_MIN, 2)
        assert result[0]["estimated_time_saved_min"] == 4

    def test_cache_cost_matches_formula_exactly(self):
        """missing_cache: median 300s → saved=2 → cost = round(2 * 0.007 * 10, 2) = 0.14."""
        bottlenecks = [{"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        result = propose(bottlenecks, profiles)
        expected = round(2 * CACHE_COST_PER_GB_MONTH * 10, 2)
        assert result[0]["estimated_cost_per_run"] == expected
        assert result[0]["estimated_time_saved_min"] == 2

    def test_zero_cost_for_serial_parallel(self):
        """serial_parallel: no runner cost, no cache cost → $0.00."""
        bottlenecks = [{"type": "serial_parallel", "job_name": "test", "evidence": "...", "severity": "low"}]
        profiles = [{"job_name": "test", "median_sec": 300}]
        result = propose(bottlenecks, profiles)
        assert result[0]["estimated_cost_per_run"] == 0.0

    def test_zero_cost_for_oversized_context(self):
        """oversized_context: .dockerignore is free → $0.00."""
        bottlenecks = [{"type": "oversized_context", "job_name": "docker", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "docker", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        assert result[0]["estimated_cost_per_run"] == 0.0

    def test_cost_per_run_is_float(self):
        bottlenecks = [{"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"}]
        profiles = [{"job_name": "test", "median_sec": 600}]
        result = propose(bottlenecks, profiles)
        assert isinstance(result[0]["estimated_cost_per_run"], float)


class TestRiskAssessment:
    def test_add_cache_is_low_risk(self):
        bottlenecks = [{"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"}]
        result = propose(bottlenecks, [{"job_name": "build", "median_sec": 600}])
        assert result[0]["risk_level"] == "low"

    def test_parallelize_jobs_is_medium_risk(self):
        bottlenecks = [{"type": "serial_parallel", "job_name": "test", "evidence": "...", "severity": "high"}]
        result = propose(bottlenecks, [{"job_name": "test", "median_sec": 600}])
        assert result[0]["risk_level"] == "medium"

    def test_reduce_matrix_is_high_risk(self):
        bottlenecks = [{"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"}]
        result = propose(bottlenecks, [{"job_name": "test", "median_sec": 600}])
        assert result[0]["risk_level"] == "high"

    def test_redundant_rebuild_is_medium_risk(self):
        bottlenecks = [{"type": "redundant_rebuild", "job_name": "build", "evidence": "...", "severity": "high"}]
        result = propose(bottlenecks, [{"job_name": "build", "median_sec": 600}])
        assert result[0]["risk_level"] == "medium"

    def test_oversized_context_is_low_risk(self):
        bottlenecks = [{"type": "oversized_context", "job_name": "docker", "evidence": "...", "severity": "high"}]
        result = propose(bottlenecks, [{"job_name": "docker", "median_sec": 600}])
        assert result[0]["risk_level"] == "low"


class TestSimulateSavings:
    def test_simulate_sums_selected_optimizations(self):
        opts = [
            {"estimated_time_saved_min": 5},
            {"estimated_time_saved_min": 3},
            {"estimated_time_saved_min": 2},
        ]
        assert simulate(opts) == 10

    def test_simulate_with_no_selections_returns_zero(self):
        assert simulate([]) == 0

    def test_simulate_with_single_optimization(self):
        assert simulate([{"estimated_time_saved_min": 7}]) == 7

    def test_simulate_ignores_missing_field(self):
        opts = [{"estimated_time_saved_min": 5}, {}, {"estimated_time_saved_min": 3}]
        assert simulate(opts) == 8

    def test_simulate_with_real_optimizations(self):
        bottlenecks = [
            {"type": "missing_cache", "job_name": "build", "evidence": "...", "severity": "high"},
            {"type": "redundant_matrix", "job_name": "test", "evidence": "...", "severity": "high"},
        ]
        profiles = [
            {"job_name": "build", "median_sec": 600},
            {"job_name": "test", "median_sec": 900},
        ]
        opts = propose(bottlenecks, profiles)
        total = simulate(opts)
        assert total == opts[0]["estimated_time_saved_min"] + opts[1]["estimated_time_saved_min"]
