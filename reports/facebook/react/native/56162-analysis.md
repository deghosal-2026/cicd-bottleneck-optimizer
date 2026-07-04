# PR #56162 — feat: calc support

- **Repo:** facebook/react/native
- **Author:** paradowstack
- **State:** open
- **Created:** 2026-03-19
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| check_code_changes | 9s | pass |
| lint | 121s | pass |
| set_release_type | 4s | pass |
| build_android | 1540s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1439s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 2072s | pass |
| prebuild_apple_dependencies / Prepare workspace | 33s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 30s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 27s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 22s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 24s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 26s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 27s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 20s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 33s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 28s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 24s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 19s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 25s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 24s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 27s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 28s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 27s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 110s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 125s | pass |
| build_fantom_runner | 429s | fail |
| build_js_types | 69s | pass |
| test_js (24) | 203s | pass |
| test_js (22.13.0) | 225s | pass |

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
| Add caching to the 'triage-issue' stage to save ap | triage-issue | 1m | $0.01 | low |
| Add caching to the 'act-on-label' stage to save ap | act-on-label | 1m | $0.01 | low |
| Implement serial execution for tasks in the 'triag | triage-issue | 1m | $0.00 | medium |
| Implement serial execution for tasks in the 'act-o | act-on-label | 1m | $0.00 | medium |
| Add caching to the 'stale' issue stage to save app | stale | 1m | $0.01 | low |
| Add caching to the 'stale-asc' issue stage to save | stale-asc | 1m | $0.01 | low |
| Add caching to the 'stale-needs-author-feedback' i | stale-needs-author-feedback | 1m | $0.01 | low |
| Add caching to the 'stale-needs-author-feedback-as | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Implement serial execution for tasks in the 'stale | stale | 1m | $0.00 | medium |
| Implement serial execution for tasks in the 'stale | stale-asc | 1m | $0.00 | medium |
| Implement serial execution for tasks in the 'stale | stale-needs-author-feedback | 1m | $0.00 | medium |
| Implement serial execution for tasks in the 'stale | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add caching to the 'rebase' stage to save approxim | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
