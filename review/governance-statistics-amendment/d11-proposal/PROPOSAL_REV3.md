# D-11 decision proposal, revision 3 (senior-statistical-governance agent)

This is a delta on `PROPOSAL_REV2.md` (845a516), made after the R19-2 re-checks `SOL_REREVIEW_845A516.md` and `ASTRA_REREVIEW_845A516.md` (aa5f665). Agent: `senior-statistical-governance`, read-only, checkout `aqt-freeze-sheet` at `aa5f665`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). The report follows verbatim; only the harness's indentation was removed.

---

# D-11 decision proposal, revision 3 (delta on revision 2)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, as reported by the session metadata. I am an AI reviewer, not an authority. This is a proposal only: it accepts, signs and activates nothing.

**What it revises:** revision 2 (`d11-proposal/PROPOSAL_REV2.md`, `845a516`). It answers `SOL_REREVIEW_845A516.md` (gpt-6-sol, FIX, D11R2-S-1..4) and `ASTRA_REREVIEW_845A516.md` (gpt-6-astra, FIX, D11R2-A-1..4), both committed in `aa5f665`, which I read in full.

**How to read it:** revision 3 is a delta. Every section of revision 2 that is not restated below stands unchanged.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, HEAD `aa5f665`, read-only. Nothing was edited or committed. No simulation was run, and there was no confirmation, lockbox, network or credential access.

**Review status:** revision 3 is unreviewed. R19-2 requires a focused re-check before any owner decision.

**VERDICT: `AMENDMENT_REQUIRED`**, unchanged from revision 2:
- Route A (the statistics) is a `BINDING_CANDIDATE`.
- The lockbox run needs the §7a and threat-model access amendment (Q2).
- Retaining the historical window needs a Constitution §0 reading, adopted through §4 (Q3).

## §2 (changed row): Numerics

**Float64 numerics rule for L-1 and L-2 (a proposed D-11 choice, not accepted).**
- The float64 output of the reference code decides L-1 (`T_L ≥ q`) and L-2 (`T_L > 0`), including sign residues. Example (rev 2 §6): when the exact mean difference is 0, float64 gives E-DIFF = 8.384e−16, so L-2 passes.
- C-0 Numerics covers the L gates only by AI default (SA5-6), so the owner must adopt this rule.
- The alternative is a tolerance band around 0, for example treating `|T_L|` below a fixed ε as not > 0. That would be a new threshold, which makes it an amendment question.

## §4 (replaced): Execution contract for one lockbox evaluation

All of this needs the §4 amendment to Constitution §7a and to the threat-model permission for `lockbox_eval` (D11-13; Q2).

1. **Inputs handed over: identifiers only.** The experiment engine passes `lockbox_eval` exactly these, and nothing else:
   - the cycle-record hash;
   - the declaration hash;
   - `trial_id`;
   - the hypothesis hash;
   - the configuration hash;
   - the sealed prediction artifact (q, n, b, stream identity, artifact hash).

   No confirmation per-bar output and no fitted model crosses identities.

2. **Immutable lookup.** `lockbox_eval` fetches these from the append-only registry (Constitution §26) and the cycle record:
   - the hypothesis record (§8 fields: training rule, retrain hash, grid point, feature hash, exposure mapping, band and minimum hold, cost hash);
   - the declared trial code and configuration;
   - the nominee's declared model seed, fixed before the beacon post (C-13);
   - the backtester and engine code at the commit bound in the cycle record (`cycle_start_bindings`; R-8 engine commit), on the pinned image;
   - the data-manifest hash.

3. **Verification before any lockbox byte is read.** Every hash must match the cycle record and the declaration, and the prediction artifact's identity must match the nominee.
   - [AI default] On a mismatch, `lockbox_eval` reads no lockbox data, so the segment is not EXPOSED.
   - The nominee's lockbox result is then a technical failure, a `NO_RESULT` cause (DRAFT l.325–326).
   - There is no retry in C2.

4. **Read-only data.** BTC and ETH 1h bars over `[S_pre, L1)`, with S_pre = 2022-11-13T00:00Z, under the manifest hash.
   - S_pre gives 4,800 warm-up hours before the first 24-month training row on 2023-06-01 (FEATURE_FACTORY l.20).
   - EMA, EWMA and benchmark-volatility state are initialised at S_pre, with the feature factory's own convention.

5. **Fits.** `lockbox_eval` refits the nominee itself, with the declared model seed:
   - refits at `r_k = L0 + 30k` days, k = 0..15, the last on 2026-08-25;
   - each trained on `[r_k − 24 months, r_k)`, with labels purged at `r_k` (l.198–200, l.205).

   No confirmation-fitted model is used. Rule-based nominees skip fitting.

6. **Start state: both legs flat at L0, for BTC and ETH.** This is a **new proposed binding**. It is not the CPCV convention, because C-14 (3) restarts only the candidate and slices the benchmark (D11R2-A-3, S-1).
   - **At L0:** exposure 0, no pending order, unset clock, fresh overlay, equity 1.0; MDD measured from L0.
   - **Justification:** it reproduces at L0 how the prediction source was produced. Each confirmation leg is one run started flat at `w0`: C-10 (4) states this for G-11 draws, and EC-3 in `src/aqt/backtest/event_contract.py` is a *proposed* reading of it (D11-16).
   - **Consequences:** both legs pay their entry cost at L0, and the benchmark holds nothing before its first 00:00 decision.
   - **Alternative:** carry the benchmark on from S_pre. That gives the benchmark a position the candidate lacks, and the target would no longer match how the source was produced.

7. **Outputs.**
   - Research gets PASS or FAIL only (§7 l.79).
   - The attestation record gets the coarse fields as decided by **D-12, which is still open**.
   - The human approver receives the attestation (§13).
   - Every other output stays under the `lockbox_eval` identity.

## §7 (replaced paragraph): Reads, budget and sealing

**Reads.** v1.0 **permits**, but does not require, more than one read of the same window within a cycle: two evaluations per family (l.74), with the window marked EXPOSED at each read (§7 l.77). Under C2 (one read per family, DRAFT §2.3), each family's read:
- consumes **that family's** lockbox budget;
- is logged;
- gets **its own evaluation ID**;
- leaves the segment EXPOSED.

Release to confirmation happens only between cycles (§7 l.81–83). The two reads are at least 30 days apart (DRAFT l.243).

**Sealing [AI default].** Before the first lockbox read, each declared family's terminal pre-lockbox status is sealed and recorded. It is exactly one of:
- (a) a fixed nominee that is ELIGIBLE, with a valid sealed prediction artifact;
- (b) no nominee (the family is `UNAVAILABLE`, Annex A P18-3);
- (c) a nominee that is not ELIGIBLE;
- (d) a nominee whose gates or prediction artifact are `UNAVAILABLE`.

Rules:
- Only status (a) requests a read.
- One family's status never blocks the other family.
- The purpose: nothing about any family is decided after any lockbox result exists (D11R2-A-1).

## §9 (replaced cost paragraph): What a future window would cost

**Assumptions:**
- day 0 = declaration;
- the future window is `[day s, day s+m)` with s ≥ 0;
- the processing allowance after the window ends is p = 7 days (finalised klines, run, verification) [assumption];
- the first read is at R1 = s + m + p;
- the second read is at R2 ≥ R1 + 30;
- each promoted nominee's attestation and 72 h cooling-off end by R + 3;
- `lockbox_eval` processing ends at day 255 (DRAFT l.244).

**The draft states the end of processing in two ways (D11-15):**
- reading (i): a fixed day 255 (P18-2, "day 180 plus the fixed post-pick window"; `calendar_cap_rule`);
- reading (ii): the nomination look plus 75 days (`post_nomination_window_days`).

The look happens at the earlier of plan completion and day 180 (P18-2).

**Arithmetic (exact, with s = 0 and p = 7):**

| Case | Constraint | Maximum m | Approx. L-2 SD* |
|---|---|---|---|
| Two families, reading (i) or a look at day 180 | m + 7 + 30 + 3 ≤ 255 | **215 days** (zero slack) | 1.303 |
| One family, same | m + 7 + 3 ≤ 255 | 245 days | 1.221 |
| Two families, reading (ii), look at day L | m ≤ L + 35 | L = 120 → 155 days; L = 60 → 95 days | 1.535 at 155 days |
| A 457-day future window | the cap must be ≥ 457 + 40 = 497 days | needs a new cap | 0.894 |

\* SD = √(365/m), under the same Gaussian, near-zero-Sharpe, unselected-nominee assumptions as rev 2 §6. Illustrative only.

**Conclusion, stated plainly.**
- **Every future window needs amendments to:** the partition dates (l.67); the "15 months" basis of the pass rule (l.92); and reading the ingested future data into the lockbox identity.
- **About 7 months** (at most 215 days) fits the current timing rules only under reading (i), or if the look happens at day 180, and then with zero slack.
- **Under reading (ii) with an early look,** P18-2's look timing or O-2's 75-day window must also change.
- **A 15-month future window** requires changing O-2 and raising the 255-day cap to at least about 497 days.
- **In every case** the earliest read moves to at least about day m + 7. Under the historical window it can follow the gates directly after the look.

Retaining the historical window needs R2 ("later than confirmation and held back from research") written at the **Constitution §0 level**, through §4 (D11R2-S-2 note). Protocol wording alone cannot override §0.

## §10 (additions): New findings

- **D11-15, QUESTION (on the S4 draft).** DRAFT §2.3 gives `post_nomination_window_days: 75` and a day-255 `calendar_cap_rule`, without saying whether the window runs from the actual look or ends at a fixed day 255. P18-2 suggests the latter. The S4 draft should resolve it, because it matters for any future window and for an early look.
- **D11-16, NON-BLOCKING.** No decided clause fixes the start state of the confirmation **baseline** run. C-10 (4) covers G-11 draws only, and EC-3 is a proposed code reading. The prediction source depends on it, so D-20 or Annex C should bind it. The justification in §4 item 6 holds only if EC-3 is accepted.
- **D11-12 wording correction:** "accepted under C-0 Numerics" becomes "proposed D-11 choice" (§2 above).

## Dispositions

| ID | Disposition |
|---|---|
| S-1 | Accepted, repaired: §4 items 1–3 (lookup and verification); item 6 (both legs flat, as a new binding with its justification; D11-16) |
| S-2 | Accepted, repaired: §9 derives the schedule and names the rules that must change |
| S-3 | Accepted, repaired: §2, now a proposed choice, with an alternative that would need an amendment |
| S-4 | Accepted, repaired: §7 (per-family budget, log, evaluation ID) |
| A-1 | Accepted, repaired: §7 terminal-status sealing; the other family proceeds |
| A-2 | Accepted, repaired: §9, with explicit assumptions, the 75-day and 30-day rules, the 72 h cooling-off and processing time; D11-15 |
| A-3 | Accepted, repaired: §4 item 6, explained in Q2 |
| A-4 | Accepted, repaired: Q1 states the shared D-20 cost; Q2 names the recipients and keeps the D-12 qualification |
| Astra note ("permits") | Accepted, repaired: §7 |

## Owner questions

**Q1. What should the lockbox's main BTC test measure?** Every option needs new, reviewed code (the lockbox rows of D-20).
- **"Average daily difference, as written (Recommended)."** BTC passes only if its average daily return over the lockbox beats the benchmark's, and is not unexpectedly low against the range predicted from confirmation. It does not have to win every day. This keeps the frozen rule text and tests the same claim your luck test certifies. A smoother strategy that earns less on average fails; how often that happens to good strategies is unknown.
- **"Sharpe minus Sharpe."** The frozen rule text must be rewritten, and it tests a claim the luck test never certified.
- **"Keep blocked."** C2 cannot be signed as drafted.

**Q2. May the lockbox checker read the price history from 2022-11-13 to 2025-05-31 and run the strategy exactly as registered?** If so, the checker:
- looks up and checks the registered strategy by its fingerprint;
- retrains the strategy itself;
- starts both the strategy and the benchmark with no position on 1 June 2025. This is a new choice: both pay their entry cost on day one, matching how the confirmation runs started.

Research gets only PASS or FAIL. The attestation record gets the coarse fields, whatever D-12 decides, and you receive the attestation.
- **"Yes, add it to the C2 amendment (Recommended)."** This changes Constitution §7a and the threat model. Data flows only into the most locked-down program.
- **"No / decide later."** The lockbox cannot run, so there is no promotion in C2.

**Q3. The lockbox period (June 2025 to August 2026) had already ended when the rules were frozen, and its prices are public. What should happen?**
- **"Keep it as a held-back historical check (Recommended)."** The amendment adds a Constitution sentence: "future" means later than confirmation and held back from research. You give up any claim that this is a fresh test: it can catch over-fitting to confirmation, but not strategies shaped by public 2025–26 prices. Later paper trading counts as fresh only under its own rules, fixed in advance.
- **"Use a truly future window."**
  - About 7 months fits the current timing rules only if the pick happens at day 180, with no spare days, and it is a weaker test.
  - Otherwise the pick timing or the 75-day rule must change.
  - 15 months means extending the cycle to at least about 497 days.
  - Every version needs amendments.
- **"Decide later."** The lockbox cannot run until this is decided.

## Remaining and unauthorized

**Remaining:**
- the R19-2 re-check of revision 3;
- owner Q1–Q3;
- D-12;
- the lockbox rows of D-20 (seed source, identity, generator, ψ vectors, start state of the baseline run);
- D11-15 in the S4 draft;
- the §16 review of `lockbox_eval`;
- the owner's signed §4 commit.

**Unauthorized:** editing frozen files, activation, code, simulation, confirmation or lockbox access, promotion, deployment, trading.

**Not checked:** that the registry stores the nominee's model seed and trial-code bytes, as §4 items 1–2 assume. p = 7 days is an assumption. Coverage remains unestablished.
