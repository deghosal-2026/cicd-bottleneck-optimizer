"""Unit tests for classifier.py — bottleneck detection (rules + LLM hybrid)."""
import json
import pytest
from lib.classifier import (
    classify,
    _assign_severity,
    _merge_bottlenecks,
    _LLM_CACHE,
    _check_missing_cache,
    _check_serial_parallel,
    _check_redundant_matrix,
    _check_profiles_only,
)


@pytest.fixture(autouse=True)
def _clear_llm_cache():
    _LLM_CACHE.clear()


class TestRuleBasedClassification:
    def test_missing_cache_detected(self):
        jobs = [{"name": "build", "steps": [{"run": "npm install"}]}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        cache_bn = [b for b in result if b["type"] == "missing_cache"]
        assert len(cache_bn) == 1
        assert cache_bn[0]["job_name"] == "build"

    def test_missing_cache_not_flagged_when_cache_present(self):
        """Job with actions/cache step → no missing_cache, even with build-keyword name."""
        jobs = [{"name": "build", "steps": [{"uses": "actions/cache@v4"}, {"run": "npm install"}]}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        assert all(b["type"] != "missing_cache" for b in result)
        assert result == []

    def test_serial_parallel_detected(self):
        """Job with needs + real-work steps and median >= 30s → serial_parallel."""
        jobs = [{"name": "test", "steps": [{"run": "npm test"}], "needs": ["build"]}]
        profiles = [{"job_name": "test", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        serial = [b for b in result if b["type"] == "serial_parallel"]
        assert len(serial) == 1
        assert serial[0]["job_name"] == "test"

    def test_serial_parallel_not_flagged_when_no_real_work(self):
        """Job with needs but only echo/no-op steps → not flagged (no real work to parallelize)."""
        jobs = [{"name": "notify", "steps": [{"run": "echo done"}], "needs": ["build"]}]
        profiles = [{"job_name": "notify", "median_sec": 60}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        assert all(b["type"] != "serial_parallel" for b in result)

    def test_serial_parallel_not_flagged_when_fast(self):
        """Job with needs + real work but median < 30s → not flagged (too fast to matter)."""
        jobs = [{"name": "test", "steps": [{"run": "npm test"}], "needs": ["build"]}]
        profiles = [{"job_name": "test", "median_sec": 15}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        assert all(b["type"] != "serial_parallel" for b in result)

    def test_redundant_matrix_detected(self, matrix_workflow, matrix_profiles):
        result = classify(matrix_profiles, matrix_workflow)
        matrix_bn = [b for b in result if b["type"] == "redundant_matrix"]
        assert len(matrix_bn) == 1
        assert matrix_bn[0]["job_name"] == "test"

    def test_no_bottlenecks_in_clean_workflow(self):
        """Well-optimized workflow: cached build job, fast notify job → 0 bottlenecks."""
        jobs = [
            {"name": "build", "steps": [{"uses": "actions/cache@v4"}, {"run": "npm ci"}]},
            {"name": "notify", "steps": [{"run": "echo done"}], "needs": ["build"]},
        ]
        profiles = [
            {"job_name": "build", "median_sec": 60},
            {"job_name": "notify", "median_sec": 5},
        ]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        assert result == []

    def test_severity_high_for_long_wasted_time(self):
        assert _assign_severity(600) == "high"
        assert _assign_severity(900) == "high"

    def test_severity_medium_for_moderate_waste(self):
        assert _assign_severity(180) == "medium"
        assert _assign_severity(599) == "medium"

    def test_severity_low_for_small_waste(self):
        assert _assign_severity(30) == "low"
        assert _assign_severity(179) == "low"

    def test_empty_profiles_returns_empty_bottlenecks(self):
        assert classify([], [{"filename": "x.yml", "content": "", "jobs": []}]) == []

    def test_rule_based_pass_runs_without_llm(self):
        jobs = [{"name": "build", "steps": [{"run": "npm install"}]}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows, llm_client=None)
        assert len(result) == 1
        assert result[0]["type"] == "missing_cache"


class TestLLMClassification:
    _profiles = [{"job_name": "notify", "median_sec": 5}]
    _workflows = [{"filename": "ci.yml", "content": "", "jobs": [{"name": "notify", "steps": [{"run": "echo done"}]}]}]

    def test_redundant_rebuild_detected_by_llm(self, mock_llm_client):
        mock_llm_client.call_local.return_value = json.dumps([
            {"type": "redundant_rebuild", "job_name": "build", "evidence": "npm install in both build (420s) and test (360s)", "severity": "high"},
        ])
        result = classify(self._profiles, self._workflows, llm_client=mock_llm_client)
        assert any(b["type"] == "redundant_rebuild" and b["job_name"] == "build" for b in result)

    def test_oversized_context_detected_by_llm(self, mock_llm_client):
        mock_llm_client.call_local.return_value = json.dumps([
            {"type": "oversized_context", "job_name": "docker-build", "evidence": "No .dockerignore found", "severity": "medium"},
        ])
        result = classify(self._profiles, self._workflows, llm_client=mock_llm_client)
        assert any(b["type"] == "oversized_context" for b in result)

    def test_llm_returns_structured_bottleneck(self, mock_llm_client):
        mock_llm_client.call_local.return_value = json.dumps([
            {"type": "redundant_rebuild", "job_name": "build", "evidence": "Evidence text.", "severity": "high"},
        ])
        result = classify(self._profiles, self._workflows, llm_client=mock_llm_client)
        assert len(result) == 1
        b = result[0]
        assert b["type"] == "redundant_rebuild"
        assert b["job_name"] == "build"
        assert "evidence" in b
        assert b["severity"] == "high"

    def test_llm_returns_no_bottlenecks(self, mock_llm_client):
        mock_llm_client.call_local.return_value = "[]"
        result = classify(self._profiles, self._workflows, llm_client=mock_llm_client)
        assert result == []

    def test_llm_not_called_when_rules_find_bottlenecks(self, mock_llm_client):
        """When rules produce bottlenecks, LLM is never invoked."""
        jobs = [{"name": "build", "steps": [{"run": "npm install"}]}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        classify(profiles, workflows, llm_client=mock_llm_client)
        mock_llm_client.call_local.assert_not_called()

    def test_llm_called_when_rules_find_nothing(self, mock_llm_client):
        """When rules produce no bottlenecks, LLM is invoked as fallback."""
        mock_llm_client.call_local.return_value = "[]"
        jobs = [{"name": "notify", "steps": [{"run": "echo hi"}]}]
        profiles = [{"job_name": "notify", "median_sec": 5}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        classify(profiles, workflows, llm_client=mock_llm_client)
        mock_llm_client.call_local.assert_called_once()


class TestMergeBottlenecks:
    def test_merge_deduplicates_by_type_and_job_name(self):
        rules = [{"type": "missing_cache", "job_name": "build", "evidence": "R1", "severity": "medium"}]
        llm = [{"type": "missing_cache", "job_name": "build", "evidence": "R2", "severity": "high"}]
        merged = _merge_bottlenecks(rules, llm)
        assert len(merged) == 1
        assert merged[0]["evidence"] == "R1"

    def test_merge_keeps_distinct_bottlenecks(self):
        rules = [{"type": "missing_cache", "job_name": "build", "evidence": "R1", "severity": "medium"}]
        llm = [{"type": "redundant_rebuild", "job_name": "build", "evidence": "R2", "severity": "high"}]
        merged = _merge_bottlenecks(rules, llm)
        assert len(merged) == 2

    def test_merge_empty_inputs(self):
        assert _merge_bottlenecks([], []) == []

    def test_merge_preserves_order_rules_first(self):
        rules = [{"type": "missing_cache", "job_name": "build", "evidence": "rule", "severity": "low"}]
        llm = [{"type": "oversized_context", "job_name": "docker", "evidence": "llm", "severity": "high"}]
        merged = _merge_bottlenecks(rules, llm)
        assert merged[0]["evidence"] == "rule"
        assert merged[1]["evidence"] == "llm"


class TestProfilesOnly:
    def test_flags_build_keyword_job_without_cache(self):
        profiles = [{"job_name": "my-build-job", "median_sec": 300}]
        result = _check_profiles_only(profiles)
        assert len(result) == 1
        assert result[0]["type"] == "missing_cache"

    def test_skips_fast_jobs(self):
        profiles = [{"job_name": "build", "median_sec": 20}]
        assert _check_profiles_only(profiles) == []

    def test_skips_non_build_keyword_jobs(self):
        profiles = [{"job_name": "notify", "median_sec": 300}]
        assert _check_profiles_only(profiles) == []

    def test_skips_jobs_that_have_cache_in_workflow(self):
        """_check_profiles_only must not flag jobs already known to have cache."""
        profiles = [{"job_name": "build", "median_sec": 300}]
        result = _check_profiles_only(profiles, cached_jobs={"build"})
        assert result == []

    def test_flags_uncached_build_job_when_other_job_cached(self):
        profiles = [
            {"job_name": "build", "median_sec": 300},
            {"job_name": "test", "median_sec": 200},
        ]
        result = _check_profiles_only(profiles, cached_jobs={"build"})
        assert len(result) == 1
        assert result[0]["job_name"] == "test"


class TestEvidenceQuality:
    def test_evidence_contains_timing_data(self):
        jobs = [{"name": "build", "steps": [{"run": "npm install"}]}]
        profiles = [{"job_name": "build", "median_sec": 300}]
        workflows = [{"filename": "ci.yml", "content": "", "jobs": jobs}]
        result = classify(profiles, workflows)
        assert len(result) == 1
        assert "5m" in result[0]["evidence"]
        assert result[0]["severity"] == "medium"
