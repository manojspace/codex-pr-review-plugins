# Risk-Adaptive Independent Review

Load before fixes or clean/ready conclusions when risk requires independence. Do not delay defensible first-pass findings.

- Low-risk, self-contained review or local correction with complete direct evidence may use no subagent.
- Moderate material uncertainty uses one independent verifier focused on the uncertain contract/path.
- Privileged/destructive, account, payment, schema, or cross-boundary paths require two complementary independent lenses before a clean/ready conclusion or consequential fix, even for a one-line change.

Line count informs cost, never risk exemption. Non-trivial edits require an explicit risk classification and adequate verification; do not automatically classify a small diff as low risk.

## Independent Lenses And Briefs

Use fresh minimal context (`fork_turns="none"` where supported), not inherited full conversation. At most two review lenses may run concurrently. Give neutral briefs with the request/success criteria, action and validation boundaries, canonical PR identity, pinned objects/comparisons, raw artifact/hunk references, required contract entry points, relevant trusted instructions, and loaded reference paths. Include the smallest producer/consumer context needed; agents may challenge scope and request omitted evidence. Do not supply expected findings, a preferred conclusion, or another lens's output. Do not spawn user-visible chats for review subtasks.

- **Lens A:** correctness, security of reachable effects, scalability, failure outcomes, retries, partial effects, idempotency, and observability. Trace forward from actor/input and producer outcomes through caller decisions, completed/pending effects, response/ack, and recovery. For changed collection processing, follow eligibility and checkpoints into the next page/run.
- **Lens B:** contracts, authorization/tenant boundaries, API/schema/package drift, configuration/deployment, and existing-code consistency. Work backward from required success conditions through local/cross-repository callers and unchanged callees, including returned versus thrown failure. Independently verify requirement preservation, including reporting for excluded populations when selection or effects move; record unavailable material criteria.

For one verifier, choose the lens addressing the material uncertainty and state its scope. Review core risks first, then only triggered domain references. Soft read/call guidance is not a completeness cutoff; use bounded artifact windows and disclose inaccessible evidence.

## Required Evidence And Adjudication

Require findings, direct evidence and counterevidence, files/hunks inspected, material outcome coverage, unknowns, suggested correction/validation, checks run, files changed (normally none), and confidence/remaining risk. Calibrate severity with `review-gates.md`. Separate confirmed defects from unresolved contracts and decision-dependent fixes. Hypothetical behavior of an unavailable helper is a gap, not a confirmed additional defect. A no-findings result counts only with inspected scope and limitations; incomplete material coverage cannot support an unqualified clean conclusion.

Evidence outranks votes. Inspect disputed source, schemas, runtime tests, checks, and remote state directly. Preserve independent perspectives until both finish. Reject unsupported claims with counterevidence; unresolved high-impact contradictions block the affected ready/clean conclusion, not unrelated confirmed findings. Ask only if user intent/authority is actually missing after available investigation.

## Retry And Invalidation

Retry only a failed/timed-out lens, once, with a narrower fresh brief; retain a successful independent lens. Never launch a replacement pair for one failure or rerun merely to obtain agreement. Distinguish failure retries from evidence invalidation. After edits, head/base changes, or material contract/config/policy changes, rerun only invalidated evidence/lenses. Allow one automatic affected-evidence rerun; further material change leaves that gate outstanding. A rerun limit never permits stale delivery or an unqualified clean conclusion.

Before edits, record compact verifier statuses, confirmed/rejected/unresolved findings, fix readiness, contradictions, scope, and required validation. Reuse unaffected pinned evidence, not path-only or prior-comment verdicts.

If an optional verifier is unavailable, manually inspect that scope and disclose reduced independence. If a risk-required verifier remains unavailable after its one retry, retain confirmed findings and any proposal but withhold the affected clean/ready conclusion or consequential edit; do not claim the independent gate completed.
