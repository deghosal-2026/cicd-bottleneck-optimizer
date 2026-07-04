# PR #152890 — ESQL:DS: Further EXTERNAL to FROM migration

- **Repo:** elastic/elasticsearch
- **Author:** bpintea
- **State:** closed
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 5s | pass |
| build / match | 4s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for build artifacts to avoid red | validation | 5m | $0.01 | low |
| Use pipeline artifacts caching to skip dependencie | build | 3m | $0.01 | low |

**Total savings: 8 min/run**
