# Review Gates

Load after changed-file inventory is known. Complete every gate on the pinned review snapshot; load domain references only for changed behavior or unresolved contracts they cover.

Record material paths as `actor/input → guard/contract → outcomes → committed/pending effects → response/ack → recovery/consumer`. Do not replace tracing with a checklist.

Caps locate code, not complete coverage. If output hides relevant matches/blocks, narrow the next read; avoid unrelated repository-wide inspection.

## Gate 1: Critical Bugs And Correctness

Look for crashes, data loss, wrong branching/identifiers/defaults, invalid null assumptions, lost promises, races, stale state, duplicate processing, partial writes and user-visible regressions. Check concurrency and idempotency in affected requests, jobs and writes.

Trace changed data through affected callers/consumers and domain rules. Establish the changed path, concrete consequence and smallest correction.

### Enclosing Scopes And Cumulative Budgets

For changes to a helper or its invocation, result handling, error conversion, ordering, or retries, inspect the enclosing paths needed to establish behavior. Read unchanged callees when a changed caller depends on their outcomes. For helper-contract changes, identify affected existing callers, including callers outside the diff. Group equivalent callers; inspect distinct paths and the most constrained consumers rather than every unrelated helper or file.

When timeouts, retries, polling, or other bounded work change:

- Identify the effective deadline or resource limit of the enclosing test, request, transaction, or job. Check configuration, local overrides, and environment differences.
- Include unchanged work on the same reachable path: setup, sequential calls, retry attempts and backoff, navigation, and any hooks or cleanup charged to that budget by the framework. An individual wait being below the outer limit does not establish sufficient headroom.
- Model achievable elapsed time. Account for shared readiness, concurrent work, early failure, and separately budgeted operations. Do not add maxima across separate tests or assume every wait consumes its ceiling. Shared readiness avoids duplicate delay only while it remains satisfied.
- Support deadline-exhaustion findings with source establishing a feasible delay scenario, relevant timings, or a focused reproduction. A sum of configured ceilings is a risk signal, not proof. Name the affected caller, effective budget, changed behavior, and remaining work. If evidence is insufficient, state the uncertainty and the smallest useful check rather than presenting a guaranteed failure.
- Prefer a fix at the affected scope. Do not automatically raise global limits or weaken assertions to make a test pass.

### Evidence For The Claimed Fix

For reliability changes, check the claimed failure condition; healthy runs do not prove resilience. Distinguish inspection, author reports, observed CI and reproduction. Verify tested revision, runner discovery, paths/filters and real assertions: unawaited assertions, zero matching tests, mocks removing safeguards or fork CI on another tree can invalidate evidence. Identify skipped/cancelled/flaky/stale/lint-only checks. Documented manual/direct tests can supply evidence without package scripts; unexecuted source supplies intent. Use cheap relevant checks within authorization; disclose material gaps, not every unrun test as a blocker.

## Gate 2: Scalability And Performance

Inspect N+1 queries, unbounded work/fetches, broad filters, payload/memory growth, repeated calls, hot-path logs, cache/index drift and request fan-out. Preserve effective batching/caching/limits. Use `database-runtime.md` or `frontend.md` for affected query/render paths. Require realistic load and consequence.

## Gate 3: Failure Outcomes, Handling, And Observability

Inspect changed async boundaries, network/DB/file operations, jobs/webhooks, parsers/serializers, provider calls and user actions.

Establish correctness independently of conventions. Result objects, propagated rejections and caller-owned boundaries can all be correct; local catches or throws are not universally required.

### Required Operation-Outcome Trace

For each changed consequential operation, establish its actual success and failure contract and trace every material failure outcome to the caller's externally reported outcome. Trigger this for added/changed calls, result consumption, error conversion, ordering, retries, transaction participation, or completion signaling on required IO, mutations, account/session lifecycle, payments, jobs, webhooks, and dependent user actions.

Keep a compact internal record per distinct behavior, pinned to the reviewed head:

`call site → implementation/contract → outcomes → caller handling → completed/pending effects → response/commit/ack → evidence or uncertainty`

1. Identify the promised success condition and observable completion boundary. An intermediate database commit does not prove that the overall operation succeeded.
   Separate observed behavior, required behavior, and external consequence. Establish the applicable product, authorization, or provider contract before treating a difference as a defect: backend support need not be a UI requirement, and a request-controlled option need not violate authoritative policy. Local payload/state changes do not alone prove resulting provider state. If the violated requirement or claimed consequence depends on missing evidence, report that gap and limit the finding, severity, and blocking disposition to what is proved. A caveat below an unqualified finding does not correct an unsupported headline.
2. Read the actual callee and outcome-transforming wrappers, including unchanged dependencies, catches, and cleanup. Use the reviewed-version contract for external APIs when needed; names, signatures, and `await` alone are insufficient.
3. Enumerate reachable success, benign no-op, rejection/throw, fulfilled failure value, sentinel/null/zero result, partial batch outcome, and indeterminate completion after timeout. Use the actual discriminator; an object can be truthy while representing failure.
4. Follow each material outcome through the caller. Prove it is checked, forwarded into a compatible contract, or intentionally tolerated. A catch sees rejection/throw, not a fulfilled failure object. Logging alone neither recovers nor propagates failure.
5. Trace subsequent writes, events, success responses, queue acknowledgments, cache state, and checkpoints. Inspect already-completed effects and transaction participation; identify what a retry or concurrent invocation would repeat. Atomicity prevents partial commit; idempotency prevents duplicate effects on retry. Establish each protection that the path requires; neither substitutes for the other or automatically rolls back an external effect.
6. Check counterevidence: documented idempotent absence, genuinely optional work, a verified adapter/error boundary, or supported recovery. Establish that the promised outcome remains truthful. Comments and neighboring style express intent but do not prove it.
   A requested substep can be explicitly best effort while success promises only the primary effect. Adjudicate that contract using the caller, implementation, tests and consumer; do not redefine success as completion of every requested field. Dropping optional work is not false completion unless a required outcome or failure-reporting contract is violated. A locally proved omission plus an unknown remote consequence does not establish that missing requirement.
7. Report the changed call site, producer contract, plausible failure trigger, lost/incorrect handling, and concrete consequence. Separate a confirmed defect from uncertainty about how to fix it. Do not promote “if this unavailable helper rejects” into a confirmed finding merely because a catch logs and continues or a comment describes stale state. Establish the producer's failure channel and the consumer/recovery behavior needed for the claimed consequence; otherwise record that path as incomplete. A separate proven defect can coexist with this coverage gap.

Stop when the contract and handling boundary are established. Follow further wrappers only while outcomes or effects remain unresolved. Missing code, truncated reads, or an unknown critical dependency contract are coverage limitations, not proof of a defect or of safety. Do not demand a whole-repository call graph.

For example, `{ok:false}` fulfills a promise: an outer catch cannot catch it. Ignoring it after writing active state can report false success; globally throwing or returning failure after committed writes may cause unsafe retries. Check ordering and other callers first. Conversely, optional analytics can fail without invalidating a core write; documented already-absent deletion can succeed despite `deleted:false`; documented `Promise<void>` success needs no invented result check.

Check failure visibility: logger serialization/level, stable error codes, operation/entity/provider/request/job correlation and proven alert/audit/recovery contracts. Redact secrets, private payloads and unnecessary personal data, including raw provider messages. Records rolled back with business writes may not support recovery. Duplicate paging can be defective; separate correlated audit/operational records can be correct. Do not require one record per failure or universal sibling-log parity.

Check partial failure behavior:

- step 2 fails after step 1 succeeded;
- one item in a batch fails;
- retry runs twice;
- rollback or cleanup fails;
- frontend optimistic state must roll back;
- external API returns timeout, 4xx, 5xx, malformed response, or rate limit.

Apply the actual library semantics: native `fetch` can fulfill on HTTP errors; a 2xx body or SDK batch can still contain application failures; `allSettled` can contain rejected entries and fulfilled failure values. Check affected-row counts when a mutation is required, detached promises/async callbacks before completion, transaction callbacks that convert errors to normal returns, cleanup that masks the primary outcome, and timeout races that leave mutations running. Retry safety requires evidence of idempotency or reconciliation when the original outcome is unknown.

Resolve framework/runtime wrappers and rejection policy when detached failures depend on them; use `providers-and-timing.md`. Detachment alone proves neither termination nor safe optional work. Ignored results alone do not establish severity.

### Review Completion

Before a clean recommendation, complete material traces and reconcile findings. Deferred fixes do not erase blocking defects; unresolved material contracts require a limited/incomplete conclusion. Unrun unrelated tests need not block inspection-based review. No findings, green checks and agent agreement do not replace missing evidence.

## Gate 4: Cross-Repo Contract Drift And Existing-Code Inconsistency

Trace affected producers/consumers across supplied PRs: failure values versus throws, shapes, optionality/nullability, enums, pagination/sorting, errors, date/number serialization and routes. Check environment/flag defaults, migration/rollout order, mixed versions, rollback, workers and CI/deploy configuration. Separate regressions/newly exposed defects from unrelated pre-existing issues.

Use `artifacts-and-packages.md` for package/export/generated changes and `database-schema.md` for schema/model compatibility. Application expectations, consumer pins, migration lineage and applied schema are separate evidence; source/pins alone do not establish deployment.

Cite convention source and consequence: trusted policy, nearby pattern, helper/constant, registration, validation, error/log contract or release order. Siblings/frequency do not prove correctness. Use `structure.md` for responsibility growth or copied policy; require actual drift or an explicit convention violation.

### Multiline Braced Control Flow

For changed JavaScript/TypeScript control-flow bodies, require braces with the body on separate lines. Cover `if/else`, `for`/`for...of`/`for...in`, `while`/`do...while`, `switch`, and `try/catch/finally`; existing braces alone do not make a one-line body acceptable. Keep switch case statements on separate lines; do not require a new lexical block around each case unless needed. Apply this to statement-bodied callbacks/functions as well, without converting concise expression arrows or ternary expressions merely for this rule.

```js
if (rows.some((row) => !row.external_id || String(row.group_id) !== groupId)) {
  return null;
}
```

Report a violation in changed code as a style/convention finding, normally low priority; do not inflate it into a runtime defect or treat it as a material failure-contract gap. Fix only when edits are authorized and brace placement preserves the existing control flow, including dangling-else ownership and loop scope. Do not reformat unrelated existing code. Explicit user/repository exceptions take precedence.

Exact-head lint supplies evidence only if it enforces this complete multiline rule; ordinary brace-presence checks alone do not.

## Gate 5: Security And Trust Boundaries

Trace changed capabilities from actor through effective entry/middleware, identity, resource/tenant and guard to sensitive effect, including new effects behind unchanged routes. Inspect untrusted SQL/HTML/URL/path/model sinks, secrets and environment scope; load `security.md` for changed boundaries/privilege. Public endpoints can be intentional. Harmless mode-only changes are not access flaws; CI executable-bit changes remain reviewable. Prove reachability, failed control and consequence.

## Findings And Impact

Use `repo:path:line — concrete problem`, then trigger, consequence, evidence and smallest safe correction. Deduplicate root causes and order findings by concrete impact. Never emit priority codes such as P0, P1, P2, P3 or bracketed variants in chat, inline comments, or requested summaries. Separate confidence, blocking disposition and fix readiness; evidence gaps are not invented defects.

Serious security, data, money, availability or core-function failures ordinarily block readiness. Bounded correctness/operational failures depend on impact and release policy. Convention or minor maintainability issues are normally non-blocking; do not inflate them into runtime defects. Describe the actual consequence instead of assigning a severity badge.

Keep clean conclusions scoped to material investigated risks. Inline comments require verified current diff anchors; otherwise retain the finding in chat and explain the posting gap. Summaries require an explicit request; follow `review-actions.md`. A valid finding can still need a decision, authority or validation before correction.
