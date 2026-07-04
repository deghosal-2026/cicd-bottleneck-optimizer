# PR #152880 — Reapply "Redo blob cache defer gap list evaluation" (#150118) (#152647)

- **Repo:** elastic/elasticsearch
- **Author:** ywangd
- **State:** closed
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 5s | pass |
| build / match | 7s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for dependencies during the vali | validation | 1m | $0.01 | low |
| Implement caching for the entire build process to  | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
