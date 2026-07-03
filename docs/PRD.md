# PRD — CI/CD Bottleneck Optimizer

| Field | Value |
|---|---|
| Project | #33 CI/CD Pipeline Bottleneck Analyzer & Optimizer |
| Status | Draft |
| Complexity | Mid |
| Created | 2026-07-03 |
| Owner | Debashish Ghosal |
| GitHub | https://github.com/deghosal-2026/cicd-bottleneck-optimizer |

---

## 1. Overview

An AI agent that fetches real GitHub Actions workflow files and run history from large public repositories, identifies performance bottlenecks, proposes quantified optimizations, and opens a PR with the rewritten workflow. A human approves the trade-offs (cache cost vs. speed, parallel fan-out risk) before the PR opens.

This is the second project in the DevOps Agentic Track, extending CI-Agent (#04) from failure triage to performance optimization.

---

## 2. Problem Statement

CI pipelines in mature repos (`kubernetes/kubernetes`, `tensorflow/tensorflow`, `moby/moby`) run for 30–120 minutes. Engineers accept this as "just how it is" — but 30–50% of that time is waste:

- Redundant matrix legs rebuilding the same artifact
- Serial steps that could run in parallel
- Missing or ineffective cache hits
- Oversized build contexts shipping unnecessary files

No one has time to audit a 500-line workflow YAML by hand. Existing tools report *that* a pipeline is slow, but don't propose *specific* fixes with quantified impact.

### Why existing solutions fall short

| Tool | What it does | What it doesn't do |
|---|---|---|
| GitHub Actions insights | Shows run duration trends | Doesn't propose fixes |
| `act` | Runs workflows locally | Doesn't analyze or optimize |
| Manual review | Engineer reads YAML | Doesn't scale; misses patterns |

---

## 3. Target Users

| User | Context | Pain Point |
|---|---|---|
| **DevOps engineer** | Owns CI for a team of 20+ | Pipeline takes 45 min; no time to audit |
| **Engineer learning CI** | Studies how large repos do CI | Wants to see what big repos do well/poorly |
| **CI owner** | Responsible for monthly CI cost + speed | Needs data to justify optimization work |

---

## 4. Goals & Non-Goals

### Goals

1. Fetch workflows + run history from any public GitHub repo via API
2. Profile per-job timing (median, p90, failure rate, cache hit ratio)
3. Classify at least 3 bottleneck types with evidence
4. Propose optimizations with quantified time savings AND cost estimates
5. Present trade-offs to a human via `interrupt()`; human edits selections
6. Generate valid rewritten workflow YAML
7. Open a PR on the target repo with before/after estimates and trade-off rationale

### Non-Goals (v1)

- Private repositories (v2 — requires auth + privacy review)
- Non-GitHub-Actions CI systems (GitLab CI, Jenkins, CircleCI)
- Auto-merging optimization PRs (human always reviews + merges)
- Optimizations that change build semantics (reordering tests, changing build flags)
- Real-time/streaming analysis (batch mode only in v1)
- Scheduled/continuous optimization mode (v2 — requires CronJob + state persistence + diff detection)
- Web dashboard (v1 is CLI output only; web dashboard deferred to v2)
- Cross-repo pattern memory via Qdrant (v2 — requires embedding + storage + retrieval)
- GitHub Enterprise repos (v2 — auth flow differs)

---

## 5. Customer User Journeys

### CUJ-1: Optimize a slow pipeline (v1)

| Step | Actor | Action |
|---|---|---|
| 1 | DevOps engineer | `python main.py --repo owner/repo --optimize` |
| 2 | Agent | Fetches all `.github/workflows/*.yml` + last 50 runs |
| 3 | Agent | Profiles each job: median, p90, failure rate, cache hit ratio |
| 4 | Agent | Classifies bottlenecks: redundant rebuilds, serial-where-parallel, missing cache, oversized context |
| 5 | Agent | Proposes optimizations with quantified estimates ("job X: 8m → 3m by adding cache, costs $0.02/run") |
| 6 | Agent | `interrupt()` — presents trade-off table in CLI |
| 7 | Human | Edits which optimizations to apply (rejects costly cache, accepts parallelism) |
| 8 | Agent | Generates rewritten workflow YAML, validates syntax |
| 9 | Agent | Opens PR on target repo with diff + before/after estimates + trade-off rationale |
| 10 | Human | Reviews PR, merges or requests changes |

### CUJ-2: Audit a public repo for learning (v1)

| Step | Actor | Action |
|---|---|---|
| 1 | Engineer | `python main.py --repo kubernetes/kubernetes --audit` |
| 2 | Agent | Fetches + profiles + classifies |
| 3 | Agent | Prints a report of what the repo does well/poorly to CLI |
| 4 | Engineer | Decides which patterns to adopt in own repos |

### CUJ-3: Continuous optimization (v2 — deferred)

Scheduled weekly run that detects new bottlenecks since last run. Requires CronJob deployment + state persistence + diff detection. Out of scope for v1.

### CUJ-4: PR review of optimized workflow (v1)

| Step | Actor | Action |
|---|---|---|
| 1 | Reviewer | Receives PR notification |
| 2 | Reviewer | PR includes diff + before/after estimates + trade-off rationale |
| 3 | Reviewer | Merges or requests changes |

---

## 6. Functional Requirements

### FR-1: GitHub API Integration

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | Fetch all workflow YAML files from `.github/workflows/` | P0 |
| FR-1.2 | Fetch last 50 runs per workflow with timing data | P0 |
| FR-1.3 | Fetch per-job timing + logs via jobs API | P0 |
| FR-1.4 | Handle GitHub API pagination + rate limiting | P0 |
| FR-1.5 | Support GitHub GraphQL API for batched timing data at scale | P1 |
| FR-1.6 | Create a branch + commit + PR on the target repo via GitHub API | P0 |

### FR-2: Profiling

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | Parse workflow YAML into a job graph | P0 |
| FR-2.2 | Compute median, p90, p99 duration per job | P0 |
| FR-2.3 | Compute failure rate per job | P0 |
| FR-2.4 | Estimate cache hit ratio from run logs | P1 |

### FR-3: Bottleneck Classification

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Classify redundant rebuilds (same artifact rebuilt across jobs) | P0 |
| FR-3.2 | Classify serial-where-parallel-possible (independent jobs running sequentially) | P0 |
| FR-3.3 | Classify missing cache (no `cache:` directive or cache key is too broad) | P0 |
| FR-3.4 | Classify oversized build context (no `.dockerignore` or large context) | P1 |
| FR-3.5 | Classify redundant matrix legs (overlapping matrix dimensions) | P1 |

### FR-4: Optimization Proposals

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | Generate candidate optimizations per bottleneck | P0 |
| FR-4.2 | Estimate time savings per optimization (minutes saved) | P0 |
| FR-4.3 | Estimate cost per optimization (cache storage cost, runner cost) | P0 |
| FR-4.4 | Estimate risk level per optimization (low/medium/high) | P0 |
| FR-4.5 | Simulate expected total time savings across all selected optimizations | P1 |

### FR-5: Human-in-the-Loop

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | `interrupt()` presents trade-off table in CLI: optimization, time saved, cost, risk | P0 |
| FR-5.2 | Human selects/deselects optimizations via CLI input | P0 |
| FR-5.3 | Human can edit optimization parameters (e.g., cache key strategy) | P1 |
| FR-5.4 | Graph re-runs with revised state after human input | P0 |

### FR-6: YAML Generation + PR

| ID | Requirement | Priority |
|---|---|---|
| FR-6.1 | Generate valid rewritten workflow YAML | P0 |
| FR-6.2 | Validate YAML syntax | P0 |
| FR-6.3 | Validate workflow with `act` locally (dry run) | P1 |
| FR-6.4 | Generate diff (before/after) | P0 |
| FR-6.5 | Open PR on target repo with description: estimates, trade-offs, rationale | P0 |

### FR-7: CLI Output

| ID | Requirement | Priority |
|---|---|---|
| FR-7.1 | Print before/after time per job as formatted table | P0 |
| FR-7.2 | Print estimated monthly savings | P1 |
| FR-7.3 | Print cache cost per optimization | P1 |
| FR-7.4 | Print PRs opened/merged summary | P2 |

---

## 7. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | **Performance** — Full analysis of one repo completes in < 2 min (excluding LLM calls) |
| NFR-2 | **Privacy** — Repo contents analyzed with local LLM by default; cloud LLM only for final YAML generation |
| NFR-3 | **Cost** — Token cost tracked per optimization; local LLM used for >80% of calls |
| NFR-4 | **Reliability** — GitHub API rate-limit errors are retried with exponential backoff |
| NFR-5 | **Portability** — Runs in Docker |
| NFR-6 | **Observability** — Every agent step logged with duration + token count |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Repos analyzed | 1 (kubernetes/kubernetes) for v1 | GitHub API call count |
| Bottleneck types classified | ≥ 3 | Classifier output |
| Time savings proposed | ≥ 20% of total pipeline time | Before/after estimate |
| PRs opened with valid YAML | 100% pass syntax validation | YAML linter + `act` dry run |
| Human approval rate | ≥ 50% of proposed optimizations selected | interrupt() selection log |
| Token cost | < $1 per repo analysis (local LLM default) | Token counter |
| PR merge rate (stretch) | ≥ 30% of opened PRs merged | GitHub PR status |

---

## 9. Constraints

- **Public repos only** for v1 (no private repo auth flow)
- **GitHub Actions only** (no GitLab CI, Jenkins, CircleCI)
- **Target repo requires write access** — agent pushes branch + opens PR directly on the target repo (not a fork)
- **Mechanical optimizations only** — no semantic changes (reordering tests, changing build flags)
- **Human merges** — agent never auto-merges
- **Local LLM default** — cloud LLM only for final generation or low-confidence reasoning
- **CLI output only** — no web dashboard in v1

---

## 10. LLM Strategy

| Tier | Model | Use | Why |
|---|---|---|---|
| Local (free) | OMLX Qwen3.5-9B-MLX-4bit | YAML parsing, bottleneck classification, pattern matching, trade-off descriptions, PR description drafting | Code/YAML analysis is its strength; no data leaves laptop; single model keeps it simple |
| Cloud (API) | OpenAI gpt-4o-mini | Complex optimization reasoning (parallelization strategies, cache key design) | When local model confidence is low; cheap enough for batch |
| Cloud (API) | Claude 3.5 Sonnet | Final YAML generation + validation | Strong at structured output; use for the final PR artifact |

**Strategy:** Default to Qwen3.5-9B-MLX-4bit (local) for all analysis passes. Escalate to cloud only for final YAML generation and low-confidence reasoning. Track token cost per optimization.

**OMLX endpoint:** `http://127.0.0.1:8000/v1` with API key `omlx-test` (see [[training/omlx-tuning.md]] for tuning details).

---

## 11. Technology Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph, LangChain |
| Language | Python 3.11+ |
| Local LLM | OMLX Qwen3.5-9B-MLX-4bit (OpenAI-compatible API on :8000) |
| Cloud LLM (optional) | OpenAI gpt-4o-mini, Claude 3.5 Sonnet |
| Container | Docker |
| Workflow validation | `act` (local GitHub Actions runner) |
| Data sources | GitHub REST API, GitHub GraphQL API |

---

## 12. Milestones

| Milestone | Scope | Output |
|---|---|---|
| M1 | GitHub API tools | `tools/github.py` with pagination, rate limit handling |
| M2 | Profiler | `profiler.py` — median, p90, failure rate, cache hit ratio |
| M3 | Bottleneck classifier | `classifier.py` — rule-based + LLM hybrid |
| M4 | Optimization proposer | `optimizer.py` — per-optimization: type, impact, cost, risk |
| M5 | LangGraph state graph | `graph.py` — full state machine with checkpointing |
| M6 | Trade-off CLI | CLI table display for the `interrupt()` interaction |
| M7 | PR generator | `pr_generator.py` — diff + description with estimates |

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GitHub API rate limits | High | Medium | Token auth (5000 req/hr); GraphQL for batch; cache responses |
| Generated YAML is invalid | Medium | High | Schema validation + `act` dry run before PR |
| LLM proposes semantic changes | Medium | High | System prompt constraints; human review gate; mechanical-only rule |
| Cloud LLM cost exceeds budget | Low | Medium | Local LLM default; cloud only for final generation; token tracking |
| Large repos have too many workflows | Medium | Low | Limit to top N workflows by run frequency; paginate |
| No write access to target repo | Medium | High | Pre-flight check: verify token has `repo` scope + push permission before running |

---

## 14. Open Questions

- [ ] Should we support GitHub Enterprise repos in v2? (auth flow differs)
- [ ] Should v2 add Qdrant for cross-repo pattern memory ("this anti-pattern seen in 3 repos")?
- [ ] Should v2 add a web dashboard (FastAPI) for historical view across multiple runs?
- [ ] Should v2 add fork-mode PR target for repos without write access?

---

## 15. References

- [Project definition (vault)](https://github.com/deghosal-2026/my-2nd-brain/blob/main/vault/projects/33-CICD-Bottleneck-Optimizer.md)
- [LangGraph interrupts](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [GitHub Actions API](https://docs.github.com/en/rest/actions)
- [CI-Agent (#04)](https://github.com/deghosal-2026/ci-agent) — predecessor project
- [OMLX Tuning Guide (vault)](https://github.com/deghosal-2026/my-2nd-brain/blob/main/vault/training/omlx-tuning.md)
