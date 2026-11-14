# Astra re-check: slice 6b design rev 10 at 99fbac3 (verdict FIX)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1da70-eedb-7e91-91ca-23fbcb1c1496; 86,644 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV10_PROMPT_ASTRA.md` (commit `3f570f5`). Finding R14D6B10-A-1; minor wording points (called N-1 "protected-data read", N-2 runner eligibility checks inside the lock, N-3 F-4 justification qualifier by the adjudicator). Report below verbatim.

---

**Verdict: FIX — one new major issue.**

Exact runtime model ID is not exposed; I cannot certify an Astra model ID. Reviewed `99fbac3` on `confirmation-module`. Actual HEAD is `3f570f5`; its only subsequent change adds the review prompt. Findings are proposals, not authority.

**Status of R14D6B9 findings**

Line references below refer to rev 10 of `DESIGN_SLICE6B.md`.

| ID | Status | Evidence |
|---|---|---|
| R14D6B9-F-1 | APPLIED | L68 uses `qualification_object_sha256`. It exists in `SIGNED_ROWS`; `start` reads it through the same `protocol_row` parser and passes it to `verify_code` (code L2358–2363, 2494–2507, 2707–2718). |
| R14D6B9-F-2 | APPLIED | L394–401 requires matching hashes for both stored records, a closing entry and no termination, explicitly including lockbox `begin_read`. |
| R14D6B9-F-3 | APPLIED | L179–184 requires runner writes under the look lock; L236–242 fixes look-lock → append-lock ordering. |
| R14D6B9-F-4 | PARTIAL | Required minimum applied at L99–103 and L437. Optional pre-`persist` hash entry deliberately omitted. |
| R14D6B9-F-5 | APPLIED | Inputs and pre-read attempt checks at L35–53; first breach at L190; scoped test at L286–288; contract additions at L414–419. |
| R14D6B9-F-6 | APPLIED | Residuals and capture floor at L89–98. The floor introduces A-1 below. |

**R14D6B10-A-1 — MAJOR: capture floor can permanently reject a qualifying capture**

- **Location:** [DESIGN_SLICE6B.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN_SLICE6B.md:89), L89–92.
- **Evidence:** Bitcoin’s future-time check compares the header against the **validating node’s clock**, not independently established UTC: `block.Time() > NodeClock::now() + MAX_FUTURE_BLOCK_TIME`. [Bitcoin Core v30.0 source](https://github.com/bitcoin/bitcoin/blob/v30.0/src/validation.cpp#L3857-L3860). The design establishes no bound between that clock and the archive timestamp.
- **Failure scenario:** At actual UTC 12:00, an explorer’s node reads 12:05 and accepts an otherwise valid acceptance-tip block timestamped 14:04. A genuine qualifying capture occurs at 12:00:30. Bitcoin’s time predicate permits acceptance, but rev 10 refuses the capture because it precedes 12:04. O-6a SPEC L95–106 expressly permits captures before the verifier’s own observation and requires the earliest qualifying capture. Waiting does not change the frozen timestamp; substituting a later capture is not a valid repair.
- **Proposed correction:** Remove the unconditional rejection or make this discrepancy diagnostic. A hard rejection needs an explicitly accepted clock-bound assumption and corresponding rule; do not invent a tolerance. This corrects the newly added check without reopening B-1 or B-2.

**Other requested checks**

- **Store release:** No unclosed-record route to the lockbox remains under the stated Store obligation. A matching, unterminated closed cycle remains eligible subject to existing lockbox checks. This is a design contract, not implemented enforcement.
- **Locks:** No lock-order cycle found. Runner writes and evaluator appends acquire look then append; ledger append never acquires the look lock. `evaluate_look` releases its look lock before reads and persistence.
- **Inputs and §13:** Acceptance bytes are hash-bound before use; attempt identity and running state are required before protected reads and rechecked before appending. The §13 additions match the existing functions that must change.

Omitting F-4’s optional entry is **sound for the minimum requested correction**: release remains blocked and counting remains explicitly owner-controlled. The recomputation justification needs qualification: recomputation can recover an expected result given retained inputs; it cannot prove that the original execution finished or committed those exact hashes.

Minor wording: “before any read” should say “before any protected-data read.” The runner rule should explicitly include its eligibility checks inside the locked write operation.

**Files and ranges read**

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–443; complete requested diff |
| `FABLE_FINAL_DESIGN_SLICE6B_9CA4DE5.md` / `ADJUDICATION_FINAL_DESIGN_SLICE6B_9CA4DE5.md` | 1–251 / 1–31 |
| `calibration/c2_confirmation.py` | 600–654, 730–974, 1480–1518, 1610–1705, 1820–1885, 2340–2375, 2430–2550, 2570–2765, 2790–2902 |
| `calibration/c2_lockbox.py` | 1205–1300; `begin_read` references searched |
| `src/aqt/core/ledger.py` / `attempts.py` | 1–145, 275–415 / 270–405 |
| `tests/unit/test_c2_confirmation_start.py` | 203–221 |
| O-6a `SPEC.md` | 60–145 |
| Constitution / protocol / hash canonicalization | 138–158 / 60–70, 183–198 / 1–10 |

Validation: four isolated checks of the actual `protocol_row` function passed; the clock counterexample reproduced. Both `git diff --exit-code` and `git diff --cached --exit-code` returned 0. The reviewed commit range changes only review documents.

Tests, lint, types and import-boundary suites were N/A for this narrow design-only re-check. No files changed; this response remains uncommitted under your read-only instruction.