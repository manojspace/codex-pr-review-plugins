# Connected PR Review, Delivery, And Comment Workflow

Load this reference for every mutating run.

## Input And Routing

1. Extract all GitHub PR URLs before repository work, normalize them to `{owner, repo, prNumber}`, deduplicate repeated identities, and preserve first-seen order.
2. Treat every distinct supplied PR as one connected set.
3. Apply any workspace-root or comparison-branch overrides from applicable user or repository instructions.
4. Otherwise search the active workspace roots for a local repository whose canonical remote matches `owner/repo`, and use the PR's declared base branch as the comparison branch.
5. If no local checkout exists, use a disposable clone when safe. Ask only when the local target, authentication, fork destination, comparison branch, or writable head remains ambiguous.

## GitHub Metadata

Fetch bootstrap metadata before local work:

- owner, repository, PR number, state, and draft status;
- title and body;
- declared base ref/SHA and head ref/SHA;
- head repository, owner, branch, fork status, and deletion status;
- changed-file list;
- authenticated write access to the exact head repository/ref.

Fetch enrichment metadata before the final review:

- author, linked issues, and evidence-backed related PRs;
- commits, file statuses, renames, additions, and deletions;
- reviews, inline comments, timeline comments, unresolved/outdated context;
- CI/check status for the exact head SHA.

Prefer the GitHub connector/MCP. Use authenticated `gh` only as fallback. If neither can establish metadata and the writable head destination, stop instead of guessing.

Recheck every head SHA before editing, committing, and pushing. If a head changes, discard the stale delivery attempt, refresh its metadata and diff, rebuild the connected graph, and invalidate every prepared finding, edit, and commit for that PR and its transitive dependents. Restart and rerun the two-agent gate for the affected graph from the new SHAs without resetting or overwriting remote work.

## Task Naming

After bootstrap metadata is available and before local repository work:

1. Prefer an explicit goal from the user's request.
2. Otherwise infer one shared outcome from all PR titles, bodies, and changed-file inventories.
3. If no shared outcome is defensible, use the first prompt-ordered PR title as the fallback.
4. For title-derived fallback text only, remove one leading bracketed or unbracketed ticket token matching `[A-Za-z][A-Za-z0-9]*-\d+`, plus surrounding whitespace and an optional `-`, `:`, `–`, or `—`. Keep the original title when removal would leave an empty string.
5. Format one PR as `PR Review - <goal>` and multiple distinct PRs as `<N> PRs Review - <goal>`.
6. Unless the user opted out, call `codex_app__set_thread_title` exactly once without `threadId`. Continue silently if the host does not expose the tool or the rename fails.

## Local Isolation

1. Locate each repository under the resolved workspace roots by canonical Git remote URL, not folder name. Create a disposable clone when no matching checkout exists and doing so is safe.
2. Inspect ordinary checkout status, current branch/SHA, remotes, worktrees, and required comparison branch availability without changing it.
3. Fetch the required base and PR head into temporary refs.
4. Create an isolated disposable worktree for every distinct `{head repository, head ref, head SHA}`. PRs sharing that tuple share one worktree and delivery; other PRs remain isolated even when they use the same repository.
5. Never stash, reset, clean, rebase, switch, or otherwise alter the user's ordinary checkout.

For fork PRs, fetch by URL or temporary ref without a permanent remote. Before delivery, prove the authenticated user can push to the exact fork head branch. Never substitute the upstream/base repository.

Closed or merged PRs are review/comment-only: do not update their former head branches.

## Review Coverage

For each PR, inspect the declared PR-base-to-head diff and any instruction-overridden comparison-branch-to-head diff. Compare GitHub file metadata with local rename/copy-aware diff output and explain mismatches.

Classify every changed file as source, test, config, migration, generated, binary, lockfile, vendored, asset, workflow, submodule, symlink, or documentation. Inspect every text hunk and enough callers/consumers to understand behavior. Record explicit limitations for generated, binary, large, LFS, or truncated files.

Build the connected producer-consumer graph before editing. Include APIs, routes, schemas, migrations, generated clients, packages, environment variables, feature flags, workers, jobs, queues, webhooks, deployment units, and required release order. Cross-repo findings must name both sides of the contract.

Run all review gates and both independent agents. Reconcile findings against direct evidence, then implement every accepted fix across the supplied PR set.

## Inspection And Delivery

For each distinct changed head:

1. Inspect complete worktree status and final diff. Do not run automated validation unless the current request adds it.
2. Inspect the effective Git hook configuration. If committing would run validation not authorized by the request, stop and ask; never bypass the hook.
3. Re-fetch and confirm the remote head still equals the reviewed SHA.
4. Stage only intended files/hunks and inspect the staged diff for unrelated changes or secrets.
5. Create one non-empty commit with subject exactly `ai review`.
6. After hooks finish, inspect worktree status, the commit's full diff/name-status, parent/tree, and full message. Stop unless the commit contains exactly the intended changes, its subject is exactly `ai review`, and its body is empty.
7. Recheck the remote head again, then non-force push the commit to the verified head repository/ref.
8. Confirm GitHub reports the PR head at the pushed commit before marking it delivered.

Prepare all connected commits first. Push in evidence-backed dependency order, producers before consumers. If a producer push fails, do not push its dependent consumers; continue independent PRs. Never roll back a successful push solely because another PR or comment failed.

## Per-PR Timeline Comment

Post one summary comment on every supplied PR after all review, fix, and push attempts reach a final state. Use this structure:

- **Missing:** accepted findings and material deferred findings; say no required change was found when applicable.
- **Done:** changed behavior/files, exact commit SHA/link, and push status; say no commit was created for unchanged PRs.
- **Validation:** `Reviewed by inspection`; list lint, build, tests, migrations, installs, and code generation not run, plus any checks that mandatory Git hooks actually ran.
- **Related PRs:** every supplied or evidence-backed linked PR URL, relationship, delivery status, and dependency/release order. Do not invent a relationship.
- **Remaining risk:** blockers, deferred decisions, CI state, incomplete deliveries, and comment failures.

Include the stable hidden marker `<!-- pr-review-and-commit:summary -->`. Inspect existing timeline comments for a marker authored by the authenticated user. Update that plugin-owned comment to the latest final connected-set state instead of posting a duplicate; never trust or edit another author's marker. If the available GitHub interface cannot update comments, post a new summary only when its final content differs and report that idempotent replacement was unavailable.

Never say a change was committed or pushed until GitHub confirms the new head. If a PR is unchanged, blocked, closed, merged, protected, stale, or not writable, comment with that exact outcome when commenting remains permitted. Redact local paths, credentials, secrets, exploit details, private payloads, and unnecessary PII.

## Failure Semantics

- Missing write permission, branch protection, deleted branches, stale heads, hook failures, and push rejection stop delivery for that head without force or bypass.
- A failed producer prevents dependent pushes but not independent ones.
- If push succeeds and commenting fails, preserve the pushed commit and report the comment failure to the user.
- If commenting succeeds for some PRs only, update existing authenticated-user-owned plugin summary comments during retry and do not duplicate successful comments.
- Report partial cross-repository state precisely. Never describe the connected set as fully delivered unless every intended push and PR comment succeeded.
