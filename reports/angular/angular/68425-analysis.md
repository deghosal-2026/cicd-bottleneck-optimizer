# PR #68425 — docs: add signal forms dynamic forms with json guide

- **Repo:** angular/angular
- **Author:** bencodezen
- **State:** open
- **Head SHA:** 6094f3eb865c
- **Created:** 2026-04-28
- **CI runs:** 2

## Job Profiles

| Job | Median | Status |
|---|---|---|
| test | 283s | pass |
| zone-js | 147s | pass |
| vscode-ng-language-service | 182s | pass |
| adev | 531s | pass |
| lint | 158s | pass |
| devtools | 309s | pass |
| integration-tests | 186s | pass |

## Bottlenecks Found

| Type | Job | Severity | Source |
|---|---|---|---|
| missing_cache | pull_request_labels | low | Rule |
| missing_cache | post_approval_changes | low | Rule |
| missing_cache | issue_labels | low | Rule |
| serial_parallel | pull_request_labels | low | Rule |
| serial_parallel | post_approval_changes | low | Rule |
| serial_parallel | issue_labels | low | Rule |
| missing_cache | analysis | low | Rule |
| missing_cache | trigger | low | Rule |
| missing_cache | assistant_to_the_branch_manager | low | Rule |

## Recommendations

| Optimization | Job | Saved | Cost/Run | Risk |
|---|---|---|---|---|
| Optimize build process by adding caching to pull r | pull_request_labels | 1m | $0.01 | low |
| Optimize build process by adding caching to post-a | post_approval_changes | 1m | $0.01 | low |
| Optimize build process by adding caching to issue  | issue_labels | 1m | $0.01 | low |
| Optimize build process by serializing and running  | pull_request_labels | 1m | $0.00 | medium |
| Optimize build process by serializing and running  | post_approval_changes | 1m | $0.00 | medium |
| Optimize build process by serializing and running  | issue_labels | 1m | $0.00 | medium |
| Optimize analysis phase by adding caching, saving  | analysis | 1m | $0.01 | low |
| Optimize CI trigger by adding caching, saving appr | trigger | 1m | $0.01 | low |
| Optimize interaction between CI and the branch man | assistant_to_the_branch_manager | 1m | $0.01 | low |

**Total estimated savings: 9 minutes per run**
