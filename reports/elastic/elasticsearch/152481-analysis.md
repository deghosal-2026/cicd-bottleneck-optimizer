# PR #152481 — Remove columnar index mode and make columnar available as tech preview.

- **Repo:** elastic/elasticsearch
- **Author:** martijnvg
- **State:** open
- **Created:** 2026-06-30
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 7s | pass |
| build / check | 9s | pass |
| build / build | 5s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip dep | validation | 1m | $0.01 | low |
| Introduce caching for build processes to avoid reb | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
