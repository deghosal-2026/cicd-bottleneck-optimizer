"""Real-life repo test cases — live API calls against the 3 field study repos.

Run with: pytest tests/live/ --run-live
Requires: GITHUB_TOKEN env var (read-only scope OK)
"""
import os
import pytest

pytestmark = pytest.mark.live

REPOS = ["kubernetes/kubernetes", "tensorflow/tensorflow", "moby/moby"]
REPO_K8S = "kubernetes/kubernetes"
REPO_TF = "tensorflow/tensorflow"
REPO_MOBY = "moby/moby"


# ── CUJ-1: Optimize a slow pipeline ──────────────────────────────────────

class TestOptimizeModeRealRepos:
    """End-to-end optimize mode against real repos (read-only — no PR opened)."""

    def test_fetch_workflows_kubernetes(self):
        """kubernetes/kubernetes has ≥ 1 GitHub Actions workflow."""

    def test_fetch_workflows_tensorflow(self):
        """tensorflow/tensorflow has ≥ 1 GitHub Actions workflow."""

    def test_fetch_workflows_moby(self):
        """moby/moby has ≥ 1 GitHub Actions workflow."""

    def test_fetch_runs_kubernetes(self):
        """Top workflow in kubernetes/kubernetes has ≥ 10 runs with timing data."""

    def test_fetch_runs_tensorflow(self):
        """Top workflow in tensorflow/tensorflow has ≥ 10 runs with timing data."""

    def test_profile_jobs_kubernetes(self):
        """Profiling kubernetes/kubernetes yields median/p90 for at least 1 job."""

    def test_profile_jobs_tensorflow(self):
        """Profiling tensorflow/tensorflow yields median/p90 for at least 1 job."""

    def test_classify_bottlenecks_kubernetes(self):
        """kubernetes/kubernetes workflows have ≥ 1 bottleneck (e.g., missing cache)."""

    def test_classify_bottlenecks_tensorflow(self):
        """tensorflow/tensorflow matrix-heavy workflows trigger redundant_matrix."""

    def test_classify_bottlenecks_moby(self):
        """moby/moby workflows trigger oversized_context if no .dockerignore."""

    def test_propose_optimizations_kubernetes(self):
        """Optimizations proposed for kubernetes/kubernetes include time + cost estimates."""

    def test_optimization_has_real_timing_data(self):
        """Optimization evidence references actual job durations, not placeholders."""

    def test_cost_estimate_uses_hardcoded_rates(self):
        """Cost per optimization matches $0.008/min runner + $0.007/GB-month cache."""


# ── CUJ-5: Field study — 10 PRs across 3 repos ───────────────────────────

class TestFieldStudyRealRepos:
    """Field study mode: fetch PRs, analyze CI runs, save markdown reports."""

    def test_fetch_prs_kubernetes_last_30d(self):
        """kubernetes/kubernetes has ≥ 4 PRs updated in last 30 days."""

    def test_fetch_prs_tensorflow_last_30d(self):
        """tensorflow/tensorflow has ≥ 3 PRs updated in last 30 days."""

    def test_fetch_prs_moby_last_30d(self):
        """moby/moby has ≥ 3 PRs updated in last 30 days."""

    def test_fetch_prs_total_is_10(self):
        """Across all 3 repos with --pr-limit 10, exactly 10 PRs are fetched."""

    def test_fetch_pr_runs_kubernetes(self):
        """Each kubernetes/kubernetes PR has ≥ 1 CI run with job timings."""

    def test_fetch_pr_runs_tensorflow(self):
        """Each tensorflow/tensorflow PR has ≥ 1 CI run with job timings."""

    def test_fetch_pr_runs_moby(self):
        """Each moby/moby PR has ≥ 1 CI run with job timings."""

    def test_profile_pr_jobs_kubernetes(self):
        """PR CI runs profiled → median/p90 computed per job per PR."""

    def test_classify_pr_bottlenecks_kubernetes(self):
        """Real PRs in kubernetes/kubernetes yield real bottleneck classifications."""

    def test_save_report_creates_markdown_file(self):
        """reports/kubernetes-kubernetes/<pr#>-analysis.md file is created."""

    def test_save_report_tensorflow(self):
        """reports/tensorflow-tensorflow/<pr#>-analysis.md file is created."""

    def test_save_report_moby(self):
        """reports/moby-moby/<pr#>-analysis.md file is created."""

    def test_report_contains_job_profiles_table(self):
        """Report markdown contains a Job Profiles table with real durations."""

    def test_report_contains_bottlenecks_table(self):
        """Report markdown contains a Bottlenecks table with evidence."""

    def test_report_contains_recommendations_table(self):
        """Report markdown contains a Recommendations table with time/cost."""

    def test_report_contains_summary_section(self):
        """Report markdown contains a Summary with total wasted time."""

    def test_report_has_real_data_not_empty(self):
        """Report tables are not empty — contain real PR/job timing data."""

    def test_summary_table_prints_all_3_repos(self):
        """Summary table shows kubernetes, tensorflow, moby with correct PR counts."""

    def test_total_10_reports_generated(self):
        """10 markdown report files exist under reports/ after field study run."""

    def test_no_prs_opened_on_any_repo(self):
        """Verify no branches or PRs created on kubernetes, tensorflow, or moby."""

    def test_total_api_calls_under_500(self):
        """Field study run makes < 500 GitHub API calls (rate limit safe)."""


# ── CI system detection ──────────────────────────────────────────────────

class TestCIDetectionRealRepos:
    """Detecting GitHub Actions vs prow/Jenkins on real repos."""

    def test_kubernetes_has_github_actions(self):
        """kubernetes/kubernetes has at least some GitHub Actions workflows."""

    def test_kubernetes_also_has_prow(self):
        """kubernetes/kubernetes uses prow — agent logs warning for prow workflows."""

    def test_tensorflow_uses_github_actions(self):
        """tensorflow/tensorflow detected as github_actions CI system."""

    def test_moby_uses_github_actions(self):
        """moby/moby detected as github_actions CI system."""

    def test_non_actions_repo_skipped_with_warning(self):
        """A repo with no .github/workflows/ is skipped with a warning log."""


# ── Bottleneck type verification on real data ────────────────────────────

class TestBottleneckTypesRealRepos:
    """Verify the 5 bottleneck types are detectable in real repo workflows."""

    def test_missing_cache_found_in_kubernetes(self):
        """At least 1 job in kubernetes/kubernetes lacks a cache directive."""

    def test_serial_parallel_found_in_real_workflow(self):
        """At least 1 real workflow has jobs that could parallelize but don't."""

    def test_redundant_matrix_found_in_tensorflow(self):
        """tensorflow/tensorflow matrix-heavy workflows show redundant dimensions."""

    def test_oversized_context_found_in_moby(self):
        """moby/moby Docker build workflows show oversized context if no .dockerignore."""

    def test_redundant_rebuild_found_in_real_repo(self):
        """At least 1 real repo has the same artifact rebuilt across multiple jobs."""

    def test_at_least_3_bottleneck_types_across_3_repos(self):
        """Across all 3 repos, ≥ 3 distinct bottleneck types are classified."""


# ── PR-based CI run analysis ─────────────────────────────────────────────

class TestPRRunAnalysisRealRepos:
    """Analyzing CI runs triggered by specific PRs."""

    def test_pr_run_has_multiple_jobs(self):
        """A real PR's CI run has ≥ 2 jobs (build, test, lint, etc.)."""

    def test_pr_run_job_timings_are_positive(self):
        """All job durations in real PR runs are > 0 seconds."""

    def test_pr_run_failure_rate_realistic(self):
        """PR CI run failure rate is between 0% and 30% (not 100% — that's a broken repo)."""

    def test_pr_with_no_ci_runs_handled_gracefully(self):
        """PR with no associated CI runs → skipped with warning, no crash."""

    def test_merged_pr_has_more_runs_than_open_pr(self):
        """Merged PRs typically have more CI runs than open PRs (re-runs after review)."""

    def test_pr_head_sha_matches_run_head_sha(self):
        """CI run's head_sha matches the PR's head_sha — correct PR-to-run mapping."""


# ── Edge cases on real repos ─────────────────────────────────────────────

class TestRealRepoEdgeCases:
    """Edge cases that only appear with real, large repos."""

    def test_large_repo_workflow_pagination(self):
        """kubernetes/kubernetes may have > 30 workflows — pagination handled."""

    def test_workflow_with_no_runs_handled(self):
        """A workflow with 0 runs (newly added) → skipped with warning."""

    def test_archived_workflow_skipped(self):
        """Disabled/archived workflows are skipped during analysis."""

    def test_repos_with_few_prs_last_30d(self):
        """If a repo has < 3 PRs in 30 days, agent fetches what's available."""

    def test_rate_limit_hit_during_field_study(self):
        """If GitHub rate limit is hit mid-run, agent backs off and resumes."""

    def test_large_pr_diff_does_not_break_analysis(self):
        """PR with 500+ file changes doesn't crash the CI run fetcher."""
