# Two-Agent Review Gate

Load this reference only before non-trivial edits or uncertain high-impact conclusions. Do not block first-pass findings on subagents.

Run this gate before any non-trivial edit, broad fix recommendation, or high-risk conclusion that remains uncertain after direct source inspection.

## Independent Lenses

Start two parallel agents with neutral prompts and raw artifacts only.

Agent A lens:

- correctness;
- scalability;
- error handling;
- retries;
- partial failures;
- idempotency;
- logging and observability.

Agent B lens:

- cross-repo contracts;
- schema/API drift;
- generated clients;
- env/config mismatch;
- release order;
- existing-code inconsistency.

Do not pass one agent's output to the other. Do not give either agent a preferred conclusion.

## Artifact Bundle

Pass only relevant artifacts:

- user request and success criteria;
- PR URLs and metadata snapshot;
- org routing decision;
- changed-file inventory;
- targeted diffs/hunks;
- relevant `AGENTS.md` instructions;
- relevant contracts, schemas, routes, env/config, package manifests, generated-client context, tests, logs, or CI status;
- validation constraints and commands already run.

Avoid full repo dumps. Prefer targeted diffs and surrounding code.

## Required Agent Output

Require each agent to return:

- findings ordered by severity;
- evidence;
- files inspected;
- unknowns and blind spots;
- suggested fix or validation;
- confidence.

A "no findings" response only counts if it lists what was inspected and what remains unverified.

## Retry And Fallback

Wait for both agents before non-trivial fixes. If one times out, retry once with a narrower artifact bundle. If it still fails, manually perform that lens and disclose reduced independence.

If code changes materially after agent review, rerun only the affected lens when the change could alter that lens's conclusion.

## Adjudication

Do not use majority vote. Source code, schemas, tests, CI output, and reproducible command output outrank agent claims. For contradictions, inspect cited evidence directly. If a high-impact contradiction remains unresolved, ask the user before fixing.

Before editing, summarize:

- Agent A status;
- Agent B status;
- accepted findings;
- rejected findings;
- open contradictions;
- fix scope;
- validation plan or validation intentionally skipped.
