# Sol re-check: confirmation slices 5a/5b repairs (verdict FIX)

- Reviewer: OpenAI Codex CLI v0.164.0, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a1c124-661d-7781-98ea-b286276b2427`, 2026-11-09.
- Reviewed: repairs `292def2..77b41ec` at `775a3e4`. Recorded verbatim below (final message only).

---

**What this change does:** Commit `77b41ec` repairs seed binding and sealing, lockbox artifact checks, CPCV split embargo, and tests. I reviewed those changes at `775a3e4` using the committed diff. This is an independent read-only review, not an approval.

| Earlier finding | Status | Evidence |
|---|---|---|
| R14S5-S-1 | **CLOSED** | `seal_family` recomputes line 266 from the trial record and compares the index, derived seed, policy, and estimator seed before status (a). It uses the same function and inputs as `derive_seeds`; I found no disagreement path with immutable inputs. |
| R14S5-S-2 | **CLOSED** | `sealing_record` requires entries to equal the declared family set. “Exactly the declared families” is right: `check_declaration` requires both only for an eligible window and permits one for a non-eligible window. |
| R14S5-S-3 | **PARTLY** | The repair rejects the malformed values in the original finding and accepts a valid degenerate `raw = 0.0`. It still accepts an impossible block length; see R14S5R-S-1. |
| R14S5-S-4 | **CLOSED** | The added synthetic test exercises a model, overlay, and nonzero seed, checks every fit’s seed, and checks the resulting daily series. |
| R14S5-S-5 | **CLOSED** | A missing family seed now raises `CycleError` as an invalid seed record. Failures later in eligible-nominee sealing yield status (d). |
| R14S5B-S-1 | **CLOSED** | Each split’s ACF cutoff uses only realized, purged training labels; retained rows and fitted targets use that split’s selected indices. Computing all window labels first does not pass held-out label values to a fit. |
| R14S5B-S-2 | **NOT CLOSED; acceptable as an open owner/S4 item** | Causal feature history can still cross a test group. The narrowed claim concerns **labels** only, and the recorded owner item preserves the unresolved feature-history binding without changing the prescribed embargo. |
| R14S5B-S-3 | **CLOSED** | The new test assigns distinct synthetic predictions by split and independently checks each path against `{g, g XOR p}`. |

**R14S5R-S-1 — BLOCKER:** [c2_lockbox.py:649](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:649) checks `block.value >= 1` but no upper bound. In a synthetic direct check, `source.n = 457` and `block.value = hexf(458.0)` passed `_check_shape`; the later identity and P-4 checks do not inspect that value. The A4 generator requires `1 <= block.value <= n` ([c2_confirmation.py:1761](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1761)), under Annex D §§D-1.3 and D-3.5. Add `value <= src["n"]` to the pre-read check and a negative test. A separate direct check confirmed that `raw = hexf(0.0)` passes.

**Verdict: FIX.** The blocker prevents closing the pre-read artifact validation finding.

Validation: 14 focused tests passed; Ruff check and format passed on the four repaired files; all 7 import contracts were kept; `git diff --check` passed. The initial pytest invocation failed because capture needed a writable temporary directory; the 14 tests passed with capture disabled. A no-write mypy attempt ended in an internal error, so type validation was not verified. I did not run fixture-dependent tests, verify every frozen hash, access confirmation or lockbox data, or use the network. The working tree is clean. This read-only review has no committed review record; the repository’s committed-record requirement remains outstanding. Exact executing model metadata was not exposed to me.
