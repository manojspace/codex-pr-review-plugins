# Timeout Review Evaluation Cases

Use these portable inputs to evaluate either plugin's review reasoning. They require no application, credentials, external services, or test runner. In separate review contexts, provide the updated skill and review gates plus one input at a time; withhold the expected assessments below until scoring. Use a review-only request so the delivery plugin does not edit, commit, or comment.

Ask for findings, the effective enclosing deadline, evidence, and uncertainty. Do not tell the reviewer which cases should have findings. Record the plugin version and actual answers; parsing this file or passing repository validation does not count as passing these behavioral cases.

## Input A: Longer Wait In A Multi-Step Test

The PR claims to tolerate a status response taking 55 seconds during a known latency spike. It changes only the status wait from 20 to 60 seconds. The default per-test deadline is 120 seconds, with no project, suite, fixture, or test override. All operations below run sequentially within one test. Controlled timing data establishes setup at 25 seconds, status readiness 55 seconds after its wait starts, exit-SMS readiness 50 seconds after sending, and receipt work at 5 seconds. Readiness remains satisfied after each event. The measured healthy run finishes in 35 seconds.

```ts
test('complete stay', async () => {
  await setupPayment();
  await expect(status).toBeVisible({ timeout: 60_000 }); // was 20_000
  await sendExit();
  await expect(exitSms).toBeVisible({ timeout: 60_000 });
  await verifyReceipt();
});
```

The send operation is immediate for this scenario. The timing data describes each stage independently; it is not a claim that the complete test already ran for 135 seconds under a 120-second limit.

## Input B: Two Assertions Observe One Readiness Event

The per-test deadline is 90 seconds, with no overrides. The PR raises the garage-name wait from 30 to 60 seconds to handle data arriving at 40 seconds. The same render makes both the garage name and Entry Time label visible; both remain visible thereafter. There is no reload or intervening navigation. Remaining receipt work takes 10 seconds. No other setup or hooks consume time in this fixture.

```ts
test('status page', async () => {
  await expect(garageName).toBeVisible({ timeout: 60_000 }); // was 30_000
  await expect(entryTimeLabel).toBeVisible({ timeout: 60_000 });
  await verifyReceipt();
});
```

## Input C: Separate Tests And An Effective Override

The default per-test deadline is 90 seconds. A serial suite contains two separately budgeted tests. No hooks or fixtures add time. The PR raises a shared wait ceiling from 30 to 60 seconds in both tests. The first test takes 10 seconds of setup plus a 50-second welcome wait. The second test has an effective override set before doing any work: setup takes 25 seconds, status readiness takes 55 seconds, exit readiness takes 50 seconds, and receipt work takes 5 seconds. Events start at their respective waits; assertions remain satisfied afterwards.

```ts
test.describe.serial('stay', () => {
  test('open stay', async () => {
    await setupSession();
    await expect(welcomeSms).toBeVisible({ timeout: 60_000 }); // was 30_000
  });

  test('finish stay', async () => {
    test.setTimeout(180_000);
    await setupPayment();
    await expect(status).toBeVisible({ timeout: 60_000 }); // was 30_000
    await expect(exitSms).toBeVisible({ timeout: 60_000 });
    await verifyReceipt();
  });
});
```

## Expected Assessments (Withhold During Review)

| Case | Expected result | Required reasoning |
| --- | --- | --- |
| A | A concrete budget finding is warranted. | The intended successful path needs 25 + 55 + 50 + 5 = 135 seconds. The outer 120-second deadline interrupts it despite both waits individually being within their ceilings. This is incomplete handling of the PR's promised scenario, not proof that it newly breaks healthy runs. Recommend a scoped budget adjustment or a demonstrated way to reduce the work; do not change assertions or global defaults automatically. The 35-second healthy run does not test the target condition. |
| B | No deadline finding from these facts. | Both assertions observe one stable readiness event. The modeled path takes about 40 + 10 = 50 seconds, not 60 + 60 + 10. Do not recommend a larger timeout solely from summing ceilings. |
| C | No deadline finding from these facts. | The first test takes 60 seconds within its 90-second budget; the second takes 135 seconds within its effective 180-second budget. Serial execution does not combine their per-test deadlines. Do not ignore the override or add suite-wide waits together. |

A case passes only when its conclusion and causal reasoning match. Invented timings, counting maxima as measured durations, unsupported certainty, or claiming these fixtures prove production reliability fail the evaluation. When real review inputs omit timing or readiness evidence, identify the smallest missing evidence instead of inventing it.

## Recorded Evaluation: 2026-09-24

One independent reviewer context per plugin read the updated instructions and inputs with the expected assessments withheld. Both version 1.0.4 bundles passed A, B, and C: they identified expiry at 120 seconds before exit readiness at 130 seconds in A, a single readiness delay and 50-second completion in B, and separate 60/135-second paths within their 90/180-second budgets in C. Both distinguished modeled timings from an executed reproduction.

This is one instruction-level evaluation per plugin, not a runtime test or a guarantee of future review quality. No application tests or external services were run for these cases.
