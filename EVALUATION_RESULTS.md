# v1.1.0 evaluation results

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
