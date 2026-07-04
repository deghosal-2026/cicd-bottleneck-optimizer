# PR #152200 — [ES|QL] Unmapped fields: fallback to default nulls for two legged PUNKs with no implicit cast

- **Repo:** elastic/elasticsearch
- **Author:** GalLalouche
- **State:** closed
- **Created:** 2026-06-25
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| check | 25s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Implement caching for build steps to avoid re-fetc | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
