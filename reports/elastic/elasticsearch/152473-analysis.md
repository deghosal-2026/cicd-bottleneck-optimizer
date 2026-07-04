# PR #152473 — ES|QL|DS: user-declared schema for external datasets

- **Repo:** elastic/elasticsearch
- **Author:** quackaplop
- **State:** open
- **Created:** 2026-06-30
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 4s | pass |
| build / check | 6s | pass |
| build / build | 10s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for dependencies in the validati | validation | 1m | $0.01 | low |
| Implement caching for the build artifacts in the b | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
