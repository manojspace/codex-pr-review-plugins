# Database Schema And Deployment

Load for DDL, migrations, model fields, typed/shared schema versions or destructive data-shape changes. Ordinary query edits do not require a migration audit. Discover materially affected readers/writers through bounded contract searches, including unchanged workers and supplied repositories; do not scan an organization or connect to a database by default.

## Establish The Separate Sources Of Evidence

Record application/model expectations, consumer dependency versions, migration lineage, deployment topology and available execution evidence separately. A package pin, base-branch migration or model field is not proof of deployed schema. If deployment facts are missing, state expected compatibility and the unknown fact rather than asserting production state.

Compare semantic names/types/defaults/nullability/constraints among migrations, models, generated types and consumers. An intentionally database-only index or model-mapping correction may require no matching edit elsewhere. Identify the owning source before proposing changes to generated files. For ORM column alterations, establish the reviewed version's generated SQL or authoritative implementation before claiming omitted attributes are lost.

## Compatibility And Rollout

- For renamed/removed fields or enum changes, trace existing data and old/new readers and writers, workers, generated clients and shared-model consumers. An additive nullable field can be safe; an old exhaustive enum reader may reject a new writer's value.
- Check actual deployment order, expand/contract or maintenance-window assumptions, feature flags, rollback/forward-recovery policy and read-replica schema lag. Push order does not establish rollout order. Do not demand reversible `down` migrations where truthful forward-only recovery is the policy.
- If a migration is already released/applied under an append-only policy, inspect whether a corrective migration is needed. Being present on the base branch does not prove application. Unknown deployment state prevents claiming a history rewrite is safe.

## Execution And Existing Data

- Establish engine/version, storage/table options, exact SQL and algorithm/lock modes before concluding DDL is online, transactional or blocking. Check table size/write activity only as needed for the claimed operational consequence; avoid universal DDL matrices.
- For multi-step or nontransactional DDL, trace partial completion and retry. Does the next run safely recognize what happened, or fail after an earlier irreversible effect? An engine-supported atomic operation is relevant counterevidence.
- For constraints/backfills, inspect existing nulls, duplicates, ranges and consumer assumptions through authorized evidence. Large/live backfills need bounded progress, concurrency handling and restart behavior; a small bounded update may be sufficient. Resumption must not overwrite concurrent newer writes or silently skip gaps.

Report the changed contract, affected version/data population, feasible rollout/execution failure and smallest supported correction. If facts require runtime access, identify the smallest missing fact or use an already authorized read-only source; do not invent live schema or execute migrations for review.
