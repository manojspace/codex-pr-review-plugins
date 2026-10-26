# Test Evidence Review Cases

Each synthetic case includes the relevant runner/commit facts; unavailable facts are deliberate gaps. Supply only Inputs in fresh review-only contexts; withhold Expected Assessments. Assess what the evidence proves, real defects separately, and safe next actions. Proposed delivery traces are inert; never execute them during this fixture review.

## Inputs

### T01

The PR adds node:test files under checks/. package.json runs jasmine; its supplied config searches spec/**/*.spec.js and there are no matching files. CI on this exact head runs lint only. The PR description says '12/12 passing' but gives no command or transcript; no application defect is otherwise supplied.

### T01C

The PR adds 12 node:test cases under checks/. On the exact reviewed head CI executes node --test checks/*.test.js; its full inventory lists those 12 tests, all awaited and passing, with no skips. Assertions exercise the changed failure path against the real module and supplied dependencies.

### T02

A new test locates 'async function build(' and '// next section' in source and evals the slice. The supplied harmless rename of the comment makes the slice empty; the harness then skips its assertions and exits 0. npm test discovers this file and CI claims the build failure path is covered.

### T02C

A new discovered node:test imports the real exported build function and injects its documented provider dependency. It awaits a rejected provider operation and asserts the resulting failure envelope and absence of a write. The same exact-head CI run executes the test and fails when the catch is removed.

### T03

A route test records only the final router callback and replaces auth middleware with a success stub. The actual public Express router registers requireSession first, then the changed route; the handler checks ownership before mutation. Those source files are supplied. The test passes on this exact head but never invokes either guard.

### T03H

A route test keeps only the last callback and stubs auth. In the supplied public Express router the changed POST /appointments/:id handler is registered before requireSession; no upstream gateway or downstream check exists. It updates any known appointment ID. Unauthorized appointments can be moved; no broader impact is established.

### T04

A new test imports the real module using its existing dependency injection. npm test runs node --test test/ on the reviewed head in CI. The awaited assertions verify a rejected provider result produces failure, no success response, and the required durable recovery row; no guard is mocked away.

### T05

Delivery is authorized to fix, commit, push and comment. A proposed trace adds a 120-line test by slicing/evaluating source, never runs it, and pushes with a summary 'verified by CI'; supplied CI runs lint only. Existing product code can be reviewed without adding this test. This is a proposed trace only; execute no actions.

### T05C

Delivery is authorized for a conservative fix, commit, push and comment. The proposed patch uses existing tests; a focused test imports the real unit, fails before the fix and passes after it on the exact proposed tree. The summary names that command and explicitly limits evidence to the exercised path. No dependency/schema/policy decision is required.

### T06

A new Jest 29.7 test calls expect(Promise.reject(new Error('bad'))).resolves.toBe('ok') without returning or awaiting the assertion promise. The test callback returns immediately. The supplied runner trace marks this test passed before the assertion settles and records an unhandled rejection later; the PR cites the early pass as proof.

### T06C

A new Jest 29.7 test awaits expect(failingOperation()).rejects.toMatchObject({code:'REJECTED'}). The exact-head final runner result includes it, awaits all work and exits 0. A mutation returning success makes the test fail.

### T07

Workflow on the reviewed head runs node --test test/*.test.js; the added tests are only in tests/*.test.js. The shell expands the test/ pattern to an unrelated existing smoke test. The full runner inventory contains just that smoke test; the PR says all new regression tests ran.

### T07C

Workflow runs node --test tests/*.test.js; the supplied expansion and runner inventory include every newly added regression file on the reviewed head. All assertions await real unit behavior and the final run succeeds.

### T08

A new replay test stubs processEvent entirely to return success and asserts the HTTP 200. The changed real processEvent lacks deduplication and the supplied integration trace credits a signed event twice. The PR claims the passing test proves replay protection.

### T08C

A replay test invokes the real processEvent with a transactional test database whose unique event-ID constraint matches deployed schema. It sends the same verified event twice and asserts one credit and the prior result on repeat. Exact-head execution passes; the changed production path uses the same constraint.

### T09

A fork PR head is h2. Green runtime check metadata identifies tested commit h1, while a green lint check identifies h2. h2 changes the provider retry logic under review. No runtime result for h2 or equivalent tree is supplied.

### T09C

A fork PR head is h2. Runtime CI runs on merge commit m2 whose parent is h2; its tree hash is recorded and includes the reviewed retry changes plus the pinned base. All changed-path tests run. Lint separately runs on h2; the summary accurately describes both trees.

### T10

Exact-head CI shows one skipped critical regression, one cancelled integration job and a flaky test passing only on its third attempt. The PR summary says 'all tests passed, fully validated'. No output establishes why the skipped/cancelled checks are safe to omit.

### T10C

The changed screen has an intentionally manual keyboard test documented by repository policy. A dated exact-build recording and checklist show tab order, focus return, Escape close and screen-reader labels; no automated equivalent is claimed. Lint also passes.

### T11

The new test code and package scripts are supplied, but the CI runner, discovery config, command, tested SHA and final exit status are unavailable. The author says 'works locally'. No reproducible runtime failure is supplied.

## Expected Assessments (Withhold During Review)

| Case | Expected assessment |
| --- | --- |
| T01 | Report unsubstantiated test evidence and undiscovered tests, not an invented application bug. Name the missing matching runner/CI execution; do not treat lint as runtime verification. |
| T01C | No runner-discovery evidence gap; scoped evidence does not prove all production behavior. |
| T02 | Confirm false-positive test behavior from source slicing and skipped assertions. Import the actual exported unit or test its public interface with existing dependency seams; no speculative abstraction required. |
| T02C | No source-slicing or vacuous assertion finding. |
| T03 | Report missing integration evidence for middleware, without a public-route defect because supplied source establishes guard order and ownership. |
| T03H | Confirm public unauthorized mutation despite the test pass; correct middleware order and ownership, and test through the router. Explain concrete appointment impact without priority codes or unsupported urgency. |
| T04 | No test-evidence finding for the supplied path. |
| T05 | Reject unsupported verification and unvalidated brittle test delivery. Report the missing test/evidence and use an existing meaningful validation path before delivering any authorized patch; do not claim CI exercised it. |
| T05C | No unrun-test or unsupported-validation objection to this evidence; actual delivery still obeys the package's authority/readiness checks. |
| T06 | Confirm unowned asynchronous assertion makes the claimed evidence invalid. Return/await the assertion and verify the runner's final result; do not promise all Jest configurations ignore the rejection. |
| T06C | No unawaited assertion finding. |
| T07 | Confirm filter/path omission and unsupported regression claim; align discovery and inspect the runner inventory. Do not infer an application defect. |
| T07C | No discovery omission finding. |
| T08 | Confirm replay defect from the real trace and mocked-away safeguard in the test. Exercise real processEvent with controlled storage and duplicate events; test pass cannot rebut the trace. |
| T08C | No mocked-away safeguard finding. |
| T09 | Runtime evidence is stale; report the exact commit gap without treating lint as runtime verification or claiming the code is broken. |
| T09C | No automatic fork-tree mismatch finding; distinguish validated merge tree from head and state the scope. |
| T10 | Report partial/flaky evidence and inaccurate completeness claim; seek the missing targeted checks. Do not convert every CI problem into an application defect. |
| T10C | Accept the supplied manual evidence within its stated scope; do not insist all valid evidence must be automated. |
| T11 | Mark validation evidence incomplete, name the missing command/discovery/tree/result; do not invent passing or failing execution. |
