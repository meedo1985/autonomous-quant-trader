# D-11 decision proposal (senior-statistical-governance agent)

Requested by Claude Opus 5.5, 2026-10-25, after the owner asked to work ahead of certify. Agent `senior-statistical-governance`, read-only, working under `.agents/skills/statistical-binding-review/SKILL.md`, on checkout `aqt-freeze-sheet` at `421737f`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). The report follows verbatim, with only the harness's indentation removed.

---

# D-11 decision proposal: lockbox prediction distribution and pass rule (L-1..L-4)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, as reported by the session metadata. I am an AI reviewer, not an authority. This is a proposal: it does not accept, sign or activate anything.
**Checkout:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`, HEAD `421737f`; the working tree was clean before and after.
**Mode:** read-only. No file was edited and nothing was staged or committed. No simulation was run. There was no confirmation, lockbox, network or credential access.
**VERDICT:** `BINDING_CANDIDATE` for **Route A** (below), as a reading of the frozen text. It is complete only once owner questions Q2 and Q3 are answered. Route B is `AMENDMENT_REQUIRED`. Keeping D-11 blocked (Route D) stays a valid choice.

## 1. Authority and status

| Item | Status | Source |
|---|---|---|
| Lockbox construction, tail, pass rule | FROZEN v1.0 | `protocols/protocol_v1.yaml` l.83–92 |
| Bootstrap type, PW blocks, 2,000 iterations | FROZEN | l.223–226 |
| Lockbox cost multiplier 1.0; PASS_FAIL_ONLY; cooldown | FROZEN; the draft keeps them "in force" | l.75–76, l.80–82; DRAFT_WORDING §4 |
| Coarse attestation fields | FROZEN; open as D-12 | l.77–79 |
| Lockbox partition [2025-06-01, 2026-09-01) | FROZEN; C2 keeps it | l.67; DRAFT §2.1 ("keys unchanged") |
| Only lockbox_eval reads the lockbox; confirmation reachable only through the experiment engine | FROZEN | Constitution §7 l.73–85; §7a l.90, l.94 |
| E-IMPROV and E-DIFF registered as separate measures | OWNER-DECIDED D-01 | `d02-d04-proposal/OWNER_DECISION_D01_D04.md` |
| L-4 (ETH sanity on the lockbox) = C-3 with E-IMPROV, "subject to D-11" | OWNER-DECIDED D-02 | same file, l.42–44 |
| DSR and nomination use E-DIFF | OWNER-DECIDED D-18 | DRAFT §2.4 |
| Two AI reviews plus the owner replace the statistician (`STAT`) | OWNER-DECIDED R19-2; disclosed as weaker | `d19-recommendation/OWNER_STEP0_DECISION.md` |
| D-20 lockbox code bindings | OPEN; R-8: "No lockbox clause is bound here" | DRAFT l.147; `OWNER_DECISION_D20_D13.md` effect 1 |
| `LOCKBOX_PREDICTION_PROPOSAL.md` | UNACCEPTED AI proposal | its status line |
| D-11 (L-1..L-4), D-12 | OPEN | DRAFT l.308–311, l.337–339 |

## 2. Definitions (Route A, proposed)

| Symbol | Definition |
|---|---|
| Window | `[L0, L1)`: `L0` = 2025-06-01T00:00Z, `L1` = 2026-09-01T00:00Z. A day is a complete UTC day. |
| `m` | The number of scheduled complete UTC days in `[L0, L1)`: **457** (exact). It is fixed from the protocol text before any lockbox read. It is the l.85 "decision-count" under the decided one-decision-per-day reading (C-11 item 1, from N-1; l.209). It is not a count of hours, trades, effective decisions or observed valid days. |
| Source | The nominee's BTC daily paired series, at 1x cost, on the eligible confirmation window `[w0, w1)`: `d_t = c_t − b_t`, where `b` is the VOL_TARGET_BUY_AND_HOLD leg (C-0). `n` = the number of days, 1247 − gap embargo days. It is not known before declaration. |
| Resampling | A stationary bootstrap of `d`. One index sequence of length `m` over source positions `0..n−1`: each step restarts with probability `1/b`, otherwise it advances modulo `n`. Exact identity: applying the same indices to the pairs `(c, b)` and then differencing gives exactly `d_{i_t}`. Under E-DIFF, "joint-leg" and "difference-series" resampling are therefore the same, and the source-representation question disappears. |
| Block length `b` | `block_length` (PPW-2009, the Task 12 convention) on `d` itself, the literal l.85 reading [AI default]. The alternative input, the Sharpe influence process of `d`, is a sub-choice for D-20. |
| Statistic | `T = sqrt(365)·mean(d)/sd(d)`, with n−1 variance: **E-DIFF** (`difference_series_sharpe` in `paired_sharpe_statistics`). The same function is used for each bootstrap path and for the actual lockbox path. |
| Distribution | Exactly 2,000 attempts, indexed 0..1999. Any invalid replicate makes the result UNAVAILABLE. No recentring. `q` = `type_seven_quantile(values, 0.05)`; the reference float64 result decides (see D11-2). |
| L-1 | PASS iff the lockbox `T ≥ q`. |
| L-2 | PASS iff the lockbox `T > 0`. It is the same statistic, because l.91 uses "delta-Sharpe" twice in one sentence. |
| L-3 | PASS iff `DD(BTC)` holds, with C-0's "window" replaced by `[L0, L1)`. That is `max_drawdown` on each leg's lockbox BacktestResult (the hourly segment path). |
| L-4 | PASS iff C-3 holds on the ETH lockbox run at 1x: ETH E-IMPROV > 0 AND `DD(ETH)` (D-02). |
| Availability | Every day must pass the `daily_net_returns` integrity rule: 24 contiguous accepted segments. Any missing, irregular or non-finite day, or zero variance, makes the result UNAVAILABLE, and UNAVAILABLE cannot pass. A failed read is a NO_RESULT cause (DRAFT l.325–326). |
| Identity boundary | The experiment engine computes `q` after eligibility and before `lockbox_request`, and seals it by hash in the eligibility record. lockbox_eval receives only the sealed artifact, plus the handover in Q2. Research receives PASS/FAIL only. |

## 3. Consumer matrix

| Consumer | Frozen wording | Required statistic | Status / missing decision |
|---|---|---|---|
| l.84–86 construction | "bootstrap … paired-difference series … delta-Sharpe per path" | E-DIFF can be computed from it; E-IMPROV cannot | D-11 (Route A, or an amendment for Route B) |
| l.87–89 tail | one-sided lower 5th percentile | type-7 at 0.05 | D-11; quantile rule and numerics (D11-2) |
| l.91 L-1 | lockbox delta-Sharpe ≥ 5th percentile | the same estimand as the paths | D-11 |
| l.91 L-2 | BTC delta-Sharpe > 0 | the same token, in the same sentence | D-11 |
| l.91 L-3 | the drawdown constraint holds (l.276–278, O-7) | DD on `[L0, L1)` | D-11 window referent (D11-11); D-20 code |
| l.91 L-4 | ETH sanity must also pass (l.42–43, l.279) | E-IMPROV (D-02) | decided by D-02; D-11 applies it |
| l.77–79 coarse fields | sign, drawdown held, prediction decay | follow L-2, L-3, L-1 | D-12 (not decided here) |
| l.80–82 cost | 1.0 | both legs at 1x | settled |
| l.223–226 bootstrap | stationary, PW, 2,000 | as above | settled; the stream identity is D-20 |
| l.67 partition | lockbox dates | fixes m = 457 | settled |
| l.93–95 | net-return rule REMOVED (de-risker) | — | tension under Route A (D11-10) |
| l.294–296 | lockbox only after eligibility | — | settled |

## 4. Identifiability

- Under Route A, everything can be computed from data that lockbox_eval and the experiment engine already hold.
- E-IMPROV cannot be identified from a difference series (`TECHNICAL_APPENDIX.md` §2 Example A; §7 l.268–281). Route B therefore needs both legs, which changes an input.
- L-3 and L-4 need both legs on the lockbox under any route, so lockbox_eval runs both legs either way.

## 5. Dependence and selection

- Serial dependence is handled only by the PW blocks.
- The source is the **selected** nominee, the family maximum of E-DIFF Sharpe (P18-4). The centre of the distribution is therefore biased upward by construction, and the frozen text says not to recentre.
- The plug-in leaves out the source's own estimation error (D11-3).
- The two families' reads share the same window and the same benchmark path, so they are correlated (D11-9).
- The lockbox prices are already public (D11-5).
- There is no retry or adaptive reseeding: a FAIL is final for the cycle (Constitution §7 l.85).

## 6. Exact calculations (independent; checked against the repository code by import only, with no repository writes)

**Lengths.** `m` = (2026-09-01 − 2025-06-01) = **457** days. The confirmation partition is 1247 days.

**Type-7 position.** `1999·(1/20) = 1999/20 = 99.95`, so `j = 99` and the fraction is `19/20`. That gives `q = (1/20)·y[99] + (19/20)·y[100]`.

**Worked boundary, positive case.** With `y[99] = 0.30` and `y[100] = 0.32`, `q = 319/1000` exactly.
- A lockbox `T = 0.319` passes L-1 (≥) and passes L-2.
- Discriminating check: type 6 gives `301/1000` and nearest-rank gives `0.30`. So `T = 0.31` passes under type 6 or nearest-rank but **fails** under type 7. The quantile rule decides the boundary.

**Float64 versus exact.** The repository's `type_seven_quantile` returns `0.31900000000000006`, while the proposal's closed form `0.05*y[99]+0.95*y[100]` returns `0.319`. So `T = 0.319` passes under the closed form and **fails** under the reference code (D11-2).

**Worked boundary, negative case.** With `y[99] = −0.42` and `y[100] = −0.40`, `q = −401/1000`.
- `T = −0.401` passes L-1 but fails L-2.
- `T = 0` exactly fails L-2, because the inequality is strict.
- When `q < 0`, L-2 is the binding condition.

**The two measures can disagree on the same lockbox data.** Take `c = (0.012, 0.004, 0.012, 0.004)` and `b = (0.03, −0.01, 0.03, −0.01)`.
- Exact squared Sharpes: `S(c)² = 3`, `S(b)² = 3/16`, `S(d)² = 3/256`, with `mean(d) = −1/500`.
- E-IMPROV = `(3/4)√1095 ≈ +24.818`; E-DIFF = `−√1095/16 ≈ −2.068`. The repository code agrees to the last digits.
- So L-2 passes under E-IMPROV and fails under E-DIFF.
- In general, `sign(E-DIFF) = sign(mean d)` whenever `sd(d) > 0`.

**Approximate coverage.** Assumptions: iid, stationary, an unselected nominee, and equal per-day asymptotic variance in source and target. The plug-in width is then `√(n/(n+m))` of the correct predictive width.
- For `n = 1247` (ratio `1247/1704`): a false-fail rate ≈ **0.080**, not 0.05.
- For `n = 1100`: ≈ 0.083.
- The asymptotic variance form of the Sharpe ratio is an `UNVERIFIED_EXTERNAL_ASSUMPTION`; only the ratio is used.

**Approximate power, same assumptions.** The standard deviation of the annualised T over 457 days is ≈ 0.894. A no-edge nominee passes L-2 about 50% of the time; one with a true E-DIFF of 0.5 passes about 71%. The lockbox is a weak filter, as l.92 itself admits ("without pretending 15 months is … high-power").

These calculations are not calibration evidence.

## 7. Routes

| Route | What it is | Assumptions | Information needed | Governance | Falsifier | Frozen wording |
|---|---|---|---|---|---|---|
| **A** (recommended) | E-DIFF for L-1 and L-2; m = 457; PW on `d`; L-3 = DD on the lockbox; L-4 = C-3 | the bootstrap of `d` is adequate; selection bias accepted | n at declaration; the Q2 handover | fills the marker; no change of input; checks the claim that the DSR certified | a frozen or decided text making l.91 "delta-Sharpe" mean E-IMPROV | **works** (as a reading) |
| B | the existing AI proposal: joint legs, E-IMPROV | the same, plus a two-leg law | the same, plus new code | **amends l.85** (a change of input); to be listed in DRAFT §1 with a rationale | — | does not work; needs amendment wording |
| C | L-1 E-DIFF, L-2 E-IMPROV | reads one token two ways in one sentence | the same | defensible only as explicit amendment wording; the D-12 sign field becomes ambiguous | — | contested |
| D | KEEP_BLOCKED | — | — | DRAFT l.356 says every marker must be filled before signing. So either C2 cannot be signed as drafted, or it is signed with promotion impossible (NO_RESULT at best) | — | works; no promotion path |

Routes A and B both need D-20 code: an index generator with output length `m ≠ n`, a new stream purpose, a seed source and reference vectors.

## 8. Recommendation

Adopt Route A as the D-11 binding. It is the only route faithful to l.85, and it gives l.91 a single meaning. Its lockbox check tests the same E-DIFF claim that C2's DSR certifies and that nomination selects on. G-1 (E-IMPROV) already filters, before the lockbox, the exposure-tilt case that E-DIFF lets through. Owner Q2 and Q3 must be answered before the binding is complete. Changing the coverage (D11-3) or the window (Q3) is a separate amendment question.

**What D-12 needs from D-11 (not decided here):**
- `paired_delta_sharpe_sign` = the sign of the L-2 statistic;
- `drawdown_constraint_held` = L-3;
- `prediction_decay_test_passed` = L-1;
- whether L-4 appears;
- the tension between these fields and PASS_FAIL_ONLY.

**What D-20 needs:**
- the statistic function;
- the series used for the block length;
- an `m ≠ n` index generator (the current `bootstrap_indices` fixes the output length at n; the seed material already carries `output_length`);
- a new purpose (`ReplicateStream` accepts only `paired_sharpe_ci`);
- the seed source;
- `type_seven_quantile`;
- `max_drawdown` for L-3;
- an R-8 extension, refreshed vectors, and a §16 review of lockbox_eval (Constitution l.152: lockbox ACL tooling and the promotion gate).

## 9. Findings

- **D11-1, BLOCKER** (for adopting the existing proposal as a binding; inherited from `TECHNICAL_APPENDIX.md` §7, Astra B4 and `PAIRED_SHARPE_USAGE_RECORD.md`). `LOCKBOX_PREDICTION_PROPOSAL.md` l.37–58 resamples joint legs and computes E-IMPROV, which l.85 cannot identify, and it does not label itself as an amendment. Its l.77 "existing strictly positive BTC improvement" decides L-2 in advance. It is the right answer for E-IMPROV but wrong as a reading. Remedy: the owner chooses A, or chooses B as explicit amendment text.
- **D11-2, NON-BLOCKING.** The proposal's closed-form quantile (l.63–64) differs from the reference float64 exactly at the boundary (§6). The C-0 numerics rule (l.77–79) is extended only by AI default SA5-6, and Annex C does not cover the L-gates. D-11 must name `type_seven_quantile` and state the numerics rule for L-1.
- **D11-3, NON-BLOCKING** (disclosure). The plug-in prediction leaves out source error: a false-fail rate of about 8%, not 5%, before selection. This is inherent to l.84–86. The proposal (l.66–68, l.110–111) gives no magnitude. A correction would be an amendment.
- **D11-4, QUESTION.** The lockbox run's start state and its pre-lockbox history (feature warm-up, the 24-month training window, the 30-day refits) are undefined. §7a l.90 confines confirmation data to the experiment engine, and the proposal's l.83–84 says lockbox_eval gets no raw confirmation data. No record I found addresses this. It goes to owner Q2.
- **D11-5, QUESTION.** The D-18 accepted weakness (`OWNER_DECISION_D18.md` l.52–54) covers only the public 2022–2025 prices. The lockbox window ended on 2026-08-31 and its prices are public too, so declarations could be shaped by them. This cannot be verified. It goes to owner Q3.
- **D11-6, NON-BLOCKING.** Partial disagreement with `METHOD_CANDIDATE.md` §6.3 (3) and appendix §7 item 1. The mismatch between decision-count and days is settled as a reading by the decided C-11 "one decision per day", which gives m = 457.
- **D11-7, NON-BLOCKING.** A declared outage inside the lockbox window would make L-1..L-3 permanently UNAVAILABLE (NO_RESULT). Declared gaps exist in this dataset (`src/aqt/data/quality.py`). Whether the lockbox window has one cannot be determined without access, which is prohibited.
- **D11-8, NON-BLOCKING.** The DRAFT l.254 comment "existing purposes, incl. the lockbox interval (line 85)" could be read as saying a lockbox stream purpose exists. None exists in v1.0 or in the code.
- **D11-9, NON-BLOCKING.** The two families' lockbox reads share the same window and the same benchmark path, so they are correlated. The second read is of a segment already EXPOSED.
- **D11-10, NON-BLOCKING.** Under Route A, L-2 becomes a mean-return comparison, which is in tension with the l.93–95 de-risker rationale. The practical cost is small, because a nominee must already have a large positive confirmation E-DIFF to pass the DSR.
- **D11-11, NON-BLOCKING.** C-0 DD is defined "over the window", which is `[w0, w1)`. L-3 needs an explicit `[L0, L1)` substitution, and R-8 (l.147) binds `max_drawdown` only for C-0 and G-2.

## 10. Questions for the owner

**Q1. Which measure should the lockbox's main test use?**
- **"Day-by-day difference, as written (Recommended)."** The lockbox re-checks the same "beats the benchmark day by day" claim that your luck-test certifies. No rule text changes. A smoother strategy that earns less per day than the benchmark fails.
- **"Sharpe minus Sharpe, like your ETH and CI checks."** The frozen line must be rewritten in the C2 amendment, it needs new code, and it checks a claim the luck-test never certified.
- **"Keep blocked."** No strategy can be promoted in C2.

**Q2. How does the lockbox checker get the history it needs before 2025-06-01?**
- **"Sealed hand-over, start flat (Recommended)."** The experiment engine packs and fingerprints the strategy's state and the history it needs. The checker starts with no position and follows the strategy's own retraining rule.
- **"Sealed hand-over, carry the position over."**
- **"Decide later."** The lockbox cannot run until this is decided.

**Q3. The lockbox period (June 2025 to August 2026) is over and its prices are public. What should happen?**
- **"Keep it and record the weakness openly (Recommended)."** Later forward paper trading is the truly fresh test.
- **"Replace it with a later, future window."** This needs an amendment and a long wait.
- **"Decide later."**

## 11. Verification protocol items run

1. Two-way citations: done. The topic search found C-11, l.93–95, §7a, the D-18 caveat and DRAFT l.356.
2. Referents: L-4 → C-3 (ETH) is correct; R-8 checked.
3. Byte and hash claims: N/A (this proposal records no digests).
4. Discriminating checks: done (type 6, nearest-rank, and the closed form against the code).
5. Lemma sweep: the sign lemma and the tilt lemma were applied to every route.
6. Right answer versus right reason: applied in D11-1.
7. Tooling: no `python` on PATH. I used `D:\PMP-programs-for-sharawi\autonomous-quant-trader\.venv\Scripts\python.exe` (3.14.7), importing the freeze-sheet `src`, with bytecode writing disabled. No tests were run.
8. Exact arithmetic: `Fraction` throughout §6.
9. No repairs were made; every change is a proposal.
10. The 11 findings are numbered consecutively.
11. Inheritance: D11-1 and D11-6 are marked.
12. Attribution: every claim about another record is given by its lines.
13. §16 does not apply to this Markdown proposal. It does govern the later lockbox_eval code.

## 12. What I could not determine

- the real coverage and calibration of the plug-in prediction;
- `n` (the gap embargo is fixed only at declaration);
- whether the lockbox window contains outages;
- whether v1.0 intended the second family to re-read the same exposed segment;
- the precise asymptotic variance of the Sharpe ratio (`UNVERIFIED_EXTERNAL_ASSUMPTION`).

No human statistician reviewed this (R19-2).

**Remaining:** owner Q1–Q3; the two different-model AI reviews (R19-2); the D-12 and D-20 lockbox rows; the owner's signed §4 commit.

**Still unauthorized:** editing frozen files, signing or activating any binding, building lockbox_eval or the index code, simulation, confirmation or lockbox access, Task 13, promotion, deployment, trading.

I did not check D-12's PASS_FAIL_ONLY tension or the choice of seed source; both are left to their own rows.
