# Providers, Jobs And Timing

Load relevant sections when provider calls, webhooks, queues, retries, cron or date/time behavior changes. Resolve exact SDK/API versions using reviewed dependency evidence and primary versioned contracts or implementation; do not substitute stale local dependencies. Keep the core outcome trace and cumulative-budget reasoning authoritative.

## Completion, Acknowledgment And Recovery

- Classify definite success/rejection, fulfilled failure and indeterminate outcome using the actual contract. HTTP 408/429/5xx, SDK errors and timeouts have no universal provider-effect meaning. A definite rejection now says nothing about earlier effects or concurrent work.
- Prove retry/compensation safety for the whole operation, including committed effects, duplicates and reordered delivery. Inspect operation identity, payload binding, key scope/expiry and retention. An expired idempotency key may permit repetition. Equivalent key implementations in separate runtimes need compatible semantics, not necessarily a shared builder.
- Where acknowledgment promises eventual processing, establish durable ownership before acknowledging. Check shutdown/crash between receipt and persistence or enqueue; `ack then enqueue` can lose work. Confirm actual queue durability and enqueue-failure behavior. A synchronous completed operation can have a different valid acknowledgment contract.
- For retry exhaustion and dead-letter queues, trace who observes, owns and recovers the failed work. Do not demand an outbox/reconciler when the existing contract and mechanism already establish required durability.
- Check out-of-order cancel/update, duplicate notification, stale versions and concurrent updates. Version checks, conditional ETag updates, ordering or another verified mechanism can be sufficient; successful transport alone does not establish correct final state.

## Rate Limits And Deadlines

Check retryable conditions, bounded attempts, backoff/jitter, provider-specific `Retry-After` units/formats and the effective enclosing request/job/transaction budget. Include sequential work and cleanup that share that budget; configured ceilings alone do not prove exhaustion. Cancellation can stop local waiting while mutation continues. For lock/pool consequences use the relevant `database-runtime.md` section.

For detached optional work, establish framework/runtime version, effective error wrapper and startup rejection policy when they determine whether a rejection is contained or terminates the process. Optional business importance does not prove safe rejection handling; a verified supervisor/boundary can provide counterevidence. Do not infer termination from a detached promise alone.

## Time Meaning

Identify whether a value is an instant, local wall time, date-only value, elapsed interval or ordering/version marker. Verify timezone conversion, precision, interval inclusivity and source-clock assumptions at affected consumers. For scheduled local times, inspect daylight-saving ambiguous/nonexistent times and the documented resolution policy. A server authorization deadline cannot safely depend solely on a client clock. Fixed UTC scheduling and explicit stale-result policies can be valid controls.

Report a feasible failure ordering and supporting contract; unknown provider semantics remain an evidence gap. Avoid prescribing blind retries, global timeout increases or a new distributed workflow without proving the actual requirement.
