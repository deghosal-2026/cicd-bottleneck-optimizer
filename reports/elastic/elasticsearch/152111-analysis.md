# PR #152111 — Restrict doc values multi_value/nullability parameters to columnar mode

- **Repo:** elastic/elasticsearch
- **Author:** parkertimmins
- **State:** open
- **Created:** 2026-06-24
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 7s | pass |
| build / match | 4s | pass |
| build / build | 7s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | low | LLM |
| missing_cache | validation | low | Rule |
| oversized_context | build | low | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 3 min/run**
