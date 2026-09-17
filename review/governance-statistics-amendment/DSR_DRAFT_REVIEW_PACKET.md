# DSR draft local gate and independent review packet

Date: 2026-09-17
LOCAL GATE: PASS for proposal preparation only.
Calibration/activation gate: BLOCKED.
Claude status: NOT SENT — READY FOR HUMAN RELAY.
Reviewer: Codex local review; no additional agent or independent reviewer ran.

## Scope and reviewed state

Base and HEAD: bc82a42d6babbbe4997633309ae3f5552263b382.
The initial draft-preparation worktree was clean. This continuation updates only
this packet and DSR_METHOD_PREREGISTRATION_DRAFT.md. Existing AGENTS.md changes
and review/skill-setup/ belong to the separate skill-setup task and are preserved.
No staged changes; these draft files remain local and uncommitted.
The complete draft is attached below, with its raw SHA-256 identifying the
reviewed snapshot. This packet does not hash itself.

Acceptance criteria for this preparation task:
1. Supply a reviewable candidate equation, proposed inputs/counts, selection
   rule, and explicit boundary behavior: draft sections 2-4.
2. Expose unresolved preregistration choices without silently selecting
   scientific acceptance values: worksheet and scenario coverage.
3. Preserve frozen governance, existing implementation, and data boundaries:
   read-only frozen verification below; only review Markdown added.
4. Record local scientific/quant review and prepare the independent handoff:
   findings, exact checks, and full attachment below.

## Local scientific-reproducibility and quant-code review

The repository skills were applied by the same assistant; this is not
independent or different-model review.

- NON-BLOCKING for preparation / BLOCKER for calibration: the worksheet remains
  unresolved. The exact support grid, error claim, confidence procedure,
  availability rule, acceptance tolerance, runtime, seeds, replication budget,
  and independent references require preregistration before simulation.
- NON-BLOCKING for preparation / BLOCKER for activation: this conventional
  baseline supports a narrow synthetic design. Dependent returns, adaptive
  selection and prior-cycle histories need a separately reviewed solution.
  Raw count does not establish valid selection correction.
- The draft keeps population-moment and sample-variance conventions explicit,
  distinguishes return-difference Sharpe from paired delta-Sharpe, separates
  single-trial behavior, and rejects missing or zero dispersion without repair.
- The opposite-trial counterexample remains unsupported instead of being
  collapsed by squared correlation. Unsupported raw diagnostic scores are
  separated from available method outcomes.
- Trial failures/reruns remain counted; current and lifetime counts are distinct;
  prior-cycle return matrices are not pooled.
- The 0.95 score threshold is preserved without a claimed 5% family error rate
  or posterior interpretation. Promotion and Task 13 remain blocked.
- No raw confirmation/lockbox data, credentials, exchange behavior, execution
  code, benchmark/cost implementation, or temporal feature pipeline changed.
  Observation-through-fill tracing and Binance review are N/A for this DSR-only
  documentation change. No numerical calibration or independent reproducibility is claimed. Author-run
  exact-arithmetic checks of R1-R3 are recorded below.

B1-B5 remain open as recorded in ASTRA_REVIEW.md. Local preparation passing does
not resolve those activation blockers or replace human review.

## Validation evidence

Environment: Linux aarch64, Python 3.14.4, PyYAML 6.0.3, jsonschema 4.19.2.
The default sandbox shell returned exit 182 without output; checks were rerun
with approved execution. The initial dependency probe failed because PyYAML was
absent. An isolated pip install could not start because pip was absent.
Installing system packages python3-yaml and python3-jsonschema succeeded;
the final verification then exited 0.

Commands from repository root:
- `git status --short`: exit 0; initially only the new draft, finally draft and
  packet untracked.
- `git diff --check`: exit 0. Since it excludes untracked files, the Python
  check below explicitly checks the draft; final formatting checks cover both.
- `git diff --cached --stat`: exit 0; no staged changes.
- Frozen/schema/draft verification command below: exit 0. All 28 protected
  files and exact inventory match both the recorded Task 1 snapshot and
  pre-task HEAD; all 14 sidecars, Constitution self-hash, seven manifest
  bindings, protocol/nested bindings, five schemas and protocol/rejection
  controls pass.
- Tests, Ruff, mypy and import-linter: N/A. Only review Markdown was added;
  no executable behavior, Python files, configuration or import edges changed.
  The verification command is review evidence, not a production code change.

Baseline limitation: HEAD is the freshly cloned pre-task commit; Task 1's
snapshot is repository-recorded evidence. No independently signed external
historical baseline was supplied. Verification establishes consistency with
those baselines, not independently authenticated historical provenance.

## Independent reviewer request

Please review the full draft below alongside the listed repository governing
documents at HEAD. Return stable IDs under BLOCKER, NON-BLOCKING or QUESTION,
with file/line, triggering case, evidence, impact and minimal correction.
State missing evidence explicitly; do not invent strategies or acceptance values.

1. Does the equation match the cited literature, and are project-specific
   conventions clearly distinguished from sourced claims?
2. Are all proposed branches internally consistent, particularly N=1,
   zero dispersion, incomplete histories and lifetime/current-cycle counts?
3. Is the independence/selection limitation explicit enough to prevent this
   synthetic baseline being mistaken for a calibrated practical method?
4. Are unavailable outputs and unsupported-design stress outputs distinguished
   without hiding failures or inflating apparent error control?
5. Does the worksheet require enough advance commitments to prevent
   outcome-dependent calibration choices and held-out tuning?
6. Does any text improperly authorize implementation, Task 13, data access,
   promotion or a frozen-governance amendment?

Human relay: provide this packet and the repository context to the reviewer,
then return the full response with finding IDs for adjudication. No external
transmission has occurred. Human authorship of final amendments and formal
activation remain required by Constitution section 4. Any later protected
implementation also requires section 16 different-model and human PR review.

## Exact verification command

```bash
python3 - <<'PY'
import hashlib, json, re, subprocess, platform, sys
from pathlib import Path
from importlib.metadata import version
import yaml
from jsonschema import Draft202012Validator
r=Path("/root/autonomous-quant-trader")
h=lambda p: hashlib.sha256((r/p).read_bytes()).hexdigest()
base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=r,text=True).strip()
expected={e["path"]:e["sha256"] for e in json.loads((r/"review/task1/protected-before.json").read_text())}
inventory={p.relative_to(r).as_posix() for area in ("docs","protocols","schemas","specs") for p in (r/area).rglob("*") if p.is_file() and p != r/"docs/README.md"} | {"FROZEN_HASHES.json","FROZEN_HASHES.json.sha256"}
assert inventory == set(expected)
for p,d in expected.items():
    assert h(p)==d, p
    assert (r/p).read_bytes()==subprocess.check_output(["git","show",base+":"+p],cwd=r), p
for p in inventory:
    if p.endswith(".sha256"):
        d,name=(r/p).read_text().strip().split(maxsplit=1)
        assert name==Path(p).stem and h(p[:-7])==d, p
c=(r/"docs/RESEARCH_CONSTITUTION.md").read_text()
pat=r"(\*\*Content hash:\*\* `)([0-9a-f]{64})(`)"
m=re.findall(pat,c)
assert len(m)==1
ch=hashlib.sha256(re.sub(pat,r"\1\3",c).encode()).hexdigest()
assert ch==m[0][1]
manifest=json.loads((r/"FROZEN_HASHES.json").read_text())
assert manifest["release"]=="v1.0" and manifest["status"]=="FROZEN"
assert manifest["constitution_content_hash"]==ch
bindings={"protocol_file_sha256":"protocols/protocol_v1.yaml","cost_model_sha256":"specs/COST_MODEL_v1.md","feature_factory_sha256":"specs/FEATURE_FACTORY_v1.md","benchmark_set_sha256":"specs/CANONICAL_BENCHMARKS_v1.md","backtester_spec_sha256":"specs/BACKTESTER_SPEC_v1.md","threat_model_sha256":"docs/THREAT_MODEL_v1.md","hash_canonicalization_spec_sha256":"schemas/HASH_CANONICALIZATION_v1.md"}
for k,p in bindings.items(): assert manifest[k]==h(p), k
protocol=yaml.safe_load((r/"protocols/protocol_v1.yaml").read_text())
assert protocol["constitution_hash"]==ch
for k in ("cost_model","feature_factory","benchmark_set","backtester_spec","threat_model","hash_canonicalization_spec"):
    assert protocol[k+"_hash"]==manifest[k+"_sha256"], k
assert protocol["cost_model"]["hash"]==protocol["cost_model_hash"]
assert protocol["feature_factory"]["hash"]==protocol["feature_factory_hash"]
assert protocol["benchmarks"]["benchmark_set_hash"]==protocol["benchmark_set_hash"]
assert manifest["hash_canonicalization_spec_sha256"] in c
schemas=sorted((r/"schemas").glob("*.schema.json"))
assert len(schemas)==5
for p in schemas: Draft202012Validator.check_schema(json.loads(p.read_text()))
v=Draft202012Validator(json.loads((r/"schemas/protocol.schema.json").read_text()))
v.validate(protocol)
assert list(v.iter_errors({}))
assert list(v.iter_errors({**protocol,"status":"UNFROZEN"}))
draft=r/"review/governance-statistics-amendment/DSR_METHOD_PREREGISTRATION_DRAFT.md"
b=draft.read_bytes()
assert b.endswith(b"\n") and b"\r" not in b
assert all(line.rstrip()==line for line in b.decode().splitlines())
print("PASS: 28 protected files match recorded Task 1 baseline and pre-task HEAD; exact inventory; 14 sidecars")
print("PASS: Constitution self-hash; 7 manifest bindings; protocol and nested bindings; 5 schemas and protocol/rejection controls")
print("PASS: new draft UTF-8/LF and whitespace")
print("HEAD:",base)
print("Environment:",platform.platform(),sys.version.split()[0],"PyYAML",version("PyYAML"),"jsonschema",version("jsonschema"))
print("Draft SHA256:",hashlib.sha256(b).hexdigest())
PY
```

## Continuation: proposed reference examples

Added R1-R8 to the existing draft. R1-R3 numerical identities were checked with
Python 3.14.4 stdlib Fraction (exact rational arithmetic) and NormalDist
(descriptive decimal output). The command below exited 0. R4-R8 are proposed
logical boundary expectations checked against the draft, not executed production
tests. No sampling, calibration, market-data access or statistical implementation.

Scientific/quant local review: examples distinguish author calculations from
independent oracles, preserve incomplete/lifetime counts, expose the opposite
trial counterexample, and claim neither support from four observations nor
calibration from a score. Remaining boundary/multi-trial coverage is explicit.
Local task-gate: PASS for review preparation only. Independent reviewer choice
is pending; no separate agent or different-model review has occurred.
Calibration/activation remain BLOCKED by the existing scientific requirements.

Tests/Ruff/mypy/import-linter remain N/A for this Markdown-only change. The
frozen verification above was rerun and passed all listed checks. Formatting
checks cover both untracked draft files. Existing skill-setup changes untouched.

Additional reviewer questions: verify R1-R3 algebra independently and assess
whether R4-R8 reason-code expectations match the proposed contract. Do not
accept these as frozen reference vectors solely because author checks pass.

Exact arithmetic-check command:

```bash
python3 - <<'PY'
from fractions import Fraction as F
from math import sqrt
from statistics import NormalDist
for values, expected_mean, expected_variance, expected_s2, expected_d, expected_z2 in [
    ((-3,-1,1,3), F(0), F(1,1500), F(0), F(1), F(0)),
    ((-2,0,2,4), F(1,100), F(1,1500), F(3,20), F(128,125), F(225,512)),
    ((-4,0,4,8), F(1,50), F(1,375), F(3,20), F(128,125), F(225,512)),
]:
    x=[F(v,100) for v in values]
    mean=sum(x)/4
    e=[v-mean for v in x]
    m2=sum(v*v for v in e)/4
    m3=sum(v**3 for v in e)/4
    m4=sum(v**4 for v in e)/4
    variance=sum(v*v for v in e)/3
    assert mean==expected_mean and variance==expected_variance
    assert m3==0 and m4/m2**2==F(41,25)
    s2=mean**2/variance
    d=1+(m4/m2**2-1)*s2/4
    z2=3*s2/d
    assert (s2,d,z2)==(expected_s2,expected_d,expected_z2)
    print(values, "score", NormalDist().cdf(sqrt(float(z2))))
print("PASS: R1-R3 exact rational identities; decimals descriptive; no simulation")
PY
```

## Complete reviewed draft

Raw SHA-256: 5c7119a56a35427b3a370e86cb9d2a46a46c2f0cf50891baeac92eadf606e899

```markdown
# DSR method candidate and preregistration worksheet

Date: 2026-09-17
Status: AI PROPOSAL ONLY; not selected, preregistered, calibrated, or active.
Scope: review preparation under the recorded owner decision. This is not the
human-authored final specification or an amendment. No simulation was run.

## Decision requested from scientific and human review

Consider the conventional candidate below as a synthetic calibration baseline.
It is not proposed as a validated solution for dependent trading returns.
Accepting a calibration experiment would not accept its method for promotion.
Complete and review the registration worksheet before any calibration run.
Keep DSR diagnostic-only and the mandatory 0.95 gate unsatisfied throughout.

References: `DSR_CALIBRATION_PLAN.md`, `OWNER_DECISION.md`,
`DRAFT_AMENDMENT_PROPOSAL.md`, and frozen Constitution sections 4, 7a, 9, 16, 27.

## Candidate equation for review

Literature basis: Bailey and Lopez de Prado (2014), equations 1-2, printed
pages 7-9, [author-hosted paper](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
Their conventional score uses a normal CDF, selected-series moments, and an
approximate expected maximum based on trial count and Sharpe dispersion.
The expected-maximum derivation assumes independent normal trial Sharpes.

```text
A(N) = (1-gamma) * Phi_inverse(1-1/N)
       + gamma * Phi_inverse(1-1/(N*e))                 [N > 1]
S0 = sqrt(V) * A(N)
D = 1 - skew*S + ((kurtosis-1)/4)*S*S
score = Phi((S-S0)*sqrt(T-1)/sqrt(D))
```

Here gamma is the Euler-Mascheroni constant; Phi is the standard normal CDF.
The equations are a literature baseline, not evidence that 0.95 controls a
family error rate or represents a posterior probability.

## Proposed project-specific contract

Everything in this section is a review proposal, not a claim from the paper.
Candidate identifier: `aqt.dsr.iid_raw_count.proposal.v1`; never substitute it
for the inactive Task 12 implementation identity or an active method identifier.

- Each column is unannualized daily candidate net return minus the fixed
  comparison benchmark's daily net return. Compound each leg before subtraction.
  Follow the existing complete-UTC-day, alignment, asset, cost, and no-repair
  conventions. Difference-series Sharpe is not paired delta-Sharpe.
- For each usable column, `S = mean(x)/s`, with sample variance denominator
  `T-1`. Let `mu_r = sum((x-mean(x))**r)/T`; proposed skew is
  `mu_3/mu_2**1.5` and Pearson kurtosis is `mu_4/mu_2**2`.
- Record `N_cycle`, `N_lifetime`, and `K` separately. Counts include failures,
  evaluated aborts, and actual reruns; event redelivery does not add attempts.
  Never pool previous-cycle returns into the current-cycle matrix.
- Proposed numerical baseline support is deliberately narrow:
  `N_lifetime = N_cycle = K = N`, complete aligned series, no adaptive search,
  and a synthetic design with independent trials and independent daily draws.
  This does not claim independence can be established from sample correlations.
  A practical method for broader histories remains unresolved.
- For `N > 1`, propose sample dispersion
  `V = sum((S_j - mean(S_j))**2)/(K-1)`. No effective-count substitution,
  estimated pairwise-correlation correction, or silent dispersion fallback.
- The baseline selects the largest difference-series Sharpe; break exact ties
  by ascending preregistered trial ID. This is a calibration-only selection rule,
  not a change to project candidate selection. Any other rule needs an explicit
  whole-procedure calibration and method identity.
- The null for this baseline is zero population mean in every difference-series
  column. This does not equate zero difference-series mean with zero paired
  delta-Sharpe. Alternatives and error claims must be registered separately.
- For the single-attempt case `N_cycle=N_lifetime=K=1`, propose `S0=0` with the
  same moment denominator `D`; do not evaluate inverse-normal terms at `N=1`
  or estimate cross-trial dispersion. Calibrate this branch separately.

The proposal combines sample Sharpe, population moments, and estimated
cross-trial dispersion. Independent reference calculations must check that
finite-sample combination; it is not asserted to be exact.

## Proposed unavailable outcomes

Return no numeric score for the following conditions. Record all applicable
reason codes in the fixed table order; do not discard an evaluated attempt.

| Condition | Proposed reason |
| --- | --- |
| Noninteger, negative, zero, or inconsistent counts; `K > N_cycle`; `N_cycle > N_lifetime` | `INVALID_COUNTS` |
| Missing, nonfinite, duplicated, irregular, or misaligned daily data | `INVALID_SERIES` |
| Any column has `T < 4` | `INSUFFICIENT_OBSERVATIONS` |
| Any column has nonpositive variance or undefined moments | `INVALID_MOMENTS` |
| Incomplete trial vectors, including `N_cycle > 1, K = 1` | `INCOMPLETE_HISTORY` |
| Prior-cycle attempts exist, even if current-cycle vectors are complete | `UNSUPPORTED_LIFETIME_HISTORY` |
| Known dependent, adaptive, heterogeneous, or otherwise unregistered design | `UNSUPPORTED_DESIGN` |
| `N > 1` and `V` is missing, nonfinite, or nonpositive | `DISPERSION_UNAVAILABLE` |
| `D <= 0`, nonfinite intermediate, invalid quantile, or overflow | `INVALID_ARITHMETIC` |

Check structural validity before arithmetic; dependent values need not be
evaluated after their prerequisites fail. No epsilon, clipping, absolute-value
repair, row deletion, imputation, replacement trial, or ESS-for-T substitution.
In particular, duplicated trials with zero dispersion do not imply no selection
bias. The `X` versus `-X` design is outside the baseline's independence support;
it must not collapse into a one-trial success.

Unsupported-design stress experiments may record the formula's raw output only
under an explicitly separate diagnostic field. Such output is not an available
method score and cannot enter acceptance or promotion as a valid supported case.

## Preregistration worksheet — all unresolved entries block execution

No value below is implicitly supplied by the 0.95 frozen score threshold.
An independent reviewer and human must resolve these entries before simulation.

| Required registration item | Current state / decision needed |
| --- | --- |
| Method identity, equations, counts, dispersion, selection, unavailable branches | Candidate above; accept or revise explicitly |
| Scientific claim at score 0.95 | OPEN: define precise null, event, and population |
| Supported domain | OPEN: exact sample sizes, trial counts, distributions, moments, dependence and selection rules |
| Error measure and tolerance | OPEN: name measure, target, and allowed deviation; do not infer 5% from 0.95 |
| Monte Carlo confidence procedure | OPEN: confidence level, bound calculation and simultaneous scenario control |
| Replication budget and stopping | OPEN: fixed counts by scenario, failures and rerun rules; no stopping when results look favorable |
| Development versus held-out scenarios | OPEN: disjoint scenario/seed manifests and custodian for held-out execution |
| RNG and deterministic computation | OPEN: generator/version, seed derivation, ordering, precision, reductions and threading |
| Environment and code | OPEN: exact runtime/dependency versions, OS/architecture and code hashes |
| Independent numerical references | OPEN: separately derived inputs, expected outputs, tolerances and reviewer |
| Registration authority | OPEN: human reviewer, record identity/hash, date and signature before execution |

An unresolved entry is not a default or permission to start. This worksheet is
not itself a completed preregistration. Revising a method after held-out results
requires a new identity and a new independent validation set; preserve failures.

## Scenario and reference coverage required in that registration

Carry forward all seven scenario groups in `DSR_CALIBRATION_PLAN.md`.
Distinguish supported calibration cells from unsupported-design challenge cells.
Include one trial, the 20-trial PBO boundary and the 81-trial family boundary;
daily sample sizes must be specified rather than replacing them with ESS 120.
Explicitly cover positive and negative serial dependence, 24/72/168-hour overlap,
identical/opposite/near-duplicate columns, unequal variances, heavy tails,
volatility clustering, ties, non-Sharpe selection, adaptation, missing attempts,
and lifetime counts larger than current-cycle counts.

Before Monte Carlo calibration, independent deterministic references should
cover each unavailable branch, the separately defined single-trial branch,
`S=S0` giving score 0.5 when otherwise valid, positive scale invariance, and
the distinction between paired delta-Sharpe and difference-series Sharpe.
These are requested reference properties, not results already demonstrated.
For independent standard normal trial statistics, compare the expected-maximum
approximation with independent high-accuracy integration or another accepted
oracle. Record approximation error, especially at small trial counts.

For each supported scenario, retain the distribution of scores, selected-null
threshold-crossing frequency over all attempted replications, its registered
confidence bounds, unavailable frequency/reasons, expected-maximum bias, and
power under registered alternatives. Also report valid-only frequencies with
their denominator; unavailable-heavy methods cannot pass by shrinking the set
of reported outcomes. Freeze the availability acceptance rule before results.

## Proposed evidence handoff and remaining boundary

A later calibration submission needs the signed registration, exact method and
scenario manifests, environment/code hashes, complete synthetic results,
independent references, independent rerun evidence, and a claim-by-claim review.
No confirmation or lockbox returns enter this preparation or calibration.

B1-B3 remain open: a literature candidate and explicit branches do not establish
calibration, practical support, or an accepted DSR gate. B4 (lockbox semantics)
and B5 (human-authored specification and implementation/hash migration) remain
unchanged. The conventional candidate may fail or prove too narrow; preserve
that result instead of changing acceptance criteria. Task 13 and promotion
remain blocked under the recorded project gate.

## Proposed arithmetic reference examples

These are author-prepared algebra examples for review, not independent accepted
reference vectors or calibration evidence. No random sampling is involved.
The return vectors below represent four aligned complete synthetic UTC days;
these vectors test arithmetic only and do not establish a supported stochastic
design. An independent reviewer must check them before accepting any oracle.

For the single-trial branch set `N_cycle=N_lifetime=K=1`, hence `S0=0`.

| Example | Daily difference returns | Exact expected intermediate values | Proposed score |
| --- | --- | --- | --- |
| R1: zero mean | `[-0.03,-0.01,0.01,0.03]` | mean `0`; sample variance `1/1500`; skew `0`; Pearson kurtosis `41/25`; `S=0`, `D=1` | `Phi(0)=0.5` |
| R2: positive mean | `[-0.02,0,0.02,0.04]` | mean `1/100`; sample variance `1/1500`; skew `0`; kurtosis `41/25`; `S=sqrt(3/20)`; `D=128/125` | `Phi(15/(16*sqrt(2)))`, approximately `0.746306736608969` |
| R3: positive rescaling | Multiply every R2 return by `2` | mean doubles; variance quadruples; `S`, skew, kurtosis and `D` unchanged | Same as R2 |

Derivation: R1 and centered R2 have population second moment `1/2000`
and population fourth moment `41/100000000`; their third moment is zero.
For R2, `D=1+(4/25)*(3/20)=128/125` and the squared CDF argument
is `(T-1)*S^2/D=225/512`. The displayed decimal is descriptive, not a frozen
numerical tolerance. The exact identities are the proposed review targets.

Boundary examples (no numeric score):

- R4: a constant four-day column has zero variance: `INVALID_MOMENTS`.
- R5: one usable R2 column with `N_cycle=N_lifetime=2,K=1`:
  `INCOMPLETE_HISTORY`; count both attempts and do not invent dispersion.
- R6: one usable R2 column with `N_cycle=K=1,N_lifetime=2`:
  `UNSUPPORTED_LIFETIME_HISTORY`; do not import prior-cycle vectors.
- R7: two identical R2 columns, counts all `2`, deliberately constructed as
  duplicates: `UNSUPPORTED_DESIGN` and `DISPERSION_UNAVAILABLE` in that order.
- R8: R2 and its negative, counts all `2`, deliberately paired:
  `UNSUPPORTED_DESIGN`; the squared-correlation effective count must not turn
  this into the single-trial branch. Their Sharpes are opposite and selecting
  their maximum gives `abs(S)`, illustrating the selection issue directly.

These examples cover only some branches. Multi-trial score oracles, selection
and tie cases, invalid timestamps/counts, unsupported moments, and numerical
failure controls remain outstanding; this appendix is not a complete test suite.
```

## Separate-agent review status update — 2026-09-17

The earlier statements that no separate agent ran and reviewer choice was
pending describe the historical preparation snapshot. Scientific and senior
AI reviews have now completed. See [review findings and adjudication](DSR_AGENT_REVIEW_ADDENDUM.md)
for reviewed hashes, independently checked arithmetic, proposed corrections,
and the next deliverable. Both agents reviewed the unchanged attached draft.
Human acceptance, verified different-model review, and calibration remain
outstanding. Claude status remains NOT SENT.
