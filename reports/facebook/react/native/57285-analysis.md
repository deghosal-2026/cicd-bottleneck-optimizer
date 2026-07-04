# PR #57285 — refactor(ios): remove clang VFS overlay, resolve headers via new ReactNativeHeaders framework

- **Repo:** facebook/react/native
- **Author:** chrfalch
- **State:** open
- **Created:** 2026-06-19
- **CI runs:** 1

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| check_code_changes | 10s | pass |
| set_release_type | 3s | pass |
| lint | 124s | pass |
| build_android | 578s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 1561s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 110s | fail |
| prebuild_apple_dependencies / Prepare workspace | 76s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 169s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 106s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 201s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 112s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 148s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 195s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 142s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 152s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 116s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 130s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 95s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 108s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 113s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 120s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 178s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 186s | pass |
| build_fantom_runner | 482s | pass |
| test_js (22.13.0) | 216s | pass |
| build_js_types | 67s | pass |
| test_js (24) | 211s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 89s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 109s | pass |

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
| Optimize build pipeline by adding cache to reduce  | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Improve the efficiency of issue triage by implemen | triage-issue | 1m | $0.01 | low |
| Enhance the automation of actions on pull requests | act-on-label | 1m | $0.01 | low |
| Implement a serial execution pattern for tasks in  | triage-issue | 1m | $0.00 | medium |
| Adopt a similar serial pattern for actions in the  | act-on-label | 1m | $0.00 | medium |
| Introduce a missing cache strategy to streamline t | stale | 1m | $0.01 | low |
| Implement a caching mechanism for issues marked as | stale-asc | 1m | $0.01 | low |
| Enhance the workflow for issues requiring author f | stale-needs-author-feedback | 1m | $0.01 | low |
| Implement a serial execution pattern for tasks rel | stale-needs-author-feedback-asc | 1m | $0.01 | medium |
| Introduce a caching mechanism for issues marked as | stale | 1m | $0.00 | medium |
| Add a missing cache mechanism to the process of re | stale-asc | 1m | $0.00 | low |
| Run 'stale-needs-author-feedback' in parallel with | stale-needs-author-feedback | 1m | $0.00 | medium |
| Run 'stale-needs-author-feedback-asc' in parallel  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add cache directive to 'rebase' to avoid re-downlo | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
