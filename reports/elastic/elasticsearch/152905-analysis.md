# PR #152905 — Fix GPU codec issues from Lucene 10.5 upgrade

- **Repo:** elastic/elasticsearch
- **Author:** mayya-sharipova
- **State:** open
- **Created:** 2026-07-03
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 6s | pass |
| build / check | 5s | pass |
| build / build | 7s | pass |

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
