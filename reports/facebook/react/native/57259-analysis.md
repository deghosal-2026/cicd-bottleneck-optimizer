# PR #57259 — Allow to disable shouldDelayChildPressedState on scrollable Android containers (#57259)

- **Repo:** facebook/react/native
- **Author:** j-piasecki
- **State:** closed
- **Created:** 2026-06-18
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| validate_cxx_api_snapshots | 172s | pass |

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
| Optimize builds by adding cache to the applyNeedsA | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Optimize builds by adding cache to the triage-issu | triage-issue | 1m | $0.01 | low |
| Optimize builds by adding cache to the act-on-labe | act-on-label | 1m | $0.01 | low |
| Optimize builds by processing issues sequentially  | triage-issue | 1m | $0.00 | medium |
| Optimize builds by processing issues sequentially  | act-on-label | 1m | $0.00 | medium |
| Optimize builds by adding cache to the stale proce | stale | 1m | $0.01 | low |
| Optimize builds by adding cache to the stale-asc p | stale-asc | 1m | $0.01 | low |
| Optimize builds by adding cache to the stale-needs | stale-needs-author-feedback | 1m | $0.01 | low |
| Optimize builds by adding cache to the stale-needs | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Optimize builds by processing issues sequentially  | stale | 1m | $0.00 | medium |
| Optimize builds by processing issues sequentially  | stale-asc | 1m | $0.00 | medium |
| Optimize builds by processing issues sequentially  | stale-needs-author-feedback | 1m | $0.00 | medium |
| Optimize builds by processing issues sequentially  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Optimize builds by adding cache to the rebase proc | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
