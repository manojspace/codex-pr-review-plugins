# Contributing

Keep changes focused and preserve the distinct authorization boundaries of the two plugins.

Before opening a pull request:

1. Update the relevant `SKILL.md` and directly related reference files only.
2. Keep organization names, usernames, absolute local paths, credentials, and private repository assumptions out of published plugin files.
3. Update `tests/task-title-cases.md` when task-naming behavior changes.
4. Run `python3 scripts/validate_repository.py`.
5. Validate each plugin with the current Codex plugin and skill validation tools.

When changing review reasoning, evaluate both plugins with [the timeout review cases](tests/timeout-review-cases.md). Give the reviewer each input before revealing its expected assessment, and record findings and uncertainty. These manual cases check reasoning; the repository validator only checks bundle structure and metadata.

For a release, update both plugin versions together, add a changelog entry, tag the validated commit, and publish release notes describing behavioral or authorization changes.
