# PR #152888 — Bulk score HNSW candidates during adjacency building

- **Repo:** elastic/elasticsearch
- **Author:** thecoop
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 7s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Implement caching for build steps to avoid re-runn | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
