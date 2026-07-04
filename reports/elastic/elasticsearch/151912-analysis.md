# PR #151912 — PromQL query logging

- **Repo:** elastic/elasticsearch
- **Author:** smalyshev
- **State:** open
- **Created:** 2026-06-22
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 5s | pass |
| build / match | 12s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement a cache mechanism for dependencies in th | validation | 1m | $0.01 | low |
| Implement a cache mechanism for the build artifact | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
