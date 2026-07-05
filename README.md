# CI/CD Bottleneck Optimizer

A LangGraph agent that profiles GitHub Actions workflows, identifies bottlenecks, proposes optimizations with quantified time/cost estimates, and generates rewritten YAML with PR body.

## How It Works

```
fetch workflows & run history → profile per-job timing → classify bottlenecks
  → propose optimizations → human approves trade-offs → generate YAML → validate → open PR
```

The agent runs as a LangGraph state machine with SQLite checkpointing, so interrupted sessions can be resumed across process restarts.

## Features

- **Profile** — fetches workflow YAML + last 50 runs via GitHub API, profiles per-job median/p90 duration, failure rate, cache hit ratio
- **Classify** — dual classifier: rule-based (missing_cache, serial_parallel, redundant_matrix) + LLM (redundant_rebuild, oversized_context). LLM always runs alongside rules; results merged with deduplication
- **Propose** — generates candidate optimizations with quantified time savings, cost estimates, and risk levels
- **Human-in-the-loop** — trade-off table presents optimizations with time/cost/risk; human selects which to apply
- **Generate** — rule-based YAML rewrite + LLM fallback for generation; PyYAML validation with 3-retry loop
- **Resume** — SQLite checkpointer persists state; resume any session with `--resume <thread_id>`
- **Field study** — batch analyze PRs across multiple repos; standalone script with 20-repo pool, random selection, 7-day window

## Quick Start

```bash
# Clone and install
git clone https://github.com/deghosal-2026/cicd-bottleneck-optimizer.git
cd cicd-bottleneck-optimizer
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
# Edit config.yaml — add your GitHub token

# Audit a repo (read-only, no PR created)
python3 main.py --repo kubernetes/kubernetes --audit

# Optimize a repo (requires write access, opens PR)
python3 main.py --repo owner/repo --optimize

# Field study across multiple repos
python3 main.py --field-study --repos owner1/repo1,owner2/repo2 --pr-limit 10 --since 30

# Run standalone field study (uses 20-repo pool, random selection)
python3 run_field_study.py

# Resume an interrupted session
python3 main.py --resume <session-id>
```

## CLI Reference

| Flag | Description | Default |
|---|---|---|
| `--repo owner/repo` | Target repository | Required (unless --field-study) |
| `--optimize` | Full mode: profile, classify, generate YAML, open PR | Default |
| `--audit` | Read-only: profile, classify, print report | — |
| `--field-study` | Batch analyze PRs across repos | — |
| `--repos a/b,c/d` | Comma-separated repos for field study | — |
| `--pr-limit N` | PRs per repo in field study | 10 |
| `--since N` | PR lookback window in days | 30 |
| `--workflow-limit N` | Max workflows to analyze | 5 |
| `--review` | Interactive trade-off table in field study | — |
| `--resume THREAD_ID` | Resume interrupted session | — |

## Configuration

Copy `config.yaml.example` to `config.yaml` and fill in:

```yaml
github:
  token: "ghp_your_token_here"     # Required — needs repo scope for --optimize

cost_rates:
  runner_per_min: 0.008            # GitHub Actions Linux runner $/min
  cache_per_gb_month: 0.007        # GitHub Actions cache $/GB/month

llm:
  local:
    base_url: "http://127.0.0.1:8000/v1"
    api_key: "omlx-test"
    model: "mlx-community/gemma-3-4b-it-4bit"
```

The LLM runs locally via [OMLX](https://github.com/ml-explore/mlx-examples). No cloud API keys needed.

## Local LLM Setup

The classifier and YAML generator use a local LLM via OMLX (OpenAI-compatible API on localhost). To run:

```bash
# Install OMLX server (Apple Silicon only)
pip install mlx-lm

# Start server with Gemma 3 4B (4-bit quantized)
mlx_lm.server --model mlx-community/gemma-3-4b-it-4bit --port 8000
```

If OMLX is unavailable, the agent continues with rule-based classification only and skips LLM-assisted YAML generation.

## Bottleneck Types

| Type | Source | Description |
|---|---|---|
| `missing_cache` | Rules | No `actions/cache` directive in build/install job |
| `serial_parallel` | Rules | Job with `needs:` dependency that could run in parallel |
| `redundant_matrix` | Rules | Matrix with overlapping OS/language combinations |
| `redundant_rebuild` | LLM | Same artifact rebuilt from scratch in multiple jobs |
| `oversized_context` | LLM | Docker build with no `.dockerignore`, large repo context |

## Project Structure

```
main.py                 CLI entry point
graph.py                LangGraph state graph + build_graph()
state.py                AgentState TypedDict
config.py               Config loading + validation
run_field_study.py      Standalone field study script (20-repo pool)
tools/github.py         GitHub API client (REST, pagination, rate limit)
llm/client.py           LLM client (OMLX local)
lib/classifier.py       Dual classifier (rules + LLM)
lib/optimizer.py        Optimization proposer + savings simulator
lib/generator.py        YAML rewriter (rule-based)
lib/validator.py        YAML validator (PyYAML schema check)
lib/profiler.py         Job timing profiler (median, p90, p99)
lib/cli.py              CLI tables (trade-off, summary)
nodes/                  LangGraph nodes (fetch, profile, classify, optimize, pr, generate)
tests/                  83 tests (unit, graph integration, live)
data/                   Dataset — 429 PRs across 7 repos
llm-output/             Field study reports — 35 PRs across 7 repos
docs/                   PRD, SPEC, WBS, field study report
```

## Test Results

```
83 passed, 57 skipped (live tests require --run-live flag)
```

- **Unit tests** — classifier (28), optimizer (24), profiler (19)
- **Graph integration tests** — optimize path (3), resume/checkpoint (3), LLM routing (6)
- **Live tests** — skipped by default, require `--run-live` flag and GitHub API access

## Field Study Results

35 PRs analyzed across 7 repos using Gemma 3 4B (4-bit, local via OMLX):

| Repo | PRs | Bottlenecks | 
|---|---|---|
| react/react | 5 | 83 |
| python/cpython | 5 | 96 |
| nodejs/node | 5 | 97 |
| flutter/flutter | 5 | 89 |
| huggingface/transformers | 5 | 95 |
| apache/kafka | 5 | 105 |
| django/django | 5 | 190 |
| **Total** | **35** | **755** |

Full report: [`docs/field-study-report.md`](docs/field-study-report.md)

## Requirements

- Python 3.11+
- GitHub personal access token (repo scope for optimize, public_repo for audit/field study)
- OMLX server (optional — Apple Silicon only, for LLM-assisted classification)
- No cloud API keys needed

## Technology Stack

| Layer | Technologies |
|---|---|
| Agent framework | LangGraph 1.2.6 |
| LLM | OMLX (local, Gemma 3 4B 4-bit) |
| Checkpointing | SQLite (langgraph-checkpoint-sqlite) |
| Data source | GitHub REST API |
| Validation | PyYAML schema check |

## License

MIT
