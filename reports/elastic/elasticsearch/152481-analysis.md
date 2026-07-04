# PR #152481 — Remove columnar index mode and make columnar available as tech preview.

- **Repo:** elastic/elasticsearch
- **Author:** martijnvg
- **State:** open
- **Created:** 2026-06-30
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 7s | pass |
| build / check | 9s | pass |
| build / build | 5s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| oversized_context | validation | low | LLM |
| missing_cache | build | low | Rule |
| oversized_context | build | low | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 4 min/run**
