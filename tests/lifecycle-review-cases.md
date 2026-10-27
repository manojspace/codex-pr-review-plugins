# Persistent Lifecycle Review Cases

Supply only Inputs to fresh review-only contexts. Cases are independent synthetic contracts; do not execute applications or contact a database/provider. Ask for causal findings, inspected dependencies, next-attempt behavior, safe corrections, and uncertainty. Formatting is outside these semantic cases. Withhold Expected Assessments until independent scoring. Source discovery is evaluated separately with `fixtures/lifecycle-discovery/`; knowing the answer from these cases does not pass that exercise.

## Inputs

### L01

A new suite reuses a fixture by stable name. Requests commit child rows referencing it. Teardown deletes only IDs in a process-local list, then deletes the fixture. The unchanged schema has an enforced child.fixture_id foreign key with ON DELETE RESTRICT. A supplied crash occurs after child creation but before teardown. The next process starts with an empty list, reuses the fixture, creates and deletes its own child, then attempts to delete the fixture. Failures propagate; the next scheduled run repeats the same setup. This fixture and all its children are exclusively owned by this suite.

### L02

A suite reuses an exclusively owned fixture after interruption and deletes the parent during teardown. The supplied schema and execution trace establish ON DELETE CASCADE on every surviving child relationship; deleting the parent atomically removes those children. No external side effects or other owners exist. The next run creates a fresh fixture successfully.

### L03

A cleanup patch deletes current-run children and then a reused parent. Previous runs can leave children. The installed models are a different version from the locked dependency. The owning schema repository is unavailable, no FK actions or execution trace are supplied, and the ORM declares only an association. Both independent reviewers report no confirmed findings because deletion semantics are unknown.

### L04

A recovery patch fixes a restrictive-FK failure by deleting every child of a reusable parent before deleting the parent. The parent is a shared workspace; another live worker owns child B, and the new query filters only parent_id. Supplied traces show that B is deleted even though its owner is live and still using it. A generation/owner field exists on each child but is ignored.

### L05

Each suite owns a distinct persistent fixture recorded in a durable registry. Recovery enumerates all children of its verified fixture identity, deletes their dependent rows, then removes children and fixture. Other workers have different fixture identities. The supplied restrictive-FK schema matches the deletion order. If a statement fails, durable ownership remains discoverable; the next attempt resumes safely. Already-absent deletes are documented successful no-ops.

### L06

A request commits a row and returns its ID. The new test asserts that its returned category is correct before adding the ID to cleanup tracking. A supplied wrong-category response throws at that assertion. Teardown uses only tracked IDs; there is no other recovery mechanism. Separately, a proposed fix records the ID immediately after the response. The same suite reuses a fixture across processes with restrictive child FKs and only in-memory tracking. Assess the original returned-ID failure and whether that proposed fix also establishes recovery after a killed process.

### L07

All fixture and child creation runs inside one database transaction on a single connection. The connection is closed on process death, and the supplied database contract and interruption trace show complete rollback. No DDL or external effects participate. Teardown rolls back on normal completion. A new run cannot observe survivors from this transaction.

### L08

A provisioning job uses a fresh random provider operation ID on every invocation. Provider creation commits before its response and can lose the response; the provider treats distinct IDs as distinct billable resources. The local resource ID is written only after a response arrives. A supplied lost-response trace followed by retry creates and bills a second resource. Provider lookup by stable operation ID is available within the retry window.

### L09

Blob cleanup retains a durable manifest until every owned blob is confirmed absent. Interruption after any deletion leaves the manifest intact; retry treats already-absent blobs as success, completes remaining deletes, then removes the manifest. Ownership is generation-scoped and prevents deleting live newer generations. Verified eventual consistency is accounted for before marking cleanup complete.

### L10

A new cleanup job removes the sole durable manifest before deleting its blobs. A supplied interruption leaves blobs but loses all rediscovery keys. Restart allocates another group; each invocation repeats this. Measured retained blobs exhaust a documented quota and block further allocations. No listing API, expiry or secondary registry exists.

### L11

A test API can commit an anonymous diagnostic row and fail before returning its ID. The test accurately fails and cannot identify that row. A verified independent sweeper removes these rows within ten minutes; rows have no dependents, unique-name conflict or user-visible effect, and measured accumulation remains below quotas. The test's success contract does not promise immediate deletion on failed requests. No recurring fixture failure is shown.

### L12

The only change narrows a read-only parameterized SELECT from all active rows to the authenticated owner's active rows. The owning column/type, authorization boundary, index, result consumers and query bounds are supplied and unchanged. The operation creates, reuses, resets and deletes no persistent resources. No result invariant depends on foreign keys or delete semantics.

### L13

A reusable queue subscription is allocated with a stable name. Delivery creates acknowledged leases linked to the subscription in durable provider state. Cleanup drops only leases recorded by the current process and then deletes the subscription. The supplied provider contract rejects deletion while any lease remains; acknowledged leases do not expire automatically. A killed worker leaves a lease; a fresh worker reuses the subscription and repeatedly fails to delete it. The subscription is exclusively owned by this job, and provider enumeration of its leases is available.

### L14

Two reviewers agree that parent deletion may be safe, but neither inspected the unchanged schema file in the available pinned repository. One reports the FK contract as unavailable; the other repeats that statement. Their scoped output says all changed hunks were read. The repository inventory identifies the local schema owner and exact version, with no access restriction. No authoritative delete semantics have been established yet.

## Expected Assessments (Withhold During Review)

| Case | Required assessment |
| --- | --- |
| L01 | Confirm recurring teardown failure: old child survives, new process loses IDs, parent is reused, RESTRICT blocks deletion after current children are removed. Propagating the error does not recover. Rediscover survivors through the verified suite-owned fixture identity and remove them in constraint order, or establish equivalent recovery. Existing persistent identity may suffice; earlier ID capture alone does not. |
| L02 | No repeated restrictive-FK failure. Verified atomic cascade and exclusive ownership are concrete counterevidence. Do not demand manual child deletion or a general migration audit. |
| L03 | Material evidence gap, not confirmed restrictive failure or a clean conclusion. Identify the reviewed schema/delete contract as missing; a mismatched installed package and ORM association cannot establish it. Do not access a live database without authorization. |
| L04 | Confirm destructive cross-owner cleanup. The broad fix is unsafe despite resolving the FK symptom. Preserve other owners/generations and reconcile only resources whose ownership is established; shared parent deletion may be invalid. |
| L05 | No demonstrated recovery defect. Durable owned-resource discovery survives lost process memory; correct dependency order and idempotent absence let retries converge. |
| L06 | Confirm the lost returned-ID cleanup defect and capture IDs before assertions. This closes the returned-ID window only. Establish survivor discovery/reconciliation or another verified mechanism preventing survivors from blocking subsequent runs; keep the two failure windows distinct. |
| L07 | No surviving-state recovery finding: verified same-transaction rollback removes all effects. Do not invent external work or ignored transaction options. |
| L08 | Confirm duplicate billable allocation after ambiguous completion. Use stable operation identity and provider reconciliation before creating again; a catch or local in-memory list is insufficient. |
| L09 | No demonstrated defect. Durable manifest and generation ownership support partial deletion and retry. Do not demand global scans or synchronous provider semantics. |
| L10 | Confirm lost recovery metadata and recurring quota exhaustion, supported by the supplied trace. Retain durable discovery until cleanup is complete or establish an equivalent bounded recovery path. |
| L11 | No blocking cleanup defect from these facts. Report bounded retention only if useful; do not inflate a failed request's residual diagnostic row into repeated fixture failure or require perfect immediate cleanup. |
| L12 | No lifecycle/schema audit triggered by these facts. Review the changed filter and supplied authorization/query contracts; avoid unrelated schema discovery. |
| L13 | Confirm the same cross-invocation dependency failure without SQL: prior durable lease survives, current list omits it, provider rejects deletion, retry repeats. Inspect actual provider ownership/delete semantics and use available owned-lease reconciliation. |
| L14 | Assign a bounded inspection of the available owning schema before a clean verdict or an unavailability claim. Shared uncertainty and full hunk counts are not independent contract evidence. Do not invent the FK action before reading it. |

Score detection, causal trace, correction safety, control/gap handling and unnecessary exploration separately. A prose pass does not prove tool-use discovery or runtime recovery.
