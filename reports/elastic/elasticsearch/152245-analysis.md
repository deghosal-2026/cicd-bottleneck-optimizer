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
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Enable caching for the validation step to skip dep | validation | 1m | $0.01 | low |
| Implement caching for the build step to reuse depe | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
