# Codex PR Review Plugins

Two public Codex plugins for high-signal GitHub pull-request review:

- **PR Review + Fix** reviews one or more connected PRs and can apply conservative local fixes when authorized.
- **PR-Review and Commit** reviews a connected PR set, applies accepted fixes, commits, non-force pushes, and comments when the request explicitly authorizes the complete delivery workflow.

Both plugins give the current Codex task a concise goal-based name after reading PR bootstrap metadata:

- One distinct PR: `PR Review - <goal>`
- Multiple distinct PRs: `<N> PRs Review - <goal>`

The goal comes from the user's stated objective when available, then a confidently inferred shared outcome, then the first PR title as a fallback. A leading card identifier such as `VD-102 -` is removed only from that title fallback.

## Install

Add the public GitHub marketplace and install either or both plugins:

```bash
codex plugin marketplace add manojspace/codex-pr-review-plugins --ref main
codex plugin add github-pr-review-fix@pr-review-plugins
codex plugin add pr-review-and-commit@pr-review-plugins
```

For a release-pinned marketplace, replace `main` with `v1.0.2`.

To receive updates from the selected ref:

```bash
codex plugin marketplace upgrade pr-review-plugins
```

## Use

```text
Use $github-pr-review-fix to review these PRs. Findings first; no edits unless I ask:
<PR URLs>
```

```text
Use $pr-review-and-commit to review and fix these PRs, commit as ai review,
push, and comment on each PR:
<PR URLs>
```

The plugins discover repositories from applicable user or repository instructions first, then from canonical Git remotes in active workspace roots. They use each PR's declared base branch unless instructions override it. Machine- or organization-specific routing belongs in private Codex instructions, not in this public bundle.

## Safety

PR Review + Fix never stages, commits, pushes, or comments unless explicitly authorized. PR-Review and Commit requires explicit authorization for edits, commits, pushes, and comments; it never merges, approves, force-pushes, closes, labels, or deletes branches. Both workflows stop instead of guessing when repository identity or a writable destination is ambiguous.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repository.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the release checklist and [SECURITY.md](SECURITY.md) for responsible reporting.
