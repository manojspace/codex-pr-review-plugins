# Workflow

Load this reference for multi-PR routing, branch drift, dirty/diverged branch handling, exact coverage details, or output rules. Use the fast path in `SKILL.md` first for ordinary single-PR review.

## Input And Routing

1. Extract all GitHub PR URLs from the user prompt before doing repository work.
2. Normalize each URL to `{ owner, repo, prNumber }`, deduplicate repeated identities, and preserve first-seen order.
3. Treat all distinct PRs in one prompt as one interconnected review set, even when they are in different repos.
4. Apply any workspace-root or comparison-branch overrides from applicable user or repository instructions.
5. Otherwise search the active workspace roots for a local repository whose canonical remote matches `owner/repo`, and use the PR's declared base branch as the comparison branch.
6. If no local checkout exists, use a disposable clone or worktree when safe. Ask only when the local target, authentication, fork destination, or comparison branch remains ambiguous.

## Metadata Tiers

Fetch only bootstrap metadata before branch alignment:

- owner, repo, PR number;
- title and body;
- declared base ref/SHA and head ref/SHA;
- head branch name, head repo, head owner, and fork status;
- changed-file list.

Fetch enrichment metadata before final output or deep review:

- author, draft state, labels, linked issues, and linked PRs;
- commit list;
- changed files with status, additions, deletions, old paths, and new paths;
- reviews, inline comments, issue comments, unresolved/outdated context when available;
- CI/check status for the exact head SHA.

Prefer structured GitHub connector or MCP metadata. Use `gh` only if installed and authenticated. If neither metadata source is available, stop and report that PR metadata cannot be safely resolved.

Re-check each PR head SHA before final output. If a PR was force-pushed during review, stop or restart from the new metadata snapshot.

## Task Naming

After bootstrap metadata is available and before local repository work:

1. Prefer an explicit goal from the user's request.
2. Otherwise infer one shared outcome from all PR titles, bodies, and changed-file inventories.
3. If no shared outcome is defensible, use the first prompt-ordered PR title as the fallback.
4. For title-derived fallback text only, remove one leading bracketed or unbracketed ticket token matching `[A-Za-z][A-Za-z0-9]*-\d+`, plus surrounding whitespace and an optional `-`, `:`, `–`, or `—`. Keep the original title when removal would leave an empty string.
5. Format one PR as `PR Review - <goal>` and multiple distinct PRs as `<N> PRs Review - <goal>`.
6. Unless the user opted out, call `codex_app__set_thread_title` exactly once without `threadId`. Continue silently if the host does not expose the tool or the rename fails.

## Local Repo Safety And Branch Alignment

For each routed PR:

1. Search only the resolved workspace roots, or create a disposable clone when no matching checkout exists.
2. Match local repos by Git remote URL containing the canonical `owner/repo`, not folder name alone.
3. Run the fast local safety check:
   - current branch or detached HEAD;
   - current HEAD SHA;
   - `git status --short`;
   - remotes;
4. Verify the resolved comparison branch exists locally or as a remote ref. Stop for that PR if it is missing.
5. Fetch the required base branch and PR head before switching.
6. Unless the user explicitly asked for review-only/no checkout, align to the PR branch early when safe.
7. If already on the target PR branch, stay there.
8. If clean and the target branch exists, switch to it.
9. If clean and the target branch is missing, create it from the fetched PR head.
10. If the target branch exists and is behind the fetched PR head, fast-forward only.
11. If the target branch is ahead of the fetched PR head, keep it and report local-only commits.
12. If the target branch diverged, do not reset; use a clean PR worktree or ask.
13. If dirty, do not switch, stash, reset, or clean; use a clean PR worktree or ask.

Use full snapshots only before edits or when changed paths involve submodules, sparse checkout, executable bits, generated files, or worktree-sensitive behavior. A full snapshot includes `git status --porcelain=v2 --untracked-files=all`, worktree list, sparse checkout state, recursive submodule status, and `core.fileMode`.

Do not stash, reset, clean, update submodules, alter sparse checkout config, add permanent remotes, or overwrite branches unless the user explicitly asks.

## Forks And Fallback Worktrees

For fork PRs, avoid permanently adding remotes. Fetch the fork PR head by URL or temporary ref. Create a local branch from the fetched head only when push/upstream behavior is unambiguous; otherwise use a no-upstream branch or ask.

Use temp refs or disposable worktrees for dirty local checkouts, multiple PRs in the same repo, fork PRs that cannot safely checkout, diverged branches, or explicit review-only/no-checkout requests. Do not use detached worktrees by default for a single safe plugin-selected PR flow.

## Diff Coverage

For each PR, inspect:

- declared PR base to PR head for actual PR correctness;
- instruction-overridden comparison branch to PR head when it differs from the declared base;
- aggregate diff for the connected PR set when PRs interact.

Compare GitHub changed-file metadata with local `git diff --name-status --find-renames --find-copies`. Flag any mismatch.

Classify every changed file:

- source;
- test;
- config;
- migration;
- generated;
- binary;
- lockfile;
- vendored;
- asset;
- workflow;
- submodule;
- symlink;
- docs.

For text files, inspect every changed hunk and enough surrounding callers/consumers to understand behavior. For generated, binary, large, LFS, or truncated files, record the inspection method or explicit limitation. Track renamed, copied, and deleted files with old and new paths.

Pure chmod-only authorization findings are out of scope, but executable-bit changes affecting scripts, package entrypoints, CI, deployment, hooks, or runtime behavior remain in scope.

## Connected Review Graph

Do not build a connected review graph before first-pass findings for an ordinary single PR. Build it when there are multiple PRs or when changed files touch APIs, packages, schemas, migrations, env/config, deployment, generated clients, shared contracts, workers, cron, queues, or webhooks.

When triggered, include:

- repos and services;
- packages and shared models;
- APIs, routes, schemas, and generated clients;
- DB migrations and model changes;
- environment variables and feature flags;
- workers, cron jobs, queues, webhooks, and deployment units;
- imports, package dependencies, route calls, schema generation, Docker/deploy config, and CI workflows.

Cross-repo findings must name both sides of the contract: producer repo/file and consumer repo/file.

## First Pass And Deep Pass

First pass:

- align to the PR branch when safe;
- inspect changed-file inventory and risk tags;
- inspect changed hunks plus nearby callers;
- run the error/logging sentinel;
- run the cross-repo contract/inconsistency sentinel;
- return concrete findings as soon as defensible.

Deep pass triggers:

- multiple PRs;
- public/shared contracts changed;
- schema, migration, env/config, generated client, or shared-infra changes;
- async/error/logging changes in high-risk paths;
- performance-sensitive paths;
- large diffs;
- missing tests around risky behavior;
- non-trivial fixes;
- explicit exhaustive review request.

## Final Output

Return:

- findings first, ordered by severity;
- finding tags: `PR-local`, `series-level`, `base-drift`, or `cross-repo`;
- coverage metadata: PRs reviewed, base/head SHAs, changed file counts, limited/skipped files with reasons, CI/comment context inspected, and subagent status;
- files changed, if any;
- validation run or skipped by policy;
- remaining risk and deferred approval-needed issues.

Do not say "verified" unless validation actually ran. Use "reviewed by inspection" when lint/build/tests were intentionally not run.
