# Review Gates

Load this reference after changed-file inventory is known. Use it to complete the review pass; do not block branch alignment or first changed-hunk inspection on this file.

Run all four gates when completing review. Do not collapse them into a shallow checklist.

Use capped searches to locate code, not to establish complete coverage. If a cap hides relevant matches or an enclosing block, narrow the follow-up read before drawing a conclusion; do not expand into unrelated repository-wide inspection.

## Gate 1: Critical Bugs And Correctness

Look for concrete runtime bugs:

- crashes and data loss;
- incorrect branching, wrong identifiers, and incorrect defaults;
- broken async flow, missing `await`, missing `return`, and lost promises;
- race conditions, stale state, duplicate processing, and state corruption;
- partial writes and missing rollback;
- invalid null/undefined assumptions;
- user-visible regressions;
- broken concurrency or idempotency in handlers, jobs, webhooks, retries, queues, imports, exports, and DB writes.

Trace changed data through callers and consumers, not only the touched function. Verify new conditions against existing domain rules and sibling code paths. A finding must include the behavior risk, changed code path, and smallest concrete fix.

### Enclosing Scopes And Cumulative Budgets

For changes to a helper or its invocation, result handling, error conversion, ordering, or retries, inspect the enclosing paths needed to establish behavior. Read unchanged callees when a changed caller depends on their outcomes. For helper-contract changes, identify affected existing callers, including callers outside the diff. Group equivalent callers; inspect distinct paths and the most constrained consumers rather than every unrelated helper or file.

When timeouts, retries, polling, or other bounded work change:

- Identify the effective deadline or resource limit of the enclosing test, request, transaction, or job. Check configuration, local overrides, and environment differences.
- Include unchanged work on the same reachable path: setup, sequential calls, retry attempts and backoff, navigation, and any hooks or cleanup charged to that budget by the framework. An individual wait being below the outer limit does not establish sufficient headroom.
- Model achievable elapsed time. Account for shared readiness, concurrent work, early failure, and separately budgeted operations. Do not add maxima across separate tests or assume every wait consumes its ceiling. Shared readiness avoids duplicate delay only while it remains satisfied.
- Support deadline-exhaustion findings with source establishing a feasible delay scenario, relevant timings, or a focused reproduction. A sum of configured ceilings is a risk signal, not proof. Name the affected caller, effective budget, changed behavior, and remaining work. If evidence is insufficient, state the uncertainty and the smallest useful check rather than presenting a guaranteed failure.
- Prefer a fix at the affected scope. Do not automatically raise global limits or weaken assertions to make a test pass.

### Evidence For The Claimed Fix

For reliability or resilience changes, identify the failure condition the PR claims to handle and check whether the affected path can now handle it. Healthy runs and green unrelated checks do not demonstrate behavior under that condition. Distinguish source inspection, author-reported results, observed CI coverage, and reproduced behavior. Use the cheapest relevant evidence; this does not authorize running tests or external operations otherwise prohibited by the user or skill. Before recommending approval, disclose any material evidence gap without treating every unrun test as a blocker.

## Gate 2: Scalability And Performance

Search for new load-sensitive risks:

- N+1 queries;
- unbounded loops, unpaginated fetches, broad DB filters, or missing limits;
- large in-memory transforms or payload growth;
- repeated network calls;
- hot-path logging;
- inefficient cache invalidation or cache-key drift;
- missing indexes for new query paths;
- fan-out work added to request paths.

Compare new data access with existing repository conventions. Check whether pagination, batching, caching, debounce/throttle, background processing, or query limits already exist nearby and should be preserved.

For frontend changes, inspect render loops, memoization-sensitive paths, expensive selectors, repeated API calls, bundle-affecting imports, and large table/list behavior.

Only report performance findings that matter under realistic load. Explain the load path and impact.

## Gate 3: Failure Outcomes, Handling, And Observability

Inspect every changed:

- async boundary;
- network call;
- DB call;
- file operation;
- queue/job handler;
- webhook handler;
- parser/serializer;
- payment or external API call;
- user-triggered action.

Follow nearby representation conventions, but establish correctness independently: an existing pattern can also discard failures. A result object, propagated rejection, or caller-owned error boundary can be correct; do not require a local catch or a thrown error everywhere.

### Required Operation-Outcome Trace

For each changed consequential operation, establish its actual success and failure contract and trace every material failure outcome to the caller's externally reported outcome. Trigger this for added/changed calls, result consumption, error conversion, ordering, retries, transaction participation, or completion signaling on required IO, mutations, account/session lifecycle, payments, jobs, webhooks, and dependent user actions.

Keep a compact internal record per distinct behavior, pinned to the reviewed head:

`call site → implementation/contract → outcomes → caller handling → completed/pending effects → response/commit/ack → evidence or uncertainty`

1. Identify the promised success condition and observable completion boundary. An intermediate database commit does not prove that the overall operation succeeded.
2. Read the actual callee and outcome-transforming wrappers, including unchanged dependencies, catches, and cleanup. Use the installed-version contract for external APIs when needed; names, signatures, and `await` alone are insufficient.
3. Enumerate reachable success, benign no-op, rejection/throw, fulfilled failure value, sentinel/null/zero result, partial batch outcome, and indeterminate completion after timeout. Use the actual discriminator; an object can be truthy while representing failure.
4. Follow each material outcome through the caller. Prove it is checked, forwarded into a compatible contract, or intentionally tolerated. A catch sees rejection/throw, not a fulfilled failure object. Logging alone neither recovers nor propagates failure.
5. Trace subsequent writes, events, success responses, queue acknowledgments, cache state, and checkpoints. Inspect already-completed effects and transaction participation; identify what a retry or concurrent invocation would repeat. Atomicity prevents partial commit; idempotency prevents duplicate effects on retry. Establish each protection that the path requires; neither substitutes for the other or automatically rolls back an external effect.
6. Check counterevidence: documented idempotent absence, genuinely optional work, a verified adapter/error boundary, or supported recovery. Establish that the promised outcome remains truthful. Comments and neighboring style express intent but do not prove it.
7. Report the changed call site, producer contract, plausible failure trigger, lost/incorrect handling, and concrete consequence. Separate a confirmed defect from uncertainty about how to fix it. Do not promote “if this unavailable helper rejects” into a confirmed finding merely because a catch logs and continues or a comment describes stale state. Establish the producer's failure channel and the consumer/recovery behavior needed for the claimed consequence; otherwise record that path as incomplete. A separate proven defect can coexist with this coverage gap.

Stop when the contract and handling boundary are established. Follow further wrappers only while outcomes or effects remain unresolved. Missing code, truncated reads, or an unknown critical dependency contract are coverage limitations, not proof of a defect or of safety. Do not demand a whole-repository call graph.

For example, a helper that catches a provider error and returns `{ok:false}` fulfills its promise. A caller that ignores it after writing active state can still report success; adding an outer catch does not help. Making the helper throw globally or merely returning failure after committed writes may cause unsafe retries. Inspect other callers and ordering before proposing a correction.

Conversely, optional analytics failure may be logged after a successful core write without invalidating that write. An exact documented already-absent result may be successful deletion; `deleted:false` does not necessarily mean failure. A documented `Promise<void>` success needs no invented result-object validation.

Check that failures are not swallowed silently and do not return misleading success states. Ensure logging exists where failures would otherwise be invisible. Logging should include useful context such as operation, entity identifier, external provider, request ID, job ID, and the error object. Do not log secrets, tokens, credentials, private payloads, or unnecessary PII.

Check partial failure behavior:

- step 2 fails after step 1 succeeded;
- one item in a batch fails;
- retry runs twice;
- rollback or cleanup fails;
- frontend optimistic state must roll back;
- external API returns timeout, 4xx, 5xx, malformed response, or rate limit.

Apply the actual library semantics: native `fetch` can fulfill on HTTP errors; a 2xx body or SDK batch can still contain application failures; `allSettled` can contain rejected entries and fulfilled failure values. Check affected-row counts when a mutation is required, detached promises/async callbacks before completion, transaction callbacks that convert errors to normal returns, cleanup that masks the primary outcome, and timeout races that leave mutations running. Retry safety requires evidence of idempotency or reconciliation when the original outcome is unknown.

A finding must state the missing failure mode, supporting contract and consequence, and fix readiness under the current validation/authorization constraints. Do not inflate severity solely because a return value is ignored.

### Review Completion

Before a clean recommendation, complete the material operation-outcome traces and reconcile confirmed findings. A confirmed blocking defect remains reportable when its fix is deferred; an unresolved material contract requires a limited/incomplete conclusion. Distinguish these from unrun unrelated tests, which do not automatically block an inspection-based review. No finding in inspected scope is not proof of correctness, and green checks or agent agreement do not replace missing evidence.

## Gate 4: Cross-Repo Contract Drift And Existing-Code Inconsistency

Build the producer-consumer view within repositories and across all supplied PRs. Include local caller–callee success/failure contracts: changing returned failures to throws (or the reverse) can break consumers even when names and signatures stay the same. Inspect affected consumers and distinguish new regressions/newly exposed defects from unrelated pre-existing issues.

Check package contracts:

- `package.json`;
- lockfiles;
- workspace/file/link/latest versions;
- package exports maps;
- peer deps;
- TypeScript path aliases;
- generated declaration files;
- shared model packages.

Check API and data contracts:

- request/response shapes;
- required/optional field changes;
- nullable changes;
- enum additions/removals;
- pagination and sorting;
- error formats;
- date/number serialization;
- URL/callback/webhook routes;
- generated clients and source schemas.

Check operational contracts:

- env vars;
- feature flags and defaults;
- migration order;
- rollback safety;
- mixed old/new deployment behavior;
- backend-before-frontend or frontend-before-backend deploy assumptions;
- workers, cron, queues, background jobs, and webhook consumers;
- CI/deploy config.

Compare new code to existing patterns in the target branch and sibling repos. Report inconsistency when it changes behavior, error shape, logging style, validation, naming, release order, or deployment assumptions in a risky way.

### Multiline Braced Control Flow

For changed JavaScript/TypeScript control-flow bodies, require braces with the body on separate lines. Cover `if/else`, `for`/`for...of`/`for...in`, `while`/`do...while`, `switch`, and `try/catch/finally`; existing braces alone do not make a one-line body acceptable. Keep switch case statements on separate lines; do not require a new lexical block around each case unless needed. Apply this to statement-bodied callbacks/functions as well, without converting concise expression arrows or ternary expressions merely for this rule.

```js
if (rows.some((row) => !row.zoom_uuid || String(row.zoom_meeting_id) !== zoomId)) {
  return null;
}
```

Report a violation in changed code as a style/convention finding, normally low priority; do not inflate it into a runtime defect or treat it as a material failure-contract gap. Fix only when edits are authorized and brace placement preserves the existing control flow, including dangling-else ownership and loop scope. Do not reformat unrelated existing code. Explicit user/repository exceptions take precedence.
