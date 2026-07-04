# PR #152908 — Unmute term vectors resharding tests

- **Repo:** elastic/elasticsearch
- **Author:** lkts
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 8s | pass |
| build / check | 7s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Implement caching for the build process to re-use  | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
