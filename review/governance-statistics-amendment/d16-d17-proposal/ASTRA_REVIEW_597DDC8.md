# Astra review of the D-16/D-17 proposal at `597ddc8` — UNSOUND as written

Date: 2026-10-02. Requested by the owner ("yes start the Astra review"), as
the second, non-Claude model-family review required by the owner's step-0
decision R19-2 (`../d19-recommendation/OWNER_STEP0_DECISION.md`).

- Invocation: `codex exec -s read-only -m gpt-6-astra -o <last> - < review/governance-statistics-amendment/d16-d17-proposal/ASTRA_PROMPT_597DDC8.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-6-astra`; sandbox read-only;
  reasoning effort high; session id `01a0fe23-1850-7af2-ade5-edd1cf5542de`;
  tokens used 107,047; exit 0.
- Checkout HEAD at run time: `ac5f973` (`597ddc8` plus the prompt). Prompt
  SHA-256: `80572ac82e63eae80957ef39cc8065d8a7db9529fea759caf2a12337a2910751`.
- Findings: AS-1, AS-2, AS-3 BLOCKER; AS-4, AS-5, AS-6 NON-BLOCKING. AS-5
  and AS-6 concern `../d19-recommendation/RECOMMENDATION.md`. Nothing is
  decided by this record; the owner decides.

Below is the reviewer's final message, verbatim.

---

**Reviewer:** GPT-6 Astra (`gpt-6-astra`), OpenAI model family; identity from this session, not independently verified through provider metadata.  
**Reviewed commit:** `597ddc84597e15bfd5f9af84963e71b1ed0ab494`, branch `docs/d19-recommendation`. Actual working HEAD was `ac5f973`, whose only addition was `ASTRA_PROMPT_597DDC8.md`.  
**Mode:** Read-only. No network, credentials, confirmation/lockbox data, edits, commits, or pushes.

**Verdict: UNSOUND as written as a justification for unconditional raw-count deflation.** Lemma 1 is correct within its domain, and raw lifetime attempts remain a reasonable **candidate for evaluation**. The universal “mean-correct” and “double counting” conclusions are false. The packet’s `KEEP_BLOCKED` disposition is appropriate.

This review closes no D-row. Under `OWNER_STEP0_DECISION.md` R19-2, it supplies the second model-family review; the owner decides. The recorded replacement of the human-statistician check is acknowledged.

**1. Lemma 1 and its generalization**

Write \(K=N\ge2\), \(\sigma>0\), \(P=I-\mathbf1\mathbf1^\top/N\), and

\[
X=\sigma\sqrt{1-\rho}\,Pe+bW\mathbf1,\qquad
b^2=\frac{\sigma^2[1+(N-1)\rho]}N,
\]

where \(e\) has independent standard-normal coordinates and \(W\) is an independent standard normal. Then

\[
\operatorname{Cov}(X)=\sigma^2[(1-\rho)I+\rho\mathbf1\mathbf1^\top].
\]

This construction works throughout \(-1/(N-1)\le\rho<1\), including the negative boundary. Also,

\[
\max_jX_j=\sigma\sqrt{1-\rho}(\max_je_j-\bar e)+bW,
\]

and

\[
V=\frac{\sigma^2(1-\rho)}{N-1}\|Pe\|^2,\qquad
\|Pe\|^2\sim\chi^2_{N-1}.
\]

Consequently,

\[
E[\max X]=\sigma\sqrt{1-\rho}\,E[M_N],
\]

\[
E[\sqrt V]=\sigma\sqrt{1-\rho}\,c_4(N),\quad
c_4(N)=\sqrt{\frac2{N-1}}\frac{\Gamma(N/2)}{\Gamma((N-1)/2)},
\]

which proves the stated ratio. No independence between the maximum and dispersion is needed for this ratio of expectations.

**Qualifications:** This requires the same \(N\) observations in the maximum, dispersion, and multiplier. At \(\rho=1\), an admissible covariance boundary expressly excluded by the packet, both expectations are zero and their ratio is undefined. \(N=1\) is also outside the lemma.

Independent numerical integration reproduced:

| N | \(c_4(N)A(N)/E[M_N]\) |
|---:|---:|
| 2 | 0.735045057 |
| 3 | 0.893054780 |
| 4 | 0.941677292 |
| 5 | 0.963934167 |
| 12 | 0.998910098 |
| 13 | 1.000158421 |
| 81 | 1.006811766 |

Thus “mean-correct” means approximately correct **under these assumptions**, not exactly unbiased. Even here, the exactly mean-matching count for \(N=100\) is **95.384911533**, contradicting the literal assertion that *any* smaller count double-counts dependence.

More importantly, the generalization fails:

| Construction, \(N=K=81\) | \(E[\max X]\) | \(E[S_0]\) | Ratio |
|---|---:|---:|---:|
| 80 copies of \(Z\), one independent \(W\) | 0.564189584 | 0.307866179 | 0.545678594 |
| 80 copies of \(Z\), one \(-Z\) | 0.797884561 | 0.435388525 | 0.545678594 |
| 80 copies of \(0.1Z\), one \(Z\) | 0.359048052 | 0.195924836 | 0.545678594 |

Here \(Z,W\) are independent standard normals.

For the first construction,

\[
V=(Z-W)^2/81,\qquad
E[\sqrt V]=2/\sqrt{81\pi},\qquad
E[\max(Z,W)]=1/\sqrt\pi.
\]

Therefore the ratio is \(2A(81)/9=0.545678594\). This is an **equal-variance Gaussian counterexample with only nonnegative correlations**.

It is not a singular-matrix artifact. Set

\[
X_i=(Z+0.1e_i)/\sqrt{1.01}\quad(i\le80),\qquad X_{81}=W,
\]

with independent standard normals. The correlation matrix is positive definite; within-block correlation is \(0.990099\). Then

\[
E[V]=\frac{2/81+0.01}{1.01},
\]

so Jensen’s inequality gives

\[
E[S_0]\le0.455092203
<0.564189584
=E[\max(X_1,W)]
\le E[\max_jX_j].
\]

Conversely, the packet’s **balanced** three-cluster example is conservative: \(E[S_0]=1.787912489\) versus \(E[\max]=0.846284375\). A reduced multiplier count of **4.758284326**, rather than 81, matches its mean. Therefore reducing a count need not double-count dependence.

The third table row supplies a heteroscedastic Gaussian counterexample with every marginal variance positive. Non-Gaussian generalization also fails. For 81 independent standardized Bernoulli variables,

\[
X_j=(B_j-p)/\sqrt{p(1-p)},\qquad p=0.001,
\]

exact binomial summation gives \(E[\max]=2.431226493\), but \(E[S_0]=0.682938636\).

For a fat-tailed **score-vector** counterexample, multiply the first Gaussian construction by an independent positive \(L=\sqrt{3/U}\), \(U\sim\chi^2_5\). Marginals then have standardized \(t_5\) distributions. Both expectations multiply by \(E[L]\), so the same 0.545679 ratio remains. This does **not** establish a finite-sample Sharpe law for \(t\)-distributed returns: the Gaussian approximation for trial Sharpes, serial dependence, and moment estimation need their own validation.

Finally, the sign-spectrum objection remains valid, including after accounting for \(V\). A vector containing \(m\) copies of \(Z\) and \(81-m\) copies of \(-Z\) always has correlation spectrum \((81,0,\ldots,0)\), but

\[
\frac{E[S_0]}{E[\max]}
=2A(81)\sqrt{\frac{m(81-m)}{81\cdot80}}.
\]

This equals **0.545679** for \(m=1\) and **2.470665** for \(m=40\). A spectrum-only count cannot universally repair the normalized mean either.

**2. Mean matching versus pass/fail calibration**

Mean matching is a useful diagnostic of the proposed penalty. It is not the criterion that establishes an error-rate claim.

For a declared selection rule \(J\), the relevant event is

\[
P_0\!\left[
\frac{(S_J-\sqrt V A(N))\sqrt{T-1}}{\sqrt{D_J}}
\ge \Phi^{-1}(0.95)
\right],
\]

including the actual random dispersion, candidate-specific denominator, missing-result rules, and selection procedure. D-18 must distinguish this from “some candidate passes”; those events can differ.

Equicorrelation itself demonstrates the distinction: the lemma’s mean ratio is independent of \(\rho\), whereas R19-5’s false-pass probabilities vary substantially with \(\rho\).

I reproduced R19-5 and found a small methodological labeling error:

| \(\rho\) | Uncertainty multiplier | Using \(\sqrt{E[V]}\): reproduces R19-5 | Using \(E[\sqrt V]\): stated in R19-5 |
|---:|---:|---:|---:|
| 0 | 1 | 0.1669% | 0.1725% |
| 0.3 | 1 | 0.7739% | 0.7925% |
| 0.6 | 1 | 2.2505% | 2.2816% |
| 0.9 | 1 | 4.2454% | 4.2683% |
| 0 | 2 | 4.1470% | 4.2586% |
| 0 | 2.2 | 5.3571% | 5.4974% |

Neither column evaluates the full random-\(V\) procedure. These are illustrative Gaussian calculations, not calibration results for the repository gate.

A directly integrable small-N example is stronger. In standardized Gaussian score units, with correctly specified unit individual uncertainty, two equicorrelated trials satisfy

\[
\max X-A(2)\sqrt V
=
\sqrt{\frac{1+\rho}{2}}Z+
\sqrt{1-\rho}\left(\frac1{\sqrt2}-A(2)\right)|Q|,
\]

with independent standard normals \(Z,Q\). Integrating its upper tail at \(z_{0.95}\) gives:

| \(\rho\) | Raw \(A(2)\) | R-16b multiplier \(1/\sqrt2\) |
|---:|---:|---:|
| 0 | 1.84866% | 1.00046% |
| 0.9 | **5.07138%** | 4.57455% |

The \(\rho=0.9\) result reproduced as 0.0507137634 and 0.0507137635 on successively finer grids.

This is an exact Gaussian score-model calculation, and a large-sample normal-return limit where the Sharpe denominator tends to one—not a finite-\(T\) calibration claim. It proves that the unguarded small-N formula lacks even a universal 5% guarantee in that simple setting.

**3. D-17: lifetime, cycle, and usable counts**

**Non-binding preference: retain raw lifetime family attempts as the candidate input to \(A(N)\).** It best respects persistent accounting and avoids making crashes or cycle resets reduce the recorded search history.

However:

- Constitution §5 requires lifetime counts to persist; it does not explicitly bind them into \(A(N)\).
- The ledger must retain failures, evaluated aborts, actual reruns, and invalidated-cycle attempts. Event redelivery must not create another attempt.
- \(K\) measures available vectors; it is not a substitute for that attempt count.
- The proposal’s confirmation-only scope and lockbox exclusions need explicit owner binding, including the accounting cutoff.
- Per-family accounting does not establish a cross-family or lifetime false-pass bound.

**The lemma does not validate \(A(N_{\rm lifetime})\sqrt{V_K}\).** Even assuming all lifetime scores were independent, homogeneous normals and the current \(K\) were an unbiased subset,

\[
E[S_0]=\sigma c_4(K)A(N_{\rm lifetime}),
\]

not \(\sigma c_4(N_{\rm lifetime})A(N_{\rm lifetime})\).

For \(N_{\rm lifetime}=81,\ K=2\), its ratio to the hypothetical lifetime maximum’s mean is **0.805833799**. This calculation does not identify the correct cross-cycle selection event; it shows why the lemma cannot justify the proposed substitution.

Counts and current dispersion cannot reconstruct historical selection dependence. The same current pair with correlation 0.9 and the same lifetime count 81 can coexist with:

- an entirely equicorrelated lifetime family: \(E[\max_{\rm lifetime}]=0.768854240\); or
- 79 independent historical trials: \(E[\max_{\rm lifetime}]\ge2.422153926\).

The available current inputs are identical. No forbidden pooling is needed to expose this non-identifiability.

There is also a concrete non-monotonicity: scores \((0,1)\) give \(S_0=0.367522528\); adding 79 copies of the zero score gives \(S_0=0.272839297\), with the same maximum. Increasing the attempt count raises the multiplier **holding V fixed**, but the whole procedure need not become stricter when more trials change V.

Prior-cycle history, incomplete outcomes, adaptation, and duplication therefore need supported-domain and calibration decisions. They cannot be handled by simply removing P-7’s unavailable branches.

**4. Small N, K, and unavailable dispersion**

The packet correctly identifies small-N mean bias. Its proposed handling is incomplete for acceptance.

| Case | Review conclusion |
|---|---|
| \(N_{\rm lifetime}=N_{\rm cycle}=K=1\) | A separate \(S_0=0\) branch is mathematically coherent. Do not evaluate \(A(1)\) or estimate cross-trial variance. It still needs separate calibration. |
| \(K=1\), multiple lifetime/current attempts | Dispersion is unidentified. Do not convert this into the single-attempt branch. |
| \(N=K=2,\ldots,5\) | Raw mean ratios are 0.735045, 0.893055, 0.941677, 0.963934. |
| \(V=0\), missing, or nonfinite | Preserve an explicit unavailable outcome unless an separately specified and validated branch is adopted. Do not silently use zero, epsilon, clipping, or imputation. |
| \(K<N\) | The missingness mechanism and count/dispersion mismatch remain relevant even when \(K\ge2\). |

R-16b’s correction

\[
\max\{A(N),E[M_N]/c_4(N)\}
\]

fixes the downward **mean** bias under the matched equicorrelated Gaussian model. It is not a general dependence correction, missing-dispersion solution, or tail-probability guarantee. It does nothing to the N=81 counterexamples.

Nor does a negative mean bias automatically imply a false-pass rate above 5%: the N=2 independent example above passes only 1.84866%. The packet should distinguish “underestimates the expected maximum” from “violates a stated error-rate limit.”

For rejected effective-count alternatives, a further boundary matters: \(A(N)\to-\infty\) as \(N\downarrow1\); for example \(A(1.1)=-0.317619\). A continuous effective count near one cannot safely inherit an integer single-attempt branch without explicit rules.

**5. Frozen method and amendment scope**

Unconditional raw-count use replaces the primary method named at `protocol_v1.yaml:232`; the presence of a raw-count fallback at line 233 does not itself authorize that replacement.

Constitution §9’s “if no frozen effective-count method exists” leaves a real interpretive question because a method is named but not defined. P-16’s proposed T-16 should not present one interpretation as already settled.

Also, **the equation and cross-sectional V are in an unaccepted `METHOD_CANDIDATE.md`, not frozen protocol text**. The packet repeatedly calls them the “frozen formula” or “frozen cross-sectional V.” That is incorrect authority labeling.

Possible wording, **AI proposal only**, for the owner to consider:

> For the successor protocol’s proposed DSR method, replace the eigenvalue-based primary method and raw-count fallback arrangement with an explicitly specified raw-attempt-count method. Its multiplier input is the family’s lifetime number of registered confirmation evaluation attempts begun by the declared accounting cutoff, including failures, evaluated aborts, actual reruns, and attempts from invalidated cycles. Event redelivery is counted once. Its dispersion uses only the specified usable current-cycle vectors, without pooling prior-cycle matrices. This count is not claimed to be a universally mean-correct effective count or a calibrated error rate.

This is **not a complete amendment**. The owner would also have to bind:

- the full equation and supported domain;
- counting scope, authoritative ledger, and cutoff;
- missing-history, zero-dispersion, and small-N branches;
- D-18’s selection/error event and D-19’s claim and calibration requirements;
- activation and unavailable-result behavior.

Section 4 requires the versioned, owner-authored, signed/dated change, cycle termination, preserved history, and activation before the next cycle. As R19-4 states, the contemplated successor is **C2**. Closing D-16/D-17 does not resolve D-05, D-06, D-11, D-14, D-15, or D-18, or authorize a cycle or promotion.

**6. Disposition of P-1 through P-12**

| Finding | Assessment |
|---|---|
| **P-1** | **Agree.** For symmetric correlation \(R\), \(\sum\lambda_i^2=\operatorname{tr}(R^2)=\sum_{ij}R_{ij}^2\). Eigenvalue participation ratio and the squared-correlation expression are identical. |
| **P-2** | **Disagree as written.** Some reductions double-count dependence under the equicorrelation model; *every* effective count does not. The balanced-cluster mean-matching count 4.758284 and N=100 count 95.384912 are counterexamples. |
| **P-3** | **Agree with qualification.** The stated small-N mean deficit is reproduced. Call it mean underestimation, not an established tail-error conclusion. R-16b is model-specific. |
| **P-4** | **Agree within stated Gaussian assumptions.** The bound follows from \(E\max X_i\le \log(N)/t+\sigma^2t/2\), minimized over \(t>0\). It is not a generic finite-variance/fat-tail bound. Actual antithetic grid returns remain unestablished: clipping, costs, banding, and holding rules prevent assuming exact proportionality from vol targets alone. |
| **P-5** | **Agree that the curriculum needs correction; qualify the replacement.** Inverting an independent maximum using marginal scale cannot simply be combined with cross-sectional V. But this does not prove all effective-count approaches wrong or raw N universally correct. |
| **P-6** | **Agree for attempt accounting; qualify legal inference.** K cannot represent all begun attempts. Frozen accounting alone still does not explicitly bind the multiplier argument; that is D-17. |
| **P-7** | **Agree.** The inherited unavailable branches exclude the cases the expanded proposal seeks to handle. Their revision requires statistical support, not deletion to make outputs available. |
| **P-8** | **Agree.** Family scope, lockbox inclusion, attempt identity, and competing count sources require decisions. `attempts.py:423–425` and `review/attempt-counting/OWNER_REVIEW.md:65` additionally show that “lifetime” spans only the supplied ledger; global persistence is not guaranteed by this function. |
| **P-9** | **Partly agree.** D-16 and D-17 must be designed together. No pooling prevents reconstructing a full lifetime correlation matrix from current vectors; it does not mathematically prohibit every possible current-matrix/lifetime-count hybrid. Such a hybrid would need its own definition and validation. |
| **P-10** | **Agree with the blocking conclusion; update the historical explanation.** R19-2 replaces the statistician process, and R19-1 lifts the September 18 pause for design work. The contemplated amended cycle is C2; other blocking rows remain. |
| **P-11** | **Agree.** The additional citations are relevant, but do not independently settle D-17. |
| **P-12** | **Agree.** Neither the packet nor the numerical check calibrates the 0.95 threshold. |

Additional issues are recorded below rather than silently folded into these dispositions.

**Findings**

For reproduction references: **Command A** is the existing script command shown below. **Command B** is the supplied in-memory Python verification block, run through `.venv/Scripts/python.exe -B -`. All results below were reproduced; no findings were repaired.

| ID | Severity | Location and concrete scenario | Evidence / reproduction | Proposed disposition |
|---|---|---|---|---|
| **AS-1** | **BLOCKER** | `PROPOSAL_PACKET.md` §2, §3 VC-2, P-2: universal raw-count and double-counting conclusions fail for unequal cluster sizes. | **Yes**, B: 80 copies plus one independent trial gives `0.564189584 0.307866179`; positive-definite near-duplicates retain the failure. | Restrict the lemma-based claim. Reject universal mean-correction language; evaluate unequal clusters and duplicates explicitly. |
| **AS-2** | **BLOCKER** | `PROPOSAL_PACKET.md` §4 R-17: lifetime N with current K is justified using a matched-N theorem. | **Yes**, B: lifetime 81/current K=2 yields mean ratio `0.805833799` against the specified IID lifetime reference. Fixed-score duplication lowers S0 from `0.367522528` to `0.272839297`. | Keep lifetime accounting; separately define and validate the count/dispersion/selection combination and missing-history treatment. |
| **AS-3** | **BLOCKER** | `PROPOSAL_PACKET.md` R-16b/P-3/P-7; `METHOD_CANDIDATE.md` §3.5: finite-sample and availability branches remain unbound. | **Yes**, A/B and source inspection: N=2 mean ratio `0.735045057`; actual-V Gaussian \(\rho=.9\) false-pass rate `5.07138%`; K=1 leaves denominator K−1 zero. | Resolve branches before acceptance. Describe R-16b as a limited mean correction, not calibration. |
| **AS-4** | **NON-BLOCKING** | `PROPOSAL_PACKET.md` §§2–3 and authority preamble: candidate equation is called frozen; fallback interpretation and obsolete STAT requirement appear settled. | **Yes**, `git show 597ddc8:protocols/protocol_v1.yaml` shows eigenvalue primary/raw fallback; `METHOD_CANDIDATE.md:3` says not accepted/not active; owner step-0 record replaces STAT. | Correct authority labels and use an explicit owner-authored successor amendment. No frozen violation occurred in this read-only proposal. |
| **AS-5** | **NON-BLOCKING** | `RECOMMENDATION.md` R19-5: “√V replaced by its expected value” does not match the reported numbers. | **Yes**, B: at \(\rho=.6\), \(\sqrt{EV}\) gives `2.2505%`; \(E\sqrt V\) gives `2.2816%`. | Correct the plug-in description; retain the illustrative-only qualification. |
| **AS-6** | **NON-BLOCKING** | `RECOMMENDATION.md` §2 proposed interpretation: “failed to falsify a non-positive incremental Sharpe” reverses the statistical direction. | **Yes**, formula check: a one-trial standardized statistic 2 gives score `0.977249868` and one-sided zero-null p-value `0.022750132`. A high score is evidence against a non-positive null under that model. | Say “passed the specified incremental-performance screen under its assumptions,” without claiming posterior probability or calibrated error control. |

AS-1 through AS-3 block accepting this justification as a usable gate method. They do not prohibit further proposal work.

**Reproduction and validation record**

Existing check:

```powershell
.venv/Scripts/python.exe -B review/governance-statistics-amendment/d16-d17-proposal/check_numbers.py
```

Exit 0. The displayed results reproduced `NUMBERS_CHECK.md`, including the **2.42**, rather than 2.43, N=243/v=1 hurdle. This check reproduces arithmetic, not validity.

Independent verification used Python **3.14.7**, NumPy **2.5.3**, Windows AMD64. The following core checks run entirely in memory:

```python
import math
from statistics import NormalDist
import numpy as np

F = NormalDist()
g = 0.5772156649015329
A = lambda n: ((1-g)*F.inv_cdf(1-1/n)
               + g*F.inv_cdf(1-1/(n*math.e)))
c4 = lambda n: math.sqrt(2/(n-1))*math.exp(
    math.lgamma(n/2)-math.lgamma((n-1)/2))

x = np.linspace(-12, 12, 200001)
pdf = np.exp(-x*x/2)/math.sqrt(2*math.pi)
Phi = lambda v: np.array([F.cdf(float(t)) for t in v])
cdf = Phi(x)
EM = lambda n: float(np.trapezoid(x*n*pdf*cdf**(n-1), x))

for n in (2, 3, 4, 5, 12, 13, 81):
    print("mean", n, f"{c4(n)*A(n)/EM(n):.9f}")

print("block",
      f"{1/math.sqrt(math.pi):.9f}",
      f"{2*A(81)/math.sqrt(81*math.pi):.9f}")
print("near-duplicate",
      f"{A(81)*math.sqrt((2/81+.01)/1.01):.9f}",
      f"{1/math.sqrt(math.pi):.9f}")
print("duplicate-fixed",
      f"{A(2)/math.sqrt(2):.9f}", f"{A(81)/9:.9f}")
print("lifetime81-K2",
      f"{c4(2)*A(81)/EM(81):.9f}")

for rho, scale in [(0,1),(.3,1),(.6,1),(.9,1),(0,2),(0,2.2)]:
    results = []
    for sd_factor in (1, c4(81)):
        h = math.sqrt(1-rho)*sd_factor*A(81) + F.inv_cdf(.95)/scale
        p = (1-F.cdf(h)**81 if rho == 0 else
             float(np.trapezoid(
                 pdf*(1-Phi((h-math.sqrt(rho)*x)
                            /math.sqrt(1-rho))**81), x)))
        results.append(f"{100*p:.4f}%")
    print("R19", rho, scale, *results)

u = np.linspace(0, 12, 40001)
du = np.exp(-u*u/2)/math.sqrt(2*math.pi)
for rho in (0, .9):
    results = []
    for a in (A(2), 1/math.sqrt(2)):
        t = (F.inv_cdf(.95)
             - math.sqrt(1-rho)*(1/math.sqrt(2)-a)*u
             )/math.sqrt((1+rho)/2)
        p = np.trapezoid(2*du*(1-Phi(t)), u)
        results.append(f"{100*p:.5f}%")
    print("actual-V-N2", rho, *results)
```

Run as a PowerShell here-string piped to `.venv/Scripts/python.exe -B -`. Key outputs:

```text
block 0.564189584 0.307866179
near-duplicate 0.455092203 0.564189584
duplicate-fixed 0.367522528 0.272839297
lifetime81-K2 0.805833799
actual-V-N2 0 1.84866% 1.00046%
actual-V-N2 0.9 5.07138% 4.57455%
```

Read-only gate checks:

- `git diff --exit-code` and `git diff --cached --exit-code`: clean.
- `git status --porcelain=v1 --untracked-files=all`: clean; Git warned that a user-level ignore file was inaccessible.
- All 28 tracked files under the frozen-area paths, including `FROZEN_HASHES.json`, matched reviewed-commit bytes.
- All 13 frozen-area SHA-256 sidecars matched; all seven raw-file manifest bindings, the Constitution canonical self-hash, and seven protocol header bindings matched.
- This establishes consistency with `597ddc8`, not preservation against an independently trusted historical baseline.
- Application tests, lint, type, and import-boundary checks: **N/A**, because no application code or artifact was changed. Numerical verification was applicable and completed.
- Statistical-binding, quant, reproducibility, curriculum, and task-gate review instructions were applied. No additional model review was launched.
- Initial read/check commands encountered a console-encoding error and an incorrect threat-model filename; both were corrected. Neither represented a repository defect.

**Non-binding recommendations**

**D-16: REVISE.** Retain raw attempts as a simple candidate to evaluate, replacing the spectral method only through an explicit amendment. Remove the universal mean-correction argument. Keep gate acceptance blocked pending supported-domain, small-N, availability, and whole-procedure evidence.

**D-17: REVISE, with a preference for lifetime family attempts.** Preserve lifetime accounting and current-cycle-only matrices. Treat their combination in the score as a separate statistical specification, not a consequence of Lemma 1. Resolve it together with D-18, D-19, and P-7.

**Plain-language owner summary — eight lines**

- The equation proved for equally correlated Gaussian trials is correct.
- Realistic changes in clustering can make its penalty much too small.
- Counting every lifetime attempt is sensible accounting, but does not fix that problem.
- Adding duplicate trials can actually lower the complete penalty.
- Matching an average winner does not establish how often noise passes.
- Small-count and missing-result rules still need explicit decisions.
- Keep raw lifetime counts as a candidate; do not activate this method on this evidence.
- You decide the D-rows and author any amendment; this review accepts nothing.