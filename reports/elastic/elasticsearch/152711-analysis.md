# PR #152711 — Check success before forwarding to the original progress listener

- **Repo:** elastic/elasticsearch
- **Author:** ywangd
- **State:** closed
- **Created:** 2026-07-02
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 8s | pass |
| build / match | 8s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip dep | validation | 1m | $0.01 | low |
| Implement caching for build steps to reuse depende | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
