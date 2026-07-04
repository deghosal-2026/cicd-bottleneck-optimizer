# PR #57115 — Fix Android text descender clipping with tight lineHeight

- **Repo:** facebook/react/native
- **Author:** TorinAsakura
- **State:** closed
- **Created:** 2026-06-08
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| validate_cxx_api_snapshots | 176s | pass |

## Bottlenecks

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | applyNeedsAttentionLabel | low | Rule |
| missing_cache | triage-issue | low | Rule |
| missing_cache | act-on-label | low | Rule |
| serial_parallel | triage-issue | low | Rule |
| serial_parallel | act-on-label | low | Rule |
| missing_cache | stale | low | Rule |
| missing_cache | stale-asc | low | Rule |
| missing_cache | stale-needs-author-feedback | low | Rule |
| missing_cache | stale-needs-author-feedback-asc | low | Rule |
| serial_parallel | stale | low | Rule |
| serial_parallel | stale-asc | low | Rule |
| serial_parallel | stale-needs-author-feedback | low | Rule |
| serial_parallel | stale-needs-author-feedback-asc | low | Rule |
| missing_cache | rebase | low | Rule |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Enable caching on pipeline stages to avoid rerunni | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Optimize the pipeline by serializing tasks on the  | triage-issue | 1m | $0.01 | medium |
| Optimize the pipeline by serializing tasks on the  | act-on-label | 1m | $0.01 | medium |
| Enable caching on the stale label to avoid rerunni | triage-issue | 1m | $0.00 | low |
| Enable caching on the stale-asc label to avoid rer | act-on-label | 1m | $0.00 | low |
| Enable caching on the stale-needs-author-feedback  | stale | 1m | $0.01 | low |
| Enable caching on the stale-needs-author-feedback- | stale-asc | 1m | $0.01 | low |
| Optimize the pipeline by serializing tasks on the  | stale-needs-author-feedback | 1m | $0.01 | medium |
| Optimize the pipeline by serializing tasks on the  | stale-needs-author-feedback-asc | 1m | $0.01 | medium |
| Optimize the pipeline by serializing tasks on the  | stale | 1m | $0.00 | medium |
| Optimize the pipeline by serializing tasks on the  | stale-asc | 1m | $0.00 | medium |
| Enable caching on the rebase label to avoid rerunn | stale-needs-author-feedback | 1m | $0.00 | low |
| Run 'stale-needs-author-feedback-asc' in parallel  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add cache directive to 'rebase' to avoid re-downlo | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
