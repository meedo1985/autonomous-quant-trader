# Sol High review of the broadened DSR method design rev1 at `6481f28` — UNSOUND as written

Date: 2026-10-03. OpenAI-family review for R19-2; run in parallel with, and
without sight of, the Fable review.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a100bf-146c-7a22-956e-2344d9cb1e98`;
  tokens used 124,715; exit 0. (Self-report names only "GPT-5"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `773e30e`) with `{{PREFIX}}`
  replaced by `SB1` (substituted file SHA-256
  `cf7effddea2d5111fac30dc50504818af1b3413b8520973d2dceea03f2a6b817`).
- Findings: SB1-1..SB1-4, SB1-9 BLOCKER; SB1-5..SB1-8 NON-BLOCKING. Nothing
  is decided by this record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

Model: GPT-5, OpenAI Codex family; exact deployment identifier is not exposed in this session.  
Commit reviewed: `6481f289e45a916d204a67cfc2bd2e38fb9f7131`  
Verdict: **UNSOUND as written**

The joint recentered stationary bootstrap is a defensible candidate for estimating `S0` under a global, shift-to-zero null, subject to short-memory stationarity, adequate moments, controlled `K/T`, and end-to-end calibration. It does not, as specified, estimate the claimed nominee-Sharpe variance `D`.

| ID | Severity | Location | Concrete scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| **SB1-1** | **BLOCKER** | `DESIGN.md` §2.4, lines 79–89 | All replicates use recentered `Y`, so `D` estimates Sharpe variance at null Sharpe zero—not generally at the nominee’s observed/nonzero Sharpe. Let `Z=1−Exp(1)` and `X=Z+0.5`. Then `S=0.5`, skew `g=−2`, kurtosis `k=9`, and the decided moment scale is `D=1−gS+((k−1)/4)S²=2.5`. Recentring gives `Y=Z`, `S=0`, and asymptotic bootstrap scale `D=1`. Calling this “nominee’s Sharpe variance” understates it by 60% and inflates `z` by `sqrt(2.5)=1.5811`. | Use recentered resamples for `S0`, but uncentered resamples—or residuals with the original mean restored—for nominee `D`. Alternatively rename it a *null variance scale* and establish the resulting statistic solely through full calibration; do not claim it is the original `D`. |
| **SB1-2** | **BLOCKER** | §1, §2.2–2.5, §5 | The proposal says one construction fixes serial dependence and heavy tails, but the guarantee is conditional. Stationary bootstrap validity is not established here for long memory, nonstationarity/regime changes, infinite variance, or infinite-fourth-moment Sharpe inference. The proposal itself admits that infinite-fourth-moment bootstrap validity is not guaranteed. Empirical resampling also cannot generate tail events beyond the observed sample. | Restrict the supported domain to an explicit stationary, short-range-dependent, finite-moment class justified by D-19. Treat long memory, structural breaks, and infinite-fourth-moment laws as challenge or unavailable cases until a separate method is validated. |
| **SB1-3** | **BLOCKER** | §2.3, §2.6 item 4 | “Largest PW length is conservative” is false in general: longer blocks do not monotonically increase uncertainty, especially with negative or oscillating autocovariances. Taking the maximum over up to 80 noisy univariate selectors also introduces a `K`-dependent extreme-selection effect. Moreover, the cited implementation caps `L` at `ceil(3√T)` for `T≥365`; at `T=365`, `L≤58<T/4=91.25`. Thus `L>T/4` is unreachable after the cited clipping and supplies no protection. | Remove the conservative claim. Specify and validate a statistic-targeted multivariate/common block selector, or openly classify “largest univariate PW” as a calibrated heuristic. State whether the `T/4` test applies to raw or already-clipped length. |
| **SB1-4** | **BLOCKER** | §2.3 and §2.6; `statistics.py:443–465` | The reason precedence is ordered and fail-closed only after assuming a valid family matrix and stream. It is not total: no family-level seed identity is defined although the existing stream is keyed by one `trial_seed_hex`; the proposed purpose `"dsr_family_max_null"` is rejected by the cited `ReplicateStream`; declaration/count/ID errors are not incorporated into this contract. `T_min=365` is an uncalibrated calendar threshold and says nothing about effective information under dependence. | Define a canonical family seed from the complete ordered declaration/hash, bind its convention hash and runtime identity, extend the permitted purpose explicitly, and state inherited declaration checks and cause precedence. Select `T_min` through preregistered development evidence, not an AI default. |
| **SB1-5** | **NON-BLOCKING** | §3, B-1/B-2 | With a complete current-cycle matrix, the joint maximum directly represents current declared-set multiplicity, so an effective-count scalar is unnecessary. Under P18-0, using only the declared current-cycle family is coherent for the decided *per-cycle* error event. What is lost is any lifetime-familywise error claim, protection against adaptation through public/history knowledge, and a score penalty for earlier searches. C2’s public-history weakness remains unverifiable. | Accept D-16/D-17 only with the narrow wording “per eligible cycle, conditional on the declared set and supported law.” Continue mandatory lifetime accounting and reporting; explicitly disclaim lifetime error control. |
| **SB1-6** | **NON-BLOCKING** | §4 B-3; D-18 O18-2/P18-6 | Redefining `D` changes the method materially, but D-18 O18-2 expressly left the broadened method’s equation/count/dispersion for later specification. It need not reopen D-18’s top-Sharpe nomination, global-null event, or per-family targets. It does require an explicit owner method decision and amendment; “formula unchanged” is misleading because the statistic’s numerical meaning changes. | Keep D-18’s selection/error decision closed, but treat the definition of `D` as an open method/amendment component. Resolve SB1-1 before that decision. |
| **SB1-7** | **NON-BLOCKING** | §2.3–2.4, §5 | `B=2000` is not negligible error. Even for Gaussian replicates, the sample-variance estimator has approximate relative SD `sqrt(2/1999)=3.163%`; the corresponding SE has about `1.582%`. For `S0`, Monte Carlo SE is `sd(M*)/sqrt(2000)`. Heavy-tailed replicate statistics can be much noisier. | Calibration must rerun the exact 2,000-replicate inner algorithm, including seed construction, block selection, invalid replicates, and shared estimation of `S0` and `D`, inside every outer replication. Otherwise add an explicit Monte Carlo margin or increase `B`. |
| **SB1-8** | **NON-BLOCKING** | §3 cross-cycle risk | `1−0.95^m` applies only if cycles are independent and each attains exactly 5%. Spacing cycles years apart does not establish independence. From per-cycle control alone the general union bound is `min(1,0.05m)`; after 10 cycles these are respectively `40.13%` and `50%`. Reporting does not control accumulation. | Report both the independence illustration and the assumption-free union bound. State that no lifetime guarantee exists unless the owner later adopts alpha spending, an overall cycle cap, or another calibrated sequential rule. |
| **SB1-9** | **BLOCKER** | §5 calibration | The list of scenarios is not yet a qualifying calibration contract. Missing items include the exact supported-law classifier/dominance rule, null location-shift assumption, `K/T` boundary, long-memory and regime-change disposition, tuning/freeze order for `T_min` and block rules, family seed derivation, nested-bootstrap randomness, simultaneous confidence family, outer replication budget, and separate power/mixed-null reporting. Infinite-fourth-moment laws cannot simultaneously be “qualifying” while validity is expressly unestablished. | Write D-19 as a complete preregistration, tune only on development replications, freeze the entire algorithm and support classifier, and then use untouched held-out seeds. Keep unsupported laws as challenges, not qualifying cells. |

### Defects from §1

| Defect | Result |
|---|---|
| AS-1, unequal clusters/dependence | Substantially removed for the current declared family if the joint bootstrap is valid; contemporaneous pairing and exact duplicates are retained. |
| AS-2, lifetime `N` with current `K` | Avoided by changing scope, not statistically solved. Lifetime error accumulation remains. |
| AS-3 / P-7, `K=1`, duplicates, `V=0` | The cross-sectional-dispersion failures are removed. Missing current attempts still fail `A_f`, and invalid bootstrap replicates can still cause unavailability. |
| Serial dependence | Addressed only for sufficiently stationary short-memory dependence and a valid common block rule. |
| Heavy tails | Finite-sample empirical tails are represented, but the general heavy-tail claim remains unsupported; infinite-fourth-moment and more extreme cases remain unresolved. |
| Recentering | Appropriate for a shift-to-zero global-null `S0`; inappropriate for the claimed nonzero-nominee variance `D`. |

### Calculation record

The in-memory calculation used Python 3.14.7 and wrote no files:

```text
Shifted negative exponential:
S = 0.5, g = -2, k = 9
D_original = 1 - (-2)(0.5) + ((9-1)/4)(0.5²) = 2.5
D_recentered-null = 1
z inflation = sqrt(2.5/1) = 1.5811388301

B = 2000, Gaussian variance estimate:
relative SD(var) ≈ sqrt(2/(B-1)) = 0.0316307
relative SD(SE)  ≈ 0.5*sqrt(2/(B-1)) = 0.0158153

At T = 365:
cited implementation cap = ceil(3*sqrt(365)) = 58
T/4 = 91.25
therefore the proposed L > T/4 rejection cannot occur.
```

No external methodological claims were network-verified, as required by the review restriction. The working tree remained clean. Because the user prohibited writes and commits, this response is not yet a committed R19-2 review record; an authorized party must preserve and commit every finding before it can count as the required governance review.

### Eight-line owner summary

- The joint bootstrap is a promising way to measure the current family’s null maximum.
- The same recentered bootstrap does not measure the nominee’s claimed Sharpe variance.
- A simple skewed-return example makes the resulting z-score 1.58 times too large.
- Serial dependence is covered only when it is stationary and short-lived.
- Long memory and very heavy tails remain unsupported.
- The largest-block and one-year defaults are not scientifically justified yet.
- Dropping lifetime count is reasonable only for a per-cycle claim, not lifetime safety.
- Keep promotion blocked until the method, support boundary, and held-out calibration are revised.