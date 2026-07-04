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
| oversized_context | analysis | low | LLM |
| oversized_context | assistant_to_the_branch_manager | low | LLM |
| oversized_context | trigger | low | LLM |

## Recommendations

| Opt | Job | Saved | Cost | Risk |
|---|---|---|---|---|
| Add .dockerignore to 'analysis' to exclude unneces | analysis | 1m | $0.01 | low |
| Add .dockerignore to 'assistant_to_the_branch_mana | assistant_to_the_branch_manager | 1m | $0.01 | low |
| Add .dockerignore to 'trigger' to exclude unnecess | trigger | 1m | $0.01 | low |

**Total savings: 3 min/run**
