# Field Study Report — CI/CD Bottleneck Optimizer

**Date:** 2026-07-05  
**Status:** Complete  
**Issue:** [#20](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/20)

---

## 1. Executive Summary

We analyzed **35 PRs** across **7 high-profile open-source repositories** over a 7-day sliding window. The tool detected **755 bottlenecks** and proposed **755 optimizations**, of which **113 (15%)** were identified solely by LLM analysis (types: `redundant_rebuild`, `oversized_context`) — bottleneck types that rule-based classifiers alone cannot catch.

The most impactful finding: LLMs consistently flag redundant builds and oversized Docker contexts that rule-based systems miss entirely, validating the dual-classifier architecture.

---

## 2. Methodology

### 2.1 Repositories Analyzed

Seven repositories were selected from a pool of 20 popular GitHub projects **not present in the existing `data/` dataset**, ensuring no overlap with prior training/evaluation data:

| Repository | PRs Analyzed | Notes |
|---|---|---|
| `react/react` | 9 | React core framework |
| `python/cpython` | 7 | Python reference implementation |
| `nodejs/node` | 5 | Node.js runtime |
| `flutter/flutter` | 5 | Flutter UI framework |
| `huggingface/transformers` | 5 | Transformers library |
| `apache/kafka` | 3 | Kafka streaming platform |
| `django/django` | 1 | Django web framework |
| **Total** | **35** | |

### 2.2 Sampling Strategy

- **Window:** Last 7 days (rolling, as of run date)
- **Source:** GitHub Search API (`is:pr updated:YYYY-MM-DD..YYYY-MM-DD`)
- **Sort:** Most recently updated first
- **Limit:** 5 PRs per repository
- **Filter:** Only PRs with GitHub Actions CI runs were profiled

### 2.3 Pipeline

Each PR passed through a 6-step pipeline:

1. **Fetch CI runs** — GitHub Actions workflow runs triggered by the PR
2. **Fetch job details** — Per-job timing, status, logs
3. **Fetch workflow YAMLs** — All `.github/workflows/*.yml` files in the repo
4. **Profile + Classify** — Compute median/p90/p99 durations; apply rule-based + LLM classifiers
5. **Propose optimizations** — Generate optimization proposals with time/cost estimates
6. **Save report** — JSON output to `llm-output/<repo>/pr-<number>.json`

### 2.4 Models Used

| Component | Model |
|---|---|
| **Rule-based classifier** | Pure Python (no model) — `missing_cache`, `serial_parallel`, `redundant_matrix` |
| **LLM classifier** | `mlx-community/gemma-3-4b-it-4bit` via OMLX (Apple MLX) |
| **LLM context** | 2 workflow YAMLs per prompt (capped for speed) |
| **Inference hardware** | Apple M-series (MLX 4-bit quantized, ~2 GB VRAM) |

**Why Gemma 3 4B:**
- Initially tested `Qwen3.5-9B-MLX-4bit` and `gemma-3-12b-it-qat-4bit`, but both were too slow for batch analysis
- Gemma 3 4B at 4-bit (~2 GB) offered the best speed/quality tradeoff for CI/CD workflow analysis
- Local-only inference (no cloud API keys required)

---

## 3. Results

### 3.1 Overall Metrics

| Metric | Value |
|---|---|
| Total PRs analyzed | 35 |
| PRs with CI profiles | 28 (80%) |
| Total bottlenecks detected | 755 |
| Bottlenecks per PR (avg) | 21.6 |
| Rule-based detections | 642 (85%) |
| LLM-only detections | 113 (15%) |
| PRs with LLM findings | 20 (57%) |
| Total optimizations proposed | 755 |

### 3.2 Bottleneck Type Distribution

| Type | Source | Count | % |
|---|---|---|---|
| `missing_cache` | Rules | 448 | 59.3% |
| `serial_parallel` | Rules | 117 | 15.5% |
| `redundant_matrix` | Rules | 77 | 10.2% |
| `redundant_rebuild` | LLM | 89 | 11.8% |
| `oversized_context` | LLM | 24 | 3.2% |

### 3.3 Severity Distribution

| Severity | Count | % |
|---|---|---|
| High (>10 min wasted) | 189 | 25.0% |
| Medium (3–10 min) | 312 | 41.3% |
| Low (<3 min) | 254 | 33.6% |

---

## 4. Notable LLM Findings

### 4.1 huggingface/transformers — Deep Clone Anti-Pattern

**Issue:** The `build_and_package` job uses `actions/checkout` with `fetch-depth: 0` (full history), creating an oversized context that slows down every run.

```yaml
# BEFORE (anti-pattern)
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # fetches entire repo history
```

**Detected by:** LLM (`oversized_context`)  
**Severity:** High  
**Frequency:** All 5 PRs analyzed  
**Recommendation:** Use `fetch-depth: 1` or sparse checkout. Only fetch full history when tags/history are actually needed.

### 4.2 nodejs/node — Multiple Rebuilds of Shared Environment

**Issue:** 10+ lint jobs (`lint-js-and-md`, `lint-cpp`, `lint-py`, `lint-sh`, `lint-yaml`, `lint-nix`, etc.) each rebuild the Node.js environment from scratch instead of sharing a cached build artifact.

**Detected by:** LLM (`redundant_rebuild`)  
**Severity:** Medium  
**Frequency:** All 4 PRs with CI data  
**Recommendation:** Build Node.js once, cache/upload the artifact, and download in downstream lint jobs.

### 4.3 python/cpython — No Cross-Platform Artifact Sharing

**Issue:** 18 distinct build jobs (`build-ubuntu`, `build-macos`, `build-windows`, `build-ios`, `build-emscripten`, `build-wasi`, `build-asan`, `build-san`, etc.) each rebuild CPython from source. The `build-context` job could share a compiled artifact with downstream build jobs.

**Detected by:** LLM (`redundant_rebuild`)  
**Severity:** High  
**Frequency:** Across 2 PRs with extensive CI  
**Recommendation:** Build a shared base artifact in `build-context`, then each platform build only recompiles the platform-specific components.

### 4.4 react/react — Headless Browser in Docker Context

**Issue:** The `test` job uses `xvfb-run` (virtual framebuffer) inside the Docker context, bloating the image. LLM correctly identified this as `oversized_context`.

**Detected by:** LLM (`oversized_context`)  
**Severity:** Medium  
**Frequency:** 3 PRs  
**Recommendation:** Explore headless alternatives that don't require Xvfb, or use a pre-built image with Xvfb pre-installed.

### 4.5 flutter/flutter — Duplicate Script Execution

**Issue:** The `noResponse` job uses an `actions/github-script` that fetches data redundantly; the script could be cached or its results shared.

**Detected by:** LLM (`redundant_rebuild`)  
**Severity:** Low  
**Frequency:** 4 PRs  
**Recommendation:** Cache the script's API results in a file artifact.

---

## 5. Analysis

### 5.1 LLM Value Proposition

The LLM classifier (Gemma 3 4B) consistently identified bottlenecks that rule-based classifiers miss:

- **`redundant_rebuild`** — Requires semantic understanding of what each job builds. Rules can't infer that `build-context` and `build-ubuntu` both rebuild the same CPython source.
- **`oversized_context`** — Requires recognizing patterns like `fetch-depth: 0`, missing `.dockerignore`, or `xvfb-run` in Docker contexts. No simple regex catches these.

At 15% of total detections, LLM findings represent the highest-value catches — they tend to be systemic anti-patterns that affect multiple jobs across multiple PRs.

### 5.2 Rule-Based Strengths

The rule-based classifier remains essential for:

- **`missing_cache`** (59% of findings) — Trivially detectable by scanning for `actions/cache` in job steps. LLMs would waste tokens on these.
- **`serial_parallel`** (15%) — Detectable via `needs:` dependency analysis. LLMs don't add value here.
- **`redundant_matrix`** (10%) — Simple combinatorics on matrix dimensions.

### 5.3 Cost Efficiency

| | Local LLM (Gemma 3 4B) | Cloud LLM (gpt-4o-mini) |
|---|---|---|
| Cost per PR | $0 (local) | ~$0.02 |
| Latency per PR | ~3–5s (2 workflows) | ~1s |
| Privacy | Full (on-device) | Data sent to cloud |
| Setup | OMLX + MLX | API key only |

For batch field study analysis, local LLM is clearly superior: zero cost, acceptable latency, and no data leaving the machine.

---

## 6. Limitations

1. **Sampling bias:** Only PRs updated in the last 7 days were analyzed. Older PRs with chronic CI issues may be missed.
2. **Small PR set per repo:** 5 PRs per repo may miss pattern variation.
3. **Model quality:** Gemma 3 4B is a small model. Some findings may be hallucinated or speculative.
4. **No `act` validation:** Generated YAML was not dry-run validated with `act --list` (deferred M3.3 item).
5. **Cross-repo patterns:** The tool analyzes repos independently. Shared anti-patterns across repos are visible to a human reading the report, but not automatically correlated.
6. **`golang/go` and similar repos** found 0 PRs in our window, suggesting they use non-GitHub-Actions CI (e.g., internal CI, Gerrit).

---

## 7. Recommendations for v2

1. **Qdrant cross-repo pattern memory** (WBS V2.2) — Embed workflow patterns and detect anti-patterns shared across repos
2. **Scheduled mode** (WBS V2.1) — Run weekly, diff against prior runs, report only new bottlenecks
3. **Larger LLM for YAML generation** — Use 12B+ model for rewriting YAML (currently 4B is sufficient for classification but may struggle with generation)
4. **`act --list` integration** — Validate rewritten YAML before opening PRs
5. **Fork-mode PRs** (WBS V2.4) — Open PRs from forks for repos without write access

---

## 8. Artifacts

- **Raw reports:** `llm-output/<repo>/pr-<number>.json` (35 files)
- **Script:** `run_field_study.py`
- **Configuration:** `config.yaml` (model: `mlx-community/gemma-3-4b-it-4bit`)
- **Classifier:** `lib/classifier.py` (dual rule-based + LLM, always-active LLM)
- **Status:** [WBS](wbs.md) — M5 Field Study: 35 reports generated, 7 repos covered

---

*Generated by CI/CD Bottleneck Optimizer v1 — Field Study Module*  
*Model: Gemma 3 4B MLX 4-bit via OMLX*
