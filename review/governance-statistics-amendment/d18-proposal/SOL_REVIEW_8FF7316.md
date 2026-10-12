# Sol High re-review of the D-18 proposal revision 3 at `8ff7316` — UNSOUND as written

Date: 2026-10-03. Third-round re-review by the OpenAI family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("yes start both reviews"), run in parallel with, and without sight of,
`FABLE_REVIEW_8FF7316.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a1006d-f67b-7d62-8520-28bc5e6f133a`;
  tokens used 154,518; exit 0. (The reviewer's self-report below names only
  "GPT-5 family"; the CLI header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_8FF7316.md` (committed `29232f1`) with `{{PREFIX}}`
  replaced by `SR3` (substituted file SHA-256
  `7cc495de6e8a4b3bb68565bdf943d36acfab20d26de61fc8b5675057f4385bde`).
- Findings: SR3-1..SR3-5 BLOCKER; SR3-6 NON-BLOCKING. Nothing is decided by
  this record; no finding is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

Model: OpenAI Codex, GPT-5 family; exact serving variant is not exposed to me. | Commit reviewed: `8ff73162e396f278436646b69bad90fd63235981` | Verdict: **UNSOUND as written**

I reviewed the `8ff7316` Git tree directly. Checkout HEAD was `29232f1`; its only additional file is the revision-3 prompt. I did not read any revision-3 review by another reviewer. No network, edits, commits, restricted data, or trading actions were used.

## Findings

| ID | Severity | Location | Concrete scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SR3-1** | **BLOCKER** | `PROPOSAL.md` P18-2 and §0 Round 3 Q2; protocol lines 184–194 | Each family declares one trial and both finish on day 1. P18-2 performs the shared pick on day 1. The owner selected a pick when **both budgets are used up or day 180 arrives**; the frozen termination trigger is `all_family_trial_budgets_exhausted`, not “all declared trials finished.” | Declared-plan completion can occur with 1 of 81 allowed trials used in each family. Revision 3 therefore implements a materially earlier rule than the option shown to the owner and calls it “cycle end” when the cycle need not have ended. | Either use the earlier of actual exhaustion of both 81-trial budgets and day 180, or re-ask the owner whether completion of the frozen declared plan should replace budget exhaustion. Amend `cycle_termination` consistently. |
| **SR3-2** | **BLOCKER** | P18-2, P18-7 | Every calibration replication is invalidated before the shared pick. P18-2 calls each a “non-event”; `E_f` is always false, while no family availability result necessarily exists. The procedure can appear to meet both numerical targets without ever producing a pick. | The new 1% availability safeguard covers `A_f` failure, but P18-2 creates a third state—no pick—which P18-7 does not put in the unavailable numerator. This reintroduces the vacuous-qualification problem FR2-4/SR2-3 sought to close. | Count every no-pick attempted cycle as unavailable/no-result for the 1% target, or exclude governance termination from the stochastic experiment by a preregistered rule and state that calibration is conditional on reaching the pick. Bound and report the reach-pick rate. |
| **SR3-3** | **BLOCKER** | P18-1, P18-4 | `J_f` is empty, contains 82 trials, contains duplicate IDs, or contains a declaration whose hash does not match the evaluated configuration. For an empty set, `A_f` is vacuously true but `argmax J_f` is undefined; an oversized set violates the frozen family budget. | P18-1 freezes a set but gives no admissible-set domain. A total selection event requires at least one legal, uniquely identified trial and deterministic rejection of declaration/evaluation mismatches. | Require `1 ≤ |J_f| ≤ 81`, unique stable IDs, complete immutable hypothesis/grid hashes, family membership, and pre-evaluation validation. Invalid declarations must prevent cycle start, not become a post-result statistical branch. |
| **SR3-4** | **BLOCKER** | P18-6, P18-7, O18-4 | Several thresholds or cell-specific thresholds are tried on the held-out calibration results; the least stringent one whose estimated upper bound falls below 2.5% is selected. The quoted confidence bound no longer has its nominal simultaneous coverage unless this selection was included in the multiplicity design. | “`z_crit` is set by the calibration” does not say whether it is one global threshold, one per family, or one per cell; nor whether it is frozen before qualification data. Current frozen governance has one `0.95` threshold. | D-19 must freeze the threshold scope and selection algorithm. Prefer one decimal threshold fixed from development data before held-out qualification; otherwise preregister all candidates and simultaneous adjustment. Actual family designs also need a deterministic qualifying-cell/support mapping, with out-of-support designs unavailable. |
| **SR3-5** | **BLOCKER** | P18-7 and §0 Round 3 Q4 | Each family has a 1% unavailable rate. The probability that at least one family is unavailable can be as high as 2%, although the owner-facing description says the “method gives a result in at least 99% of no-edge test runs.” | The proposal says “unavailable-family rate,” but does not bind whether 1% is per family or for the cycle-wide event `U_trend ∪ U_vol`. These are different targets. | Owner must choose: 1% per family, or 1% cycle-wide. For a cycle-wide target, directly bound the union or allocate family budgets whose sum is at most 1%. Include no-pick outcomes per SR3-2. |
| **SR3-6** | **NON-BLOCKING** | P18-3, P18-6 | Arithmetic yields `z=+∞`, while a materialized normal CDF reports `Φ(z)=1.0`, which is finite. A literal “finite DSR” test could admit the observation before P18-6 compares non-finite `z`. | `METHOD_CANDIDATE.md` already makes non-finite intermediate arithmetic unavailable, so the intended behavior is recoverable, but P18-3 should name the actual comparator. | Define availability as finite `S`, finite shared `S0`, valid `T`, finite positive `D`, and finite pre-Φ `z`; the reported CDF is not an availability surrogate. |

## Answers to the five questions

### 1. Event identity

The nominee-specific event is correct once the procedure is total:

\[
J_f^*=\arg\max_{j\in J_f}(S_j,-id_j),\qquad
E_f=A_f\cap\{z_{J_f^*}\ge z_{\rm crit}\}.
\]

Per-trial \(T_j\), skewness, kurtosis, and \(D_j\) affect each \(z_j\), but not the top-\(S\) nomination. Exact \(S\) ties are resolved by ID; non-finite inputs must make `A_f` false before nomination.

It is **not** identical to “some trial passes DSR.” Reproducing the earlier two-trial example with \(T=365\), \(A(2)=0.519755344\), \(S_0=0.0001837613\), and \(z_{.95}=1.644853627\):

| Trial | \(S\) | \(k\) | \(z\) | DSR |
|---|---:|---:|---:|---:|
| X | **0.0880** | 40 | 1.615547 | 0.946904 — fail |
| Y | 0.0875 | 1.2 | 1.665569 | 0.952100 — pass |

Top-Sharpe nominates X and fails even though Y passes. Thus \(E_S\subsetneq E_{\rm DSR}\). Revision 3 states this correctly.

The unresolved total-event defects are SR3-1 through SR3-3, not the algebra above.

### 2. False-promotion bound

Under the declared all-zero E-DIFF-mean global null, and assuming no alternative nomination path:

\[
F_f=E_f\cap H_f\subseteq E_f,
\]

so

\[
P_0(F)\le P_0(E_{\rm trend}\cup E_{\rm vol})
\le P_0(E_{\rm trend})+P_0(E_{\rm vol}).
\]

If each family is bounded at 2.5%, the arbitrary-dependence upper bound is 5%. Under independence:

\[
1-(1-0.025)^2=0.049375.
\]

For a single ideal-normal trial, moving from a 5% to a 2.5% one-sided rate requires approximately

\[
z_{\rm crit}=\Phi^{-1}(0.975)=1.9599639845,
\]

rather than \(\Phi^{-1}(0.95)=1.644853627\).

The set inclusion survives:

- Mixed nulls, under the same mixed probability law, if “false” means the nominated trial has non-positive true E-DIFF mean.
- Unavailable trials, when they fail closed and remain in the denominator.
- Family-level PBO, because it is an additional conjunct in \(H_f\).

What does **not** survive mixed nulls is the global-null numerical bound. A true-positive trial may make \(P_\theta(E)\) nearly one while false promotion is zero; conversely, global-null calibration proves no uniform mixed-null false-selection rate.

### 3. Frozen compatibility and amendment status

P18-1’s advance declaration is stricter than Constitution §8; it does not directly contradict §8, but changing registration timing requires the successor-cycle amendment.

P18-2, as written, does not match the owner-selected or frozen cycle-end trigger because “all declared trials finished” is not “both budgets exhausted” (SR3-1).

P18-5’s one-submission rule is within the frozen ceiling of two lockbox evaluations, but permanently eliminating the justified replacement path changes the governing contract and belongs in the amendment.

P18-6 directly replaces frozen `validation.dsr.minimum: 0.95` and `promotion.dsr_minimum: 0.95`; amendment is mandatory.

`configuration_selection` is compatible with one top-Sharpe grid point. Plateau can be evaluated on it, at the stated loss of runner-ups. PBO alignment is only conditional on D-08 adopting E-DIFF.

The §4 label is correct. The amendment must be owner-authored, versioned, signed/dated, terminate C1, and activate only for C2. Later promotion-gate or protocol-enforcement code is §16 protected.

### 4. Completeness of O18-1 through O18-5

They are not complete. Option C still needs:

- A shared-pick trigger that matches the owner’s choice and frozen cycle semantics.
- A nonempty, budget-valid declared-set contract.
- Treatment and a rate limit for no-pick/censored cycles.
- A decision whether the 1% availability ceiling is per family or cycle-wide.
- One global, family-specific, or cell-specific `z_crit`, with a deterministic live lookup rule.
- Threshold selection separated from held-out qualification, or multiplicity-adjusted.
- A fixed confidence level and multiplicity family covering every cell, family, error bound, and availability bound.
- A deterministic supported-domain classifier mapping actual declared families to qualifying cells; out-of-support designs must fail closed.
- Complete `H_f` state semantics. O18-5 promises this but does not yet supply it.

The generator, seeds, custody, replication budget, and confidence construction properly belong to D-19, but they must consume a total D-18 procedure.

### 5. Top Sharpe, no fallback

It is a defensible choice after the blockers are repaired.

Its benefits are a smaller DSR-stage event than top-DSR, alignment with the maximum-Sharpe quantity motivating \(S_0\), deterministic nomination, and only one irreversible lockbox use.

Its costs are substantial:

- A lower-Sharpe trial can have a better DSR because of \(T\), skewness, or kurtosis.
- The nominated point can fail plateau, CI, or another gate while a runner-up would pass.
- Selected-point intervals and confirmation null tests remain post-selection; no-fallback does not restore nominal single-test coverage.
- Declaring everything in advance removes mid-cycle adaptation.
- One unavailable non-nominee blocks the entire family.

Top-DSR has a broader DSR event—effectively “any available score passes”—and selects partly on noisy higher moments. It needs its own calibration.

Fallback with “any trial passes all gates” offers more discovery power but has the broadest multiplicity, technical-failure, timing, and lockbox burden. Its DSR-stage upper event is the union of all DSR passes; downstream selected-point gates would be repeated and the frozen lockbox still permits at most two reads.

## Revision-2 finding disposition

| Finding | Revision-3 status |
|---|---|
| FR2-1 | **Resolved:** `J_f` is declared before results. SR3-3 adds missing admissibility rules. |
| FR2-2 | **Resolved in direction:** owner chose a stricter threshold; exact threshold governance remains SR3-4. |
| FR2-3 | **Resolved for D-18:** 2.5% per family and DEC-02 revision are explicit; D-19 must implement the joint design. |
| FR2-4 | **Partly resolved:** 1% availability and conditional reporting added, but no-pick and scope loopholes remain SR3-2/SR3-5. |
| FR2-5 | **Resolved:** comparison is expressly DSR-stage only. |
| FR2-6 | **Resolved:** only the fresh lockbox is credited with single-use meaning. |
| FR2-7 | **Resolved conditionally:** D-08 dependency is explicit. |
| FR2-8 | **Resolved:** E-DIFF and unannualized daily \(S\) are named. |
| FR2-9 | **Resolved:** started attempts count; unstarted declarations fail availability. |
| FR2-10 | **Resolved in principle:** exact nominee identity and technical-invalid fail-closed behavior are specified. |
| FR2-11 | **Resolved:** correlation/tail rationale replaces the obsolete coincidence claim. |
| FR2-12 | **Resolved:** blocking on an unavailable non-nominee is deliberate. |
| FR2-13 | **Resolved:** option descriptions shown to the owner are recorded. |
| SR2-1 | **Partly resolved:** both families share one look, but its trigger mismatches the chosen cycle-end rule and no-pick handling is unsafe. |
| SR2-2 | **Resolved:** comparison is on pre-Φ \(z\) against a frozen decimal threshold. |
| SR2-3 | **Partly resolved:** 1% availability was added; SR3-2/SR3-5 remain. |
| SR2-4 | **Partly resolved:** a strong cell catalogue is present, but threshold selection and supported-domain mapping remain D-19 blockers. |
| SR2-5 | **Resolved:** post-selection coverage limitation is explicit. |
| SR2-6 | **Resolved:** full promotion events are explicitly not nested. |
| SR2-7 | **Resolved:** equal 2.5% allocation was deliberately selected. |
| SR2-8 | **Partly resolved:** fail-closed gate behavior is stated, but the promised complete gate enumeration is not yet present. |

## Review gate

`LOCAL GATE: BLOCKED` for accepting D-18 or starting qualification calibration.

The target commit changes only `PROPOSAL.md`; `git diff --check` passed and the working tree is clean. The repository PowerShell verifier was incompatible with this runtime because `Convert.ToHexString` was unavailable; an independent standard-library reproduction passed: 28/28 frozen files and exact inventory, 14/14 sidecars, Constitution self-hash, seven manifest/protocol bindings, and nested bindings. Tests, lint, typing, and import-boundary checks were N/A because no code or configuration changed.

Per repository policy, this review is not a completed governance record until an authorized actor writes and commits it. I did not do so because the request expressly prohibited edits and commits.

## Eight-line owner summary

1. The central safety logic is right: promotion requires the nominated trial to pass the calibrated DSR screen.
2. Top Sharpe passing is still different from any trial passing, and revision 3 now handles that correctly.
3. The proposed pick happens when declared trials finish, not when both budgets are exhausted as you selected.
4. Early invalidation can disappear as a “non-event,” bypassing the new 1% availability safeguard.
5. Empty, oversized, or malformed declared trial sets still have no defined rejection rule.
6. The calibration must freeze how one threshold is chosen before held-out results are examined.
7. Top Sharpe with no fallback is defensible, but it deliberately loses viable runner-ups.
8. Keep D-18 and calibration blocked until these contracts are repaired and reviewed.