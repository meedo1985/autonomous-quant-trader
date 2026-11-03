# Codex Astra re-check of D-20 lockbox revision 4 (df28ee6)

Prompt: `REREVIEW3_PROMPT.md`, prefixed with "Do NOT open SOL_REREVIEW3_DF28EE6.md; give an independent check." Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a17a0a-d015-7240-aeb2-d504092bc5c1`, 138,709 tokens. Reviewed HEAD 578b45d (rev 4 = df28ee6 plus the Sol record). The report says runtime metadata is not exposed to it; the CLI header is the verified source. IDs used correctly (D20LR4-A-n).

Verdict: **FIX** (2 BLOCKER). Findings D20LR4-A-1 (shared lock gives a timing side-channel on publisher `state`) and D20LR4-A-2 (cap does not end access or processing; existing entry served after C). Dispositions: S-1/A-1 FIX (payload repaired, timing channel remains); S-2, S-3/A-6, S-4/A-5, S-5, S-6, A-2, A-3 ACCEPT; A-4 ACCEPT WITH NOTES. Errata E4-1, E4-2, E4-3 confirmed.

## Report (verbatim)

**Verdict: FIX — two remaining BLOCKERs.** Statistical-binding status: **REVISION_REQUIRED**.

I use **D20LR4-A-n** identifiers. Exact runtime model metadata is not exposed here; the caller’s CLI header must establish it. Reviewed HEAD `578b45d2d4f5f2ae33538f7dfefcf435a9bb39c6`. I did not open `SOL_REREVIEW3_DF28EE6.md` and wrote nothing.

| Authority | Status |
|---|---|
| Frozen Constitution/protocol | Controlling |
| D-11/D-12 owner decisions | Require incorporation through the signed C2 amendment |
| Revision 4 and inherited bindings | Inactive proposals; this review activates nothing |

**New findings**

| ID | Severity | Place, failure scenario, minimal repair |
|---|---|---|
| **D20LR4-A-1** | **BLOCKER** | **[B4.1, line 115](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:115): the common lock creates an observable completion channel.** `state`, `begin_read` and other public-facing operations share `L_store` with `write_bundle` and `mark_finished`, holding it throughout each operation. Compare two executions with identical public records and eventual FAIL: one worker writes its result and finished record; another crashes before those writes. A publisher polling the otherwise constant pre-deadline `state` response encounters lock waits in the first execution. Response latency reveals sealed write/completion activity even though the payload omits it. This requires neither a faulty signer nor a bypassed store. **Repair:** retain synchronization for transaction integrity, but require public response timing and availability to be independent of sealed operations—for example, through a public snapshot and fixed response schedule. Cover every public operation, including deferred/cap answers. Add a controlled contention test; identical JSON alone is insufficient. |
| **D20LR4-A-2** | **BLOCKER** | **[B4.1, lines 121–139](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:121): the cap guards reservation, but does not end access or processing.** Reserve at `t_s=C−1`, commit the default and pre-read entry, then crash before serving any byte. Restart at `C+1`: step 2 returns the existing entry before checking the cap, and all three listed read-gate conditions pass. The first lockbox byte can therefore be served after C. Likewise, the inherited finished-record guard checks `d_w`, which can exceed C. Calling `t_s` the logical authorization time does not establish compliance with P-6’s “processing ends.” **Repair:** bind expiry to the read gate and worker completion, preserving consumed budget, existing evidence and post-cap publication. If previously authorized work is intended to continue after C, route that explicit exception through the applicable owner/S4 decision. Do not introduce the separately rejected “too late to promote” admission cutoff. |

These are specification counterexamples, not claims about an implemented store. A read-only, in-memory lock check confirmed that the fixed public response cannot return while the sealed operation holds the shared lock.

**Revision-4 §1a dispositions**

Here S/A numbers denote **D20LR3** findings.

| Disposition row | Decision | Evidence |
|---|---|---|
| **S-1 / A-1**, publisher state | **FIX** | Line 92 repairs the payload: no finish flag, timestamp or commitment before `d_w`. A-1 above identifies the remaining timing channel. |
| **S-2**, entitlement | **ACCEPT** | Steps 2–3 reconcile the default and bind sealing, nominee/artifact identity, check record and successful startup before creating authorization. |
| **S-3 / A-6**, release bounds | **ACCEPT** | Lines 95–110 impose `[R_j−21600,R_j)`, integer `j≥0`, uniqueness and endpoint tests. |
| **S-4 / A-5**, hourly interval | **ACCEPT** | A6 explicitly requires one-hour series for both legs; the bypass counterexample reproduces. |
| **S-5**, fixture | **ACCEPT** | Full capture hashes and canonical bytes reproduce. `k` is now honestly illustrative. |
| **S-6**, entry costs | **ACCEPT** | Q2(i) matches the owner’s “first permitted entry.” |
| **A-2**, L4 composition | **ACCEPT** | Null propagation belongs to atomic comparisons; false-first `AND3` then resolves both examples consistently. |
| **A-3**, seed-policy branch | **ACCEPT** | Both signed policies have derivation rules; numeric zero is valid; evidence checks policy and derivation. Annex C wording follows both branches. |
| **A-4**, order/cooldown | **ACCEPT WITH NOTES** | Shared conditions are rechecked under the lock, and early requests defer without consuming their test. The separate cap/access defect remains A-2 above. |

The previously marked **FIX rows** are explicitly covered:

| Earlier row marked FIX | Decision now |
|---|---|
| Astra’s **D20LR2-S-4**, seed branch | **ACCEPT**, through repaired D20LR3-A-3 |
| Astra’s **D20LR2-A-1**, L4 | **ACCEPT**, through repaired D20LR3-A-2 |
| Astra’s **D20LR2-A-2**, shared admission | **ACCEPT WITH NOTES**, through repaired D20LR3-A-4; cap caveat above |
| Sol’s **D20LR2-A-4**, publisher disclosure | **FIX**, because the payload repair leaves A-1 above |

For the eight note rows: **read-gate/store-lock ACCEPT WITH NOTES** because synchronization is repaired but creates A-1; **D20L-36, Q5 timing, Q2 adapter placement, embedded attestation, dropped derivable timestamps, Q1/D11-15 separation, and D20L-24/31 wording ACCEPT**. E-1/E-2 are applied correctly. E-3 fixes the explicit state fields, subject to A-1.

**D20L-36 and D20L-37..50**

| Findings | Assessment |
|---|---|
| **36** | **NON-BLOCKING reclassification accepted.** Published result and nominee expiry status are distinct. A pre-cap finished result can remain PASS/FAIL while the nominee is `U_ops`. |
| **37** | Real BLOCKER; payload repaired, disclosure closure incomplete under A-1. |
| **38, 39** | Real BLOCKERs; entitlement/reconciliation and release-window repairs are sound. |
| **40, 41, 42** | NON-BLOCKING classifications and repairs accepted: hourly interval, typed fixture, first-permitted-entry wording. |
| **43, 44** | Real BLOCKERs; repaired, subject to owner adoption of the explicitly proposed precedence and seed policy. |
| **45** | Real BLOCKER; order/cooldown serialization and nonterminal deferral repaired. |
| **46** | Real BLOCKER; distinct store and ledger locks avoid the literal nested-sidecar problem. Synchronizing the gate prevents observing a partially appended or unflushed entry. The broader lock policy introduces A-1. |
| **47** | NON-BLOCKING operational correction accepted: updated build commit, reviewed hashes and fresh G0 evidence are necessary. |
| **48** | Real scheduling BLOCKER, correctly routed to Q2(ii)/S4. R-14’s last sentence covers the confirmation adapter. `screen.py` is the proposed placement, though R-14 technically permits another eligible later-object file. |
| **49** | Citation corrections accepted. |
| **50** | Real BLOCKER; new-reservation guard is correct, but the claimed processing cutoff remains incomplete under A-2. |

**Transaction and disclosure sweep**

Entitlement and cooldown now compose correctly. With the other family’s `r0′`, the earliest authorization is:

`r0′ − 604800 + 2592000 = t_s′ + 30 days`.

The boundary is inclusive at that instant. Order deferral depends on sealed status and pre-read/rejection records, rather than the other family’s result.

Crash handling is coherent before the cap: no durable default means no read; a default without an entry is an orphan; a torn ledger causes an incident; a durable entry with lost acknowledgement is reused; a missing/corrupt referenced default stops access. The gate’s synchronization repairs the append/fsync race. The post-cap recovery case remains unresolved.

| Non-sealed surface | Payload assessment |
|---|---|
| Pre-read entry | No default commitment or finish metadata; added check ID references a pre-read fact. |
| Release entry | Uniform FAIL shape and effective commitment; no public default commitment for comparison. E4-3 applies. |
| No-read entry | Pre-read reasons are permitted; barred descendants inherit the ancestor’s release visibility. |
| Publisher `state` | Fixed pre-deadline payload; effective PASS/FAIL thereafter. Payload repair accepted. |
| `DEFERRED`, `DEFERRED {earliest}`, `CAP_REACHED` | Contents depend on admission records and public schedule, not FAIL subtype. |

**All these public response paths need the timing protection in A-1.**

**Numerical bindings and executable checks**

| Consumer | Quantity, units and rule |
|---|---|
| L1/L2 | Daily BTC E-DIFF: `√365 × mean(c−b)/sample_sd(c−b)`; annualized Sharpe units. Compare inclusively with q and strictly with zero. |
| Prediction q | Type-7 5th percentile of 2,000 lockbox-length E-DIFF replicates; same units as L1. |
| L3 | Hourly-path BTC drawdown magnitudes; candidate minus benchmark `≤0.05`. |
| L4 | ETH E-IMPROV `>0` and ETH drawdown difference `≤0.05`, combined using `AND3`. |
| Cause/upside/attestation | DEFAULT precedes false, then null; upside remains sealed and nongating; PASS attestation fields follow L1–L3. |

Using the actual `calibration.seeds.cj` under Python **3.14.7**, with `-I -B`:

- Fixture serialization equals the displayed bytes exactly: **1,053 bytes**.
- SHA-256: **`d64d228b84a1aaf6015a6860af7f69f2315cc77865e0afad4547822ab54ba520`**.
- All four label-derived capture hashes match.
- All seven decoded floats match: `0.412`, `−0.731`, `0.21`, `0.24`, `0.30`, `0.33`, `0.18`.
- ETH false/null gives **FAIL/PERFORMANCE**; true/null gives **FAIL/TECHNICAL**.
- `"0"*56 + "80000000"` maps to estimator seed **0**.
- The default two-hour runner raises **`CostModelError`**; supplying `sigma_bps` returns **24 equity points spanning 48 hours**.

No replicate vector is supplied, so `k=1275` and `exceeds_p95=false` remain illustrative, not independently validated statistical outputs.

**Freeze timing, errata and owner questions**

A1b’s policy/evidence repair is sound. Annex C’s distinction between independent derivation and accidental numeric equality is also sound.

Both **Q5’s recommended seed parameter and Q2(ii)’s confirmation adapter** must reach the selected, reviewed object bytes before G. Merely merging them is insufficient: update the build commit, matching `FREEZE_REVIEWS.json` entries and committed review records, then refresh G0 evidence. I did **not** report that file’s absence on this branch as a finding.

- **E4-1 confirmed:** eight note rows, not five.
- **E4-2 confirmed:** cite `event_contract.py` lines 151–156 and retain the default-path `CostModelError` qualification.
- **E4-3 confirmed as the supplied clarification:** retain and enforce at insertion the inherited **iff** rule: non-null attestation exactly when PASS and `R_j<C`. A null attestation on a pre-cap PASS must be refused.

Q1–Q5 are broadly fair and answerable without statistical expertise once these blockers are resolved. Q1 correctly leaves D11-15 open. Q5’s “No code change” would be clearer as **“No estimator-seed change; Q2(ii)’s confirmation adapter is still required.”**

The duplicate attestation hash and derivable timestamps were sensible deletions. No further essential transaction machinery is droppable. Consolidating the effective bindings would reduce cross-revision reading without changing history.

**Validation and limits:** worktree and staged diffs remain clean. Fourteen frozen sidecars, seven manifest bindings, seven protocol bindings and the Constitution self-hash passed. `docs/README.md` differs from HEAD only by CRLF checkout conversion. A supplementary oracle-manifest check found six existing CRLF checkout mismatches; their committed bytes match the accepted hashes.

Implementation suites, lint, types and import-boundary checks were N/A for this read-only proposal review. No restricted data or production store was exercised. **LOCAL GATE: BLOCKED. Claude status: NOT SENT.** The caller must preserve this report and verified model metadata in a committed review record before counting it as completed R19-2 evidence.