# PR #152867 — ESQL: Solves NoSuchElementException in ViewUnionAll analyzer retries

- **Repo:** elastic/elasticsearch
- **Author:** ncordon
- **State:** closed
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 5s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement a caching mechanism for dependencies dur | validation | 1m | $0.01 | low |
| Enable caching for the build process to skip depen | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
