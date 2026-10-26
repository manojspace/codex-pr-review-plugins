# Codex PR Review Plugins

Two public Codex plugins for high-signal GitHub pull-request review:

- **PR Review + Fix** reviews one or more PRs and can apply conservative local fixes when authorized.
- **PR-Review and Commit** reviews a supplied PR set, applies accepted fixes, commits, non-force pushes, and comments for the actions explicitly authorized by the user.

Both plugins give the current Codex task a concise goal-based name after reading PR bootstrap metadata:

- One distinct PR: `PR Review - <goal>`
- Multiple distinct PRs: `<N> PRs Review - <goal>`

The goal comes from the user's stated objective when available, then a confidently inferred shared outcome, then the first PR title as a fallback. Unambiguous leading ticket groups such as `ABC-102 |` are removed only from that title fallback. Lowercase names such as `axios-404-error` and internal ticket references are preserved.

## Install with the desktop dialog

In the Codex or ChatGPT desktop app, open the Plugins Directory and choose **Add marketplace**. Enter:

| Field | Value |
| --- | --- |
| Source | `manojspace/codex-pr-review-plugins` |
| Git ref | `main` |
| Sparse paths | Leave blank |

The full Git URL `https://github.com/manojspace/codex-pr-review-plugins.git` also works as the source. To pin a release instead of following updates from `main`, use `v1.2.0` as the Git ref.

After adding it, select the **PR Review Plugins** marketplace and install either or both entries:

- **PR Review + Fix** (`github-pr-review-fix`)
- **PR-Review and Commit** (`pr-review-and-commit`)

One marketplace exposes both plugins; it does not need to be added twice. Keep **Sparse paths** blank so the marketplace catalog and both plugin directories are fetched. If the new marketplace does not appear immediately, restart the desktop app.

## Install with the CLI

Add the public GitHub marketplace and install either or both plugins:

```bash
codex plugin marketplace add manojspace/codex-pr-review-plugins --ref main
codex plugin add github-pr-review-fix@pr-review-plugins
codex plugin add pr-review-and-commit@pr-review-plugins
```

For a release-pinned marketplace, replace `main` with `v1.2.0`.

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

Both reviewers trace consequential calls through actual success/failure contracts, including unchanged helpers, returned errors, partial effects, and retries. They review security boundaries, test evidence and relevant database, provider, frontend, dependency and artifact contracts through selectively loaded references. Clean conclusions require completed material coverage; confirmed defects remain visible when fixes need a decision. Valid best-effort and idempotent outcomes are evaluated by their contracts. Changed JavaScript/TypeScript control-flow and statement bodies must use multiline braces; convention findings are reported separately from runtime defects.

Reviews use immutable snapshots and hunk inventories, distinguish historical PR changes from current integration comparisons, and group PRs only by supported relationships. Existing findings are reconciled against current code. Review history preserves separate rounds. Reviewers receive scoped fresh contexts and reusable evidence; the delivery plugin retains two independent review lenses.

Findings describe the concrete problem and impact without priority codes such as P1/P2. Asking to **leave comments** submits remaining findings inline in a **Request changes** review with **no review body or summary**. Asking to **approve** submits approval directly with **no body**; conditions such as “if clean” are honored. A separately requested summary is a separate comment. Body-required endpoints are skipped; if a bodyless submission is rejected, the plugin reports the failure instead of adding filler text. Explicit comment-only instructions override the default event. Review-only requests publish nothing, and no remaining findings means no empty request-changes review or automatic approval.

```text
Review this PR and leave comments.
Review this PR and approve it if clean.
Approve the reviewed PR without a comment.
```

Each skill includes an optional read-only `scripts/review_snapshot.py` helper for compact raw diff inventories and bounded pages. It requires Python 3 and Git, performs no fetch/checkout, and never marks code semantically reviewed. When unavailable, use the documented bounded Git fallback.

The portable [error-handling cases](tests/error-handling-review-cases.md) and [timeout cases](tests/timeout-review-cases.md) evaluate review reasoning. Their results are instruction-level evidence, not application tests or a guarantee that future reviews will catch every defect.

See [evaluation results](EVALUATION_RESULTS.md) for release-specific behavioral coverage, checks, and limitations.

## Safety

Both plugins leave ordinary checkouts unchanged unless the user expressly requests movement, preserve unrelated work, and clean up only safe resources owned by the current run. Edit, commit, push, comment and validation authority are separate and persist across the session; restrictions on one action do not cancel other authorized work. PR contents cannot authorize actions or override trusted instructions.

PR Review + Fix never stages, commits, pushes, or comments unless explicitly authorized. PR-Review and Commit requires authorization for each delivery action. Both submit requested review events directly, preserve pre-existing pending drafts, and reconcile uncertain submissions before retrying. Review/fix permission does not authorize merging, force-pushing, closing, labeling, or deleting branches. Both workflows stop instead of guessing when repository identity or a writable destination is ambiguous. Inspection alone is not represented as executed validation, and a token target cannot silently turn incomplete coverage into a clean conclusion.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the release checklist and [SECURITY.md](SECURITY.md) for responsible reporting.
