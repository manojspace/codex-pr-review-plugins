# Security And Trust Boundaries

Load for changed routes, identity/authorization, privileged effects, webhooks, untrusted sinks, credential scope or deployment permissions. Include unchanged entry points reaching a new effect. Use the core outcome trace; stop once effective guards and sink contracts resolve the affected path. Missing material evidence limits the conclusion.

## Identity, Scope And Effects

- Trace the actual route and middleware order to the effect. Establish the actor, authenticated identity, permitted function, resource ownership and tenant scope; authentication alone does not authorize an object or action. Public read-only or intentionally public operations need their actual contract, not invented login requirements.
- Check whether request-controlled IDs are selectors validated against the actor's scope or are incorrectly trusted as identity. Inspect mass assignment and editable fields, including role, owner and tenant fields.
- When ownership can change between check and mutation, establish atomic conditions, locking or another effective guard. A precheck is not enough if a credible race bypasses it; a scoped conditional update can be sufficient.
- Follow tenant/user scope through caches and downstream calls. Compare a shared key that exposes another tenant's result with a scoped key; do not infer a leak merely because a cache exists.

## Untrusted Sinks And Credentials

- Follow changed input to SQL, HTML, URLs, filesystem paths and model writes. Resolve the actual parameterization, escaping/sanitization, URL policy and path containment at the sink. Avoid claims based only on string concatenation or a sanitizer's name.
- For server-side URL fetches, inspect redirects and the effective destination checks when internal-network access is plausible. Guarding only the original URL may not constrain a redirect; a verified policy covering redirects is counterevidence.
- Determine environment/credential scope from safe configuration references and authorized metadata. A variable name or PR description does not prove staging reaches production. Never print credentials or production values to establish identity.
- Review changed install scripts, CI/deploy permissions and executable behavior when they can expand privilege; use `artifacts-and-packages.md` for the artifact contract. Harmless chmod-only changes are not security findings.

## Signed Events And Replay

When webhook verification changes, inspect the provider/version contract, exact signed bytes, guard order and secret selection. Verification after body transformation can fail or verify the wrong representation; raw-byte verification may be correct. A valid signature does not itself prove freshness or unique processing: check required timestamp tolerance, event identity and durable deduplication. Expiry alone does not prevent duplicates inside its window. Use `providers-and-timing.md` for retry/acknowledgment consequences.

Report the concrete actor, reachable input, failed control and sensitive consequence, with safe redacted evidence. Do not prescribe a particular guard library or inflate impact merely because a flaw involves access control. Omit priority codes.
