# PR #152245 — Incremental bulk: return 429 on request cancellation, add timeout ITs

- **Repo:** elastic/elasticsearch
- **Author:** mhl-b
- **State:** open
- **Created:** 2026-06-26
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 7s | pass |
| build / check | 8s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | low | LLM |
| oversized_context | build | low | LLM |
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |

**Total savings: 4 min/run**
