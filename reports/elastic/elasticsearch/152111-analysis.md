# PR #152111 — Restrict doc values multi_value/nullability parameters to columnar mode

- **Repo:** elastic/elasticsearch
- **Author:** parkertimmins
- **State:** open
- **Created:** 2026-06-24
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 7s | pass |
| build / match | 4s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for the validation stage to avoi | validation | 1m | $0.01 | low |
| Implement caching for the build stage to avoid rer | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
