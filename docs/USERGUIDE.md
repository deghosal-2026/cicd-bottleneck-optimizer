# User Guide — CI/CD Bottleneck Optimizer

## Architecture

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

### LangGraph State Graph

```
                    ┌────────────────────────────────────────────────────────┐
                    │                  LangGraph State Graph                  │
                    │                                                        │
  START ──────────▶ fetch_workflows                                         │
                    │                                                       │
                    ▼                                                       │
                  fetch_runs                                                │
                    │                                                       │
                    ▼                                                       │
                  profile_jobs                                              │
                    │                                                       │
                    ▼                                                       │
              classify_bottlenecks                                          │
                    │                                                       │
                    ▼                                                       │
              propose_optimizations                                         │
                    │                                                       │
                    ▼                                                       │
              simulate_savings ─────────────────────────────────────┐       │
                    │                                               │       │
                    ▼                                               │       │
              interrupt_for_approval                                │       │
                    │                                               │       │
              ┌─────┴──────┐                                        │       │
              ▼            ▼                                        │       │
         [approve]     [edit]                                       │       │
              │            │                                        │       │
              │            └──────────── reanalyze ──┐              │       │
              │                      or               │              │       │
              │                    recompute ─────────┴──────────────┘       │
              ▼                                                             │
          generate_yaml                                                     │
              │                                                             │
              ▼                                                             │
          validate_syntax                                                   │
              │                                                             │
         ┌────┴────┐                                                       │
         ▼         ▼                                                       │
    [valid]   [invalid] ──── retry gen (max 3) ────────────────────────────┘
         │
         ▼
       open_pr
         │
         ▼
       END — PR opened on target repo
```

### LLM Call Routing

```
                    LLM Call Decision Tree

  classify_bottlenecks
    ├─ OMLX available? ── YES ──▶ OMLX Qwen3.5-9B (local, free)
    └─ NO ──▶ prompt: "OMLX down. Use cloud? (y/n)"
               ├─ y ──▶ Cloud gpt-4o-mini
               └─ n ──▶ FAIL (cannot classify without LLM)

  propose_optimizations
    ├─ OMLX available? ── YES ──▶ OMLX Qwen3.5-9B (local, free)
    └─ NO ──▶ prompt: "OMLX down. Use cloud? (y/n)"
               ├─ y ──▶ Cloud gpt-4o-mini
               └─ n ──▶ FAIL (cannot propose without LLM)

  generate_yaml
    ├─ Cloud keys configured? ── YES ──▶ Cloud (Claude/gpt-4o-mini)
    └─ NO ──▶ prompt: "No cloud keys. Use OMLX local? (y/n)"
               ├─ y ──▶ OMLX Qwen3.5-9B
               └─ n ──▶ FAIL (cannot generate without LLM)

  simulate_savings, validate_syntax, all other nodes
    └─ No LLM (rule-based / API calls only)
```

### Optimize Mode Flow

```
User: python main.py --repo owner/repo --optimize
  │
  ▼
STARTUP
  1. Load + validate config.yaml (token, LLM, cost_rates)
  2. Pre-flight: verify write access to target repo
     ├─ has push permission? ── NO ──▶ FAIL: "use --field-study"
     └─ YES ── continue
  3. Check act installed (warn if not)
  4. Check OMLX reachable (warn if not)
  5. Load or create SQLite checkpointer
  │
  ▼
fetch_workflows
  ─ GET /repos/{owner}/{repo}/actions/workflows
  ─ GET /repos/{owner}/{repo}/contents/.github/workflows/{file}
  ─ Detect CI system (skip if non-Actions, log warning)
  ─ Sort by run frequency, take top N (default 5)
  ─ Output: workflows[] (YAML + parsed job graph)
  │
  ▼
fetch_runs
  ─ For each workflow: GET .../runs?per_page=50
  ─ For each run: GET .../runs/{run_id}/jobs
  ─ Sequential calls, retry on 403 (exponential backoff)
  ─ Output: runs[] (job timings, statuses, durations)
  │
  ▼
profile_jobs
  ─ Parse workflow YAML → job dependency graph
  ─ For each job across runs:
    compute median_sec, p90_sec, p99_sec
    compute failure_rate
    estimate cache_hit_ratio
  ─ Output: profiles[]
  │
  ▼
classify_bottlenecks
  ─ RULE-BASED PASS: missing_cache, serial_parallel, redundant_matrix
  ─ LLM PASS (OMLX): redundant_rebuild, oversized_context
  ─ If OMLX down → prompt: "Use cloud LLM? (y/n)"
  ─ Output: bottlenecks[] (type, job, evidence, severity)
  │
  ▼
propose_optimizations
  ─ LLM (OMLX) generates candidates per bottleneck
  ─ Each: description, estimated_time_saved_min, estimated_cost, risk, yaml_diff_hint
  ─ Output: optimizations[]
  │
  ▼
simulate_savings
  ─ Sum estimated time savings across all proposed optimizations
  ─ Output: simulated_total_saved_min
  │
  ▼
interrupt_for_approval  ◀── CHECKPOINT PERSISTED
  │
  CLI displays trade-off table:
    # | Optimization     | Job   | Saved | Cost  | Risk
    1 | Add cache        | build | 5 min | $0.02 | Low
    2 | Parallelize     | lint  | 3 min | $0.00 | Medium
    3 | Reduce matrix   | test  | 8 min | $0.00 | High
  │
  Two actions:
    • Enter # to VIEW evidence for a bottleneck
    • Type 's' to enter SELECTION mode
      ──▶ "Select optimizations (e.g. 1 3): "
      ──▶ "Proceed? (y/n): "
  │
  ┌─ APPROVE (y) ──▶ generate_yaml
  │
  └─ EDIT (n) ──▶ "Re-analyze with edits, or just recompute? (1/2)"
                    ├─ 1 reanalyze ──▶ propose_optimizations
                    └─ 2 recompute ──▶ simulate_savings
  │
  ▼
generate_yaml
  ─ Cloud LLM (Claude/gpt-4o-mini) generates rewritten YAML
  ─ If no cloud keys → prompt: "Use OMLX local? (y/n)"
  ─ Output: rewritten_yaml
  │
  ▼
validate_syntax
  ─ Primary: act --list dry-run
  ─ Fallback: PyYAML + custom schema
  ─ If invalid: retry generate_yaml (max 3)
  ─ After 3 failures: STOP with error
  │
  ▼
open_pr
  ─ Create branch: ci-optimizer/<slug>-<id>
  ─ Commit rewritten YAML to branch
  ─ Open PR with structured markdown body
  ─ Output: pr_url
  │
  ▼
END — PR opened on target repo
```

### Field Study Mode Flow

```
User: python main.py --field-study \
    --repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby \
    --pr-limit 10 --since 30d [--review]
  │
  ▼
STARTUP
  1. Load + validate config.yaml (read-only token OK)
  2. No write access check needed (read-only mode)
  3. Check OMLX reachable (warn if not)
  4. Load or create SQLite checkpointer
  │
  ▼
fetch_prs
  ─ For each repo in --repos list:
    GET /repos/{owner}/{repo}/pulls?state=all&sort=updated&direction=desc
  ─ Filter: PRs updated within --since days
  ─ Detect CI system per repo (skip non-Actions with warning)
  ─ Output: prs[] (PR number, title, head_sha, updated_at)
  │
  ▼
fetch_pr_runs
  ─ For each PR:
    GET .../actions/runs?event=pull_request&head_sha={sha}
  ─ For each run: GET .../jobs
  ─ Also fetch .github/workflows/*.yml per repo
  ─ Sequential calls, retry on 403
  ─ Output: pr_runs{pr_number: [RunRecord]}
  │
  ▼
profile_jobs
  ─ Same as optimize mode: median, p90, failure_rate per job
  ─ Profiled per PR's CI runs (not per workflow)
  ─ Output: profiles[]
  │
  ▼
classify_bottlenecks
  ─ Same as optimize mode: rules + OMLX LLM hybrid
  ─ Output: bottlenecks[]
  │
  ▼
propose_optimizations
  ─ Same as optimize mode: LLM generates candidates
  ─ Output: optimizations[]
  │
  ▼
        ┌────────────┴────────────┐
        │                         │
  --review flag?          no --review
        │                         │
        ▼                         ▼
  show trade_off_table    save_report
  (read-only, no PR)      ─ Write reports/<repo>/<pr#>-analysis.md
  Enter # to view evidence ─ Markdown: profiles, bottlenecks, recs, summary
  Type 'q' for next PR     ─ Output: report_path
        │                         │
        └──────────┬──────────────┘
                   ▼
  print_summary
  ─ Print summary table: Repo | PR # | Bottlenecks | Min Wasted | Top Rec
  ─ Print: "Reports saved to reports/ (N files)"
  │
  ▼
  END — 10 markdown reports saved locally
       No PRs opened (read-only)
```

### Logging Architecture

```
Every agent node execution emits: {ts, node, duration_ms, tokens, level, message}

stderr (human-readable)         logs/run-<timestamp>.jsonl (machine)

2026-07-03 14:22:01 INFO        {"ts":"2026-07-03T14:22:01Z","node":"fetch_workflows",
  fetch_workflows: 5 workflows   "duration_ms":3200,"tokens":0,"level":"INFO",
  fetched (3.2s)                 "msg":"5 workflows fetched"}

2026-07-03 14:22:04 INFO        {"ts":"2026-07-03T14:22:04Z","node":"classify",
  classify: 6 bottlenecks        "duration_ms":8500,"tokens":1200,"model":"omlx:Qwen3.5-9B",
  (8.5s, 1200 tokens)            "level":"INFO","msg":"6 bottlenecks found"}
```

---

## Customer User Journeys (CUJ)

### CUJ-1: Optimize a Slow Pipeline

**Command:** `python main.py --repo owner/repo --optimize`

**Actor:** DevOps engineer  
**Goal:** Reduce pipeline runtime by identifying bottlenecks and opening a PR with optimized YAML.

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1 | DevOps engineer | `python main.py --repo owner/repo --optimize` | CLI starts |
| 2 | Agent | Startup: validates config.yaml (GitHub token, cost rates, LLM keys), checks OMLX reachable, verifies write access to target repo, checks `act` installed | Warnings printed if optional deps missing |
| 3 | Agent | Fetches all `.github/workflows/*.yml` files via GitHub REST API. Sorts by run frequency, keeps top N (default 5). Detects CI system — skips non-Actions repos (prow/Jenkins) with warning. | `workflows[]` — YAML content + parsed job graph |
| 4 | Agent | Fetches last 50 runs per workflow with per-job timing via Jobs API. Sequential calls, exponential backoff on 403 rate limits. | `runs[]` — job timings, statuses, durations |
| 5 | Agent | Profiles each job: median, p90, p99 duration, failure rate, cache hit ratio from logs. | `profiles[]` — per-job timing stats |
| 6 | Agent | Classifies bottlenecks: rule-based pass (missing cache, serial-where-parallel, redundant matrix) + LLM pass via OMLX Qwen3.5-9B (redundant rebuilds, oversized context). OMLX down → prompt for cloud fallback. | `bottlenecks[]` — type, job, evidence, severity |
| 7 | Agent | Proposes optimizations with quantified estimates per bottleneck. Each includes: description, time saved (min), cost/run ($0.008/min runner, $0.007/GB-month cache), risk level, YAML diff hint. | `optimizations[]` — candidate fixes |
| 8 | Agent | Simulates total savings across all proposed optimizations. | `simulated_total_saved_min` |
| 9 | Agent | `interrupt()` — presents trade-off table in CLI with numbered list. Human types numbers to view evidence, then selects/deselects optimizations. State checkpointed to SQLite. | `selected_optimizations[]`, `human_approved` |
| 10 | Human | Edits which optimizations to apply (rejects costly cache, accepts parallelism). Can re-analyze or just recompute savings. | Revised selections |
| 11 | Agent | Cloud LLM (Claude/gpt-4o-mini) generates rewritten workflow YAML with selected optimizations. No cloud keys → prompt for OMLX fallback. | `rewritten_yaml` |
| 12 | Agent | Validates YAML syntax via `act --list` (primary) or PyYAML + schema (fallback). Retries generation up to 3 times on failure. | `validation_attempts`, valid YAML |
| 13 | Agent | Opens PR on target repo: creates branch `ci-optimizer/<slug>-<id>`, commits rewritten YAML, writes structured PR body with before/after estimates + trade-off rationale. | `pr_url` |
| 14 | Human | Reviews PR, merges or requests changes. | Merged PR |

**Input:** `--repo owner/repo`, valid `config.yaml` with write-access GitHub token  
**Output:** PR opened on target repo with optimized workflow  

---

### CUJ-2: Audit a Public Repo for Learning (Read-Only)

**Command:** `python main.py --repo kubernetes/kubernetes --audit`

**Actor:** Engineer learning CI  
**Goal:** Study how large repos structure their CI and identify anti-patterns.

| Step | Actor | Action |
|------|-------|--------|
| 1 | Engineer | `python main.py --repo kubernetes/kubernetes --audit` |
| 2 | Agent | Fetches workflows + profiles + classifies (same pipeline as optimize mode) |
| 3 | Agent | Prints a report of what the repo does well/poorly to CLI |
| 4 | Engineer | Reviews findings; decides which patterns to adopt in own repos |

**Input:** `--repo owner/repo` (read-only GitHub token OK)  
**Output:** CLI report — no branches, commits, or PRs created  

---

### CUJ-3: Field Study — Analyze PRs Across Multiple Repos (Read-Only)

**Command:** `python main.py --field-study --repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby --pr-limit 10 --since 30d`

**Actor:** DevOps engineer  
**Goal:** Analyze real CI bottlenecks across 10 PRs from 3 active public repos, save reports locally.

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1 | DevOps engineer | `python main.py --field-study --repos a,b,c --pr-limit 10 --since 30d` | CLI starts |
| 2 | Agent | Startup: validates config (read-only token OK, no write check). Checks OMLX reachable (warn if not). | Config loaded |
| 3 | Agent | For each repo: fetches last N PRs in the last 30 days via GitHub API. Detects CI system per repo — skips non-Actions repos with warning. | `prs[]` — PR number, title, head_sha, updated_at |
| 4 | Agent | For each PR: fetches CI runs for that head SHA via Actions API. Also fetches `.github/workflows/*.yml` per repo. Sequential calls with backoff. | `pr_runs{pr_number: [RunRecord]}` |
| 5 | Agent | Profiles per-job timing per PR: median, p90, failure rate. | `profiles[]` |
| 6 | Agent | Classifies bottlenecks per PR (same hybrid rule + LLM approach as optimize). | `bottlenecks[]` |
| 7 | Agent | Proposes optimizations per PR with quantified estimates. | `optimizations[]` |
| 8 | Agent | If `--review` flag: shows trade-off table interactively per PR (view evidence, 'q' for next). | Human inspects |
| 9 | Agent | Saves report locally: `reports/<repo>/<pr-number>-analysis.md` with job profiles, bottlenecks, recommendations, summary. | `report_path` |
| 10 | Agent | Prints summary table: repo, PR #, bottlenecks, min wasted, top recommendation. | CLI summary |

**Example output:**
```
Repo                  | PR #  | Bottlenecks | Min Wasted | Top Rec
kubernetes/kubernetes | 12453 | 4           | 18 min     | Add cache
tensorflow/tensorflow | 62341 | 5           | 22 min     | Split job
moby/moby             | 45012 | 2           | 7 min      | Add cache
Reports saved to reports/ (10 files)
```

**Input:** `--field-study`, `--repos` (comma-separated), read-only GitHub token OK  
**Output:** 10 markdown reports in `reports/` — no PRs opened  

**Key constraints:**
- Read-only — no write access needed, works with `public_repo` scope or unauthenticated
- No PRs opened — recommendations are local markdown files only
- Real data — analyzes actual PR CI runs from kubernetes/kubernetes, tensorflow/tensorflow, moby/moby
- Last 30 days only

---

### CUJ-4: PR Review of Optimized Workflow

**Command:** N/A (incoming PR notification)

**Actor:** Reviewer (team member)  
**Goal:** Review agent-proposed optimizations and merge or request changes.

The reviewer receives a GitHub PR notification. The PR body contains:

- **Summary** — which workflow was optimized and why
- **Bottlenecks Found** — table of each bottleneck with type, job, evidence, severity
- **Optimizations Applied** — table of selected optimizations with time saved, cost, risk
- **Before/After** — median times per job before and after
- **Trade-offs** — cost vs. speed breakdown (e.g., "Added cache: saves 5 min/run, costs $0.02/run")
- **Validation Status** — `act` dry-run result or schema validation result

The reviewer can view the diff inline on GitHub, check the trade-off rationale, and merge or request changes.

**Input:** PR notification on GitHub  
**Output:** Merged PR or change request  

---

### CUJ-5: Continuous Optimization (v2 — Deferred)

Scheduled weekly runs that detect new bottlenecks since last analysis. Requires CronJob deployment + state persistence + diff detection. Deferred to v2.

---

## Mode Reference

### Optimize Mode

| Aspect | Detail |
|--------|--------|
| Command | `python main.py --repo owner/repo --optimize` |
| Default? | Yes (optimize is the default mode) |
| Token scope | `repo` (write access required) |
| GitHub API calls | Read: workflows, runs, jobs. Write: create branch, commit, PR |
| Output | PR opened on target repo |
| LLM calls | OMLX for classify + propose; Cloud (Claude/gpt-4o-mini) for YAML generation |
| Human interaction | Trade-off table via CLI interrupt |
| Session persistence | SQLite checkpoint — resume with `--resume <thread_id>` |

### Audit Mode

| Aspect | Detail |
|--------|--------|
| Command | `python main.py --repo owner/repo --audit` |
| Token scope | `public_repo` or unauthenticated (read-only) |
| Output | CLI report |
| PRs created? | No |

### Field Study Mode

| Aspect | Detail |
|--------|--------|
| Command | `python main.py --field-study --repos a,b,c --pr-limit 10 --since 30d` |
| Token scope | `public_repo` or unauthenticated (read-only) |
| Output | Markdown reports in `reports/<repo>/` |
| PRs created? | No |
| Optional flags | `--review` (interactive per-PR inspection), `--pr-limit`, `--since` |

### Resume

| Aspect | Detail |
|--------|--------|
| Command | `python main.py --resume <thread_id>` |
| Behavior | Loads state from SQLite checkpoint, re-displays trade-off table, continues from interrupt |

---

## Requirements

- Python 3.11+ or Docker
- OMLX running locally at `127.0.0.1:8000` (free local LLM inference)
- GitHub PAT with `repo` scope (optimize mode) or `public_repo` scope (field study/audit)
- Optional: OpenAI/Anthropic API keys for cloud LLM YAML generation
- Optional: `act` installed for workflow validation

## Quick Start

```bash
# 1. Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your GitHub token and LLM settings

# 2. Run optimize mode
python main.py --repo moby/moby --optimize

# 3. Or run field study (read-only)
python main.py --field-study --repos kubernetes/kubernetes,tensorflow/tensorflow,moby/moby --pr-limit 10 --since 30d
```

Or with Docker:

```bash
docker build -t cicd-bottleneck-optimizer .
docker run -v ./config.yaml:/app/config.yaml \
  cicd-bottleneck-optimizer --repo kubernetes/kubernetes --optimize
```
