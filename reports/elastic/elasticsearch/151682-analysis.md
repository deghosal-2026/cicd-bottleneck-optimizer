# PR #151682 — ESQL: Support MATCH(FIELD_EXTRACT(flattened, "path"), "value")

- **Repo:** elastic/elasticsearch
- **Author:** nik9000
- **State:** open
- **Created:** 2026-06-18
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 6s | pass |
| build / match | 6s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | medium | LLM |
| missing_cache | build | low | Rule |
| oversized_context | build | medium | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'validation' to exclude unnec | validation | 1m | $0.01 | low |
| Add cache directive to 'build' to avoid re-downloa | build | 1m | $0.01 | low |
| Add .dockerignore to 'build' to exclude unnecessar | build | 1m | $0.01 | low |

**Total savings: 3 min/run**
