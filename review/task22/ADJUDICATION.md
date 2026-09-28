# Task 22 adjudication of Astra review 1

Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementer. Date:
2026-09-27. Review: `REVIEW.md` (GPT-6 Astra, verdict FIX, reviewed commit
`34043c7`). Each finding was traced against the code and turned into a
regression test that fails without the repair (mutation results below).

| ID | Verdict | Repair |
| --- | --- | --- |
| R-1 BLOCKER | **Accepted, repaired.** Confirmed by trace: the zero-quantity branch released without redeeming, so a replay of an already-redeemed authorization could release a frozen reservation. | `_begin` now redeems before anything else. Only a run that redeemed the authorization itself (and then found a zero quantity), or found it never-redeemed and `STATE_CHANGED`, may release. Test: `test_a_replay_cannot_release_a_frozen_reservation`. |
| R-2 BLOCKER | **Accepted, repaired.** The strongest scenario (a fill hidden behind two lagging NOT_FOUND answers, then expiry) released the reservation over an undiscovered fill. | A run that sent anything to the venue never releases. `ExecutionResult.reconciliation_required` is true, and only reconciliation (Task 23) may release. Tests: `test_a_fill_hidden_behind_not_found_is_never_released`, plus the updated fill, partial-fill, rejection and expiry tests. |
| R-3 BLOCKER | **Accepted, repaired.** | `_place` reads the clock immediately before every placement, including the first, and fires `AUTHORIZATION_EXPIRED` from `SUBMITTING` if the authorization has expired. Test: `test_expiry_is_checked_at_the_submission_boundary`. |
| R-4 BLOCKER | **Accepted, repaired.** Confirmed: backward jumps outside the sleep were accepted, and the retry loop was unbounded. | Every clock read in a run must be at or after the previous one, or the run FREEZEs (`CLOCK_FAULT` from every live state). Separately, placements are capped at `lifetime // delay + 1` (`ATTEMPT_LIMIT` → FREEZE). The cap cannot be reached while the clock is honest; it is a second barrier. Test: `test_a_clock_that_goes_backwards_freezes_instead_of_retrying`. The mutation that used to hang is now caught. |
| R-5 BLOCKER | **Partly repaired; enforcement deferred to the owner.** A market order cannot carry a price bound, so the executor cannot prevent a fill beyond `max_slippage_bps`. | Containment: a fill beyond the bound now ends in FREEZE (`SLIPPAGE_BREACH`), and the reservation is kept. Tests: `test_a_fill_beyond_the_slippage_bound_freezes`, `test_a_gap_beyond_the_slippage_bound_freezes`. **Not repaired:** enforcing the bound before the fill needs a different order type (for example a price-capped immediate-or-cancel limit order in a live adapter). That changes the execution contract and possibly the reading of Cycle 1's taker-only rule, so it is an owner/governance decision, not an AI edit. Recorded as open question T22-Q3. |
| R-6 NON-BLOCKING | **Accepted, documented.** | The `orders.py` docstring now says the one-order guarantee depends on the venue never accepting a second order under an id it has already filled. The simulator guarantees that; Binance does not (it allows id reuse after a fill). A real adapter needs its own guard. The integration tests count actual simulator fills (`_fills`), not only request tuples. |

Comments on the disclosed deviations:

- T22-02: accepted. Any future adapter must classify errors conservatively,
  with unknown as the default. The report carries this forward.
- T22-04, T22-05: superseded by the R-2 and R-4 repairs.
- T22-06, T22-Q2: breach handling is now FREEZE (the safer option). T22-Q2
  becomes a question of whether to relax it.
- T22-Q1: accepted that 2 NOT_FOUND answers do not prove absence against an
  arbitrarily lagging venue. After R-2 that no longer releases anything: it
  only allows a resend under the same id, which the simulator deduplicates.
  The values stay unadopted.

## Mutation checks after repair

Each mutation was applied alone and run against the two executor test files.

| Mutation | Result |
| --- | --- |
| R-1: release a REFUSED run without owning it | caught |
| R-2: release every non-FREEZE end | caught |
| R-3: remove the submission-boundary expiry check | caught |
| R-4: remove the forward-only clock check | caught |
| R-5: remove the slippage FREEZE | caught |
| UNKNOWN query leads to resend (hung before) | caught |
| Skip the protocol delay | caught |
| One NOT_FOUND counts as absence | caught |
| Remove the order-mismatch check | caught |
| `DUPLICATE_CLIENT_ORDER_ID` as a rejection | caught |
| New `clientOrderId` per attempt | caught |
| Quantity rounded up one step | caught |
| Remove only the pre-resend expiry check | survives: the R-3 boundary check covers it by design |

## Validation after repair

| Command | Result |
| --- | --- |
| `pytest -q` | 1467 passed, 4 skipped in 83.61s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 90 files already formatted |
| `mypy src scripts` | Success: no issues found in 46 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |
| `git diff --check` | clean |

Frozen files: SHA-256 identical to the pre-task snapshot.

The repairs are not yet re-reviewed. A second Astra review follows.
