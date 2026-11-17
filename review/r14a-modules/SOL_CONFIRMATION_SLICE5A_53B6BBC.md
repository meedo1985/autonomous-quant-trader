# Sol review: confirmation slice 5a (verdict FIX)

- Reviewer: OpenAI Codex CLI v0.164.0, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a1c112-061b-7940-874e-1f2e37c014ee`, 2026-11-09.
- Reviewed commit: `53b6bbc`. Prompt: see the slice prompt file. Recorded verbatim below (final message only); adjudication in the matching ADJUDICATION file.

---

What this change does: Slice 5a adds the confirmation-side A4 forecast, reruns the nominee’s BTC baseline pair, and builds the prediction artifact and family sealing record. I reviewed commit `53b6bbc`; the checkout’s later 5b commit was outside scope.

### Findings

1. **R14S5-S-1 — BLOCKER:** [c2_confirmation.py:1948](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1948) copies the trial index, seed policy, and estimator seed from caller-supplied `seeds` without checking them against the nominee record and line-266 derivation. For a rule-based nominee, changing `estimator_seed` by one still produces status **(a)**; I reproduced that result. The lockbox then rejects the artifact as `IDENTITY_MISMATCH`. Annex D §§D-3.2, D-3.5 and D-1.7 require a valid sealed artifact for (a). Check those bindings before returning (a), and test a wrong seed and index.

2. **R14S5-S-2 — BLOCKER:** [c2_confirmation.py:1998](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1998) accepts a sealing record containing only `trend`; I reproduced it. An eligible C2 window declares both families, and Annex D §D-1.7 requires each declared family’s terminal status before a read. Require the entries to match the declared families and test a missing family.

3. **R14S5-S-3 — BLOCKER in the connected lockbox contract:** [c2_lockbox.py:622](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:622) checks the `source` and `block` *keys* but not their values. Its shape, identity, and P-4 checks accepted an artifact with `source.n = -1`, `source.d_sha256 = "bad"`, and `block.value = "bad"`. This does not meet the field meanings in Annex D §D-3.5; [the new positive test](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_seal.py:106) would miss it. Validate those fields at pre-read and add negative tests. A wrong `seed_source` **was** refused as `IDENTITY_MISMATCH`.

4. **R14S5-S-4 — BLOCKER test gap:** [test_c2_confirmation_seal.py:146](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_seal.py:146) tests `baseline_d` only with a rule-based trial without an overlay and with seed zero. Removing the model-fit or overlay branch from [baseline_d](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1780) would leave this test green. Annex D §D-3.5 A7 step 1 and R-14d require the registered nominee run. Add a synthetic model and overlay case with a nonzero registered estimator seed.

5. **R14S5-S-5 — NON-BLOCKING:** [c2_confirmation.py:1918](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1918) reads the family seed before its sealing `try` block. A missing family entry raises `KeyError`, which I reproduced, rather than status (d). This qualifies LG5-5’s “any failure” claim under Annex D §D-3.5. Put failures encountered during sealing within the status-(d) handling; keep earlier seed-derivation failure governed by the evaluation-invalid rule.

### Checks and limits

- **Q-D1 passed:** the copied A4 function and class source and all seven constants match the lockbox copy. The tests would catch a one-sided function or constant edit. The generator emits the schema’s fields, numeric-sorts the 2,000 hexadecimal replicates, and hashes the artifact as `SHA256(cj(artifact))`.
- **Baseline and statuses:** `baseline_d` uses the same frozen target, event, cost, and daily-return functions as `screen_gates`; its `c − b` series is C-0 **E-DIFF**. The code maps no nominee to (b), `FAILED` to (c), and `NO_RESULT` to (d), so gate unavailability takes precedence over failure. The caller still supplies the path, pre-look `d_sha256`, evaluation-record hash, seed record, and signed-code values; slice 6 must bind them.
- **LG5-1–5:** I disagree with LG5-1’s implied completeness because a family may be omitted, and with LG5-5’s unrestricted “any failure” claim. LG5-2’s pre-sealing evaluation-record hash and LG5-3’s pre-look hash producer remain unverified until wiring. LG5-4’s window comparison is present.
- **Validation:** 22 focused tests passed; 11 fixture-dependent tests were deselected. Ruff check and format, mypy on 56 source files, and all seven import-boundary contracts passed. Full pytest could not run because this read-only environment has no writable temporary directory. No frozen-file changes appear in `bf07eec..53b6bbc`. I did not read confirmation or lockbox data, verify slice 6 wiring, or independently rerun all slices 1–4a.

**Verdict: FIX.** This read-only review approves nothing. The required committed review record and full mandatory test gate remain outstanding.
