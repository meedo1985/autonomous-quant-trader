# Sol High review of the D-18 proposal at `690fa97` — SOUND WITH FIXES

Date: 2026-10-03. Second of the two different-model reviews required by R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); reviewers chosen by the
owner ("Fable 5.1 + Sol High"). Run in parallel with, and without sight of,
`FABLE_REVIEW_690FA97.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10048-b34e-73f2-babc-868d4ffda95d`;
  tokens used 121,084; exit 0. (The reviewer's own self-report below names
  only "GPT-5 family"; the CLI header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_690FA97.md` with `{{PREFIX}}` replaced by `SR`
  (substituted file SHA-256
  `bbfa0f71e55e5a8c03b973a077fd60cc658fdbdcef80b800f39b3a5ac124bf50`).
  Checkout HEAD at run time: `00dac52`.
- Findings: SR-1..SR-4 BLOCKER; SR-5, SR-6 NON-BLOCKING. Nothing is decided
  by this record; no finding is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

Model: OpenAI Codex, GPT-5 family; exact serving variant is not exposed to me. | Commit reviewed: `690fa978cd2ea218898db8622a04fc8963f20c44` | Verdict: **SOUND WITH FIXES**

I reviewed the target commit directly from Git objects because the clean checkout had advanced to `00dac52`. Read-only; no network, edits, restricted data, commits, or pushes.

## Findings

| ID | Severity | Location | Concrete scenario | Evidence / calculation | Proposed disposition |
|---|---|---|---|---|---|
| **SR-1** | **BLOCKER** | `PROPOSAL.md` §3 and O18-2; `METHOD_CANDIDATE.md` §§3.5, 6.1 | Trial A has DSR `0.96`; trial B has zero variance and is unavailable. O18-2 makes the family unavailable and submits nothing. Yet `max` over available scores is `0.96`, while `max` over all trials is undefined. Thus the section 3 equality is respectively false or not an event. | For complete finite scores, if \(J^*=\arg\max_j(s_j,-id_j)\), then \(s_{J^*}=\max_j s_j\), regardless of per-trial denominators or ties. But that proof has an unstated availability premise. | Define \(A=\{\text{all required trial DSR scores available}\}\) and \(E=A\cap\{\max_j s_j\ge.95\}\). Define no \(J^*\) outside \(A\). Count unavailable families in the all-attempt denominator as `E=0`, and calibrate availability separately. |
| **SR-2** | **BLOCKER** | `PROPOSAL.md` §3 and O18-1; reconciliation DEC-02 | In a mixed family, a genuinely positive trial may clear almost surely, making `P(E)` near one while false promotion is zero. Conversely, global-null calibration supplies no theorem for the probability that a null trial wins in a mixed family. | Under the same probability law, \(F_{\text{false}}\subseteq E\) remains true. But \(P_{\theta=0}(E)\le\alpha\) does **not** imply \(P_{\theta\in\text{mixed}}(F_{\text{false}})\le\alpha\); the probability measure changed. | Register the all-zero-mean global null as the primary scope if that is intended. Treat mixed-null error separately, e.g. \(E_0=A\cap\{\exists j:\theta_j\le0,\ s_j\ge.95\}\), with its own scenarios and claim. |
| **SR-3** | **BLOCKER** | P18-1/P18-3 and O18-3; protocol `trial_accounting` and `configuration_selection` | It is unspecified whether \(J\) means all usable trials in one family at family close, all current-cycle trials, or candidates across families. Repeated opportunities are not bounded by a per-family event. | Two independent family/cycle opportunities each controlled at 5% give \(1-(1-.05)^2=9.75\%\), not 5%. Lifetime count in the hurdle does not itself prove lifetime or cross-family error control. | Fix the family identity, candidate-set membership, accounting cutoff, selection time, treatment of late/failed attempts, and whether selection occurs separately per family. State explicitly that the calibration is per family-cycle unless a broader aggregate is calibrated. |
| **SR-4** | **BLOCKER** | P18-1 ties; O18-2; calibration contract | Exact ties, duplicate trials, or floating-point CDF saturation can make several stored DSR scores equal. Lowest-ID selection is deterministic, but the tied trials can have different plateau or other selected-point results. Non-finite downstream gates introduce the same total-event issue. | The DSR-threshold union is tie-invariant, but the selected candidate and full promotion outcome are not. `z ≥ Φ⁻¹(.95)` uses `Φ⁻¹(.95)=1.644853626951`; comparison via the latent finite `z` and comparison via a rounded/materialized CDF score need not induce identical ties. | Freeze whether selection compares the untransformed DSR statistic or the stored full-precision score; define exact equality, numerical failure, reason precedence, downstream-gate unavailability, and whether technical invalidation permits replacement. Calibrate that exact implementation. |
| **SR-5** | **NON-BLOCKING** | P18-2; protocol `configuration_selection`, `pbo`, `plateau`, and lockbox limits | The top scorer may be on a plateau boundary and fail while a runner-up passes. No fallback deliberately rejects the family. PBO, however, is one family scalar, not something the selected trial individually fails. | Frozen text requires one submitted grid point and says family DSR/PBO/plateau account for selection; it does not prescribe the nomination rule. The lockbox allowance of at most two evaluations is a ceiling, not a requirement to use a replacement. | Retain fail-closed behavior if desired, but say “the family PBO gate fails or is unavailable.” Clarify that “no promotable candidate” does not itself terminate the cycle before frozen termination conditions. |
| **SR-6** | **NON-BLOCKING** | P18-1 versus `METHOD_CANDIDATE.md` §3.4 and `TECHNICAL_APPENDIX.md` §5 | In the repository example, X has the higher Sharpe (`0.3872983 > 0.3853813`) but Y has the higher DSR (`0.7474 > 0.7459`) because \(D_X=1.024\), \(D_Y=1\). | Per-trial skew/kurtosis denominators therefore do not break the maximum-DSR identity; they change which trial is selected. This differs from the original maximum-Sharpe procedure for which the expected-maximum motivation was written. | Give this selection procedure a distinct method identity and calibrate the complete maximum-DSR procedure. Do not carry over evidence for maximum-Sharpe selection. |

## Event identity and probability bound

For a complete family of finite scores, section 3 is correct:

\[
J^*=\arg\max_j(s_j,-id_j)
\quad\Longrightarrow\quad
s_{J^*}=\max_j s_j
\]

and therefore

\[
\{s_{J^*}\ge.95\}
=\{\max_j s_j\ge.95\}
=\{\exists j:s_j\ge.95\}.
\]

Different \(D_j\) denominators can reverse the Sharpe ordering but cannot invalidate this identity because selection is by the resulting score. Exact ties also preserve it.

It is incorrect as a total event over the proposal’s full domain until availability is included, as shown by SR-1.

With the corrected event, let \(H\) mean every remaining selected-point or family-level gate passes. Then

\[
F=A\cap\{s_{J^*}\ge.95\}\cap H
\subseteq
A\cap\{\max_j s_j\ge.95\}=E.
\]

Under the all-zero global null, every promotion is false, so:

\[
P_0(\text{false promotion})=P_0(F)\le P_0(E).
\]

That calculation is correct. It also survives:

- unavailable trials, provided they make both promotion and `E` false while remaining in the attempted-family denominator;
- PBO and other family-level gates, because they merely add conjuncts to \(F\);
- mixed nulls as a set inclusion under the **same mixed distribution**.

What does not survive is transferring a numerical bound calibrated under the global null to mixed/composite nulls. Under mixed nulls, `P(E)` is not a false-pass rate because true-positive trials contribute to it, and the global-null calibration says nothing uniform about null-trial selection in that different population.

## Frozen compatibility and amendment status

P18-1/P18-2 do not directly contradict frozen v1.0 text:

- `configuration_selection` permits one submitted grid point but does not identify it.
- Plateau applies naturally to the selected point; no fallback intentionally loses power when that point fails.
- PBO remains a family-level filter.
- The two-lockbox-evaluation provision is a maximum, so using fewer is permitted.
- Constitution §§4, 9, and 16 do not supply a competing selection rule.

O18-5 is correctly labelled: authoritative adoption requires a Constitution §4 successor amendment. The rule adds operational semantics to frozen `configuration_selection` and restricts replacement behavior. The matrix’s old `STAT` label for D-18 does not authorize altering a frozen protocol. Section 16 becomes applicable when promotion-gate or protocol-enforcement code is later changed; it is not triggered by this proposal-only review.

## What O18-1 through O18-5 still omit

Before option-C calibration can be preregistered, D-18 must additionally bind:

- the exact trial universe, family boundary, selection cutoff, and nomination time;
- a total event over every attempted replication, including unavailable results;
- the all-attempt denominator and a separate availability-rate acceptance rule;
- the exact numerical comparison used for selection and thresholding;
- the mixed-null false-promotion estimand, if any;
- cross-family and repeated-cycle scope;
- treatment of unavailable family gates and technical invalidation;
- whether the no-fallback rule extends through lockbox processing or only eligibility.

The error tolerance, simultaneous confidence method, scenario grid, replication budget, custody, and stopping rule belong primarily to D-19/calibration governance, but they cannot be fixed coherently until these D-18 items are settled.

## Selection alternatives and their costs

| Rule | Benefit | Plain cost |
|---|---|---|
| **Top DSR, no fallback** | Makes the DSR event exactly “any available trial clears”; simplest conservative bound. | Selects partly on estimated skew/kurtosis denominators, not necessarily performance; loses good runner-ups; requires fresh whole-procedure calibration. |
| **Maximum Sharpe, no fallback** | Matches the original expected-maximum motivation and existing baseline proposal more closely. | The selected trial passing is not the same as any trial passing. Any later fallback or operator discretion invalidates that calibration. |
| **Fallback; any trial passes all gates** | Best chance of finding a genuinely robust eligible point. | Broadest multiplicity and highest calibration burden; the event combines selected-point gates, family-level PBO, availability, ties, and dependence. A DSR-union bound remains possible but may be very loose. |

Top DSR with no fallback is a defensible governance choice when simplicity and strictness are valued over power. It is not uniquely statistically preferable.

No implementation checks were applicable because nothing changed. The worktree remained clean. Under the repository rule, this review is not a completed review record until its model metadata and all SR findings are written and committed by an authorized actor; I did not do that because the request prohibited edits and commits.

Plain-language owner summary:

- The top-DSR, no-fallback idea is defensible, but the written contract is incomplete.
- When every score is valid, the highest scorer passes exactly when any trial passes.
- One unavailable score currently makes that claimed identity false or undefined.
- The false-promotion bound is valid for the declared all-zero global null.
- That global-null calibration does not automatically protect mixed-null families.
- PBO does not break the bound because it is an additional family-level filter.
- Adoption needs an owner-authored section 4 amendment and later protected-code review.
- Keep calibration blocked until availability, scope, timing, and numerical selection are fixed.