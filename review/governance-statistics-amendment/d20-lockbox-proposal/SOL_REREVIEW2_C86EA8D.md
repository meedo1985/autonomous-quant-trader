# Codex Sol re-check of D-20 lockbox revision 3 (c86ea8d)

Prompt: `REREVIEW2_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a179ed-ec0c-7e82-a7e3-afc30f59bc84`, 106,869 tokens. The report says the model could not see its exact variant; the CLI header is the verified source.

Verdict: **FIX** (3 BLOCKER, 3 NON-BLOCKING). Findings D20LR3-S-1 .. S-6. Dispositions: S-4, S-5, A-3, A-5 ACCEPT; S-1, S-2, S-3, S-6, A-1, A-2, A-6 ACCEPT WITH NOTES; A-4 FIX. Author errata E-1, E-2, E-3 confirmed (E-3 blocking, = D20LR3-S-1).

## Report (verbatim)

## Verdict: FIX

Revision 3 is an **inactive proposal**. It repairs most of the revision 2 findings, but its publisher `state` response exposes outcome timing, its read gate does not verify the pre-read entitlement, and its release guards permit inserts before D-12’s six-hour window. These need repair before an owner decision on the package.

I used **S** finding IDs; my exact runtime model variant is not visible to me. This was read-only. The worktree was clean, and I wrote nothing.

### §1a dispositions

| Row | Disposition | Evidence |
|---|---|---|
| S-1 | **ACCEPT WITH NOTES** | Sealed-default fsync precedes the pre-read entry; the read gate requires both. Existing-entry reconciliation needs an explicit check before returning a retry. |
| S-2 | **ACCEPT WITH NOTES** | Nulls, `upside`, and `hexf` are specified. The claimed exact PASS fixture still contains placeholder hashes. |
| S-3 | **ACCEPT WITH NOTES** | Post-cap publication is restored. The new insert rule omits P-7’s six-hour lower bound. |
| S-4 | **ACCEPT** | The 31-bit mapping is correctly labeled a new owner choice; the seed-0 equivalence test is gone. |
| S-5 | **ACCEPT** | At `R_j = C − 259,200`, `E = C`, so no decision can satisfy `t_dec < C`. |
| S-6 | **ACCEPT WITH NOTES** | Resolving `EventResult.start` through its series is correct; A6 must also assert a one-hour interval. |
| A-1 | **ACCEPT WITH NOTES** | PASS/null cause, DEFAULT precedence, and three-valued AND are coherent; the fixture qualification above applies. |
| A-2 | **ACCEPT WITH NOTES** | The serialized uniqueness and budget checks repair the race. The resulting read entitlement remains too weak. |
| A-3 | **ACCEPT** | Replay verifies the release commitment, then compares the bundle without `operational`; a faithful replay can differ there. |
| A-4 | **FIX** | Roles and trusted signer guard state are added, but publisher `state` discloses finished-record presence and commitment before `d_w`. |
| A-5 | **ACCEPT** | The closed seed-source enum makes both signed choices verifiable. |
| A-6 | **ACCEPT WITH NOTES** | Cap equality and post-cap visibility are repaired; enforce the release window as well. |

### New findings

| ID | Severity | Place, failure scenario, minimal repair |
|---|---|---|
| **D20LR3-S-1** | **BLOCKER** | [B1 publisher `state`](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:180>). Before `d_w`, finished-record presence distinguishes an unfinished DEADLINE FAIL from a finished FAIL; returning its commitment also exposes outcome timing. Apply E-3: after `d_w` only, return the effective `{result, commitment}`, with no finished-presence bit or default commitment. |
| **D20LR3-S-2** | **BLOCKER** | [B4.1 read gate](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:236>). `begin_read` checks index and budget but not the sealed status-(a), ELIGIBLE nominee and successful pre-read identity/artifact checks. A publisher call can create an entry that passes the stated two-record bar gate without those prerequisites. Bind a verified pre-read entitlement to the entry and require the gate to match it; reconcile the default before returning an existing entry. |
| **D20LR3-S-3** | **BLOCKER** | [B3a and signer guard](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:207>). `store_now < R_j` permits an insert or signature days early, whereas decided [P-7](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV7.md:86>) puts the publisher sequence in `[R_j − 6 h, R_j)`. Add that lower bound to the store guards and test both endpoints. |
| **D20LR3-S-4** | **NON-BLOCKING** | [A6](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:136>). `BarSeries` permits a uniform interval other than one hour; contiguity plus start and length alone do not prove hourly timestamps. Assert `series.interval == 1 hour` for both legs. |
| **D20LR3-S-5** | **NON-BLOCKING** | [B4.2 PASS example](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:288>). Its key order and float encodings reproduce under `cj`, but `0…`–`3…` are not the specified 64-hex hashes, and the unnamed 2,000-vector cannot verify `k`. Replace placeholders with full hashes for a byte-exact typed fixture; label `k` illustrative unless its vector is supplied. |
| **D20LR3-S-6** | **NON-BLOCKING** | [Q2(i)](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:388>). “Each paying its entry cost on the first day” overstates the [D-11 owner decision](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/OWNER_DECISION_D11.md:11>): cost is paid at each leg’s **first permitted entry**, which need not occur on day one. Use that wording. |

### Checks requested

**D20L-22..36.** The newly discovered 23, 24, 26, 31, 34, 35 and 36 are real. D20L-23’s equality-of-commitments leak is removed from the pre-read entry, subject to S-1 above. D20L-24 correctly removes the circular bundle `finished` field. D20L-26 is an owner choice: with `(false, false, true, null)`, definite failure produces PERFORMANCE under the proposed precedence, while revision 2 produced TECHNICAL. D20L-31 is correctly time-sensitive: [R-14](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:152>) binds `screen.py` to the qualification object, and [the current fit uses seed 0](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/calibration/screen.py:1547>); the recommended seed path must enter that object before step G. D20L-34 is a genuine blocker: the [runner requires `bars[j+1].open`](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/backtest/event_contract.py:206>), while D-11 authorizes bars only through the excluded end. Routing the end-price convention to S4 and Q2(ii) is right. D20L-35 supplies the required barred-descendant record. D20L-36 is appropriately a **QUESTION**: the owner’s “finished results keep their outcome” can refer to the stored result, while P-6 assigns an unreleased nominee `U_ops`; the owner should clarify the status wording.

The remaining 22, 25, 27–30 and 32–33 have sound classifications and proposed repairs, subject to S-2 through S-5 above. In particular, the code confirms that [`append_entry` only serializes and verifies the chain](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/core/ledger.py:369>), and [`EventResult.start` is an integer index](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/backtest/event_contract.py:93>).

**Records and arithmetic.** The pre-read entry has no FAIL-kind discriminator. The release entry’s random-nonce commitment has no published default commitment to compare against; the no-read reasons are fixed before any read and are allowed by D-12 Q2b. Publisher `state` is the remaining discriminator. For B4.2, I checked canonical key order and decoded every displayed float; the values match the prose. Three-valued AND gives `false AND null = false`, and DEFAULT precedence remains DEADLINE. For B3a, with no outage, `R_j=C−259,201` permits `E=C−1`; `R_j=C−259,200` gives `E=C` and cannot promote. Post-cap PASS/FAIL publication remains required. B4.4’s projection changes only by dropping `operational`; it retains the scientific fields and `capture`.

**Questions and errata.** E-1 is correct: R-a is the owner’s **D-12 Q4** route. E-2 is correct: RN-1 is at [`screen.py` 720–721](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/calibration/screen.py:720>). E-3 is correct and blocking. Q2–Q5 expose understandable choices, and Q5’s before-freeze claim is true under the proposed R-14 layout. Q1 is a large conditional package, including a provisional cap still assigned to S4; its adoption must not be read as settling D11-15. Q2(i) needs the cost wording repair.

The publisher’s broad `state` payload can be reduced as E-3 says. The release row need not store both a full `attestation` and a hash reference to that same embedded object unless a separate lookup uses the reference. The orphan attempt, separate finished mark, and sealed replay comparison have concrete recovery or audit purposes.

No tests, lint, type, or import checks apply to this document-only review. Because you required **write nothing**, this response is not the committed review record that the repository requires before counting an R19-2 check as complete.