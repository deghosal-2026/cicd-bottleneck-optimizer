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
| oversized_context | analysis | medium | LLM |
| oversized_context | assistant_to_the_branch_manager | medium | LLM |
| oversized_context | trigger | medium | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Optimize analysis task by reducing oversized conte | analysis | 1m | $0.01 | low |
| Improve assistant_to_the_branch_manager task effic | assistant_to_the_branch_manager | 1m | $0.01 | low |
| Enhance trigger performance by reducing oversized  | trigger | 1m | $0.01 | low |

**Total savings: 3 min/run**
