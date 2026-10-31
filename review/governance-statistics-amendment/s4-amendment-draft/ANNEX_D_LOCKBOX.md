# Annex D: the lockbox (D-11, D-12, D-20, R-14a), consolidated

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority.

**Status: DRAFT, IN PROGRESS, UNREVIEWED.** Part 1 (§D-1) is written. Parts 2-3 (§D-2, §D-3) are to follow. Nothing here binds until the owner signs the C2 §4 amendment after the required human review. This annex invents no rule. Each row restates a decided rule, cites its source, and marks any wording the AI chose as `[AI wording]`. Where the sources disagree, the later owner decision governs and the difference is noted.

**Sources and precedence.** A later item governs an earlier one where they differ:

| Order | Source | What it decides |
|---|---|---|
| 1 | `d11-proposal/OWNER_DECISION_D11.md` on `PROPOSAL_REV2.md` §2-3 with `PROPOSAL_REV3.md` §2, §4, §7 | the prediction distribution and the pass rule L-1..L-4; the read and execution contract; the historical window |
| 2 | `d12-proposal/OWNER_DECISION_D12.md` on `PROPOSAL_REV7.md` §3 (P-1..P-8) | attestation fields; technical FAIL; cooling-off; cap; publisher |
| 3 | `d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md` on `PROPOSAL_REV3.md`..`PROPOSAL_REV8.md` (read side) and `OPTION_C_PROPOSAL_REV2.md`..`_REV5.md` | the bindings, release on request, Q2-Q5, Q7, QC1-QC3 |
| 4 | `r14-exception/OWNER_DECISION_R14A.md` on `PROPOSAL_REV2.md` + `_REV3.md` | where the lockbox and confirmation code live |

---

## §D-1 The prediction distribution and the pass rule (D-11, Route A)

### D-1.1 Window and length

- `L0 = 2025-06-01T00:00Z`, `L1 = 2026-09-01T00:00Z`. (D-11 rev 2 §2)
- `m = 457` scheduled complete UTC days. This reads l.85's "decision-count" as one decision per day (l.209). It is fixed before any read. (rev 2 §2; decided, D-11 "Recorded meaning")
- **The window is a historical held-back check, not a fresh test.** Its prices are public, so it cannot detect strategies shaped by them. Fresh evidence comes only from later paper trading under its own rules, fixed in advance. (D-11 Q3) The Constitution §0 reading that this needs is a row of DRAFT §1.

### D-1.2 The source and the statistic

- **Source.** The nominee's BTC baseline 1x run over `[w0, w1)`:
  - both legs go through `daily_net_returns` and are aligned by `paired_daily_returns`;
  - `d_t = c_t − b_t`;
  - `n = (w1 − w0) / 1 day`.

  (rev 2 §2) The run itself, including its start state and final hour, is §D-3 (D-20 A6; Q2).
- **Statistic.** `T = difference_series_sharpe.scaled = √365 · mean(d) / sd(d)`, with the `n − 1` divisor (E-DIFF). (rev 2 §2; D-11 Q1, Route A)

### D-1.3 Block length

`b = block_length(ψ)`, where ψ is the Sharpe influence process of `d`:

`ψ_t = u_t − (S/2)(u_t² − 1)`

Here `u` is `d` standardised with the population scale, and `S` is the sample daily Sharpe of `d`. This follows the Task 12 convention, applied to one series. (rev 2 §3)

**Disclosed limit:** PPW chooses `b` for the long-run variance of a mean. It does not establish coverage for a selected nominee's predictive quantile at horizon `m ≠ n` (`UNVERIFIED_EXTERNAL_ASSUMPTION`). (rev 2 §3)

### D-1.4 Resampling and the quantile

- **Stationary bootstrap, 2,000 attempts.** Each attempt draws `m = 457` indices over `0..n−1`: restart with probability `1/b`, otherwise step forward modulo `n`. The attempt's path is `d` at those indices, and `T*_r` is the statistic of that path. (rev 2 §2; D-11 "Recorded meaning")

  The generator and its stream are §D-3 (D-20 A4).
- **Quantile.** `q = type_seven_quantile(T*_0 .. T*_1999, 0.05)`. (rev 2 §2)
- **Numerics.** The float64 output of the reference code decides L-1 and L-2, including sign residues. (rev 3 §2; adopted by D-11, "Recorded meaning")

### D-1.5 The pass rule

| Gate | PASS iff | Source |
|---|---|---|
| L-1 | `T_L ≥ q` | rev 2 §2 |
| L-2 | `T_L > 0` (the same statistic as L-1) | rev 2 §2 |
| L-3 | `max_drawdown(cand) − max_drawdown(bench) ≤ 0.05` on the BTC lockbox runs over `[L0, L1)`, hourly segments | rev 2 §2 |
| L-4 | Annex C C-3 holds on the ETH lockbox 1x run: E-IMPROV > 0 and DD(ETH) | rev 2 §2 |

`T_L` is E-DIFF of the BTC lockbox legs' daily `d` over `[L0, L1)`.

### D-1.6 Availability (fail-closed; UNAVAILABLE never passes)

From rev 2 §2:

1. **Source days.** The timestamps are exactly `w0 + k` days for `k = 0..n−1`. Candidate and benchmark identities, asset and cost string match, and `n ≥ 16`.
2. **Source E-DIFF.** `difference_series_sharpe.reason` is None. The test is this field, not the aggregate `.reason`.
3. **Block length.** `1 ≤ b ≤ n`.
4. **Attempts.** All 2,000 attempts are run in order, and every `T*_r` is available and finite. Nothing is omitted, replaced or extended. `q` is finite.
5. **Lockbox days.** The timestamps are exactly `L0 + k` days for `k = 0..456`: 457 days and 10,968 hourly segments for both legs. A shorter path is UNAVAILABLE. `T_L` comes from the `d`-field and is available.
6. **L-3.** Both BTC legs' `max_drawdown` values are finite.
7. **L-4.** The ETH timestamps pass the same checks, and both leg Sharpes are available (`paired_sharpe_improvement` not None, aggregate reason None).

A gate that is UNAVAILABLE fails. How that failure is labelled is §D-2 (D-12 P-3).

### D-1.7 Reads, budget and sealing

- **One read per family.** Each family's read:
  - consumes that family's lockbox budget;
  - is logged;
  - has its own evaluation ID;
  - leaves the segment EXPOSED.

  Release to confirmation happens only between cycles (§7 l.81-83). The two reads are at least 30 days apart (DRAFT l.243). (rev 3 §7)
- **Sealing before the first read.** Each declared family's terminal pre-lockbox status is sealed and recorded as exactly one of these (rev 3 §7; D-11 "Recorded meaning"):
  - (a) a fixed nominee that is ELIGIBLE, with a valid sealed prediction artifact;
  - (b) no nominee (`UNAVAILABLE`, Annex A P18-3);
  - (c) a nominee that is not ELIGIBLE;
  - (d) a nominee whose gates or prediction artifact are `UNAVAILABLE`.

  Where both (c) and (d) apply, (d) governs. Only (a) requests a read, and one family's status never blocks the other.

### D-1.8 Access and execution (needs the DRAFT §1 rows for Constitution §7a and the threat model)

`lockbox_eval` may read BTC and ETH 1h bars over `[S_pre, L1)`, with `S_pre = 2022-11-13T00:00Z`. It reads them read-only, under the cycle's data-manifest hash, and runs the registered strategy itself. (D-11 Q2; rev 3 §4 item 4)

1. **Inputs handed over: identifiers only.** These are the cycle-record hash, the declaration hash, `trial_id`, the hypothesis hash, the configuration hash, and the sealed prediction artifact. No confirmation per-bar output and no fitted model crosses identities. (rev 3 §4 item 1) The artifact's fields are §D-3 (D-20 A7).
2. **Immutable lookup and verification before any lockbox byte is read.** This covers the hypothesis record, the trial code and configuration, the nominee's model seed, the engine and backtester code at the bound commit, and the data-manifest hash. Every hash must match.
   - On a mismatch, no lockbox data is read, the segment is not EXPOSED, and the result is a technical failure with no retry in C2.

   (rev 3 §4 items 2-3) The artifact identity and retrieval path are §D-3 (D-20 A2/A3, D11R3-S-1).
3. **Warm-up.** EMA, EWMA and benchmark-volatility state start at `S_pre`, with the feature factory's own convention. (rev 3 §4 item 4)
4. **Fits.** `lockbox_eval` refits the nominee itself, with the nominee's estimator seed (§D-3; D-20 Q5):
   - at `r_k = L0 + 30k` days, `k = 0..15`;
   - each trained on `[r_k − 24 months, r_k)`, with labels purged at `r_k`.

   No confirmation-fitted model is used, and rule-based nominees skip fitting. (rev 3 §4 item 5)
5. **Start state: both legs flat at L0, for BTC and ETH.** Exposure 0, no pending order, an unset clock, a fresh overlay, equity 1.0, and MDD measured from L0. **Each leg pays its entry cost at its first permitted entry.** (D-11 Q2; D-20 Q2(i), D20L-42) This corrects rev 3 §4 item 6's "both legs pay their entry cost at L0", which D20L-42 found inherited and wrong.
6. **Outputs.** Research receives PASS/FAIL only (§7 l.79). The attestation and the human approver are covered in §D-2. Every other output stays under the `lockbox_eval` identity. (rev 3 §4 item 7, as decided by D-12)

### D-1.9 Not decided here

D11-15 (whether day 255 or the 75-day window governs) is carried by D-11 to the S4 draft, and §D-2 records how D-12 and D-20 read it. The §16 review of `lockbox_eval` is still required.
