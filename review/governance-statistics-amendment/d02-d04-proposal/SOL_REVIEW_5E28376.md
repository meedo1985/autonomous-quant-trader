# Sol High review of the D-02..D-04 proposal rev1 at `5e28376` — SOUND WITH FIXES

Date: 2026-10-03. The OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a1020f-333a-7a33-8467-b54e414d64fa`;
  tokens used 85,265; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `5e28376`) with `{{PREFIX}}` = `SE1`
  (substituted file SHA-256 `dd1d326f873b428413d8f4feb9eebda9f2dcd3cbf66f1b0740a167618151ee81`).
- The reviewer's final message, verbatim:

---

Model: **OpenAI Codex, GPT-5 family**; exact serving variant is not exposed to this session.  
Commit reviewed: **`5e283763d49e748d850d1a34b678e416723676b4`**  
Verdict: **SOUND WITH FIXES** — do not present the current wording to the owner until the BLOCKER findings are repaired.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SE1-1 | **BLOCKER** | [§3 point 4 and §5](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:63>) | Serial dependence or long bootstrap blocks make the G-1 bootstrap dispersion materially larger than the DSR formula’s `sqrt(D/(T−1))`. For illustration, `S0=.02`, DSR scale `.05`, `zcrit=1.972`, and `S=.13` pass DSR, while bootstrap scale `.10` gives an approximate lower endpoint `.13−1.645(.10)<0`. | D-18 P18-6 defines a moment-based pre-Φ statistic; the implemented interval uses a stationary block bootstrap and percentile endpoints. No ordering between their scales is established. `K>=2` also does not ensure `S0>0`, because trial-Sharpe dispersion can be zero. | Delete “nearly redundant” and “almost never,” or label them as an untested hypothesis. D-19 may preregister and report joint disagreement rates, but it cannot be assumed beforehand. |
| SE1-2 | NON-BLOCKING | [§3 point 5](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:70>) | An easier gate can increase actual global-null promotion probability relative to a stricter gate, although it cannot exceed the calibrated `E_f` envelope. Mixed-null behavior can also change. | D-18 defines `E_f=A_f∩{z_f*>=zcrit}` and separately proves `F_f⊆E_f`; `E_f` is not itself the false-promotion event. The bound is claimed only for the all-zero-mean E-DIFF global null. | Retain the set argument but say: “The binding cannot change `P0(E_f)` or its upper bound while D-18 nomination remains fixed; it can change `P0(F_f)`, power, mixed-null behavior, and availability.” |
| SE1-3 | **BLOCKER** | [§4 C-2](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:84>) | A leg has zero variance, block selection fails, or any of 2,000 bootstrap replicates is invalid. G-1 then becomes `UNAVAILABLE`; its frozen `na` is “never.” | The implementation requires valid candidate and benchmark Sharpes, at least 16 observations for block selection, and zero invalid replicates. P18-7 requires a simultaneous upper bound `U_proc<=.01`; it does not merely require availability to be reported. | State that E-IMPROV must satisfy the D-19 whole-cycle `U_proc` qualification target or the method cannot qualify. Compare this with E-DIFF’s distinct requirement that the difference series have usable variance; neither availability profile dominates automatically. |
| SE1-4 | **BLOCKER** | [§4 C-1](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:77>) | The top-E-DIFF nominee fails an E-IMPROV gate even though another family trial would pass it. D-18 forbids fallback, so the family loses promotion eligibility. | P18-4 nominates solely by E-DIFF; P18-5 permits no fallback. D-18 also expressly says the selected-point interval is post-selection and lacks nominal single-test coverage. | Disclose the selection/objective mismatch and likely power loss. Require D-19 power and mixed-null cells to report failure by individual gate. Do not describe G-1 as having nominal 90% coverage for the selected nominee. |
| SE1-5 | NON-BLOCKING | [§4 C-5](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:96>) | The owner could infer that every lockbox statistic is compelled to use E-DIFF. | Appendix §7 proves only that the frozen **prediction-distribution construction** cannot recover E-IMPROV from confirmation difference-series paths. It does not establish that actual BTC/ETH lockbox return legs are unavailable. D-11 remains open precisely because source representation and statistic are unspecified. | Narrow the conclusion: L-1’s frozen bootstrap construction admits only E-DIFF as written. L-2, L-4, and D-12 require explicit D-11 bindings; using E-IMPROV would require both legs and formal amended wording. |
| SE1-6 | **BLOCKER** | [§5 alternative](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:104>) | The owner is steered away from E-DIFF by treating inactive implementation as substantive evidence and by describing E-DIFF as merely “additive return.” | E-DIFF is a risk-adjusted Sharpe of the active-return stream, not raw additive return. The existing E-IMPROV estimator is inactive and still needs D-20 review. The permitted evidence does not establish that Annex B is the only possible E-DIFF interval method. | Present E-DIFF’s benefits equally: alignment with nomination/DSR/PBO, no dual-objective nominee mismatch, and a different availability profile. Its costs are the absent reviewed interval implementation and weaker alignment with the difference-of-leg-Sharpes reading. |
| SE1-7 | **BLOCKER** | [§6 owner question](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md:113>) | A single yes/no answer simultaneously accepts the independent D-01 naming act and all three gate bindings, without offering E-DIFF, split decisions, or `KEEP_BLOCKED`. | The decision matrix says D-01 is independent; D-02–D-04 are individually independent, though deciding them together is advisable for coherence. D-05 still blocks G-8, and D-20 remains necessary. | Ask D-01 separately. For each D-02–D-04 row offer `E-IMPROV`, `E-DIFF`, or keep blocked, while recommending a common binding only as a coherence consideration. Explicitly disclose the dual-objective, availability, power, and unresolved-dependency consequences. |

Argument-by-argument: points 1 and 2 are defensible interpretations but do not uniquely compel E-IMPROV; point 3 is factually correct but is an implementation consequence, not statistical evidence; point 4 is unsupported; point 5’s set inclusion is correct after distinguishing `E_f` from actual false promotion.

In §4, C-3 and C-4 are correct. C-1 and C-2 are correct but materially incomplete, while C-5 overstates what the frozen lockbox construction proves. The missing power, post-selection-coverage, no-fallback, and `U_proc` consequences could change the owner’s choice.

A neutral owner question should separate naming from binding:

1. “D-01: register `E-IMPROV` and `E-DIFF` as distinct names, without binding any gate?”
2. “For each of D-02, D-03, and D-04, choose `E-IMPROV`, `E-DIFF`, or keep blocked. A common choice improves coherence, but E-IMPROV adds a second objective to E-DIFF nomination and has two-leg availability requirements; E-DIFF aligns with nomination/DSR/PBO but lacks a reviewed interval implementation. D-05, D-06/D-07, D-11/D-12, and D-20 remain unresolved. Nothing is activated.”

No files were changed, no network or restricted data was accessed, and the worktree was clean. Tests and frozen-baseline verification were not applicable to this document-only, evidence-restricted review. Per repository governance, this review is not a completed record until a human saves and commits it; I did not do so because the review instructions prohibit edits and commits.

The recommendation is reasonable, but the current proposal is not ready for the owner.  
A DSR pass does not nearly guarantee that the E-DIFF interval gate will pass.  
E-IMPROV adds a second objective and can reject the nominated E-DIFF winner.  
Availability, power, lockbox consequences, and the E-DIFF alternative need a fairer account.  
Ask separate neutral questions and keep every unresolved gate inactive.