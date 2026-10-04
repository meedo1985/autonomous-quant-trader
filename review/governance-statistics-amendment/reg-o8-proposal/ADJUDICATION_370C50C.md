# Adjudication of FR1 and SR1 (rev 1 `370c50c`) → revision 2

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter. This adjudication is
not an authority.
**Records:**
- `FABLE_REVIEW_370C50C.md` (`36e24ab`): SOUND WITH FIXES.
- `SOL_REVIEW_370C50C.md` (`8a68d02`): UNSOUND.

**The reviewers agree on the substance.** Rev 1's sizing argument was wrong:
E-DIFF, and therefore the DSR and PBO, depend on position size. Its REG-2
ban was presented as stronger than it is. O-8 is correct against the code.
Every finding is accepted. None is left unrepaired.

| Finding | Disposition | Rev 2 location |
|---|---|---|
| FR1-1, SR1-2 | Accepted. "Sharpe-based conclusions carry over" is withdrawn. A statistic-by-statistic analysis replaces it: E-IMPROV is invariant only approximately; E-DIFF/DSR/PBO depend strongly on size; drawdown is easier at small size. Added: a small fixed size is very unlikely to pass the DSR. | §2 |
| SR1-3 | Accepted. The vol-target test is described as a different strategy. Rev 1's drift, cost and clip arguments are included. REG-1 (a) now says plainly that the 10% rule is not tested. | §2, §6 Q2 |
| FR1-2, SR1-1 | Accepted. REG-2 (a) is restated as a declared-input ban (`s_inputs` plus run-time restriction, `<<OPEN D-20>>`) that stops only accidental or honest use. Near-proxy and recompute routes are disclosed as keeping most or nearly all of the artifact; this is the residual already accepted under D-14 Q3 (a). A functional ban, option (c), is shown and not recommended. Sol's "otherwise keep blocked" is not adopted as the recommendation: no input rule can close the route, and the residual is already owner-accepted. The owner may still choose "keep blocked". | §1, §6 Q1 |
| FR1-3 | Accepted. The misalignment works in both directions. | §1 |
| FR1-4 | Accepted, as the `s_inputs` field and run-time restriction. | §1 (a), §5 |
| FR1-5 | Accepted. The missing entry trigger, the hourly stop and the risk per stopped trade are stated. | §2 |
| FR1-6, SR1-4 | Accepted. The drawdown wording is now "materially easier, potentially weak", with no fixed ratio, and covers any lower-exposure candidate. | §2 |
| FR1-7 | Accepted. Citation fixed. The band is read through `reaches_rebalance_band`, binding `<<OPEN D-20>>`. Folding this into Annex C C-6 is deferred to the next Annex C revision; it is recorded here so it is not lost. | §3 |
| SR1-5 | No change needed. It confirms O-8. | §3 |
| SR1-6, FR1-10 | Accepted. Questions 1–3 are rewritten. | §6 |
| FR1-8, FR1-9, SR1-7 | Accepted. O-6a now lists the requirements, says a hash reveals nothing, gives the third-party alternative and names a candidate channel (Sigstore Rekor, unverified; it must be checked against official documentation before asking). O-9 uses the exact invalidation event and both consequences. | §4, §6 Q4–Q5 |

**Follow-up for Annex C**, applied when the draft is next revised:
- C-6: the band is read through `reaches_rebalance_band` (FR1-7).
- C-10 (1): the `s_inputs` field, if REG-2 (a) is chosen.

**Not re-reviewed.** Revision 2 changes the substance of REG-1 and REG-2, so a
focused two-model check is run before the owner is asked.
