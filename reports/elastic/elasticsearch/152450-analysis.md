# PR #152450 — ES|QL|DS: Push heavy aggregates (incl. filtered) through UnionAll

- **Repo:** elastic/elasticsearch
- **Author:** julian-elastic
- **State:** open
- **Created:** 2026-06-29
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / match | 5s | pass |
| build / check | 6s | pass |
| build / build | 4s | pass |

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
