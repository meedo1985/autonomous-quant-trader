# Fable narrow re-check DF5 of the D-19 preregistration rev 5 at `327aa3d`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent narrow re-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Model: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. The drafter, Claude Opus 5.5, is in the same family, so this is only the Claude half of R19-2.
Commit: `327aa3d` (branch `docs/d19-recommendation`). Object: `PREREGISTRATION.md` rev 5. Scope: `git diff a841fb3 327aa3d` of that file only.
Verdict: **READY WITH FIXES.** All eleven DF4 and DS4 findings are resolved. No finding below is a BLOCKER or MAJOR. The five MINOR fixes are wording edits that can be made in the acceptance text, and none of them needs another review round.

## Status of DF4 and DS4

| ID | Status | Note |
|---|---|---|
| DF4-1 | RESOLVED | The mapping now uses each cell's own per-tail order statistics, at the design's `K` and `T_C2`. The cell ids are recorded, and §11 is reworded to match. |
| DF4-2 | RESOLVED | (a)–(e) are all addressed: the pre-run and post-run failure boundary, the horizon substitutions, the run after the freeze read and the round's publication, the `v{n+1}` namespace, and `D_Q2` fixed in the attempt-2 record. Residuals: DF5-1, DF5-2, DF5-3. |
| DF4-3 | RESOLVED | A coverage table is added, and Q2m is added for unequal moments. Residual: DF5-5. |
| DF4-4 | RESOLVED | The Σ formulas are complete. The within-group ρ is 0.9. The factor formula, the pairing and the bar chaining are stated. Residual: DF5-4. |
| DF4-5 | RESOLVED | Development uses the envelope over all candidate cells. The refusal gap of up to about 1.3e-4 is disclosed. |
| DF4-6 | RESOLVED | The τ values are quoted at `M_max ≈ 1,143`, and the compute estimate is marked stale. The pilot now includes a mapping run. Q2m raises `M` slightly. The text says the manifest prints the exact values, which is acceptable. |
| DS4-1 | RESOLVED | The design must lie in one specific cell's region (same as DF4-1). |
| DS4-2 | RESOLVED | The symmetric eigen square root is used with eigenvalues clipped at 0. The full Σ matrices are given. The signs are iid fair and independent of the path. Residual: DF5-4. |
| DS4-3 | RESOLVED | An invalidation at or after the run's start is a failed attempt: the namespace is burned and P18-6 applies. Residual: DF5-2. |
| DS4-4 | RESOLVED | The declaration mapping is removed from `U_proc^R` (§1, §6). |
| DS4-5 | RESOLVED | The OHLC reconstruction and chaining are specified, gaps are dropped, and no demeaning is stated. `s` is defined. |

## New findings

| ID | Sev | Location | Problem | Fix |
|---|---|---|---|---|
| DF5-1 | MINOR | §4 failure boundary, step 7 | Only two keys exist. A void consumes a key, so a void of attempt 2, or a void of attempt 1 followed by a failure, leaves no key, and the outcome is unstated. It is also unclear whether a void attempt counts toward "at most one further attempt". | State that voids consume keys. When no key remains, qualification has not been obtained under this preregistration. Any further key needs a new acceptance. |
| DF5-2 | MINOR | §4 failure boundary | "Found before the held-out run starts" depends on when someone looked, and the start time is not tied to a record that can be checked. | Before the run, commit a pre-run O-6a invalidation check and a run-start record. An invalidation that is not in that committed check is a failure, even if the chain shows it existed earlier. |
| DF5-3 | MINOR | §4 "Keys and coins" vs "Horizons" | The acceptance placeholder still fixes `D_Q2` at acceptance. "Horizons" says `D_Q2` is fixed in the attempt-2 record. The two statements contradict each other. | Remove `D_Q2` from `<<ACCEPTANCE: …>>`. Keep `A_Q2` and `F_Q2` in it. |
| DF5-4 | MINOR | §3.2 dependence table, "opposites" row vs §3.1 | The table says "the first floor(K/2) columns are negated". The new Σ already sets −0.9 between the groups. If the negation is also applied, the between-group correlation becomes +0.9. My in-memory check confirms the Σ is PSD, with minimum eigenvalue 0.1 for both opposites and unequal clusters. | Rewrite the table row as "Σ per §3.1 (0.9 within, −0.9 between); no further negation". |
| DF5-5 | MINOR | §3.2 Q2m | "Half" is undefined at odd `K`, and it is not said which columns are t₅. If the laws and the scales both alternate by index, law and scale are confounded: every t₅ column gets the same scale. | State the assignment exactly, for example: columns `j < ceil(K/2)` are t₅; `c_j = 0.5` for even `j` and `2` for odd `j`. Check that both laws have both scales at each `K ≥ 5`. At `K = 2`, accept the confounding or state that it is accepted. |

Development refusal is measured with the wider thresholds. As a result, development may understate held-out DSR availability by up to about 1.3e-4, which is about 11% of τ_DSR. This is disclosed and does not affect validity. The pilot should report the margin.

**Commands:** `git rev-parse HEAD` (`327aa3d`), `git diff --stat`, the scoped `git diff`, and a `grep`/`sed` of rev 5. `.venv\Scripts\python.exe -c` ran in memory to compute the minimum eigenvalues of the cluster and opposites Σ (0.1 at `K` ∈ {2, 5, 20, 80}). No files were written, nothing was edited, committed or pushed, and no network was used. `data/`, the confirmation data and the lockbox data were not opened. Tests, lint and type checks are N/A because this is a review of a document only.

## For the owner

1. All the problems the reviewers raised last round have been fixed on paper. That includes "does my strategy design match a tested case" and "a problem after the result is seen counts as a failure, not a retry".
2. Five small wording gaps remain, such as what happens if both Bitcoin attempt keys get used up. The author can close them in the text you accept, without another review round.
3. You can be asked to accept it, together with your Q-1 Bitcoin-fingerprint decision. A measured pilot must come first, before any full run. Nothing has been built or run, and nothing here is evidence of a trading edge.
