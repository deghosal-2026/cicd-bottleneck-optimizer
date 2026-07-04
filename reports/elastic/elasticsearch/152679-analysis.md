# PR #152679 — Deflake FUSE multivalued-group warning tests

- **Repo:** elastic/elasticsearch
- **Author:** lefteris-z
- **State:** closed
- **Created:** 2026-07-01
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| build / check | 8s | pass |
| build / match | 6s | pass |
| build / build | 4s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| oversized_context | validation | low | LLM |
| oversized_context | build | low | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Optimize validation process by reducing oversized  | validation | 1m | $0.01 | low |
| Optimize build process by reducing oversized conte | build | 1m | $0.01 | low |

**Total savings: 2 min/run**
