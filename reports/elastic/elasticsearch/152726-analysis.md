# PR #152726 — [ML] Add ingest model memory autoscaling SPI and service

- **Repo:** elastic/elasticsearch
- **Author:** valeriy42
- **State:** open
- **Created:** 2026-07-02
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 6s | pass |
| build / check | 8s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement caching for validation steps to avoid re | validation | 1m | $0.01 | low |
| Implement caching for build steps to avoid re-down | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
