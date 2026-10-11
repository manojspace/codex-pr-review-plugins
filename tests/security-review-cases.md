# Security Review Cases

All identities are synthetic. Each case states its own pinned reachability and trust contract. Supply only Inputs to fresh review-only reviewers; withhold Expected Assessments. Ask for actor, entry point, violated boundary, consequence, severity rationale and safe correction. No live requests or secrets are needed. A severe-sounding API name alone never establishes P0.

## Inputs

### SEC01

Public API uses requireLogin for every route. Any logged-in member can reach /members/reactivate; only sibling /members/deactivate calls can(user,'members','manage'). The PR adds external identity deletion inside reactivate for a target selected by body memberId, including another member. The UI hides this action for non-managers. No downstream permission check exists; deletion disables the victim's login.

### SEC02

The PR registers a route after requireLogin. It loads the selected record within the authenticated tenant, rejects a mismatched projectId, and awaits a fail-closed manage permission check before every side effect. Tests exercise both denial and ownership mismatch through the real router.

### SEC03

A new endpoint decides whether to send client invites using req.body.isRestrictedProject. The database Project.restricted is the authoritative privacy setting; restricted projects must never send external invites. A logged-in project editor may invoke this endpoint but may not override restriction. Sending is possible by passing false; no lower-level policy check exists. One old sibling trusts the same body flag.

### SEC03C

A new invitation endpoint authenticates an editor, loads their project, and derives restriction exclusively from Project.restricted. It ignores any body isRestrictedProject value and rejects external invites for restricted projects. The send function runs only after this check.

### SEC04

The new staging identity-cleanup path uses a committed configuration selecting a production identity project. The runtime's existing credential can delete identities in that project; a supplied staging trace resolves to production. Staging lifecycle events must not change production identities. Values and credentials are intentionally omitted.

### SEC04C

The new staging identity-cleanup path uses an environment-scoped secret whose principal can delete only staging identities. Cleanup enablement defaults false, is explicitly enabled only for staging, and validates target project against the deployed environment before deletion. Supplied resolution evidence matches staging.

### SEC05

A changed server template interpolates an editor-controlled display name into HTML. Every supplied rendering consumer runs the result through the approved sanitizer that removes scripts, event attributes and unsafe URLs before assigning HTML. The sanitizer configuration and all consumers are included; no bypass exists in this fixture.

### SEC05H

A changed server template interpolates an editor-controlled display name into HTML. The public profile consumer assigns it directly to innerHTML without a sanitizer or escaping. A supplied name containing an image onerror handler executes as a viewer; authenticated session actions are available to that origin.

### SEC06

In a public Express router, requireSession is registered at line 30. The PR adds POST /bookings/:id/move at line 18; it loads any known booking ID and updates startsAt without ownership checks. There is no upstream authentication gateway, guessing defense, or downstream authorization; IDs appear on public confirmation pages. The effect is changing another person's appointment, not financial transfer or administrative access.

### SEC06C

A public Express router registers requireSession at line 10, then POST /bookings/:id/move at line 18. The handler loads the booking only within the authenticated tenant and awaits assertBookingAccess before updating startsAt. Denials are fail-closed; no earlier alternate route exists.

### SEC07

Only file modes change: docs/setup.md from 100644 to 100755, and scripts/release.sh from 100755 to 100644. CI invokes ./scripts/release.sh directly on Linux; it does not call bash or restore its executable bit. The script's text is unchanged.

### SEC07C

Only scripts/release.sh changes from 100755 to 100644. Every supplied caller runs bash scripts/release.sh and the archive policy intentionally stores scripts without executable bits. Script text and caller behavior are unchanged.

### SEC08

A changed authenticated report route loads tenant-specific data. Its shared cache key is 'report:' + reportId, omitting tenantId; report IDs are tenant-local and collide. The cache is read before the database tenant predicate. A tenant B request receives tenant A's cached report for ID 7 in the supplied trace.

### SEC08C

An authenticated report route has tenant-local report IDs. Cache keys include trusted session tenantId and reportId; database queries include that tenantId, and permission checks precede both cache access and response. Supplied requests for ID 7 in different tenants use distinct entries.

### SEC09

The webhook provider signs the exact raw HTTP body bytes. A new JSON parser executes first and the verifier hashes JSON.stringify(req.body). A supplied valid payload includes insignificant whitespace; reserialization differs and verification rejects it. All effects are after verification.

### SEC09C

The webhook provider signs raw body bytes. The handler verifies the captured raw buffer with the correct secret and constant-time comparison, enforces timestamp expiry and atomically deduplicates event IDs, then parses and dispatches. No middleware transforms the captured buffer.

### SEC10

A new webhook verifies a correct signature but ignores the signed timestamp and event ID. The provider contract allows a 5-minute window and unique event IDs. A captured signed request from yesterday can be replayed; every accepted replay inserts another credit. No database deduplication exists.

### SEC10C

The new webhook verifies raw-byte signatures, enforces the signed 5-minute window with documented tolerance and atomically inserts a unique event ID with the credit in one transaction. A duplicate returns the prior result; stale requests are rejected before mutation.

### SEC11

A new transfer handler verifies object ownership, awaits an external lookup, then updates by object ID only. Ownership can change concurrently through another supplied endpoint. A controlled trace transfers ownership between check and mutation, yet the old owner's update succeeds; no row lock spans the check or conditional predicate exists.

### SEC11C

A new transfer handler authenticates the caller, reads the object, performs a remote lookup outside its transaction, then conditionally updates by ID, ownerId and captured revision. Ownership transfer increments revision; zero affected rows returns conflict without side effects.

### SEC12

A URL preview service accepts HTTPS URLs from users. It rejects private IPs only at the first URL, follows redirects automatically, and can access an internal metadata endpoint. The supplied public URL redirects to a private address and the response containing a service token is returned. No network egress boundary blocks the second hop.

### SEC12C

A URL preview service uses an established egress client enforcing public-only resolved IPs on every connection and redirect, disallowing alternate schemes and credentials, pinning the checked address per connection and applying a redirect limit. Network policy blocks metadata/private ranges; output is sanitized text.

### SEC13

A changed update endpoint authenticates a normal member but spreads req.body into Member.update. The accepted ORM attributes include isAdmin and tenantId. Members may edit only displayName; a supplied request with isAdmin:true persists admin privileges. No schema allowlist or downstream filtering exists.

### SEC13C

A changed member update endpoint authenticates the owner, validates an input schema with only displayName and rejects extra fields. It constructs Member.update({ displayName }) with a tenant/owner predicate. isAdmin and tenantId cannot reach the write.

### SEC14

A changed search endpoint concatenates query.name into a SQL WHERE string. The supplied driver executes that raw string; no parameter binding or escaping occurs. A controlled quote-containing input changes the predicate and returns other tenants' rows despite an adjacent tenant literal.

### SEC14C

A changed search endpoint uses driver-bound parameters for both query.name and trusted session tenantId. The supplied driver sends values separately from the SQL statement; quote-containing inputs remain a literal name. Results are tenant scoped.

### SEC15

A PR shows a new admin-like JSON configuration filename and a token-shaped string in a test fixture. Runtime credential loading, token validity, deployed environment and reachable consumers are unavailable. The string is explicitly synthetic in the fixture generator, but no deployment trace is supplied.

### SEC16

A new authenticated export endpoint joins the user-supplied filename to /srv/exports and reads it. The supplied path library normalizes ../ segments; no containment or allowlist check exists. The service account can read /srv/private/config.json, and a controlled request for ../private/config.json returns that file. Authorization grants only the caller's export files.

### SEC16C

An export endpoint accepts only an opaque export ID, loads it within the authenticated tenant and maps it to a server-owned file handle. User strings cannot supply paths; the file store enforces root containment including symlinks. A request for ../private/config.json fails input validation before access.

### SEC17

A new authenticated endpoint accepts body.userId and loads that user's private preferences without comparing to session identity or checking administrative authority. Any ordinary user can request another valid userId. A controlled trace returns the other user's private notification destinations.

### SEC17C

An authenticated preferences endpoint treats body.userId as an optional target selector. It defaults to session userId; a different target requires the supplied fail-closed admin authorization scoped to the target tenant. Ordinary cross-user requests are rejected before the private record is loaded.

## Expected Assessments (Withhold During Review)

| Case | Expected assessment |
| --- | --- |
| SEC01 | Confirm authorization defect: authenticated non-manager can disable another member's access. Guard before loading/destructive effects and scope the target. P1 is supportable from this concrete impact; do not label unconditional P0 or dismiss the unchanged missing guard. |
| SEC02 | No authorization finding; account for guard order, ownership and fail-closed checks. |
| SEC03 | Confirm request-controlled policy bypass. Read authoritative project restriction under the existing authorization model; the unsafe sibling does not justify the copy. |
| SEC03C | No request-controlled restriction finding. |
| SEC04 | Confirm environment crossover with deletion impact; cite configuration/trace without exposing values. Select an environment-scoped credential/project and validate cleanup enablement before effect; no invented committed-secret claim. |
| SEC04C | No cross-environment deletion finding. |
| SEC05 | No demonstrated stored-XSS finding; trace sanitization through the real sinks. |
| SEC05H | Confirm stored XSS at the unsanitized sink. Escape the text interpolation or use the established sanitizer at all sinks; do not rely on sanitization in other consumers. |
| SEC06 | Confirm unauthenticated cross-owner mutation, with actor, entry point and impact. Register behind session guard and assert booking access before mutation. Material/blocking severity is justified; unconditional P0 is not. |
| SEC06C | No guard-order or ownership finding. |
| SEC07 | Confirm direct CI execution failure for the release script; restore its executable bit. No defect inferred for executable documentation. |
| SEC07C | No direct-execution failure on supplied callers. |
| SEC08 | Confirm cross-tenant cache disclosure; include trusted tenant identity and relevant authorization dimensions in the cache namespace. Do not rely on the later database filter. |
| SEC08C | No tenant cache isolation finding. |
| SEC09 | Confirm valid webhook rejection from transformed bytes; preserve/verify the raw body under the provider contract before parsing. Do not claim authentication bypass without evidence. |
| SEC09C | No signature-byte or replay finding. |
| SEC10 | Confirm signed-request replay causes duplicate credits. Enforce signed expiry with the documented clock tolerance and durable idempotency/unique event ownership. |
| SEC10C | No replay credit finding. |
| SEC11 | Confirm check/mutation race. Use an atomic tenant/owner/revision predicate and handle zero affected rows, or a justified locking protocol; a second non-atomic check alone is insufficient. |
| SEC11C | No ownership race under the supplied conditional update. |
| SEC12 | Confirm SSRF/token exposure. Validate every resolved redirect destination and prevent DNS/rebinding races with the established network client; do not quote token values. |
| SEC12C | No demonstrated redirect SSRF finding. |
| SEC13 | Confirm mass-assignment privilege escalation. Build an explicit allowlisted update and enforce ownership; severity follows this escalation, not a universal P0 rule. |
| SEC13C | No mass-assignment finding. |
| SEC14 | Confirm SQL injection/tenant data exposure. Use driver parameter binding and retain trusted tenant scope; do not suggest hand-escaped concatenation. |
| SEC14C | No SQL injection finding. |
| SEC15 | Do not claim leaked live credentials or production exposure from shape/filename. Identify the smallest missing runtime/environment evidence if material; avoid echoing secret-shaped values. |
| SEC16 | Confirm path traversal outside the authorized export root. Resolve a server-owned export identifier to an authorized file or enforce canonical containment/ownership with symlink-safe access; do not trust filename normalization alone. |
| SEC16C | No request-controlled path traversal finding. |
| SEC17 | Confirm request-controlled identity disclosure. Derive self identity from the trusted session or validate an authorized target selector with ownership/role checks before loading/responding. |
| SEC17C | No identity-selection authorization finding; a request parameter is not automatically unsafe when its authority is validated. |
