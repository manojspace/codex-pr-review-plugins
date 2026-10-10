# Fix And Delivery Policy

Load this reference before changing files. The goal is to attempt every ready, authorized fix in the supplied PR set without inventing missing requirements or including unrelated work.

## Finding Validity And Fix Readiness

Validate a finding from the changed path, actual contract, plausible failure trigger, and concrete consequence. Classify it as confirmed, rejected with counterevidence, or unresolved. A confirmed defect remains reportable even if its fix needs a product decision, affects an out-of-scope repository, or cannot currently be delivered.

Separately classify its fix as ready, decision-dependent, or outside authorized scope. A fix is ready when all are true:

- the issue is confirmed by direct evidence rather than agent agreement or nearby style alone;
- the intended result is sufficiently clear to implement without guessing;
- the change belongs to a supplied PR and can be delivered to its verified head branch;
- the implementation can be made coherent across every affected supplied PR.

Ready, authorized fixes may include local correctness changes, error handling, performance work, public contracts, schemas, migrations, dependencies, generated artifacts, or coordinated multi-repo changes. Keep the implementation as small and maintainable as the confirmed finding allows.

Do not accept a proposed fix merely because an agent suggested it. Reject unsupported or contradicted claims with evidence; record unresolved evidence gaps separately. Keep confirmed findings with deferred fixes visible in the final review and authorized PR summaries.

Changing returned failures into throws or throws into result values changes a behavioral contract even without a signature change. The same applies to mutation reordering, fail-open/fail-closed behavior, and retry policy. Inspect affected callers and already-completed effects before choosing the smallest coherent correction. A caller-side check that reports failure after committed writes can still invite duplicate effects on retry; do not treat it as a complete fix without that analysis.

## Stop Conditions

Stop and ask only when completion requires:

- a product or business decision not established by the supplied code or PR context;
- credentials, secrets, permissions, or a writable Git destination that are unavailable;
- an irreversible or destructive data action whose exact intent and rollback are unspecified;
- changing a repository or PR that the user did not place in scope;
- choosing between materially different contract or release behaviors with no authoritative evidence.

Record blocked findings in the relevant PR comments. Do not silently choose a risky interpretation.

## Editing Rules

Before editing, summarize both agent reviews, confirmed/rejected findings, fix readiness, open contradictions, intended files, and the inspection plan.

During editing:

- use a disposable worktree for the exact PR head;
- preserve unrelated and pre-existing changes;
- keep every changed line traceable to a confirmed finding;
- make coordinated fixes across supplied PRs when required for contract consistency;
- do not perform unrelated cleanup, broad modernization, or speculative hardening;
- do not run lint, builds, tests, package scripts, installs, migrations, or code generation unless the current request explicitly authorizes them.

After editing:

- inspect `git status`, the unstaged diff, and the staged diff;
- confirm only intended files and hunks are included;
- state that the changes were reviewed by inspection and list checks not run;
- rerun an affected review-agent lens when the edits materially change its original conclusion;
- reinspect affected operation-outcome traces, including completed effects, failure reporting, and retry safety, against the final code;
- recheck the PR's remote head SHA before staging and again before pushing.
- inspect the repository's effective Git hooks before committing; if a hook would run validation that the request did not authorize, stop and ask rather than bypassing it;

## Commit And Push Rules

- Deduplicate PRs sharing the same verified head repository, ref, and SHA into one worktree and one delivery.
- Stage explicit intended paths only. Never use staging that could capture unrelated files without first proving the complete status is clean and intended.
- Never create an empty commit. Unchanged PRs still receive a review summary.
- Create one commit per distinct changed PR head with the exact subject `ai review` and no generated body. Preserve the configured author identity.
- After hooks finish, inspect worktree status, the commit's complete diff and name-status, its parent/tree, and its full message. Stop unless the committed paths and content are exactly intended, the subject is exactly `ai review`, and the body is empty.
- Push without force to the exact verified PR head repository/ref. For forks, prove the fork destination is writable and do not add a permanent remote.
- Never reset, rebase, force-push, bypass hooks, delete branches, create replacement PRs, merge, approve, request changes, close, or label.
- Prepare all connected changes before delivery, then push producers before dependent consumers. If a producer fails, do not push its dependent consumers; independent PRs may continue.
- Recheck that the remote PR head resolves to the pushed commit before describing delivery as successful.

Cross-repository delivery is not atomic. Do not roll back a successful push because another push or comment failed; report the exact partial state instead.
