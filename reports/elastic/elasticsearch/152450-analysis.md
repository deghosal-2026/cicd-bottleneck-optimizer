# PR #152450 — ES|QL|DS: Push heavy aggregates (incl. filtered) through UnionAll

- **Repo:** elastic/elasticsearch
- **Author:** julian-elastic
- **State:** open
- **Created:** 2026-06-29
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 5s | pass |
| build / check | 6s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Enable caching for dependencies in the validation  | validation | 1m | $0.01 | low |
| Implement caching for the build phase to avoid reb | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
