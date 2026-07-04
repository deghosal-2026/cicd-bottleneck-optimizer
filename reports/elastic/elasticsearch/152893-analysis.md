# PR #152893 — Skip spawning ML controller when ML is disabled

- **Repo:** elastic/elasticsearch
- **Author:** bpintea
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 7s | pass |
| build / check | 4s | pass |
| build / build | 5s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for the validation stage to avoi | validation | 1m | $0.01 | low |
| Implement caching for the build stage to avoid re- | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
