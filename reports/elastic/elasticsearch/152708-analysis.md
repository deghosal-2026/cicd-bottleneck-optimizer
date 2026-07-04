# PR #152708 — Make data-generation test framework index-mode aware for doc_values

- **Repo:** elastic/elasticsearch
- **Author:** parkertimmins
- **State:** closed
- **Created:** 2026-07-02
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 4s | pass |
| build / check | 8s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Integrate caching mechanism into the build process | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
