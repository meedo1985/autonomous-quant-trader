# R-14a modules: design rev 5.1 (lockbox module, confirmation module)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-01. AI drafting, not an authority.
**Status: DESIGN DRAFT rev 5.1** (rev 5 `8a470fc` plus the R14D5-S-1 cleanup of `SOL_DESIGN_RECHECK_8A470FC.md`, §0.3; rev 5 = rev 4 `c2c5131` plus repairs of
`ASTRA_DESIGN_RECHECK_C2C5131.md` R14D4-A-1..3, adjudicated in §0.2 and marked inline;
rev 4 = rev 3 `1d42bb7` plus repairs of `SOL_DESIGN_RECHECK_1D42BB7.md` R14D3-S-1..4,
adjudicated in §0.1; rev 3 = rev 2 `670d56f` plus repairs of `SOL_DESIGN_RECHECK_670D56F.md` R14D2-S-1..4;
Astra's re-check of rev 2 did not complete, `ASTRA_DESIGN_RECHECK_670D56F_ATTEMPT_1.md`).
Replaces rev 1 (`3f141fb`) whole. No code yet.
Nothing here changes a decided rule. Every rule is cited to the signed-C2 draft; a choice
the text leaves open is marked **[DESIGN]**; a choice that could change a result is an
owner question.

**Reviews of rev 1:** `SOL_DESIGN_REVIEW_3F141FB.md` (FIX, R14D-S-1..7) and
`ASTRA_DESIGN_REVIEW_3F141FB.md` (FIX, R14D-A-1..5). Dispositions in §0.

**Authority:** R-14a (`OWNER_DECISION_R14A.md`; text in `s4-amendment-draft/DRAFT_WORDING.md`
l.159), R-10, R-13, R-14, R-14b..d (l.154-162), Annexes A, B, C, D (Annex D rev 2.1,
freeze-sheet `3abcafb`). Frozen code: engine commit `eeaa728`; later object files at main
`eba1c21`. The modules bind only through the owner's signed C2 (R-14a item 1).

**Before the owner signs C2** (R-14a decision): both modules built, each with its complete
input-to-record contract in the signed text, consumer-boundary tests, an independent
different-model review and the owner's §16 PR review; both SHA-256 values in the signed
protocol bytes; R-14b's bindings carried into those bytes (R-14b itself is written,
DRAFT l.160).

---

## 0. Dispositions of the rev 1 reviews

| ID | Disposition | Where |
|---|---|---|
| R14D-S-1 ~ R14D-A-1 (BLOCKER: `screen_gates`, `g11_check`, `g14_check` return availability only; seven gates mis-listed as "glue") | **Accepted.** Verified at `eba1c21`: `screen_gates` returns `None` for an available run and discards the statistics (l.1238-1261); `g11_check` and `g14_check` likewise. Inventory rebuilt gate by gate, primitive vs pass decision. `None` is never read as PASS. | §1 |
| R14D-S-2 ~ R14D-A-3 (BLOCKER: Annex A and G-13 unallocated; `dsr.evaluate`'s nominee is a column index; its classifier is optional) | **Accepted.** Every P18 rule and G-13 now has an owner. The classifier is passed always. | §2 |
| R14D-S-3 ~ R14D-A-2 (BLOCKER: `check_object` rejects the new modules; `__file__` hash is not proof of executed bytes) | **Accepted.** Astra reproduced the refusal. New loader contract uses the existing lower-level checks, extended by exactly the two signed files. | §4 |
| R14D-S-4 (BLOCKER: lockbox pre-read list incomplete; read must depend on `begin_read`) | **Accepted.** | §6.3, §6.4 |
| R14D-S-5 ~ R14D-A-5 (BLOCKER / NON-BLOCKING: contracts are an outline) | **Accepted in part.** The lockbox contract is written in full (§7.1). The confirmation contract is written per gate (§7.2); the exact function names in it depend on Q-P1, and its text must be complete before the owner signs C2, which stays a hard prerequisite. | §7 |
| R14D-S-6 ~ R14D-A-4 (NON-BLOCKING: Q-P1 framing) | **Accepted, Astra's framing.** (b) is the decided baseline; (a) is an optional earlier binding, with the true scope and schedule cost. (a) needs no new exception; the object and the `AQTQ1` post would then carry the new bytes. | §3 |
| R14D-S-7 (NON-BLOCKING: keep the A4 location out of Q-P1) | **Accepted.** Q-D1 is separate. | §5.5 |

### 0.1 Adjudication of the rev 3 re-check (`SOL_DESIGN_RECHECK_1D42BB7.md`)

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, against the cited sources.

| ID | Disposition | Where |
|---|---|---|
| R14D3-S-1 (BLOCKER: the fresh module has no `.py` `__spec__.origin`, so `bytecode_problem()` refuses the valid start) | **Accepted.** Verified: `rundef.py` l.338-342 refuses any `aqt`/`calibration` module whose `__spec__.origin` does not end in `.py`; a module object built without a spec has origin `None`. Repair: build the spec with `importlib.util.spec_from_file_location` and the module with `module_from_spec`, then execute the verified code object into it; the loader's `exec_module` is never called, so the file is not read again. Probe (2026-11-02, repo `.venv`, Python 3.14): a module made this way from in-memory bytes has a `.py` origin and `__cached__` under the prefix, and the frozen `bytecode_problem()` returns `None` before and after loading it. | §4 step 5 |
| R14D3-S-2 (BLOCKER: the `__main__`-guard route executes the file before its own check) | **Accepted.** Running `python module.py` executes whatever bytes are on disk, so a substituted file need not check itself. Repair: the `__main__` route is removed; only a launcher that authenticates the bytes before executing them may start a module. Where the launcher's own text is bound, so that R-14a's "nothing else is loaded" holds, is an open review question (§10). | §4, §10 |
| R14D3-S-3 (BLOCKER: the P18-0 (iii) check would reject an eligible C2 window) | **Accepted in part.** The rev 3 wording was ambiguous and is repaired. Sol's reading, that Annex A exempts C2 from the gap, is not adopted (rev 5, R14D4-A-1 note: the decisive source is DRAFT R-3, l.147, which defines "its first embargo dropped" as excluding the partition's first `gap_embargo.value_days` days, with the start bound at l.196): Annex A l.31-32 makes the v1 partition eligible "with its first `embargo` dropped under (iii)", i.e. the window's first `embargo` days are removed so that (iii) holds; the gap is not waived. The check `w0 ≥ last + embargo` is therefore the same for every cycle, and for C2 `w0` is the partition start plus `embargo`. R-3 settles the reading; no owner question remains (R14D5-S-1). | §2 P18-0 |
| R14D3-S-4 (BLOCKER: A-U1's pre-declaration fail-closed null screen has no owner) | **Accepted.** The screen exists in frozen code: `screen.declare` (`screen.py` l.2012, at `eba1c21`) runs the trial set on the `n_S = 30` simulated null paths and returns `outcome` `SCREEN_AVAILABLE` or `INVALID`. Repair: an allocation row; no new rule. | §2 A-U1 |

### 0.2 Adjudication of the rev 4 re-check (`ASTRA_DESIGN_RECHECK_C2C5131.md`)

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, against the cited sources.

| ID | Disposition | Where |
|---|---|---|
| R14D4-A-1 (BLOCKER: P18-0 (iii)'s embargo source omits R-9) | **Accepted.** Verified: DRAFT R-9 (l.153) replaces "data outside the window" with "data mounted in the sandbox or evaluated before declaration", and `gap_embargo.rule` (l.204) computes the value from that data only. Rev 4 still said "outside the window", which unexposed lockbox data would satisfy. Repair: the governance consumer computes `gap_embargo.value_days` by `gap_embargo.rule` and records its input manifest; the module checks the value against the bound one and the inputs against the pre-declaration mount/evaluation inventory. Restates R-9; no new rule. Also adopted: Astra's stronger citation (R-3, l.147, l.196) for the R14D3-S-3 adjudication. | §2 P18-0, §0.1 |
| R14D4-A-2 (BLOCKER: §7.1 omits Annex D A6's asset and same-series/start checks) | **Accepted.** Verified: Annex D l.371-377 lists, per leg, the asset and "the same series and `start` for both legs"; §7.1's refusals did not. `screen.daily_returns` takes only the result, so it cannot check either. Repair: both checks added to §7.1's refusals, with wrong-asset and different-series tests in §8. | §7.1, §8 |
| R14D4-A-3 (NON-BLOCKING for the design, mandatory before signing: launcher authority) | **Accepted.** Rev 4's suggestion that stating the launcher's text in the signed C2 bytes would admit it is withdrawn: R-14a admits exactly two further files and nothing else. R14D3-S-2 stays **open as a pre-signing build item**: before the owner signs C2 there must be a launch route whose every executed line lies in the engine commit, a later object file, or one of the two signed modules; if none exists, the owner must decide a change to R-14a's draft wording under the applicable process. Neither the design nor a reviewer can admit it. | §4, §10 |

### 0.3 Adjudication of the rev 5 re-check (`SOL_DESIGN_RECHECK_8A470FC.md`, ACCEPT WITH NOTES)

| ID | Disposition | Where |
|---|---|---|
| R14D5-S-1 (NON-BLOCKING: §0.1 still offered a waiver reading of "first embargo dropped" as an owner question) | **Accepted.** DRAFT R-3 (l.147) defines the excluded days and l.196 binds the start, so no waiver reading is open. The caveat is removed; nothing else changes. | §0.1 |

---

## 1. Inventory: frozen primitive vs pass decision, per rule

"Primitive" = a frozen function that computes the gate's statistic or part of it.
"Decision" = the code that turns it into PASS / FAIL / N/A / UNAVAILABLE per Annex C.
All rows verified against `eeaa728` / `eba1c21`.

| Rule (source) | Frozen primitive | Frozen decision? | Missing work |
|---|---|---|---|
| C-0 Sharpe, E-IMPROV, E-DIFF | `statistics.sharpe` l.203, `paired_sharpe_statistics` l.218 | n/a | window/identity/integrity checks in the caller |
| C-6 event contract | `backtest/event_contract.run_event_contract` l.119; `screen.leg_targets`, `benchmark_targets` | n/a | the caller validates original timestamps before `screen.path_series` rebuilds them from row positions (l.911); §7.2 C-T (R14D2-S-4) |
| G-1 paired CI (C-1) | `paired_sharpe_improvement_interval` l.591 | no | `lower > 0` comparison; R-13 stream seed |
| G-2 drawdown (C-2) | `descriptive._max_drawdown` l.232 | no (`gates.g2` = availability) | `DD(BTC)` comparison |
| G-3 ETH sanity (C-3) | ETH run in `screen_gates` (statistics discarded) | no | E-IMPROV `> 0` AND `DD(ETH)` |
| G-4 fold win rate (C-4) | none (`gates.g4` = calibration length check only) | no | **calendar 3-month blocks, integrity, per-block E-IMPROV, win rule, rate ≥ 0.60** |
| G-5 2x cost (C-5) | 2x run in `screen_gates` (statistics discarded) | no | four-condition rule |
| G-6, G-7 delays (C-7) | delayed runs in `screen_gates` (discarded) | no | survival rule C-7 item 4 |
| G-8 plateau (C-8) | neighbours computed in `screen_gates` l.1259 (discarded) | no | **median `m ≥ 0.5·v` and boundary rule** |
| G-9 DSR (A P18-6, Annex B) | `dsr.evaluate` l.120 (rules 1-6, S0, z, column nominee) | no (`choices._passes` l.372 is the calibration-record form) | `z* ≥ z_crit` on the declared nominee; A-V1 Task-12 comparison and disclosure |
| G-10 PBO (C-9) | `gates.SPLITS` l.18 (12,870 splits), `gates.g10` availability | no | **PBO score per split, mean `phi`, `phi ≤ 0.30`; N/A when K < 20** |
| G-11 random null (C-10) | `g11_check` l.1173 draws and statistics (discarded) | no | **≥ 476 of 500 strictly below** |
| G-12 ESS (C-11) | `statistics.effective_sample_size` l.261 | no (`gates.g12` checks all three horizons, calibration form) | `ESS ≥ 120` at the nominee's **declared** horizon |
| G-13 benchmark hash (R-10; DRAFT l.317) | none found | no | hash equality with the v1.1 canonical benchmark hash |
| G-14 shuffled labels (C-12) | `g14_check` l.1205 ICs (discarded) | no | **≥ 476 of 500 null ICs strictly below** |
| C-14 CPCV report (diagnostic) | `type_seven_quantile`, model helpers | no | **8 groups, 28 splits, 7 paths, report**; read by nothing |
| L-1..L-4 (Annex D D-1) | `sharpe`, `paired_sharpe_statistics`, `_influence`, `block_length`, `_uniform_index`, `type_seven_quantile`, `_max_drawdown`, `screen.daily_returns`, `confirmation_path`, `estimator_seed`, `walk_forward` | no | **A4 bootstrap (m ≠ n)**, A6 adapter, L-condition evaluation, bundle (B4.2) |

**Summary.** No C2 pass decision exists in frozen code. The heavy new statistics are G-4,
G-8, G-10 (PBO), G-11, G-14 and the C-14 report; the rest are comparisons on frozen
primitives. Estimated size **[DESIGN, rough]**: 700-1,000 lines plus tests and reference
vectors, of which ~400-600 are the statistics above.

## 2. Annex A allocation (R14D-S-2, R14D-A-3)

| Rule | Executed by | How |
|---|---|---|
| P18-0 (i)-(iv) eligibility, A-B7 (v) | **governance consumer** (the declaration's preparer, before the declaration post) produces the evidence; the confirmation module **checks** it | The declaration must record: the window id and manifest; the non-overlap list against every exposed segment; for (i) the job-log extract showing the window was never mounted in the sandbox and an inventory showing no evaluation output on any part of it existed (verified by a person from the job log and output store, recorded with who verified it); for (iii) the last mounted or evaluated observation instant, and `embargo` = `gap_embargo.value_days` computed by `gap_embargo.rule` (DRAFT l.204) with the manifest of its inputs, every input being data mounted in the sandbox or evaluated before declaration (R-9, DRAFT l.153; no confirmation or lockbox data not so mounted or evaluated; R14D4-A-1); for (iv) the declaration timestamp; `T ≥ T_min`. The module refuses unless every field is present, recomputes the (iii) gap `w0 ≥ last + embargo`, the same check for every cycle (for C2, `w0` = `partitions.confirmation.start` = 2022-01-01T00:00:00Z + `gap_embargo.value_days`, DRAFT R-3 l.147 and l.196; R14D3-S-3) and the (v) count from the manifest, checks the recorded `embargo` equals the bound `gap_embargo.value_days` and that every input in its manifest appears in the pre-declaration mount/evaluation inventory, and refuses on any failure. It cannot itself prove (i)'s negative; that stays a recorded governance check **[DESIGN]** (R14D2-S-2) |
| A-U1 fail-closed screen before declaration | **governance consumer** runs the frozen `screen.declare` on the actual trial set before the declaration is committed; the confirmation module **checks** the record (R14D3-S-4) | The declaration lists the screen record. A set whose record has `outcome` `INVALID`, or that has no record, cannot be declared and spends no `m`. Before the first evaluation the module refuses unless the listed record's bytes match the hash in the declaration, its `trial_set_sha256` equals the declared set's (`screen.trial_set_sha256`), its `qualification_object_sha256` is the posted object, and its `outcome` is `SCREEN_AVAILABLE`. The module does not re-run the screen; the record is seeded from `trial_set_sha256`, so any reviewer can reproduce it **[DESIGN]** |
| P18-1 declared set | confirmation module, before the first evaluation | `1 ≤ |J_f| ≤ 80`, unique ids, complete hashes, both families when eligible; invalid → cycle does not start |
| P18-1 automatic re-run | confirmation module, using `core/attempts.py` accounting | one re-run per family, first crash only, same hash and seed; `attempts.py` l.81-90 disclaims enforcement, so the module enforces it |
| P18-2 one shared look | confirmation module | **Trigger:** the look runs only when, from the attempt records, every declared trial has finished (completed, or crashed with its one re-run used or unavailable), or the cycle clock has reached day 180 (from the recorded cycle start); a look requested earlier is refused. **Pre-pick termination:** if a protocol-revision or invalidation record for the cycle exists, the module refuses the look and records "no pick" (no promotion). One call evaluates both families, trend then volatility; a second look is refused (look record keyed by cycle). Trials unfinished at day 180 are `U_ops` (timeout) (R14D2-S-2) |
| P18-3 availability `A_f` | confirmation module | every declared trial has exactly one completed evaluation with matching hash; finite `S`, valid `T`, finite positive `D`, finite pre-Φ `z`; an unfinished trial makes `A_f` fail, never an omitted column |
| P18-4 nomination | `dsr.evaluate` + confirmation module | matrix columns in **declared-id order**, so `dsr.evaluate`'s lowest-column tie rule is the lowest-declared-id rule; the module maps the column back to the trial id and checks the mapping is a bijection |
| supported-law classifier (D-18 O18-2; prereg §3.5) | `dsr.evaluate(..., classifier=...)` | always passed (`classifier.diagnostics`, `within`); calling without it is refused by the module |
| P18-5 no fallback | confirmation module | only `J_f*` proceeds; no code path nominates another trial |
| P18-6 G-9 | per Q-P1 | `z* ≥ z_crit`, `z_crit` parsed from its decimal string to the nearest binary64 |
| P18-7 every gate regardless; cause codes | confirmation module | every pre-lockbox mandatory gate is computed for every nominee whatever earlier results are; a gate not computed is `UNAVAILABLE`; cause code by fixed precedence: infrastructure/governance (`U_ops`) first, else procedure (`U_proc`) |
| A-V1 | confirmation module | reproduce the frozen reference vectors on the frozen runtime; compute V and Task-12 numerics; V governs; differences disclosed |

## 3. Q-P1, reframed (owner question)

**Where should the missing C2 pass decisions and statistics of §1 live?**

- **(b) Baseline, already decided (R-14a).** In the confirmation module, written after the
  `AQTQ1` post. Bound by the C2 declaration post's chain, reviewed under §16, tested
  against its contract. Accepted residual: promotion statistics are frozen later than
  the qualification object and could reflect knowledge gained after it. No effect on the
  freeze date.
- **(a) Optional earlier binding.** Put the §1 statistics and decisions (not the I/O,
  loading, records or Annex A orchestration) into `screen.py` before step G, as pure
  functions with frozen reference vectors, in one reviewed change. Needs no new
  exception: `screen.py` is in `qobj.LATER` and `REVIEWED`; the route is independent
  review, owner §16 PR review, a new `FREEZE_REVIEWS.json` entry, a new build commit, a
  G0 redo, and step G and `AQTQ1` built from those bytes. **Cost:** ~700-1,000 reviewed
  lines to be merged before the development run ends (~25-26 Nov) or step G waits for
  them; a large `screen.py` change late in the freeze sequence carries its own review
  risk. Even under (a), the confirmation module's alignment and aggregation stay post-freeze
  code (R14D-S-6).

**[AI recommendation]** (b), unless the owner wants the promotion statistics frozen with
the qualification object badly enough to accept a possible delay of step G. Rev 1
recommended (a) on an estimate that was several times too small.

## 4. Loading and the start check (R14D-S-3, R14D-A-2)

**Entry script** (one launcher per module **[DESIGN]**; R14D3-S-2: a module is never
started as `python module.py` or through a `__main__` guard, because that executes the
file's bytes before any check; where the launcher's own text is bound is open, §10):
before importing any
`calibration` or `aqt` module it sets `sys.dont_write_bytecode = True` and points
`sys.pycache_prefix` at a new empty directory (as `scripts/d19_screen.py` l.29-36 do),
so `rundef.bytecode_problem()` can pass.

**Chain (R-14a item 2), before any protected-data read:**
1. the accepted C2 post (O-6a §3);
2. declaration bytes whose SHA-256 is the post's `declaration_sha256`;
3. the declaration's `protocol_hash`;
4. the complete signed C2 protocol bytes hashing to it, containing both module rows;
5. for each of the two module files: the SHA-256 of **the exact bytes that are compiled
   and executed** equals its signed row (R14D2-S-1). The entry script does not `import`
   the module from the path. It reads the file's bytes once, hashes them, refuses on a
   mismatch, then `compile`s **those same bytes** (filename = the repository path) and
   executes them into a module object registered in `sys.modules` under the module's
   name. The module object is made by `importlib.util.module_from_spec(
   importlib.util.spec_from_file_location(name, path))`, so `__spec__.origin` and
   `__file__` are the `.py` path and `__cached__` lies under the empty
   `sys.pycache_prefix`, as `bytecode_problem()` requires (`rundef.py` l.338-342;
   R14D3-S-1); `spec.loader.exec_module` is never called. No second read of the file feeds execution, so a file swapped before
   or after the check cannot be what runs. The signed row is the SHA-256 of the file as
   committed (LF line endings, the git blob bytes), which is what the Linux server's
   checkout holds; a Windows checkout with `core.autocrlf` would refuse, correctly.
   `check_screen_code` then also passes, because it reads the same unchanged file.

**Code check:** the module repeats `screen.check_object`'s steps (manifest against the
posted hash, `qobj.read`, `mapping.check_runtime`) and calls `screen.check_screen_code`
with `reviewed` = the object's `mapping.py` and `screen.py` **plus exactly the two
module files' bytes verified in step 5**, under their repository paths. That function
then (a) checks the engine inventory against the run's `generator_sha256`, (b) calls
`bytecode_problem()`, which refuses any engine module not executed from its `.py`
source, and (c) refuses every loaded `calibration`/`aqt` module whose bytes are neither
the engine commit's nor one of these four. Nothing else is added; R-14's two checks are
unchanged, and any third extra module is still refused.

Each module carries its own copy of this sequence (no cross-import, item 3). A test
checks that the two copies are identical in source **[DESIGN]**.

**Tests:** a valid start passes, including the frozen `bytecode_problem()` itself with
both modules loaded by this route (R14D3-S-1); each broken chain
link refuses before any read; a substituted module file, a stale `.pyc`, a non-empty
cache directory and an extra loaded module each refuse; a file swapped after the hash
check and before execution cannot run (the test swaps it between the read and a
hypothetical second read and shows the executed code object is the hashed bytes'); a
module file run directly is not a supported start (R14D3-S-2).

## 5. Confirmation module (`calibration/c2_confirmation.py` [DESIGN])

Runs as the registered experiment-engine identity, on the confirmation partition the
signed C2 allows; returns only the C2 evaluation record, the prediction artifacts and
the sealing record.

### 5.1 Seeds (R-14a item 7; R-13; D-3.2)

Verified against the governing records, never taken from the caller: the accepted post;
the selected round of the bound quicknet chain (FP3), its BLS signature and randomness,
verified **inside the module** with the pinned verifier library of
`deploy/calibration/drand-verify` against the chain public key in the signed C2
**[DESIGN; open: the library must be importable in the pinned image or the check runs
as a verified subprocess, to settle in review]**; `family_seed_f` (R-7); every
`trial_seed_j` (R-13); each trial's `seed_l266` and `estimator_seed` under
`L266_MOD_2_31`; the C-0 window and id; `g`. Failure: evaluation invalid, no gate runs.
Every value and its source is recorded (§27).

### 5.2 Steps, in order

1. Start check (§4). 2. Declaration validity (P18-0 fields, P18-1). 3. Seeds (§5.1).
4. Per trial: build the path (§7.2 C-T), run the trial and benchmark legs, record
`S`, `T`, `D`, `d_sha256` (pre-look, D-3.5). Crashes go to P18-1 re-run accounting.
5. At the look (P18-2): availability `A_f` (P18-3), `dsr.evaluate` with the classifier,
nominee mapping (P18-4). 6. For each nominee: every gate G-1..G-14 (§1), every one
computed whatever the others give (P18-7). 7. Sealing (§5.3). 8. The C2 evaluation record.

### 5.3 Sealing (A7; R-14a rev 3 item 2; D-3.5), before any lockbox read

For every declared family, status (a)-(d) (D-1.7; (d) over (c)); for status (a):
re-run the nominee's BTC baseline pair from the confirmation bars (registered code,
`estimator_seed`, `confirmation_path`, both legs flat at `w0`, R-14d); require
`SHA256(d)` = the recorded `d_sha256`; `ψ = _influence(d, sharpe(d))`;
`b = block_length(ψ).value`; the A4 forecast (§5.5); build `aqt.lockbox.prediction.v1`
with `code = {lockbox_module_sha256, confirmation_module_sha256, engine_commit,
screen_object_sha256}` (both module hashes from the signed rows); write the artifact and
`aqt.lockbox.sealing.v1`. Any failure → status (d).

### 5.4 C-14 report

Computed only if C-11 effective decisions ≥ 250; otherwise "CPCV not enabled". Written
to the record as `diagnostic_only`; no code path reads it (test).

### 5.5 Q-D1: the A4 generator in both modules (separate from Q-P1)

The confirmation module needs it to compute `q`; the lockbox module needs it for the
startup reference vectors (D-3.4). R-14a item 3 forbids cross-import, and R-14a item 4
places a rule with no frozen function in the module. Proposal: identical function text in
both files, with tests that the two copies' source and A5 reference vectors are
identical **[DESIGN]**. Moving it into a frozen file would be a separate proposed change
to the signed allocation, not part of Q-P1.

## 6. Lockbox module (`calibration/c2_lockbox.py` [DESIGN])

Runs only as `lockbox_eval`; reads BTC/ETH 1h over `[S_pre, L1)` only through the store's
read gate; returns the sealed bundle to the store; research sees PASS/FAIL only.

### 6.1 Startup (D-3.4)

On each process start on the qualified image, after §4: recompute the A5 reference vectors
for the published synthetic `d`; ask the store to append `aqt.lockbox.startup.v1`.

### 6.2 The A4 generator (R-14a item 4)

Seed material: IMPLEMENTATION_CONVENTIONS l.84-94 layout; purpose `lockbox_prediction`,
asset `BTCUSDT`, cost `1.0`, window id `["<w0>","<w1>"]`, `output_length = 457`,
replicate `r = 0..1999`; `seed_hex` the R-13 trial seed. Draw order as
`bootstrap_indices`: `_uniform_index(gen, n)` first, then for each of the next 456 steps
`gen.random() < 1/b` → `_uniform_index(gen, n)`, else `(prev + 1) mod n`. Over `[0, n)`,
457 draws. `T*_r = sharpe(d[idx_r]).scaled`; `q = type_seven_quantile(T*, 0.05)`.
`ReplicateStream` unchanged.

### 6.3 Pre-read checks (D-1.8 item 2; D-3.5; D-3.4), all before any lockbox byte

Immutable lookup and hash match of: the hypothesis record; trial code (A1a artifacts,
hash-before-execute as `screen.load`) and configuration; the nominee's model seed; the
engine and backtester code at the bound commit; the data-manifest hash. Then: artifact
hash = sealing entry; `seed_l266`, `estimator_seed` re-derive under the signed policy;
`seed_hex` re-derives from `family_seed_f` and `trial_id`; `seed_source`, `purpose`, `m`
and both module hashes equal the signed values; P-4; a `PASS` startup record exists for
this module hash and image. Any difference → the Q2b reason code, recorded by
`record_pre_read_check`; nothing read, segment not EXPOSED.

### 6.4 Read and run

The worker does not authorise its own read. `open_read(evaluation_id)` succeeds only
after the publisher's `begin_read` has made the pre-read entry durable with its DEFAULT,
budget and EXPOSED status, and the store's read gate has verified the DEFAULT and the
startup record (D-3.7); each bar is served under the store's `D*` start check. Then:
warm-up from `S_pre`; refits at `r_k = L0 + 30k` (`k = 0..15`) on `[r_k − 24 months, r_k)`,
labels purged at `r_k`, `estimator_seed` (`screen.walk_forward`); both legs flat at L0
(R-14d); `confirmation_path`; the A6 adapter; L-1..L-4 with D-1.6 availability. The whole
read-and-compute runs twice; results must be identical.

### 6.5 Output

`aqt.lockbox.sealed_bundle.v1` without `operational`; precedence DEFAULT > PERFORMANCE >
TECHNICAL > PASS; `reasons` sorted unique `<scope>:<code>`; `values` hexf or null; then
`write_bundle`, `mark_finished`. Store calls **[DESIGN]**: `append_startup`,
`record_pre_read_check`, `open_read`, `write_bundle`, `mark_finished`; tested against a
synthetic store with an injectable clock. The store, publisher and signer are separate
builds (D-3.9).

## 7. Input-to-record contracts (R-14a item 5)

### 7.1 Lockbox module (complete)

| Item | Contract |
|---|---|
| Timestamps read | BTC and ETH 1h bars, `open_time` in `[S_pre, L1)` ascending, each exactly once, served by the read gate under the cycle manifest; the bar at `L1` is never read (`confirmation_path` supplies the final close) |
| Warm-up | EMA, EWMA and benchmark-volatility state from `S_pre`, the feature factory's convention |
| Run window | `[L0, L1)`: hourly instants `L0 + i h`, `i = 0..10,967` |
| Start state (R-14d; D-3.3; D-1.8 item 5) | both legs, BTC and ETH: exposure 0, no pending order, an unset clock, a fresh overlay, equity 1.0, MDD measured from L0; each leg pays its entry cost at its first permitted entry (not at L0) |
| Day pairing | day `k` = `[L0 + k d, L0 + (k+1) d)`, `k = 0..456`; candidate and benchmark legs paired on the same `k`; `d_k = c_k − b_k` |
| Complete-window rule | exactly 457 days and 10,968 hourly segments per leg; anything else → `DAYS_INCOMPLETE` |
| Transformations | daily returns `screen.daily_returns`; `T_L = sharpe(d).scaled`; MDD `_max_drawdown((1.0, *equity))`; E-IMPROV via `paired_sharpe_statistics`; `q` from the sealed artifact, never recomputed |
| Availability → result | D-1.6 items 5-7; A6 failures `DAYS_INCOMPLETE`, `NONFINITE_EQUITY`; equity `EventContractError` → `RUN:NONFINITE_EQUITY`; other runner error → `RUN:RUN_FAILED`; BTC failure nulls L-1..L-3, ETH failure nulls L-4; each atomic comparison null iff an input is null |
| Refusals | missing, duplicate, out-of-order or off-grid bar; per leg, a series whose asset is not the leg's (BTC or ETH); candidate and benchmark legs not on the same series and the same `start` (Annex D A6, l.371-377; R14D4-A-2); series interval ≠ 1 h; start ≠ L0; non-finite or non-positive equity: refuse, never fill or drop |
| Output fields | B4.2 `aqt.lockbox.sealed_bundle.v1` exactly: `schema`, `evaluation_id`, `kind` (RESULT; the DEFAULT is the store's), `result`, `cause_class`, `values {t_l, q, mdd_btc_cand, mdd_btc_bench, eth_e_improv, mdd_eth_cand, mdd_eth_bench}` (hexf or null), `conditions {L1..L4}`, `reasons`, `upside`, `capture {engine_commit, image_digest, input_manifest_sha256, lockbox_module_sha256, prediction_artifact_sha256}`; `operational {read_start, sealed_at, startup_check_id}` filled by the store only |
| A7 fields produced here | none (reads the artifact; checks `code.lockbox_module_sha256` and `code.confirmation_module_sha256` against the signed rows) |

### 7.2 Confirmation module (structure complete; function names depend on Q-P1)

**Status (R14D2-S-3):** this table is the design's contract. Its final signed wording,
with each function named, cannot be written until Q-P1 fixes where the gate code lives.
Completing it in the S4 text is a hard condition **before the owner signs C2** and is
tracked as an open build item, not closed by this design.

| Item | Contract |
|---|---|
| C-T timestamps | confirmation 1h bars of BTC and ETH, `open_time` in `[w0 − warm-up, w1)` ascending, each exactly once; validated **before** `screen.path_series` rebuilds times from row positions (`screen.py` l.911); the bar at `w1` is never read (`confirmation_path`) |
| Day pairing | day `k` = `[w0 + k d, w0 + (k+1) d)`, `k = 0..n−1`, candidate and benchmark on the same `k` and the same symbol, cost multiplier, day index (C-0) |
| Complete-window rule | exactly `n = (w1 − w0)/1 d` days per leg; source `n ≥ 16` for sealing; `T ≥ T_min` (A-B7) checked before computation |
| Per-gate inputs and rules | G-1..G-14 exactly as Annex C C-1..C-12, R-10 (G-9, G-13); G-4 blocks per C-4 items 1-6; G-12 at the declared horizon; every gate computed (P18-7) |
| Transformations | Sharpe, E-IMPROV, E-DIFF (C-0); DSR quantities by `dsr.evaluate`, method V (A-V1); the A4 forecast for sealing |
| Availability → result | Annex C outcomes; "not computed" and "technically invalid" → `UNAVAILABLE` with a P18-7 cause code; seed failure → evaluation invalid, no gate runs; sealing failure → status (d) |
| Refusals | missing, duplicate, misaligned or non-finite observation inside the window: the affected gate or trial is `UNAVAILABLE` with cause, never repaired (C-0 "Outcomes") |
| Output fields | C2 evaluation record: per trial `S`, `T`, `D`, `d_sha256`, attempt ids; per family `A_f`, nominee id, z, every gate result and cause code; every seed and its provenance; the C-14 report; the prediction artifact and sealing record |
| A7 fields produced here | all of `aqt.lockbox.prediction.v1` |

## 8. Tests (the parts these modules own; Annex D D-3.8)

Synthetic data only. Loader (§4). A1a artifacts; A1b seeds (incl. one mapping to 0); A5
vectors and startup refusal; A6 (kernel vs `_max_drawdown` bit-equal; BTC/ETH availability
independent; hourly instants; two-hour series refused; wrong-asset leg and candidate/benchmark on different series (identical timestamps, lengths, starts) refused (R14D4-A-2); terminal bar changes only the last
return); A7 `seed_hex` vector and `seed_source` mismatch; B4.2 byte-exact bundles incl. the
PASS fixture (1,053 bytes, `d64d228b…ba520`); per gate: a PASS, a FAIL and an UNAVAILABLE
case, incl. Astra's examples (negative finite ETH improvement fails G-3; 500 tied null
statistics fail G-11 and G-14); P18-3 an unfinished trial makes `A_f` fail; P18-4 tie by
declared id and the column↔id bijection; classifier omitted → refused; P18-7 a failed gate
does not stop the others; contract tests for each refusal in §7 and that the series
reaching each statistic is exactly the contract's; the duplicated-code identity tests (§4,
§5.5); C-14 read by nothing.

## 9. Build order [DESIGN]

1. Owner answers Q-P1. Under (a), the `screen.py` statistics change first, before step G.
2. Lockbox module (rules complete in Annex D).
3. Confirmation module.
4. Contracts (§7) into the S4 text; module hashes into `<<BUILD>>`.

## 10. Still open (to settle in review or build)

The drand verification library inside the pinned image (§5.1); the exact confirmation
partition access path and identity mechanism; the store interface names (§6.5).

**Pre-signing build item (R14D3-S-2, R14D4-A-3):** the launch route. Every executed line
must lie in the engine commit, a later object file, or one of the two signed modules;
stating a launcher's text in the signed C2 bytes does not admit a third file. If no such
route exists, the owner decides a change to R-14a's draft wording under the applicable
process; this design and its reviewers cannot admit it.
