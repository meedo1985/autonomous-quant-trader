# Sol High re-review of the D-18 proposal revision 2 at `ffbedad` — SOUND WITH FIXES

Date: 2026-10-03. Re-review by the OpenAI family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("ok wait for sol"), run in parallel with, and without sight of,
`FABLE_REVIEW_FFBEDAD.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10052-9b5d-7950-8896-8f4a30542a9c`;
  tokens used 138,366; exit 0. (The reviewer's self-report below names only
  "GPT-5 family"; the CLI header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_FFBEDAD.md` (committed `cb116c6`) with `{{PREFIX}}`
  replaced by `SR2` (substituted file SHA-256
  `bb03e34f447145ed532057833886b40f05546c40c1e4c4851e0f5a8ed37341ef`).
- Findings: SR2-1..SR2-4 BLOCKER; SR2-5..SR2-8 NON-BLOCKING. Nothing is
  decided by this record; no finding is repaired here. The owner decides.
- Note: absolute `D:/...` file links in the verbatim text below are as the
  reviewer wrote them.

Below is the reviewer's final message, verbatim.

---

Model: OpenAI Codex, GPT-5 family; exact serving variant is not exposed to me. | Commit reviewed: `ffbedad67a8b98c24a5fb981b7c91a9e24805ac9` | Verdict: **SOUND WITH FIXES**

I reviewed the immutable `ffbedad` tree because the checkout has advanced to `cb116c6`. Read-only: no network, edits, commits, confirmation/lockbox data, or trading activity.

| ID | Severity | Location | Concrete scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SR2-1** | **BLOCKER** | [PROPOSAL.md:37](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d18-proposal/PROPOSAL.md:37), [protocol_v1.yaml:192](D:/PMP-programs-for-sharawi/autonomous-quant-trader/protocols/protocol_v1.yaml:192) | Trend exhausts its budget and promotes on day 70. The cycle terminates immediately, so volatility reaches neither budget exhaustion nor day 180 and never receives its defined look. `E_vol` is then undefined. The same gap exists for `protocol_revision` and `cycle_invalidated`. | P18-1 names only budget exhaustion and day 180, while frozen `cycle_termination` has five terminating conditions. A probability bound requires `E` to be a total event on every replication. | Define no-look semantics, preferably `E_f=false` when the cycle terminates before that family’s look; bind simultaneous-event ordering and calibrate the actual stopping rule. Alternatively require a common cycle-close nomination before any promotion. |
| **SR2-2** | **BLOCKER** | P18-5; reconciliation “reference and implementation must agree exactly” | A mathematically boundary-equal score can pass one comparator and fail another. | Python 3.14.7 gives `z95=1.6448536269514715`, but `NormalDist().cdf(z95)=0.94999999999999984`. Thus `z>=z95` passes while materialized `DSR>=0.95` fails. Revision 2 fixes the Sharpe ranking key but not the threshold representation. | Freeze one comparator, precision, CDF implementation, and boundary behavior; add exact boundary reference vectors. Also bind technical-invalid reason precedence. |
| **SR2-3** | **BLOCKER** | P18-2/P18-5, O18-2; `METHOD_CANDIDATE.md` §§3.5/6.1; Astra AS-3 | A prior-cycle attempt or abort makes lifetime/current/usable counts unequal. Under the narrow candidate, all scores can remain unavailable forever. Then `P(E)=0` trivially satisfies 5% although no usable procedure exists. | Unavailable outcomes correctly remain denominator non-events, but “availability is calibrated and accepted separately” gives no accepted ceiling. DEC-02’s proposed 1% ceiling is explicitly unaccepted. `K=1`, `V=0`, `K<N`, and incomplete history remain unresolved. | Before qualification, freeze the supported domain, every unavailable branch, and a separate simultaneous upper confidence bound for availability. Error-rate success alone must never qualify a vacuously unavailable method. |
| **SR2-4** | **BLOCKER** | O18-5; DEC-01–DEC-03 | “Qualifying non-Gaussian, correlated cells” is not a calibration design. A favorable chosen correlation structure can pass while duplicate clusters, opposite trials, unequal uncertainty, or lifetime/current mismatch fail. | Astra already showed large dependence-structure sensitivity. Missing cases include duplicates/opposites, unequal clusters and `T`, serial and cross-trial dependence, adaptive/missing attempts, exact ties, heterogeneous moments, and mixed-null selection. | D-18 must freeze the complete deterministic procedure and event. D-19/calibration governance must then preregister the qualifying cell grid, joint generator, cellwise success rule, simultaneous one-sided bounds, seeds, custody, replication budget, and no-rescue stopping rule. |
| **SR2-5** | **NON-BLOCKING** | PROPOSAL §3 lines 72–75 | One application of a confidence interval after choosing the maximum Sharpe does not retain nominal single-test coverage. | For 81 independent null standardized Sharpe estimates, a nominal 90% two-sided interval has a positive lower bound when `Z>1.64485`. After maximum selection, that happens with `1−0.95^81 = 0.984310394`, not 5%. The DSR screen may still bound overall promotion; it does not restore the interval’s stand-alone coverage. | Replace “each keeps its single-test meaning” with the narrower truth: no fallback limits discretionary repetition and irreversible lockbox use. Selected-point intervals and null tests remain post-selection quantities. |
| **SR2-6** | **NON-BLOCKING** | PROPOSAL §3 lines 77–83 | Top-Sharpe has a smaller **DSR event**, but the full promotion events under top-Sharpe and top-DSR are not ordered because the two rules can nominate different trials with different plateau, CI, and other gate results. | `E_S⊆E_DSR` is correct. No analogous general inclusion exists between `E_S∩H(J_S)` and `E_DSR∩H(J_DSR)`. | Say explicitly that the strictness comparison concerns only the DSR component, not the complete promotion procedure. Calibrate whichever complete nomination rule is adopted. |
| **SR2-7** | **NON-BLOCKING** | P18-5, O18-4 | The equal 2.5% family split is sufficient, but it is an additional unaccepted design choice and may allocate power poorly. | For arbitrary dependence, `P(E_trend∪E_vol)≤0.025+0.025=0.05`. If independent, the exact union is `1−0.975²=0.049375`. | Bind general budgets `α_trend+α_vol≤0.05`, including whether bounds apply in every qualifying cell. Equal allocation is acceptable if deliberately selected; direct joint-family calibration is another route. |
| **SR2-8** | **NON-BLOCKING** | O18-6/O18-7 | `H_f` is left abstract: PBO can be disabled or unavailable, OOS/IS has no frozen threshold, and selected-point versus family-level failures have different scopes. | This does not invalidate `F⊆E`, because additional gates are conjuncts, but it leaves the operational false-promotion event incomplete. | Enumerate every `H_f` component and its `PASS`/`FAIL`/`N/A`/`UNAVAILABLE` behavior, including PBO enablement and lockbox technical invalidation, in the amendment. |

## Answers to the five questions

### 1. Event identity

Conditionally, revision 2 is correct:

\[
E_f=A_f\cap\{\operatorname{DSR}(J_f^*)\ge0.95\},
\qquad
J_f^*=\arg\max_j(S_j,-id_j).
\]

Per-trial \(T_j\), skewness, kurtosis, and therefore \(D_j\) may change DSR ordering, but they do not change the top-Sharpe nomination. Exact Sharpe ties are resolved by ID, and non-finite values make \(A_f\) false before nomination.

Revision 2 also correctly rejects the old identity with “any trial passes DSR.” A concrete counterexample is:

\[
T=365,\quad
(S_X,k_X)=(0.088,40),\quad
(S_Y,k_Y)=(0.0875,1.2),\quad g_X=g_Y=0.
\]

For these two Sharpes:

\[
\sqrt V=0.000353553,\quad A(2)=0.519755344,\quad S_0=0.000183761.
\]

Applying the proposal’s formula gives:

| Trial | Sharpe | \(z\) | DSR |
|---|---:|---:|---:|
| X | **0.0880** | 1.615547 | **0.946904 — fail** |
| Y | 0.0875 | 1.665569 | **0.952100 — pass** |

Thus the top-Sharpe event fails while “some trial passes” is true. This establishes the strict inclusion \(E_S\subset E_{DSR}\), not equality.

The remaining defects are that the numerical comparison and no-look cycle outcomes are not yet total, as SR2-1 and SR2-2 explain.

### 2. False-promotion bound

Under the declared all-zero-mean global null, and once the procedure is total:

\[
F_f=E_f\cap H_f\subseteq E_f,
\]

so

\[
P_0(F)\le P_0(E_{\text{trend}}\cup E_{\text{vol}})
\le P_0(E_{\text{trend}})+P_0(E_{\text{vol}}).
\]

That reasoning is correct.

It survives:

- Mixed nulls as a **set inclusion under the same mixed distribution**. What does not transfer is the numerical global-null 5% calibration. Mixed-null false selection needs its own event and challenge results.
- Unavailable trials, provided `A_f=false` prohibits nomination and promotion and remains in the all-attempt denominator.
- Family-level PBO and other gates, because they add conjuncts rather than alternative promotion paths.

It does not yet survive undefined no-look outcomes or an implementation path permitting technical replacement outside P18-4.

### 3. Frozen compatibility and amendment status

Top-Sharpe nomination is compatible in direction with frozen text:

- `configuration_selection` requires one submitted grid point but does not select it.
- PBO ranks the family by `paired_delta_sharpe`, which aligns with top-Sharpe.
- Plateau can be evaluated on the nominated point; no fallback deliberately loses power when that point fails.
- The lockbox limit of two is a ceiling, so using only one does not directly violate line 74.
- Constitution §§4, 9, and 16 supply no competing selector.

Nevertheless, authoritative adoption requires a Constitution §4 successor-cycle amendment. It adds binding nomination and error-event semantics, permanently forbids use of a frozen replacement allowance, and must reconcile cycle termination, D-16/D-17 counts, D-19’s claim, unavailable branches, and the remaining promotion-gate decisions. Section 16 applies later to implementing promotion-gate or protocol-enforcement code.

O18-8 labels this correctly. No frozen file was changed by `ffbedad`.

### 4. Completeness of the open items

O18-1 through O18-9 are materially better but not complete. Option C still needs:

- Total no-look and early-cycle-termination semantics.
- The exact DSR threshold comparator and numerical boundary contract.
- Supported availability branches and an accepted availability ceiling.
- A precise qualifying scenario grid, not merely “non-Gaussian, correlated.”
- Pointwise versus averaged cell success and simultaneous-confidence multiplicity.
- A joint two-family generator or a frozen family alpha allocation.
- Exact gate-state semantics for disabled, unavailable, and technically invalid gates.
- Correction of the downstream “single-test meaning” claim.
- Explicit recognition that DSR-event ordering does not order full promotion outcomes.

The procedure/event decisions belong in D-18. Threshold claims, calibration confidence, budgets, custody, and acceptance criteria belong principally to D-19 and the calibration preregistration.

### 5. Top Sharpe, no fallback

It is a sound candidate, subject to the blockers above.

Its advantages are that it matches the maximum-Sharpe object motivating \(S_0\), aligns with PBO’s ranking metric, removes operator discretion, and limits downstream and lockbox repetitions.

Its costs are plain:

- It can reject a family even when a lower-Sharpe trial has a better DSR and would pass.
- It can nominate a high-Sharpe, heavy-tail trial whose skew/kurtosis penalty makes it fail.
- It remains data-dependent selection; nominal selected-point intervals are not ordinary single-trial intervals.
- No fallback sacrifices power and can waste the only viable robust configuration.

Top-DSR nomination offers more DSR-component power and makes the event “any score passes,” but selects partly on noisy moment estimates and no longer directly matches the maximum-Sharpe/PBO construction.

Fallback with “any trial passes all gates” offers the most discovery power, but creates the broadest multiplicity, availability, timing, and lockbox contract. A DSR-union upper bound remains possible, but is looser and does not preserve the nominal meaning of repeatedly applied downstream tests.

## Revision-1 finding disposition

| Earlier finding | Revision-2 status | Assessment |
|---|---|---|
| FR-1 | **PARTIAL** | One fixed family look is added; early cycle termination still leaves no-look events undefined. |
| FR-2 | **PARTIAL** | Whole-cycle scope and the two-family union are added; realized stopping/no-look semantics remain. |
| FR-3 | **RESOLVED** | Replacement is forbidden and line 74 is included in amendment scope. |
| FR-4 | **RESOLVED** | The owner was re-asked, strictness was corrected, and no-fallback is no longer credited with producing the bound. |
| FR-5 | **RESOLVED** | Top-Sharpe aligns with PBO ranking and \(S_0\); O18-7 records PBO as family-level. |
| FR-6 | **RESOLVED** | Global-null scope and separate mixed-null challenge event are explicit. |
| FR-7 | **PARTIAL** | `A_f` and the denominator are defined; lifetime mismatch and the availability acceptance ceiling remain open. |
| FR-8 | **RESOLVED** | Non-finite values fail availability; ranking uses full-precision Sharpe and deterministic ID ties. |
| FR-9 | **RESOLVED** | “Nominated trial” and the permitted selection inputs are explicit. |
| FR-10 | **PARTIAL** | The problem is acknowledged, but the promised complete gate list is not in this proposal. |
| FR-11 | **RESOLVED** | The proposal now cites the correct Astra line 208 subject. |
| FR-12 | **PARTIAL** | Non-Gaussian/correlated qualifying cells are recognized, but the required cell contract is incomplete. |
| FR-13 | **PARTIAL** | R19-2 supersession is disclosed; the committed matrix still carries the stale `STAT` label. |
| FR-14 | **OPEN** | The proposal explains definition versus calibration dependency, but the owner has not confirmed the changed decision order. |
| SR-1 | **RESOLVED** | Availability is included in `E_f`, and no nominee exists outside `A_f`. |
| SR-2 | **RESOLVED** | No mixed-null numerical guarantee is claimed. |
| SR-3 | **PARTIAL** | Family, current-cycle universe, cutoff, and cycle scope are defined; early stopping and repeated-cycle control remain unresolved. |
| SR-4 | **PARTIAL** | Nomination ties and non-finite inputs are fixed; the DSR threshold comparator and technical-invalid precedence are not. |
| SR-5 | **RESOLVED** | No fallback, family-level PBO, and cycle continuation after family failure are addressed. |
| SR-6 | **RESOLVED** | The selector switched to top Sharpe and the proposal targets that selector’s event directly. |

## Review gate and reproducibility

`LOCAL GATE: BLOCKED` for accepting D-18 or starting option-C calibration, because SR2-1 through SR2-4 remain.

Independent checks found:

- `ffbedad` changed only `PROPOSAL.md`; whitespace check passed.
- The working tree was clean; current HEAD merely adds the later review prompt.
- Frozen-path diffs from `ffbedad^` to `ffbedad`, and from `ffbedad` to current HEAD, were empty.
- Read-only verification passed for 28 protected baseline files, 14 sidecars, the Constitution self-hash, seven manifest bindings, seven protocol bindings, and three nested bindings.
- The numerical counterexamples were reproduced under Python 3.14.7.
- Tests, lint, typing, and import-boundary checks were N/A because the reviewed commit changes only prose and this task authorized no implementation.
- Per repository policy, this response is not a completed review record until an authorized actor saves and commits it; I did not do so because the request expressly prohibited edits and commits.

## Plain-language owner summary

1. The central idea is valid: if the chosen top-Sharpe trial passes DSR, false promotion must be inside the calibrated DSR event.
2. Top Sharpe passing is not the same as any trial passing; the proposal now correctly recognizes that difference.
3. The rule still fails to say what happens to a family that never gets its look because the cycle ends early.
4. The exact numerical meaning of “DSR at least 0.95” must be frozen because equivalent-looking comparisons can disagree at the boundary.
5. Unavailable results can make the error rate look perfect while making the method permanently unusable, so availability needs its own limit.
6. The 2.5% plus 2.5% split is mathematically safe, but it is an optional allocation that must be deliberately accepted.
7. Top Sharpe with no fallback is defensible, but it loses valid runner-ups and does not make selected confidence intervals ordinary single tests.
8. Keep D-18 and calibration blocked until these fixes are recorded; this review itself must also be committed before it counts as complete.