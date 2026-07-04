# PR #56766 — Add support for case-sensitive OpenType feature

- **Repo:** facebook/react/native
- **Author:** ashfurrow
- **State:** open
- **Created:** 2026-05-11
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| lint | 124s | pass |
| set_release_type | 3s | pass |
| check_code_changes | 10s | pass |
| test_ios_rntester_dynamic_frameworks (Debug) | 1401s | pass |
| test_ios_rntester_dynamic_frameworks (Release) | 1516s | pass |
| build_android | 1279s | pass |
| prebuild_apple_dependencies / Prepare workspace | 80s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos) | 183s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, macos) | 112s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios-simulator) | 150s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, mac-catalyst) | 172s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios-simulator) | 123s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros) | 107s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, macos) | 194s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, tvos-simulator) | 140s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, mac-catalyst) | 152s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, xros-simulator) | 195s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros-simulator) | 124s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, xros) | 110s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos-simulator) | 123s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Debug, ios) | 163s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, tvos) | 167s | pass |
| prebuild_apple_dependencies / Build Apple Slice (Release, ios) | 139s | pass |
| build_fantom_runner | 672s | pass |
| test_js (24) | 209s | pass |
| test_js (20.19.4) | 224s | pass |
| test_js (22) | 210s | pass |
| build_js_types | 52s | pass |
| prebuild_apple_dependencies / Prepare XCFramework (Debug) | 116s | pass |

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
| Optimize the CI/CD pipeline by implementing a cach | applyNeedsAttentionLabel | 1m | $0.01 | low |
| Implement a strategy to handle issues more efficie | triage-issue | 1m | $0.01 | medium |
| Enhance the processing of pull requests by impleme | act-on-label | 1m | $0.01 | low |
| Introduce a serial execution pattern for tasks in  | triage-issue | 1m | $0.00 | medium |
| Apply a serial execution pattern on the act-on-lab | act-on-label | 1m | $0.00 | medium |
| Implement a cache mechanism for stale issues, aimi | stale | 1m | $0.01 | low |
| Enhance the handling of stale issues by applying a | stale-asc | 1m | $0.01 | low |
| Implement a cache mechanism for issues that requir | stale-needs-author-feedback | 1m | $0.01 | low |
| Apply a cache mechanism for issues that require au | stale-needs-author-feedback-asc | 1m | $0.01 | low |
| Introduce a serial execution pattern specifically  | stale | 1m | $0.00 | medium |
| Enhance the handling of issues that need ASC calcu | stale-asc | 1m | $0.00 | medium |
| Implement a cache mechanism for issues requiring r | stale-needs-author-feedback | 1m | $0.00 | low |
| Run 'stale-needs-author-feedback-asc' in parallel  | stale-needs-author-feedback-asc | 1m | $0.00 | medium |
| Add cache directive to 'rebase' to avoid re-downlo | rebase | 1m | $0.01 | low |

**Total savings: 14 min/run**
