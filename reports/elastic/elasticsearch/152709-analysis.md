# PR #152709 — ES|QL Fix assertion with Lookup Join

- **Repo:** elastic/elasticsearch
- **Author:** julian-elastic
- **State:** open
- **Created:** 2026-07-02
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 5s | pass |
| build / check | 8s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Enable caching for validation processes to skip re | validation | 1m | $0.01 | low |
| Implement caching for the build process to reuse c | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
