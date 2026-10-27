# Database Runtime And Concurrency

Load applicable sections for changed writes, transaction/lock ownership, critical queries or result interpretation. Apply the core operation-outcome trace, including commit and rollback outcomes. Finish at the invariant, actual connection/coordination boundary and affected consumer; ordinary scoped reads do not require every section.

## Transaction Membership And Lifetime

- Identify the transaction/connection covering each effect, including implicit context propagation and explicit overrides for the reviewed ORM version. Sharing a callback does not make independent connections or provider effects atomic. Multiple schemas/databases can share a transaction where the engine and connection support it; labels and ORM-instance counts alone settle neither case.
- Trace caught errors, normal callback returns, affected-row counts, cleanup and commit ambiguity. A successful provider charge followed by an unknown database commit result may make a blind retry duplicate the charge. Check durable reconciliation or existing idempotency rather than assuming rollback undoes the provider.
- For network calls while holding a lock/connection, establish effective deadline, achievable latency, lock ordering, contention and pool demand. This is an investigation trigger, not automatically a defect. An enclosing bounded client/deadline can supply counterevidence; cancellation may leave remote work running.

## Concurrent Writes And Retries

- State the required invariant and check conditional updates, versions, unique constraints, locks or existing coordination. Do not mandate one architecture. A check-then-write race needs a credible interleaving and consequence.
- Follow preliminary availability/permission reads through every intervening allocator, reservation helper, model hook, constraint and commit boundary that may enforce the invariant. Concurrent advisory checks can be valid when final admission is atomic. Missing shared locking at the early read, or assuming both provider calls succeed, does not prove conflicting local commits. If final enforcement is unavailable, report a material concurrency evidence gap rather than a confirmed integrity defect; a conditional consequence does not justify an unqualified defect headline or priority.
- A unique conflict is successful replay only if the existing record matches the operation identity and material payload. Distinguish equivalent replay from another request colliding with the same key. Inspect key scope and expiry where they affect correctness.
- For leases, consider an expired worker continuing after another obtains ownership. A fencing token or verified equivalent can reject stale effects; lease renewal alone may not establish exclusivity after a pause.
- Inspect retry state, lock order and isolation only as needed for the affected invariant. Do not infer rollback, serialization or retry safety from a transaction wrapper's name.

## Query And Value Semantics

- Trace query shape, filters, joins, pagination/order, data volume and relevant index evidence. Establish realistic N+1, full-scan, pool or memory impact before reporting performance defects.
- Check replica/cache read-after-write behavior when a stale read can drive an incorrect response or repeated mutation. Strong-read routing, consistency tokens or supported eventual behavior can be sufficient.
- Where changed comparisons/serialization depend on them, verify numeric precision/range, timezone, NULL and collation semantics against the actual driver/engine contract. Do not assume JavaScript numbers preserve arbitrary database integers or money precision.

Keep confirmed defects separate from unknown topology, generated SQL or isolation settings. Use `database-schema.md` when the changed runtime invariant depends on schema constraints or deployment contracts, including unchanged foreign-key actions. Inspect only affected relationships; ordinary query edits do not require a migration audit.
