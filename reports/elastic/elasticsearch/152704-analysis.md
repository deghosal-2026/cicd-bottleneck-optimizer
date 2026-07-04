# PR #152704 — ES|QL: check for type mismatch in runtime `match`

- **Repo:** elastic/elasticsearch
- **Author:** KevinCorcoran
- **State:** open
- **Created:** 2026-07-01
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 7s | pass |
| build / check | 5s | pass |
| build / build | 9s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for build artifacts to skip depe | validation | 1m | $0.01 | low |
| Enable pipeline caching for validation steps to re | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
