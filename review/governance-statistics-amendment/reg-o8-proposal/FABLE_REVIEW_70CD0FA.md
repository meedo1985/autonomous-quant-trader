# Fable narrow check of the REG-1/REG-2/O-8 proposal rev 4 at `70cd0fa` — NOT READY

Date: 2026-10-04. This is the Anthropic-family narrow check for R19-2. It used
prompt `REVIEW_PROMPT_R2.md` with prefix FR4, plus a narrow-scope preamble. It
ran in parallel with Sol SR4 and did not see it.

The model ID is self-reported, because Fable subagent transcripts come back
empty. The hand-back below was recorded verbatim by Claude Opus 5.5
(`claude-opus-5-5`). No finding is omitted.

---

**Model:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family (self-reported)
**Commit checked:** `70cd0fa` (`review/governance-statistics-amendment/reg-o8-proposal/PROPOSAL.md` rev 4; the commit touches only PROPOSAL.md and ADJUDICATION_370C50C.md)
**Prompt:** `REVIEW_PROMPT_R2.md`, PREFIX = FR4, narrow check
**Verdict: NOT READY.** There is one MAJOR finding (FR4-1), which can be fixed by editing text with no new analysis.

**Read:** PROPOSAL rev 4, ADJUDICATION_370C50C.md (with both addenda), FABLE_REVIEW_CC8C89C.md and SOL_REVIEW_62977BA.md.
**Not done:** no network, no confirmation or lockbox data, no edits.

**FR2 resolution:**
- FR2-1 is resolved by deferral. O-6a is out of this batch, there is no O-6a owner question, and §4 states that signing stays blocked until it is resolved.
- FR2-2 is resolved by the combined Q1. (A) and (B) now state the exact or near-10% route. FR4-1 covers the remaining gap in (C).
- FR2-3 is resolved in §1 (a).
- FR2-4 is resolved, and further corrected by SR3-3.
- FR2-5 is resolved in §1, and Q1 now states the fail direction.
- FR2-6 is resolved in §1 and Q1 (A). The §1 (a) table still says "recompute σ̂ from prices" without the qualifier. This is harmless.
- FR2-7 is resolved in Q3, and FR2-8 in Q2.
- FR2-9 is resolved by the rev 4 follow-up repair (SR3-4).

**Checked and confirmed:**
- I recomputed SR3's example as cited in §2: benchmark exposure 0.6, with 625 days of +1% and 623 days of −1%. C − B is −0.005 on up days and +0.006 on down days. This gives E-DIFF ≈ +1.70 annualized and a benchmark Sharpe of about +0.031. Both figures match.
- The O-8 and O-9 text is unchanged in substance and is still correct.

| ID | Severity | Location | Evidence | Proposed disposition |
|---|---|---|---|---|
| FR4-1 | MAJOR | §6 Q1 (C); ADJUDICATION follow-up "Under (C)" | (A) and (B) each fix both REG-1 and REG-2. (C) fixes only REG-1: it adds a `fixed_size` class whose `e` may not read σ̂. It does not say whether vol-target trials then keep the `s_inputs` ban, as in (A), or allow σ̂, as in (B). The Annex C follow-up for (C) lists only the new class clauses, which suggests no ban, but this is never stated. An owner who answers (C) therefore leaves REG-2 undecided. Under the no-ban reading, the near-10% route through the vol-target class also stays open. | State what (C) means for REG-2: either "(C) includes (A)'s ban for vol-target trials", or split (C) into (C-A) and (C-B). Update the follow-up to match. |
| FR4-2 | MINOR | §4 "Default relay allows up to 83 bytes … verified" | The cited source is developer.bitcoin.org's devguide, an old guide that is no longer maintained. Reviewer recollection, unverified: Bitcoin Core 30 (October 2025) raised the default `datacarriersize` far above 83 bytes. If so, "verified" overstates the claim, and "the §2.0 message is too long" may be wrong under current defaults. The current owner questions are unaffected, because O-6a is deferred. | Change "verified" to "per an older developer guide; current Bitcoin Core relay defaults to be checked when O-6a is specified". Keep "a short prefix plus the 32-byte hash" as the safe design. |
| FR4-3 | MINOR | §6 Q1 (C) | §2 (b) says the drawdown checks become lenient at small `c`. Q1 (C) omits this, so the owner may read a drawdown pass as meaningful. | Add: "At 10% the drawdown checks also become easy to pass." |
| FR4-4 | MINOR | §6 Q1 (A) | Two (A) consequences from §1 and §5 are not in the question: (i) honest variance-timing signals with default sizing lose `ewma_vol_168h`; (ii) the ban needs §16 code (`<<OPEN D-20>>`). | Add one line covering both. |
| FR4-5 | MINOR | §6 Q1 (B) | "Judges it unreliably" gives no direction. §1 says a plain fixed-size rule written this way tends to **fail** the random-timing check (FR1 toy: 53 of 500 draws, where 476 are needed). That is the case the owner most needs to know. | Add: "A plain version tends to fail that check for reasons unrelated to its timing." |

**Summary for the owner (three lines):**
1. The earlier problems are fixed: the sizing analysis is honest, no pass probability is claimed, and the public-post channel has been taken out of this batch.
2. One gap remains. Option (C) does not say whether the volatility-number ban applies to the normal strategies, so answering (C) would leave that question undecided.
3. After a one-line fix there and three small additions to the option text, questions 1–3 should be ready to put to you.
