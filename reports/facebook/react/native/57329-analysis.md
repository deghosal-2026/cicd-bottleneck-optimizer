# PR #57329 — Skip `RawPropsParser::prepare<T>()` when the iterator-setter path is active (#57329)

- **Repo:** facebook/react/native
- **Author:** javache
- **State:** open
- **Created:** 2026-06-24
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| lint | 130s | pass |
| check_code_changes | 8s | pass |
| set_release_type | 3s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1511s | pass |
| build_android | 2240s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 1507s | pass |
| prebuild_apple_dependencies / Prepare workspace | 108s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 140s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 146s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 214s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 182s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 210s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 176s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 185s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 124s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 119s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 191s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 200s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 147s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 133s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 136s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 229s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 147s | pass |
| test_js (22.13.0) | 217s | pass |
| build_js_types | 65s | pass |
| build_fantom_runner | 607s | pass |
| test_js (24) | 204s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 104s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Release) | 120s | pass |

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
| Enable cache for Terraform apply to reduce build t | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Enable cache for triage issue processing to reduce | triage-issue | 1m | $0.01 | low |
| Enable cache for action on label to reduce build t | act-on-label | 1m | $0.01 | low |
| Optimize triage-issue processing by serializing ta | triage-issue | 1m | $0.00 | medium |
| Optimize act-on-label processing by serializing ta | act-on-label | 1m | $0.00 | medium |
| Enable cache for stale issues to reduce build time | stale | 1m | $0.01 | low |
| Enable cache for stale issues with ASCension to re | stale-asc | 1m | $0.01 | low |
| Enable cache for issues needing author feedback to | stale-needs-author-feedback | 1m | $0.01 | low |
| Enable cache for issues needing author feedback wi | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Optimize stale issues processing by serializing ta | stale | 1m | $0.00 | medium |
| Optimize stale issues with ASCension processing by | stale-asc | 1m | $0.00 | medium |
| Optimize issues needing author feedback processing | stale-needs-author-feedback | 1m | $0.00 | medium |
| Optimize issues needing author feedback with ASCen | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Enable cache for rebasing to reduce build time by  | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
