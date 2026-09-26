---
name: sharpe-selection-statistics
description: "Curriculum for the statistics this project turns on: Sharpe inference under selection, DSR, effective trial count, PBO, the paired estimands, block bootstrap, CPCV. Use when a question turns on what a statistic means or whether a number can be trusted. A curriculum, not an authority; it closes no D-nn."
---

# Sharpe inference under selection — working curriculum

The statistics this project actually turns on, taught in the order they depend on
each other, grounded in this repository's frozen text and open decisions.

**Who this is for.** The owner is not a statistician and has said so. This skill
exists so the reasoning is available on demand, in the repository, rather than
living in one session's memory. Read the lesson that covers the question in
front of you; they are ordered by dependency, not by importance.

**What this skill is not.** It is not acceptance of any method. It closes no
`D-nn`. Teaching the owner what a deflated Sharpe ratio is does not make one
calibrated, and nothing here substitutes for the qualified human review that
`review/governance-statistics-amendment/` requests.

Every number below is reproducible with the stdlib alone. Scripts write nothing
into the repository.

---

## Lesson 1 — Why your best backtest is probably noise

### The one fact

A strategy with **exactly zero edge**, measured over `T` daily observations, has
an annualized Sharpe with standard deviation approximately

```
sd(annualized Sharpe) = sqrt(A^2 / T) = sqrt(365 / T)
```

For `T = 500` (about two years) that is **0.854**. A worthless strategy routinely
shows +0.8, and sometimes +1.7. Nothing is broken when that happens.

### Selection makes it far worse

```
     T = 500 daily observations. EVERY strategy has ZERO true edge.

     trials tried   best annualized Sharpe found
                1                          0.00
                5                          0.99
               20                          1.60
              100                          2.15
              500                          2.64
             2000                          3.05
```

Try 100 configurations, keep the winner, and pure randomness hands you a Sharpe
of 2.15. You are not measuring performance; you are measuring **the maximum of
N draws**, and the maximum grows with N.

This does not feel like cheating. A few lookback windows, a couple of thresholds,
two sizing rules — that is twenty trials, and twenty trials buys a free 1.6.

### Reproduce it

```python
import random, math
rng = random.Random(20260921)
A, T = math.sqrt(365), 500

def ann_sharpe(x):
    n = len(x); m = sum(x)/n
    sd = math.sqrt(sum((v-m)**2 for v in x)/(n-1))   # ddof=1, project convention
    return A*m/sd

pool = [ann_sharpe([rng.gauss(0,1) for _ in range(T)]) for _ in range(20000)]
for N in (1, 5, 20, 100, 500, 2000):
    best = sum(max(pool[rng.randrange(len(pool))] for _ in range(N))
               for _ in range(4000)) / 4000
    print(N, round(best, 2))
```

### Where it lands in this repository

`protocols/protocol_v1.yaml` lines 227-233 request a deflated Sharpe ratio. The
DSR's job is exactly this correction:

```
A(N) = (1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e))
S0   = sqrt(V) * A(N)
DSR  = Phi( (S - S0) * sqrt(T - 1) / sqrt(D) )
```

`A(N)` is the expected maximum of `N` standard normals — the table above.
`sqrt(V)` is the spread of your trials' Sharpes, which scales that expectation to
your actual trial population. `S0` is the resulting **hurdle**: the Sharpe you
would expect from noise alone, given how many times you looked.

Treat the functional form as an external assumption. It is Bailey and
López de Prado (2014) as recorded in
`review/governance-statistics-amendment/DSR_METHOD_PREREGISTRATION_DRAFT.md`,
which is an unaccepted draft. What the argument needs is only that the hurdle is
non-decreasing in the trial count, which holds for the maximum of `N` draws under
any of the candidate forms.

---

## Lesson 2 — Effective trial count, and why `D-16` is the dangerous row

### The problem

Lesson 1 assumed trials were independent. Yours are not. Fifty lookback windows
between 20 and 70 days produce fifty highly correlated equity curves. Counting
them as fifty independent looks overstates the hurdle; counting them as one
understates it. Neither error is safe, but **understating is the one that costs
money**, because it lowers the hurdle.

### Two candidates are in play, and they disagree

| Construct | Source | Status |
| --- | --- | --- |
| Eigenvalue effective number from the trial-return correlation matrix | `protocol_v1.yaml:232` | **Frozen primary method**, never evaluated |
| `raw_trial_count` | `protocol_v1.yaml:233` | **Frozen fallback**, no protocol-stated trigger |
| `N_eff = N^2 / sum(R_ij^2)` (participation ratio) | `DRAFT_AMENDMENT_PROPOSAL.md:101` | Unaccepted AI candidate, warned against |

The existing candidate `aqt.dsr.iid_raw_count.proposal.v1` uses the **fallback**
without the primary ever being evaluated. The only frozen trigger text is
`docs/RESEARCH_CONSTITUTION.md` §9 line 106: "If no frozen effective-count method
exists, raw count is used." Whether the method *named but not defined* at line
232 "exists" is undecided — which is why `D-16` is open.

### The demonstration that matters

Take `N = 100` trials sharing a common factor with pairwise correlation `rho`.
Ask two questions. How many *independent* trials would produce the same selection
bias? And what does the participation ratio say?

```
   rho    E[max]   true effective N   participation ratio
  0.00     2.507               93.5                 100.0
  0.30     2.105               32.4                  10.1
  0.60     1.581               10.1                   2.7
  0.90     0.794                2.8                   1.2
  0.99     0.249                1.5                   1.0
```

At `rho = 0.3` the selection bias is that of 32 independent trials; the
participation ratio reports 10. Feed 10 into `A(N)` and the hurdle is materially
too low.

**But equicorrelation is not what a parameter sweep looks like**, and the
magnitude above is therefore too flattering to the argument. A real sweep has
neighbouring lookbacks far more alike than distant ones. Under structures that
resemble one, the understatement is **about twofold**, not threefold:

| Correlation structure | true effective `N` | participation ratio | understates by |
| --- | ---: | ---: | ---: |
| Equicorrelated, `rho = 0.3` | 32.1 | 10.1 | 3.2x |
| Equicorrelated, `rho = 0.6` | 10.1 | 2.7 | 3.7x |
| AR decay, `corr = 0.9^abs(i-j)` | 25.6 | 11.0 | **2.3x** |
| AR decay, `corr = 0.97^abs(i-j)` | 8.1 | 3.6 | **2.2x** |
| 10 blocks of 10, within-block `0.90` | 23.3 | 12.0 | **1.9x** |

An earlier revision of this lesson claimed "roughly threefold across the
realistic range" on the strength of the equicorrelated rows alone. That was an
overstatement: threefold is the equicorrelated figure, and equicorrelation is the
least realistic of the three structures. The **direction is unchanged and is the
point** — the participation ratio understates, and understating lowers the hurdle
— but the honest magnitude for a parameter sweep is roughly a factor of two.

Why the direction matters more than the size: `A(N)` is non-decreasing in `N`, so
a smaller `N_eff` gives a smaller `S0`, which is a lower bar. An error of 2x in
the permissive direction is still an error in the direction that promotes noise.

This is Astra finding `B1` made concrete: a construction can collapse correlated
trials toward one effective trial while selection over their maximum still
biases. `B1` says neither candidate is validated for maxima. The tables show why
that warning has teeth, and why adopting the participation ratio because it
"looks principled" would be a mistake in the permissive direction.

**What this does and does not establish.** It shows the participation ratio is
unsuitable for selection over a maximum. It does **not** establish that the
frozen eigenvalue method at `protocol_v1.yaml:232` is suitable — that method was
never evaluated, and `B1` doubts both. Nor does it supply a correct construction.
Defining `N_eff` as the inverse image under `A` — the independent-trial count
producing the same expected maximum — is the right definition *for this purpose*,
because `A(N)` is exactly where the number is consumed; but it is a simulation
result under an assumed correlation model, not a theorem, and whether any real
trial family matches any of the three structures above is
`UNVERIFIED_EXTERNAL_ASSUMPTION`.

### Reproduce it

```python
import random, math
from statistics import NormalDist
rng = random.Random(7)
g, Phi = 0.5772156649015329, NormalDist().inv_cdf
def AN(N): return (1-g)*Phi(1-1/N) + g*Phi(1-1/(N*math.e)) if N > 1 else 0.0

def best_of(N, rho, reps=20000):
    a, b = math.sqrt(rho), math.sqrt(1-rho)
    return sum(max(a*rng.gauss(0,1) + b*rng.gauss(0,1) for _ in range(N))
               for _ in range(reps)) / reps   # note: redraw z per rep in real use

for rho in (0.0, 0.3, 0.6, 0.9, 0.99):
    N = 100
    obs = best_of(N, rho)
    lo, hi = 1.0001, 1e6
    for _ in range(200):
        mid = math.sqrt(lo*hi)
        lo, hi = (mid, hi) if AN(mid) < obs else (lo, mid)
    print(rho, round(obs,3), round(math.sqrt(lo*hi),1),
          round(N*N/(N + N*(N-1)*rho*rho),1))
```

(The snippet above draws the common factor inside the `max` for brevity; draw
`z` once per repetition to reproduce the table exactly.)

### `D-17`, the second trap

Even with a construction chosen, *which* count enters `A(N)` is undecided:
`N_cycle`, `N_lifetime`, or `K`. `A` is monotone in `N`, so the choice moves
every score. Concretely, with the dispersion above: a true 500 trials gives a
hurdle near 2.61 and a recorded 20 gives 1.63. A noise strategy at 2.2 clears
the second and fails the first.

This is why `src/aqt/core/attempts.py` keeps the counts **separate and merged
into nothing**. Supplying a single number would be answering `D-17` in code.

---

## Lesson 3 — The rest of the DSR: `V` and `D`

`S0 = sqrt(V) * A(N)` has a second input, and the final step has a third.

**`V` is the variance of the trial Sharpes**, `V = sum((S_j - mean(S))^2)/(K-1)`.
It scales the expected maximum to your actual population. A family of near
identical trials has small `V` and a low hurdle; a scattered family has a high
one. This is the term that makes the hurdle depend on *what else you tried*, not
only on how many.

**`D` carries the shape of the return distribution:**

```
D = 1 - g*S + ((k - 1)/4) * S^2
```

with `g` the skew and `k` the kurtosis of the difference series
(`g = mu_3/mu_2^1.5`, `k = mu_4/mu_2^2`, `mu_r = sum((x-mean)^r)/T`).

`D` is the variance of the Sharpe estimator under non-normal returns. Negative
skew and fat tails — the normal condition for a strategy that sells volatility or
buys dips — **increase** `D`, which **decreases** the DSR. A strategy with a good
Sharpe and an ugly return distribution is correctly penalized, because its Sharpe
is estimated less precisely than a normal one's.

Crypto daily returns are reliably fat-tailed. Expect `D > 1` and expect the DSR
to be lower than a naive reading of the Sharpe suggests. That is the formula
working, not a bug.

---

## Lesson 4 — PBO: a different attack on the same problem

The DSR corrects the Sharpe. PBO asks a different question entirely, and it is
worth understanding because it fails differently.

**The question:** does in-sample ranking predict out-of-sample ranking at all?

The construction in `protocol_v1.yaml:234-241`, with the candidate's proposed
details in `METHOD_CANDIDATE.md` §4:

1. Split the day index into 16 chronological balanced blocks.
2. Take all `C(16,8) = 12,870` oriented in-sample selections. Exactly
   `12,870 = 2 * 6,435`: each unordered half-partition is used twice, once in
   each orientation. Both are required; using 6,435 halves the sample and biases
   the result.
3. Per split: pick the in-sample best trial, find its out-of-sample rank among
   all `N` trials, set `omega = rank/(N+1)`, score the split `1` if
   `logit(omega) < 0`, `0` if `> 0`, `0.5` if `= 0`.
4. `phi` is the mean of the 12,870 split scores. The gate is `phi <= 0.30`.

`phi` is the estimated probability that the in-sample winner lands in the bottom
half out of sample. If your selection procedure is pure overfitting, `phi`
approaches 0.5 — a coin flip.

**Why this catches what the DSR cannot.** The DSR asks whether one number clears
a hurdle. PBO asks whether your *selection procedure* has any predictive content.
A family can contain a genuinely good strategy and still show a terrible `phi`,
if your method cannot identify which one it is in advance. That is a distinct and
equally fatal problem.

**The open row.** `D-08`: the stored matrix is a difference matrix, and
`ranking_metric` says `paired_delta_sharpe`, which the two candidate estimands
read differently. See Lesson 5.

---

## Lesson 5 — The two estimands, and `D-01`

Everything above assumed "the Sharpe" was well defined. In this protocol it is
not. Two quantities exist, and they are not interchangeable.

| Name | Formula | Needs | Meaning |
| --- | --- | --- | --- |
| `E-IMPROV` | `A*S(c) - A*S(b)` | **both** legs | how much better the candidate's Sharpe is |
| `E-DIFF` | `A*S(c - b)` | the difference series only | the Sharpe of the outperformance stream |

They sound like the same idea. They are not functions of each other.

### They disagree in rank, totally

From `TECHNICAL_APPENDIX.md` §4, with `b = (0.20, -0.10, 0.20, -0.10)`, exact
rationals:

| | Trial 1 | Trial 2 |
| --- | --- | --- |
| `S(c_j)^2` | `243/4` | `507/3844` |
| **`E-IMPROV`** | **+143.393** | +1.423 |
| **`E-DIFF`** | -0.551 | **+49.636** |

Ranking by improvement: Trial 1 wins. Ranking by the difference-series Sharpe:
Trial 2 wins. Complete reversal, two trials, shared benchmark, clean aligned
data. Whichever you pick for PBO's `ranking_metric` selects a different
in-sample winner and therefore a different `phi`.

### Lemma `L-1`, and the trap it sets

Within a fixed window with one shared benchmark `b`, `E-IMPROV_j = A*S(c_j) -
A*S(b)` differs from `A*S(c_j)` by a constant. **So ranking by `E-IMPROV` is
identical to ranking by the candidate's own Sharpe.** The benchmark cancels.

That is why `D-08` recommends reading `ranking_metric` as `E-DIFF`: ranking by
`E-IMPROV` would reduce PBO to ranking by raw Sharpe, contradicting the frozen
justification at line 239 that PBO stays "on the same incremental objective as
DSR".

The same collapse reaches further. Type-7 quantiles are translation-equivariant,
so in the row-12 null test, "realized `E-IMPROV` >= 0.95 quantile of 500 null
`E-IMPROV` values" is *exactly* equivalent to comparing raw Sharpes — the
benchmark is inert. That is finding `F-Q1`, left standing for the statistician by
owner election. Invariant `I-12` exists to stop `L-1` being used to substitute
`A*S(c)` for a gate statistic.

Rows 3-7 do **not** collapse: sign tests compare `S(c)` against `S(b)`, the
plateau rule's `0.5 *` factor is not translation-invariant, and the confidence
interval is on the difference series.

---

## Lesson 6 — Dependence, block bootstrap, and `D-20`

Daily returns are autocorrelated, and volatility clusters. Resampling single days
destroys that structure and produces confidence intervals that are far too
narrow — the classic way to conclude an edge is significant when it is not.

The project uses a **stationary bootstrap** with Politis-White block length
selection, resampling blocks of consecutive days so dependence survives.

The consequence that matters for governance: the block length is derived from the
**influence process** of the statistic, which for the Task 12 implementation is
`z = psi_c - psi_b` with `psi = u - (S/2)*(u^2 - 1)` — an `E-IMPROV` influence
process. Change the estimand and you change the influence process, therefore the
block length, therefore every resample and every interval endpoint.

That is invariant `I-10` and Astra `B5`: binding any bootstrap-backed clause to
`E-DIFF` requires a reviewed migration with regenerated deterministic reference
vectors. It cannot be done quietly. `D-20` is the row.

---

## Lesson 7 — CPCV, purging, and embargo

Cross-validation on time series leaks unless you prevent it. Two mechanisms:

- **Purging** removes training observations whose labels overlap the test window
  in time. Without it, a label built from a forward window lets the test period
  bleed into training.
- **Embargo** drops a further gap after the test window, because serial
  correlation means observations adjacent to the test set carry information about
  it even without label overlap.

`protocol_v1.yaml:215-222` configures 8 groups, 2 test groups, purge and embargo,
and — importantly — `role: diagnostic_only` with "no independent promotion gate".

CPCV here **consumes and never gates**. Its median and 5th-percentile path
summaries are descriptive. `D-13` proposes reporting both estimands per path,
separately labelled, on the reasoning that dual reporting binds nothing and is
therefore narrower than choosing one.

---

## How the lessons map to the open decisions

| Row | Question | Lesson |
| --- | --- | --- |
| `D-01` | Which estimands exist and how are they named | 5 |
| `D-02`-`D-07` | Per-clause bindings, Queue I | 5 |
| `D-08` | PBO ranking metric | 4, 5 |
| `D-09`, `D-10` | PBO block minimum, tie rule | 4 |
| `D-11`, `D-12` | Lockbox specification | 5, 6 |
| `D-13` | CPCV reporting | 7 |
| `D-14` | Random-exposure null pass event | 5 |
| `D-16` | Effective trial count construction | **2** |
| `D-17` | Which count enters `A(N)` | **2** |
| `D-18` | Primary selection rule and error event | 1, 3 |
| `D-19` | What `score >= 0.95` claims | 1, 3 |
| `D-20` | Bootstrap migration | 6 |

`D-16` and `D-17` are the rows where a wrong answer fails toward promoting noise.
Lesson 2 is the one to understand first.

---

## What none of this authorizes

Understanding a method is not accepting one. This skill closes no `D-nn`, binds
no estimand, calibrates nothing, and authorizes no calibration engine,
simulation, confirmation or lockbox access, promotion, deployment, or trading.
`KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid results, and the frozen v1.0
protocol is unchanged.
