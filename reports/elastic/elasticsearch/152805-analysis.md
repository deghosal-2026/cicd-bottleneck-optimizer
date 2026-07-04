# PR #152805 — Add blob cache lock-acquisition metric

- **Repo:** elastic/elasticsearch
- **Author:** szybia
- **State:** closed
- **Created:** 2026-07-02
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 9s | pass |
| build / match | 4s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
