# PR #152376 — [ES|QL] Take where in subquery out of snapshot

- **Repo:** elastic/elasticsearch
- **Author:** fang-xing-esql
- **State:** closed
- **Created:** 2026-06-28
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 4s | pass |
| build / build | 5s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | validation | low | Rule |
| missing_cache | build | low | Rule |
| oversized_context | validation | medium | LLM |
| oversized_context | build | medium | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 4 min/run**
