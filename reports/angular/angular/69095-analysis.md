# PR #69095 — build: update cross-repo angular dependencies (22.0.x)

- **Repo:** angular/angular
- **Author:** angular-robot
- **State:** closed
- **Created:** 2026-06-02
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| zone-js | 175s | pass |
| test | 510s | pass |
| devtools | 701s | pass |
| lint | 142s | pass |
| adev | 624s | pass |
| integration-tests | 503s | pass |
| vscode-ng-language-service | 567s | pass |

## Bottlenecks

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

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Optimize build pipeline by adding cache for pull r | pull_request_labels | 1m | $0.01 | low |
| Optimize build pipeline by adding cache for post-a | post_approval_changes | 1m | $0.01 | low |
| Optimize build pipeline by adding cache for issue  | issue_labels | 1m | $0.01 | low |
| Optimize build pipeline by processing pull request | pull_request_labels | 1m | $0.00 | medium |
| Optimize build pipeline by processing post-approva | post_approval_changes | 1m | $0.00 | medium |
| Optimize build pipeline by processing issue labeli | issue_labels | 1m | $0.00 | medium |
| Optimize build pipeline by adding cache for analys | analysis | 1m | $0.01 | low |
| Optimize build pipeline by adding cache for trigge | trigger | 1m | $0.01 | low |
| Optimize build pipeline by adding cache for intera | assistant_to_the_branch_manager | 1m | $0.01 | low |

**Total savings: 9 min/run**
