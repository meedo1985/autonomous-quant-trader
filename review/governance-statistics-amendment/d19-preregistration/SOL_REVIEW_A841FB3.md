# Sol re-review DS4 of the D-19 preregistration rev 4 at `a841fb3`: UNSOUND

Date: 2026-10-04. This is an R19-2 independent statistical re-review by the different model family. The prompt was the same as Fable DF4's, with the ID prefix `DS4`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10704-2fd7-7963-b4a1-e8948d005897`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex, GPT-5 family; exact served identifier unavailable  
Commit: `a841fb3a3b538036cbe2a1058b15666ab5fa8064` (`docs/d19-recommendation`)  
Verdict: **UNSOUND**

### Prior-finding status

| Finding | Status | Assessment |
|---|---|---|
| DF3-1 | PARTIAL | K=2, QJ and the coverage rule were added, but the declaration mapping does not establish membership in any individual qualifying cell. |
| DF3-2 | RESOLVED | Per-cell threshold statistics are retained, recomputed after demotion, and challenge-cell acceptance is reported. |
| DF3-3 | RESOLVED | T levels, availability-only `T_min`, conservative `M_max`, and the 20k/40k rule are fixed. |
| DF3-4 | PARTIAL | Per-attempt keys and payload are supplied, but late O-6a invalidations conflict with held-out namespace burning. |
| DF3-5 | RESOLVED | Integer cluster sizes are specified. |
| DF3-6 | RESOLVED | Q5 includes K=1; G-4 is simulated; cap rate is a 90% UCB. |
| DF3-7 | PARTIAL | Philox and indexing are fixed, but seed symbol `s` and several generator choices remain undefined. |
| DF3-8 | RESOLVED | Screen length, warm-up and infeasible-cost consequence are stated. |
| DS3-1 | PARTIAL | K=2 exists, but the required design-to-cell mapping remains defective. |
| DS3-2 | PARTIAL | A separate AQTQ1 proposal now exists, but its failure semantics are not sound after held-out access. |
| DS3-3 | RESOLVED | Threshold construction now covers all candidate cells and freezes after development. |
| DS3-4 | RESOLVED | `U_G` is one union event and G-10 uses the whole family matrix. |
| DS3-5 | PARTIAL | Several bindings were added, but the dependence, sign-null and hourly-path generators are still not uniquely executable. |
| DS3-6 | RESOLVED | The joint pass figure is explicitly only a plug-in diagnostic. |

### Answers

1. Not every DF3/DS3 finding is resolved; the partial rows above remain material.

2. **O18-4 is not yet met as written.** K=2, QJ sharing BTC days, use of the last `T_C2` exploration days, and the coverage rule are present. However, §3.6 tests against one coordinatewise threshold envelope pooled across all qualifying cells at a T level—not membership in any single qualifying cell, and not even per `(K,T)`. A design can pass that envelope while lying outside every qualifying cell.

3. **AQTQ1 is not ready for `<<OWNER Q-1>>`.** The 39-byte script and per-attempt keys are correct. The blanket “attempt void / namespace not burned” rule is unsound because O-6a permits invalidations discovered after held-out data have been generated or read.

4. There are new defects and remaining overstatement. It is not ready for owner acceptance or pilot authorization until the blockers are repaired and re-reviewed.

### New findings

| ID | Severity | Location | Problem, evidence, fix |
|---|---|---|---|
| DS4-1 | BLOCKER | §3.5 lines 182–186; §3.6 lines 193–205; §11 | **No actual design-to-cell mapping.** Thresholds are pooled per T, while acceptance only checks the pooled coordinatewise envelope. A point can lie inside every pooled marginal range but inside no cell-specific region; an in-memory two-cell counterexample confirmed this. Freeze per-cell, per-`(K,T)` acceptance regions and require that one specific final qualifying cell contains the complete diagnostic vector. |
| DS4-2 | MAJOR | §§3.1–3.4, especially lines 88–112 and 156–160 | **Generators remain non-unique.** The full `Σ` matrices for pairs, duplicates, opposites and factors—and the matrix-square-root convention—are absent. The Q5/QJ sign process does not explicitly say iid fair ±1 and independent of the resampled path, which is required for the claimed exact zero mean. Specify the complete formulas and deterministic construction. |
| DS4-3 | BLOCKER | §4 lines 237–241 versus O-6a §3 lines 46–49 and §5 line 106 | **Late invalidation can erase a seen held-out attempt.** O-6a allows later-post and late-earlier-capture invalidations after a run may have occurred, while rev 4 says the run “is not made” and the namespace is unburned. This contradicts P18-6 and permits retry after information exposure. Pre-run voids may avoid burning; after any held-out generation/access, the namespace and attempt must remain burned, with no retuning. Define that boundary explicitly. |
| DS4-4 | MAJOR | §1 lines 48–49; §3.6; §6 lines 265–268 | **The bound improperly includes the declaration classifier.** §3.6 is a deterministic P18-1 pre-declaration validity check; it is not evaluated inside replications and cannot contribute a stochastic `U_proc^R` event. Remove it from “both classifiers” and treat mapping failure only as declaration invalid/no `m`, or define and simulate a legitimate replication event. |
| DS4-5 | MAJOR | §7.2 lines 307–311; §8 lines 355–366 | **Reproduction remains incomplete.** Resampling hourly bars plus reflecting OHLC does not state how opens are rebased/chained into a continuous path or how drift is removed. Seed variable `s` is also undefined. Freeze the complete OHLCV reconstruction and define every seed symbol. |

### Commands run

- `rtk git status`, `rev-parse`, branch, scoped `git diff`, `diff --stat`, `diff --check`, and tracked/cached-diff checks.
- Read-only `git show` inspection of the named reviews, adjudication, owner decisions, rev 4, O18-4, O-6a rev 5, Annexes A–C, Constitution, protocol and hash rules.
- `.venv\Scripts\python.exe -c ...` in memory:
  - order-statistic tail `1.0999989e-05`;
  - 12-tail union `0.000131999868`;
  - screen powers `0.95760884` and `0.26029963`;
  - AQTQ1 payload 37 bytes and script 39 bytes;
  - coordinatewise-envelope counterexample passed globally but matched no cell.
- Tests/lint/type checks: N/A for a document-only review.
- No network, edits, commits, pushes, confirmation data, lockbox data, or `data/` contents were read. The status command only reported untracked names.
- Local gate: **BLOCKED**. This response is not a committed review record and cannot satisfy the repository’s record requirement until committed separately.

Revision 4 restores K=2, joint-family cells, and the coverage rule, but its global envelope does not prove that a design belongs to any qualifying cell.
The Bitcoin commitment syntax is mostly complete, but a late invalidation can conflict with the rule that seen held-out data permanently burns an attempt.
Do not accept it yet; repair the blockers, re-review and commit this review, then authorize only the measured pilot before deciding on the full run.
