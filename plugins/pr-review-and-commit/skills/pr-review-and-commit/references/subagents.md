# Mandatory Two-Agent Review Gate

Load this reference after the changed-file inventory and connected-PR graph are available. Complete this gate before any edit on every run.

## Independent Concurrent Lenses

Start two agents concurrently with neutral prompts and the same relevant raw artifacts. Do not pass one agent's output or a preferred conclusion to the other.

Agent A reviews:

- correctness and runtime behavior;
- scalability and performance;
- async flow, retries, partial failures, and idempotency;
- error handling, logging, and observability.

Trace material failures forward from producer outcomes through caller decisions, completed/pending effects, and the final response or acknowledgment.

Agent B reviews:

- cross-repo contracts and schema/API drift;
- generated clients and package contracts;
- environment and deployment configuration;
- release order and existing-code inconsistency.

Independently work backward from required success conditions through local and cross-repository caller–callee contracts, including unchanged dependencies and return-versus-throw behavior. Verify whether the inspected consumers support the claimed outcome and retry behavior.

## Artifact Bundle

Pass only relevant artifacts:

- user request and authorization boundaries;
- PR URLs and metadata snapshot;
- routing decisions and exact base/head SHAs;
- changed-file inventory and targeted diffs;
- connected producer-consumer graph;
- relevant repository instructions, callers, contracts, schemas, tests, CI, comments, and validation constraints.
- unchanged callees and outcome-transforming wrappers needed to resolve consequential calls.

Avoid full repository dumps and unrelated files.

## Required Agent Output

Require each agent to return:

- findings ordered by severity;
- direct evidence and affected PR/file;
- files and context inspected;
- suggested fix;
- unknowns, blind spots, and confidence.

Include compact operation-outcome coverage, missing material contracts, and counterevidence for apparent best-effort or idempotent cases. Distinguish a confirmed finding from uncertainty about its fix. Before confirming a finding, identify the inspected producer and consumer/recovery evidence; hypothetical rejection of an unavailable helper is a coverage gap, not an additional confirmed defect. A no-findings opinion without completed material coverage cannot support an unqualified clean recommendation.

A no-findings response counts only when it states what was inspected and what remains unverified.

## Retry And Recheck

Wait for both agents before editing. If either agent times out or fails, launch a fresh concurrent replacement pair with a narrower artifact bundle. If two independent agent results still cannot be obtained, stop before edits or delivery and ask the user; do not substitute a manual lens for the required independent review.

After edits, rerun only a lens whose conclusion may have changed materially. Do not rerun agents merely to obtain agreement.

## Adjudication

Do not use majority vote. Source code, schemas, tests, CI, GitHub state, and reproducible command output outrank agent claims. Inspect cited evidence directly. If a high-impact contradiction remains unresolved, stop that fix and ask the user.

Before editing, record both agent statuses, confirmed/rejected findings, fix readiness, contradictions, fix scope, and inspection plan.
