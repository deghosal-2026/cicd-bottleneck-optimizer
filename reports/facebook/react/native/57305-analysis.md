# PR #57305 — refactor(iOS): include resources like bundles into the precompiled XCFrameworks

- **Repo:** facebook/react/native
- **Author:** chrfalch
- **State:** open
- **Created:** 2026-06-22
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| check_code_changes | 8s | pass |
| lint | 121s | pass |
| set_release_type | 3s | pass |
| build_android | 591s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1770s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 1917s | pass |
| prebuild_apple_dependencies / Prepare workspace | 76s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 181s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 154s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 158s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 96s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 126s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 124s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 139s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 110s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 118s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 132s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 94s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 104s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 176s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 105s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 119s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 132s | pass |
| test_js (22.13.0) | 213s | pass |
| build_js_types | 72s | pass |
| test_js (24) | 213s | pass |
| build_fantom_runner | 531s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 80s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 142s | pass |

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
| Optimize build pipeline by implementing cache for  | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Optimize triage-issue task by implementing cache f | triage-issue | 1m | $0.01 | low |
| Optimize act-on-label task by implementing cache f | act-on-label | 1m | $0.01 | low |
| Enhance triage-issue task by adopting a serial-par | triage-issue | 1m | $0.00 | medium |
| Enhance act-on-label task by adopting a serial-par | act-on-label | 1m | $0.00 | medium |
| Optimize build pipeline by implementing cache for  | stale | 1m | $0.01 | low |
| Optimize stale-asc task by implementing cache for  | stale-asc | 1m | $0.01 | low |
| Optimize stale-needs-author-feedback task by imple | stale-needs-author-feedback | 1m | $0.01 | low |
| Optimize stale-needs-author-feedback-asc task by i | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Enhance stale task by adopting a serial-parallel e | stale | 1m | $0.00 | medium |
| Enhance stale-asc task by adopting a serial-parall | stale-asc | 1m | $0.00 | medium |
| Enhance stale-needs-author-feedback task by adopti | stale-needs-author-feedback | 1m | $0.00 | medium |
| Enhance stale-needs-author-feedback-asc task by ad | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Optimize rebase task by implementing cache for mis | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
