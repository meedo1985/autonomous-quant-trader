# Codex Astra re-check of D-20 lockbox revision 3 (c86ea8d)

Prompt: `REREVIEW2_PROMPT.md`, prefixed with "Do NOT open SOL_REREVIEW2_C86EA8D.md; give an independent check." Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a179f2-ff65-7970-b81c-dac4a3632ed3`, 113,804 tokens. The report says the model could not see its exact variant; the CLI header is the verified source.

**ID mapping (caller):** the report labels its findings `D20LR3-S-1..6` (it says it uses "S" identifiers). They are Astra's findings and are recorded here as **D20LR3-A-1..6**, same numbers: report `D20LR3-S-n` = **D20LR3-A-n**. They are not Sol's D20LR3-S-n in `SOL_REREVIEW2_C86EA8D.md`.

Verdict: **FIX** (4 BLOCKER, 2 NON-BLOCKING). Findings D20LR3-A-1 .. A-6. Dispositions of Sol rows: S-5 ACCEPT; S-1, S-2, S-3, S-6 ACCEPT WITH NOTES; S-4 FIX. Of Astra rows: A-5 ACCEPT; A-3, A-4, A-6 ACCEPT WITH NOTES; A-1, A-2 FIX. Errata E-1, E-2, E-3 confirmed (E-3 = D20LR3-A-1).

## Report (verbatim)

**Verdict: FIX.** Statistical-binding status: **REVISION_REQUIRED**.

I use **S** identifiers; my exact model variant is not visible here. Reviewed [revision 3](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md>) at HEAD `4d18af94fc65b7dca3cf4fdc83bbde1c673f8bae`. I did **not** open `SOL_REREVIEW2_C86EA8D.md` and wrote nothing.

Frozen governance remains controlling. D-11/D-12 owner decisions require signed C2 incorporation; revision 3 remains an inactive proposal.

**Disposition of every Sol finding**

| Finding | Disposition | Evidence |
|---|---|---|
| **D20LR2-S-1** | **ACCEPT WITH NOTES** | B4.1 writes and fsyncs the default before the ledger entry, samples `t_s` under the lock, and requires both records. This repairs the original durability defect. Read authorization must observe the completed transaction; see the crash audit below. |
| **D20LR2-S-2** | **ACCEPT WITH NOTES** | B4.2 now defines DEFAULT `read_start:null`, complete upside objects, hexf values and PASS cause null. Canonical bytes reproduce. The separate L4 ambiguity below still needs repair. |
| **D20LR2-S-3** | **ACCEPT WITH NOTES** | B3a permits publication after C without certification, consistent with D-12 P-7 line 94. Its table’s “iff” omits the inherited release-window lower bound; finding S-6 below. |
| **D20LR2-S-4** | **FIX** | Mapping is correctly marked NEW DEFAULT; same-seed reproduction replaces seed invariance. However, Q5’s seed-0 alternative contradicts A1b/A7, and the recommended mapping can itself legitimately produce zero. |
| **D20LR2-S-5** | **ACCEPT** | `E ≥ C` correctly prevents promotion. At `R_j=C−259200`, uninterrupted cooling ends at C, leaving no valid decision second. |
| **D20LR2-S-6** | **ACCEPT WITH NOTES** | Resolving `result.start` through its actual series is correct. The claimed hourly-sequence proof additionally requires a one-hour interval check; finding S-5 below. |

For the other reviewer’s rows: **A-1 FIX** (L4 ambiguity); **A-2 FIX** (transaction admission gap below); **A-3 ACCEPT WITH NOTES** (E-1); **A-4 ACCEPT WITH NOTES** for authentication/guard/reconciliation, with E-3 a remaining disclosure blocker; **A-5 ACCEPT**; **A-6 ACCEPT WITH NOTES**, as for S-3/S-5.

**Findings**

| ID | Severity | Place, failure scenario and minimal repair |
|---|---|---|
| **D20LR3-S-1** | **BLOCKER** | **B1 line 180; E-3.** Publisher `state` exposes finished-record presence and its result/commitment. An unfinished deadline FAIL is distinguishable from a finished FAIL; polling also reveals completion before the deadline. Removing `default_commitment` from the pre-read entry does not close this channel. **Repair:** return only the effective `{result, commitment}` once the deadline has fixed the outcome, with identical shape for every FAIL. Never expose finished-record existence, finish time, or intermediate commitments through this operation. |
| **D20LR3-S-2** | **BLOCKER** | **B4.2 line 278.** Explicit three-valued AND says `false AND null = false`, but the immediately following sentence says a condition is null if any input is null. With L1–L3 true, negative ETH E-IMPROV and unavailable ETH drawdown, these readings produce PERFORMANCE versus TECHNICAL, changing the disclosed cycle label. **Repair:** apply null propagation to the *atomic comparisons*; combine them using the stated AND. Add both `false/null` and `true/null` examples. |
| **D20LR3-S-3** | **BLOCKER** | **A1b lines 125–132, inherited A7 seed checks, Q5.** Choosing “seed 0 everywhere” still encounters the unconditional modulo derivation and “No result fitted with seed 0 counts as C2 evidence.” Moreover, `% 2**31` legitimately returns zero for some protocol seeds. **Repair:** branch estimator derivation and validation on Q5’s signed choice. Reject evidence produced under the superseded seed policy, not the numeric value zero. Make Annex C’s replacement wording branch consistently. |
| **D20LR3-S-4** | **BLOCKER** | **B4.1 lines 236–242; D-11 REV3 line 87.** Two different families can pass pre-read checks against the same prior state, then enter `begin_read` sequentially. Both have unused family budgets; neither encounters a cooldown recheck in the listed transaction. Both can obtain authorization despite the required 30-day separation. **Repair:** recheck shared, mutable admission conditions—particularly cooldown—under the transaction lock before reservation. Test concurrent requests from different families, not just duplicate evaluation IDs. |
| **D20LR3-S-5** | **NON-BLOCKING** | **A6 lines 137–149.** `BarSeries` permits intervals other than one hour. The runner’s usual volatility calculation rejects those, but supplying `sigma_bps` bypasses that check. A synthetic two-hour series successfully returned 24 equity points starting at the correct midnight: 48 hours represented as one “day.” **Repair:** require `series.interval == timedelta(hours=1)` in the adapter. With that check, contiguity and the resolved start establish the complete hourly sequence without storing it separately. |
| **D20LR3-S-6** | **NON-BLOCKING** | **B3a lines 211–221.** “Release insert … valid iff `store_now < R_j`” also admits times before the inherited P-7 six-hour release window. The retained B3 rule and the table therefore disagree if the table is implemented literally. **Repair:** include `R_j−21600 ≤ store_now < R_j`, the scheduled integer `j≥0`, and uniqueness, or explicitly label the table as additional cap comparisons rather than complete validity conditions. |

**New findings D20L-22..36**

| Finding | Assessment |
|---|---|
| **22** | Original BLOCKER is real; durable ordering, lookup and duplicate handling are substantially repaired. The broader transaction still needs S-4. |
| **23** | Real BLOCKER. Comparing public default and effective commitments revealed deadline defaults. Removing the former repairs that specific channel; E-3 remains. |
| **24** | Real completion-time inconsistency, correctly repaired by separating bundle-write time from the finished record. “Circular” is imprecise: the problem is recording a later completion event in already committed bytes. |
| **25** | Original schema defects are repaired. S-2 above identifies a remaining rule ambiguity. |
| **26** | Correctly classified QUESTION/NEW DEFAULT. False-first precedence preserves FAIL while changing its cause and potentially the cycle label. It needs owner adoption, not an assertion that it is mathematically compulsory. |
| **27** | Real; post-cap publication and the cooling-off equality correction are sound, subject to S-6. |
| **28** | Real; comparing the scientific projection after authenticating the original bundle fixes timestamp/startup-ID replay failures. |
| **29** | Authentication, trusted signer state and compromise reconciliation are materially repaired. The role table still contains E-3. |
| **30** | Correct QUESTION. The mapping is a choice; deterministic fits need not be seed-invariant. Q5 remains internally inconsistent under S-3. |
| **31** | Scheduling issue is real **under the retained R-14 architecture**. `walk_forward` hard-codes zero; object-bound replacement bytes must be included before qualification freeze. See timing qualification below. |
| **32** | Correctly repaired: the bootstrap seed-source enum selects the appropriate verification branch. This does not repair Q5’s separate estimator-seed branch. |
| **33** | Index correction is right; add the interval check in S-5. |
| **34** | Real BLOCKER, correctly routed to owner/S4. The runner requires a following bar and reads its open. The lockbox bounds fail, and a confirmation window ending at L0 crosses the authorization boundary. |
| **35** | Real missing record binding; NON-BLOCKING classification and B4.3 repair are reasonable. A barred descendant inherits the ancestor’s release visibility and reveals no additional FAIL subtype. |
| **36** | Reasonable clarification QUESTION, but a substantive contradiction is **not established**. A finished result can remain FAIL while its nominee receives `U_ops` because it was not visible at C. Distinguish immutable result from nominee status explicitly; an owner-decision rewrite may be unnecessary. |

**Transaction and disclosure audit**

The intended crash behavior is sound:

- Before a durable default exists: no read.
- Durable default without a committed pre-read entry: orphan, no read, new attempt.
- Torn/damaged ledger append: incident and stop.
- Durable pre-read entry but lost acknowledgement: return the existing entry.
- Missing/corrupt referenced default: incident and no read.

The read gate must share the transaction’s synchronization or otherwise prove commit completion. Merely observing both files while step 6 is writing/flushing is insufficient. Add a concurrent read-gate test during the append and fsync boundary; the existing before/after crash tests do not exercise that interleaving.

For non-sealed observers:

| Surface | Result |
|---|---|
| Pre-read entry | No remaining default-commitment comparison. Attempt number concerns pre-read recovery, not FAIL subtype. |
| Release entry | Uniform FAIL shape and only the effective commitment are appropriate. |
| No-read entry | Rejection reasons are covered by Q2b; barred descendants expose the already permitted ancestor FAIL only, at or after its release. |
| Publisher `state` | **Fails the disclosure requirement until E-3 is applied.** |

**Canonical bytes, statistics, boundaries and replay**

Using the actual `cj` function body, the PASS JSON reproduces byte-for-byte, both with the displayed placeholders and after expanding them. All seven hexf values match their stated decimal examples. The supplied text does not include the synthetic replicate vector, so its illustrative `k=1275` cannot independently be recounted.

The consumer bindings remain consistent:

| Consumer | Binding |
|---|---|
| L1/L2 | Daily E-DIFF: `√365 × mean(c−b)/sample_sd(c−b)`; compare with q inclusively and zero strictly. |
| L3 | Hourly BTC drawdown magnitude difference `≤0.05`. |
| L4 | ETH E-IMPROV `>0` and hourly drawdown difference `≤0.05`; fix null composition. |
| Cause | DEFAULT first, then false, then null, then PASS/null cause—an explicit proposed policy. |

Independent arithmetic reproduced `start=22344`, `n=10968`, `len=33312`, hence runner rejection without a terminal bar. For the cap, `R_j=C−259201` leaves one decision second; `R_j=C−259200` leaves none. Reader outages can only push E later.

B4.4’s projection excludes all identified execution-varying metadata. A faithful replay must retain the original evaluation identity and recorded capture bindings; under those constraints, no necessary difference outside `operational` was identified. The in-memory projection comparison passed. This is specification evidence, not an implemented replay test.

**Labels, questions and errata**

The revised DETAIL definition is honest, and the mapping, cap, anchor and cause precedence are now exposed as choices. Q1–Q4 are broadly answerable without statistical expertise. Q5 needs S-3 repaired.

Q5’s timing claim is true for the existing freeze and unchanged R-14 route, but “merge before G” is insufficient operationally: the freeze must select the updated build commit and matching reviewed file hashes. Step G currently names a fixed build commit. “This option is gone” should mean **unavailable under the retained frozen-object route**, not impossible through any future formal amendment. Q2’s confirmation adapter also needs placement/timing consistent with R-14.

- **E-1 confirmed:** cite **D-12 Q4, route R-a**, not “P-6 R-a.”
- **E-2 confirmed:** RN-1 is `screen.py` **720–721**.
- **E-3 confirmed:** substantive blocker, recorded as S-1 above.

Further machinery that can be dropped: duplicate storage of derivable timestamps/seeds and duplicate encoding prose across revisions. Keep the durable default, sealed verification, shared admission lock and effective-result interface.

Validation used read-only Python 3.14.7 checks with `-I -B`; the successful checks and counterexample are recorded above. Worktree/staged diffs were empty. Fourteen sidecars, seven manifest bindings and the Constitution self-hash passed. Protected inventory matched HEAD; `docs/README.md` alone differed in raw bytes through CRLF checkout conversion. No historical accepted-baseline claim is made.

Implementation tests, lint, types and import-boundary suites were N/A for this document review. No restricted data or external reviewer was used. This response still requires caller-recorded model metadata and a committed review record before counting as completed R19-2 evidence.