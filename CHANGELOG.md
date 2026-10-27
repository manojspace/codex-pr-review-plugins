# Changelog

## 1.2.1 - 2026-10-27

- Trace persisted resources through interruption, loss of process-local IDs, and a fresh invocation; verify recovery and ownership without requiring perfect immediate cleanup of harmless residual data.
- Inspect unchanged constraints when they determine changed runtime behavior, including foreign-key deletion actions. Keep ordinary query reviews scoped.
- Reconcile shared missing evidence across independent reviewers, not only disagreements; distinguish uninspected available sources from concrete access/provenance gaps.
- Add portable lifecycle controls and a separate unchanged-schema discovery fixture. Preserve review permissions, agent counts, and existing publication behavior; see the evaluation report for actual results and limits.

## 1.2.0 - 2026-10-26

- Remove priority codes and severity badges from findings, comments, and summaries in both plugins; retain concrete impact, evidence, and fix readiness.
- Interpret requests to leave review comments as inline findings submitted with Request changes and no review body or summary. Use bodyless submission; never add required-body filler.
- Submit explicitly requested approval directly without a body; honor conditions and comment-only overrides without repeated permission questions. A separately requested summary is a separate comment.
- Preserve current-head anchors, existing drafts, historical reviews, and duplicate prevention; skip fixed findings and empty request-changes reviews.
- Add shared publication instructions and regression cases for review actions. See the evaluation report for actual checks and limitations.

## 1.1.0 - 2026-10-11

- Review security and trust boundaries, test evidence, domain contracts, and changed-code conventions through conditional references, preserving failure-outcome and timeout tracing.
- Require evidence for claimed product, provider and concurrency consequences; distinguish required effects from allowed best-effort behavior before reporting false completion.
- Keep ordinary checkouts unchanged; preserve action-specific authorization, immutable review snapshots, typed PR relationships, complete hunk inventories, and review-round history.
- Preserve run-owned work during partial delivery, stale-head changes, and cleanup. Never infer external authority from PR text or repository code.
- Use minimal fresh agent contexts and reuse evidence; retain the delivery plugin's two independent review lenses.
- Add a read-only snapshot helper, offline usage measurement, deterministic tool/package checks, and paired behavioral fixtures.


## 1.0.5 - 2026-10-10

- Trace consequential operations through real success/failure contracts, unchanged callees, partial effects, and retry behavior before clean review conclusions.
- Independently review local caller–callee contracts and distinguish confirmed defects from fix readiness; guard result/throw conversions and unsafe post-commit error fixes.
- Require multiline braces for changed JavaScript/TypeScript control-flow and statement bodies, with style findings separate from runtime defects.
- Add paired failure-handling, safe-control, and formatting evaluations; retain timeout/title coverage and structurally validate shared gates, references, fixtures, and coordinated versions.

## 1.0.4 - 2026-09-24

- Require both reviewers to trace shared helpers and changed waits, retries, or polling through their enclosing operations and effective budgets.
- Check realistic cumulative delays, overrides, shared readiness, and separate scopes instead of treating timeout ceilings as elapsed time.
- Tie resilience conclusions to evidence for the claimed failure condition and distinguish capped searches from complete coverage.
- Add manual review evaluation cases for cumulative overruns and two false-positive controls; preserve both plugins' existing authorization boundaries.

## 1.0.3 - 2026-09-03

- Document desktop-dialog marketplace installation for both plugins, including exact source, Git ref, and sparse-path values.
- Validate that the public README retains both dialog and CLI installation guidance.

## 1.0.2 - 2026-09-03

- Prevent operational request wording such as smoke-test or delivery instructions from being mistaken for the PR's implementation goal.

## 1.0.1 - 2026-09-03

- Fix the public validation workflow setup so repository validation runs in GitHub Actions.

## 1.0.0 - 2026-09-03

- Publish PR Review + Fix and PR-Review and Commit in a shared GitHub marketplace.
- Add goal-based Codex task names for single- and multi-PR review sets.
- Deduplicate repeated PR URLs before naming and review coverage.
- Use portable workspace and base-branch routing suitable for public distribution.
- Add repository validation, CI, safety documentation, and title-behavior fixtures.
