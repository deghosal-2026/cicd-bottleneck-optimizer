# PR #152383 — ESQL: Fix ClassCastException for narrow time windows

- **Repo:** elastic/elasticsearch
- **Author:** sidosera
- **State:** open
- **Created:** 2026-06-28
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 8s | pass |
| build / check | 6s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Implement caching for build steps to avoid reinsta | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
