# PR #151881 — Use ObjectParser for Amazon Bedrock service settings

- **Repo:** elastic/elasticsearch
- **Author:** demjened
- **State:** open
- **Created:** 2026-06-22
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 5s | pass |
| build / check | 6s | pass |
| build / build | 6s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Implement a pipeline cache to skip steps that have | validation | 1m | $0.01 | low |
| Add pip cache to the build job to store and reuse  | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
