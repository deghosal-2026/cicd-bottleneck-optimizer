# PR #152300 — ES|QL|DS direct-to-block CSV/TSV read path

- **Repo:** elastic/elasticsearch
- **Author:** julian-elastic
- **State:** closed
- **Created:** 2026-06-26
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 8s | pass |
| build / match | 6s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Introduce caching for the build process to store a | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
