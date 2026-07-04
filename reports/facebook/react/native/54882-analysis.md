# PR #54882 — Remove ViewAtIndex and manageChildren API from legacy architecture

- **Repo:** facebook/react/native
- **Author:** mdvacca
- **State:** closed
- **Created:** 2025-12-13
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| set_release_type | 3s | pass |
| lint | 173s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1744s | pass |
| test_js (20.19.4) | 220s | pass |
| test_js (24) | 212s | pass |
| test_js (22) | 225s | pass |
| prebuild_apple_dependencies / Prepare workspace | 32s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 343s | fail |
| build_android | 667s | pass |
| run_fantom_tests | 654s | fail |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 21s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 21s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 19s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 23s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 23s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 23s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 27s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 21s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 22s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 29s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 23s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 21s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 24s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 24s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 21s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 20s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 159s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 103s | pass |
| prebuild_react_native_core / build-rn-slice (Release, ios-simulator) | 1236s | pass |
| prebuild_react_native_core / build-rn-slice (Release, ios) | 847s | pass |

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
| Add caching to the applyNeedsAttentionLabel step t | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Add caching to the triage-issue step to save time  | triage-issue | 1m | $0.01 | low |
| Add caching to the act-on-label step to save time  | act-on-label | 1m | $0.01 | low |
| Optimize the triage-issue step to run tasks serial | triage-issue | 1m | $0.00 | medium |
| Optimize the act-on-label step to run tasks serial | act-on-label | 1m | $0.00 | medium |
| Add caching to the stale step to save time on buil | stale | 1m | $0.01 | low |
| Add caching to the stale-asc step to save time on  | stale-asc | 1m | $0.01 | low |
| Add caching to the stale-needs-author-feedback ste | stale-needs-author-feedback | 1m | $0.01 | low |
| Add caching to the stale-needs-author-feedback-asc | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Optimize the stale step to run tasks serially and  | stale | 1m | $0.00 | medium |
| Optimize the stale-asc step to run tasks serially  | stale-asc | 1m | $0.00 | medium |
| Optimize the stale-needs-author-feedback step to r | stale-needs-author-feedback | 1m | $0.00 | medium |
| Optimize the stale-needs-author-feedback-asc step  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add caching to the rebase step to save time on bui | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
