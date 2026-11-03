# Claude candidate (written before reading GPT's)

## 0. The honest frame (criterion 2)

What step M `certify` establishes: that the **D-19 statistical method** (screen + calibration) is within its targets on held-out data (FREEZE_HELDOUT.md "What it is"; M: "every test is within its target (§6)"; §5 step 6 "the method does not qualify"). It is **not** a strategy result and does not by itself permit any trade. After it, real money still needs, per the frozen Constitution and the deployment draft:

1. A cycle under an activated protocol: §4 amendment for C2 (`review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md`, status "AI WORDING PROPOSAL — NOT AUTHORED — NOT SIGNED — NOT ACTIVE"), owner-authored and signed (§4).
2. A promoted candidate: `eligibility_gate → lockbox_request → promotion_attestation`, human `APPROVE_AS_IS`/`REJECT` (§13), cooling-off ≥ 72 h (§3 line 52) — or the named deployable baseline (§11), which is exempt only from beating itself.
3. The deployment protocol activated (`review/deployment/DEPLOYMENT_PROTOCOL_v1_DRAFT.md`, "DRAFT — NOT ACTIVATED"; §19 "Separate deployment protocol required before shadow").
4. Forward paper of that candidate for L-02 ≥ 240 effective decisions (draft §1, 2.2), then shadow 90 days (D-3, owner-set, 2.3), key rotation rehearsal (§28), L-01 non-zero (now 0) and §25 C-8 signed, then canary.

So the earliest real money is **months away on every path**. Two paths run in parallel:
- **Baseline path** (already running): forward paper since 2026-10-04; baseline decides daily, so 240 effective decisions ≈ 8+ months (`review/task29/OWNER_REVIEW.md` Q4) → about June 2027, + shadow 90 days → about September 2027 at the earliest. It earns no "edge" claim; §12 says vol management is de-risking, not alpha.
- **Research path**: D-19 attempt 1 (now) → C2 amendment → cycle → candidate → promotion → candidate's own L-02 (faster only if it decides more often than daily) → shadow 90 d → canary. Realistic earliest: second half of 2027. `NO_EDGE_FOUND` at any step is a valid end.

Neither path can honestly be made "soon"; what can be done is removing idle waiting from the critical path.

## A. Owner — now and soon (ordered)

1. **Today:** weekly Telegram alert test (due 2026-10-25) and its ack. Keeps the alert channel (needed before shadow) proven.
2. **Next days:** keep the laptop on as much as practical so the Bitcoin node finishes its first sync; say "check node" in sessions. Start/stop with the Desktop files only.
3. **~2026-10-31:** send the dev-run weekly status (Notepad file I prepare) → if finished, step F `choose` (FP1). Exit 3 `margin_failed` comes to you to decide.
4. **FP3 — the largest owner lever, start now in parallel:** decide how the drand chain is bound (chain hash + public key + whether the 7-day failure rule applies), through the formal process (Constitution §4 amendment or the C2 signing). The AI explains the options and their consequences; **you** write, sign and activate. Every step from G onward waits on it, and the node's block window (projected to drop F_Q1 around mid-January 2027) makes **early January 2027** a practical deadline for the post.
5. **Wallet safety (FP5):** confirm the Electrum wallet holding `A_Q1`'s key has an offline seed backup (paper), since the laptop now holds both the key and the node. Losing the key voids the attempt (DF5-1 uses keys up).
6. When asked: §16-style review/merge of PR #76 (sheet, once H/I are written and reviewed) — docs, but it is the procedure you will execute. PR #78 (skill) at your convenience.
7. Later, not on the critical path now: decide the deployment draft's OPEN values and L-01; consider (not now) whether D-3's 90-day shadow stays — shortening it is a risk loosening and should be a deliberate, recorded owner decision.

## B. AI — now (ordered)

1. Write steps H/I for a laptop node, closing the items that block step H: event-based acceptance time from the node's `UpdateTip` log prefix (FP4N-R2/FP4N2-R2), `shrinkdebugfile=0` before the post, clock check, scan gate with `scanblocks completed:true` + covered heights + `getdescriptoractivity` (FP4N-R3), `estimatesmartfee 6` numeric (FP4N-R4); Codex review to ACCEPT; record.
2. FP3 explainer for the owner: what exactly must be bound, the candidate chains (e.g. drand mainnet "default" vs "quicknet": period, signature scheme), what the engine/sheet expect (prereg §8 round rule, DRAFT §2.0 failure rule), and the formal route options. Plain language; no AI-authored amendment text presented as the owner's.
3. Prepare the ~10-31 dev-run status Notepad file and step F; on finish, record evidence and run `choose` per FULL_RUN.md.
4. Daily node checks; after first sync measure W, fill MARGIN LOW DATE, re-measure weekly.
5. Estimate the held-out run duration on the 2-vCPU server from the dev run's measured throughput (12k dev vs 20k held-out reps, BF1 estimate), so the owner sees the real calendar; check server disk for it.
6. Fix the stale sheet header ("Three preconditions are open (FP2...)"): FP2 holds.
7. Write a one-page roadmap from certify to canary (sections above) with the gates, owners and durations, so the owner's "how soon" has one honest answer.

## C. Checks / verification

1. FP4 timing: post (step H) must happen while `pruneheight <= 972269`; margin rule S2 and the projected mid-January window vs FP3 timing.
2. D_Q1 = 1,000,000 post deadline (~6 months), FP6 fee ≤ ~30 sat/vB on post day.
3. FP5 on the post day: both explorers show `A_Q1` unspent holding only `F_Q1`.
4. Forward paper health weekly (it is the baseline path's evidence clock); Telegram weekly.
5. Docker packages stay held until step M; dev run memory under the slice.
6. CI flakiness (AMD EPYC probe segfault) is a known inconclusive, not a pass.
7. Server disk and the held-out run's resource needs before step L.

## Critical path (research path)

FP1 (~10-31) ∥ FP3 (owner, unknown) ∥ FP4 sync (days) ∥ H/I written+reviewed (AI, days) → G freeze (hours) → H post + 6 conf (~1 h; fees) → I freeze read (+7 days) → L held-out run (weeks; to estimate) → M certify + owner decision → C2 amendment/cycle → … months.
Earliest certify if FP3 is done by mid-November: roughly December 2026–February 2027.

## Least sure of

1. That certify concerns only the method and not any trading strategy (I read FREEZE_HELDOUT.md and §5 step 6 that way).
2. The held-out run's duration on the server.
3. Whether the C2 signing is the intended route for FP3 or a separate amendment is needed before step G.
