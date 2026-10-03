# Addendum to the owner decision on D-14/D-15/N-3/N-4: re-asked items after the agent check

**Date:** 2026-10-03
**Why this exists:** after answering, the owner asked "let the agent check the
answers". Two different-model checks ran:
- `FABLE_DECISION_CHECK_E2A1A74.md` (FC7, INCONSISTENT, `f279c5a`)
- `SOL_DECISION_CHECK_E2A1A74.md` (SC7, INCONSISTENT, `6d0ba1b`)

Both found that some questions left out facts, and that the record (`e2a1a74`)
listed as "accepted" some consequences that were never shown. The owner was
then asked again. Claude Opus 5.5 (`claude-opus-5-5`) asked and recorded the
questions. **Where this addendum and `OWNER_DECISION_D14_D15.md` differ, this
addendum governs.** The original record is kept unchanged as history.

## Exchange (verbatim)

1. **Q13 / N-3** (FC7-1, FC7-8). The first attempt returned no answer for
   this question, so it was asked again.
   - Question: "Q13 (new row N-3, the 2x cost check for ETH). On 2026-09-15
     you decided: 'ETH remains at 1x. The proposed ETH 2x tightening is
     rejected.' My earlier Q13 didn't tell you this, and its recommended
     answer would reverse that decision. Answering also adds N-3 as a
     decision row. Nothing is activated."
   - Options: "Keep 09-15: ETH at 1x (Recommended)" / "Set 09-15 aside".
   - Answer: **"Keep 09-15: ETH at 1x (Recommended)"**.
2. **Q15/Q17** (FC7-2, SC7-3).
   - Question: "Q15/Q17, re-asked (delay checks for ETH). Under the two delay
     checks (fills one hour late; inputs one hour old), should ETH be
     stressed too? Your 09-15 decision was about cost only, so it doesn't
     strictly decide this. But it treated ETH as a light sanity check that
     isn't tightened under stress."
   - Options: "ETH at baseline (Recommended)" / "Stress ETH too".
   - Answer: **"ETH at baseline (Recommended)"**.
3. **Q2b** (FC7-3, SC7-1).
   - Question: "Q2b, re-asked with a correction. I told you your rule (10%,
     −0.5% stop, +10% take-profit) would 'skip' the random-timing check
     under (A). That was wrong. A fixed 10% CAN be written in the required
     format, and then the check WOULD run on it, but it would test something
     unrelated to your stop and take-profit. Whether a fixed-size rule can be
     registered at all is still undecided. Under (B) your rule is blocked
     either way. The choice itself is unchanged: should stop/take-profit
     timing go untested by this check, as disclosed (A), or block such
     strategies until a separate test exists (B)?"
   - Options: "(A) Accept and disclose (Recommended)" / "(B) Fail-closed".
   - Answer: **"(A) Accept and disclose (Recommended)"**.
4. **Q11** (SC7-2).
   - Question: "Q11, re-asked (delay check: what 'inputs one hour old'
     means). Under the recommended meaning, each input takes its value as of
     one clock hour earlier. For hourly inputs that's exactly one hour. For
     an input updated once a day at 00:00, it depends on the hour: a decision
     at 12:00 sees no extra delay, but a decision at 00:00 sees the previous
     day's value. The alternative delays every input by one of its own
     updates (one hour for hourly inputs, one full day for daily ones)."
   - Options: "One clock hour (Recommended)" / "One update of each input".
   - Answer: **"One clock hour (Recommended)"**.
5. **Consequences that were left out earlier** (SC7-3, SC7-5, FC7-5).
   - Question: "Your 'accept all' earlier didn't show these trade-offs. Do you
     still accept them?
     (1) Each strategy declares whether its signal changes; a mismatch makes
     the check 'unavailable'.
     (2) A signal that only reacts to volatility can pass the random-timing
     check with no price-direction skill.
     (3) The 30-day minimum slide is a guess with no data behind it, and it
     reduces the check's power for slow signals.
     (4) How the random slides are drawn still depends on the open D-20
     decision.
     (5) The delay checks only require the strategy to stay positive, so a
     large deterioration can still pass.
     (6) Measuring the 24-hour clock from decision time changes four rulebook
     lines and allows adding risk 23 hours after an actual fill; in effect
     the 24-hour rule never bites for daily decisions.
     Nothing is activated."
   - Options: "Confirm all six (Recommended)" / "Revisit some".
   - Answer: **"Confirm all six (Recommended)"**.

## Effect (supersedes the corresponding parts of `OWNER_DECISION_D14_D15.md`)

- **N-3, decided:**
  - The BTC benchmark is at 2x in G-5.
  - **ETH: the whole ETH sanity rule stays at 1x under G-5**, which keeps
    the 2026-09-15 decision, item 3. This is Q13(b).
  - The original record's statement that the ETH point estimate runs at 2x
    is withdrawn.
  - N-3 is now explicitly added as a row.
- **Q15/Q17, decided as (b):**
  - ETH runs entirely at baseline in G-7 and G-6. Only BTC legs are stressed.
  - The BTC benchmark is delayed under G-7 (Q14(i)) and not lagged under G-6
    (Q16(ii)), unchanged from the original record.
- **Q2b(A), reaffirmed** with the corrected description of the owner's rule:
  - Whether a fixed-size rule can be registered is **undecided**.
  - Whether `s` may depend on `σ̂` is an **open question**, to be settled
    with registration (FC7-3).
- **Q11, reaffirmed**, with its time-of-day dependence explicitly accepted.
- **Consequences (1)–(6), explicitly accepted.**
- **Consequences recorded in rev 7 but never shown to the owner, and not
  re-asked here, are relabelled "recorded, not presented":**
  - that Q19's event contract also governs baseline runs;
  - the D-19 workload;
  - that Q2(b) would close the vol family. This one did not apply, since Q2(a)
    was chosen.
- **Wording corrections (FC7-4, FC7-6):**
  - The "5% limit holds either way" wording means: G-11 `N/A` does not change
    the DSR error event, and that bound is still conditional on the D-19
    calibration. Under B-5, the 5% allowance applies to the first eligible
    cycle only.
  - Q10(b) changes only G-7. Under (a), the 24 h clause would bind only under
    execution delay.
- **Provenance correction (FC7-7, SC7-6):**
  - Six revisions (rev 1 to rev 6) were reviewed by both families.
  - Revision 7 was not reviewed before the first answers.
  - It was then checked by FC7 and SC7 together with the answers. Neither
    found a new technical defect in rev 7, apart from FC7-9, which is
    cosmetic: the Q9 table should read "type-7 (overridden: FAIL)".

## Not changed

All the other answers in `OWNER_DECISION_D14_D15.md` stand. Nothing is
activated. No frozen file or matrix is edited. Promotion stays blocked.
