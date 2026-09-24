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

For shared-helper changes, identify affected callers, including callers outside the diff, and inspect the complete enclosing paths needed to understand the changed behavior. Group equivalent callers; inspect distinct paths and the most constrained consumers rather than every unrelated helper or file.

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

## Gate 3: Error Handling, Try-Catch, Logging, And Observability

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

Require the error style expected by nearby code: `try/catch`, `.catch`, result objects, transaction rollback, cleanup/finally, retry/backoff, or propagated typed errors.

Check that failures are not swallowed silently and do not return misleading success states. Ensure logging exists where failures would otherwise be invisible. Logging should include useful context such as operation, entity identifier, external provider, request ID, job ID, and the error object. Do not log secrets, tokens, credentials, private payloads, or unnecessary PII.

Check partial failure behavior:

- step 2 fails after step 1 succeeded;
- one item in a batch fails;
- retry runs twice;
- rollback or cleanup fails;
- frontend optimistic state must roll back;
- external API returns timeout, 4xx, 5xx, malformed response, or rate limit.

A finding must state the missing failure mode, the expected handling/logging pattern from nearby code, and whether the fix is safe without lint/build.

## Gate 4: Cross-Repo Contract Drift And Existing-Code Inconsistency

Build the producer-consumer view across all supplied PRs.

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
