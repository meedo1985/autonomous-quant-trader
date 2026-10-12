# Fable 5.1 review: D-19 engine item 1 at 3a84b86

Recorded verbatim from the reviewer's final report (2026-10-10). Prompt:
`review/d19-engine/ITEM1_REVIEW_PROMPT.md`. Run as a read-only Claude Code
subagent requested with model `fable`; adjudication pending.

---

## Reviewer

- **Model:** Claude Fable 5.1. The runtime reports the model ID `claude-fable-5-1`. The reviewer ran as a Claude Code subagent on 2026-10-10.
- **Role:** independent adversarial reviewer. This review is not an authority.
- **Mode:** read-only.
  - No repository file was edited. No commit was made and git state was not changed.
  - There was no network access and no calibration run.
  - Scratch scripts were written only to the session scratchpad and the user temp directory. One pytest run loaded a scratch logging plugin from the scratchpad. The plugin wraps `dsr.evaluate` in memory only and changes no file.

## Commit reviewed

- **Commit:** `3a84b869d8642dbad93c6d178d6cc546be3ebf4c` on `d19-calibration-engine`. The working tree is clean apart from the untracked review prompt.
- **Diff:** against `8103052^`, so the binomial commit `8103052` is included.
- **Implementer:** Claude Opus 5.5.

## Scope

**Files reviewed:**
- `calibration/binomial.py`
- `calibration/reduce.py`
- `calibration/choices.py`
- `calibration/chunks.py` (diff)
- `calibration/rundef.py` (diff)
- `scripts/d19_run.py` (diff)
- `scripts/d19_choose.py`
- the new and changed tests

**Read for context:**
- `calibration/dsr.py` (`evaluate`, `family_block`)
- `calibration/gates.py`
- `calibration/seeds.py`
- `calibration/classifier.py`

**Checked against:**
- `review/d19-engine/ITEM1_DEVELOPMENT_AND_CHOICES.md`
- the accepted preregistration at `docs/d19-recommendation`: §1, §2, §3.2, §3.5, §5, §6, §7, §8, §9, and §13 items 2–4 and 6
- Annex A P18-3..P18-7

## Commands run and results

| # | Command | Result |
|---|---|---|
| 1 | `.venv/Scripts/python -m pytest tests/unit/test_calibration_binomial.py tests/unit/test_calibration_choices.py tests/unit/test_calibration_reduce.py tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | 35 passed in 29.28 s |
| 2 | Independent check (scratch `indep.py`, `indep2.py`). Uses `Decimal` with 60 digits and a binomial term recurrence, with no `lgamma`. Compares `upper`, `critical` and `tau` at M = 322 and 340 for N = 12k, 20k and 40k. | Every critical count agrees: error 418/417 at 20k and 883 at 40k; DSR 40; U_G 11 at 20k and 32 at 40k. Every τ and every UCB at 12k (0–3 events) agrees to a relative ≤ 2.1·10⁻⁹. Examples: τ_G(20k) is 2.0215720605·10⁻⁴ from the code and 2.0215720580·10⁻⁴ exact; τ_G(40k) is 4.512364498·10⁻⁴ from the code and 4.512364507·10⁻⁴ exact. See I1-6. |
| 3 | Scratch `probe.py`. Runs `dsr.evaluate` with no classifier on the two pilot cells of the test fixture (T = 60), 10 replications each. | pilot-k1: 10 available. pilot-k2: 9 available, 1 `BLOCK_LENGTH_CAPPED`. |
| 4 | `PYTHONPATH=<scratchpad> .venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -k independent_section_2 -q -p no:cacheprovider -p probe_plugin -s`. The plugin logs each `dsr.evaluate` outcome. | 1 passed in 14.39 s. All 8 logged evaluations (4 driver, 4 test; both rules) are `UNSUPPORTED_LAW` with `z=None`. See I1-1. |
| 5 | `.venv/Scripts/python -m ruff check calibration scripts/d19_run.py scripts/d19_choose.py tests/unit/test_calibration_*.py` | All checks passed |
| 6 | `.venv/Scripts/python -m mypy calibration scripts/d19_run.py scripts/d19_choose.py` | Success: no issues found in 14 source files |

**Not re-run:**
- The two other driver tests in `test_calibration_rundef.py`, because each takes about a minute.
- The full suite, `lint-imports` and `verify_frozen.ps1`. The implementer's record reports them; this review does not re-verify those claims.

## Verdict

**ACCEPT for pilot use of the development namespace and choices.**

- No finding is a BLOCKER for the measured re-pilot.
- I1-1, I1-2, I1-3 and I1-4 should be repaired before the **full** development run. Development records cost about 12,000 replications per cell, and fields left out now can only be recovered by recomputing them.
- No finding requires a change to the accepted preregistration. I1-8 holds an optional proposal for the owner.

## Check results by area

### 1. `calibration/binomial.py`

The definitions match §5, §6 and §13 item 3:
- `upper` is the one-sided Clopper–Pearson root of P(X ≤ x | p) = 1 − confidence.
- `critical` is the largest x with UCB at 1 − α within the bound, where α = 0.025/M.
- `tau` is the largest p with P(X ≤ c) ≥ 0.999.

Numerics:
- The bisection is monotone and stops at adjacent floats.
- The edge cases x = n, c < 0, c ≥ n, p ≤ 0 and p ≥ 1 are correct.
- Large N works: 40k reproduces the exact values.
- Accuracy is limited to about 10⁻⁹ relative by `lgamma` cancellation at N = 40k (I1-6).

### 2. `calibration/reduce.py` and the development thresholds

- **Decode.** Bit-exact, with NaN and −0.0 tested.
- **Pooling per `K`.** Correct and necessary. `K` is an exact check (`upper["K"] == lower["K"]`), so pooling across `K` would produce a threshold set no draw could match.
- **Threshold chains.** Each chain is verified and complete through `chunks.reduce`. `classifier.fit_thresholds` enforces the field set and finiteness.
- **Mixed `T`.** Pooling refuses cells of one `K` with different `T`.

### 3. `scripts/d19_run.py` (development)

These match §8:
- **Seeds:** outer seed with `ns = "d19-dev-v1"` and anchor = the preregistration hash; streams `market` and `columns`; `rep` 0-based.
- **Family seed fields:** `protocol_hash`, `family_id = "agnostic"`, `cycle_id = "D19"`, `window_id = cell_id`, `data_manifest_hash = s`, `trials`, and R-7 with round = rep.
- **`g1_ci`:** derived from the outer seed.

These match §2 and §3.5:
- **Classifier position:** after rules 1–4 (non-finite, zero variance, block length unavailable, capped) and before rules 5–6.
- **Classifier inputs:** diagnostics on `X`, with the pooled per-`K` thresholds.

Also checked:
- **Block rules.** Both rules run.
- **K = 1 reuse.** Correct: `family_block` of one length is that length under both rules, and the rule does not enter any seed.
- **Stored values.** `z_f*` is stored as binary64 hex.
- **`U_G` nominee.** `nominee()` uses the same `_sharpe_exact` and tie rule as `dsr.evaluate`.
- **What is not recorded:** `L`, the nominee and `S0` (I1-2).

### 4. `calibration/choices.py` and `scripts/d19_choose.py`

**Step 1, block rule.**
- Chosen by the worst-cell rate at 1.96. A tie goes to `largest`.

**Step 2, availability.**
- **DSR unavailability:** any non-`None` reason under the chosen rule, including `UNSUPPORTED_LAW`, `CAPPED`, `INVALID_*` and `ZERO_VARIANCE_COLUMN`.
- **`U_G` events:** any non-`None` `u_g`, including `NO_NOMINEE`.

**Cap rule.**
- Compares UCB_90(capped) with τ_DSR(20k)/4. It is applied before availability.

**Escape and demotion.**
- 0 `U_G` events → 20k; 1–2 → 40k; 3 or more → demoted; more than 9 DSR events → demoted. Tested at M = 322.

**`M` and τ.**
- τ_err is taken at each cell's own `N_i`, so an escape cell uses τ_err(40k), as §13 item 3 requires ("all its tests use `N_i` = 40,000").

**Step 3, `z_crit` search.**
- Bisection on the integer grid 0..20,000 × 0.001. Monotone, because the event count does not increase with z.
- P18-6 comparison: `float(Decimal)` is the correctly rounded nearest binary64, and is compared as `z >= value`, the same form as production.

**Final thresholds.**
- Pooled per `K` over the qualifying cells only (§3.5 item 3).

## The seven interpretations

| # | Assessment |
|---|---|
| 1. Pooled per `K` | **Correct.** It is the only coherent reading, since `K` is an exact check. It is also no less refusing than held-out, because the final cells are a subset of the candidate cells per `K`. So development refusal is at most held-out refusal in distribution, and `z_crit` is not biased low by it. |
| 2. `U_G` nominee independent of DSR availability | **Correct.** §2 step 5 says "whatever the outcomes above", which includes the step-3 classifier refusal. It is also valid for the union bound: U_proc^R = ¬A_f ∪ (A_f ∩ U_G) ⊆ ¬A_f ∪ U_G(argmax S), so measuring `U_G` marginally is conservative. `NO_NOMINEE` double counts with DSR availability, which is conservative. The held-out run must use the same definition (I1-5). |
| 3. Both block rules in every replication | **Correct** as required by §5 step 1. The cost disclosure is accurate: the §13 estimate uses one 4.5 s evaluation for development and held-out alike (`ADJUDICATION_C09337F.md` BF1-4). See I1-8. |
| 4. `M` = 3 per family-agnostic cell | **Correct for Q1–Q4.** It becomes wrong once Q5 or QJ enter the manifest (I1-4). |
| 5. `z_crit` grid [0, 20] | **Defensible.** A qualifying negative value is clamped up to 0, which is conservative and practically unreachable. "None" is §5 step 6. |
| 6. Cap rule at τ_DSR(20k)/4 | **Correct** per §3.2 and §13 item 3. Using τ_DSR(20k) rather than τ_DSR(40k) is the stricter choice. One capped development replication demotes a cell, as disclosed. A further consequence is in I1-7. |
| 7. Start gate in the selection script | **Correct and necessary.** `lgamma`, `exp` and the binary64 comparison depend on libm. |

## Findings

### I1-1 — NON-BLOCKING — the development tests never reach `z_f*`, the bootstrap, or K = 1 reuse

**Location.** `tests/unit/test_calibration_rundef.py:971` and `:1010`.

**What the tests claim.** `test_development_records_equal_an_independent_section_2_computation` claims to check "both rules" and the stored `z_f*`.

**What actually happens.** The thresholds come from 3 threshold draws, which give max/min thresholds. Command 4 shows both replications of `pilot-k2` are refused as `UNSUPPORTED_LAW` under both rules, so the test only compares `None == None`. As a result, none of these is exercised:
- the accepted-classifier path through `dsr.evaluate`;
- rules 5–6;
- `S0`;
- `_hex(z)`;
- a difference between the two rules.

The K = 1 cell is not checked independently at all; only K = 2 is replicated. The end-to-end test checks key sets only, and its `demoted_cap` assertion holds for any n = 2 (see I1-7).

**Failure scenario.** Suppose a regression stored `z` under the wrong rule, or passed `accept` inverted, at K ≥ 2. A wrongly accepted replication would then go through the bootstrap, and the stored record would differ from the independent computation. Because no fixture replication is accepted, the test would not catch it.

**Proposed repair.**
- In the independent test, give the dev worker very wide finite bounds. For example, take the pooled bounds and widen each tail by a large finite margin. Assert that at least one replication has a non-`None` `z` under each rule, and that the two rules differ in `block`.
- Add the K = 1 cell and assert that its `median` record equals an independent `dsr.evaluate(..., "median")`.
- Assert `accept` both ways: one refused replication and one accepted.

### I1-2 — NON-BLOCKING — the development record omits values §2 step 6 and §9 need

**Location.** `scripts/d19_run.py:112-121`.

**What is missing.** §2 step 6 says "Record the events, cause codes, `L`, `L/T` and the diagnostics". The record holds `reason`, `z` and `length_ratio` (max L_j/T), but not:
- the family block `L` (`result.block`);
- `S0`;
- the nominee index.

§9's reported rates ("Cap and failure rates per column, by `K`"; `P_0(E_f | A_f)`) are untouched by §13 item 5. The per-column cap and failure rates cannot be computed from these records, because `dsr.evaluate` exposes only one capped flag and the max ratio.

**Failure scenario.** After the full development run (about 104 cells × 12,000 replications), there are two problems:
- §9's per-column rates, and an audit that the `U_G` nominee equals the DSR nominee, would need the development run recomputed.
- §2 step 6's `L` is not in the reduced results the qualification object carries.

**Proposed repair.**
- Add `"block": _hex(result.block)`, `"s0": _hex(result.s0)` and `"nominee": result.nominee` per rule.
- Add the `U_G` nominee `j` once per replication. Choose can then assert that the DSR nominee equals `j` whenever DSR is available.
- For §9 per-column rates, have `dsr.evaluate` (or `fast.column_lengths`) return the per-column lengths and cap flags, and store them, or record the decision that §9's per-column rates come from another source. The fields are cheap; the decision belongs to the implementer, and to the owner if §9 is to be narrowed.

### I1-3 — NON-BLOCKING — the choices report is not bound to the development thresholds or chain heads

**Location.**
- `scripts/d19_run.py:126-145` and `:203-213`: the bounds are computed in the parent and passed to workers, and appear in no record.
- `scripts/d19_choose.py:80-103`: the report records only `definition_sha256`.

**What is missing.**
- Development chunks do not record the thresholds they were classified against.
- `d19_choose` does not re-check that each stored reason agrees with `classifier.within(diagnostics, pooled bounds)`.
- §13 item 6 says the qualification object "adds the final chain head of every threshold and development chain, and their reduced results". The report does not record the chain heads it read.

**Failure scenario.** A driver bug, or a code path that later passes the wrong `K`'s bounds or stale bounds, would produce development records whose `UNSUPPORTED_LAW` events do not follow from the threshold chains. `choose` would accept them silently. The report also cannot later be tied to the exact chains it was computed from.

**Proposed repair.**
- In `choose`, recompute the pooled development thresholds from the verified threshold chains. For every development record whose reason is `None` or `UNSUPPORTED_LAW`, assert that `UNSUPPORTED_LAW` holds if and only if `within(decode(diagnostics), ...)` is false. Fail on any mismatch.
- Write each chain's final head, both namespaces, and a SHA-256 of the pooled development thresholds into the report.

### I1-4 — NON-BLOCKING — `M` is hard-coded for family-agnostic cells, not read from the manifest

**Location.** `scripts/d19_choose.py:36` and `:93`; `calibration/choices.py:72-74`.

**The issue.** §5 says "`M_max` is the manifest's test count". §4 says "the manifest of cells and enumerated tests". The code derives M = 3 × the number of cells, which holds only while every cell is family-agnostic. Q5 has per-family tests and QJ adds family and cycle tests.

**Failure scenario.** When Q5 or QJ generators are added (item 2), `choose` would understate M. α would then be too large, τ too large, `z_crit` too low, and availability too lenient, with no error raised.

**Proposed repair.** Make `choose` refuse any cell that is not family-agnostic until per-family test counting exists. Better, take M from the frozen manifest's enumerated-test list and assert it equals the derived count.

### I1-5 — NON-BLOCKING — the family-seed `protocol_hash` is passed the anchor

**Location.** `scripts/d19_run.py:105`.

**The issue.** The call is `family_seed(seed, cell.cell_id, "agnostic", cell.k, anchor, rep)`, whose fifth parameter is `prereg`. §8 sets `protocol_hash` to the preregistration hash in every namespace, while `anchor` equals the preregistration hash only in the threshold and development runs.

**Failure scenario.** The held-out driver (not built yet) reuses this line. In held-out the anchor is `SHA256(cj({beacon_randomness, qobj, round}))`, so `protocol_hash` would be wrong. Held-out seeds would then not reproduce from the §8 specification, and under Constitution §27 a result that does not reproduce is void.

**Proposed repair.** Pass `defn["prereg_sha256"]` explicitly as the fifth argument, separate from `anchor`. Also record in the held-out design that the `U_G` nominee rule of interpretation 2 is part of the frozen definition.

### I1-6 — NON-BLOCKING — the targets carry about 10⁻⁹ relative error with no recorded margin

**Location.** `calibration/binomial.py:22-41` and `:44-55`.

**The issue.** The terms are `exp(lgamma(n+1) − lgamma(i+1) − lgamma(n−i+1) + …)`. At N = 40k, `lgamma(40001)` is about 3.8·10⁵, so cancellation leaves about 10⁻¹⁰ absolute error in each log term. Command 2 measured up to 2.1·10⁻⁹ relative error in τ and the UCBs, not always in the conservative direction: the code's τ_G(20k) is larger than the exact value. `_solve` also returns the lower bisection end, so the UCB can be one ulp below the root.

**Effect.** No current decision flips. The nearest pair checked is UCB(2 of 12k) = 4.4347·10⁻⁴ against τ_G(40k) = 4.5124·10⁻⁴, a 1.7% gap. But when an error-test UCB at some count lies within about 10⁻⁹ of τ_err, a decision would depend on rounding the preregistration does not specify. The decision stays reproducible on the pinned runtime (interpretation 7).

**Proposed repair.**
- Have `choose` report, for every comparison it makes, the smallest relative margin |UCB − τ|/τ. Fail closed, or flag to the owner, if it is below 10⁻⁶.
- Alternatively, compute the CDF with a term ratio recurrence in log space from the mode outward, which is accurate to a few ulps.
- Pin the printed τ values in the qualification object as the frozen script's output, as §13 item 3 already says.

### I1-7 — QUESTION — a pilot can never exercise `z_crit` or the final thresholds

**Location.** `calibration/choices.py:86-89`; `calibration/rundef.py:245` (a pilot must stay below 12,000).

**The issue.** UCB_90(0 of n) ≈ 2.303/n. This is within τ_DSR(20k)/4 (≈ 3.0·10⁻⁴ at M ≈ 322) only when n ≥ about 7,700, and within the larger pilot-M value only somewhat earlier. In any practical pilot, every cell is `demoted_cap` with zero capped replications. The pilot report therefore always has `z_crit: null` and empty `final_thresholds`; the end-to-end test asserts exactly this. Also, at pilot size M = 3 × (pilot cells), so even with larger n the pilot's τ would not be the qualification τ.

**Question for the implementer.** Is it accepted that the re-pilot measures cost and rates only, while the choice steps 2–3 are validated only by the unit tests on synthetic `Rep`s?

**Proposed repair (no change to the preregistration).**
- State this in the pilot report.
- Optionally, add a `choose` diagnostic that prints, per cell, the counts behind the decisions (dsr, `U_G`, capped). The owner can then read rates from the pilot without implying a choice.

### I1-8 — QUESTION / owner proposal — development cost of the second block rule

**Location.** `scripts/d19_run.py:107-117`.

**The issue.** At K ≥ 2 the Annex B bootstrap (B = 2000) runs twice per development replication. The §13 estimate assumes one 4.5 s evaluation per replication in both development and held-out. If the bootstrap is most of the 4.5 s, development at K ≥ 2 costs up to about 1.6–1.9× its estimate. That is roughly +700 to +1,100 server-core-hours on about 5,400–7,300, about +10–15% or 2–3 weeks. This is an estimate to be measured; it is not a defect, since §5 step 1 requires `P̂_0(E_f)` under both rules in every candidate cell.

**Question.** The re-pilot should time the two evaluations separately, and the go-ahead estimate should include the second one.

**Owner proposal (changes the accepted preregistration; owner decision only).** If the cost is material, §5 step 1 could choose the rule on a prefix of the development replications, for example the first 2,000 per cell. After that, only the chosen rule would be computed. The current code follows the accepted text and needs no change unless the owner decides this.

## Findings deliberately not raised

- **The equity ≤ 0 check (§3.1) is applied only to the nominee, through G-2.** This is pre-existing code outside item 1, and the event is practically impossible at about 2.3% daily volatility.
- **`assert isinstance(record, dict)` in `d19_choose.py:61` disappears under `-O`.** This is trivial, because chain verification already guarantees the record shape.
