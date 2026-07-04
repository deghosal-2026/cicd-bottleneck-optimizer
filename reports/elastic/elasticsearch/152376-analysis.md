# PR #152376 — [ES|QL] Take where in subquery out of snapshot

- **Repo:** elastic/elasticsearch
- **Author:** fang-xing-esql
- **State:** closed
- **Created:** 2026-06-28
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 4s | pass |
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
| Enable caching for the build process to reuse depe | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
