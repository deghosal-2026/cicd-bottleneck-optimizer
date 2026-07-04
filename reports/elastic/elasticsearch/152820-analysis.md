# PR #152820 — Fix RecoveryIT relocation test

- **Repo:** elastic/elasticsearch
- **Author:** nicktindall
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 4s | pass |
| build / match | 6s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip dep | validation | 1m | $0.01 | low |
| Enable caching for the build process to reuse depe | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
