# Frontend Consumers And User Actions

Load for changed interactive controls, actions, client helpers, state or rendering; for backend-only changes, load only when an affected rendering consumer remains unresolved. Trace the real request helper through transformation/error handling, state and renderer. Stop at the user's truthful visible outcome and safe next action, not an unrelated UI audit.

## Outcomes And Concurrent State

- Check material success/error fields and stable codes reach the appropriate consumer. Dropping an internal provider message can be intentional sanitization; losing a contract needed for recovery is different. Inspect loading, empty, error, retry and success states where the action requires them; a parent boundary or shared operation model may own them.
- When identity or selection changes, can user A's late response overwrite user B's state? Verify cancellation, ignoring obsolete results, request versions or the data library's ownership contract. An explicit AbortController is not required if another effective guard exists. Post-unmount completion alone does not establish a memory leak.
- For optimistic updates, trace the affected version and rollback after concurrent edits. An older failed action must not restore state over a newer successful action. Check subscriptions/listener ownership when lifecycle changes.
- For repeated submission, distinguish UI suppression from server idempotency. Trace misleading success and unsafe retry advice after partial/unknown completion. Copy should offer a supported next step; a local clock cannot supply server authorization.

## Changed Controls And Render Paths

- Check keyboard reachability, accessible names/labels, focus movement/restoration and modal behavior for changed controls. Compare the actual interaction with its supported keyboard/focus contract; do not demand unrelated design cleanup.
- Review safe rendering of changed external/user content and URLs; use `security.md` when a trust boundary changes.
- Inspect repeated API calls, render loops, expensive selectors/transforms, large tables/lists and bundle-affecting imports only on affected paths. Require realistic work/size evidence. Line count is not bundle cost; memoization, extraction and lazy loading are options, not automatic findings.

Report the input/order, affected user-visible state, evidence and smallest correction using the existing helper/state ownership pattern. Keep convention feedback separate from functional or accessibility regressions.
