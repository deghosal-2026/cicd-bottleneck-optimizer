# SPEC — CI/CD Bottleneck Optimizer

| Field | Value |
|---|---|
| Project | #33 CI/CD Pipeline Bottleneck Analyzer & Optimizer |
| Status | Draft |
| Created | 2026-07-03 |
| PRD | [docs/PRD.md](./PRD.md) |

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        cicd-bottleneck-optimizer                            │
│                                                                             │
│  ┌────────────────┐     ┌───────────────────────────────────────────────┐  │
│  │  config.yaml   │────▶│              LangGraph Agent                  │  │
│  │  (gitignored)  │     │                                               │  │
│  │  ─ github.token│     │  ┌──────────┐  ┌───────────┐  ┌──────────┐  │  │
│  │  ─ local_llm   │     │  │  nodes/  │  │   lib/    │  │   llm/   │  │  │
│  │  ─ cloud_llm   │     │  │ fetch    │  │ profiler  │  │ client   │  │  │
│  │  ─ cost_rates  │     │  │ profile  │  │ classifier│  │ OMLX     │  │  │
│  │  ─ defaults    │     │  │ classify │  │ optimizer │  │ cloud    │  │  │
│  └────────────────┘     │  │ optimize │  │ generator │  └──────────┘  │  │
│                         │  │ generate │  │ validator │                 │  │
│  ┌────────────────┐     │  │ pr       │  │ reporter  │                 │  │
│  │  main.py (CLI) │────▶│  │          │  │ cli       │                 │  │
│  │  --repo        │     │  └──────────┘  └───────────┘                 │  │
│  │  --field-study │     │                  │         │                  │  │
│  │  --resume      │     │                  ▼         ▼                  │  │
│  │  --review      │     │  ┌─────────────────────────────────────────┐ │  │
│  │  --pr-limit    │     │  │           External Services             │ │  │
│  │  --since       │     │  │  ┌─────────┐ ┌────────┐ ┌───────────┐  │ │  │
│  │  --workflow-limit│    │  │ │ GitHub  │ │ OMLX   │ │ Cloud LLM │  │ │  │
│  └────────────────┘     │  │ │ REST API│ │ :8000  │ │ (optional)│  │ │  │
│                         │  │ └─────────┘ └────────┘ └───────────┘  │ │  │
│                         │  └─────────────────────────────────────────┘ │  │
│                         └───────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────┐    ┌──────────────────────┐    ┌─────────────────────┐   │
│  │  SQLite      │    │  reports/            │    │  logs/              │   │
│  │  checkpoints │    │  <repo>/             │    │  run-<ts>.jsonl     │   │
│  │  agent.db    │    │   <pr#>-analysis.md  │    │  (JSON lines)       │   │
│  │  (gitignored)│    │  (gitignored)        │    │  (gitignored)       │   │
│  └──────────────┘    └──────────────────────┘    └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Optimize Mode Flow (CUJ-1, CUJ-2, CUJ-4)

```
User: python main.py --repo owner/repo --optimize
  │
  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STARTUP                                                             │
│  1. Load + validate config.yaml (token, LLM, cost_rates)            │
│  2. Pre-flight: verify write access to target repo                   │
│     ├─ has push permission? ── NO ──▶ FAIL: "use --field-study"     │
│     └─ YES ── continue                                               │
│  3. Check `act` installed (warn if not)                              │
│  4. Check OMLX reachable (warn if not)                               │
│  5. Load or create SQLite checkpointer                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: fetch_workflows                                              │
│  ─ GET /repos/{owner}/{repo}/actions/workflows                      │
│  ─ GET /repos/{owner}/{repo}/contents/.github/workflows/{file}      │
│  ─ Detect CI system (skip if non-Actions, log warning)              │
│  ─ Sort by run frequency, take top N (default 5)                    │
│  ─ Output: workflows[] (YAML + parsed job graph)                    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: fetch_runs                                                   │
│  ─ For each workflow:                                               │
│    GET /repos/{owner}/{repo}/actions/workflows/{id}/runs            │
│    ?per_page=50                                                     │
│  ─ For each run:                                                    │
│    GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs             │
│  ─ Sequential calls, retry on 403 (exponential backoff)            │
│  ─ Output: runs[] (job timings, statuses, durations)               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: profile_jobs                                                 │
│  ─ Parse workflow YAML → job dependency graph                       │
│  ─ For each job across runs:                                        │
│    compute median_sec, p90_sec, p99_sec                             │
│    compute failure_rate (failures / total runs)                     │
│    estimate cache_hit_ratio (parse run logs)                        │
│  ─ Output: profiles[]                                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: classify_bottlenecks                                         │
│  ─ RULE-BASED PASS (no LLM):                                        │
│    • missing_cache: no `cache:` directive in job                    │
│    • serial_parallel: jobs with no `needs:` running sequentially    │
│    • redundant_matrix: overlapping matrix dimensions                │
│  ─ LLM PASS (OMLX Qwen3.5-9B):                                      │
│    • redundant_rebuild: same artifact built in multiple jobs        │
│    • oversized_context: large build context, no .dockerignore       │
│  ─ If OMLX down → prompt: "Use cloud LLM? (y/n)"                   │
│  ─ Output: bottlenecks[] (type, job, evidence, severity)           │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: propose_optimizations                                        │
│  ─ LLM (OMLX Qwen3.5-9B) generates candidates per bottleneck        │
│  ─ Each optimization gets:                                          │
│    • description, estimated_time_saved_min                          │
│    • estimated_cost_per_run (hardcoded rates: $0.008/min runner)   │
│    • risk_level (low/medium/high)                                   │
│    • yaml_diff_hint (what changes)                                  │
│  ─ Output: optimizations[]                                          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: simulate_savings                                             │
│  ─ Sum estimated time savings across all proposed optimizations     │
│  ─ Output: simulated_total_saved_min                                │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: interrupt_for_approval  ◀── CHECKPOINT PERSISTED ──┐       │
│                                                              │       │
│  CLI displays trade-off table:                              │       │
│    # | Optimization     | Job   | Saved | Cost  | Risk      │       │
│    1 | Add cache        | build | 5 min | $0.02 | Low       │       │
│    2 | Parallelize     | lint  | 3 min | $0.00 | Medium    │       │
│    3 | Reduce matrix   | test  | 8 min | $0.00 | High      │       │
│                                                              │       │
│  Two actions:                                               │       │
│    • Enter # to VIEW evidence for a bottleneck              │       │
│      ──▶ shows: type, job, severity, data-backed evidence   │       │
│      ──▶ returns to table                                   │       │
│    • Type 's' to enter SELECTION mode                       │       │
│      ──▶ "Select optimizations (e.g. 1 3): "                │       │
│      ──▶ "Proceed? (y/n): "                                 │       │
│                                                              │       │
│  ┌─────────────┬────────────────────────────────────────────┘       │
│  │ APPROVE (y) │                                                    │
│  └──────┬──────┘                                                    │
│         │    ┌──────────────┬────────────────────────────────┐      │
│         │    │ EDIT (n)     │                                 │      │
│         │    └──────┬───────┘                                 │      │
│         │           │                                         │      │
│         │           ▼                                         │      │
│         │  "Re-analyze with edits, or just recompute? (1/2)" │      │
│         │           │                                         │      │
│         │     ┌─────┴──────┐                                  │      │
│         │     ▼            ▼                                  │      │
│         │  reanalyze    recompute                              │      │
│         │     │            │                                   │      │
│         │     │            └──────────────────────────────────┼──┐   │
│         │     └───────────────────────────────────────────────┼──┼──│
│         │                                                     │  │  │
│         ▼                                                     │  │  │
│  generate_yaml ◀──────────────────────────────────────────────┘  │  │
│                                                                  │  │
│  (reanalyze loops back to propose_optimizations ─────────────────┘  │
│   recompute loops back to simulate_savings ────────────────────────┘
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: generate_yaml                                                │
│  ─ Cloud LLM (Claude/gpt-4o-mini) generates rewritten YAML         │
│  ─ If no cloud keys → prompt: "Use OMLX local? (y/n)"              │
│  ─ Output: rewritten_yaml                                           │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: validate_syntax                                              │
│  ─ Primary: `act --list` dry-run (most accurate)                    │
│  ─ Fallback: PyYAML + custom schema (if act not installed)         │
│  ─ If invalid: retry generate_yaml (max 3 attempts)                │
│  ─ After 3 failures: STOP with error                                │
│  ─ Output: validation_attempts, rewritten_yaml_valid               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: open_pr                                                      │
│  ─ Create branch: ci-optimizer/<slug>-<id>                         │
│  ─ Commit rewritten YAML to branch                                   │
│  ─ Open PR with structured markdown body:                           │
│    • Summary, Bottlenecks, Optimizations, Before/After table       │
│    • Trade-offs, Validation status                                  │
│  ─ Output: pr_url                                                   │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
                            END
                  PR opened on target repo
```

### 1.3 Field Study Mode Flow (CUJ-5)

```
User: python main.py --field-study \
    --repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby \
    --pr-limit 10 --since 30d [--review]
  │
  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STARTUP                                                             │
│  1. Load + validate config.yaml (read-only token OK)                │
│  2. No write access check needed (read-only mode)                   │
│  3. Check OMLX reachable (warn if not)                               │
│  4. Load or create SQLite checkpointer                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: fetch_prs                                                    │
│  ─ For each repo in --repos list:                                   │
│    GET /repos/{owner}/{repo}/pulls                                  │
│    ?state=all&sort=updated&direction=desc&per_page={pr_limit}      │
│  ─ Filter: PRs updated within --since days                          │
│  ─ Detect CI system per repo (skip non-Actions with warning)        │
│  ─ Output: prs[] (PR number, title, head_sha, updated_at)         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: fetch_pr_runs                                                │
│  ─ For each PR:                                                     │
│    GET /repos/{owner}/{repo}/actions/runs                           │
│    ?event=pull_request&head_sha={sha}                              │
│  ─ For each run:                                                    │
│    GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs             │
│  ─ Also fetch .github/workflows/*.yml for each repo                 │
│  ─ Sequential calls, retry on 403                                   │
│  ─ Output: pr_runs{pr_number: [RunRecord]}                         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: profile_jobs                                                 │
│  ─ Same as optimize mode: median, p90, failure_rate per job        │
│  ─ Profiled per PR's CI runs (not per workflow)                     │
│  ─ Output: profiles[]                                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: classify_bottlenecks                                         │
│  ─ Same as optimize mode: rules + OMLX LLM hybrid                   │
│  ─ Output: bottlenecks[]                                            │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: propose_optimizations                                        │
│  ─ Same as optimize mode: LLM generates candidates                  │
│  ─ Output: optimizations[]                                          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
                    ┌────────────┴────────────┐
                    │                         │
              --review flag?          no --review
                    │                         │
                    ▼                         ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  show trade_off_table         │  │  save_report                 │
│  (read-only, no PR opened)   │  │  ─ Write reports/<repo>/     │
│                              │  │    <pr#>-analysis.md         │
│  # | Optimization | Saved    │  │  ─ Markdown format:          │
│  1 | Add cache    | 5 min    │  │    • Job profiles table      │
│  2 | Parallelize  | 3 min    │  │    • Bottlenecks table       │
│                              │  │    • Recommendations table   │
│  Enter # to view evidence    │  │    • Summary stats           │
│  Type 'q' for next PR        │  │  ─ Output: report_path       │
│                              │  └──────────────┬───────────────┘
└──────────────┬───────────────┘                  │
               │                                  │
               ▼                                  │
┌──────────────────────────────┐                  │
│  save_report (same as above) │                  │
└──────────────┬───────────────┘                  │
               │                                  │
               └──────────────┬───────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GRAPH: print_summary                                                │
│  ─ Print summary table to CLI:                                      │
│    Repo              | PR #  | Bottlenecks | Min Wasted | Top Rec   │
│    kubernetes/k8s    | 12453 | 4           | 18 min     | Add cache │
│    tensorflow/tf     | 62341 | 5           | 22 min     | Split job │
│    moby/moby         | 45012 | 2           | 7 min      | Add cache │
│  ─ Print: "Reports saved to reports/ (N files)"                    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
                            END
              10 markdown reports saved locally
              No PRs opened (read-only)
```

### 1.4 Resume Flow (interrupted session)

```
User: python main.py --resume <thread_id>
  │
  ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STARTUP                                                             │
│  1. Load config.yaml                                                 │
│  2. Load SQLite checkpointer                                         │
│  3. Fetch state for <thread_id> from checkpoint                      │
│  4. Determine which node was interrupted:                            │
│     ├─ interrupt_for_approval ──▶ re-display trade-off table        │
│     └─ other node ──▶ resume from that node's output                │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  RESUME at interrupt_for_approval                                   │
│  ─ Re-display the same trade-off table with prior state             │
│  ─ Human can view evidence, select, approve — same as fresh run     │
│  ─ Graph continues: generate_yaml → validate → open_pr              │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.5 LLM Call Routing

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LLM Call Decision Tree                         │
│                                                                     │
│  classify_bottlenecks                                               │
│    ├─ OMLX available? ── YES ──▶ OMLX Qwen3.5-9B (local, free)     │
│    └─ NO ──▶ prompt: "OMLX down. Use cloud? (y/n)"                 │
│               ├─ y ──▶ Cloud gpt-4o-mini                            │
│               └─ n ──▶ FAIL (cannot classify without LLM)          │
│                                                                     │
│  propose_optimizations                                              │
│    ├─ OMLX available? ── YES ──▶ OMLX Qwen3.5-9B (local, free)     │
│    └─ NO ──▶ prompt: "OMLX down. Use cloud? (y/n)"                 │
│               ├─ y ──▶ Cloud gpt-4o-mini                            │
│               └─ n ──▶ FAIL (cannot propose without LLM)           │
│                                                                     │
│  generate_yaml                                                      │
│    ├─ Cloud keys configured? ── YES ──▶ Cloud (Claude/gpt-4o-mini) │
│    └─ NO ──▶ prompt: "No cloud keys. Use OMLX local? (y/n)"        │
│               ├─ y ──▶ OMLX Qwen3.5-9B                              │
│               └─ n ──▶ FAIL (cannot generate without LLM)          │
│                                                                     │
│  simulate_savings, validate_syntax, all other nodes                 │
│    └─ No LLM (rule-based / API calls only)                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.6 Logging Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Logging Architecture                        │
│                                                                     │
│  Every agent node execution emits:                                  │
│    {ts, node, duration_ms, tokens, level, message}                 │
│                                                                     │
│  ┌───────────────┐                ┌──────────────────────────────┐ │
│  │  stderr        │                │  logs/run-<timestamp>.jsonl  │ │
│  │  (human)       │                │  (machine, gitignored)       │ │
│  │                │                │                              │ │
│  │  2026-07-03    │                │  {"ts":"2026-07-03T14:22:    │ │
│  │  14:22:01      │                │   01Z","node":"fetch_work    │ │
│  │  INFO          │                │   flows","duration_ms":     │ │
│  │  fetch_work-   │                │   3200,"tokens":0,"level":  │ │
│  │  flows: 5      │                │   "INFO","msg":"5 workflows │ │
│  │  workflows     │                │   fetched"}                  │ │
│  │  fetched       │                │  {"ts":"2026-07-03T14:22:    │ │
│  │  (3.2s)        │                │   04Z","node":"classify",   │ │
│  │                │                │   "duration_ms":8500,       │ │
│  │  14:22:04      │                │   "tokens":1200,"model":    │ │
│  │  INFO          │                │   "omlx:Qwen3.5-9B",        │ │
│  │  classify:     │                │   "level":"INFO","msg":     │ │
│  │  6 bottlenecks │                │   "6 bottlenecks found"}    │ │
│  │  (8.5s, 1200   │                │                              │ │
│  │  tokens)       │                │                              │ │
│  └───────────────┘                └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. LangGraph State Graph

### Graph topology

```
                    ┌────────────────────────────────────────────────────────┐
                    │                  LangGraph State Graph                  │
                    │                                                        │
  START ──────────▶ fetch_workflows                                         │
                    │                                                       │
                    ▼                                                       │
                  fetch_runs ───────────────────────────┐                   │
                    │                                  │                   │
                    ▼                                  │ (field study      │
                  profile_jobs                         │  shortcut)        │
                    │                                  │                   │
                    ▼                                  ▼                   │
              classify_bottlenecks ──────────▶ propose_optimizations       │
                    │                                  │                   │
                    │                                  ▼                   │
                    │                          simulate_savings ◀──┐       │
                    │                                  │           │       │
                    │                                  ▼           │       │
                    │                          interrupt_for_approval       │
                    │                                  │           │       │
                    │                          ┌───────┴───────┐   │       │
                    │                          ▼               ▼   │       │
                    │                     [approve]        [edit]  │       │
                    │                          │               │   │       │
                    │                          │               └───┘       │
                    │                          │                   │       │
                    │                          ▼                   │       │
                    │                    generate_yaml              │       │
                    │                          │                   │       │
                    │                          ▼                   │       │
                    │                    validate_syntax            │       │
                    │                          │                   │       │
                    │                   ┌──────┴──────┐            │       │
                    │                   ▼             ▼            │       │
                    │              [valid]        [invalid]────────┘       │
                    │                   │             (retry gen)         │
                    │                   ▼                                   │
                    │                 open_pr                              │
                    │                   │                                   │
                    ▼                   ▼                                   │
              END ◀─────────────────────────────────────────────────────────┘
```

### Edge conditions

| From | To | Condition |
|---|---|---|
| `fetch_workflows` | `fetch_runs` | always |
| `fetch_runs` | `profile_jobs` | always (optimize mode) |
| `fetch_runs` | `propose_optimizations` | field study mode (skip profile + classify detail, use PR run data directly) |
| `simulate_savings` | `interrupt_for_approval` | always |
| `interrupt_for_approval` | `generate_yaml` | human approves selections |
| `interrupt_for_approval` | `propose_optimizations` | human edits selections + chooses "re-analyze" (re-run LLM with revised state) |
| `interrupt_for_approval` | `simulate_savings` | human edits selections + chooses "recompute" (no LLM cost, just recompute savings) |
| `validate_syntax` | `open_pr` | YAML is valid |
| `validate_syntax` | `generate_yaml` | YAML invalid (retry, max 3 attempts) |

---

## 3. State Schema

```python
from typing import TypedDict, Annotated
from langgraph.graph import MessagesList

class WorkflowFile(TypedDict):
    filename: str
    content: str               # raw YAML
    jobs: list[JobDef]         # parsed job graph

class JobDef(TypedDict):
    name: str
    steps: list[dict]
    needs: list[str]           # dependencies
    runs_on: str
    matrix: dict | None

class RunRecord(TypedDict):
    run_id: int
    status: str                # success, failure, cancelled
    created_at: str
    updated_at: str
    run_started_at: str
    jobs: list[JobRun]

class JobRun(TypedDict):
    name: str
    status: str
    started_at: str
    completed_at: str
    duration_sec: int

class JobProfile(TypedDict):
    job_name: str
    median_sec: int
    p90_sec: int
    p99_sec: int
    failure_rate: float        # 0.0–1.0
    cache_hit_ratio: float | None

class Bottleneck(TypedDict):
    type: str                  # redundant_rebuild, serial_parallel, missing_cache, oversized_context, redundant_matrix
    job_name: str
    evidence: str              # data-backed description
    severity: str              # low, medium, high

class Optimization(TypedDict):
    id: str                    # unique per proposal
    bottleneck_type: str
    job_name: str
    description: str
    estimated_time_saved_min: int
    estimated_cost_per_run: float
    risk_level: str            # low, medium, high
    yaml_diff_hint: str        # what changes in the YAML

class AgentState(TypedDict):
    # input
    repo_url: str
    mode: str                  # "optimize" | "field_study" | "audit"
    field_study_repos: list[str]
    pr_limit: int
    since_days: int

    # fetched data
    workflows: list[WorkflowFile]
    runs: list[RunRecord]
    prs: list[dict]            # field study only
    pr_runs: dict[str, list[RunRecord]]  # field study: pr_number → runs

    # analysis
    profiles: list[JobProfile]
    bottlenecks: list[Bottleneck]
    optimizations: list[Optimization]
    simulated_total_saved_min: int

    # human-in-the-loop
    selected_optimizations: list[str]  # optimization IDs
    human_approved: bool

    # output
    rewritten_yaml: str
    pr_url: str | None
    report_path: str | None    # field study only

    # control
    validation_attempts: int
    token_usage: dict[str, int]  # model → token count
    errors: Annotated[list[str], lambda a, b: a + b]
```

---

## 4. Nodes

### Optimize mode nodes

| Node | Function | Input from state | Output to state | LLM used |
|---|---|---|---|---|
| `fetch_workflows` | `tools/github.py:fetch_workflows(repo)` | `repo_url` | `workflows` | none |
| `fetch_runs` | `tools/github.py:fetch_runs(repo, workflow, limit=50)` | `repo_url`, `workflows` | `runs` | none |
| `profile_jobs` | `profiler.py:profile(runs, workflows)` | `workflows`, `runs` | `profiles` | none |
| `classify_bottlenecks` | `classifier.py:classify(profiles, workflows)` | `profiles`, `workflows` | `bottlenecks` | OMLX Qwen3.5-9B (local) |
| `propose_optimizations` | `optimizer.py:propose(bottlenecks, profiles)` | `bottlenecks`, `profiles` | `optimizations` | OMLX Qwen3.5-9B (local) |
| `simulate_savings` | `optimizer.py:simulate(optimizations)` | `optimizations` | `simulated_total_saved_min` | none (rule-based) |
| `interrupt_for_approval` | `cli.py:trade_off_table(optimizations)` | `optimizations` | `selected_optimizations`, `human_approved` | none |
| `generate_yaml` | `generator.py:rewrite(workflows, selected_optimizations)` | `workflows`, `selected_optimizations` | `rewritten_yaml` | Cloud LLM (Claude/gpt-4o-mini) |
| `validate_syntax` | `validator.py:validate(rewritten_yaml)` | `rewritten_yaml` | `validation_attempts` | none |
| `open_pr` | `tools/github.py:create_pr(repo, branch, content, description)` | `repo_url`, `rewritten_yaml` | `pr_url` | none |

### Field study mode nodes

| Node | Function | Input from state | Output to state | LLM used |
|---|---|---|---|---|
| `fetch_prs` | `tools/github.py:fetch_prs(repos, limit, since)` | `field_study_repos`, `pr_limit`, `since_days` | `prs` | none |
| `fetch_pr_runs` | `tools/github.py:fetch_pr_runs(repo, pr_number)` | `prs` | `pr_runs` | none |
| `profile_jobs` | `profiler.py:profile(pr_runs, workflows)` | `pr_runs`, `workflows` | `profiles` | none |
| `classify_bottlenecks` | `classifier.py:classify(profiles, workflows)` | `profiles`, `workflows` | `bottlenecks` | OMLX Qwen3.5-9B (local) |
| `propose_optimizations` | `optimizer.py:propose(bottlenecks, profiles)` | `bottlenecks`, `profiles` | `optimizations` | OMLX Qwen3.5-9B (local) |
| `save_report` | `reporter.py:save(repo, pr_number, analysis)` | `bottlenecks`, `optimizations` | `report_path` | none |
| `print_summary` | `cli.py:summary_table(reports)` | `report_path` | — | none |

---

## 5. Tools

### `tools/github.py`

```python
class GitHubClient:
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        ...

    # Read
    def fetch_workflows(self, repo: str) -> list[WorkflowFile]:
        """GET /repos/{owner}/{repo}/actions/workflows"""
    
    def fetch_workflow_file(self, repo: str, workflow_id: int) -> str:
        """GET /repos/{owner}/{repo}/actions/workflows/{id}/contents"""
    
    def fetch_runs(self, repo: str, workflow_id: int, limit: int = 50) -> list[RunRecord]:
        """GET /repos/{owner}/{repo}/actions/workflows/{id}/runs?per_page={limit}"""
    
    def fetch_jobs(self, repo: str, run_id: int) -> list[JobRun]:
        """GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs"""
    
    def fetch_prs(self, repos: list[str], limit: int, since_days: int) -> list[dict]:
        """GET /repos/{owner}/{repo}/pulls?state=all&sort=updated&direction=desc"""
    
    def fetch_pr_runs(self, repo: str, pr_number: int) -> list[RunRecord]:
        """GET /repos/{owner}/{repo}/actions/runs?event=pull_request&head_sha={sha}"""
    
    def detect_ci_system(self, repo: str) -> str:
        """Check .github/workflows/ existence. Returns 'github_actions' or 'other'."""
    
    # Write (optimize mode only)
    def create_branch(self, repo: str, branch_name: str) -> str:
        """POST /repos/{owner}/{repo}/git/refs"""
    
    def create_commit(self, repo: str, branch: str, path: str, content: str) -> dict:
        """PUT /repos/{owner}/{repo}/contents/{path}"""
    
    def create_pr(self, repo: str, head: str, title: str, body: str) -> str:
        """POST /repos/{owner}/{repo}/pulls → returns pr_url"""
```

### `profiler.py`

```python
def parse_job_graph(workflow: WorkflowFile) -> list[JobDef]:
    """Parse YAML → list of jobs with dependencies."""

def profile(runs: list[RunRecord], workflows: list[WorkflowFile]) -> list[JobProfile]:
    """Compute median, p90, p99, failure_rate per job across runs."""

def estimate_cache_hit_ratio(run: RunRecord) -> float | None:
    """Parse run logs for cache hit/miss indicators."""
```

### `classifier.py`

```python
def classify(profiles: list[JobProfile], workflows: list[WorkflowFile]) -> list[Bottleneck]:
    """
    Rule-based first pass + LLM hybrid.
    Rules detect:
      - missing_cache: no `cache:` directive in job
      - serial_parallel: jobs with no `needs:` running sequentially
      - redundant_matrix: overlapping matrix dimensions
    LLM (OMLX) classifies:
      - redundant_rebuild: same artifact built in multiple jobs
      - oversized_context: large build context, no .dockerignore
    """
```

### `optimizer.py`

```python
# Hardcoded cost rates
RUNNER_COST_PER_MIN = 0.008        # USD, Linux runner
CACHE_COST_PER_GB_MONTH = 0.007    # USD

def propose(bottlenecks: list[Bottleneck], profiles: list[JobProfile]) -> list[Optimization]:
    """Generate candidate optimizations with estimated savings + cost + risk."""

def simulate(optimizations: list[Optimization]) -> int:
    """Sum estimated time savings across selected optimizations."""
```

### `generator.py`

```python
def rewrite(workflows: list[WorkflowFile], selected: list[str], optimizations: list[Optimization]) -> str:
    """Generate rewritten YAML. Uses cloud LLM (Claude/gpt-4o-mini) for final output."""
```

### `validator.py`

```python
def validate(yaml_content: str) -> tuple[bool, str]:
    """Validate YAML syntax + GitHub Actions schema. Returns (is_valid, error_msg)."""
```

### `cli.py`

```python
def trade_off_table(optimizations: list[Optimization], bottlenecks: list[Bottleneck]) -> tuple[list[str], bool]:
    """
    Interactive CLI with two actions:
      - Type a number to VIEW full evidence for a bottleneck before deciding
      - Type 's' to enter selection mode

    View mode:
      # | Optimization        | Job      | Time Saved | Cost/Run | Risk
      1 | Add cache to build   | build    | 5 min      | $0.02    | Low
      2 | Parallelize lint+test| lint     | 3 min      | $0.00    | Medium

      Enter # to view evidence, or 's' to select: 1

      ── Bottleneck Evidence ──
      Type: missing_cache
      Job: build
      Severity: High
      Evidence: No `cache:` directive found. Build job downloads 2.3GB of
      dependencies on every run. Median build time: 12m 30s. Adding pip cache
      would reduce to ~7m 30s based on similar workflows.

      Enter # to view evidence, or 's' to select: s

    Selection mode:
      Select optimizations to apply (enter numbers, e.g. 1 3 4): 1 4
      Selected: 1 (Add cache to build), 4 (Add .dockerignore)
      Proceed? (y/n): y

    Returns (selected_ids, approved)
    """

def summary_table(reports: list[dict]) -> None:
    """Print field study summary:
      Repo                  | PR #  | Bottlenecks | Min Wasted | Top Recommendation
      kubernetes/kubernetes | 12453 | 4           | 18 min     | Add cache to build
    """

def prompt_re_analyze_or_recompute() -> str:
    """
    After human edits selections during interrupt(), prompt:
      'Re-analyze with your edits, or just recompute savings? (1/2)'
    Returns 'reanalyze' or 'recompute'
    """
```

### `reporter.py`

```python
def save_report(repo: str, pr_number: int, bottlenecks: list[Bottleneck], 
                optimizations: list[Optimization]) -> str:
    """Save to reports/{repo}/{pr_number}-analysis.md. Returns file path."""
```

---

## 6. LangGraph Graph Definition

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("fetch_workflows", fetch_workflows_node)
    graph.add_node("fetch_runs", fetch_runs_node)
    graph.add_node("profile_jobs", profile_jobs_node)
    graph.add_node("classify_bottlenecks", classify_bottlenecks_node)
    graph.add_node("propose_optimizations", propose_optimizations_node)
    graph.add_node("simulate_savings", simulate_savings_node)
    graph.add_node("interrupt_for_approval", interrupt_node)
    graph.add_node("generate_yaml", generate_yaml_node)
    graph.add_node("validate_syntax", validate_syntax_node)
    graph.add_node("open_pr", open_pr_node)

    # Field study nodes
    graph.add_node("fetch_prs", fetch_prs_node)
    graph.add_node("fetch_pr_runs", fetch_pr_runs_node)
    graph.add_node("save_report", save_report_node)
    graph.add_node("print_summary", print_summary_node)

    # Entry: mode-based routing
    graph.set_conditional_entry_point(
        route_entry,
        {
            "optimize": "fetch_workflows",
            "field_study": "fetch_prs",
        }
    )

    # Optimize edges
    graph.add_edge("fetch_workflows", "fetch_runs")
    graph.add_edge("fetch_runs", "profile_jobs")
    graph.add_edge("profile_jobs", "classify_bottlenecks")
    graph.add_edge("classify_bottlenecks", "propose_optimizations")
    graph.add_edge("propose_optimizations", "simulate_savings")
    graph.add_edge("simulate_savings", "interrupt_for_approval")
    graph.add_edge("generate_yaml", "validate_syntax")

    # Conditional: interrupt → approve or edit
    graph.add_conditional_edges(
        "interrupt_for_approval",
        route_after_interrupt,
        {
            "approve": "generate_yaml",
            "reanalyze": "propose_optimizations",   # re-run LLM with edited state
            "recompute": "simulate_savings",        # recompute only, no LLM cost
        }
    )

    # Conditional: validate → open_pr or retry
    graph.add_conditional_edges(
        "validate_syntax",
        route_after_validate,
        {
            "valid": "open_pr",
            "invalid": "generate_yaml",
        }
    )

    graph.add_edge("open_pr", END)

    # Field study edges
    graph.add_edge("fetch_prs", "fetch_pr_runs")
    graph.add_edge("fetch_pr_runs", "profile_jobs")
    graph.add_edge("save_report", "print_summary")
    graph.add_edge("print_summary", END)

    # Field study shortcut: after classify → propose → save_report
    graph.add_conditional_edges(
        "propose_optimizations",
        route_after_propose,
        {
            "optimize": "simulate_savings",
            "field_study": "save_report",
        }
    )

    # SQLite checkpointer
    checkpointer = SqliteSaver.from_conn_string("checkpoints/agent.db")
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["interrupt_for_approval"]
    )

def route_entry(state: AgentState) -> str:
    return state["mode"]

def route_after_interrupt(state: AgentState) -> str:
    if state["human_approved"]:
        return "approve"
    choice = state.get("cycle_choice", "recompute")  # set by prompt_re_analyze_or_recompute()
    return choice  # "reanalyze" or "recompute"

def route_after_validate(state: AgentState) -> str:
    if state["validation_attempts"] >= 3:
        raise RuntimeError("YAML validation failed after 3 attempts")
    return "valid" if state["rewritten_yaml_valid"] else "invalid"

def route_after_propose(state: AgentState) -> str:
    return state["mode"]
```

---

## 7. File Structure

```
cicd-bottleneck-optimizer/
├── main.py                      # CLI entry point + arg parsing
├── graph.py                     # LangGraph graph definition
├── state.py                     # AgentState TypedDict + models
├── config.yaml.example          # Template for config (gitignored: config.yaml)
├── requirements.txt
├── Dockerfile
├── .gitignore
├── LICENSE
├── README.md
├── docs/
│   ├── PRD.md
│   └── SPEC.md                  # this file
├── tools/
│   ├── __init__.py
│   └── github.py                # GitHubClient — REST API wrapper
├── nodes/
│   ├── __init__.py
│   ├── fetch.py                 # fetch_workflows, fetch_runs, fetch_prs, fetch_pr_runs
│   ├── profile.py               # profile_jobs node
│   ├── classify.py              # classify_bottlenecks node
│   ├── optimize.py              # propose_optimizations, simulate_savings nodes
│   ├── generate.py              # generate_yaml, validate_syntax nodes
│   └── pr.py                    # open_pr, save_report nodes
├── lib/
│   ├── __init__.py
│   ├── profiler.py              # profiling logic (median, p90, cache hit)
│   ├── classifier.py            # bottleneck classification (rules + LLM)
│   ├── optimizer.py             # optimization proposals + cost calc
│   ├── generator.py             # YAML rewriting
│   ├── validator.py             # YAML + schema validation
│   ├── reporter.py              # field study report generation
│   └── cli.py                   # CLI table display + stdin prompts
├── llm/
│   ├── __init__.py
│   └── client.py                # OMLX + cloud LLM client wrapper
├── checkpoints/                 # gitignored — SQLite checkpointer
│   └── agent.db
└── reports/                     # gitignored — field study reports
    └── kubernetes-kubernetes/
        └── 12453-analysis.md
```

---

## 8. LLM Configuration

```yaml
# config.yaml (gitignored)
github:
  token: "ghp_xxx"              # read-only for field study, full repo scope for optimize

local_llm:
  provider: "openai-compatible"
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "omlx-test"
  model: "Qwen3.5-9B-MLX-4bit"

cloud_llm:
  # Optional — only used for final YAML generation
  openai:
    api_key: "sk-xxx"
    model: "gpt-4o-mini"
  anthropic:
    api_key: "sk-ant-xxx"
    model: "claude-3-5-sonnet-20241022"

cost_rates:
  runner_per_min: 0.008
  cache_per_gb_month: 0.007

defaults:
  workflow_limit: 5             # top N workflows by run frequency
  runs_per_workflow: 50
  validation_max_attempts: 3
```

### LLM call routing

| Node | LLM | Fallback |
|---|---|---|
| `classify_bottlenecks` | OMLX Qwen3.5-9B (local) | prompt user: "OMLX unavailable. Use cloud LLM? (y/n)" |
| `propose_optimizations` | OMLX Qwen3.5-9B (local) | prompt user: "OMLX unavailable. Use cloud LLM? (y/n)" |
| `generate_yaml` | Cloud (Claude or gpt-4o-mini) | prompt user: "No cloud LLM keys. Use OMLX local? (y/n)" |
| all other nodes | none | — |

### Validation

`validate_syntax` uses `act --list` to dry-run the generated workflow. This is the most accurate validation — `act` parses the workflow exactly as GitHub Actions would. Requires `act` installed locally.

- If `act` is not installed, fall back to PyYAML syntax check + custom schema check (fields: `on`, `jobs`, `steps`) and log a warning that `act` is not available.
- On validation failure, retry `generate_yaml` up to 3 times. After 3 failures, stop with error — human must re-run or adjust.

### Branch naming

Branches created by the agent in optimize mode use a descriptive convention:

```
ci-optimizer/<optimization-slug>-<pr-or-run-id>
```

Examples:
- `ci-optimizer/add-cache-build-12453`
- `ci-optimizer/parallelize-lint-test-12467`
- `ci-optimizer/reduce-matrix-test-12489`

The slug is derived from the primary optimization's description, kebab-cased, truncated to 40 chars.

### PR body format

Structured markdown with sections:

```markdown
## CI/CD Optimization — Automated Proposal

### Summary
{one-line summary of what was optimized}

### Bottlenecks Found
| # | Type | Job | Severity | Evidence |
|---|---|---|---|---|
| 1 | missing_cache | build | High | No cache: directive; rebuild downloads 2.3GB |
| 2 | serial_parallel | lint | Medium | lint + test sequential; no needs: dependency |

### Optimizations Applied
| # | Optimization | Time Saved | Cost/Run | Risk |
|---|---|---|---|---|
| 1 | Add cache to build | 5 min | $0.02 | Low |
| 2 | Add .dockerignore | 2 min | $0.00 | Low |

### Before/After
| Job | Before (median) | After (est.) | Saved |
|---|---|---|---|
| build | 12m 30s | 7m 30s | 5m |
| docker | 4m 00s | 2m 00s | 2m |
| **Total** | **16m 30s** | **9m 30s** | **7m** |

### Trade-offs
- Cache cost: $0.02/run (~$15/month at 750 runs/month)
- Risk: Low — mechanical optimization, no build semantics changed

### Validation
- ✅ YAML syntax valid
- ✅ `act --list` dry-run passed

---
Generated by [cicd-bottleneck-optimizer](https://github.com/deghosal-2026/cicd-bottleneck-optimizer)
```

### Logging

The agent logs in two formats simultaneously:

| Output | Format | Destination |
|---|---|---|
| Human-readable | `logging` module, plain text | stderr (console) |
| Machine-readable | JSON lines (`{"ts": "...", "node": "...", "duration_ms": ..., "tokens": ..., "level": "..."}`) | `logs/run-<timestamp>.jsonl` |

Each log entry includes: timestamp, node name, duration in ms, token count (if LLM call), and level (INFO/WARN/ERROR).

### Config validation

`config.yaml` is validated on startup before the graph runs. Checks:

| Check | Behavior on failure |
|---|---|
| `github.token` present | Fail: "GitHub token not set in config.yaml" |
| `github.token` has required scope | Fail: "Token lacks 'repo' scope (required for optimize mode)" or warn for field study ("read-only token OK") |
| `local_llm.base_url` reachable | Warn: "OMLX not reachable at {url} — will prompt for cloud fallback at runtime" |
| `cloud_llm` keys present | Warn: "No cloud LLM keys configured — generation will use OMLX local" |
| `cost_rates` present | Fail: "cost_rates not set in config.yaml" |
| `act` installed | Warn: "act not found — validation will use PyYAML fallback" |

### API call strategy

All GitHub API calls are **sequential**. Rationale: avoids rate limit spikes, simpler error handling, no async complexity for v1. Parallelization deferred to v2 if performance is a problem.

---

## 9. Field Study Repos

Repos identified for the 10-PR field study (CUJ-5). All are very active, use GitHub Actions for at least some CI, and have 30–120 min pipeline durations.

| Repo | PRs/month | CI system | Why selected |
|---|---|---|---|
| `kubernetes/kubernetes` | 200+ | GitHub Actions + prow | Largest K8s repo; mixed CI; called out in PRD problem statement |
| `tensorflow/tensorflow` | 150+ | GitHub Actions | Large ML framework; long build times; matrix-heavy |
| `moby/moby` | 50+ | GitHub Actions | Docker engine; complex build pipeline; cited in PRD |

**Selection criteria:** PRs opened or merged in the last 30 days, with at least 1 CI run triggered. Agent detects GitHub Actions workflows and skips repos using only prow/Jenkins with a warning log.

**Report output:**
```
reports/
├── kubernetes-kubernetes/
│   ├── 12453-analysis.md
│   ├── 12467-analysis.md
│   ├── 12489-analysis.md
│   └── 12501-analysis.md
├── tensorflow-tensorflow/
│   ├── 62341-analysis.md
│   ├── 62355-analysis.md
│   └── 62378-analysis.md
└── moby-moby/
    ├── 45012-analysis.md
    ├── 45034-analysis.md
    └── 45056-analysis.md
```

### Report format (`reports/<repo>/<pr#>-analysis.md`)

```markdown
# CI/CD Bottleneck Analysis — kubernetes/kubernetes PR #12453

**PR:** [#12453](https://github.com/kubernetes/kubernetes/pull/12453)
**Analyzed:** 2026-07-03
**CI runs analyzed:** 3

## Job Profiles

| Job | Median | P90 | Failure Rate |
|---|---|---|---|
| build | 12m 30s | 18m 10s | 5% |
| test | 8m 15s | 11m 40s | 2% |
| lint | 1m 20s | 2m 05s | 0% |

## Bottlenecks Found

| # | Type | Job | Severity | Evidence |
|---|---|---|---|---|
| 1 | missing_cache | build | High | No cache: directive; rebuild downloads 2.3GB each run |
| 2 | serial_parallel | lint | Medium | lint + test run sequentially; no `needs:` dependency |

## Recommendations

| # | Optimization | Time Saved | Cost/Run | Risk |
|---|---|---|---|---|
| 1 | Add `cache: pip` to build job | 5 min | $0.02 | Low |
| 2 | Parallelize lint + test | 1.5 min | $0.00 | Low |

## Summary

- **Total estimated time wasted:** 6.5 min per run
- **Top recommendation:** Add cache to build job (5 min saved, $0.02/run)
```

---

## 10. CLI Interface

### Optimize mode

```bash
$ python main.py --repo owner/repo --optimize

Fetching workflows for owner/repo...
  Found 5 workflows (top 5 by run frequency)

Fetching runs (50 per workflow)...
  250 runs fetched across 5 workflows

Profiling jobs...
  15 jobs profiled

Classifying bottlenecks...
  6 bottlenecks found

Proposing optimizations...

  # | Optimization              | Job      | Time Saved | Cost/Run | Risk
  1 | Add cache to build        | build    | 5 min      | $0.02    | Low
  2 | Parallelize lint + test   | lint     | 3 min      | $0.00    | Medium
  3 | Reduce matrix dimensions  | test     | 8 min      | $0.00    | High
  4 | Add .dockerignore         | docker   | 2 min      | $0.00    | Low
  5 | Split monolithic job      | build    | 10 min     | $0.01    | High

  Estimated total savings: 28 min/run

  Select optimizations to apply (enter numbers, e.g. 1 3 4): 1 4

  Selected: 1 (Add cache to build), 4 (Add .dockerignore)
  Estimated savings: 7 min/run, cost: $0.02/run
  Proceed? (y/n): y

Generating rewritten YAML...
Validating syntax... ✓ valid

Opening PR on owner/repo...
  PR created: https://github.com/owner/repo/pull/123
```

### Field study mode

```bash
$ python main.py --field-study \
    --repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby \
    --pr-limit 10 \
    --since 30d

Fetching PRs (last 30 days, 10 total)...
  kubernetes/kubernetes: 4 PRs
  tensorflow/tensorflow: 3 PRs
  moby/moby: 3 PRs

Analyzing CI runs per PR...

  Repo                  | PR #  | Bottlenecks | Min Wasted | Top Recommendation
  kubernetes/kubernetes | 12453 | 4           | 18 min     | Add cache to build
  kubernetes/kubernetes | 12467 | 2           | 6 min      | Parallelize lint+test
  kubernetes/kubernetes | 12489 | 3           | 12 min     | Reduce matrix
  kubernetes/kubernetes | 12501 | 1           | 3 min      | Add .dockerignore
  tensorflow/tensorflow | 62341 | 5           | 22 min     | Split monolithic job
  tensorflow/tensorflow | 62355 | 2           | 5 min      | Add cache
  tensorflow/tensorflow | 62378 | 3           | 9 min      | Parallelize
  moby/moby             | 45012 | 2           | 7 min      | Add cache
  moby/moby             | 45034 | 1           | 2 min      | Reduce context
  moby/moby             | 45056 | 3           | 11 min     | Split job

  Reports saved to reports/ (10 files)
```

---

## 11. Error Handling

| Scenario | Behavior |
|---|---|
| GitHub API rate limit (403) | Retry with exponential backoff: 1s, 2s, 4s, 8s (max 4 retries) |
| GitHub API 404 (repo/workflow not found) | Log error, skip workflow, continue with others |
| No GitHub Actions workflows found | Log warning: "Repo uses non-Actions CI, skipping" |
| LLM returns invalid YAML | Retry generation (max 3 attempts). After 3, stop with error — human re-runs or adjusts. |
| LLM unavailable (OMLX down) | Prompt user: "OMLX unavailable. Use cloud LLM? (y/n)". If no cloud keys, fail with message. |
| `act` not installed | Fall back to PyYAML syntax check + custom schema. Log warning. |
| No write access to target repo (optimize mode) | Pre-flight check fails with: "Token lacks push permission on {repo}" |
| SQLite checkpoint DB locked | Log warning, continue without checkpointing for this run |
| Config validation fails on startup | Fail fast with clear message before graph runs |

---

## 12. Dependencies

```
# requirements.txt
langgraph>=0.2.0
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-anthropic>=0.2.0
openai>=1.0
PyYAML>=6.0
requests>=2.31
rich>=13.0          # for CLI table formatting
```

---

## 13. Testing Strategy

| Level | Scope | Tool |
|---|---|---|
| Unit | profiler, classifier rules, optimizer cost calc, validator, reporter, cli | pytest |
| Integration | GitHubClient with mocked API responses | pytest + responses |
| Graph | LangGraph state transitions, interrupt flow, cycle termination, resume | pytest + LangGraph test utils |
| Field study | Run against real repos (read-only), verify report output | manual |
| Real-life repo | Live API calls against the 3 field study repos | pytest (marked `@pytest.mark.live`, skipped in CI) |

### Unit test cases

**`test_profiler.py`**
- median/p90/p99 computation from mock run data
- failure_rate calculation (0% and 100% edge cases)
- cache_hit_ratio parsing from mock logs
- job dependency graph parsing from mock workflow YAML
- empty runs list returns empty profiles
- single run returns that run's duration as median

**`test_classifier.py`**
- missing_cache detected when no `cache:` directive
- missing_cache not flagged when cache present
- serial_parallel detected when jobs have no `needs:` and run sequentially
- redundant_matrix detected with overlapping dimensions
- redundant_rebuild detected (LLM-mocked) when same artifact in multiple jobs
- oversized_context detected (LLM-mocked) when no `.dockerignore`
- severity assignment: high/medium/low based on time wasted
- rule-based pass runs without LLM
- LLM pass falls back to cloud when OMLX unavailable (mocked)
- empty profiles returns empty bottlenecks

**`test_optimizer.py`**
- cost estimate matches hardcoded rates ($0.008/min runner)
- cache cost calculation ($0.007/GB-month)
- risk level assignment: low/medium/high
- time savings estimation per optimization type
- simulate_savings sums correctly across optimizations
- empty bottlenecks returns empty optimizations

**`test_validator.py`**
- valid GitHub Actions YAML passes
- invalid YAML syntax fails with error message
- missing required field (`on:`, `jobs:`) fails
- `act --list` validation passes valid workflow
- `act --list` validation fails invalid workflow
- fallback to PyYAML when `act` not installed (mocked)
- validation_attempts counter increments on retry

**`test_reporter.py`**
- report file created at `reports/<repo>/<pr#>-analysis.md`
- report contains job profiles table
- report contains bottlenecks table
- report contains recommendations table
- report contains summary with total wasted time
- repo name with slash converted to dash in path

**`test_cli.py`**
- trade_off_table displays numbered list
- view evidence mode shows bottleneck details
- selection mode accepts numbered input
- proceed prompt accepts y/n
- prompt_re_analyze_or_recompute returns "reanalyze" or "recompute"
- summary_table prints formatted table
- invalid input handling (non-numeric, out of range)

### Integration test cases

**`test_github_client.py`** (mocked API responses)
- fetch_workflows returns parsed workflow list
- fetch_workflows handles 404 (repo not found)
- fetch_runs paginates correctly (2 pages of 30)
- fetch_runs handles empty runs
- fetch_jobs returns per-job timing
- fetch_prs filters by since_days
- fetch_pr_runs maps PR to CI runs
- detect_ci_system returns "github_actions" when workflows exist
- detect_ci_system returns "other" when no workflows
- create_branch + create_commit + create_pr sequence
- rate limit 403 triggers exponential backoff retry
- rate limit 403 after 4 retries raises error
- token scope check: read-only token detected for field study
- token scope check: full token detected for optimize mode

### Graph test cases

**`test_graph_optimize.py`**
- full optimize path: fetch → profile → classify → propose → simulate → interrupt → approve → generate → validate → open_pr
- interrupt → edit → reanalyze cycle (loops back to propose_optimizations)
- interrupt → edit → recompute cycle (loops back to simulate_savings)
- validation retry: generate → validate (invalid) → generate → validate (valid)
- validation fails 3 times → graph stops with error
- pre-flight write access check fails → graph stops before fetching
- field study mode routes to fetch_prs instead of fetch_workflows
- field study routes to save_report instead of interrupt
- field study + --review flag shows trade-off table then saves report

**`test_graph_resume.py`**
- resume from interrupt_for_approval re-displays trade-off table
- resume preserves prior state (workflows, profiles, bottlenecks)
- resume with invalid thread_id fails with clear message
- checkpoint written after each node completes
- SQLite DB locked → continues without checkpointing (warned)

**`test_graph_llm.py`**
- OMLX available → classify uses local LLM
- OMLX down → prompt for cloud → y → uses cloud LLM
- OMLX down → prompt for cloud → n → fails gracefully
- generate_yaml uses cloud when keys configured
- generate_yaml prompts for OMLX when no cloud keys
- token_usage tracked per model across all LLM calls

### Real-life repo test cases

**`test_live_repos.py`** (`@pytest.mark.live` — requires GITHUB_TOKEN + network)

These tests make real API calls against the 3 field study repos. Skipped by default (`pytest -m live` to run).

**kubernetes/kubernetes:**
- fetch_workflows returns ≥ 1 workflow
- detect_ci_system returns "github_actions" (some workflows use Actions)
- detect_ci_system logs warning for prow-based workflows
- fetch_runs returns runs with timing data
- profile_jobs computes median/p90 for at least 1 job
- classify_bottlenecks finds ≥ 1 bottleneck in workflows with no cache
- field study: fetch_prs returns ≥ 1 PR updated in last 30 days
- field study: fetch_pr_runs returns ≥ 1 CI run per PR
- field study: save_report creates markdown file with correct path
- field study: report contains real job timings (not empty)

**tensorflow/tensorflow:**
- fetch_workflows returns ≥ 1 workflow
- profile_jobs: matrix-heavy workflows show high p90 variance
- classify_bottlenecks: redundant_matrix detected in matrix-heavy workflows
- field study: 3 PRs fetched, reports generated

**moby/moby:**
- fetch_workflows returns ≥ 1 workflow
- classify_bottlenecks: oversized_context detected if no .dockerignore
- field study: 3 PRs fetched, reports generated
- field study: summary table prints with correct repo names

**Cross-repo field study:**
- `--repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby --pr-limit 10 --since 30d`
- 10 reports generated across 3 repos
- summary table shows all 3 repos with correct PR counts
- each report file is valid markdown with all sections
- no PRs opened on any repo (read-only verification)
- total API calls < 500 (rate limit safe)

### Config validation test cases

**`test_config.py`**
- valid config loads successfully
- missing github.token → fail with message
- missing cost_rates → fail with message
- OMLX unreachable → warn (not fail)
- no cloud LLM keys → warn (not fail)
- `act` not installed → warn (not fail)
- read-only token accepted for field study mode
- full token required for optimize mode
