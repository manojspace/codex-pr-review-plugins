# Failure Recording Review Cases

Synthetic pinned contracts are authoritative only for their stated case. Each case is independent. Supply only the Inputs section to a fresh review-only reviewer; withhold Expected Assessments. Ask for evidence, consequence, safe correction and uncertainty. These prose snippets test behavior; formatting is assessed only where explicitly requested. No live services or delivery actions are needed.

## Inputs

### R01

The new optional analytics catch follows an atomic idempotent order save. Logger version 2 serializes Error objects only at error/critical levels; at warn, JSON serialization produces {}. Approved warning examples use errorMessage and code. New code emits logger.warn('Analytics unavailable', { orderId, error }); analytics failure cannot affect save success.

### R02

The new optional analytics catch follows an atomic idempotent order save. Logger version 3 serializes Error objects with redacted message, code and stack at every level. Approved warnings use { orderId, error }. The new catch emits that exact shape.

### R03

A new retireIdentity(member, operation) catch is reached from deactivation and reactivation. Trusted logging policy requires stable memberId, operation and a redacted Error serializer preserving code/stack; emails are forbidden. It instead logs { email: member.email, error: error.message } with text 'Deactivated'. Error.message can contain an email. The caller already safely handles the returned failure.

### R03C

A new identity-retirement catch is used by deactivate and reactivate. Trusted policy forbids email logging and requires memberId, operation, and a redacted Error serializer preserving code/stack. The catch logs those fields with the actual operation; callers safely handle its returned failure.

### R04

An upstream permission service outage makes this new endpoint return a failed outcome. The service's only outage alert counts error-level records; trusted neighboring catches log { error, resourceId } using a redacting serializer. The new catch logs warn with only resourceId, then returns an actionable reconnect message. There is no lower-level error record.

### R04C

A new upstream-permission catch returns failure and logs error with resourceId and the approved redacted cause. The error-rate monitor covers this service and this event. The UI maps the failure code to a reconnect action.

### R05

A provider error body can echo an attendee email, and trusted policy forbids those emails in logs. The new catch records operationId, HTTP status and stable provider code through the approved structured logger; its monitor keys on provider code. The failure outcome is handled by the caller.

### R06

A changed helper returns { ok:false, message:'PERMISSION_DENIED' }. Its supplied UI consumer renders side + ': ' + reason then 'Retry finishes this operation'. The contract requires reconnecting an account; retry alone cannot help. Existing error mapping turns PERMISSION_DENIED into a reconnect action but this call bypasses it.

### R06C

A helper returns a failed envelope with code PERMISSION_DENIED. The supplied UI consumer uses the existing mapping to 'Reconnect your account' and offers the reconnect action. Retrying without reconnect cannot help and no retry is offered.

### R07

Supplied backend and frontend snapshots are both in the requested review scope. The backend now returns an actionable, validated user-safe message for a recoverable failure. The unchanged request helper rejects with that message; the changed catch replaces it with 'Failed'. Trusted UI policy requires preserving these approved actions.

### R08

Both backend and frontend snapshots are supplied. The backend returns a validated user-safe recovery message, the request helper rejects with it, and the new catch renders it as text using the approved error component. No raw HTML rendering occurs.

### R09

The transaction library awaits/catches only promises returned by afterCommit callbacks. Startup explicitly exits on unhandledRejection. A new callback calls void notifyPartner(record) without returning it; notifyPartner rejects on HTTP failure and has no internal catch. Notification is optional after the committed save.

### R10

Startup exits on unhandledRejection and afterCommit only catches returned promises. A new callback starts notifyPartner without awaiting it. The supplied implementation catches every asynchronous rejection, logs approved cause/recordId fields, and always resolves. Notification is optional.

### R11

Express 5.1.0 async route returns the awaited loadReport promise. Rejection is automatically forwarded to the supplied final error middleware, which logs a redacted cause and returns the required failed envelope. The PR adds only the route.

### R12

Express 4.21.2 is installed without async-error patches or wrappers. A new async route awaits loadReport, which rejects; the router does not consume returned promises. Startup exits on unhandledRejection. The final error middleware logs only errors passed to next.

### R13

A required partner-cancel failure must page an operator under the supplied runbook; only critical events with notify:true page. Equivalent catches use that shape plus a redacted error and resourceId. The new catch emits error level with resourceId only. No other failure recorder exists.

### R14

Provider contract defines already-cancelled as benign success. The new handler logs info with resourceId and returns success. Monitoring pages only on critical plus notify:true. The runbook requires pages for failures, not already-cancelled success.

### R15

A worker starts a database transaction, changes an order, then on provider failure inserts failure_state using the same transaction and rolls back. The supplied operational reader depends exclusively on committed failure_state rows; no external recorder exists. After rollback the reader sees no failure.

### R15C

On provider failure the worker rolls back the business transaction and writes failure_state in a separately committed transaction keyed by operation ID; if that write fails the durable job remains retryable. The recovery reader consumes committed failure_state. No provider side effect occurred under this contract.

### R16

A new failure path writes a correlated immutable audit event and an operational error record with the same operation ID. The audit sink never alerts; exactly one alert is emitted by the operational sink. Trusted policy requires both records; messages redact personal data.

### R17

A new catch logs one operational error locally, and the enclosing error boundary logs the same operation again. The supplied monitor pages on every record, without deduplication. A controlled failure emits two pages; trusted policy assigns recording to the boundary.

### R17C

A new catch attaches operationId and rethrows without logging; the enclosing boundary emits one redacted operational error. The monitor pages once per record, and the supplied failure emits one page. Trusted policy assigns logging to the boundary.

### R18

A new catch logs { error } at warn. Logger serializer behavior, monitoring rules, lower-level recording and caller handling are unavailable. One neighboring catch uses error.message; another uses error. No produced log record is supplied.

## Expected Assessments (Withhold During Review)

| Case | Expected assessment |
| --- | --- |
| R01 | Recording finding: cause disappears at warn. Use the established redacted errorMessage/code fields and orderId. No save-semantics finding. |
| R02 | No recording or business-outcome finding; serialization is established. |
| R03 | Confirm lost cause/code, prohibited personal data and wrong operation labeling. Use memberId, operation and the approved serializer; do not invent a caller failure. |
| R03C | No recording finding. |
| R04 | Confirm missing outage signal and cause. Use the established error-level serializer/ID contract; do not claim user-message failure. |
| R04C | No missing outage-signal or cause finding. |
| R05 | No recording parity finding; do not suggest logging the raw body. |
| R06 | Confirm sentinel leakage and false retry advice at producer/consumer boundary. Return a stable code through the established envelope and use the supplied mapping. |
| R06C | No actionable-copy finding. |
| R07 | Producer/consumer finding: approved recovery guidance is discarded. Use the established safe message mapping; do not render arbitrary server text as HTML. |
| R08 | No discarded-guidance or HTML injection finding. |
| R09 | Confirm process termination from an unowned optional rejection. Return/await the promise and catch/log according to optional-failure policy; do not retry the committed save. |
| R10 | No unhandled-rejection finding on supplied implementation; do not demand a business rollback. |
| R11 | No mandatory local try/catch finding. |
| R12 | Confirm failed request and process exit path. Use the existing async wrapper or catch and next(error); no framework-upgrade mandate. |
| R13 | Confirm missing required page and cause; restore the existing critical/notify and redacted cause fields, avoiding duplicate notifications. |
| R14 | No missing-page finding; adding a page would create noise. |
| R15 | Confirm recovery state is rolled back. Roll back business work and persist a minimal failure outcome through an independent durable transaction/outbox protocol with an operation ID; do not claim logging alone satisfies the recovery reader. |
| R15C | No lost-failure-state finding. |
| R16 | No duplicate-alert finding merely because two distinct-purpose records exist. |
| R17 | Confirm duplicate operational paging; retain one owner/correlated record under the supplied contract, without removing an independently required audit trail. |
| R17C | No duplicate-page finding. |
| R18 | Evidence gap; obtain serializer/monitor/ownership contracts. Neither lost fields nor duplicate alerts are confirmed from spelling alone. |
