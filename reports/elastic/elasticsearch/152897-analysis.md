# PR #152897 — [Backport] Fix NodesCachesStatsIntegTests.testNodesCachesStats

- **Repo:** elastic/elasticsearch
- **Author:** samxbr
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 4s | pass |
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
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
