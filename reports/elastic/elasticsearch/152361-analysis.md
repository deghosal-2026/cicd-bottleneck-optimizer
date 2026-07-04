# PR #152361 — Added nullability doc_values mapping parameter

- **Repo:** elastic/elasticsearch
- **Author:** Kubik42
- **State:** closed
- **Created:** 2026-06-26
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 5s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | low | LLM |
| missing_cache | validation | low | Rule |
| oversized_context | build | low | LLM |
| missing_cache | build | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add cache directive to 'validation' to avoid re-do | validation | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |

**Total savings: 4 min/run**
