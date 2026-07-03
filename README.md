# CI/CD Bottleneck Optimizer

A LangGraph agent that profiles GitHub Actions workflows, identifies bottlenecks, proposes optimizations with quantified estimates, and opens PRs with the rewritten YAML.

## How It Works

```
fetch workflows & run history → profile per-job timing → classify bottlenecks → propose optimizations → human approves trade-offs → generate YAML → open PR
```

## Features

- **Profile** — fetches workflow YAML + last 50 runs via GitHub API, profiles per-job median/p90 duration, failure rate, cache hit ratio
- **Classify** — identifies redundant rebuilds, serial-where-parallel-possible, oversized context, missing cache, redundant matrix
- **Propose** — generates candidate optimizations with quantified time savings AND cost estimates
- **Human-in-the-loop** — `interrupt()` presents trade-off matrix; human edits which optimizations to apply
- **Generate** — produces valid rewritten workflow YAML + opens a PR with before/after estimates

## Quick Start

```bash
# Clone and install
git clone https://github.com/deghosal-2026/cicd-bottleneck-optimizer.git
cd cicd-bottleneck-optimizer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run against a public repo
python main.py --repo kubernetes/kubernetes

# Run with local LLM (OMLX)
python main.py --repo kubernetes/kubernetes --model omlx

# Run with all stages (requires GitHub token + OMLX or cloud API key)
python main.py --repo kubernetes/kubernetes --optimize --pr
```

## Requirements

- Python 3.11+
- [OMLX](https://omlx.ai) (local) or OpenAI/Anthropic API key (cloud)
- GitHub personal access token (for API calls + PR creation)

## Technology Stack

| Layer | Technologies |
|---|---|
| Agent framework | LangGraph, LangChain |
| LLM | OMLX (local), OpenAI, Anthropic Claude |
| Infrastructure | Docker, FastAPI, Qdrant |
| Data sources | GitHub REST API, GitHub GraphQL API |
| Validation | `act` (local workflow runner) |

## Project Status

Mid complexity. Second project in the DevOps Agentic Track (#33 of 55).

## License

MIT
