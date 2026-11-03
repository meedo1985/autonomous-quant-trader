# Codex Sol review of the D-11 proposal (c870152)

Prompt: `REVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a17351-e18a-7c51-a3d2-baf905164c18`, 95,794 tokens. (The report names itself `gpt-6.1-sol`; the CLI header says `gpt-6-sol`.) R19-2 review 1 of 2.

Verdict: **FIX**. Findings D11R-S-1 .. D11R-S-7.

## Report (verbatim)

# D-11 independent review

**Verdict: FIX.** Route A is the best reading of the frozen prediction construction, but the proposal is not ready for an owner decision as a complete L-1..L-4 binding. The consequential gaps are the block-length input, the confirmation-to-lockbox handover, and several statements that disagree with the proposed float64 rule.

Reviewer: Codex Sol family (`gpt-6.1-sol`, the model identified to this session). This is an independent read-only review, not acceptance or amendment authority.

## Authority and binding

| Item | Review conclusion |
| --- | --- |
| Frozen [protocol lines 83–91](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:83) | “Bootstrap the confirmation BTC paired-difference series” yields paths of \(d=c-b\). Their Sharpe is **E-DIFF**. |
| [Technical appendix Example A](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/external-review-packet/TECHNICAL_APPENDIX.md:49) | Correctly proves that \(d\) alone cannot identify **E-IMPROV**, even when benchmark Sharpe is known. Joint-leg Route B changes the frozen input and needs a §4 amendment. |
| [D-01/D-02 owner decision](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d02-d04-proposal/OWNER_DECISION_D01_D04.md:36) | Keeps the measures distinct and binds lockbox ETH sanity, L-4, to E-IMPROV, subject to D-11. It does not bind BTC L-1 or L-2. |
| [D-18](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d18-proposal/OWNER_DECISION_D18.md:44), [D-20/D-13](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-d13-proposal/OWNER_DECISION_D20_D13.md:96), [C2 draft R-8](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:147) | D-18’s selection uses E-DIFF; existing D-20 bindings expressly leave lockbox clauses open. None activates D-11. |

The proposed **457 scheduled UTC days** follows the fixed lockbox dates and the one-decision-per-day convention. It is a defensible *binding choice*, though “decision-count” in frozen line 85 does not itself say “scheduled calendar days.” Fail-closed treatment of any missing day makes that choice coherent.

| Consumer | Needed binding |
| --- | --- |
| L-1 | Lockbox BTC E-DIFF \(\geq\) the type-7 fifth percentile of 2,000 confirmation-derived, 457-day E-DIFF paths. |
| L-2 | Lockbox BTC E-DIFF \(>0\); the same “delta-Sharpe” token as L-1. |
| L-3 | BTC candidate MDD minus benchmark MDD \(\leq0.05\), on the **lockbox hourly equity paths**. |
| L-4 | ETH lockbox E-IMPROV \(>0\) and the ETH drawdown condition, at 1× cost. |
| D-12 | Must inherit the L-2 sign, L-1 decay result and L-3 drawdown result; disclosure remains unresolved against PASS_FAIL_ONLY. |
| D-20 | Must bind the new \(m\)-from-\(n\) generator, stream identity and seed, block-length method, runtime/numerics and reference vectors before implementation. |

## Findings

| ID | Severity; place | Failure scenario and minimal repair |
| --- | --- | --- |
| **D11R-S-1** | **BLOCKER**; [proposal §6](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md) | Both “equality passes” worked examples contradict the proposal’s operative float64 rule. With \(y_{99}=.30,y_{100}=.32\), `type_seven_quantile` returns **0.31900000000000006**, so `T=0.319` **fails** L-1. With \(-.42,-.40\), it returns **−0.40099999999999997**, so `T=−0.401` also **fails**. Label the rational examples as exact-arithmetic illustrations, show the operative outcomes, and demonstrate equality using `T` equal to the returned float64 quantile. |
| **D11R-S-2** | **BLOCKER**; §2 “Block length” | The frozen rule specifies Politis–White blocks, but does not choose `block_length(d)` over an influence process for **Sharpe(d)**. The accepted inactive Task 12 convention selects blocks from the statistic’s influence process. Persistent volatility can leave return autocorrelation small while dependence relevant to Sharpe remains. Choosing raw \(d\) as an “AI default” is a scientific choice, not merely a D-20 code detail. Compare and justify the admissible inputs, bind one explicitly, and carry its vectors into D-20. |
| **D11R-S-3** | **BLOCKER**; §2 identity boundary and Q2 | “Sealed state and the history it needs” does not specify what `lockbox_eval` receives or how later 24-month refits obtain pre-lockbox observations. Raw confirmation history crossing to that identity conflicts with [Constitution §7a](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:87) as presently written. Starting flat also changes the run’s position and equity boundary. Specify the exact state, training buffer, refit and benchmark rules, handover contents, verification and authorized access path; use an amendment if that path widens confirmation access. Q2’s two position choices alone cannot settle it. |
| **D11R-S-4** | **BLOCKER**; §2 “Availability” and named statistic code | “Zero variance makes the result unavailable” must name **which series**. A constant candidate leg and varying benchmark can give a valid E-DIFF even while `paired_sharpe_statistics.reason` reports `ZERO_VARIANCE` for E-IMPROV; I reproduced that case. Require valid \(d\) Sharpe for L-1/L-2, valid **both leg** Sharpes for L-4, and expressly fail closed on \(n<16\), unavailable block length, invalid replicate or incomplete target path. Do not use the aggregate `reason` as the E-DIFF availability test. |
| **D11R-S-5** | **BLOCKER for an executable C2 rule**; §5 D11-9 and [draft §2.3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:222) | D11-9 identifies correlation but stops short of the access question: the second family would read the **same dates after the first read marks the segment EXPOSED**. The draft says to process both nominees, while Constitution §7 says exposed segments never re-lock. State explicitly whether both predeclared nominees may receive separate `lockbox_eval` evaluations of that segment, when exposure and release occur, and what the second result may disclose. |
| **D11R-S-6** | **NON-BLOCKING**; §8 and Q1 | “Beats the benchmark day by day” is misleading: E-DIFF’s sign tests the **mean** of daily differences; it does not require a win each day. “Practical cost is small” in D11-10 is unsupported: a strong confirmation DSR does not ensure positive lockbox mean difference. Use the formula in the owner-facing description and remove the asserted small cost. |
| **D11R-S-7** | **NON-BLOCKING for D-11; blocker for activation**; §8 D-20 inheritance | The proposal correctly notes that current `bootstrap_indices` fixes output length at \(n\) and `ReplicateStream` admits only `paired_sharpe_ci`. It should state plainly that no lockbox seed source or complete source/target/nominee identity has been decided. D-20 must make and review those choices; the beacon decision for G-1/G-11/G-14 does not automatically extend to lockbox. |

**D11-1 through D11-11:** D11-1, -3, -4, -5, -7, -8 and -11 are sound. D11-2 finds a real boundary issue but misses the contradictory worked pass claims above. D11-6 should call 457 a proposed interpretation rather than already settled frozen wording. D11-9 understates the exposed-segment issue. D11-10’s “small cost” claim is unsupported.

## Independent numerical check

Read-only Python (`…\.venv\Scripts\python.exe -B`, importing this checkout’s `src`) confirmed:

- \(m=457\); type-7 position \(1999(0.05)=99.95\), weights \(0.05,0.95\). Type-6 and nearest-rank discriminators in the proposal are correct.
- The four-day example gives **E-IMPROV = 24.818088161661457** and **E-DIFF = −2.0681740134717863**. Its exact squared-Sharpe identities and reversal are correct.
- Under the proposal’s **iid, stationary, independent source/target, unselected-nominee and equal asymptotic-variance approximation**, the false-fail probabilities are **0.07970** for \(n=1247\) and **0.08340** for \(n=1100\). \(\sqrt{365/457}=0.89369\); the stated L-2 powers are approximately **0.50** at true E-DIFF 0 and **0.712** at 0.5. These are illustrative approximations, not coverage or selection calibration.

Q1 is fair after its plain-language correction; **Route A is my recommendation for fidelity to v1.0**. Q2 needs the technical access and state specification in D11R-S-3. Q3 is answerable by the owner, but “keep and disclose” must explicitly give up any claim that public, already elapsed prices provide a fresh prospective test. A future window is the stronger scientific choice and requires amendment; the owner may choose the weaker fixed window for own capital with that limitation recorded.

**Gate and record status:** `git status --untracked-files=all --short` was empty; I made no changes. Implementation tests, lint, type and import checks are N/A to this read-only proposal review. The synthetic calculations above passed. Local review gate: **BLOCKED by the findings**. Because the user required read-only work, this response is **not a committed review record**; under `AGENTS.md`, it cannot count as the completed R19-2 check until the model metadata and every finding, including unrepaired ones, are recorded and committed. No frozen verification against a trusted pre-task byte snapshot or lockbox-data check was performed.
