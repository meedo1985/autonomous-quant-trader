# Sol re-review DS2 of the D-19 preregistration rev 2 at `71357d4`: UNSOUND

Date: 2026-10-04. This is an R19-2 independent statistical re-review by the different model family. The prompt was the same as Fable DF2's, with the ID prefix `DS2`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106ec-52ed-7f21-95d7-78c79b12b761`. The final message is reproduced below unchanged.

---

Model: Codex, OpenAI GPT-5 family; exact served model identifier is not exposed.  
Commit: `71357d465182c5be57815dada7b21155add70a7e`, branch `docs/d19-recommendation`  
Verdict: **UNSOUND**

The exact-null and held-out-seed ideas are sound, but two blockers remain: the two-attempt confidence budget is contradictory, and the claimed cycle-wide `U_proc ≤ 0.01` excludes route-S failures that P18-7 includes.

### Main designs

- **(a) Classifier:** Not yet sound. It is mechanical in outline, but tail directions, estimators and execution order are underdefined; passing still establishes no domination.
- **(b) Q5 sign flips:** Sound in principle. Independent symmetric block signs give conditional `E[X_j,t]=0` exactly. The exact sign process and initialization must be frozen.
- **(c) Route S:** Honest disclosure, but not equivalent to P18-7 certification. A formal amendment may authorize the screen only by explicitly weakening/replacing the whole-cycle availability claim. It cannot simultaneously retain `U_proc ≤ 0.01` over all mandatory gates.
- **(d) Exact-binomial targets:** Sound. The illustrative numbers correctly correspond to 0.99 rather than the frozen 0.999 power. The two-stage development trigger is not sound for rare events.
- **(e) Leg generators:** Improved but incomplete and not yet reproducible; allowed G-12 horizons are not covered.
- **(f) Seeds:** Binding held-out seeds to `qualification_object_sha256` is sound. Exact encodings and the route-S screen seed remain incomplete.

### DF1/DS1 status

| Finding | Status | Concise reason |
|---|---|---|
| DF1-1 | PARTIAL | Impossible route-S bound removed, but route-S real failures remain unbounded. |
| DF1-2 | PARTIAL | Exact targets added; attempt-level α and `M` remain inconsistent. |
| DF1-3 | UNRESOLVED | Stage 1 can miss rare but excessive rates and skip stage 2. |
| DF1-4 | RESOLVED | Pilot subtraction replaced by an exact symmetric sign null. |
| DF1-5 | PARTIAL | Legs exist, but generators and required gate inputs remain incomplete. |
| DF1-6 | RESOLVED | Declaration is restricted to certified `K` values. |
| DF1-7 | RESOLVED | Single-ARFIMA-column challenge cells added. |
| DF1-8 | RESOLVED | Common GARCH factor cells and block-60 sensitivity added. |
| DF1-9 | PARTIAL | Subjective library removed; screen still supplies no availability guarantee. |
| DF1-10 | RESOLVED | G-13 and integrity dispositions are assigned. |
| DF1-11 | UNRESOLVED | Family dimension is not reconciled with the stated `M`. |
| DF1-12 | UNRESOLVED | §§4 and 6 allocate different α to attempt 1. |
| DF1-13 | RESOLVED | Cap-based exclusion and its consequence are disclosed. |
| DF1-14 | PARTIAL | Held-out anchor fixed; screen seed and exact byte encodings remain open. |
| DF1-15 | RESOLVED | Measured pilot is required and estimate widened. |
| DS1-1 | PARTIAL | Classifier exists, but is not a fully specified domination/support rule. |
| DS1-2 | PARTIAL | Joint-leg skeleton added; hourly/strategy and coupling details remain absent. |
| DS1-3 | RESOLVED | Q5 has an exact conditional zero-mean null. |
| DS1-4 | PARTIAL | Impossible estimate removed, but current screen contradicts the total claim. |
| DS1-5 | PARTIAL | Exact target construction works; development and α inputs do not. |
| DS1-6 | UNRESOLVED | No actual disjoint family-labelled manifest; implied `M` is inconsistent. |
| DS1-7 | PARTIAL | Matrix added, but route-S causes are not operationally executable/exhaustive. |
| DS1-8 | PARTIAL | Qualification-object binding fixed; exact serialization remains ambiguous. |
| DS1-9 | RESOLVED | Benchmark pilot is required before compute approval. |

### New findings

| ID | Severity | Location | Problem, evidence, fix |
|---|---|---|---|
| DS2-1 | **BLOCKER** | §4:205–207; §6:240 | §4 says both attempts use `0.025/M`; §6 gives attempt 1 `0.05/M` and attempt 2 `0.025/M`. The latter spends 0.075 across attempts, guaranteeing only 92.5% familywise coverage. Use an α-spending rule totaling 0.05—most simply `0.025/M` for both—and recompute every target. |
| DS2-2 | **BLOCKER** | §1:34–43; §7:250–288; §11:346–353 | §1 claims the cycle bound is ≤0.01, while route-S failure on the real window is expressly an unbounded `U_proc` event. Annex A P18-7 defines `U_proc` over every mandatory pre-lockbox gate. Either calibrate route S, or formally amend P18-7 and DRAFT §2.4 to call the result a partial route-R bound—not cycle-wide `U_proc` certification. |
| DS2-3 | **MAJOR** | §7:280–288; §8 | Q5 supplies daily paths, but actual G-5–G-7, G-11 and G-14 require hourly inputs, stressed execution, signals and model refits. The screen also uses 20/5 draws instead of production 500, and has no seed anchored to a precommitted trial-set hash or retry rule. Specify executable inputs, exact screen semantics, seed and attempt accounting. |
| DS2-4 | **MAJOR** | §3.5:159–180 | “Maximum 99.99th percentile” is wrong/undefined for lower-tail diagnostics such as minimum skewness and possibly correlation. GPH/CUSUM estimators and edge cases are unspecified; `L/T` cannot be computed before Annex B rule 1 as stated. Freeze exact estimators, two-sided thresholds, quantile convention and fail-closed ordering. |
| DS2-5 | **MAJOR** | §5:212–229 | The development trigger is unsafe for rare events. With `n=2,000`, `τ=.0005`, a true `p=.001` produces zero events and skips stage 2 with probability **0.1352**. For `τ=.0013`, `p=.002` skips with probability **0.0914**. Run stage 2 for every rare-share cell or trigger from an exact upper bound rather than the point estimate. |
| DS2-6 | **MAJOR** | §§3.2, 6 | The stated grids imply 201–259 base law cells. Three bounds for both families imply `M=1,206–1,554`, not roughly 750–1,000, unless one family is silently omitted. Enumerate both families per law cell and derive `M`, α, targets and cost from the actual manifest. |
| DS2-7 | **MAJOR** | §3.1:91; Annex C C-11 | Calibration fixes G-12 to `H=24`, while decided trials allow `H∈{24,72,168}`. Bartlett bandwidth and availability can depend on `H`. Certify every allowed horizon or formally restrict declarations. |
| DS2-8 | **MAJOR** | §§3.1–3.4, 8 | Generator-identifying choices remain open: skew-t parameterization, AR/GARCH initialization and burn-in, factor-loading draw timing, BTC/ETH `X` coupling, EWMA initialization, and concatenation encodings. The claimed `>1−10⁻⁹` positive-equity probability is also unsupported for unbounded t/GARCH laws. Bind these choices before development and remove or prove that probability claim. |

### Commands run

- Read-only `rtk git show`, `git grep`, `git diff`, `git diff-tree`, `git status`, `git rev-parse`, `git ls-tree`, and `git diff --check`.
- In-memory `.venv\Scripts\python.exe` checks for exact binomial targets, CP thresholds, stage-1 miss probabilities, cell counts and t₅ tail arithmetic.
- Tracked working and cached diffs were empty. Commit `71357d4` changes only the preregistration and adjudication records.
- No network, edits, commits, pushes, confirmation/lockbox reads, or access inside `data/`. Tests/lint/type checks are N/A for this document-only review.

Because read-only was required, this response is not a completed repository review record until an authorized party commits it.

The exact sign-flip null and qualification-hash seed anchor are good improvements.  
The present text still cannot certify both-attempt 95% coverage or a whole-cycle 1% no-result rate.  
Do not accept revision 2 until DS2-1 and DS2-2 are repaired and the major specifications are closed.
