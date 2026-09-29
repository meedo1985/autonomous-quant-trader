# Task 25 owner behavioural review (Constitution section 16)

Date: 2026-09-29. Reviewed state: `35d941b` on `task25-drills-evidence`
(PR #31). Guided walkthrough by Claude Opus 5.5, four yes/no questions, as
for Tasks 17 and 21-24. Questions quoted as asked; answers are the owner's.

1. **Drills.** "Task 25 ran six drills on real 2020 prices against the
   simulator (normal run, HALT, FLATTEN, unsure order, FREEZE recovery,
   refused start). All passed, and each one is proven to fail if the safety
   feature it tests is broken. Is this the proof you want before moving on?"
   — **Yes**
2. **Honesty.** "The evidence packet states plainly that this is a simulated
   run on old data, shows NO trading edge, counts zero research trials, and
   opens NO path to real money. Is that the right message?" — **Yes**
3. **Sell log.** "Every emergency sell whose reply arrives is now written to
   the audit log, with how much was held before it. A sell whose reply is
   lost is not yet logged as an order (it FREEZEs and records the order id in
   the incident); that gap will be fixed together with the Task 23-24 fixes.
   Is that OK?" — **Yes** ("Merge Task 25 now; fix the lost-reply logging in
   the next fix branch.")
4. **Evidence.** "The drill script never overwrites earlier results, and the
   saved logs are protected so their tamper-evident chains survive any copy
   or checkout. Is that what you want?" — **Yes**

## Correction told to the owner after his answers

Question 1 overstated one point. Break-tests (mutations) were run for the
HALT drill, the FLATTEN drill (100% step, early stop), the credential
non-echo check (by Astra) and the FREEZE drill (lost reply vs rejection,
`tests/integration/test_drills.py`). The clean-run and ambiguous-order drills
were not mutation-tested. The AI told the owner this before recording.

## Reviews

GPT-6 Astra (CLI `model: gpt-6-astra`): `01f10ad` FIX; re-review attempts 1
(memory) and 2 (usage limit) incomplete; attempt 3 on `9727496` **ACCEPT**
(`ASTRA_REREVIEW_9727496.md`). `35d941b` adds only the narrowed packet claim
and adjudication text.

This review authorizes no real money, credential, live price use or
deployment. Merge only on the owner's instruction.
