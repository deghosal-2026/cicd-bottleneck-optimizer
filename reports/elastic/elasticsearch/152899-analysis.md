# PR #152899 — Support for encrypted cloud credentials

- **Repo:** elastic/elasticsearch
- **Author:** slobodanadamovic
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 6s | pass |
| build / check | 8s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip dep | validation | 1m | $0.01 | low |
| Introduce caching for the build process to reuse d | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
