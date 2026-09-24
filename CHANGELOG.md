# Changelog

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
