# Evaluation results

## v1.2.1 — 2026-10-27

The investigation identified both an execution failure and a routing gap: prior instructions already required recovery and completed material traces, but review stopped at per-invocation IDs, and the database-runtime reference limited schema routing to changed schema contracts. Three concurrent independent agents audited the cause, edge cases and efficient validation before edits. The fix explicitly traces persisted state through interruption and a fresh invocation, includes relevant unchanged constraints, and reconciles shared evidence gaps. It adds 1,546 instruction bytes per plugin, with no additional mandatory agents or broad migration audit.

Both frozen packages received all 347 input-only cases in separate fresh contexts. Expected assessments were withheld and independently scored. Fourteen new lifecycle cases cover restart failures, restrictive constraints, ownership, missing evidence, safe cascade/rollback/reconciliation/retention, provider ambiguity and non-SQL resources. Ten prior fixture files are unchanged. Package, fixture and result hashes are in [the evaluation manifest](tests/evaluation-v1.2.1.json).

| Check | Observed result |
| --- | --- |
| Automated tests | 64 passed |
| Repository and skill-format validation | Passed for both packages |
| First complete fixture matrix | 687 passed, 7 correction-quality failures across 694 assessments |
| New lifecycle cases, included above | 28/28 passed |
| Fresh focused rechecks on the same package | 6/7 passed, in two contexts |
| Additional Review + Fix E36 singleton repeats | 3/3 passed |
| Source-discovery exercise | Baseline 2/2; candidate 2/2 passed |
| Disposable SQLite fixture mechanics | 3/3 passed |

The first Review + Fix matrix failed correction criteria for C20, D09, D11 and E36; Review and Commit failed D09, D11 and E36. C20 assumed a reusable accessible component without evidence. D09 omitted provider idempotency/conditional finalization; D11 omitted duplicate remediation before uniqueness; E36 omitted concurrency protection after moving remote work outside a lock. Findings were supported, but those corrections were incomplete. Fresh focused contexts supplied the missing safeguards in six cases. Review + Fix E36 remained under-specified: short coordinated updates did not establish protection from late results overwriting newer state. A fixed batch of three further fresh singleton contexts examined that case using the unchanged package and input; their actual results appear above. These observations supplement rather than erase the seven first-attempt failures and one focused failure. Every required case has a passing assessment on the frozen package, but the first full matrix was not a perfect pass and long-context consistency is not established.

The separate source-discovery fixture places its FK action in an unchanged schema file. All four fresh CLI reviews actually inspected that file, traced a committed child surviving process death through repeated parent-deletion failure, and proposed ownership-safe recovery. A disposable SQLite exercise independently reproduced two successive restart failures and recovery after owned-child cleanup. Neither exercise contacts a production database or performs a real review action.

| Source-discovery run | Input | Cached input | Uncached input | Output | Tool calls | Wall seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v1.2.0 Review + Fix | 115,317 | 93,952 | 21,365 | 1,889 | 13 | 94.941 |
| v1.2.1 Review + Fix | 149,651 | 128,000 | 21,651 | 1,669 | 11 | 89.703 |
| v1.2.0 Review and Commit | 118,793 | 83,456 | 35,337 | 1,748 | 9 | 81.898 |
| v1.2.1 Review and Commit | 117,851 | 94,848 | 23,003 | 2,434 | 12 | 124.173 |

Input is CLI-reported cumulative input, including cached and repeated context; it is not prompt size or billed cost. Model-call counts, exact served model/settings, and matrix/recheck usage are unavailable. There is one observation per variant/plugin, launch order is counterbalanced, and overlapping runs leave cache/resource state uncontrolled. Both baseline runs passed, so these results establish neither improved detection nor token, cost or latency savings. Coverage is bounded to the supplied cases, not every possible edge case.

Git lifecycle, agent-selection execution and publication boundaries are unchanged; their historical execution results below were not rerun. Release archives are checked against all 32 frozen package files. Supported installation, installed hash parity and fresh host discovery are verified separately during delivery. The current CLI exposes no dedicated plugin-validation command; repository and skill-format validation are the available checks. Use a fresh chat to load updated skills.

## v1.2.0 — 2026-10-26

Both plugins were evaluated against 333 input-only cases each, including 26 new review-action cases. Expected assessments were withheld from fresh-context reviewers and independently audited before scoring. Reviewers used inherited session settings; exact backend model/settings and per-run usage were not exposed, so no token, latency, or efficiency claim is made. Package, fixture, input, and output hashes are recorded in [the evaluation manifest](tests/evaluation-v1.2.0.json).

| Check | Observed result |
| --- | --- |
| Automated tests | 64 passed |
| Repository and skill-format validation | Passed for both packages |
| First complete fixture matrix | 662 passed, 4 correction-quality failures across 666 assessments |
| New review-action cases, included above | 52/52 passed |
| Fresh isolated rechecks of the four failed assessments | 4/4 passed on the same package |
| Additional critical-case plain/renamed-wrapper contexts | 12/12 passed |
| Frozen v1.1.0 baseline, three critical cases per plugin | 6/6 passed |
| Offline bodyless-review protocol model | 7/7 passed |

Each plugin's first matrix had the same two correction-quality misses: C20 assumed an accessible dialog primitive already existed, and D11 omitted the duplicate audit/remediation needed before adding uniqueness. The findings themselves were supported. Fresh isolated rechecks made primitive reuse conditional and explicitly handled existing duplicates and rollout. These passes supplement the original failures; they do not erase them or establish consistent behavior in long review contexts. Across the matrix, isolated rechecks, and additional repeats, there were 678 passes and four failures in 682 candidate observations. Every required case has a passing assessment on the frozen package, but the first complete matrix was not a perfect pass.

The oracle audit also corrected two unsupported expectations without changing inputs: C20 now conditions primitive reuse on verified availability; P01 treats an overlapping archive as a conflict-investigation lead, not a proven merge conflict. Earlier attempts and private raw evidence are retained separately. The two primary matrix contexts were larger than a typical targeted review; isolated rechecks are separate contexts, not a repeat of the entire matrix.

E01, E02 and E18 each passed in three fresh candidate contexts per plugin, including a renamed/transparent-wrapper holdout. The small matched baseline also passed; this does not demonstrate improved causal detection over v1.1.0. Task-title, timeout, safe-control, missing-evidence, action-boundary and deferred-correction cases remain covered.

The seven offline protocol checks cover bodyless pending-review creation/submission, bodyless approval, preservation of an existing draft, rejected submission without filler, reconciliation of lost create/submit responses, and JSON text preservation. This is a protocol model, not an end-to-end GitHub or agent tool-use test. Official REST documentation and read-only GraphQL schema inspection support the bodyless submission path; host-specific rejection remains possible and must be reported without adding a body. No real GitHub review was created, submitted, or approved for evaluation. Git lifecycle and agent-selection execution were not rerun because those paths were unchanged; their historical results below are not new v1.2.0 observations.

Release archives were checked against all 32 frozen package files. Managed installation, installed-file parity and fresh host discovery are verified during delivery, separately from the semantic scores. Use a fresh chat to load updated skills.

## Historical v1.1.0 evaluation results

The final candidate passed the causal review and focused private-regression gates below. Priority calibration and token use have material limitations; these results are bounded observations, not a guarantee of future review accuracy.

## Scope and method

The final candidate was tested against 307 portable cases across error handling, failure recording, security, database contracts, frontend and structural consistency, test evidence, PR operations, task titles, and timeout reasoning. Each plugin received the same input-only cases in fresh contexts. Expected assessments remained outside the reviewers' allowed inputs. Six critical scenarios and six transformed holdouts were repeated three times per plugin, giving 686 completed assessments in 48 contexts. These are instruction-level assessments, not application executions.

Separate operational evaluations exercise actual agents and disposable Git repositories. Private historical PR replays check findings against source contracts and independently adjudicated counterevidence. Private source, identifiers, full model transcripts, and operational logs are excluded from this public repository.

Three earlier candidates were rejected after private replay findings overstated missing product, provider, final-concurrency, or required-versus-optional operation contracts. Their results were retained privately. The final candidate requires evidence for observed behavior, required behavior, and claimed consequence; unavailable final enforcement remains an evidence gap.

## Completed automated checks

All 64 automated tests passed: 19 snapshot-helper tests, 25 usage-measurement tests, and 20 repository-validator tests. The helper tests cover unusual paths, binary/mode/rename changes, SHA-1/SHA-256 repositories, bounded pagination, and tamper detection. Usage tests cover modern and legacy telemetry, duplicate records, child attribution, and unknown metrics. The validator checks package parity, references, versions, privacy markers, and release metadata.

## Token and quality benchmark

The matched benchmark contains four scenarios, two plugins, three variants, and three repetitions: 72 observations. The variants are v1.0.5, an efficiency-only experimental variant, and the final v1.1.0 candidate. All 24 final-candidate observations passed independent causal scoring. Baseline and efficiency-only variants each passed 21/24; their six combined failures omitted the authorization issue in the review-and-fix high-risk scenario. They remain failures in the record.

Median input tokens below are cumulative CLI-reported input across the entire context, including cached input. They are not prompt-file token estimates or billed cost.

| Plugin | Scenario | v1.0.5 input | v1.1.0 input | Change | v1.1.0 uncached input | v1.1.0 output | Tool calls | Wall seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Review + Fix | Small | 47,559 | 69,096 | +45.3% | 11,705 | 783 | 2 | 48.2 |
| Review + Fix | Medium | 47,676 | 47,582 | -0.2% | 12,638 | 748 | 2 | 29.2 |
| Review + Fix | High risk | 47,875 | 55,558 | +16.0% | 17,158 | 843 | 4 | 42.9 |
| Review + Fix | Connected set | 48,117 | 84,577 | +75.8% | 14,102 | 1,031 | 6 | 46.3 |
| Review and Commit | Small | 54,134 | 97,047 | +79.3% | 17,196 | 959 | 4 | 42.3 |
| Review and Commit | Medium | 74,414 | 73,814 | -0.8% | 10,902 | 792 | 3 | 39.8 |
| Review and Commit | High risk | 47,586 | 75,403 | +58.5% | 17,696 | 1,077 | 3 | 46.5 |
| Review and Commit | Connected set | 74,548 | 75,336 | +1.1% | 18,841 | 1,074 | 5 | 45.5 |

Each metric is independently medianed over three runs; subtracting medians need not equal the median uncached input. The 25% input-reduction target was **not met**. Measured input and tool calls generally increased despite smaller core instruction files; the results vary with reference reads and uncontrolled caching. This release improves tested review coverage; it does not claim token savings.

The [aggregate CSV](tests/benchmark-v1.1.0.csv) includes all 24 plugin/scenario/variant groups, cached and uncached input, output, tool calls, command-output bytes, and wall time. These measurements are descriptive, with the limits below.

The experiment used the user's unchanged configured defaults (`gpt-6-astra`, `xhigh`) and CLI `0.162.0-alpha.17.2`. Actual served model identity and model-call counts were not exposed. Caching was uncontrolled and measured where available. The 48 unchanged baseline/efficiency observations were reused after hash/settings verification; the 24 final-candidate observations were collected later. This is not a fully counterbalanced timing experiment. CLI startup emitted configured connector authentication warnings; those are not review findings or model-initiated application operations.

One final delivery-plugin high-risk repetition used P0 instead of the oracle’s P1. Its rationale cited the supplied broad exposure and irreversible deletion; independent adjudication accepted the causal finding and safe fix while retaining the priority difference. Priority unanimity is not claimed.

The benchmark constrains operational actions and therefore does not measure the full cost of delivery or independent review agents. A separate real-agent workflow check compares the two lenses' findings; one synthetic high-risk scenario cannot justify removing a required lens.

## Operational evidence and reuse

Five actual agent-operated workflows passed in disposable repositories and local bare remotes:

| Plugin / mode | Verified state and behavior checks |
| --- | ---: |
| Review + Fix, review only | 13/13 |
| Review + Fix, authorized delivery | 19/19 |
| Review and Commit, review only | 13/13 |
| Review and Commit, authorized delivery | 19/19 |
| Review and Commit, independent reviewers explicitly forbidden | 12/12 |

Normal fixtures contained 101 changed paths and 102 hunks, paginated files and nested comments, dirty ordinary-checkout sentinels, distinct fork/base remotes, inert prompt injection, and two latent defects. Delivery runs made and verified fixes, ran five repository tests, created an `ai review` commit with an empty body, pushed non-force to the correct local fork, reconciled an uncertain comment response without duplication, and cleaned up only owned resources. Review-only runs preserved ordinary checkout state and made no delivery writes. The restricted-reviewer case disclosed the missing gate and withheld delivery; it does not simulate an actual host outage.

Eight real initial independent lenses each found both expected defects; four affected-evidence reruns verified the delivery corrections. The two-lens union added no finding on this one synthetic high-risk fixture. This is insufficient evidence to remove a required lens. Thirteen additional deterministic Git-mechanics checks passed, including race/partial-delivery mechanics; these are scripted checks, not additional model-operated workflows.

These five workflows ran on candidate r3. Candidate r4 changed only the two mirrored core paragraphs clarifying required versus optional substeps. Independent comparison verified unchanged workflow instructions, agent policies, helper code, and explicitly mandatory fixture contracts. Their operational evidence is retained with r3 provenance; it is **not** represented as five new r4 runs. All final instruction-level cases are rerun on r4, and affected private completion contracts receive separate fresh focused replays.

## Final semantic and private-regression results

All **686/686** final instruction-level observations passed causal detection, safe-correction, control/gap handling, and action-boundary scoring. The final package hashes, exact case/run identities, answer hashes, and recorded tool traces were checked. No unsupported confirmed finding, unsafe prescribed correction, or unauthorized model action was identified in those final runs. Collection began with 12 workers; eight additional workers atomically claimed 12 unstarted contexts to finish sooner. Existing or completed contexts were not repeated. Original collector ownership errors were reconciled against successful canonical results, not counted as model passes.

Priority calibration is separate: **four explicit misses** assigned P2 instead of the fixture's P3 for optional-analytics diagnostics and approved recovery-copy conventions, across both plugins. Further P1/P2 boundary variation occurred in policy enforcement, resource-budget, stale-owner, and partial-state cases; one benchmark repetition used a source-justified P0 instead of P1. These differences remain in the evaluation record. Perfect severity consistency is not claimed.

The final focused private replay passed **6/6** fresh contexts, three per plugin. Every run distinguished allowed optional provider degradation from required completion, checked account reactivation and benign absence, and retained the supported invitation-recovery defect. Reviewers received 14 frozen source-input files, with the independent oracle withheld. Package/input hashes and actual permitted reference reads were verified. The original broader replay covered two connected historical sets comprising five PRs, 32 inventory entries and 79 text hunks; its earlier failed findings remain recorded privately. The six final runs re-evaluated all completion-contract areas affected by the last instruction change. They are scoped regressions, **not six fresh whole-PR reviews**. Unchanged historical source/coverage evidence was retained with its original provenance.

The repository CI validates packaging and runs the automated tests on pushed commits. Managed installation is checked through the supported marketplace CLI, manifest/source parity, and fresh review-only invocations; it is separate from these review-quality scores. See the [release](https://github.com/manojspace/codex-pr-review-plugins/releases/tag/v1.1.0) for the published revision. A fresh chat is needed to load updated skills into a new context.
