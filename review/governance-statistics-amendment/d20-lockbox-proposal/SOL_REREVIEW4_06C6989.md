# Codex Sol re-check of D-20 lockbox revision 5 (06c6989)

Prompt: `REREVIEW4_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-27): model `gpt-6-sol`, provider openai, sandbox read-only, reasoning effort high, Codex CLI v0.164.0, session id `01a17c1d-d353-7260-9c82-711a8fbb560c`, 74,355 tokens.

**ID mapping:** the report labels its findings `D20LR5-A-1..4` (it could not see its model variant and followed the Astra instruction). The CLI header shows `gpt-6-sol`, so these are recorded as **D20LR5-S-1..4**: A-1 = S-1, A-2 = S-2, A-3 = S-3, A-4 = S-4.

Verdict: **FIX** (3 BLOCKER, 1 NON-BLOCKING). Dispositions: D20LR4-S-1 ACCEPT; D20LR4-S-2/A-2 FIX (-> S-1); D20LR4-A-1 FIX (-> S-3); D20LR4-S-3 ACCEPT. D20L-51, D20L-54, D20L-55 accepted; consolidation deferral accepted.

No finding is left unrepaired yet; dispositions go in revision 6.

## Report (verbatim)

**Verdict: FIX.** Rev 5 repairs the missing attestation rule, but its cap check, snapshot recovery, and timing claim still need changes before the owner decides Q1. Statistical-binding status: **REVISION_REQUIRED**. This is a read-only review of an inactive proposal; it activates nothing. Runtime model variant is not exposed here, so the caller should verify the CLI header before recording the provisional `D20LR5-A-n` IDs.

| Authority | Status |
|---|---|
| [Frozen Constitution](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72) and [protocol](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:73) | Controlling; research receives PASS/FAIL only. |
| [D-12 owner decision](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/OWNER_DECISION_D12.md:20) | Decided, subject to the signed C2 amendment. |
| [D-20 rev 5](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:1) | Inactive proposal. |

The affected consumers are `begin_read` and the read gate (`C`, the day-255 cap, in store-clock seconds); the worker and fix step (`D* = min(d_w, C)`); and the publisher and readers (the durable public snapshot `P`, release time `R_j`, and response delay `Δ`). This re-check changes no Sharpe or prediction statistic.

### Prior-finding dispositions

| Rev-4 finding | Re-check | Evidence |
|---|---|---|
| D20LR4-S-1, missing PASS attestation | **ACCEPT** | [B1/B3a/B4.3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:51) enforce non-null iff PASS and `R_j < C`, with signature, evaluation ID, and cooling-off-start checks. The inherited publisher P-8 check still covers the remaining identity fields. A refusal inserts no release row; P-7 requires a missed-release incident and later retry. Thus “no other trace” is true of the release index, not of the incident record or the disclosed R1 timing residual. |
| D20LR4-S-2 / D20LR4-A-2, processing beyond C | **FIX** | The new order and `D*` close the reported post-cap reconciliation and bar-service paths, but a latched `t_s < C` can authorize a later write after C. See A-1. |
| D20LR4-A-1, shared-lock timing | **FIX** | Separate locks remove direct waiting on `L_seal`; the asserted timing guarantee and its test remain incomplete. See A-3. |
| D20LR4-S-3, E4-1/E4-2 | **ACCEPT** | Eight note rows is correct. [The code](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/backtest/event_contract.py:151) calls the hourly-return check only on the default volatility path; [that check](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/backtest/costs.py:251) rejects a non-hourly series. |

### New findings

| ID | Severity | Place, failure scenario, minimal repair |
|---|---|---|
| **D20LR5-A-1** | **BLOCKER** | [B4.1 cap and retained steps 7–8](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:99). Sample `t_s = C−1`; let verification or entitlement take two seconds. The proposal can then write a rejection or default and pre-read entry at `C+1`, although P-6 says processing ends at C. Recheck the store clock on every admission or rejection write and define what must be durably complete before C. Test a call that crosses C between sampling and each commit. |
| **D20LR5-A-2** | **BLOCKER** | [Snapshot update after index append](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:84). Crash after a release row is fsynced but before `P` is replaced: the index contains the row, while readers using `P` cannot see it. A retry finds an existing row and cannot insert another. The analogous pre-read crash leaves a consumed try invisible to the read gate. Specify startup reconciliation that rebuilds and durably replaces `P` from the verified index before serving requests, and replay an interrupted `D*` fix step. Add both crash points to tests. |
| **D20LR5-A-3** | **BLOCKER** | [Fixed schedule and contention test](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:90). `Δ` is above a *measured* worst case, not a guaranteed bound. A worker fsync load can push a public answer beyond `Δ`; logging the overrun does not conceal its latency. The proposed test also cannot hold `L_seal` indefinitely **through** `D*` and compare post-fix `state` bytes with an idle run: the fix step itself needs that lock. Define the permitted residual disclosure for owner review, or establish a response and availability contract that holds under the stated contention model. Compare like-for-like public state, and test the fix boundary separately. |
| **D20LR5-A-4** | **NON-BLOCKING** | [Q1](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:145) names `Δ` but omits the moved `state` boundary from its added-defaults list. The owner would adopt a new disclosure time without seeing it in the choice. Add the boundary and state how `Δ` is bounded or chosen before asking for adoption. |

D20L-51 is real, correctly classified and repaired. D20L-52 and D20L-53 are real blockers but only partly repaired. D20L-54 and D20L-55 are applied correctly: the Q5 qualification, Q1/Q4 plain-language summaries, Q2(ii) R-14 alternative, deletion of derivable `earliest`, and uniform `CAP_REACHED` are sound.

The near-cap consequence is stated fairly for the owner. For example, `t_s=C−3600` gives `D*=C`: the worker has one hour, and an unfinished read becomes FAIL/DEADLINE while spending the family’s try. The release result and the nominee’s `U_ops` expiry are distinct. Q1–Q5 are otherwise understandable without statistical expertise. Deferring consolidation until the S4 draft is acceptable, provided that draft presents one complete effective text for signature and review; no additional binding appears droppable now.

These are specification counterexamples and an exact boundary calculation, not execution tests. No files were written, and no implementation, lint, type, or import checks apply to this read-only review. This response alone is not a committed R19-2 review record.