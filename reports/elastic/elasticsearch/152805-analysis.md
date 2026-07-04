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
| Implement caching for dependencies during the vali | validation | 1m | $0.01 | low |
| Implement caching for build artifacts during the b | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
