# Review Gates

Load this reference after changed-file inventory is known. Use it to complete the review pass; do not block branch alignment or first changed-hunk inspection on this file.

Run all four gates when completing review. Do not collapse them into a shallow checklist.

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
