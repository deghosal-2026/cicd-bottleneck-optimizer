# PR #152679 — Deflake FUSE multivalued-group warning tests

- **Repo:** elastic/elasticsearch
- **Author:** lefteris-z
- **State:** closed
- **Created:** 2026-07-01
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 8s | pass |
| build / match | 6s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Enable caching for build steps to reduce the time  | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
