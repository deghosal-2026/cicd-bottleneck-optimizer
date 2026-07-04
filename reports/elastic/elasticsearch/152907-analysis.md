# PR #152907 — Fix resharding tests following a change to retry start split requests on the target shard

- **Repo:** elastic/elasticsearch
- **Author:** lkts
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 7s | pass |
| build / match | 5s | pass |
| build / build | 5s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for dependencies during the vali | validation | 1m | $0.01 | low |
| Enable caching for the build process to skip steps | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
