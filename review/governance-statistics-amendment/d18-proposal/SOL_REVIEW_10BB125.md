# Sol High re-review of the D-18 proposal revision 4 at `10bb125` — UNSOUND as written

Date: 2026-10-03. Fourth-round re-review by the OpenAI family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("ok wait for both reviews"), run in parallel with, and without sight of,
`FABLE_REVIEW_10BB125.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10082-73c6-7d80-8a2d-5b1e69c1c643`;
  tokens used 238,952; exit 0. The log also shows one non-fatal
  `failed to refresh available models: request timed out` line before the
  header. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_10BB125.md` (committed `8fba42c`) with `{{PREFIX}}`
  replaced by `SR4` (substituted file SHA-256
  `822a9310c1bd920d2b2d30fd6817a514bb78a5be34734459396830ac64a3fffb`).
- Findings: SR4-1..SR4-6 BLOCKER; SR4-7 NON-BLOCKING. Nothing is decided by
  this record; no finding is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

Model: OpenAI Codex, GPT-5 family; exact serving variant is not exposed to me.  
Commit reviewed: `10bb12534a5b53eb44a2a321ea8ddcf49408d71a` from the immutable Git tree. The checkout was actually at `8fba42c`, whose additional commit only adds the revision-4 review prompt.  
Verdict: **UNSOUND as written**.

The central set-inclusion argument is sound, but revision 4 still lacks a total availability event, an operational unseen-data rule, a defined broadened DSR method, a complete post-pick procedure, and a sufficient held-out-data firewall.

## Findings

| ID | Severity | Location | Concrete scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SR4-1** | **BLOCKER** | `PROPOSAL.md` P18-5, P18-7, O18-5 | All trial Sharpes and DSR statistics are finite, so both `A_f` events pass and the shared pick occurs. PBO is enabled but its matrix is invalid in every replication, so PBO is always `UNAVAILABLE`. No trial can promote, yet the P18-7 no-result event is false because neither family is DSR-`UNAVAILABLE` and a pick occurred. The reported no-result rate is therefore 0%, despite a procedure that never produces a usable gate result. | P18-5 says any unavailable mandatory gate prevents promotion. P18-7 counts only family `UNAVAILABLE` as defined by P18-3, or no pick. It omits unavailable/technically invalid `H_f` components. | Either include every mandatory gate’s `UNAVAILABLE`/technical-invalid outcome in the whole-cycle no-result numerator, or rename the 1% target as DSR-computability only and establish a separate complete-pipeline availability target. |
| **SR4-2** | **BLOCKER** | P18-0, P18-2, P18-7 | Suppose the statistical method is always computable, but 2% of cycles are invalidated before the pick by an operational or governance event. The 1% target fails, yet no DSR simulation can estimate or control that 2%. Conversely, a research-only cycle disallowed by P18-0 has “no pick,” but it is unclear whether it enters the denominator. | P18-7 combines method availability with `protocol_revision`, `cycle_invalidated`, and possibly ineligible-cycle outcomes, without specifying the probability law or attempted-cycle denominator for those events. | Define the denominator as eligible, authorized cycle attempts. Calibrate method-generated availability separately. Record exogenous cancellation/invalidation rates separately unless a preregistered operational stochastic model is genuinely intended. |
| **SR4-3** | **BLOCKER** | P18-0; §3 fixed-design justification | A historical BTC window has never been queried through the experiment engine, so no per-trial confirmation metric was returned. Researchers nevertheless saw the public prices or aggregate reports and used them to choose the declared strategies. P18-0 can pass literally, but the declared set is not independent of that window. | “No per-trial confirmation metric was returned” is weaker than “the outcome data were unavailable to the selection process.” Public or indirectly released information can recreate the cross-cycle selection problem FR3-1 identified. | Bind an immutable future/unreleased window or securely blinded custody; record its data-manifest/window ID, non-overlap with every exposed segment, disclosure lineage, and declaration timestamp. Eligibility must cover all information available to selection, not only engine-returned per-trial metrics. |
| **SR4-4** | **BLOCKER** | P18-3, O18-2, O18-4 | Duplicate/near-duplicate trials, fat tails, dependence, `K<N`, `K=1`, or `V=0` enter the required qualifying grid. The current method returns unavailable in these cases, making the 1% target impossible. Revision 4 says the method will be broadened, but supplies no replacement formula or support contract. | O18-2 acknowledges that the current method cannot qualify. An owner direction to broaden it is not a statistical method specification. Until that specification exists, `S0`, `A_f`, reason precedence, and the qualifying-cell classifier are not fixed. | Freeze and review the broadened method first: equation, D-16/D-17 count/dispersion combination, small-count branches, dependence/tail assumptions, availability rules, reason-code precedence, exact support classifier, and method identifier. Do not begin D-19 qualification before that. |
| **SR4-5** | **BLOCKER** | P18-6, O18-4 | Held-out certification fails. The threshold is not changed, but the method, cell classifier, support boundary, or margin is revised after examining those results, and the same held-out replications are reused. “No re-tuning `z_crit`” does not prevent this broader validation overfitting. | P18-6 freezes the threshold but does not expressly freeze the complete method, generator, classifier, confidence family, and acceptance rule or burn the held-out namespace after any access. | Before held-out generation, freeze the entire qualification object. Any held-out access or failure burns that seed namespace for all procedure changes; a revised procedure requires genuinely fresh held-out replications. Include all tried variants in simultaneous coverage if reuse is unavoidable. |
| **SR4-6** | **BLOCKER** | P18-2, O18-5, §3 | Both nominees exist. Trend is processed first and promotes; frozen `candidate_promoted` termination would end the cycle before volatility is processed. Reversing the order can produce a different recorded cycle. At day 180 the frozen cycle also terminates before the proposed post-pick work. | Revision 4 acknowledges that the post-pick window, order, and termination must be amended, but does not define them. The complete promotion/no-result procedure is therefore not yet a total deterministic event. | Bind the post-pick duration, nominee order, gate order, lockbox sequencing, technical-invalid behavior, simultaneous-event precedence, and the single cycle outcome before calibration. |
| **SR4-7** | **NON-BLOCKING** | §3, O18-4 | A declared design is assigned to a simulated cell, but its real return law has dependence or tails outside that generator. The cell passed while the real cycle is not dominated by it. | Revision 4 candidly says domination “cannot be fully checked at declaration.” Therefore calibration covers preregistered generator classes, not the realized market distribution. | State the D-19 claim narrowly as conditional evidence over named simulated classes. Do not describe it as a verified 5% real-cycle error guarantee. Out-of-support evidence must fail closed. |

## Event identity and calculation

For an admissible declared set and family availability,

\[
J_f^*=\arg\max_{j\in J_f}(S_j,-id_j),
\qquad
E_f=A_f\cap\{z_{J_f^*}\ge z_{\rm crit}\}.
\]

That is the correct event for **top Sharpe, no fallback**. Per-trial \(T_j\), skewness, kurtosis and \(D_j\) affect \(z_j\), but not the nomination. Exact Sharpe ties are resolved by ID. Any non-finite `S`, `S0`, `D`, or `z`, or non-positive `D`, makes `A_f` false before nomination.

It is not the event “some trial passes DSR.” Independent reproduction using \(T=365\), \(g=0\), and the proposal’s formula gives:

\[
A(2)=0.519755344,\quad
\sqrt V=0.000353553,\quad
S_0=0.000183761.
\]

| Trial | \(S\) | kurtosis | \(z\) | DSR |
|---|---:|---:|---:|---:|
| X | **0.0880** | 40 | 1.615547 | 0.946904 — fail |
| Y | 0.0875 | 1.2 | 1.665569 | 0.952100 — pass |

Top-Sharpe nominates X and fails even though Y passes. Revision 4 no longer asserts the false equality, so its nominee-specific event is algebraically correct; it remains uncomputable over the intended domain until SR4-4 is resolved.

## False-promotion bound

Under the declared all-zero E-DIFF-mean global null, once the full procedure is made total,

\[
F_f\subseteq E_f,\qquad
F\subseteq E_{\rm trend}\cup E_{\rm vol}.
\]

Therefore,

\[
P_0(F)\le P_0(E_{\rm trend})+P_0(E_{\rm vol})
\le 0.025+0.025=0.05.
\]

If the two events happened to be independent, the exact union would be

\[
1-(1-0.025)^2=0.049375.
\]

The set inclusion survives:

- mixed nulls, under the same mixed probability law;
- DSR-unavailable trials that fail closed;
- family-level PBO, because it is an additional conjunct;
- plateau and other downstream gates, provided no alternative nomination or fallback path exists.

The **numerical global-null bound does not survive mixed nulls**. A truly positive trial can make \(P_\theta(E)\) nearly one while false promotion is zero. Conversely, global-null calibration gives no uniform bound on a non-positive nominee winning in a mixed family. O18-1 correctly declines that claim.

SR4-1 does not invalidate \(F\subseteq E\); it invalidates the proposed availability safeguard and permits an unusable full gate to qualify.

## Frozen compatibility and amendment status

P18-1’s advance complete-set declaration is stricter than Constitution §8 but does not directly contradict it. It adds binding registration timing and set-validity rules and therefore properly belongs in the successor amendment.

P18-2 does conflict with or alter frozen cycle mechanics:

- `calendar_days_elapsed` currently ends the cycle at day 180;
- `candidate_promoted` currently ends the cycle immediately;
- declared-plan completion is not a frozen termination condition;
- the frozen protocol has no post-pick processing window.

P18-5 may use only one of the line-74 maximum of two lockbox evaluations, but permanently eliminating the justified replacement route changes the governing contract and should be explicit in the amendment.

P18-6 directly replaces both frozen `dsr.minimum: 0.95` and `promotion.dsr_minimum: 0.95`.

P18-0 requires a new forward confirmation-window regime beyond the fixed v1.0 partitions.

`configuration_selection` is otherwise compatible with one top-Sharpe grid point. Plateau can be applied to it, at the deliberate cost of losing viable runner-ups. PBO does not conflict if D-08 binds its ranking metric to E-DIFF; sharing a ranking metric does not make PBO a selected-trial gate.

The section 4 label is correct. Only the owner can author/sign/activate the amendment, and later promotion-gate or protocol-enforcement code remains §16 protected.

## What option C still needs from D-18

O18-1 through O18-5 are not complete enough to start qualification. D-18 must additionally supply or bind:

- the complete no-result event, including every mandatory gate’s unavailable state;
- the eligible attempted-cycle denominator and treatment of research-only cycles;
- an auditable unseen-window and information-lineage contract;
- the broadened DSR method and supported-domain classifier;
- complete post-pick and cycle-outcome semantics;
- a whole-procedure held-out-data firewall, not only a frozen threshold;
- exact handling of latent real-world dependence/tails that cannot be classified at declaration;
- complete `H_f` state semantics, including PBO enablement and lockbox technical failure;
- the mixed-null challenge event and what, if anything, it is meant to support;
- the conditional wording of the eventual claim: evidence over named simulation classes, not unconditional market coverage.

## Selection-rule comparison

**Top Sharpe, no fallback** is defensible after the blockers are repaired.

Its benefits are a smaller DSR-stage null event than top-DSR, alignment with the maximum-Sharpe quantity that motivated \(S_0\), deterministic nomination, and at most one downstream/lockbox attempt per family.

Its costs are lost power when a lower-Sharpe trial has a better \(D_j\), \(T_j\), plateau result, interval, or other gate; post-selection point intervals and null tests do not recover ordinary single-test coverage; and one unavailable non-nominee blocks the family.

**Top DSR, no fallback** finds more DSR-passing trials, but its DSR event is broader and it selects partly on noisy skewness, kurtosis and sample-size denominators. It needs separate full-procedure calibration and is less aligned with maximum-Sharpe PBO/penalty motivation.

**Fallback with “any trial passes all gates”** gives the greatest discovery opportunity, but creates the broadest multiplicity, timing, availability and lockbox problem. It can be calibrated in principle, but repeated downstream gates require an explicitly union-calibrated procedure and conflict with the intended one-read discipline.

## Revision-3 finding disposition

| Finding | Revision 4 status |
|---|---|
| FR3-1 | **Partly resolved.** P18-0 chooses unseen data, but the eligibility predicate and window custody are insufficiently operational—SR4-3. |
| FR3-2 | **Unresolved.** O18-2 acknowledges the infeasible current method but supplies no broadened replacement—SR4-4. |
| FR3-3 | **Resolved in direction.** Threshold development and held-out certification are separated; whole-procedure reuse remains SR4-5. |
| FR3-4 | **Resolved.** The N=2 high-correlation lower bound near 1.972 is recorded and the cell is required. |
| FR3-5 | **Resolved.** Availability uses finite pre-Φ `z`, positive finite `D`, and exact `z >= z_crit`. |
| FR3-6 | **Partly resolved.** The missing post-pick contract is acknowledged but still undefined—SR4-6. |
| FR3-7 | **Resolved.** Reruns are forbidden and hash mismatch is a technical failure. |
| FR3-8 | **Resolved.** The PBO dependency now points to O18-6/D-08. |
| FR3-9 | **Resolved.** The matrix dependency reference is corrected to line 79. |
| FR3-10 | **Partly resolved.** The conditional qualifying-cell limitation is disclosed, but actual domination remains unverifiable—SR4-7. |
| SR3-1 | **Resolved.** The owner re-selected declared-plan completion or day 180. |
| SR3-2 | **Resolved for early no-pick.** A no-pick cycle enters the target; SR4-1 identifies a different downstream-unavailability omission. |
| SR3-3 | **Resolved.** Nonempty/budget-valid IDs, hashes, membership and pre-start rejection are specified. |
| SR3-4 | **Partly resolved.** One global decimal threshold and held-out separation are specified; complete procedure freezing remains SR4-5. |
| SR3-5 | **Resolved.** The owner selected a whole-cycle 1% target. Its event is incomplete under SR4-1/SR4-2. |
| SR3-6 | **Resolved.** Finite pre-Φ `z` is the availability and comparison quantity. |

## Review gate

`LOCAL GATE: BLOCKED` for accepting D-18 or beginning option-C qualification.

`10bb125` changes only `PROPOSAL.md`; `git diff --check` passed. The worktree was clean. No application tests, lint, typing, or import-boundary checks applied to this read-only prose review. Frozen verification passed for 28/28 trusted bytes and inventory and 14/14 sidecars before the repository script encountered an old-.NET `Convert.ToHexString` incompatibility; independent read-only checks then passed the Constitution self-hash, 7/7 manifest bindings, 7/7 protocol bindings, and 3/3 nested bindings.

No file was edited or committed. Under repository policy, this review does not become a completed governance record until an authorized actor saves it with the model metadata and every SR4 finding and commits it.

## Eight-line owner summary

1. The basic safety logic is right: promotion requires the one nominated top-Sharpe trial to pass the calibrated DSR screen.
2. Top Sharpe passing is not the same as any trial passing; a lower-Sharpe trial can pass when the nominee fails.
3. The 1% no-result rule misses failures of PBO and other mandatory gates, so a method that never completes can still qualify.
4. “Unseen” must mean data unavailable to strategy selection, not merely that the engine returned no earlier per-trial metric.
5. The promised broadened DSR method does not exist yet, so the required realistic cells cannot be calibrated.
6. The post-pick order, window and cycle outcome are still undefined and can change which family is processed.
7. Top Sharpe with no fallback is defensible, but it deliberately sacrifices viable runner-ups and does not fix post-selection inference.
8. Keep D-18 and option-C calibration blocked until SR4-1 through SR4-6 are repaired and independently re-reviewed.