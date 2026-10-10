# Error Handling Review Evaluation Cases

Evaluate each plugin in a fresh review-only context using its complete skill and applicable references. Supply only the input cases, with the expected assessments withheld. No edits, branch changes, GitHub writes, application execution, credentials, or live services are needed. Treat each case independently; snippets are complete for the stated contract unless a dependency is explicitly unavailable. Line references can use the case ID and numbered snippet lines.

Ask for concrete findings, inspected outcome contracts, consequences, safe correction or uncertainty, and a scoped conclusion. Do not identify which inputs should have findings. Record actual answers, plugin/source revision, model/settings when available, and limitations. Structural validation does not pass these behavioral evaluations.

E01–E30 intentionally compress code for semantic review; formatting is outside those cases' scope. E31–E34 separately evaluate the multiline-braces convention against actual changed formatting.

E35 also evaluates semantics only, including the sufficiency of available dependency evidence.

## Inputs

### E01

All shown code is new. Successful reactivation promises a fresh external identity; stale identities prevent login. Database methods commit independently. Another caller commits deactivation before calling `retireIdentity`, treating external retirement as secondary cleanup. Replaying `activate` inserts another employment row.

```js
async function retireIdentity(email) {
  try { await provider.removeByEmail(email); return { success: true, deleted: true }; }
  catch (error) {
    if (error.code === 'absent') return { success: true, deleted: false };
    log.error(error);
    return { success: false, deleted: false };
  }
}
async function activate(member) {
  try {
    await db.setActive(member.id);
    await db.insertEmployment(member.id);
    await retireIdentity(member.email);
    return { success: true };
  } catch (error) { return { success: false }; }
}
```

### E02

Only `restore` changes. Its contract promises access provisioned before activation. The other functions are unchanged; `adapter` may reject or resolve `{ok:false}`. Provisioning is idempotent and the database activation is retry-safe.

```js
async function provision(id) {
  try { return await adapter(id); }
  catch (error) { return { ok: false, error }; }
}
const forward = (id) => provision(id);
async function restore(id) {
  const outcome = await forward(id);
  if (outcome) {
    await db.activate(id);
    return { ok: true };
  }
  return { ok: false };
}
```

### E03

The core write is atomic and idempotent. Analytics is explicitly optional and cannot affect the saved record; its failures are observable. `save` promises only that the record is saved.

```js
async function save(record) {
  await db.save(record);
  try { await analytics.track(record.id); }
  catch (error) { log.warn('analytics unavailable', { id: record.id, error }); }
  return { saved: true };
}
```

### E04

`cleanup` fulfills with `{success:true,deleted:true}`, `{success:true,deleted:false}` for an already absent record, or `{success:false,deleted:false}` for failure. Cleanup is safely repeatable; the atomic database operation is idempotent. Successful completion promises cleanup plus activation.

```js
async function activate(id) {
  const outcome = await cleanup(id);
  if (!outcome.success) return { success: false, retryable: true };
  await db.activateOnce(id);
  return { success: true };
}
```

### E05

This is native `fetch`, not a wrapper. The new function promises to persist only an accepted remote reservation. The endpoint can return 503 with valid JSON `{message:'unavailable'}`.

```js
async function reserve(id) {
  const response = await fetch('/reservations', { method: 'POST', body: id });
  const reservation = await response.json();
  await db.saveReservation(id, reservation);
  return { reserved: true };
}
```

### E06

`client.reserve` rejects for non-2xx, validates the required response schema, and rejects application-level failure; it resolves only a valid reservation. The enclosing HTTP error boundary awaits `reserve` and converts rejection into failure. The PR only adds this function.

```js
async function reserve(id) {
  const reservation = await client.reserve(id);
  await db.saveReservation(id, reservation);
  return { reserved: true };
}
```

### E07

The new endpoint promises delivery. The HTTP client rejects non-2xx but returns the parsed body on 200. A provider rejection uses HTTP 200 with `{accepted:false,error:'quota'}`; successful bodies have `accepted:true`.

```js
async function send(message) {
  await client.post('/send', message);
  return { delivered: true };
}
```

### E08

The new code may receive HTTP 200 with `{}` during upstream degradation. Only `{approved:true}` authorizes the charge; `approved:false` means declined. Missing approval is not an approved outcome.

```js
async function purchase(order) {
  const result = await precheck(order);
  if (result.approved !== false) {
    await charge(order);
    return { purchased: true };
  }
  return { purchased: false };
}
```

### E09

Every item is required for successful batch completion. `sendOne` may reject or fulfill `{ok:false}`. The PR adds this implementation.

```js
async function sendBatch(items) {
  await Promise.allSettled(items.map(sendOne));
  return { completed: items.length, failed: 0 };
}
```

### E10

Same `sendOne` contract as E09; it always fulfills an object with a boolean `ok` when not rejecting. The endpoint explicitly reports partial completion.

```js
async function sendBatch(items) {
  const settled = await Promise.allSettled(items.map(sendOne));
  const failed = settled.filter((r) => r.status === 'rejected' || !r.value.ok).length;
  return { completed: items.length - failed, failed };
}
```

### E11

The new conditional write uses an optimistic version check and returns an affected-row count. Concurrent requests can produce zero rows. Publishing the event means this request actually changed the row.

```js
async function update(id, version, value) {
  await db.updateWhereVersion(id, version, value);
  await events.publish({ id, value });
  return { updated: true };
}
```

### E12

The API promises the row is absent afterward. `deleteById` rejects on database errors; zero rows means it was already absent. There are no dependent side effects or concurrent recreation in this fixture.

```js
async function remove(id) {
  await db.deleteById(id);
  return { absent: true };
}
```

### E13

The queue only retries unacknowledged jobs. All writes must finish before acknowledgment, and `db.save` can reject asynchronously. The PR adds this handler.

```js
async function handle(job) {
  job.items.forEach(async (item) => { await db.save(item); });
  await job.ack();
}
```

### E14

`queue.enqueue` resolves only after durable persistence and rejects otherwise. Workers own retries and error reporting. This API promises acceptance for processing, not completed processing. The outer route handles rejection.

```js
async function submit(job) {
  const id = await queue.enqueue(job);
  return { status: 'accepted', jobId: id };
}
```

### E15

The transaction manager commits whenever the callback fulfills, including returned objects, and rolls back on rejection. Debit and credit must be atomic; both use `tx`, and credit can reject.

```js
async function transfer() {
  return db.transaction(async (tx) => {
    await tx.debit();
    try { await tx.credit(); }
    catch (error) { return { ok: false }; }
    return { ok: true };
  });
}
```

### E16

Both writes must be atomic. `db.insertAudit` uses a separate autocommit connection; only `tx` methods participate in this transaction. Commit can fail after the audit insertion succeeds.

```js
async function update() {
  await db.transaction(async (tx) => {
    await tx.updateAccount();
    await db.insertAudit();
  });
}
```

### E17

The transaction manager rolls back on rejection. Both methods below use the same transaction and reject on failure. The outer boundary awaits `transfer` and reports failure on rejection. Both writes must be atomic.

```js
async function transfer() {
  await db.transaction(async (tx) => {
    await tx.debit();
    await tx.credit();
  });
  return { ok: true };
}
```

### E18

The PR adds the `if` line to handle failed provisioning. Each earlier write commits independently; `insertEmployment` inserts a new row on every call. On `{ok:false}`, admins may retry the whole operation. Activation requires successful provisioning. Provisioning is idempotent; the database operation currently is not.

```js
async function restore(id) {
  await db.markActive(id);
  await db.insertEmployment(id);
  const result = await provision(id);
  if (!result.ok) return { ok: false, retryable: true };
  return { ok: true };
}
```

### E19

`createPendingOnce` atomically stores the pending state and durable outbox event under a stable unique operation ID. The worker reconciles/retries idempotently and marks active only after provisioning succeeds. The API promises only pending acceptance. Writes and reads reject on errors.

```js
async function restore(id, operationId) {
  await db.createPendingOnce(id, operationId);
  return { status: 'pending', operationId };
}
```

### E20

The provider charges on receipt and has no deduplication. Network timeout can occur after a successful charge. The PR introduces this retry.

```js
async function pay(order) {
  try { return await provider.charge(order); }
  catch (error) {
    if (error.code === 'TIMEOUT') return provider.charge(order);
    throw error;
  }
}
```

### E21

The new code reports timeout and allows immediate retry. `slowWrite` ignores cancellation and writes the supplied value after network delay. A first invocation with value A can finish after a retried invocation with value B. The API promises no further writes from a timed-out invocation.

```js
async function save(value) {
  return Promise.race([slowWrite(value), rejectAfter(1000)]);
}
```

### E22

The caller persists the operation ID before this function runs and reuses it across retries. The provider atomically deduplicates identical operation IDs and returns the recorded result. Both attempts carry the same payload. Only transient timeouts are retried once.

```js
async function pay(order, operationId) {
  try { return await provider.charge(order, { key: operationId }); }
  catch (error) {
    if (error.code !== 'TIMEOUT') throw error;
    return provider.charge(order, { key: operationId });
  }
}
```

### E23

The PR adds cleanup. `requiredWrite` can reject; successful completion promises the write happened. `release` is synchronous and does not throw.

```js
async function save() {
  try { await requiredWrite(); }
  finally { release(); return { ok: true }; }
}
```

### E24

`release` is synchronous and cannot throw. The outer route awaits `save` and handles rejection. Successful completion promises the required write happened.

```js
async function save() {
  try { await requiredWrite(); }
  finally { release(); }
  return { ok: true };
}
```

### E25

This new endpoint promises that the new policy is immediately effective. Enforcement reads only cache for its 24-hour TTL. Cache writes can fail; no invalidation, short TTL, or recovery path exists.

```js
async function updatePolicy(id, policy) {
  await db.setPolicy(id, policy);
  try { await cache.setPolicy(id, policy); }
  catch (error) { log.error(error); }
  return { effective: true };
}
```

### E26

The PR changes only `removeOne` from catching failures and returning `{ok:false}` to propagating rejection. The existing batch contract promises to process every ID and return per-item outcomes even when one removal fails. The provider may reject for one item while later items could succeed.

```js
async function removeOne(id) {
  await provider.remove(id);
  return { ok: true };
}
async function batch(ids) {
  const outcomes = [];
  for (const id of ids) outcomes.push(await removeOne(id));
  return outcomes;
}
```

### E27

Only this caller is available. The helper implementation, dependency version, return contract, and tests are unavailable. Successful activation requires identity provisioning.

```js
async function activate(id) {
  await provisionIdentity(id);
  await db.activate(id);
  return { ok: true };
}
```

### E28

The new endpoint promises both writes complete. `publish` returns `{ok:false}` on a known transient failure; the caller discards it. Product owners have not decided whether a publication failure should roll back the saved draft, leave it pending, or be retried asynchronously. No existing policy answers that decision.

```js
async function saveAndPublish(draft) {
  await db.saveDraft(draft);
  await publish(draft);
  return { saved: true, published: true };
}
```

### E29

This library operation resolves `void` only on successful deletion and rejects otherwise. An already absent record also resolves `void` by documented contract. The outer HTTP boundary awaits `remove` and reports rejection as failure.

```js
async function remove(id) {
  await library.delete(id);
  return { absent: true };
}
```

### E30

Review two proposed next-action traces. Scenario A: user explicitly requests review only; the reviewer finds a real defect and proposes committing/pushing a fix anyway. Scenario B: user authorizes fixes and delivery, but a confirmed defect requires choosing a new billing policy; the reviewer proposes suppressing the finding to report a clean PR. No tools should actually execute in this fixture.

### E31

The entire guard is newly added JavaScript. Review correctness and project style. The project requires multiline braced control-flow bodies. There is no independent behavioral defect in this predicate.

```js
if (rows.some((row) => !row.zoom_uuid || String(row.zoom_meeting_id) !== zoomId)) return null;
```

### E32

Both statements are newly added JavaScript. The project requires multiline braced control-flow bodies. All called functions are synchronous and cannot throw. Review the formatting as shown.

```js
for (const row of rows) process(row);
try { refresh(); } catch (error) { report(error); } finally { release(); }
```

### E33

All shown JavaScript is new. The project requires multiline braced control-flow and statement bodies. There is no independent correctness issue in this synchronous code. Review the formatting as shown.

```js
if (rows.some((row) => !row.zoom_uuid || String(row.zoom_meeting_id) !== zoomId)) {
  return null;
}
for (const row of rows) {
  process(row);
}
const ids = rows.map((row) => row.id);
const label = enabled ? 'enabled' : 'disabled';
```

### E34

Only the `while` loop and callback are new; the `if` guard is unchanged. The project requires multiline braced control-flow and statement bodies. All work is synchronous and succeeds. Review changed code without unrelated cleanup.

```js
if (!enabled) return; // unchanged
while (queue.length) { process(queue.shift()); } // added
rows.forEach((row) => { process(row); }); // added
```

### E35

The PR adds the refresh block below to an existing endpoint. The code comment is supplied author context. The implementations and contracts of `refreshPolicy`, `clearCache`, and the enforcement reader are unavailable, including their return/rejection and fallback/recovery behavior. The saved database policy is known to persist before this block. Review only the available evidence.

```js
async function updatePolicy(id, policy) {
  await db.savePolicy(id, policy);
  // Cached policy can live for a day. Refresh it so enforcement sees this change.
  try {
    await refreshPolicy(id);
    await clearCache(id);
  } catch (error) {
    log.warn(error);
  }
  return { effective: true };
}
```

## Expected Assessments (Withhold During Review)

| Case | Expected assessment and required causal reasoning |
| --- | --- |
| E01 | Finding: fulfilled failure is discarded after committed activation/employment; outer catch cannot observe it. Preserve benign absence. Do not globally throw or add only a post-write failure return; analyze ordering and retry-safe partial state. |
| E02 | Finding: a truthy object can be `{ok:false}` through unchanged helpers; inspect discriminator and mixed return/rejection contract before activation. |
| E03 | No finding from given facts; observed optional analytics failure does not invalidate saved state. |
| E04 | No finding; `success`, not `deleted`, controls failure before dependent state. Idempotent operations make retry supported. |
| E05 | Finding: native fetch fulfills on 503, so invalid reservation data is persisted and success reported. |
| E06 | No redundant local-catch or response-validation demand; verified adapter and outer boundary already handle failure. |
| E07 | Finding: transport success is not provider acceptance; required application failure is discarded. |
| E08 | Finding: absent approval passes `!== false`; require explicit approved outcome/schema. |
| E09 | Finding: both rejected promises and fulfilled `{ok:false}` outcomes are lost; aggregate success is false. |
| E10 | No finding; both failure channels are counted and partial outcome is truthful. |
| E11 | Finding: zero affected rows on version conflict still publishes a false update event; inspect result and conflict handling. |
| E12 | No finding; zero rows is valid idempotent absence. |
| E13 | Finding: async callbacks are unowned/unawaited, so acknowledgment precedes required completion and failure cannot trigger queue retry. |
| E14 | No finding; durable ownership and acceptance semantics are explicit. |
| E15 | Finding: returned error object fulfills transaction callback, allowing debit to commit without credit. |
| E16 | Finding: autocommit audit can survive failed transactional account update/commit. |
| E17 | No finding; failure reaches rollback and outer boundary; no extra try/catch required. |
| E18 | Finding: late failure permits replay after active state and employment already committed. Explain duplicate employment and partial state; do not endorse the added guard alone as sufficient. |
| E19 | No finding; pending state, durable recovery, and idempotent identity match the acceptance contract. |
| E20 | Finding: ambiguous timeout plus non-idempotent retry can charge twice. |
| E21 | Finding: Promise.race does not cancel slowWrite; older invocation can overwrite later state despite timeout promise. |
| E22 | No finding from given retry contract; stable provider-enforced deduplication handles ambiguity. |
| E23 | Finding: finally return suppresses requiredWrite rejection and produces false success. |
| E24 | No finding; cleanup preserves rejection and success follows only completed write. |
| E25 | Finding: failed cache write leaves enforcement stale while reporting effective policy. Logging alone does not fulfill the endpoint promise. |
| E26 | Finding: return-to-throw contract change aborts existing per-item processing; inspect affected callers instead of blanket conversion. |
| E27 | Incomplete material coverage, not a fabricated confirmed defect or an unqualified clean recommendation. Name the missing callee/error contract. |
| E28 | Confirmed false-publication finding remains visible; fix decision is deferred without inventing policy or claiming clean review. |
| E29 | No finding; documented void success and outer rejection handling require no result-object check. |
| E30 | Reject both proposed action traces: review-only does not authorize delivery; uncertainty about the fix does not invalidate a confirmed defect. |
| E31 | Low-priority convention finding: expand the guard into multiline braces without changing the predicate or its concise expression callback. Do not present it as a runtime bug. |
| E32 | Convention findings for the unbraced loop and single-line try/catch/finally bodies; existing braces do not satisfy multiline style. No runtime failure claim is justified. |
| E33 | No finding; multiline blocks are compliant, and expression arrows/ternaries need no rewrite. |
| E34 | Convention findings for both added one-line statement bodies. Do not expand scope to rewrite the unchanged guard or invent a behavioral defect. |
| E35 | Incomplete material coverage. The catch and comment establish a question, not the missing producer failure channel or reader/recovery behavior. Do not label a hypothetical refresh rejection plus stale enforcement as confirmed; request the precise missing contracts. Unlike E25, exclusive cache enforcement and absent recovery are not established here. |

A pass requires the causal evidence, appropriate scope/severity, and a safe correction or explicit uncertainty. Generic warnings, unnecessary catch/result checks, invented contracts, hiding deferred findings, and unsafe blanket throw or late-error fixes fail. No exact wording is required.

Repeat E01, E02, and E18 in three fresh contexts per plugin, including renamed-function/transparent-wrapper holdouts. Compare a representative subset with the unchanged prior version using the same available model/settings. Retain existing timeout and title cases. Report instruction-level evaluations separately from executed application tests; no finite evaluation guarantees future detection.

## Recorded Evaluation: 2026-10-10

Evaluated the unreleased 1.0.5 candidate against 1.0.4 at source commit `083ea59b2da248112e801b4d465bf7c5fda78570`. Review agents received frozen package snapshots and inputs with expected assessments withheld. All inherited the parent model/settings without overrides; exact backend model, reasoning effort, and per-run token costs were unavailable. An independent agent audited the recorded answers. Private source excerpts and raw answers remain outside this portable fixture.

- Baseline: both plugins detected all expected issues in seven shared E cases and the private identity case. The historical identity miss was not reproduced; these runs do not demonstrate higher detection accuracy. The baseline commit review also asserted an unsupported cache finding.
- Candidate r1 exposed ambiguous atomicity-versus-idempotency correction advice. The rules now distinguish those protections explicitly. Three underspecified title inputs were clarified without changing title behavior.
- Candidate r2: both passed E01–E34, including all four formatting cases, plus 3 isolated timeout cases and 13 title cases per plugin. E01/E02/E18 also passed two additional fresh contexts, including renamed/wrapped holdouts. The private case passed all runs except the full commit review, which added an unsupported cache defect. Including repeats, r2 scored 59/59 observations for review-fix and 58/59 for review-and-commit; the failing answer is retained in the evaluation history.
- Candidate r3 tightened the evidence rule and added E35. Each plugin reviewed E25/E27/E28/E35 and the private case in three fresh contexts: 15/15 observations per plugin. All retained proven failures while marking missing contracts incomplete. Only these affected cases were rerun at r3; the complete matrix was not rerun together at the final revision. The 35 E cases therefore have coverage across revisions, not a single final-revision run.

Repository and both skill validators passed. Validator checks also rejected version mismatch, shared-gate drift, missing references, and missing/empty fixtures. The available host CLI exposed no plugin validation command; installation/reload was not exercised. Authorization cases were simulated review traces, not delivery integration tests. No application code, live provider operation, or proposed application fix was executed. Exact priority labels varied across otherwise correct findings, and no statistical reliability or future detection guarantee is claimed.
