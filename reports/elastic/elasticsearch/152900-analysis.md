# PR #152900 — ESQL: Solves NoSuchElementException in ViewUnionAll analyzer retries

- **Repo:** elastic/elasticsearch
- **Author:** ncordon
- **State:** closed
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 8s | pass |
| build / check | 6s | pass |
| build / build | 10s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
