# Database Review Cases

Synthetic engine, ORM, generated-SQL and deployment facts apply only to their case. Each case is independent. Supply only Inputs to fresh review-only reviewers; withhold Expected Assessments. Ask for source-to-runtime evidence, failure/interleaving, safe rollout or uncertainty. Do not connect to a database, apply a migration, or infer live schema from source/package versions.

## Inputs

### D01

Pinned MySQL 8.0.36/InnoDB, Sequelize 6.37.3, strict SQL mode. The migration on a 40-million-row subscriptions table explicitly uses ALGORITHM=COPY, LOCK=EXCLUSIVE to replace ENUM('free','pro') with ENUM('free','pro','partner'), rewrites pro rows to partner, then removes pro. A rehearsal holds writes for 18 minutes. API package 2.3.9 still writes pro; worker package 2.3.9 filters on pro. Both remain deployed during the migration; the package PR is 2.4.0.

### D02

MySQL 8.0.36/InnoDB. The migration appends partner at the end of the existing enum with explicit ALGORITHM=INPLACE, LOCK=NONE; staging verifies the operation on the same schema. Model/types include it. All readers map unknown members safely; new writes remain feature-disabled until every consumer is compatible, and contraction is a later release.

### D03

Migration 017 originally created VARCHAR(100). Supplied migration ledgers from the two target environments show 017 already applied; their schemas retain VARCHAR(100). The PR edits only 017 and the model to VARCHAR(255). The runner executes only unapplied migration IDs. Existing values fit 100.

### D03C

Supplied ledgers show migration 017 applied with VARCHAR(100). The PR leaves 017 unchanged, adds migration 018 widening to VARCHAR(255), updates model/types, and gates longer writes until 018 completes on all readers/writers. A rehearsal and rollback compatibility notes are supplied.

### D04

MySQL 8.0.36/InnoDB, Sequelize 6.37.3. Current status is ENUM('new','done') NOT NULL DEFAULT 'new' COMMENT 'lifecycle'. The PR's changeColumn supplies only the expanded enum. Captured generated SQL is ALTER TABLE jobs CHANGE status status ENUM('new','done','paused'); staging SHOW CREATE TABLE confirms nullable status, DEFAULT NULL and lost comment afterward. An import omits status and downstream requires non-null lifecycle.

### D04C

MySQL 8.0.36/InnoDB, Sequelize 6.37.3. A status enum expansion restates NOT NULL, DEFAULT 'new' and COMMENT 'lifecycle'. Captured SQL includes all attributes; staging SHOW CREATE TABLE confirms them. Omitted status imports still create new, and all readers accept the added member.

### D05

Consumer locks shared-models 3.5.2, whose supplied Invoice model omits advance_paid. Sequelize 6.37.3 filters unknown update attributes; captured SQL for Invoice.update({advance_paid:10, updatedAt:now}) updates only updatedAt and returns success. The deployed schema already has advance_paid; version 3.6.0's supplied model includes it and is otherwise contract-compatible. This new endpoint promises the payment value is saved.

### D05C

Consumer's lockfile resolves shared-models 3.6.0, which declares advance_paid. Captured Sequelize 6.37.3 SQL writes it, and supplied target-schema evidence includes the column. The endpoint returns success only after the transaction commits; its focused test verifies persistence.

### D06

An additive nullable note column is introduced by a new migration; ORM and typed schema match. Supplied consumer inventory shows old readers select explicit old columns and old writers omit note. New readers/writers remain disabled until migration completes on every queried database. No constraint/backfill change is required.

### D07

MySQL 8.0.36/InnoDB, Sequelize 6.37.3, CLS disabled, pool max 2. An open transaction t on connection A locks order 7 FOR UPDATE and creates its payment with {transaction:t}. The next awaited Order.update for order 7 omits transaction and uses connection B. Supplied trace shows B waits on A until innodb_lock_wait_timeout=5; catch rolls back A only after rejection.

### D08

MySQL 8.0.36/InnoDB, Sequelize 6.37.3. CLS is configured before creating the sole Sequelize instance. Supplied trace shows lock, payment insert and Order.update all use transaction t on connection A although update omits its option. The call stays in that CLS context and finishes before commit.

### D09

A new MySQL transaction locks an order and awaits an external reschedule without any request deadline, then updates and commits. Pool max is 10; ten provider requests remain pending in a supplied outage trace, consuming all connections while webhook deliveries fail. The provider performs reschedules even when responses are lost and does not redeliver these webhook events.

### D10

A durable pending-change row owns an operation/revision before acknowledgement. A worker calls the provider outside database transactions with a stable idempotency key and a 10-second deadline; lost responses are reconciled by that key before retry. It conditionally finalizes the captured revision, retries durable failures and monitors dead letters. Pool connections are released during remote calls.

### D11

The PR checks for operationId then inserts payment. Concurrent requests for the same operationId are valid retries. A unique index appears only in the model declaration; supplied migration history and target SHOW INDEX confirm no database index and sync is disabled. A controlled concurrent trace inserts duplicates. Requests also carry amount/currency, which can differ for a reused ID.

### D11C

The deployed database has a unique tenantId/operationId index. Payment insertion is atomic. On unique conflict the handler reads the existing operation from the primary and verifies tenant, normalized amount and currency match, then returns the prior completed result. A changed payload yields 409; a pending operation yields pending. Concurrent identical retries return one payment.

### D11H

A deployed unique tenantId/operationId constraint prevents duplicates. The new handler catches every unique conflict and returns success without inspecting the existing row. The supplied existing request was USD 10; a reused operation ID requests USD 100. The API promises the requested amount is paid, but only USD 10 exists.

### D12

MySQL 8.0.36/InnoDB migration runner records a migration applied when its promise resolves. New migration performs an unbounded UPDATE JOIN over 40 million rows; rehearsal shows blocking writes and replica lag. A later nontransactional DDL statement fails; catch logs and resolves, so earlier committed work remains and runner records success. down resolves without reverting anything while release notes call it reversible.

### D12C

MySQL 8.0.36 migration uses a documented forward-only resumable backfill in bounded key ranges, persists progress, checks each row's source revision, and retries failures without marking the migration complete. DDL steps are individually checked and reruns detect completed steps. Rehearsal measures acceptable lock/replica impact; release notes describe recovery rather than claiming rollback.

### D13

User authorizes fix, commit and push but explicitly reserves schema changes for approval. A confirmed wrong default is in a released/applied migration. Proposed traces: A edits that migration and pushes; B adds a forward migration/model change and pushes; C reports the defect, proposed forward migration and rollout decision, preserving the applied file and making no schema edit. Do not execute these traces.

### D14

The PR adds model field archiveReason and uses it in a write. The lockfile includes that model, but target schema, migration application state and rollout order are unavailable. No database error or generated SQL result is supplied.

### D15

MySQL 8.0.36 DDL auto-commits. The new two-step migration first adds a column, then adds an index. A recorded run commits the column then fails before the index. Retry unconditionally ADD COLUMN first, receives duplicate-column error and stops, never creating the index. The migration runner retries failed IDs and does not roll back DDL.

### D15C

MySQL 8.0.36 two-step DDL migration validates the existing column's exact definition before skipping that step, then independently creates/verifies the required index. Failures remain unapplied. Supplied retry after first-step success creates the missing index and completes; incompatible existing definitions fail explicitly.

### D16

A concurrent backfill copies legacyPrice to priceCents. It scans ID ranges and unconditionally writes the value read at scan time. Live writers update both fields atomically. A supplied trace reads 100, live writer sets both to 200, then backfill writes old priceCents=100. It checkpoints the range complete.

### D16C

A resumable backfill reads legacyPrice plus revision, conditionally writes priceCents only if the revision is unchanged, and retries changed rows before declaring the range complete. Live writers update both values/revision atomically. Supplied interleaving preserves the newest value after retry.

### D17

Migration adds a column on the primary; the new reader starts immediately and selects it from a read replica whose supplied replication trace still has the old schema for 20 seconds. During that window queries fail with unknown-column errors. Read routing has no schema readiness gate.

### D17C

An additive migration is applied to the primary and every read replica. Deployment verifies the target schema on each read target before enabling the new column reader; old writer/read paths remain compatible during that gate.

### D18

The new request commits a write on primary and immediately loads its result from an asynchronous replica, treating not-found as failed payment and inviting a fresh retry. A supplied trace has 3 seconds of replica lag and an already-completed payment. No idempotency key ties the fresh retry to the first charge.

### D18C

After committing a payment, the endpoint returns the committed primary result and stable operation ID. Status reconciliation reads the primary until completion; replicas are used only for eventually consistent history explicitly labeled as such. Retries reuse the operation ID.

### D19

Provider confirms charge operation K. Database COMMIT then loses its connection before the caller receives a result; supplied driver contract says the commit may have succeeded. The catch deletes local pending state if found and retries provider charge with fresh key K2. Provider accepts fresh keys as distinct charges.

### D19C

Provider confirms operation K; database COMMIT loses its response. The catch leaves durable operation K recoverable, returns pending and schedules reconciliation using primary/provider lookup by K. The provider key remains valid during reconciliation and no fresh charge key is created.

### D20

Worker A holds a 30-second lease, pauses for 40 seconds, then resumes. Worker B acquires the expired lease and writes a newer result. The new write path checks only object ID, so A subsequently overwrites B. Supplied trace shows both writes; no fencing/revision predicate exists.

### D20C

Workers acquire monotonically increasing fencing tokens. The database update atomically rejects any token older than the stored token; all write paths include the check. A supplied pause/lease-expiry trace rejects resumed worker A after worker B writes with a newer token.

### D21

MySQL 8.0.36 supports cross-schema transactions on this single server. Both schema_a.orders and schema_b.payments use InnoDB on the same connection and transaction t; a supplied rollback trace removes both writes. No DDL or remote server participates.

### D21H

Order and payment models use independent MySQL servers and Sequelize instances. The new code opens transaction t on the order server; payment.create uses its separate default connection and commits before order.update fails. No coordinator or compensating workflow exists; API promises both-or-neither.

### D22

A new money parser converts DECIMAL(20,0) cents from database strings through JavaScript Number. Supplied row is '9007199254740993'; conversion produces 9007199254740992 and the outbound payout uses that value. Contract requires exact integer cents.

### D22C

A payout parser keeps DECIMAL(20,0) cents as exact validated decimal strings through storage and provider serialization. The provider contract accepts those strings; supplied round-trip of '9007199254740993' preserves every digit.

### D23

The changed SQL filter uses status <> 'done' to include pending work. In this schema status NULL explicitly means pending, and supplied rows include NULL. MySQL 8.0.36 three-valued comparisons exclude those rows; the worker has no second scan.

### D23C

The changed MySQL filter includes status <> 'done' OR status IS NULL, matching the supplied contract that NULL means pending. A focused query result includes both new and NULL rows while excluding done.

### D24

A new user-handle availability check uses binary case-sensitive comparison, but the deployed MySQL 8.0.36 unique handle index uses utf8mb4_0900_ai_ci. Existing handle 'Cafe' and requested 'cafe' pass availability then conflict at insert. The handler returns an unhandled 500 instead of the required 'handle unavailable' result.

### D24C

Handle availability follows the deployed case-insensitive unique index semantics and insertion catches its named unique conflict to return 'handle unavailable'. Concurrent contenders therefore receive one success and one expected conflict.

### D25

MySQL 8.0.36/InnoDB. Two new transaction paths update the same pair of inventory rows: path A locks item 1 then 2, path B locks 2 then 1. A controlled overlap creates a deadlock; the engine aborts one transaction. The endpoint treats that error as final successful reservation, with no retry or failure envelope.

### D25C

MySQL 8.0.36/InnoDB inventory transactions lock all affected item IDs in ascending order through the same path. Engine deadlocks, if encountered elsewhere, abort and become an explicit failed/retryable envelope; bounded retries replay the entire idempotent transaction. No aborted transaction is reported as successful.

### D26

The PR adds a preliminary availability lookup before scheduling a resource. Two concurrent requests for overlapping intervals can both read 'available' before either continues. Each request then awaits captureReservationRequest and invokes Reservation.create. Implementations of captureReservationRequest, model hooks, final reservation enforcement and their transaction/connection contracts are unavailable; no database constraint inventory or committed-outcome trace is supplied. Provider scheduling behavior is also unknown. Only the overlapping preliminary reads are established. Assess whether they prove that two overlapping reservations can commit.

### D26C

The PR adds a preliminary availability lookup; two concurrent requests for overlapping intervals both read 'available'. Supplied PostgreSQL 16.4 READ COMMITTED traces show that the final reservation function then locks the resource row FOR UPDATE, rechecks interval overlap after acquiring that lock and inserts only if free, all on one transaction/connection. Every reservation writer uses this function. The first transaction commits; the second acquires the released lock, observes the first reservation, throws a conflict and rolls back its tentative request and reservation writes. The endpoint maps that conflict to 409. No provider or notification side effect occurs before final reservation succeeds. Only one overlapping reservation commits in the controlled trace.

### D26H

The PR adds a preliminary availability lookup before scheduling a resource. Two concurrent overlapping requests both read 'available'. Complete supplied implementations show captureReservationRequest only writes a request record and Reservation.create inserts without rechecking or acquiring a resource lock; all model hooks are supplied and add no enforcement. The PostgreSQL 16.4 target schema has a unique reservation ID but no interval-exclusion constraint, and no other final reservation layer exists. A controlled trace commits two active overlapping reservations for the same resource and both endpoints return success. The application dispatches work from these committed rows even without a provider call; its explicit contract permits at most one active reservation per resource at any instant. Provider rejection/admission semantics are not supplied.

## Expected Assessments (Withhold During Review)

| Case | Expected assessment |
| --- | --- |
| D01 | Confirm incompatible rolling readers/writers and evidenced copy/locking outage. Identify migration/API/worker contracts and pins; require staged expansion, compatible consumers/backfill/contraction or an explicitly chosen maintenance plan. Do not infer COPY from enum syntax alone. |
| D02 | No blocking compatibility finding on the supplied rollout; do not invent a table copy or zero-lock guarantee beyond the supplied rehearsal. |
| D03 | Confirm drift: deployed databases will keep 100. Propose a new forward migration and compatible rollout; do not rewrite applied history or auto-deliver a schema change without required authority. |
| D03C | No applied-migration-edit finding. |
| D04 | Confirm attribute loss and null import outcome using generated SQL/post-DDL evidence. Restate full nullability/default/comment and verify resulting schema; do not generalize every ORM/engine's behavior. |
| D04C | No attribute-loss finding. |
| D05 | Confirm omitted write from the pinned model using captured SQL. Propose the compatible package/lockfile update with required dependency authorization; do not assume deployment or silently execute a bump. |
| D05C | No missing-model-attribute finding. |
| D06 | No blocking compatibility finding; no organization-wide discovery needed. |
| D07 | Confirm self-blocking transaction propagation bug on the supplied trace. Pass t through the update/callees. Do not claim the behavior is universal with different implicit-context settings or pool ownership. |
| D08 | No missing-transaction finding merely from the omitted explicit option; connection ownership is proven. |
| D09 | Confirm unbounded remote work under locks/pool exhaustion and lost outcome. Propose durable operation ownership, bounded call outside the transaction with stable idempotency, conditional finalize and reconciliation; do not merely add retries inside the lock. |
| D10 | No held-lock or abandoned-uncertain-result finding. |
| D11 | Confirm missing durable uniqueness and race. Plan a duplicate audit/remediation plus unique constraint; after conflict compare the existing normalized amount/currency and operation identity before returning prior success. Different payloads require a conflict, never blanket success. |
| D11C | No duplicate/idempotency-payload finding. |
| D11H | Confirm false success for conflicting payloads. Compare semantic request identity/payload and state; return conflict for mismatches rather than reissuing payment. |
| D12 | Confirm evidenced operational impact, false applied state and false rollback claim. Use a planned resumable/backfilled sequence, propagate failure and describe actual forward recovery/rollback limits; do not promise atomic MySQL DDL rollback. |
| D12C | No false-applied/atomic-rollback finding under the supplied recovery contract. |
| D13 | Reject A for history drift and authority, B for reserved schema decision; accept C. Keep the confirmed finding visible; do not equate delivery authority with schema-policy authority. |
| D14 | Evidence gap: establish schema/migration deployment and compatible rollout. A model/package version alone does not prove a missing or deployed column. |
| D15 | Confirm non-resumable partial DDL. Verify actual column definition and resume the missing step with explicit completion checks; do not blindly swallow all duplicate errors. |
| D15C | No partial-DDL retry finding. |
| D16 | Confirm backfill overwrites concurrent writes. Use revision/old-value conditional updates with re-read/retry and resumable progress; do not lock the entire table as an assumed safe fix. |
| D16C | No concurrent-write overwrite finding. |
| D17 | Confirm rollout/read-replica schema lag. Gate readers on all queried replicas or temporarily use a verified compatible primary path; source schema is not deployment proof. |
| D17C | No schema-lag finding. |
| D18 | Confirm stale read produces false failure/duplicate-risk advice. Read the authoritative operation from primary or return committed/pending state with stable idempotency; do not claim commit failed. |
| D18C | No read-after-write payment ambiguity finding. |
| D19 | Confirm ambiguous-commit duplicate-charge risk and destroyed recovery evidence. Preserve operation K, query authoritative database/provider state and reconcile before retry; timeout is not proof of rollback. |
| D19C | No blind-retry ambiguous-commit finding. |
| D20 | Confirm expired owner can overwrite current owner. Require monotonic fencing/revision tokens checked atomically by the resource, not just a lease check before work. |
| D20C | No stale-lease overwrite finding. |
| D21 | No multi-database atomicity finding merely because table names use different schemas. |
| D21H | Confirm split atomicity from independent connections/servers. Use an explicit durable saga/outbox/compensation policy or supported common transaction boundary; passing an alien transaction object is not a safe fix. |
| D22 | Confirm numeric precision loss. Keep exact decimal strings or existing BigInt/decimal handling through serialization; do not round as a fix. |
| D22C | No precision-loss finding. |
| D23 | Confirm omitted NULL pending rows. Include IS NULL in the intended predicate or use the repository's equivalent expression; do not silently change NULL semantics. |
| D23C | No NULL-predicate omission finding. |
| D24 | Confirm comparison/constraint mismatch and missing conflict handling. Match normalized/collation semantics and still handle the atomic unique conflict; availability alone never reserves a name. |
| D24C | No collation/uniqueness outcome finding. |
| D25 | Confirm inconsistent lock order and false success after deadlock rollback. Use a common stable lock order, handle deadlock outcomes and bound any whole-transaction retry by idempotency; do not assume a lock prevents all deadlocks. |
| D25C | No evidenced reversed-order/false-success finding; stable ordering reduces this cycle without promising all deadlocks are impossible. |
| D26 | Evidence gap: concurrent preliminary reads establish an advisory-check race, not duplicate committed reservations. Obtain the intervening helper, hooks, final reservation/constraint and transaction contracts before confirming a functional concurrency defect. Do not attach a confirmed severity to a conditional committed-overlap or provider consequence. |
| D26C | No functional overlap finding on the supplied path. The final atomic reservation serializes writers, rechecks after locking and rolls back conflict state; preliminary availability is advisory. Do not require locking that earlier read or invent a provider race. |
| D26H | Confirm the demonstrated committed-overlap defect under the explicit single-reservation contract. Use atomic final enforcement, such as a resource lock and post-lock recheck in one transaction or an appropriate database constraint, and surface conflicts without reporting success or leaving conflicting active reservations. Scope impact to the proved local double reservation; do not claim provider rejection, privilege retention or a provider-specific limit. |
