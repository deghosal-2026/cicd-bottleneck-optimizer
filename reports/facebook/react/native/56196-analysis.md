# PR #56196 — Do not synchronize on java.lang.Boolean.

- **Repo:** facebook/react/native
- **Author:** Yqwed
- **State:** closed
- **Created:** 2026-03-23
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| validate_cxx_api_snapshots | 170s | pass |

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
| Add caching to the 'applyNeedsAttentionLabel' stag | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Add caching to the 'triage-issue' stage to reduce  | triage-issue | 1m | $0.01 | low |
| Add caching to the 'act-on-label' stage to reduce  | act-on-label | 1m | $0.01 | low |
| Optimize the parallel execution of tasks in the 't | triage-issue | 1m | $0.00 | medium |
| Optimize the parallel execution of tasks in the 'a | act-on-label | 1m | $0.00 | medium |
| Add caching to the 'stale' stage to reduce build t | stale | 1m | $0.01 | low |
| Add caching to the 'stale-asc' stage to reduce bui | stale-asc | 1m | $0.01 | low |
| Add caching to the 'stale-needs-author-feedback' s | stale-needs-author-feedback | 1m | $0.01 | low |
| Add caching to the 'stale-needs-author-feedback-as | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Optimize the serial and parallel execution of task | stale | 1m | $0.00 | medium |
| Optimize the serial and parallel execution of task | stale-asc | 1m | $0.00 | medium |
| Optimize the serial and parallel execution of task | stale-needs-author-feedback | 1m | $0.00 | medium |
| Optimize the serial and parallel execution of task | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add caching to the 'rebase' stage to reduce build  | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
