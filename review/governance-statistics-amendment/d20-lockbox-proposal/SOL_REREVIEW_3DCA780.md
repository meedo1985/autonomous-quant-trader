# Codex Sol re-check of D-20 lockbox revision 2 (3dca780)

Prompt: `REREVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a17894-ea0a-7a72-82ec-1dfaaecc5683`, 188,205 tokens. The report says the model could not see its exact variant; the CLI header is the verified source.

Verdict: **FIX** (4 BLOCKER, 2 NON-BLOCKING). Findings D20LR2-S-1 .. S-6. First-round S-3, S-6, S-7, S-8 resolved; S-1, S-2, S-4, S-5, S-9 partly resolved.

## Report (verbatim)

## Verdict: FIX

Revision 2 is an **inactive proposal**. It repairs much of the first-round review, but the pre-read transaction, record encoding, and cap rules are not yet exact enough to adopt. This was a read-only review; I wrote nothing. My exact runtime model variant is not visible to me, so I use the requested **S** IDs without claiming a verified Sol variant.

| First-round finding | Re-check | Evidence |
|---|---|---|
| S-1, model seed | **Partly resolved** | A1b restores the protocol line 266 seed and records its derivation. The 31-bit mapping is a new choice, and its proposed seed-0 equivalence test is unsound. |
| S-2, provenance | **Partly resolved** | A7 adds a pre-look `d_sha256`, independent recomputation, and sealing. The evaluation-record contract and failure handling still need exact binding. |
| S-3, confirmation start | **Resolved as a proposal** | A2 labels flat-at-`w0` a new default and Q2 asks the owner. |
| S-4, key custody | **Partly resolved** | B1 binds the public key before C2 signing and specifies retrieval and permissions. Q5 still requires an owner decision on loss or compromise. |
| S-5, day 255 | **Partly resolved** | B3a supplies an anchor and comparisons, but has the cap defects below. |
| S-6, vector bytes | **Resolved** | A5 specifies byte order and sequence order. |
| S-7, ETH drawdown | **Resolved** | A6 binds both BTC and ETH to the same `_max_drawdown` kernel. |
| S-8, R-14 placement | **Resolved factually** | The fixed engine commit, open object freeze, and fixed later-file list support D20L-19 and Q4. |
| S-9, later commitment check | **Partly resolved** | B4 supplies a sealed verification operation, but should explicitly compare against the commitment in the published release entry. |

The statistical core remains consistent with D-11: L-1/L-2 use daily **E-DIFF**, the block length uses the Sharpe influence process of `d`, and L-3/L-4 use hourly drawdown. The `EventResult` bridge correctly avoids passing it to `max_drawdown(BacktestResult)`. The qualified image and engine-commit facts cited in §0 agree with the supplied run definition and freeze evidence.

### Findings

| ID | Severity | Place, failure scenario, minimal repair |
|---|---|---|
| **D20LR2-S-1** | **BLOCKER** | [B4 step 2](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:292>). One fsynced ledger line makes its *fields* atomic, but does not make the separately stored nonce and default bundle durable with that line. A crash can leave budget consumed and EXPOSED with no usable default commitment. Bind durable store write and recovery before ledger commit, make read permission depend on both records, and specify reconciliation. Also define `t_s` as a clock sample taken while committing; the exact fsync instant cannot be known when constructing the entry. |
| **D20LR2-S-2** | **BLOCKER** | [B4 schemas](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:299>). The default bundle is committed before a read, yet `times.read_start` has no null rule. The computed `upside` object’s complete fields and nulls are likewise unspecified. Two implementations can commit different bytes for the same outcome. Give canonical, typed examples for RESULT and DEFAULT, including all nulls, `q` encoding, and `upside` fields. |
| **D20LR2-S-3** | **BLOCKER** | [B3a](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:276>). “An action is valid only if `t < C`” conflicts with adopted D-12 P-7’s express path for a result first released after day 255 to show PASS or FAIL without a certificate. Distinguish post-cap publication of an already fixed outcome from signing, promotion, and owner decisions; give each its own comparison. |
| **D20LR2-S-4** | **BLOCKER** | [A1b and Q1](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:129>). Protocol line 266 yields a full SHA-256 seed; `int(seed_l266, 16) % 2**31` is a plausible estimator mapping, but B4’s `getrandbits(31)` range does not *require* it. Determinism means repeating the **same** seed reproduces a fit; it does not imply seed 0 and another seed produce bit-identical predictions. Label the mapping **NEW DEFAULT** for the owner. Test same-seed reproduction separately; if results differ from the old seed-0 screen, invalidate or rerun affected earlier results. |
| **D20LR2-S-5** | **NON-BLOCKING** | [B3a D20L-21](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:288>). Its disclosure uses `R_j > C − 72 h`. At equality, cooling-off ends at `C`, while a decision requires `t_dec < C`; promotion is still impossible. Change `>` to `≥`, allowing for any reader-path outage as well. |
| **D20LR2-S-6** | **NON-BLOCKING** | [A6](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:175>). `EventResult.start` is a bar **index**, not a UTC instant. Length alone cannot prove the intended window. Bind `series.bars[result.start].open_time` and the complete hourly timestamp sequence for each leg before deriving daily returns or MDD. |

**Labels and owner questions.** Q2–Q5 expose real choices in language a non-statistician can answer. Q1 is not yet fair as a bundle: it calls the estimator mapping a necessary detail and treats the provisional `min(A + 255 days, look + 75 days)` cap as a detail while D11-15 remains assigned to S4. Make those choices explicit and present the corrected cap behavior before asking Q1.

**Machinery to drop:** checking synthetic reference vectors on every real run can be a build/startup qualification check if the runtime and module hash are fixed; repeating it per evaluation adds little evidence. The separate provenance job can also be folded into the authorized sealing engine if it retains the independent recomputation and pre-look hash check.

No tests, lint, types, or import checks apply to this document-only re-check. Under the repository’s review rule, this feedback is **not a completed R19-2 review record** until its findings and verified model metadata are written and committed; the instruction to write nothing prevented that step.