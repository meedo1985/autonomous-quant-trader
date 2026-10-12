# Independent check of the proposal packet's numbers

Date: 2026-10-02. Checker: Claude Opus 5.5 (`claude-opus-5-5`), the
orchestrating session, at the owner's request ("do 1, check the numbers").
A different Claude model from the packet's author (Claude Fable 5.1), but
the same model family: this is **not** the different-model or human review
the rows require, and it closes nothing.

- Checked: `PROPOSAL_PACKET.md` at `b18c02c`.
- Method: `check_numbers.py` in this folder, run as
  `.venv/Scripts/python.exe -B check_numbers.py` (3.14.7 numpy 2.5.3, Windows 11),
  exit 0. Exact values by numerical integration (trapezoid on 200,001
  points over [-12, 12]); the key claims also by simulation with a fixed
  seed (20261002), which the packet did not use.

## Result

| Packet claim | Check | Result |
| --- | --- | --- |
| E[M2] = 1/sqrt(pi), E[M3] = 3/(2 sqrt(pi)) | integration | match to 12 decimals |
| Lemma 1 ratio table, N = 2..162 | integration | all 10 values match to the digits given |
| The ratio does not depend on rho or its sign | simulation, rho from -0.20 to +0.60 at N = 5, 13, 81 | agrees within simulation noise (largest gap 0.0011) |
| Raw N too low for N <= 12, fine from 13 | integration | smallest N with ratio >= 1 is 13 |
| A(N) strictly increasing, N = 2..2000 | direct | true |
| Small-N guard values | integration | all 5 match |
| Sign flip, N = 2: 0.178 and 0.778 | closed form and simulation | match |
| One matrix, three "effective N": 2, 2.5, 2.381 | direct | match |
| N = 100, rho = 0.3, N_eff = 32: S0 1.75 vs E[max] 2.10 | integration | match (1.752 vs 2.098) |
| 3 clusters x 27: E[S0] 1.788, E[max] 0.846 | simulation | match (1.787, 0.846) |
| Hurdle table (14 values) and T = 730 case | root finding | 14 of 15 identical; N = 243, v = 1 gives 2.42, packet 2.43 (rounding) |

Not checked: the rho = 0.9 example (0.25 vs 0.79), because the packet does
not state which N_eff it used there.

## What this check does not establish

- The modelling assumptions behind Lemma 1 (Gaussian trial Sharpes, equal
  variances, a common correlation) and whether the frozen grid's real
  dependence fits them; the packet itself leaves this open.
- The readings of frozen text (line 232, Constitution section 9 line 106,
  the reason codes in P-7) and the external theorems it marks
  UNVERIFIED_EXTERNAL_ASSUMPTION.
- That the proposal is the right choice. Correct arithmetic is necessary,
  not sufficient. D-16 to D-19 stay open; the verdict stays KEEP_BLOCKED.

## Output

```text
== closed-form sanity: E[M2]=1/sqrt(pi), E[M3]=3/(2 sqrt(pi))
E[M2] 0.564189583548 vs 0.564189583548
E[M3] 0.846284375322 vs 0.846284375322

== Lemma 1 ratio c4(N)A(N)/E[M_N]  (packet: .735 .893 .964 .995 .9989 1.0002 1.0045 1.006 1.0068 1.0061)
N=   2 ratio=0.7350
N=   3 ratio=0.8931
N=   5 ratio=0.9639
N=  10 ratio=0.9953
N=  12 ratio=0.9989
N=  13 ratio=1.0002
N=  20 ratio=1.0045
N=  27 ratio=1.0060
N=  81 ratio=1.0068
N= 162 ratio=1.0061

== A(N) strictly increasing 2..2000: True
smallest N with ratio >= 1: 13

== small-N guard E[M_N]/c4(N) (packet: .7071 .9549 1.2372 1.5820 1.6666)
N=  2 0.7071  A(N)=0.5198
N=  3 0.9549  A(N)=0.8528
N=  5 1.2372  A(N)=1.1926
N= 10 1.5820  A(N)=1.5746
N= 12 1.6666  A(N)=1.6648

== simulation of Lemma 1 (ratio does not depend on rho, any sign)
N=  5 rho=+0.00 simulated ratio=0.9632  exact=0.9639
N=  5 rho=+0.60 simulated ratio=0.9639  exact=0.9639
N=  5 rho=-0.20 simulated ratio=0.9647  exact=0.9639
N= 13 rho=+0.50 simulated ratio=1.0013  exact=1.0002
N= 13 rho=-0.07 simulated ratio=0.9996  exact=1.0002
N= 81 rho=+0.30 simulated ratio=1.0079  exact=1.0068

== sign flip (N=2): E[max]=sigma*sqrt((1-rho)/pi) (packet: .178 and .778)
rho=+0.9 exact=0.1784 simulated=0.1782
rho=-0.9 exact=0.7777 simulated=0.7773

== three 'effective N' readings of one matrix (N=3, rho=1/2): packet 2, 2.5, 2.381
eigenvalues [0.5 0.5 2. ]
participation 2.0
Nyholt 2.5
entropy rank 2.3811015779522995

== double counting example N=100 rho=0.3 using N_eff=32 (packet: 1.75 vs 2.10)
E[max]=2.098  S0 with N=100: 2.112  S0 with N_eff=32: 1.752
rho=0.9: E[max]=0.793  S0 with N_eff from same rule? packet .25 vs .79

== 3 clusters x 27 identical trials (packet: E[S0]=1.788, E[max]=0.846)
E[max]=0.846  E[S0]=1.787

== hurdle: annualised Sharpe needed for DSR>=0.95, T=1247, normal returns
packet v=1: .89 1.35 1.74 1.99 2.22 2.35 2.43 ; v=2: .89 1.54 2.10 2.45 2.77 2.96 3.06
v=1: 0.89 1.35 1.74 1.99 2.22 2.35 2.42
v=2: 0.89 1.54 2.10 2.45 2.77 2.96 3.06
T=730 v=1 N=81 (packet 2.91): 2.91
```
