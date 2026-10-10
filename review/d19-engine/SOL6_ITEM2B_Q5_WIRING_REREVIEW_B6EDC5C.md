<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a127a8-731d-7332-b6d5-5ae509be1af0. Tokens used: 35,745. Made from a packet (Codex's command runner fails here): the re-review prompt, SOL6_ITEM2B_Q5_WIRING_REVIEW_58B3996.md, ADJUDICATION_ITEM2BW_58B3996.md, the 'Interpretations made here' section of ITEM1_DEVELOPMENT_AND_CHOICES.md, git diff 58b3996..b6edc5c -- calibration scripts tests, the HEAD text of calibration/reduce.py, calibration/semi.py, scripts/d19_run.py, scripts/d19_run_definition.py and scripts/d19_choose.py, and the accepted preregistration §3.5 and §13. -->

# Independent re-review: D-19 item 2b step 1, Q5 wiring repairs

**Reviewer model metadata:** Codex, GPT-6 family, as identified by the session instructions. The exact served model ID and reasoning effort are not exposed to me.  
**Commit reviewed:** `b6edc5c` (diff from `58b3996`).  
**Scope:** Adjudication of I2BW-1 through I2BW-5, the supplied repair diff and HEAD excerpts, the changed tests, and accepted preregistration §3.5 and §13 item 4.  
**Basis:** Attachments only. I did not inspect the repository or independently verify the reported checks.  
**Commands run:** None; the command runner was unavailable.  
**Verdict for pilot use:** **FIX**.

## Prior findings

| ID | Status | Assessment |
|---|---|---|
| **I2BW-1** | **Partly repaired; protocol disagreement unresolved** | `reduce.pooled`, the driver, and `d19_choose` now handle multiple T levels within a K. The attached test covers that behavior. Pooling remains separated by K. Section 3.5 item 2 says the extreme over **all** candidate cells per T level. Section 13 makes K an exact classifier check, but that does not itself prevent pooling the stochastic tails shared across K values and retaining an exact K check for the evaluated cell. Correlation tails would apply only at K ≥ 2. The cited item 1 note expressly calls per-K pooling an **AI default for review and the owner**; seven review rounds do not establish an owner-approved change to the accepted text. The adjudication’s claim that pooling across K “could therefore never accept” describes the current implementation’s treatment of exact fields, not a necessary consequence of §3.5. Obtain an owner binding for per-(K, T) pooling or implement pooling of applicable stochastic tails across K at each T. |
| **I2BW-2** | **Unresolved** | Record time now rejects `{}` and a manifest whose claimed BTC hash differs from the source. It checks only four JSON fields, however. A small JSON object containing those fields and a copied `manifest_sha256` passes even if it is not the BTC manifest built from `--raw-root`. The run definition then hashes that supplied file. The test covers mismatched claims, not a forged matching claim. Compare the supplied manifest with the generated BTC manifest or validate its complete content and self-hash before recording it. |
| **I2BW-3** | **Resolved for the reported failure** | `load_source` validates the demeaned returns and computes `v_bar` before record writes a definition; each worker loads a source and reuses its `v_bar` for draws. The return-byte identity is checked against the definition. The attached invalid-source test supports the refusal path. “Once per source” is implemented once per load, including a separate load in each worker, which gives a fixed value for that worker’s draws. |
| **I2BW-4** | **Disagreement justified** | The tuple shape did change, as the adjudication acknowledges. The attached driver passes the extra arguments to its own worker, whose defaults retain the earlier call form. On the supplied evidence, keeping this internal change is reasonable; the earlier “unchanged tuples” claim needed correction, not a code reversal. |
| **I2BW-5** | **Partly repaired** | The test now independently reconstructs every stored Q5 development diagnostic using the development seed. It also calls `choices.consistent` on each record. That is a useful integration check, but it uses the production consistency validator and supplies no independently expected Annex B or `U_G` result. The original concern about an incorrect substantive development result remains. The implementation of `choices.consistent` was not attached, so its asserted coverage cannot be independently confirmed here. |

## Pooling interpretation

Per-(K, T) pooling is operationally coherent with exact K checks and with K = 1 having no correlation tails. It is **not established as consistent with the accepted wording** “per T level, the extreme over all candidate cells.” Exact checking concerns whether an evaluated window has the required K; it does not settle which candidate cells contribute to a shared stochastic-tail threshold. The item 1 note records a proposed interpretation, not an amendment. This question needs an owner binding before the pilot treats these development thresholds as the accepted method.

## Defects introduced by the repair

I found **no distinct new functional defect** in the attached changes. The permissive manifest check is an incomplete repair of I2BW-2, and the per-K scope is the unresolved part of I2BW-1; neither needs a new finding ID. The reported tests, lint, types, import checks, and frozen verification are drafter reports and were not rerun in this review.

**New findings:** None; no I2BWR ID assigned.
