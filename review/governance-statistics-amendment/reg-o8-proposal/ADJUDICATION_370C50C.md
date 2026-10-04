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
- C-10 (1): record the combined REG decision (A, B or C) with its
  consequences.
  - Under (A): add the `s_inputs` field and the run-time input restriction,
    and the banned set (the sizing estimator's output, plus any frozen
    feature identical to it, currently `ewma_vol_168h` for trials sized by
    `EWMA_168h`), with the mapping bound under `<<OPEN D-20>>`.
  - Under (C): add the new `fixed_size` class clauses.
  - (SR3-4: repairs the FR2-9 follow-up, which the rev 3 addendum claimed but
    did not write.)

**Not re-reviewed.** Revision 2 changes the substance of REG-1 and REG-2, so a
focused two-model check is run before the owner is asked.

## Addendum: FR2 focused check of rev 2 (`cc8c89c`) → revision 3

Fable FR2 (`4f230cb`) returned NOT READY. Sol SR2 was stopped by the system for
low memory before it produced any output. Rev 2 therefore has a check from
one model family only, and SR2 must be re-run on rev 3 before the owner is
asked.

| Finding | Disposition |
|---|---|
| FR2-1 | Accepted, and verified against official sources on 2026-10-04: Rekor v2 removed the search index, and v1 will eventually be frozen. Rekor is **rejected** as a channel. The new candidate is a Bitcoin OP_RETURN from one dedicated address. That is general knowledge, marked unverified, and must be verified before asking. The trusted-third-party alternative is kept. |
| FR2-2 | Accepted. REG-1 and REG-2 are now one combined question with three options, (A), (B) and (C), each stating its consequences. |
| FR2-3 | Accepted. `ewma_vol_168h` is identified as σ̂ itself for default-sized trials, and is banned under (A). The loss for honest variance-timing signals is disclosed. |
| FR2-4 | Accepted. Option (C) and the question now say that the DSR at small c mostly measures the benchmark's window, so neither a pass nor a fail is informative. |
| FR2-5 | Accepted. "Closely related to, and wider than" replaces "the one already accepted". Failure in the other direction is added. |
| FR2-6 | Accepted. The recompute route is qualified. |
| FR2-7 | Accepted. The O-9 (b) wording now says "until a later amendment creates a new eligible window". |
| FR2-8 | Accepted. The O-8 question now mentions the new fingerprints. |
| FR2-9 | Accepted. The Annex C C-10 (1) follow-up now also covers the `ewma_vol_168h` identity mapping and the combined REG answer. |

## Addendum 2: SR3 focused check of rev 3 (`62977ba`) → revision 4

Sol SR3 (`26f3615`) returned NOT READY. Every finding is accepted.

| Finding | Disposition |
|---|---|
| SR3-1 | Q1 (A) now says the ban bars direct use only, and that a deliberate model with price-history access can rebuild the exact number. "Keep blocked" is named explicitly. |
| SR3-2 | O-6a is removed from this batch, because the channel is needed only before signing. §4 lists the specification items that must be defined before it is asked: key or script and spend rule, enumeration, confirmation depth, timestamp, archive, funding and privacy. It also records the verified 83-byte relay limit, which makes the DRAFT §2.0 message too long. |
| SR3-3 | Every claim of the form "very unlikely to pass" is withdrawn and replaced: "may mostly measure the benchmark; pass probability unknown until D-19". SR3's counterexample is cited. |
| SR3-4 | The follow-up list above has been repaired. |

**FR2-1 is resolved by deferral** (O-6a is out of this batch), not by
verifying the Bitcoin channel. The DRAFT §2.0 message length must be fixed
when the channel is specified.
