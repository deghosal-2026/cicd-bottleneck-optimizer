# PR #68787 — refactor(core): implement ɵɵforeignComponent instruction

- **Repo:** angular/angular
- **Author:** leonsenft
- **State:** closed
- **Created:** 2026-05-18
- **CI runs:** 2

## Job Profiles

| Job | Duration | Status |
|---|---|---|
| devtools | 865s | pass |
| adev | 812s | pass |
| integration-tests | 578s | pass |
| test | 584s | pass |
| zone-js | 147s | pass |
| lint | 115s | pass |
| vscode-ng-language-service | 676s | pass |

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
| Optimize pull request labeling pipeline by adding  | pull_request_labels | 1m | $0.01 | low |
| Optimize post-approval changes pipeline by adding  | post_approval_changes | 1m | $0.01 | low |
| Optimize issue labeling pipeline by adding cache t | issue_labels | 1m | $0.01 | low |
| Optimize pull request labeling pipeline by using s | pull_request_labels | 1m | $0.00 | medium |
| Optimize post-approval changes pipeline by using s | post_approval_changes | 1m | $0.00 | medium |
| Optimize issue labeling pipeline by using serial_p | issue_labels | 1m | $0.00 | medium |
| Optimize code analysis pipeline by adding cache to | analysis | 1m | $0.01 | low |
| Optimize CI trigger pipeline by adding cache to re | trigger | 1m | $0.01 | low |
| Optimize assistant to the branch manager pipeline  | assistant_to_the_branch_manager | 1m | $0.01 | low |

**Total savings: 9 min/run**
