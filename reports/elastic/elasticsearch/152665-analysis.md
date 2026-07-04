# PR #152665 — ES|QL: Enable MATCH_RUNTIME_SEARCH capability in release builds

- **Repo:** elastic/elasticsearch
- **Author:** ioanatia
- **State:** open
- **Created:** 2026-07-01
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 5s | pass |
| build / match | 7s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | medium | LLM |
| oversized_context | build | medium | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
