# Task Title Cases

These fixtures preserve the deterministic first-title fallback; relationship clustering does not invent an unrelated-count suffix. Goal inference remains conservative. All ticket prefixes are synthetic. Supply only Inputs and withhold Expected Assessments. These are title-only cases; do not execute review or delivery.

## Inputs

### TT01

Single PR with explicit goal. One PR; user says the goal is add login authentication.

### TT02

Operational wording is not the goal. One PR; user requests a title-only smoke test but states no implementation goal; PR title is `Allow plugin installs for backend dependency IDs`.

### TT03

Two connected PRs. Two distinct PRs with the explicit shared goal `add login authentication`.

### TT04

Five connected PRs. Five distinct PRs with the explicit shared goal `migrate billing webhooks`.

### TT05

Duplicate URL. The same PR URL is supplied twice; no explicit/common goal; PR title is `Improve cache invalidation`.

### TT06

Hyphenated card fallback. One PR; title is `ABC-102 - add auth in login`; no explicit or inferred goal.

### TT07

Colon card fallback. One PR; title is `ABC-102: add auth in login`; no explicit or inferred goal.

### TT08

Bracketed card fallback. One PR; title is `[ABC-102] add auth in login`; no explicit or inferred goal.

### TT09

Internal card text. One PR; title is `Add auth for ABC-102 login`; no explicit or inferred goal.

### TT10

Card only. One PR; title is `ABC-102`; no explicit or inferred goal.

### TT11

Unrelated multi-PR set. Two distinct PRs with no defensible shared goal; first title is `ABC-102 - add auth in login`.

### TT12

Missing usable title. One supplied PR has no usable PR title; the user gives no explicit goal and available relationship context supports no inferred goal. Current task title is `Existing review`.

### TT13

Rename tool unavailable. One PR; title is `Improve cache invalidation`, no explicit/common goal. The supported rename tool is unavailable; the user requested a normal review.

### TT14

Pipe separator. One PR; title is `ABC-12 | Add CSV export`; no explicit/inferred goal.

### TT15

Double pipe. One PR; title is `ABC-12 || Add CSV export`; no explicit/inferred goal.

### TT16

Multiple keys. One PR; title is `ABC-12 / ABC-13: Add CSV export`; no explicit/inferred goal.

### TT17

Suffixed key. One PR; title is `ABC-12-b || Add CSV export`; no explicit/inferred goal.

### TT18

Lowercase is not a key. One PR; title is `axios-404-error`; no explicit/inferred goal.

### TT19

Two clusters with first-title fallback. Three distinct PRs; first title `ABC-12 - Add CSV export`. The first two implement CSV export and share an interface; the third changes independent docs with no relationship evidence. No common goal spans all three and user supplies no overriding goal.

### TT20

Connected, no inferable common goal. Two distinct PRs linked by an explicit body reference; first title is `ABC-102 - add auth in login`. Link text does not establish an inferable common implementation goal, and the user supplies none.

## Expected Assessments (Withhold During Review)

| Case | Expected title or disposition |
| --- | --- |
| TT01 | `PR Review - add login authentication` |
| TT02 | `PR Review - Allow plugin installs for backend dependency IDs` |
| TT03 | `2 PRs Review - add login authentication` |
| TT04 | `5 PRs Review - migrate billing webhooks` |
| TT05 | `PR Review - Improve cache invalidation` |
| TT06 | `PR Review - add auth in login` |
| TT07 | `PR Review - add auth in login` |
| TT08 | `PR Review - add auth in login` |
| TT09 | `PR Review - Add auth for ABC-102 login` |
| TT10 | `PR Review - ABC-102` |
| TT11 | `2 PRs Review - add auth in login` |
| TT12 | Leave current task title `Existing review` unchanged. |
| TT13 | Continue the workflow without failing; do not claim a successful rename. |
| TT14 | `PR Review - Add CSV export` |
| TT15 | `PR Review - Add CSV export` |
| TT16 | `PR Review - Add CSV export` |
| TT17 | `PR Review - Add CSV export` |
| TT18 | `PR Review - axios-404-error` |
| TT19 | `3 PRs Review - Add CSV export` |
| TT20 | `2 PRs Review - add auth in login` |
