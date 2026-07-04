# PR #152383 — ESQL: Fix ClassCastException for narrow time windows

- **Repo:** elastic/elasticsearch
- **Author:** sidosera
- **State:** open
- **Created:** 2026-06-28
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 8s | pass |
| build / check | 6s | pass |
| build / build | 8s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | low | LLM |
| oversized_context | build | low | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
