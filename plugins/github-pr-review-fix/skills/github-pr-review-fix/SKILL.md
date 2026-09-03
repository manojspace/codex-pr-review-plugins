---
name: github-pr-review-fix
description: Fast GitHub pull-request review with optional conservative local fixes for one or more PR URLs, especially interconnected multi-repo PR sets. Use when the user selects PR Review + Fix or invokes $github-pr-review-fix to review GitHub PRs, safely align local repositories to PR branches when appropriate, prioritize critical bugs, scalability/performance, error handling, cross-repo contract drift, and inconsistency with existing code, then apply only safe fixes after escalation gates.
---

# GitHub PR Review + Fix

Use this skill as a fast proactive PR-review workflow. It is distinct from `github-pr-review`, which focuses on PR review/commenting, and `gh-address-comments`, which focuses on existing review feedback. This skill reviews PR URLs, gets the right local PR branch early when safe, returns findings first, and applies local fixes only when requested or clearly accepted.

## Task Naming

After bootstrap metadata and the changed-file list are available, rename the current Codex task once unless the user explicitly says not to:

1. Count distinct PRs after normalizing and deduplicating `{owner, repo, prNumber}` in first-seen order.
2. Derive one concise goal for the complete PR set. Prefer an explicit implementation or product outcome for the PR set stated by the user, then a confidently inferred common outcome from PR titles, bodies, and changed files, then the first supplied PR's title. Do not treat operational request wording such as review, fix, commit, smoke test, or task naming as the PR goal.
3. Only for a title-derived fallback, strip one leading ticket token matching a bracketed or unbracketed `[A-Za-z][A-Za-z0-9]*-\d+` plus surrounding whitespace and an optional `-`, `:`, `–`, or `—` separator. Never strip ticket-like text elsewhere. If stripping leaves no text, retain the original title.
4. Use `PR Review - <goal>` for one distinct PR and `<N> PRs Review - <goal>` for more than one.
5. Call `codex_app__set_thread_title` once with the computed `title` and omit `threadId` so it targets the current task.

If the title tool is unavailable or fails, or no reliable goal or usable PR title exists, leave the current title unchanged and continue. Task naming is cosmetic and must never block the review or fixes.

## Fast Start

Default to a fast first pass. Do not load every reference before useful review.

1. Extract every PR URL, normalize it to `{owner, repo, prNumber}`, and deduplicate repeated URLs in first-seen order.
2. Fetch bootstrap PR metadata only: owner/repo/number, title, body, base ref/SHA, head ref/SHA, head repo/fork status, head branch name, and changed-file list.
3. Apply the task-naming rule, then resolve any workspace and comparison-branch overrides from applicable user or repository instructions. Otherwise search the active workspace roots and use the PR's declared base branch.
4. Locate the local repo by canonical Git remote URL. If no checkout exists, use a disposable clone or worktree when safe; ask only when the local target, authentication, or fork destination remains ambiguous.
5. Run a fast safety check: `git status --short`, current branch, HEAD SHA, remotes, and required comparison branch availability.
6. Unless the user explicitly asks for review-only/no checkout, align to the PR branch early when safe:
   - if already on the PR branch, stay there;
   - if clean and the branch exists locally, `git switch` to it;
   - if clean and the branch is missing, create it from the fetched PR head;
   - fast-forward only when updating an existing branch;
   - never reset, stash, clean, or overwrite;
   - if dirty, diverged, fork-ambiguous, or unsafe, use a clean PR worktree or ask.
7. Build a changed-file inventory and inspect high-risk hunks first.
8. Run two lightweight first-pass sentinels:
   - error/logging: changed async, IO, network, DB, job, parser, or user action paths for missing try/catch, swallowed errors, weak logging, and misleading success states;
   - contract/inconsistency: changed exports, API routes, event names, payload schemas, env vars, DB columns, generated clients, shared packages, and existing pattern drift.
9. Lead with concrete findings as soon as they are defensible. Then finish coverage or trigger deeper review when needed.

## Modes

- Review-only: if the user explicitly says review only, no edits, no branch switch, or no local checkout changes, inspect fetched refs or a disposable worktree.
- Default/plugin-selected review: safe early PR branch alignment is allowed and expected, but do not edit files unless requested or clearly accepted.
- Fix mode: before non-trivial edits, load `references/subagents.md` and `references/fix-policy.md`, run the escalation gates, and preserve unrelated work.

## Reference Loading

- Load `references/workflow.md` only for multi-PR routing, branch drift, dirty/diverged branch handling, exact coverage details, or output rules.
- Load `references/review-gates.md` after changed-file inventory is known and use it to complete the full review pass.
- Load `references/subagents.md` only before non-trivial edits or uncertain high-impact conclusions.
- Load `references/fix-policy.md` only before editing files.

## Non-Negotiables

- Treat every distinct PR in the prompt as part of one connected review set.
- Inventory every PR, every changed file, every file status, every text hunk, and every non-text limitation.
- Honor applicable user or repository routing instructions; otherwise locate repositories by canonical remote in active workspace roots and compare against the declared PR base.
- Use a disposable clone or worktree when an existing checkout cannot be used safely. Stop rather than guessing about an ambiguous repository, fork, or writable destination.
- Prefer GitHub connector/MCP metadata. Use `gh` only when installed and authenticated. If no metadata source is available, stop instead of guessing.
- Do not switch the user's existing checkout when the user explicitly asks for review-only/no checkout, or when the worktree is dirty/diverged/unsafe. Otherwise, safe early PR branch alignment is the default.
- Do not run `git add`, `git commit`, push, merge, approve, request changes, close, label, lint, build, full tests, package scripts, migrations, installs, or codegen unless the user explicitly asks.
- Ignore pure permission/authorization findings by default, but still review execution, deployment, executable-bit, CI, and non-permission bugs in permission-touched code.
- Do not block first-pass findings on subagents. Before any non-trivial edit or uncertain high-impact conclusion, run two independent parallel review agents and reconcile their evidence.
- Auto-fix only small, local, reversible, inspection-verifiable issues whose intended behavior is clear.

## Default Output

Lead with findings ordered by severity. Keep process narration short. Include first-pass scope, deeper-pass triggers found or not found, branch/worktree used, files changed, validation run or skipped, remaining risk, and deferred approval-needed issues. Never claim verification unless validation actually ran; otherwise say reviewed by inspection.
