# D-19 recommendation by the statistics agent (non-binding)

Date: 2026-10-02. Requested by the owner (asked for an agent to answer D-19;
told the decision is the owner's, chose "Statistics agent (Recommended)" for
a non-binding recommendation).

- Agent: project agent `senior-statistical-governance`, launched by Claude
  Opus 5.5 in a Claude Code session; it reports itself as Claude Fable 5.1
  (`claude-fable-5-1`), not independently verified. Read-only on `main` at
  `7f86530`; 106,952 tokens, 23 tool uses.
- Prompt: options A, B, C and the B-then-C combination as shown to the owner,
  the owner's constraints (not a statistician, cannot share the work,
  trades own capital), and the illustrative simulation now committed as
  `illustrative_simulation.py` beside this file.
- Findings: R19-1, R19-2, R19-4, R19-8 BLOCKER; R19-3, R19-5, R19-6, R19-7,
  R19-10, R19-11, R19-13 NON-BLOCKING; R19-9, R19-12, R19-14 QUESTION.
  Verdict KEEP_BLOCKED. Nothing is decided by this record.

Below is the agent's final report, verbatim.

---

# D-19 recommendation: what "DSR score >= 0.95" should claim (NON-BINDING)

**Reviewer:** Claude Fable 5.1, model ID `claude-fable-5-1`. This is taken from my session's system context and was not independently verified. I worked read-only on `main` at `7f86530c6c164f48b4348a0ca03c16e2ce941b0c`, with a clean tree. I wrote, staged and committed nothing. This record closes no D-row and accepts or activates nothing. D-19's authority is `OWNER` then `STAT`, then §4 (`HUMAN_DECISION_MATRIX.md:66`).

## 1. The options in plain words

The rule is this: the best of the trials, after a penalty for how many trials were run, must score at least 0.95.

**What the number actually means.** I checked this by calculation, under a textbook model where the trials' Sharpe estimates are normal and their spread is known (R19-5). In that model, a winner that has no real edge passes:
- about **1 time in 600** if the 81 trials are unrelated;
- up to **1 time in 20** if the trials are nearly identical.

So 0.95 is **not** "95% sure the edge is real". In ideal conditions it is a strict screen. Real data can weaken it. If the true uncertainty of the Sharpe estimate is about twice what the formula assumes, a no-edge winner passes more than 1 time in 20.

| | Claim attached to "≥ 0.95" | Research cycle | Task 29 forward paper | Real money |
|---|---|---|---|---|
| **A** keep deferring | None. DSR stays a diagnostic only. | No governed trials at all. This is stricter than "can only report NO_EDGE_FOUND": no cycle runs, so no outcome is produced (R19-11). | Waits, unless you decide otherwise (R19-12). | No |
| **B** strict screen | A pass means only that the test, after the penalty for all lifetime trials, failed to show the extra Sharpe is zero (R19-3). | Removes the DSR barrier only. A cycle still needs about eight other decisions, and it would be **C2, not C1** (R19-4). | Possible once a cycle yields a candidate. | B alone would also open promotion, which contradicts your own 2026-09-15 decision (R19-1). |
| **C** calibrate first | A pass carries a measured "how often a no-edge winner passes" rate, for the conditions that were simulated. | Waits for the simulation to be built, run and reviewed. | Waits | Only after C, the lockbox and the attestation |

**What B would most likely produce.** With about 3.4 years of data and 81 trials, the strategy's Sharpe advantage over the benchmark must reach about **2.2 per year** to pass. My estimates of the chance of passing (R19-6):
- a true advantage of 1.0: about 1%;
- a true advantage of 2.0: about 34%.

**NO_EDGE_FOUND is the expected result under B.** B gives an honest answer. It is not a shortcut to trading.

## 2. Recommendation

**The combination, with three changes:**
1. Word B to match Constitution §1 line 29: a screen, not a probability (wording below).
2. Run C **before any lockbox request**, not merely "before real money". A lockbox read cannot be undone. Each one uses up budget and permanently exposes data (§7 lines 77, 81, 85). Only 2 reads are allowed per family per cycle (protocol line 74).
3. Fix C's pass rule in writing before any cycle result, for example "false-pass rate ≤ 5% in every preregistered scenario". Otherwise the success criterion would be set after results, which §1 line 31 forbids.

**Reasons:**
- Under the combination your capital is never exposed by B, because promotion still needs C, the lockbox and the attestation.
- B's claim is honest if it is worded as a screen.
- A wastes nothing scientifically, but produces nothing.

**Risks:**
- No statistician reviews any of this (R19-2).
- C's answer depends on which no-edge scenarios are chosen, and nobody independent checks that choice (R19-14).
- B is only worth doing if the other blocking rows are also decided (R19-4).

**I would change to A if:**
- you do not want to set aside your 2026-09-15 and 2026-09-18 decisions; or
- you do not intend to decide D-05, D-06, D-11, D-14 and D-15 (then B unblocks nothing that can actually run); or
- the R19-9 check shows the Sharpe uncertainty is understated by about 2× or more.

**I would oppose B alone** for anything that leads to promotion.

**Does B contradict a frozen clause?** Not directly:
- B keeps 0.95 (protocol lines 231 and 287).
- Using the raw lifetime count is consistent with Constitution §9 line 106 and §5 line 67.
- The eigenvalue line (protocol line 232) is D-16's question, not D-19's.

But B does conflict with records that are not frozen, and it needs §4 in any case:
- Astra B1 (`ASTRA_REVIEW.md:13–14`, "requires calibration") is met only through the combination.
- Astra B3 (lines 18–21) is met only if B arrives in an amendment that makes DSR active.
- Astra B2 (lines 15–17, behaviour for very small trial counts) must be settled in the same amendment.
- Your own decisions of 2026-09-15 and 2026-09-18 must be explicitly set aside (R19-1).

**Possible §4 wording. This is an AI proposal only, not authored or accepted; you may author it, change it, or reject it.**
> `dsr.interpretation`: "A DSR of at least 0.95 is a screening rule. A pass means only that, after deflating for the family's lifetime count of trial attempts under the method's stated assumptions, the test failed to falsify a non-positive incremental Sharpe (Constitution §1 line 29). It is not a probability that an edge exists. It is not a calibrated error rate. It is not evidence that live trading is appropriate."
> `dsr.calibration_before_lockbox`: "No lockbox request may be made unless a calibration, preregistered before the first trial of the cycle, shows a selected-winner false-pass rate of at most [owner sets, e.g. 0.05] in every preregistered no-edge scenario. If it fails, the cycle cannot end CANDIDATE_PROMOTED. Any change to the threshold applies only to a later cycle."

The same amendment must also:
- bind D-16, D-17 and D-18, plus the small-trial-count rules (B2) and the reason codes (P-7);
- set aside the 2026-09-15 and 2026-09-18 owner records in writing;
- terminate C1 (§4 line 48).

## 3. Order of decisions

Yes, D-16 to D-19 must be decided together, in one amendment. The suggested order:

0. **Process first.** Decide whether you supersede your 2026-09-15 and 2026-09-18 records, and what replaces `STAT` (R19-1, R19-2).
1. **D-16 and D-17 together.** Each depends on the other (P-9).
2. **D-18, the selection event.** DSR's penalty is built around the highest-Sharpe trial, and the trial with the highest Sharpe need not have the highest DSR score (DEC-02, `DSR_CALIBRATION_RECONCILIATION.md:36–46`).
   - In the same step: B2, P-7, and the R19-9 question about how many observations count as the sample.
3. **D-19 last.** Its claim refers to the count and the selection event fixed above. If you take the combination, freeze C's preregistration in the same step.
4. **The other gate rows**, before any cycle that is meant to produce a candidate.

## 4. Findings

- **R19-1 BLOCKER.** Option B conflicts with two of your own standing decisions:
  - `OWNER_DECISION.md:13–15`: promotion stays blocked until DSR is "independently calibrated, reviewed, and accepted".
  - `OWNER_DSR_DEFER_DECISION.md:14–18, 22–24`: reconsideration needs independent numerical references and "human/statistician acceptance".

  Neither is frozen, so you may set them aside, but only explicitly. The combination conflicts only with the research-stage consequences in the 2026-09-18 record.
- **R19-2 BLOCKER.** `STAT` cannot be obtained under your constraints. The requirement comes from the decision matrix (lines 12 and 63–66) and from your own records. It does **not** come from frozen text: searching `docs/`, `protocols/`, `specs/` and `schemas/` for "statistician" found nothing. You must decide what replaces it, and record that a safeguard was lost.
- **R19-3 NON-BLOCKING.** B's phrase "credibly above zero" says more than Constitution §1 line 29 allows ("failure to falsify under the tests actually run"). `METHOD_CANDIDATE.md:100–101` already disclaims any error-rate claim.
- **R19-4 BLOCKER (how the decision was framed).** "B unblocks C1" is wrong on two counts:
  - **The cycle would be C2, not C1.** Binding the method is a §4 amendment, and an amendment ends the cycle (§4 line 48; §5 line 59), as `DRAFT_AMENDMENT_PROPOSAL.md:34–35` already says.
  - **D-19 is not the only blocker.** These rows are still marked BLOCKING in the matrix:

    | Row | Matrix line |
    |---|---|
    | D-05 | 37 |
    | D-06 | 38 |
    | D-11 | 48 |
    | D-14 | 56 |
    | D-15 | 57 |
    | D-18 | 65 |

  This wording is **not new**. It was inherited from committed records: `RESUME_2026-10-02B.md:20–23`, `ROADMAP_2_OWNER_ANSWERS.md:37–38` and P-10 (`PROPOSAL_PACKET.md:207`). Correcting it is your decision.
- **R19-5 NON-BLOCKING (my calculation).** False-pass rate of the selected winner, N = 81, textbook model, with √V replaced by its expected value and ρ the correlation between trials:

  | Condition | False-pass rate |
  |---|---|
  | ρ = 0 (unrelated trials) | 0.17% |
  | ρ = 0.3 | 0.77% |
  | ρ = 0.6 | 2.25% |
  | ρ = 0.9 | 4.25% |
  | ρ → 1 (identical trials) | about 5% |
  | ρ = 0, uncertainty understated 2.0× | 4.15% |
  | ρ = 0, uncertainty understated 2.2× | 5.36% |

  The ρ = 0 result matches the closed form 1 − Φ(A+1.645)^81. The ρ → 1 limit matches a single 5% test.
  - Not valid for a small number of usable trials, where V is very noisy.
  - Negative correlation was not covered.
- **R19-6 NON-BLOCKING (my calculation).** Pass threshold, as a yearly Sharpe advantage:

  | N | Threshold |
  |---|---|
  | 27 | 1.99 |
  | 81 | 2.22 |
  | 243 | 2.43 |

  This reproduces the proposal's 2.22. Approximate chance of passing, ignoring selection and noise in V:

  | True advantage | Chance of passing |
  |---|---|
  | 1.0 | 1.2% |
  | 1.2 | 3% |
  | 2.0 | 34% |
  | 2.5 | 70% |

- **R19-7 NON-BLOCKING.** The illustrative simulation shown to you was checked only partly; it could not be fully reproduced.
  - The single-trial value matched exactly: 0.9954 (0.995 shown).
  - At N = 81, assuming expected V, I get 0.559 and 0.899 (0.488 and 0.913 shown). The implied √V differs by +7.3% and −3.5%. That is within the roughly 7.9% sampling spread expected from 81 trials, so the values are consistent but not reproduced.
  - Wrong methods give clearly different answers: √252 annualisation gives 0.751, and the √(2 ln N) penalty gives 0.360.
  - 0 passes out of 300 is consistent with an expected 0.5.
  - **The simulation's code and seed are not committed** (no match for "0.488" on `main`). If it is cited, it must first be committed.
- **R19-8 BLOCKER (for the combination as originally worded).** "C before real money" comes after the lockbox, which cannot be undone (§7 lines 77, 81, 85; protocol line 74). C must come before any lockbox request.
- **R19-9 QUESTION.** DSR uses sqrt(T−1) over daily rows, but holding horizons are 24, 72 and 168 hours (protocol line 109). Constitution §23 line 182 says "Bar count is never sample size", and protocol lines 243–244 use an effective-sample-size measure (ESS). Should DSR use ESS? Understated uncertainty is the main way the screen fails (R19-5). I did not establish whether the series is serially correlated.
- **R19-10 NON-BLOCKING.** B's claim is undefined at N = 1, K = 1, with missing Sharpes, or with zero spread across trials (Astra B2). It must be bound together with P-3 and P-7.
- **R19-11 NON-BLOCKING.** Option A's description is inaccurate. Governed trials are blocked (`OWNER_DSR_DEFER_DECISION.md:17–18`), so no cycle outcome, NO_EDGE_FOUND included, is produced.
- **R19-12 QUESTION.** Could Task 29 paper-trade the deployable baseline `VOL_TARGET_BUY_AND_HOLD` (protocol line 132; Constitution §11 lines 114–116) under any option? That is your call. In Q-C you chose to wait for research. I did not establish whether the baseline requires a NO_EDGE_FOUND cycle outcome first.
- **R19-13 NON-BLOCKING.** The D-19 row's evidence column (matrix line 66) omits Constitution §1 line 29 and `OWNER_DECISION.md:13–15`. `M6` correctly points to `external-review-packet/README.md:184`. The matrix is committed and hash-covered, so correcting it is your decision.
- **R19-14 QUESTION.** Without a statistician, C's design (which no-edge scenarios, how correlated, fat tails, antithetic trials) can only be reviewed by AI plus you.
  - The existing drafts conflict (DEC-01, and DEC-03 at reconciliation lines 50–57).
  - D-18 must name the selection event before C can be designed (line 46).
  - Opposite-signed columns are plausible (inherited from P-4, which I did not verify).

## 5. Verdict

**KEEP_BLOCKED.** I recommend the combination with the R19-3 and R19-8 changes, through one amendment that you author and sign.

**Your decisions:**
- R19-1 and R19-2;
- A, B, C or the combination;
- the C pass threshold;
- the R19-4 and R19-13 corrections.

**Still not authorized:** frozen edits, amendment authorship, a calibration engine or simulation, Task 13, Task 29, governed trials, confirmation or lockbox access, promotion, deployment, trading. AI review does not replace the §16 different-model plus human review for later protected code. §16 does not apply here, because no code changed.

## 6. What I read and ran

**Verification protocol items applied:**
- **1:** searched the frozen texts by topic. This found §1 line 29, §4 line 48, §7, §23, and no mention of "statistician".
- **2, 4, 5, 6, 11, 12, 13, 14:** applied.
- **3:** not applicable, because I claim no hashes.
- **7:** not applicable, because no verifier was run.
- **8:** probabilities were computed in floating point with the standard library's `NormalDist` and Simpson quadrature. The quadrature was checked against the closed form; no exact-arithmetic identity is claimed.
- **10:** not applicable, because nothing was written.

**Commands:**
- `git rev-parse`, `git status`, `git ls-files --eol`, `git show origin/docs/d16-d17-proposal:…/PROPOSAL_PACKET.md`;
- `grep`, `sed` and `cat` over the files below;
- two Python heredocs that wrote nothing.

**Files (repository root `D:\PMP-programs-for-sharawi\autonomous-quant-trader\`):**
- `AGENTS.md`
- `.agents\skills\{statistical-binding-review,scientific-reproducibility-review,task-gate-review}\SKILL.md`
- `docs\RESEARCH_CONSTITUTION.md`
- `protocols\protocol_v1.yaml`
- `review\governance-statistics-amendment\{OWNER_DECISION,OWNER_DSR_DEFER_DECISION,ASTRA_REVIEW,DSR_CALIBRATION_RECONCILIATION,DRAFT_AMENDMENT_PROPOSAL}.md`
- `…\v1.1-method-candidate\{HUMAN_DECISION_MATRIX,METHOD_CANDIDATE}.md`
- `…\external-review-packet\README.md`
- `review\handoff\RESUME_2026-10-02B.md`
- `review\roadmap\{ROADMAP_2_OWNER_ANSWERS,ROADMAP_2_PROPOSAL}.md`
- branch `docs/d16-d17-proposal`: `PROPOSAL_PACKET.md` (I read the file list, but not `NUMBERS_CHECK.md`'s content)
