# PR #151682 — ESQL: Support MATCH(FIELD_EXTRACT(flattened, "path"), "value")

- **Repo:** elastic/elasticsearch
- **Author:** nik9000
- **State:** open
- **Created:** 2026-06-18
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 6s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to skip pre | validation | 1m | $0.01 | low |
| Implement caching for the build process to reuse d | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
