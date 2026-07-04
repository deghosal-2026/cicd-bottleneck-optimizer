# PR #152864 — ESQL: fix COUNT and IS NOT NULL over top-level external Parquet list columns

- **Repo:** elastic/elasticsearch
- **Author:** quackaplop
- **State:** closed
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 4s | pass |
| build / match | 9s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip red | validation | 1m | $0.01 | low |
| Enable caching for the build process to reuse depe | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
