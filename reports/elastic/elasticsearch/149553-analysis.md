# PR #149553 — Data node direct recovery cancellation

- **Repo:** elastic/elasticsearch
- **Author:** inespot
- **State:** open
- **Created:** 2026-05-21
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 6s | pass |
| build / check | 9s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | medium | LLM |
| oversized_context | build | medium | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
