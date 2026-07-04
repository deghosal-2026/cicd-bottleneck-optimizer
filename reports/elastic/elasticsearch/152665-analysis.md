# PR #152665 — ES|QL: Enable MATCH_RUNTIME_SEARCH capability in release builds

- **Repo:** elastic/elasticsearch
- **Author:** ioanatia
- **State:** open
- **Created:** 2026-07-01
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 5s | pass |
| build / match | 7s | pass |
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
| Implement caching for build steps to avoid rerunni | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
