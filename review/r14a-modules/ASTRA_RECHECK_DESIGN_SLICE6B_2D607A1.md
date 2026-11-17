# Astra re-check: slice 6b design rev 8 at 2d607a1 (verdict ACCEPT WITH NOTES)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1da44-c62b-7862-8337-74b1001e7d7c; 50,916 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV8_PROMPT_ASTRA.md` (commit `64d50cd`). No findings with IDs; three minor wording points (called N-1 capture time vs `w0`/`T`, N-2 `u_proc_results` in the record field list, N-3 `body` ASCII bytes by the adjudicator). Report below verbatim.

---

**Verdict: ACCEPT WITH NOTES.** No new blocking or major findings within the requested scope. Findings are proposals; owner decisions remain closed.

**Model:** the exact executing model ID is not exposed to me; I cannot verify the “Astra” designation.

Reviewed Git objects at **`2d607a1`**. Checkout HEAD is `64d50cd`; the working tree is clean.

| Previous finding | Status | Rev 8 evidence |
|---|---|---|
| R14D6B7-A-1 | **APPLIED** | Design 34–37, 216–231, 359–363: both exact records must be durably persisted before closing; persistence failure or a crash before closing yields no pick. |
| R14D6B7-A-2 | **APPLIED** | Design 246–255: aggregate every identity-valid pre-look result before collapsing states, including duplicates, superseded attempts and post-outcome results; retain result identities and reasons. |
| R14D6B7-A-3 | **APPLIED** | Design 237–257, 396: C-3 applies only to breached families. Unbreached precedence matches rev 6, lines 198–205. |

**Adversarial checks**

- **Persistence:** partial persistence followed by an exception leaves no closing entry. Successful persistence followed by a crash before closing explicitly produces `LOOK_WITHOUT_RECORD`, despite stored records. The existing look entry prevents another look (201–202). A torn closing append is rejected by ledger verification (`ledger.py:255–308`); a complete closing entry follows durable record storage. Missing records behind a closing entry are explicitly a store failure. No new pick, retry or hidden-success path found under the stated durability contract.
- **Identity and attribution:** “identity-valid” is sufficiently defined by design 135–139 and 166–176 together: a preceding start in this cycle after the anchor, declared trial mapping, and validation of family, cycle, configuration, seeds, manifest, code identities and window. A mismatched result causes `CycleError`; an order breach does not waive those checks. Aggregating before collapse therefore preserves failures without permitting cross-family or cross-cycle attribution.
- **C-3:** an unbreached family containing a running trial and `DAYS_INCOMPLETE` remains U_ops. A breached family containing any validated pre-look U_proc result becomes U_proc.

**New findings R14D6B8-A-n:** none at blocking or major severity.

**Minor wording points**

- **Design 85:** capture time does **not** fix `w0` or window length in `check_eligibility`. Code 675–711 derives them from signed `c2_start`/`c2_end`, with `w0 = c2_start`. Correct that parenthetical; retain distinct names for capture time and window length.
- **Design 338–340:** add `u_proc_results` to the evaluation-record field listing, consistent with the explicit requirements at 250–253 and 380–381.
- Canonical manifest versus raw-file hashing, the 480-byte header digest, and explicit `unstarted` state are corrected. For JSON `body`, specify hashing its ASCII-encoded string bytes rather than saying the JSON value is “decoded.”

**Files and ranges read**

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–400; requested diff; rev 6: 185–228 |
| `…/ASTRA_RECHECK_DESIGN_SLICE6B_E2DDCB4.md` | 1–71 |
| `…/ADJUDICATION_RECHECK_DESIGN_SLICE6B_E2DDCB4.md` | 1–32 |
| `calibration/c2_confirmation.py` | 600–716, 805–940, 2560–2616 |
| `src/aqt/core/ledger.py` | 90–415 |
| Supporting governance | `AGENTS.md` 1–48; Constitution 99–108, 140–157; protocol 55–76; hash canonicalization 1–10 |

**Validation:** `git diff --check e2ddcb4 2d607a1 -- review/r14a-modules/DESIGN_SLICE6B.md` passed. Git comparison confirmed the inspected code and frozen paths/sidecars unchanged across the revision.

Tests, lint, types and import-boundary suites were N/A to this document-only re-check; runtime persistence was not tested. No files were modified. This report remains uncommitted and therefore does not yet satisfy the repository’s review-record requirement.