# Fix Policy

Load this reference only when edits are requested, clearly accepted, or needed for an approved non-trivial fix path.

Review broadly, fix narrowly.

## Auto-Fix Eligibility

Auto-fix only when all are true:

- the issue is concrete and likely to attract reviewer comment or future production risk;
- intended behavior is clear from nearby code, tests, docs, or existing patterns;
- the fix is small, local, reversible, and inspection-verifiable;
- the fix does not alter public API, DB schema/data, migrations, auth/permissions, billing/privacy, dependencies/lockfiles, generated/vendor/minified files, or cross-repo contracts;
- lint/build/tests are not required to know whether the edit is reasonable.

Good auto-fix candidates:

- obvious null/undefined handling that matches local conventions;
- wrong variable, missing import, missing `await`, missing `return`, or wrong condition with clear intent;
- narrow try/catch/logging addition that follows nearby patterns and avoids sensitive data;
- local error propagation or cleanup/finally behavior with clear existing style;
- small consistency correction where sibling code proves intended behavior.

## Ask Before Editing

Ask before changing:

- product behavior choices;
- public API, route, schema, type, SDK, event, webhook, or generated-client contracts;
- DB migrations, indexes, seed data, model fields, enum values, backfills, destructive updates, or rollback behavior;
- auth, permission, role, tenancy, session, token, privacy, billing, or security-sensitive behavior;
- dependencies, package manager metadata, or lockfiles;
- generated, vendor, minified, snapshot, or binary files unless the source generator is known and the user asked to regenerate;
- broad refactors or new validation layers;
- coordinated multi-repo edits;
- fixes whose correctness depends on lint/build/tests that are disallowed by default.

## Editing Rules

Before editing, state:

- accepted findings;
- files intended to touch;
- why each fix is safe without lint/build;
- validation that will be skipped.

During editing:

- preserve unrelated dirty work and unrelated hunks;
- keep every changed line traceable to an accepted finding;
- do not clean up unrelated code;
- do not stage, commit, push, merge, approve, request changes, close, label, run lint/build/full tests/package scripts/migrations/installs/codegen unless explicitly asked.

After editing, report:

- files changed;
- exact behavior fixed;
- validation run or skipped by policy;
- remaining compile/type/test risk;
- findings intentionally not fixed and why;
- deferred issues needing approval.

Do not claim verification unless validation ran. Use "reviewed by inspection" when validation is intentionally skipped.
