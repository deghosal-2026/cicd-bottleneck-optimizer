# PR #57332 — feat(iOS) swiftpm support in iOS

- **Repo:** facebook/react/native
- **Author:** chrfalch
- **State:** open
- **Created:** 2026-06-25
- **CI runs:** 3

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| lint | 125s | pass |
| check_code_changes | 10s | pass |
| set_release_type | 2s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1744s | pass |
| build_android | 597s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 1375s | pass |
| prebuild_apple_dependencies / Prepare workspace | 137s | pass |
| test_js (24) | 214s | pass |
| test_js (22.13.0) | 177s | pass |
| build_js_types | 67s | pass |
| build_fantom_runner | 710s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 120s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 109s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 182s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 170s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 150s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 112s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 176s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 184s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 175s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 117s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 196s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 156s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 140s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 104s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 92s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 131s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 110s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 109s | pass |

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
| Optimize the caching mechanism for Terraform code  | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Implement a strategy to handle issues by applying  | triage-issue | 1m | $0.01 | low |
| Enhance the workflow for triaging issues by applyi | act-on-label | 1m | $0.01 | medium |
| Cache the results of stale checks to avoid recompu | triage-issue | 1m | $0.00 | low |
| Use a serial and parallel approach to handle issue | act-on-label | 1m | $0.00 | medium |
| Optimize the caching mechanism for repository reba | stale | 1m | $0.01 | low |
| Add cache directive to 'stale-asc' to avoid re-dow | stale-asc | 1m | $0.01 | low |
| Add cache directive to 'stale-needs-author-feedbac | stale-needs-author-feedback | 1m | $0.01 | low |
| Add cache directive to 'stale-needs-author-feedbac | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Run 'stale' in parallel with other independent job | stale | 1m | $0.00 | medium |
| Run 'stale-asc' in parallel with other independent | stale-asc | 1m | $0.00 | medium |
| Run 'stale-needs-author-feedback' in parallel with | stale-needs-author-feedback | 1m | $0.00 | medium |
| Run 'stale-needs-author-feedback-asc' in parallel  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add cache directive to 'rebase' to avoid re-downlo | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
