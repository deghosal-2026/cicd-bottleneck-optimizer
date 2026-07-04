# PR #149553 — Data node direct recovery cancellation

- **Repo:** elastic/elasticsearch
- **Author:** inespot
- **State:** open
- **Created:** 2026-05-21
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 6s | pass |
| build / check | 9s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation tasks to skip reb | validation | 1m | $0.01 | low |
| Utilize caching for the build process to avoid red | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
