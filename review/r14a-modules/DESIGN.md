# R-14a modules: design rev 1 (lockbox module, confirmation module)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-01. AI drafting, not an authority.
**Status: DESIGN DRAFT rev 1, UNREVIEWED.** No code yet. Nothing here changes a decided
rule. Every rule is cited to the signed-C2 draft text; where this design must choose
something the text leaves open, it is marked **[DESIGN]**, and a choice that could change a
result is raised as an owner question instead.

**Authority, in order:** R-14a (`OWNER_DECISION_R14A.md`; text inlined in
`s4-amendment-draft/DRAFT_WORDING.md` l.159), R-14b..R-14d (l.160-162), Annex D rev 2.1
(`s4-amendment-draft/ANNEX_D_LOCKBOX.md`, freeze-sheet `3abcafb`), Annex A-C, D-11, D-12,
D-20. All on branch `freeze-sheet`. The C2 text is still a draft; the modules bind only
through the owner's signed C2 (R-14a item 1).

**Conditions to meet before the owner signs C2** (R-14a decision, "Conditions carried forward"):
each module built with its input-to-record contract, consumer-boundary tests, an
independent different-model review and the owner's §16 PR review; both SHA-256 values in
the signed protocol bytes; the R-8 extension (R-14b) written.

---

## 1. Finding that needs an owner decision first (Q-P1)

R-14a item 4 says a module calls a frozen function wherever one implements a rule, and
implements a rule itself only where none does. An inventory of the frozen code
(engine commit `eeaa728`, `src/aqt` at that commit, and the later object files at
`eba1c21`) against the C2 gates gives:

| C2 rule (Annex) | Frozen implementation | What is missing |
|---|---|---|
| DSR, rules 1-6, nominee (B) | `calibration/dsr.py evaluate` (engine) | glue only |
| G-1 paired CI (C-1) | `statistics.paired_sharpe_improvement_interval` (aqt) | the pass comparison |
| G-3, G-5, G-6, G-7, G-8, G-11, G-14 (C-3, C-5, C-7, C-8, C-10, C-12) | `screen.screen_gates` (later object) | glue only |
| G-2 drawdown (C-2) | `descriptive._max_drawdown` (aqt); `gates.g2` = availability only | the comparison |
| G-4 fold win rate (C-4) | `gates.g4` = availability only | **the statistic and its pass rule** |
| G-10 PBO (C-9) | `gates.g10` = availability only | **PBO itself (12,870 splits) and its pass rule** |
| G-12 effective decisions (C-11) | `statistics.effective_sample_size` (aqt) | the threshold comparison per horizon |
| C-14 CPCV report (diagnostic) | none found | **the report** |
| Selection rule (A) | not yet inventoried | to be checked in rev 2 |
| Lockbox L-1..L-4 (D-1) | `sharpe`, `_influence`, `block_length`, `_uniform_index`, `type_seven_quantile`, `_max_drawdown`, `screen.daily_returns`, `confirmation_path`, `estimator_seed` | **the m≠n bootstrap (A4)**, the adapter (A6), the bundle (B4.2) |

So under R-14a as decided, the confirmation module would itself implement **G-4, PBO,
the CPCV report and several comparisons**: promotion statistics written after the
`AQTQ1` post. R-14a accepted this kind of residual in general terms ("some statistical
implementation is not frozen at AQTQ1"), and its §2 kept the owner an alternative: move
such code into a frozen file before step G.

Step G cannot start before the development run ends (~25-26 Nov), so that alternative
is still open now. It is no longer open after step G.

**Q-P1. Where should the missing C2 gate statistics (G-4, PBO, CPCV report, the pass
comparisons) live?**

- **(a) Before the freeze, in `screen.py` [recommended].** Pure functions with frozen
  reference vectors, added to `screen.py` in one reviewed change (as PR #81 was), so
  `AQTQ1` binds them. The confirmation module then only loads, verifies, calls and
  records. Cost: a new `screen.py` review and `FREEZE_REVIEWS.json` update, a G0 redo,
  and risk of delaying step G if the review runs long.
- **(b) After the freeze, in the confirmation module, as R-14a allows.** No change to the
  freeze schedule. The residual grows: promotion statistics are bound only by the
  later C2-post anchor, and could reflect knowledge gained after `AQTQ1`.

The lockbox module's own statistics (the A4 bootstrap, the adapter) are already
decided to live in the lockbox module (D-20 Q4, R-14a item 4); Q-P1 does not
reopen that.

Sections 2-6 hold under either answer; under (a) the confirmation module's §4.3 shrinks
to calls.

---

## 2. Files and boundaries (R-14a items 1, 3, 6)

| | Lockbox module | Confirmation module |
|---|---|---|
| File **[DESIGN]** | `calibration/c2_lockbox.py` | `calibration/c2_confirmation.py` |
| Runs as | `lockbox_eval` (worker) | the registered experiment-engine identity |
| Reads | BTC, ETH 1h bars over `[S_pre, L1)` through the store's read gate only (D-1.8) | the confirmation partition the signed C2 allows |
| Returns | the sealed bundle to the store (B4.2); research sees PASS/FAIL only | the C2 evaluation record; the prediction artifact and sealing record |
| Imports | engine-commit modules, later object files, stdlib, pinned image libraries; **not** the other module | same |

Each is one file. Neither reads a path, environment variable or argument that selects
code. The entry points refuse to start unless the R-14a item 2 chain verifies (§3).

**Out of scope here** (separate builds, D-3.9): the store service (index, sealed files,
`L_store`, `begin_read`, read gate, release, delivery, replay), the publisher, the signer,
the access tooling, and the drand fetch. The modules call the store through a narrow
interface (§5.4) so they can be tested against a synthetic store.

## 3. Shared start check: the R-14a item 2 chain

Before any protected-data read, each entry point verifies and logs, refusing on any
mismatch or unverifiable step:

1. the accepted C2 post (O-6a §3);
2. declaration bytes whose SHA-256 is the post's `declaration_sha256`;
3. the declaration's `protocol_hash`;
4. the complete signed C2 protocol bytes hashing to it, containing both module rows;
5. the SHA-256 of the module file actually loaded (`Path(__file__).read_bytes()` at import,
   compared with its row) **[DESIGN]**.

Plus R-14's two checks (engine-commit files, later object files against the posted
manifest), which the existing `qobj`/`screen.check_object` code performs; the module
calls it.

Each module carries its own copy of this check (no shared import, item 3). The two
copies are kept identical by a test that compares their source text **[DESIGN]**.

## 4. Confirmation module

### 4.1 Seeds verified before any gate (R-14a item 7; R-13; D-3.2)

From the governing records, never from the caller: the accepted post; the drand round
of the bound quicknet chain (FP3) and its signature and randomness (the existing
`deploy/calibration/drand-verify` result is an input, verified again here **[DESIGN:
how, in rev 2]**); `family_seed_f` (R-7); every `trial_seed_j` (R-13); each nominee's
`seed_l266` and `estimator_seed = screen.estimator_seed(seed_l266)` under
`L266_MOD_2_31`; the C-0 window and id; `g`. Any failure: evaluation invalid, no gate
runs (`seed_disclosure`). Every value and its source go into the record (§27).

### 4.2 Paths

Confirmation bars → `screen.confirmation_path` (final hour, R-14d) → `screen.path_series`.
Contract items in §6.

### 4.3 Gates

Calls `screen.screen_gates` (with `trial_seed`, `window_id`, `g_days`,
`model_seed = estimator_seed`), `dsr.evaluate`, `paired_sharpe_improvement_interval`,
`effective_sample_size`, `_max_drawdown`; under Q-P1 (b) also its own G-4, PBO and
CPCV code. Writes the C2 evaluation record, including each trial's pre-look `d_sha256`
(D-3.5).

### 4.4 Sealing (A7, R-14a rev 3 item 2; D-3.5)

For each declared family, before any lockbox read:
1. re-run the nominee's BTC baseline pair from the confirmation bars (registered code,
   `estimator_seed`, final-hour rule, both legs flat at `w0`, R-14d);
2. require `SHA256` of `d` to equal the record's `d_sha256`;
3. `ψ = statistics._influence(d, sharpe(d))`, `b = block_length(ψ).value`;
4. the A4 forecast: 2,000 replicates of `m = 457` draws over `[0, n)` (§5.2's generator,
   which the confirmation module must also run, see Q-D1);
5. build `aqt.lockbox.prediction.v1`, `artifact_sha256 = SHA256(cj(artifact))`;
6. write the sealing record with every family's status (a)-(d) (D-1.7). Any failure: (d).

**Q-D1 [DESIGN, raised for review].** A4's generator is needed on both sides: the
confirmation module computes `q` when sealing; the lockbox module recomputes the startup
reference vectors (D-3.4) and never recomputes `q`. Since neither module may import the
other, the generator code exists twice. Proposal: identical function text in both files,
with a test that the two copies' source and reference vectors are identical. The
alternative, putting it in `screen.py` before the freeze, is part of Q-P1 (a).

## 5. Lockbox module

### 5.1 Startup (D-3.4)

On each process start on the qualified image: recompute the A5 reference vectors for the
published synthetic `d` and ask the store to append `aqt.lockbox.startup.v1 =
{startup_check_id, lockbox_module_sha256, image_digest, vectors_sha256, result}`.

### 5.2 The A4 generator (implemented here; R-14a item 4)

Seed material: the production layout of IMPLEMENTATION_CONVENTIONS l.84-94, purpose
`lockbox_prediction`, asset `BTCUSDT`, cost `1.0`, window id `["<w0>","<w1>"]`,
`output_length = 457`, replicate index `r`. Draws follow `bootstrap_indices`' order
(`_uniform_index` start, then per step `generator.random() < 1/b` restart or step
`+1 mod n`), **457 times over `[0, n)`**. `T*_r = sharpe(d[idx_r]).scaled`;
`q = type_seven_quantile(T*, 0.05)`. `ReplicateStream` unchanged.

### 5.3 Pre-read checks and the run (D-1.8, D-3.5)

Pre-read: artifact hash = sealing entry; seeds re-derive; `seed_source`, `purpose`, `m`,
module hashes match signed values; P-4. Any difference: the reason code (Q2b list).
Then through the read gate: warm-up from `S_pre`; refits at `r_k = L0 + 30k`
(`k = 0..15`) on `[r_k − 24 months, r_k)`, labels purged at `r_k`, with
`estimator_seed`; both legs flat at L0 (R-14d); `confirmation_path`; the A6 adapter;
L-1..L-4 (D-1.5) with availability (D-1.6); computed twice, must match (D-1.8 item 6).

### 5.4 Output and the store interface

Builds `aqt.lockbox.sealed_bundle.v1` (B4.2) without `operational` (filled by the store),
precedence DEFAULT > PERFORMANCE > TECHNICAL > PASS, sorted reasons. Store calls used
**[DESIGN]**: `append_startup`, `record_pre_read_check`, `open_read(evaluation_id)` → bar
iterator, `write_bundle`, `mark_finished`. Tests run against a synthetic store with an
injectable clock.

## 6. Input-to-record contracts (R-14a item 5) — outline, filled in rev 2

For each module, a table taken from C-0, C-6, A4, A6, A7:
- timestamps read, in order (hourly `start + i h`, `i = 0..24·m − 1`; window ends by
  `confirmation_path`, never the bar at the end instant);
- day pairing of candidate and benchmark legs (`w0 + k` / `L0 + k` days, both legs);
- complete-window rule (exactly 457 lockbox days, 10,968 hourly segments; source
  `n ≥ 16`);
- each transformation (daily returns, `d_t = c_t − b_t`, ψ, b, replicates, `q`);
- error mapping (`DAYS_INCOMPLETE`, `NONFINITE_EQUITY`, `RUN:RUN_FAILED`, the Q2b codes,
  status (d), `seed_disclosure` invalid);
- output fields, with the A7 field → producing function map.

Missing, duplicate or misaligned observations refuse; nothing is dropped, filled or
re-paired.

## 7. Tests (Annex D D-3.8, the parts these modules own)

Synthetic data only. A1a artifacts; A1b seeds (including a seed mapping to 0); A5
vectors and startup refusal; A6 (kernel vs `max_drawdown` bit-equal, BTC/ETH availability
independent, hourly instants, two-hour series refused, terminal bar changes only the
last return); A7 `seed_hex` vector and `seed_source` mismatch; B4.2 byte-exact bundles
incl. the PASS fixture (1,053 bytes, `d64d228b…ba520`); the R-14a chain (each link
broken refuses before any read); consumer-boundary contract tests (missing, duplicate,
misaligned day/hour each refuse; the series reaching each statistic equals the
contract's); the two duplicated-code identity tests (§3, Q-D1). Store, signer, publisher
tests belong to their own builds.

## 8. Build order **[DESIGN]**

1. Owner answers Q-P1. Under (a): the `screen.py` gate change first (design, review,
   §16 PR, `FREEZE_REVIEWS`, G0 redo) before step G.
2. Lockbox module (smaller, its rules fully stated in Annex D).
3. Confirmation module.
4. Contracts (§6) written into the S4 text; R-14b; module hashes into `<<BUILD>>`.

## 9. Open for rev 2

Annex A selection-rule inventory; drand re-verification inside the module; the exact
confirmation-partition access path; C-14 CPCV's inputs; the full §6 contract tables.
