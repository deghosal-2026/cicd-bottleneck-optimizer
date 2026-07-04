# PR #152821 — [Security] Grant built-in viewer/editor read access to Entity Store v2 and Entity Analytics indices

- **Repo:** elastic/elasticsearch
- **Author:** opauloh
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 8s | pass |
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
| Enable caching for the build process to reduce the | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
