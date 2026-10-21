# Consistency and Frontend Review Cases

Each case supplies its trusted instructions separately from unchanged examples. User-required multiline braces apply universally to newly changed statement bodies where formatting is assessed, while expression arrows and unchanged code remain valid controls. Supply only Inputs; withhold Expected Assessments. Ask for scoped behavior/convention findings, measured evidence and conservative corrections; never execute delivery.

## Inputs

### C01

A service grows from 2,350 to 2,548 lines by adding two cooperating exports of 140 and 58 lines for a new activity type. Trusted instructions place new activity orchestration in existing per-feature modules. The supplied import graph permits services/activity/new-type.js without a cycle. Runtime logic is otherwise correct; relocation requires a public export decision.

### C02

A 1,116-line provider adapter gains a 66-line patchEvent beside existing create/update/delete operations. All four use the same private client lifecycle and serializer; extracting patchEvent would expose those internals. No trusted instruction requires a separate module; runtime contracts are satisfied.

### C03

A routes file grows from 862 to 1,015 lines; 128 added lines orchestrate billing rather than HTTP translation. Trusted instructions explicitly require new business orchestration in services. An older handler also orchestrates billing, but is unchanged. The existing billing service can host the new operation without an import cycle.

### C03C

A routes file grows from 862 to 1,015 lines through declarative endpoint schemas and route bindings. Trusted instructions put business orchestration in services, and the new handlers delegate it to the existing billing service. No duplicate policy or runtime issue is present.

### C04

A new provider operation copies a 24-line rejected-host fallback from an existing helper. Trusted policy requires the same fallback and warning shape for both operations. The copy omits the warning and returns 'unknown' instead of the required cached host; the available helper already supports this operation. No runtime outage trace is supplied.

### C04C

A new provider operation delegates its rejected-host fallback to the existing helper, whose supplied contract returns the required cached host and records the approved warning. It passes the same supported arguments as neighboring operations.

### C05

A third inline id-or-UUID lookup appears. Trusted instructions require the existing shared lookup helper. Supplied helper accepts decimal numeric IDs and UUID strings; all valid inputs in the new route match that contract. The new inline copy uses Number(value) where the helper preserves UUID strings; a supplied UUID lookup consequently misses a record.

### C05C

A new route calls the existing id-or-UUID helper with its validated decimal-ID/UUID input. The helper preserves UUID strings and normalizes numeric IDs as specified. Trusted reuse instructions and lookup behavior are both met.

### C06

Two explicitly supplied PRs in different services add the same 67-line serializer (equal blob hashes); both serialize writes to one table. Trusted series policy permits mirrored files when annotated with the counterpart and covered by a sync check, but neither new copy has either. Centralizing a package is not presently supported.

### C06C

Two services intentionally mirror a 67-line serializer for one table. Trusted policy permits this with a counterpart header and CI equality check; both are supplied and exact-head CI passes. Extracting a shared runtime package would add an unsupported dependency.

### C07

Most sibling provider catches log { error, params }, where params contain private event content. Trusted instructions forbid payload logging and require an eventId plus approved redacted error. The new helper logs precisely { error, eventId } through that serializer.

### C08

A supplied scoped inventory counts 670 approved redacted { error } calls and 30 legacy error.message calls. Trusted policy requires stable memberId and the approved error serializer, forbidding email fields. A new catch logs { email, error:error.message }; messages may contain personal data and stack/code are lost.

### C08C

A new catch logs memberId with the approved redacted error serializer preserving code/stack. Trusted policy forbids email fields; 30 old sibling calls still use error.message. The new catch follows the documented policy.

### C09

A 1,647-line component gains 114 lines: a 19-line request helper, 18-line retry flow and 24-line render branch plus supporting state. Trusted instructions place reusable request/retry policy in the existing useRecordActions hook. The same retry policy is already implemented there for sibling screens, and this screen can use it without changing render ownership. No new imports or heavy UI are added; three old children are lazy-loaded.

### C09C

A 1,647-line component gains 14 lines wiring the existing useRecordActions hook to an additional action. All request/retry policy remains in that hook and render ownership is unchanged. No new large dependency or instruction violation exists.

### C10

A 900-line page gains a 120-line optional chart dialog and four imports, including a new 220-kB compressed chart package. A supplied bundle analysis proves this adds 220 kB to the initial route chunk; the dialog opens only from a toolbar. Trusted performance policy requires optional heavy dialogs use the existing retrying import wrapper, Suspense and local error boundary. A default-export dialog module fits the existing pattern without cycles.

### C10C

A page gains a 120-line chart dialog already loaded via the existing retrying import wrapper, Suspense and local error boundary. Bundle analysis confirms its heavy dependency is absent from the initial route chunk. Focus and loading states are covered by the supplied interaction check.

### C11

A 412-line login page gains a 30-line pure error-code mapper. The form is essential first-paint content; no heavy import is added. Trusted policy recommends deferring optional heavy UI only. A proposed reviewer action lazy-loads the entire login form solely because of file growth.

### C12

The user's mandatory rule requires multiline braces for every newly changed control-flow or statement body. ESLint curly is ['error','multi-line'] but does not override that rule. The only added line is `if (!user) return null;`; its predicate and return are semantically correct.

### C12C

The user's mandatory rule requires multiline braces for newly changed control-flow/statement bodies. The PR adds a multiline braced if with return null inside, plus `const ids = rows.map((row) => row.id);` and a ternary label expression. An old unbraced guard is unchanged.

### C13

A new timestamp formatter is copied from the approved UTC formatter but drops the explicit timeZone:'UTC'. The supplied runtime default zone is America/Los_Angeles, while the export contract requires UTC. Parser still interprets the incoming instant correctly; a controlled export differs by hours.

### C13C

A new export reuses the approved parser for instants and UTC formatter. Runtime default timezone is America/Los_Angeles, but the formatter explicitly uses UTC and the supplied output matches the contract.

### C14

A new activity handler is exported and invoked only through a registry. Trusted module contract requires registering each activity kind; the PR adds kind 'archive' but omits its entry. The supplied dispatcher returns unsupported for unregistered kinds, and no auto-discovery occurs.

### C14C

A new archive handler is exported and listed under archive in the sole activity registry. The supplied dispatcher resolves the entry and passes its supported payload; a focused test exercises registry dispatch.

### C15

A new profile panel fetches by selected user. User A's request starts, selection switches to B, B's request resolves first, then A's slower response unconditionally sets the same state. A supplied trace displays A's profile under B's heading. No cancellation, request token or identity check exists.

### C15C

A profile panel records a request token and selected user ID for each fetch; completion updates state only when both still match. On A-to-B switching, the supplied late A response is ignored and B remains displayed. Unmount invalidates the token.

### C16

A new optimistic editor submits versions 1 then 2 before either completes. Version 2 succeeds, then version 1 fails; its catch restores the snapshot captured before version 1 unconditionally. A supplied trace loses the successfully confirmed version 2 UI value.

### C16C

An optimistic editor tags mutations by version. A failed older mutation rolls back only if it still owns the current optimistic state; otherwise it reconciles without overwriting a newer confirmed version. The supplied version-2-success/version-1-failure trace preserves version 2.

### C17

A changed payment button can submit twice before isSubmitting state is reflected. The backend has no idempotency constraint and each request creates a new charge; a double-click trace creates two charges. A spinner appears after both requests start.

### C17C

A payment action creates one stable operation ID per intent and the backend atomically deduplicates it with payload matching. A synchronous client guard prevents overlapping submits; a supplied double click returns the same result and only one charge.

### C18

A new delete flow tells users 'Nothing changed; retry' after a transport timeout. The supplied backend trace committed deletion before losing its response; repeating the operation also deletes the next queued item because the endpoint selects the queue head rather than a stable item ID.

### C18C

A delete flow uses stable item and operation IDs with backend deduplication. On lost response it shows 'Checking result' and polls authoritative operation state; retry is offered only for a known unapplied operation.

### C19

A new client enables a paid action when Date.now() is before subscription.expiresAt. Backend trusts the client enabled flag and performs the action without checking subscription state against server time. A supplied request with a modified client clock and enabled:true succeeds after expiry.

### C19C

Client countdown uses Date.now() for display only. Backend independently validates current entitlement using server time before the paid action and ignores the client enabled flag. A supplied expired request is denied.

### C20

A changed modal opens visually but leaves focus on background controls, exposes no accessible name, and has no keyboard close mechanism; the supplied keyboard trace cannot reach its action. Trusted accessibility contract requires labeled dialog semantics, contained focus, Escape and restored opener focus.

### C20C

The new modal uses the existing named dialog primitive. Supplied keyboard/screen-reader evidence confirms initial/contained focus, Escape close, labels and focus restored to the opener. Loading, empty, failure and retry states are textually accessible.

### C21

A large component adds 20 lines of a new action. Trusted structure instructions, runtime behavior, nearby hook contracts and bundle impact are unavailable. An author calls the file 'too big' without measurements beyond its 1,500 existing lines.

### C22

The PR adds a member-selection screen whose Save button is disabled when selectedIds is empty. The supplied backend contract accepts an empty array and clears all members, while nonempty arrays replace membership. The product brief says only 'edit membership'; no acceptance criteria, supported empty-state workflow, earlier screen behavior or user requirement to clear every member is supplied. Nonempty submissions work correctly. Assess whether backend capability alone proves a defect in this new screen.

### C22H

The PR adds a member-selection screen whose Save button is disabled when selectedIds is empty. The supplied backend contract accepts an empty array and clears all members, while nonempty arrays replace membership. Approved acceptance criteria require users to remove all members from this screen and save that empty selection. A supplied interaction trace removes the last member, leaves Save disabled and sends no request; no alternate clear action exists. Nonempty submissions work correctly.

## Expected Assessments (Withhold During Review)

| Case | Expected assessment |
| --- | --- |
| C01 | One non-blocking structure recommendation grounded in the instruction/responsibility boundary and measured growth, naming the target/cycle evidence. Treat extraction as decision-dependent; line count alone is not a runtime defect. |
| C02 | No size-only structure finding; cohesive adapter growth is justified. |
| C03 | Recommend moving the changed orchestration to the existing service, citing the instruction. Do not demand unrelated cleanup or label the older handler a new defect. |
| C03C | No structure finding solely from growth. |
| C04 | Confirm policy/recording drift from copied logic; reuse the existing compatible helper. Do not invent a demonstrated outage or a generic abstraction. |
| C04C | No copy-drift finding. |
| C05 | Confirm copy/lookup behavior drift and use the existing helper. Trace numeric-versus-string semantics; do not replace with an incompatible numeric-only helper. |
| C05C | No lookup-copy finding. |
| C06 | One series-level P3 maintenance finding naming both copies; add the required counterpart/sync mechanism or obtain a deliberate policy decision. Do not mandate a new shared package. |
| C06C | No duplication-only finding. |
| C07 | No parity finding; trusted policy outranks unsafe sibling practice. Never suggest restoring payload logging. |
| C08 | Confirm privacy/recording inconsistency using policy plus serializer contract; counts are supporting evidence, not authority by themselves. Use memberId and the approved redacted serializer. |
| C08C | No consistency finding from legacy exceptions. |
| C09 | Recommend reusing the existing hook/request boundary based on duplicated policy, not file size. No component extraction or new lazy-loading requirement; preserve UI behavior. |
| C09C | No size-only or mandatory extraction finding. |
| C10 | Recommend the measured optional-dialog split using the existing loading/error pattern. Do not generalize a line threshold into mandatory lazy loading or change bundler configuration. |
| C10C | No bundle-splitting or mandatory re-extraction finding. |
| C11 | Reject unsupported first-paint lazy loading; no structure finding is established by these numbers. |
| C12 | Low-priority convention finding: expand to a multiline braced if. Preserve the universal user rule; do not call it a runtime defect or let weaker lint configuration waive it. |
| C12C | No braces finding: expression arrows/ternaries are permitted and unrelated unchanged guards stay untouched. |
| C13 | Confirm copied formatter drift at the output boundary. Reuse the existing UTC formatter; do not invent a parsing defect. |
| C13C | No formatter/parsing drift finding. |
| C14 | Confirm unreachable new responsibility; add the existing registry entry and validate dispatch. No new registry abstraction needed. |
| C14C | No omitted-registration finding. |
| C15 | Confirm stale response overwrites current selection. Use an existing request ownership/token guard or cancellation with a completion guard; do not label every completion after unmount a memory leak. |
| C15C | No stale-result finding or invented memory leak. |
| C16 | Confirm outdated rollback overwrites newer successful state. Tie rollback to the owning optimistic version or reconcile authoritative state; don't roll back unrelated edits. |
| C16C | No concurrent optimistic rollback finding. |
| C17 | Confirm duplicate-submit consequence. Use stable server-side operation idempotency plus an appropriate synchronous client guard; disabling after render alone cannot guarantee one charge. |
| C17C | No duplicate-charge finding. |
| C18 | Confirm false outcome/retry advice with further destructive effect. Return/reconcile by stable operation/item identity and represent uncertainty; do not tell users to blindly retry. |
| C18C | No unsafe retry-copy finding. |
| C19 | Confirm client-clock authorization bypass at the backend boundary. Enforce subscription/time on the server; client countdown remains presentation only. |
| C19C | No client-clock authorization finding. |
| C20 | Confirm inaccessible modal interaction. Restore the required accessibility behaviors, reusing an existing accessible dialog primitive if available; no unrelated visual redesign. |
| C20C | No modal accessibility finding on supplied evidence. |
| C21 | Do not confirm a structural/runtime defect or mandate extraction/lazy loading from size alone. State which responsibility/convention evidence would justify a recommendation. |
| C22 | No confirmed product defect from backend support alone. Identify the missing UI requirement/empty-state contract as a question if material; do not prescribe enabling empty submissions merely because the endpoint supports them. |
| C22H | Confirm the required clear-all workflow is blocked by the empty-selection guard. Permit the supported empty array for this explicit workflow while retaining unrelated input/authorization checks; name the screen guard and accepted backend contract. |
