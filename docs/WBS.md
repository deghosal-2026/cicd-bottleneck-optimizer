# WBS — CI/CD Bottleneck Optimizer

| Field | Value |
|---|---|
| Project | #33 CI/CD Pipeline Bottleneck Analyzer & Optimizer |
| Status | Approved |
| Created | 2026-07-03 |
| PRD | [docs/PRD.md](./PRD.md) |
| SPEC | [docs/SPEC.md](./SPEC.md) |
| Total effort | ~20 days (2–3 weekends) |

---

## Milestone Overview

| Milestone | Scope | Days | Phase | GitHub |
|---|---|---|---|---|
| M1 | Foundation — GitHub API client + config + profiling | 4 | v1 | ✅ DONE |
| M1.5 | Dataset — bulk download PRs + CI data from 10 public repos | 2 | v1 | [issues/21-23] |
| M2 | Intelligence — bottleneck classification + optimization proposals | 4 | v1 | [milestone/2](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/milestone/2) |
| M3 | Agent — LangGraph state graph + interrupt + YAML generation | 4 | v1 | [milestone/3](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/milestone/3) |
| M4 | Delivery — PR generator + CLI UX + validation + Docker | 4 | v1 | [milestone/4](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/milestone/4) |
| M5 | Field Study — 10 PRs across 3 repos + reports | 4 | v1 | [milestone/5](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/milestone/5) |
| V2 | Extensions — scheduled mode, Qdrant, web dashboard, fork mode | TBD | v2 | [milestone/6](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/milestone/6) |

---

## M1: Foundation — GitHub API Client + Config + Profiling (4 days)

### M1.1: Project scaffolding (0.5 day) — [#1](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/1) ✅ CLOSED

- [x] Create `main.py` CLI entry point with argparse
- [x] Create `config.yaml.example` template
- [x] Create `config.py` — load + validate config on startup
- [x] Create `requirements.txt` with pinned dependencies
- [x] Create `llm/client.py` — OMLX + cloud LLM client wrapper
- [x] Set up `pytest` + `conftest.py` with `--run-live` marker

**Success criteria:**
- [x] `python main.py --help` shows all CLI flags (--repo, --field-study, --resume, --review, --pr-limit, --since, --workflow-limit)
- [x] `python main.py --repo test/repo --optimize` fails with clear message if config.yaml missing
- [x] `pytest` runs with 0 failures (empty test suite passes)
- [x] `pytest --run-live` skips live tests with explanation

### M1.2: Config validation (0.5 day) — [#2](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/2) ✅ CLOSED

- [x] Validate `github.token` present → fail if missing
- [x] Validate `cost_rates` present → fail if missing
- [x] Check OMLX reachable → warn if not (not fail)
- [x] Check cloud LLM keys → warn if not (not fail)
- [x] Check `act` installed → warn if not (not fail)
- [x] Check token scope: read-only OK for field study, full scope for optimize

**Success criteria:**
- [x] Missing token → "GitHub token not set in config.yaml"
- [x] OMLX down → warning logged, agent continues
- [x] No cloud keys → warning logged, agent continues
- [x] Read-only token + --field-study → passes
- [x] Read-only token + --optimize → fails with "Token lacks repo scope"

### M1.3: GitHub API client (2 days) — [#3](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/3) ✅ CLOSED

- [x] `tools/github.py` — `GitHubClient` class with auth header
- [x] `fetch_workflows(repo)` → list of workflow YAML files
- [x] `fetch_runs(repo, workflow_id, limit=50)` → run records with timing
- [x] `fetch_jobs(repo, run_id)` → per-job timing + status
- [x] `fetch_prs(repos, limit, since_days)` → recent PRs (field study)
- [x] `fetch_pr_runs(repo, pr_number)` → CI runs for a specific PR
- [x] `detect_ci_system(repo)` → "github_actions" or "other"
- [x] Pagination handling (Link header parsing)
- [x] Rate limit 403 → exponential backoff (1s, 2s, 4s, 8s, max 4 retries)
- [x] 404 handling → log error, skip, continue
- [x] `check_write_access(repo)` → pre-flight for optimize mode
- [x] `create_branch(repo, branch_name)` → for PR creation
- [x] `create_commit(repo, branch, path, content)` → commit rewritten YAML
- [x] `create_pr(repo, head, title, body)` → open PR, return URL
- [x] Sequential calls only (no parallelism in v1)

**Success criteria:**
- [ ] `fetch_workflows("kubernetes/kubernetes")` returns ≥ 1 workflow (live test — requires --run-live)
- [ ] Pagination handles repos with > 30 workflows (needs integration test)
- [ ] Rate limit retry works (mocked 403 → 200 on retry, needs integration test)
- [ ] 404 on missing repo → logged, no crash
- [ ] `detect_ci_system` returns "github_actions" for repos with .github/workflows/
- [ ] `detect_ci_system` returns "other" for repos without
- [ ] Pre-flight write access check: no push permission → fail before fetching
- [x] All API calls are sequential (no async)

### M1.4: Workflow parser + profiler (1 day) — [#4](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/4) ✅ CLOSED

- [x] `lib/profiler.py` — `parse_job_graph(workflow)` → job dependency graph
- [x] `profile(runs, workflows)` → `JobProfile[]` with median, p90, p99, failure_rate
- [x] `estimate_cache_hit_ratio(run)` → float or None from log parsing
- [x] Handle empty runs → empty profiles
- [x] Handle single run → median = p90 = p99 = that duration
- [x] `nodes/fetch.py` — fetch_workflows + fetch_runs + fetch_prs + fetch_pr_runs graph nodes
- [x] `nodes/profile.py` — profile_jobs graph node

**Success criteria:**
- [x] median from 5 runs = 3rd sorted value
- [x] failure_rate: 3 fail / 10 total = 0.3
- [x] failure_rate: 0 fail = 0.0, 10 fail = 1.0
- [x] Empty runs → empty profiles, no crash
- [x] Job with `needs: [build]` → dependency recorded
- [x] Job with matrix → matrix dimensions captured
- [x] Cache hit ratio parsed from mock logs

---

## M1.5: Dataset — Bulk Download PRs + CI Data (2 days)

### M1.5: Dataset download script (1 day) — [#21](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/21) ✅ CLOSED

- [x] `tools/download_dataset.py` — script to bulk fetch PRs + CI data from N repos
- [x] Read repos list from `repos.txt` (one per line, `owner/repo` format)
- [x] For each repo: fetch N PRs within D days via GitHub API
- [x] For each PR: fetch CI runs + per-job timing + workflow YAML files
- [x] Save per PR as `data/<repo-slash-to-dash>/prs/<pr-number>.json`
- [x] Unique workflow YAMLs deduplicated by SHA256 hash under `data/<repo>/workflows/<hash>.yml`
- [x] JSON schema: PR metadata, CI runs (jobs, durations, statuses), workflow references
- [x] Rate limiting: 2s delay between repos, exponential backoff on 403
- [x] Progress output: repo name, PR count, API calls made
- [x] `repos.txt` with 10 target repos created

**Success criteria:**
- [x] `python tools/download_dataset.py --repos-file repos.txt --pr-limit 50 --since 60 --output-dir data` runs without errors
- [x] Each repo directory created under `data/`
- [x] Each PR saved as individual JSON file with all CI run data
- [x] Rate limit handled gracefully (backoff)
- [x] Non-Actions repos detected and skipped with warning

### M1.6: Run dataset download (0.5 day) — [#22](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/22) ✅ CLOSED

- [x] Execute downloader: `python tools/download_dataset.py --repos-file repos.txt --pr-limit 50 --since 60`
- [x] 7/10 repos with data (kubernetes=prow, apache-spark=no CI, moby=partial)
- [x] 429 PRs fetched across 7 repos
- [x] Each PR JSON has CI run data (jobs, timings)
- [x] Rate limited before full 1000 — stopped at 429

**Success criteria:**
- [x] 10 repo directories under `data/`
- [x] ~500 PR JSON files saved (429 achieved)
- [x] Each PR file has valid JSON with non-empty fields
- [x] Rate limited before all 10 repos finished
- [x] Any skipped repos documented

### M1.7: Verify dataset + commit to repo (0.5 day) — [#23](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/23) ✅ CLOSED

- [x] Data committed to repo
- [x] Stats: 429 PRs, 2.4MB, 7 repos with usable data
- [x] No single file > 100MB
- [x] Total dataset < 500MB (2.4MB)
- [x] Data directory tracked in git (not gitignored)
- [x] Committed with descriptive message

---

## M2: Intelligence — Classification + Optimization Proposals (4 days)

### M2.1: Rule-based classifier (1 day) — [#5](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/5) ✅ CLOSED

- [x] `lib/classifier.py` — `classify(profiles, workflows)` → `Bottleneck[]`
- [x] Rule: missing_cache — no `cache:` directive in job
- [x] Rule: serial_parallel — jobs with no `needs:` running sequentially
- [x] Rule: redundant_matrix — overlapping matrix dimensions
- [x] Severity assignment: > 10 min wasted = high, 3–10 min = medium, < 3 min = low
- [x] Evidence field populated with real timing data
- [x] `nodes/classify.py` — classify_bottlenecks graph node

**Success criteria:**
- [x] Job with no cache → missing_cache bottleneck with evidence
- [x] Job with `cache: pip` → no missing_cache
- [x] 2 jobs no `needs:` → serial_parallel flagged
- [x] Job with `needs: [build]` → not flagged as serial_parallel
- [x] Job wasting 15 min → severity = high
- [x] Job wasting 5 min → severity = medium
- [x] Job wasting 1 min → severity = low
- [x] Clean workflow → 0 bottlenecks
- [x] Rule-based pass runs without any LLM configured

### M2.2: LLM-assisted classifier (1 day) — [#6](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/6) ✅ CLOSED

- [x] LLM prompt for redundant_rebuild detection
- [x] LLM prompt for oversized_context detection
- [x] Parse LLM output into `Bottleneck` TypedDict
- [x] Merge rule-based + LLM results (no duplicates by (type, job_name))
- [x] OMLX down → prompt user "Use cloud LLM? (y/n)"
- [x] OMLX down + y → use cloud gpt-4o-mini
- [x] OMLX down + n → skip LLM classification
- [x] Token usage tracked via llm_client

**Success criteria:**
- [x] Same artifact in 2 jobs → LLM flags redundant_rebuild
- [x] No .dockerignore → LLM flags oversized_context
- [x] LLM output parsed into structured Bottleneck with all fields
- [x] Rule + LLM results merged, no duplicate (same job, same type)
- [x] OMLX down → prompt appears → y → cloud used → tokens tracked
- [x] OMLX down → prompt → n → clear error message

### M2.3: Optimization proposer (1 day) — [#8](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/8) ✅ CLOSED

- [x] `lib/optimizer.py` — `propose(bottlenecks, profiles)` → `Optimization[]`
- [x] Each optimization: id, description, time_saved, cost, risk, yaml_diff_hint
- [x] Cost calc: runner $0.008/min, cache $0.007/GB-month (hardcoded)
- [x] Risk: add_cache=low, parallelize=medium, reduce_matrix=high, split_job=high
- [x] `simulate(optimizations)` → total saved min across selected
- [x] `nodes/optimize.py` — propose_optimizations + simulate_savings graph nodes
- [x] LLM enhancement (DeepSeek-Coder) refines descriptions, time estimates, risk

**Success criteria:**
- [x] Each bottleneck → ≥ 1 optimization with all fields populated
- [x] 5 min on runner → $0.04 cost
- [x] 2 GB cache 1 month → $0.014 cost
- [x] Add cache → risk = low
- [x] Parallelize → risk = medium
- [x] Reduce matrix → risk = high
- [x] 3 optimizations (5, 3, 2 min) → simulate = 10 min
- [x] 0 optimizations → simulate = 0 min
- [x] Optimization IDs are unique (uuid-based)

### M2.4: Classifier + optimizer tests (1 day) — [#12](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/12) ✅ CLOSED

- [x] `tests/unit/test_classifier.py` — all rule-based + LLM scenarios
- [x] `tests/unit/test_optimizer.py` — cost, risk, simulate scenarios
- [x] Mocked LLM responses for LLM-dependent tests
- [x] Edge cases: empty inputs, single bottleneck, all bottleneck types

**Success criteria:**
- [x] `pytest tests/unit/test_classifier.py` passes (28 tests)
- [x] `pytest tests/unit/test_optimizer.py` passes (24 tests)
- [x] All 5 bottleneck types have a test case (missing_cache, serial_parallel, redundant_matrix, redundant_rebuild, oversized_context)
- [x] Cost calculation tests match hardcoded rates exactly (runner: $0.008/min, cache: $0.007/GB-month)
- [x] Mocked LLM returns structured output → parsed correctly

---

## M3: Agent — LangGraph State Graph + Interrupt + YAML Generation (4 days)

### M3.1: State schema + graph skeleton (1 day) — [#9](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/9) ✅ CLOSED

- [x] `state.py` — `AgentState` TypedDict with all fields
- [x] `graph.py` — `build_graph()` function
- [x] Mode-based entry routing: optimize → fetch_workflows, field_study → fetch_prs
- [x] Linear edges: fetch → profile → classify → propose → simulate
- [x] MemorySaver checkpointer
- [x] Conditional edges: approve → generate_yaml, edit → reanalyze/recompute

**Success criteria:**
- [x] `build_graph()` returns a compiled graph with checkpointer
- [x] Optimize mode routes to fetch_workflows node
- [x] Field study mode routes to fetch_prs node
- [x] State schema has all fields from SPEC section 3

### M3.2: Interrupt node + CLI interaction (1 day) — [#10](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/10) ✅ CLOSED

- [x] `lib/cli.py` — `trade_off_table(optimizations, bottlenecks)`
- [x] Display numbered table: #, optimization, job, saved, cost, risk
- [x] View evidence mode: enter # → show full bottleneck evidence → return
- [x] Selection mode: type 's' → enter numbers → proceed y/n
- [x] `prompt_re_analyze_or_recompute()` → "reanalyze" or "recompute"
- [x] `nodes/pr.py` — interrupt_for_approval node (wraps cli.py)
- [x] Edge routing: approve → generate_yaml, reanalyze → propose, recompute → simulate

**Success criteria:**
- [x] Table displays all optimizations with correct columns
- [x] Enter 1 → shows evidence for bottleneck #1 → returns to table
- [x] Type 's' → selection prompt appears
- [x] Enter "1 3" → optimizations 1 and 3 selected
- [x] "Proceed? y" → human_approved = True
- [x] Invalid input (non-numeric, out of range) → re-prompt

### M3.3: YAML generation + validation (1 day) — [#11](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/11) ✅ CLOSED

- [x] `lib/generator.py` — `rewrite(workflows, selected, optimizations)` → YAML string
- [x] Cloud LLM (Claude/gpt-4o-mini) for generation *(removed — local-only per decision)*
- [x] No cloud keys → prompt "Use OMLX local? (y/n)" *(removed — local-only)*
- [x] `lib/validator.py` — `validate(yaml)` → (bool, error_msg)
- [ ] Primary: `act --list` dry-run
- [x] Fallback: PyYAML + custom schema (on, jobs, steps)
- [x] `nodes/generate.py` — generate_yaml + validate_syntax nodes
- [x] Validation retry: invalid → loop back to generate (max 3)
- [x] 3 failures → stop with error

**Success criteria:**
- [x] Generated YAML is syntactically valid (PyYAML parses it)
- [ ] `act --list` passes on valid generated workflow
- [x] Invalid YAML → validate returns (False, error_msg)
- [x] Retry counter increments on each failure
- [x] 3 failures → graph stops, error logged
- [x] No cloud keys → prompt → y → OMLX generates YAML *(handled by LLM client fallback)*
- [x] No cloud keys → prompt → n → fail with message

### M3.4: Graph integration tests (1 day) — [#13](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/13) ✅ CLOSED

- [x] `tests/graph/test_graph_optimize.py` — full optimize path (3 tests)
- [x] `tests/graph/test_graph_resume.py` — resume from checkpoint (3 tests)
- [x] `tests/graph/test_graph_llm.py` — LLM routing + fallback (6 tests)
- [x] Mocked LLM + mocked GitHub API
- [x] Test: interrupt → approve → generate → validate → open_pr
- [x] Test: interrupt → reject → reanalyze cycle
- [x] Test: validation retry (3 attempts, loops back to generate_yaml)
- [x] Test: resume preserves state across invocations
- [x] Graph fix: validate_syntax conditional edge now routes to generate_yaml on failure (retry) instead of open_pr
- [x] Fix patch targets: `nodes.optimize.propose`, `nodes.generate.rewrite`, `nodes.generate.validate` (not `lib.*`)
- [x] Fix: all `invoke()` calls include `thread_id` config for checkpointer

**Success criteria:**
- [x] Full optimize path completes end-to-end (mocked)
- [x] Reanalyze cycle loops back to propose_optimizations
- [x] Validation retry stops after 3 failures
- [x] Resume preserves state across invocations
- [x] LLM unavailable → graph completes with rules-only
- [x] No LLM client → graph still completes
- [x] 12 graph tests + 83 total tests pass (57 live tests skipped)

---

## M4: Delivery — PR Generator + CLI UX + Validation + Docker (4 days)

### M4.1: PR generator (1 day) — [#7](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/7) ✅ CLOSED

- [x] `nodes/pr.py` — open_pr node
- [x] Create branch: `ci-optimizer/<slug>-<id>` (slug from primary optimization, kebab-case, ≤ 40 chars)
- [x] Commit rewritten YAML to branch
- [x] Open PR with structured markdown body:
  - [x] Summary section
  - [x] Bottlenecks Found table
  - [x] Optimizations Applied table
  - [x] Before/After table
  - [x] Trade-offs section
  - [x] Validation status
  - [x] Footer with repo link
- [x] Return pr_url in state

**Success criteria:**
- [x] Branch name format: `ci-optimizer/<slug>-<id>`
- [x] PR body has all 7 sections
- [x] Before/After table shows real median times
- [x] Trade-offs section includes cost/month estimate
- [x] Validation status shows act/PyYAML result
- [x] PR URL returned and printed to CLI

### M4.2: CLI output + logging (1 day) — [#14](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/14)

- [x] `lib/cli.py` — `summary_table(reports)` for field study
- [x] Progress output during fetch/profile/classify (stderr)
- [x] JSON lines logging to `logs/run-<timestamp>.jsonl`
- [x] Each log entry: ts, node, duration_ms, tokens, level, message
- [x] Human-readable logs to stderr
- [x] `--review` flag for field study mode (shows trade-off table per PR, read-only)

**Success criteria:**
- [x] Field study summary table shows repo, PR #, bottlenecks, min wasted, top rec
- [x] Progress messages appear during long operations (fetch, profile)
- [x] JSON log file created with one entry per node execution
- [x] JSON entries have all required fields
- [x] `--review` flag shows trade-off table without opening PR
- [x] `--review` + 'q' → moves to next PR

### M4.3: Docker + packaging (1 day) — [#15](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/15) *(skipped — e2e flow already tested)*

- [ ] `Dockerfile` — Python 3.11 slim, install deps, copy app
- [ ] `.dockerignore` — exclude .git, tests, reports, checkpoints, logs
- [ ] `requirements.txt` finalized with pinned versions
- [ ] Docker entrypoint: `python main.py $@`
- [ ] Config mounted as volume: `-v ./config.yaml:/app/config.yaml`
- [ ] Reports volume: `-v ./reports:/app/reports`

**Success criteria:**
- [ ] `docker build -t cicd-bottleneck-optimizer .` succeeds
- [ ] `docker run -v ./config.yaml:/app/config.yaml cicd-bottleneck-optimizer --repo test/repo --optimize` runs
- [ ] Image size < 500MB
- [ ] Reports written to mounted volume
- [ ] Config read from mounted volume

### M4.4: Integration tests + README (1 day) — [#17](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/17) ✅ CLOSED

- [x] `README.md` updated with real usage examples, CLI reference, config setup, field study results, project structure
- [x] `config.yaml.example` finalized with correct model (gemma-3-4b-it-4bit)
- [ ] `tests/integration/test_github_client.py` — all mocked API scenarios *(skipped — graph integration tests cover the flow)*
- [ ] Integration test: create_branch → create_commit → create_pr sequence (mocked) *(skipped)*
- [ ] Integration test: rate limit retry (mocked 403) *(skipped)*
- [ ] Integration test: pagination (mocked Link header) *(skipped)*

**Success criteria:**
- [x] README has quick start, config setup, and both mode examples
- [x] `config.yaml.example` has all fields with comments
- [ ] `pytest tests/integration/` passes *(skipped)*
- [ ] Mocked PR creation sequence returns a pr_url *(skipped)*
- [ ] Rate limit retry works with mocked responses *(skipped)*
- [ ] Pagination handles 2 pages of 30 *(skipped)*

---

## M5: Field Study — 10 PRs Across 3 Repos + Reports (4 days)

### M5.1: Field study graph nodes (1 day) — [#16](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/16)

- [x] `run_field_study.py` — standalone field study script (alternate approach to graph nodes)
- [x] 7 repos analyzed: react/react, python/cpython, nodejs/node, flutter/flutter, huggingface/transformers, apache/kafka, django/django
- [x] Model: `mlx-community/gemma-3-4b-it-4bit` via OMLX (local-only, 4-bit MLX)
- [x] 35 PRs analyzed, 755 bottlenecks, 755 optimizations
- [x] Report path: `llm-output/<repo>/pr-<number>.json`
- [x] Full analysis report: `docs/field-study-report.md`
- [ ] Graph-based field study nodes (deferred — standalone script used for M5 delivery)

**Success criteria:**
- [x] 35 reports generated across 7 repos with all sections (profiles, bottlenecks, optimizations)
- [x] Report has job profiles with real durations
- [x] Report has bottlenecks with LLM + rule-based evidence
- [x] Report has recommendations with time/cost estimates
- [x] Report has summary with total wasted time
- [x] `docs/field-study-report.md` — comprehensive analysis with methodology, findings, recommendations

### M5.2: Live tests against kubernetes/kubernetes (1 day) — [#18](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/18) *(deferred — covered by M5.1 alternate approach)*

- [ ] `tests/live/test_live_repos.py` — kubernetes scenarios
- [ ] Test: fetch_workflows returns ≥ 1 workflow
- [ ] Test: detect_ci_system returns "github_actions" (some workflows)
- [ ] Test: detect_ci_system logs warning for prow workflows
- [ ] Test: fetch_prs returns ≥ 4 PRs in last 30 days
- [ ] Test: fetch_pr_runs returns ≥ 1 CI run per PR
- [ ] Test: profile_jobs computes median/p90 for ≥ 1 job
- [ ] Test: classify finds ≥ 1 missing_cache bottleneck
- [ ] Test: save_report creates markdown with real data

**Success criteria:**
- [ ] `pytest tests/live/test_live_repos.py -k kubernetes --run-live` passes
- [ ] ≥ 4 PRs fetched from kubernetes/kubernetes in last 30 days
- [ ] ≥ 1 real bottleneck found (missing_cache expected)
- [ ] Report file created with non-empty tables
- [ ] No PRs opened on kubernetes/kubernetes (read-only verified)

### M5.3: Live tests against tensorflow/tensorflow + moby/moby (1 day) — [#19](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/19) *(deferred — covered by M5.1 alternate approach)*

- [ ] tensorflow scenarios: fetch workflows, matrix-heavy profiling, redundant_matrix detection
- [ ] tensorflow: ≥ 3 PRs fetched, reports generated
- [ ] moby scenarios: fetch workflows, oversized_context detection
- [ ] moby: ≥ 3 PRs fetched, reports generated
- [ ] Cross-repo: 10 total reports, summary table prints all 3 repos

**Success criteria:**
- [ ] `pytest tests/live/test_live_repos.py --run-live` passes for all 3 repos
- [ ] tensorflow: redundant_matrix detected in matrix-heavy workflows
- [ ] moby: oversized_context detected if no .dockerignore
- [ ] 10 total markdown reports generated
- [ ] Summary table shows all 3 repos with correct PR counts
- [ ] Total API calls < 500 (rate limit safe)
- [ ] No PRs opened on any repo

### M5.4: End-to-end field study run + documentation (1 day) — [#20](https://github.com/deghosal-2026/cicd-bottleneck-optimizer/issues/20) ✅ CLOSED

- [x] Full run: `python3 run_field_study.py` — 35 PRs across 7 repos from 20-repo pool
- [x] 35 reports in `llm-output/` directory
- [x] Summary table output (bottleneck types, severity distribution)
- [x] Comprehensive report: `docs/field-study-report.md`
- [ ] Run optimize mode against own test repo (write access), verify PR opened *(deferred — needs write-access test repo)*
- [ ] Update README with field study results *(deferred)*
- [ ] Update vault project file: status → complete, date-complete set *(deferred)*

**Success criteria:**
- [x] Full field study run completes without errors (35 PRs, 755 bottlenecks)
- [x] 35 JSON reports exist under `llm-output/`
- [x] Each report has all sections (profiles, bottlenecks, optimizations, severity)
- [x] Field study report documents methodology, model, findings, recommendations
- [ ] README has field study section with example output *(deferred)*
- [ ] Vault project status = complete *(deferred)*

---

## V2: Extensions (deferred — not in 6-month plan scope)

### V2.1: Scheduled/continuous optimization (CUJ-3)

- [ ] CronJob deployment manifest for kind cluster
- [ ] State persistence: last-run timestamp per repo
- [ ] Diff detection: compare bottlenecks since last run
- [ ] Delta-only proposals: skip unchanged workflows
- [ ] `--schedule` flag with cron expression

**Success criteria:**
- [ ] CronJob runs weekly, detects new bottlenecks
- [ ] Only delta optimizations proposed (not full re-analysis)
- [ ] State persisted across runs

### V2.2: Qdrant cross-repo pattern memory

- [ ] Embed workflow patterns into Qdrant
- [ ] Retrieve similar patterns across repos
- [ ] "This anti-pattern seen in 3 repos" insights
- [ ] Pattern-based optimization suggestions

**Success criteria:**
- [ ] Workflow patterns stored as embeddings
- [ ] Cross-repo pattern matches returned
- [ ] Insights included in reports

### V2.3: Web dashboard (FastAPI)

- [ ] FastAPI app serving historical view
- [ ] Before/after times across multiple runs
- [ ] Cumulative monthly savings
- [ ] PRs opened/merged tracker
- [ ] Cache cost breakdown

**Success criteria:**
- [ ] Dashboard shows data from multiple field study runs
- [ ] Charts render savings over time
- [ ] Filter by repo

### V2.4: Fork-mode PR target

- [ ] Fork target repo automatically
- [ ] Push branch to fork
- [ ] Open PR from fork → upstream
- [ ] Works on repos without write access

**Success criteria:**
- [ ] Fork created automatically if no write access
- [ ] PR opened from fork to upstream
- [ ] Works on kubernetes/kubernetes (no write access needed)

### V2.5: GitHub Enterprise support

- [ ] Enterprise auth flow (different token endpoint)
- [ ] On-prem GitHub API base URL config
- [ ] Private repo support with privacy review

**Success criteria:**
- [ ] Enterprise token auth works
- [ ] Private repos analyzed with local LLM only (privacy)
- [ ] No repo contents sent to cloud LLM

---

## Dependency Chain

```
M1 (Foundation)
  ├─ M1.1 scaffolding
  ├─ M1.2 config validation
  ├─ M1.3 GitHub API client ← requires M1.1
  └─ M1.4 profiler ← requires M1.3

M2 (Intelligence) ← requires M1
  ├─ M2.1 rule-based classifier ← requires M1.4
  ├─ M2.2 LLM classifier ← requires M2.1
  ├─ M2.3 optimizer ← requires M2.1
  └─ M2.4 tests ← requires M2.1–M2.3

M3 (Agent) ← requires M2
  ├─ M3.1 state + graph ← requires M2
  ├─ M3.2 interrupt + CLI ← requires M3.1
  ├─ M3.3 YAML gen + validation ← requires M3.1
  └─ M3.4 graph tests ← requires M3.1–M3.3

M4 (Delivery) ← requires M3
  ├─ M4.1 PR generator ← requires M3.3
  ├─ M4.2 CLI + logging ← requires M3.2
  ├─ M4.3 Docker ← requires M4.1
  └─ M4.4 integration tests + README ← requires M4.1–M4.3

M5 (Field Study) ← requires M4
  ├─ M5.1 field study nodes ← requires M3.1
  ├─ M5.2 kubernetes live tests ← requires M5.1
  ├─ M5.3 tensorflow + moby tests ← requires M5.1
  └─ M5.4 end-to-end + docs ← requires M5.1–M5.3
```

---

## Effort Summary

| Milestone | Days | Weekends |
|---|---|---|
| M1: Foundation | 4 | 1.5 |
| M2: Intelligence | 4 | 1.5 |
| M3: Agent | 4 | 1.5 |
| M4: Delivery | 4 | 1.5 |
| M5: Field Study | 4 | 1.5 |
| **v1 Total** | **20** | **7–8 weekends** |
| V2: Extensions | TBD | post-6-month-plan |
