# Contributing

Keep changes focused and preserve the distinct authorization boundaries of the two plugins.

Before opening a pull request:

1. Update the relevant `SKILL.md` and directly related reference files only.
2. Keep organization names, usernames, absolute local paths, credentials, and private repository assumptions out of published plugin files.
3. Update `tests/task-title-cases.md` when task-naming behavior changes.
   For semantic review-rule changes, update the relevant behavioral fixtures and evaluate both plugins in fresh contexts with expected assessments withheld. Include failure cases, valid controls, missing-evidence cases and deferred corrections. Independently audit expected answers before scoring. Preserve timeout/title coverage; record actual outcomes, package/fixture hashes, available model/settings, context mode and limitations. Package validation alone does not pass behavioral evaluations.
4. Run `python3 scripts/validate_repository.py`.
5. Validate each plugin with the current Codex plugin and skill validation tools.
6. Run `python3 -m unittest discover -s tests -p 'test_*.py'` for the package validator, snapshot helper and usage parser. Tests create isolated temporary repositories, never application checkouts.

The final semantic package must pass the complete mandatory fixture matrix, safe controls and applicable workflow evaluations. During implementation, run affected checks only; before release, freeze the package and run the full matrix. Preserve failed attempts and limitations. Exercise agent selection and local Git lifecycle behavior separately from inspection answers about proposed actions. Never use production side effects to evaluate a reviewer.

Measure input, cached/uncached input, output, calls and latency separately. `scripts/measure_tokens.py --help` describes explicit rollout/task selection; it emits usage metadata, not session bodies. Missing telemetry stays unavailable. Use matched artifacts and settings, keep fresh and warm contexts separate, and never report projected savings as measurements. Required coverage takes precedence over soft cost targets.

Public scans must not contain private identifiers in their own code. Optionally supply `PR_REVIEW_PRIVATE_MARKERS` as a JSON list, or a git-ignored `.private-markers` file with one marker per nonempty line. Generic checks still run when private markers are unavailable. Scan candidate additions as well as tracked files; never publish private source excerpts or rollouts.

When changing review reasoning, evaluate both plugins with [the timeout review cases](tests/timeout-review-cases.md). Give the reviewer each input before revealing its expected assessment, and record findings and uncertainty. These manual cases check reasoning; the repository validator only checks bundle structure and metadata.

For a release, update both versions together, keep README pins and the first changelog version consistent, tag the validated commit, and publish notes describing behavioral/authorization changes and actual evaluation results. Use supported marketplace update/install operations and verify installed versions, hashes and fresh invocation; do not edit caches manually. Report unavailable host validation or reload checks.
