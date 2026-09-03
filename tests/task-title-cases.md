# Task Title Cases

These fixtures document the required deterministic title behavior. Goal inference remains semantic and must be conservative.

| Case | Inputs | Expected title |
| --- | --- | --- |
| Single PR with explicit goal | One PR; user says the goal is add login authentication | `PR Review - add login authentication` |
| Operational wording is not the goal | One PR; user requests a title-only smoke test but states no implementation goal; PR title is `Allow plugin installs for backend dependency IDs` | `PR Review - Allow plugin installs for backend dependency IDs` |
| Two connected PRs | Two distinct PRs with a confidently shared authentication goal | `2 PRs Review - add login authentication` |
| Five connected PRs | Five distinct PRs with a confidently shared billing migration goal | `5 PRs Review - migrate billing webhooks` |
| Duplicate URL | The same PR URL supplied twice | A single-PR title beginning with `PR Review -` |
| Hyphenated card fallback | First PR title is `VD-102 - add auth in login`; no explicit or inferred goal | `PR Review - add auth in login` |
| Colon card fallback | First PR title is `VD-102: add auth in login`; no explicit or inferred goal | `PR Review - add auth in login` |
| Bracketed card fallback | First PR title is `[VD-102] add auth in login`; no explicit or inferred goal | `PR Review - add auth in login` |
| Internal card text | First PR title is `Add auth for VD-102 login`; no explicit or inferred goal | `PR Review - Add auth for VD-102 login` |
| Card only | First PR title is `VD-102`; no explicit or inferred goal | `PR Review - VD-102` |
| Unrelated multi-PR set | Two distinct PRs with no defensible shared goal; first title is `VD-102 - add auth in login` | `2 PRs Review - add auth in login` |
| Missing usable title | No explicit goal, no inferable goal, and no usable PR title | Leave the current task title unchanged |
| Rename tool unavailable | Any otherwise valid case | Continue the workflow without failing |
