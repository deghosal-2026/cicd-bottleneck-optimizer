# PR #152361 — Added nullability doc_values mapping parameter

- **Repo:** elastic/elasticsearch
- **Author:** Kubik42
- **State:** closed
- **Created:** 2026-06-26
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 5s | pass |
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
| Implement caching for build steps to reduce the ti | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
