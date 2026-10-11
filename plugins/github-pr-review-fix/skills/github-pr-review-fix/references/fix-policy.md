# Conservative Local Fix Policy

Load only before authorized edits. Review broadly, fix narrowly; independently honor edit/stage/commit/push/comment/validation permissions from the action ledger.

## Finding Validity And Fix Readiness

Validate each finding from the changed path, actual contract, credible trigger, and concrete consequence: confirmed, rejected with counterevidence, or unresolved. Separately classify its correction as ready, decision-dependent, or outside authorized scope. A confirmed defect remains reportable when its fix cannot safely be chosen, validated, or delivered.

Ready requires known intended behavior, action-specific authority, coherent affected contracts, and adequate verification for the risk. Nearby style, an agent vote, and “reviewed by inspection” alone do not establish runtime safety. Preserve standing session permission; do not demand magic category wording or repeat granted authorization. A missing product/security/data decision or prohibited/unavailable required check blocks readiness, not finding validity. Continue independent authorized work and preserve a concrete proposed patch where appropriate.

## Impact And Verification

Public API, schema/data/migrations, security/privacy/billing, dependencies/lockfiles, generated artifacts, and alert semantics require explicit impact analysis. Inspect affected callers, consumers, rollout/rollback constraints, and authoritative provenance; load the triggered domain reference. These categories do not automatically require renewed approval when behavior, scope, and validation are already authorized. Reading a dependency does not add its repository to fix scope.

Returned-failure/throw conversions, global throw helpers, fail-open/fail-closed changes, mutation reordering, and retries alter behavioral contracts even without signature changes. Trace completed effects and recovery before applying them. A late caller-side error after committed writes may duplicate effects on retry. Match actual logging/alert/correlation/redaction contracts; multiple causal-stage or audit records are not automatically duplicate logging, and copying a sibling can reproduce its defect.

Choose the cheapest meaningful authorized check for the changed behavior. Required runtime validation must exercise the actual path with the established runner; do not substitute extracted source slicing/re-evaluation. Text assertions can be appropriate for generators, codemods, or parsers. Reuse existing tests/factories, avoid oversized scaffolds or implementation-mirroring tests, and do not require irrelevant full suites. A requested test edit can remain unrun under a no-execution constraint, but must be labeled unrun and cannot satisfy a required delivery check.

If required validation is prohibited or unavailable, retain the proposed patch/finding and state the exact gap. Inspection cannot convert an unvalidated consequential correction into a ready fix. Report checks actually run, their revision, and limitations; never claim verification merely from reading code.

## Surgical Editing

Before non-trivial edits, summarize confirmed findings/readiness, verifier status, intended files, and required validation. Use a suitable isolated worktree pinned to the reviewed head; preserve unrelated work and ordinary checkouts. Every changed line must address a confirmed finding. Prefer existing patterns, direct control flow, strong types, and the smallest correction. No broad extraction, speculative validation layers, schema/artifact churn, unrelated cleanup, or new abstraction to satisfy a checklist. Preserve the multiline-braces rule from `review-gates.md`.

After edits, inspect status and the final diff, re-trace effects/failure/retry behavior, rerun only invalidated verification, and record validation against the actual final revision. Preserve confirmed deferred findings. Report changed behavior/files, checks run or skipped with reasons, remaining compile/runtime risk, and specific unresolved decisions.

## Conservative Scope

For a general local-fix request, prefer small, reversible changes with known intent and sufficient evidence: a wrong variable, missing import/return/await, narrow null handling, or local cleanup can qualify only after tracing the actual affected path. No example is automatically safe. Broader contract or coordinated changes require clear existing scope and sufficient validation; otherwise retain a decision-dependent proposal. Do not ask again when the user already authorized that exact work.

Stage, commit, push, execute validation, or post comments only within separately granted authority. No merge, approval, request-changes, close, labels, or other publication is implied by a fix request. Apply workflow drift/ownership rules before final reporting or cleanup.
