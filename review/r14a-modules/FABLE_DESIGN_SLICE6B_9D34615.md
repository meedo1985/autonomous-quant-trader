# Fable design review: slice 6b design rev 2 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and proposes no
  automatic edit; every correction below is a proposal for the author and the owner.
- Date: 2026-11-13.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `9d34615` (rev 2). Branch
  `confirmation-module`, HEAD `72fe37d` (the only change after `9d34615` is
  `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md`).
- Read: the rev 2 design in full; rev 1 (`git show 1e6e672:...`);
  `SOL_DESIGN_SLICE6B_1E6E672.md`, `ADJUDICATION_DESIGN_SLICE6B_1E6E672.md`;
  `FABLE_REVIEW_SLICE6_3765910.md` (F-3, F-4, F-5), `ADJUDICATION_FABLE_SLICE6_3765910.md`;
  `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md`; `DESIGN.md` §2, §5, §7, §10;
  `calibration/c2_confirmation.py` l.625-956, 1489-1700, 1824-2078, 2340-2902;
  `calibration/dsr.py`, `reduce.py`, `classifier.py` (whole files); `calibration/c2_lockbox.py`
  l.719-756, 1210-1345; `calibration/qobj.py` l.1-70, 215-223; `calibration/mapping.py`
  l.1-40, 105-127; `scripts/d19_choose.py` l.110-175; `scripts/d19_heldout.py` l.176-193;
  `src/aqt/core/ledger.py`, `src/aqt/core/attempts.py` (whole files);
  `src/aqt/data/manifest.py` l.1-250, 360-838; `docs/RESEARCH_CONSTITUTION.md` §16, §26, §27;
  `protocols/protocol_v1.yaml` l.8-20, 55-75; from `origin/freeze-sheet`: `DRAFT_WORDING.md`
  (R-3, R-8, R-12, R-14, R-14a, R-14b, `seed_disclosure`, §3), `ANNEX_A_SELECTION_RULE.md`
  (P18-1, P18-2, P18-3, P18-4, P18-7, A-B7, A-U1, A-V1), `ANNEX_B_DSR_METHOD.md` (l.69-91,
  150), `o6a-channel/SPEC.md` (§5 capture lines); D-19 `PREREGISTRATION.md` §3.5, §3.6.
- Ran (one script, in the session scratchpad, synthetic data, no repository file written):
  option (b)'s recomputation against `dsr.evaluate(numerics="v")` for (T, K) = (200, 1),
  (300, 5), (457, 20), both block rules. `dsr._V_VERIFIED` was set by hand, so this is the
  local Windows runtime, not the pinned one. Result: `S0`, the nominee `z` and the nominee
  index were bit-equal in all six cases. `z_j` computed through Annex B's
  `D_j = (T-1)·var_b` was **not** bit-equal to `(S_j - S0)/sqrt(var_b)` in 15 of 52 columns
  (see F-6).
- No test suite, lint or type check was run: this is a design review and no code changed.

## Verdict: FIX

Rev 2 is a large improvement: the order (S-4), the two-record boundary (S-7), the record
identity fields (F-4) and option (b) are sound in direction. It is not ready to build
from, because four parts cannot be implemented as written without a choice that changes
the result or the one-look guarantee (F-1, F-2), and several "verified how" entries
promise more than the mechanism gives (F-3, F-4, F-5).

## Findings

| ID | Severity | Section | Finding (short) |
|---|---|---|---|
| R14D6B2-F-1 | blocker | §8, A-6 | The classifier bounds are still caller bytes plus a new signed row, re-pooled over an unspecified `cells`. The frozen per-T thresholds already sit in the qualification object that `start` verifies (`choices.json` `final_thresholds`); re-pooling `cell_bounds` would give the wider development thresholds. S-5 is not fully answered. |
| R14D6B2-F-2 | blocker | §2, §10 | The look record is both the source of `now` and the evidence for `looked`; who writes it, when, and what a look that aborts after the read leaves behind are undefined. As written, a look that fails after `read` can be run again. |
| R14D6B2-F-3 | major | §3 | The rules for result entries cover only "completed attempt has exactly one entry in its span". Entries in a crashed attempt, after the outcome, for an open attempt, or a second `evaluate_trial` on the same attempt are undefined; `evaluate_trial`'s own preconditions and who writes start and outcome are not stated; P18-1 "no result artifact" is not enforced. |
| R14D6B2-F-4 | major | §2 A-1 | An anchor taken at declaration time protects nothing written after it, and every cycle entry is written after it. The stated residual ("no second ledger") understates this. The reason given for option (a) over (b) does not hold, and (a) as worded has no verifiable source. |
| R14D6B2-F-5 | major | §5, A-4 | The manifest check cannot be met with the repository's manifest format: a partition manifest hashes the whole partition per symbol, its identity is not `SHA256(manifest)`, the cycle hash is a composite, and a model trial's warm-up reaches back into the exploration partition. |
| R14D6B2-F-6 | major | §7 | `D_j` is recorded as `var_b(S*_j)`. Annex B defines `D_j = (T-1)·var_b(S*_j)`. The record would carry a frozen name with another value. |
| R14D6B2-F-7 | major | §4 | With the split, `nominate` returns at the first failing trial in id order, so a U_proc trial before a U_ops trial gives the family U_proc. P18-7 fixes U_ops first. `DAYS_INCOMPLETE` is added to the U_ops list here but not to `U_OPS_REASONS`, so trials and gates would code the same reason differently. |
| R14D6B2-F-8 | major | §7, owner record | Not flagged: R-14a item 1 already makes the confirmation module a §16-reviewed file, so "whether it is protected" is not open; and option (b) composes S0, D and z in the module, which R-14a item 4 ("calls it and does not re-implement it") and item 5 (contract lists it) touch. |
| R14D6B2-F-9 | major | §2 | `cycle_start` (P18-2 day 180) has no source in the table. It is the one remaining input of `look_allowed` that is neither read nor listed as an owner item. |
| R14D6B2-F-10 | major | §9 | The evaluation record has no Task 12 fields. A-V1 requires every real evaluation to compute and report the Task 12 numerics and disclose a differing decision. |
| R14D6B2-F-11 | minor | §3 | At the look only four fields are compared with independent values. `seed_l266`, `trial_index`, `protocol_hash`, `engine_commit`, `confirmation_module_sha256`, `image_digest`, `family`, `days` are recorded but not compared. |
| R14D6B2-F-12 | minor | §6 | "The parameters must hash to `drand_chain_hash`": drand's chain hash also covers values that are not in the row list (to my memory the genesis seed and a non-default beacon id). Not verifiable offline; needs a known-answer test. |
| R14D6B2-F-13 | minor | §6 A-5 | The capture time "comes from its frozen capture record", but the acceptance record `start` verifies has an exact field set without it, so the capture record is a second store-supplied object with no stated check. |
| R14D6B2-F-14 | minor | §2 | `now` from a ledger entry is the appender's clock. "Verified how: ledger order" is not a verification of time (`ledger.py` l.20-24). |
| R14D6B2-F-15 | minor | §2, §6 | "Signed row if bound there, else the declaration's field" is a two-source rule; integer and time rows have no stated exact parse; `z_crit` and `family_block_rule` rows are not required to equal the qualification object's values. |
| R14D6B2-F-16 | minor | §2 | `verify_ledger(...)` then `read_entries(...)` reads the file twice; the recorded head and the entries used can differ. |
| R14D6B2-F-17 | minor | §3, §4 | Contract changes the design needs but does not name: `family_attempts` does not return `attempt_id`; `completed_entry` returns no reason; `nominate`'s `ops()` can only say U_ops. |
| R14D6B2-F-18 | minor | §10 | DESIGN §2 says a pre-pick termination "records no pick". §10 says a step 5 failure leaves no record. One of them must say who records it. |
| R14D6B2-F-19 | info | §7 | Option (b) holds on what I could run; the private functions it calls are inside R-8's binding. Three small tightenings. |

## Details

### R14D6B2-F-1 (blocker): the classifier bounds have a verified source that the design does not use

- Where: design §8 l.184-193, §6 l.156, §2 l.44; `calibration/qobj.py:66-67`, `215-222`;
  `scripts/d19_choose.py:119`, `134-143`, `163-167`; `scripts/d19_heldout.py:188-192`;
  `calibration/c2_confirmation.py:2601` (`_, defn = qobj.read(files)`); prereg §3.5
  l.208-209.
- What the code and the preregistration say. Prereg §3.5 item 3: "Before the freeze, each
  threshold is set per `T` level, as the extreme of the stored statistics over the
  **final** qualifying cells ... Validity rests on the held-out run, which uses the frozen
  thresholds." `d19_choose.py` writes exactly that into the report as
  `final_thresholds["T=<t>"] = {upper, lower}` (pooled over final qualifying cells only),
  and also `cell_bounds` for **every** unit, qualifying or not. `qobj.REPORT` requires both,
  and `z_crit` and `family_block_rule`, in the object's `choices.json`. `start` already
  verifies that file against the signed `qualification_object_sha256`
  (`verify_code` → `qobj.read(files)`), and then throws the report away. The frozen
  held-out runner is the model consumer: `frozen = report["final_thresholds"][f"T={t}"]`,
  then `reduce.for_k(pool, k)`.
- What rev 2 does instead. The caller supplies a "D-19 bounds document" as bytes, bound by a
  **new** signed row `classifier_bounds_sha256`; the module computes
  `reduce.pooled(cells)[T]`; `cells` is not defined; "which document" is left to the owner
  (A-6).
- Failure scenario. The obvious document with per-cell bounds is `cell_bounds`. Pooling it
  with `reduce.pooled` gives the extreme over **all** candidate cells. Those are the
  development thresholds of §3.5 item 2 (`d19_choose.py:119`), which are at least as wide
  as the frozen ones. A real-window matrix outside the frozen thresholds but inside a
  non-qualifying cell's tail is then accepted, where the certified procedure returns
  `UNSUPPORTED_LAW`. The error rate certified by the held-out run no longer describes the
  classifier that ran. Nothing in the design's checks would notice: the document hashes to
  its row, T is present, `for_k` succeeds.
- This is also check 1 of the task: a caller-trusted value with a verifiable source. Sol's
  S-5 asked to "verify the bounds are from the qualification object that certifies the
  signed `z_crit`". Rev 2 moves that to an owner item instead of doing it.
- Minimal correction (proposal). No bounds document and no `classifier_bounds_sha256` row.
  `start` keeps the verified report (one more field on `Started`, or the three values
  taken from it). The classifier is
  `upper, lower = reduce.for_k(pool, K_f)` with `pool` built from
  `report["final_thresholds"][f"T={T}"]` exactly as `d19_heldout.py:188-192` does; a missing
  `T=` key refuses before any read. No call to `reduce.pooled` at evaluation time. The
  signed rows `z_crit` and `family_block_rule` must equal `report["z_crit"]` (a decimal
  string, `choices.py:599`) and `report["family_block_rule"]`, or be read from the report.
  A-6 then needs no decision beyond "the qualification object's". Test: thresholds taken
  from `cell_bounds` or from another object are refused or give a different, pinned result.
- Smaller point in the same section: a `for_k` `ValueError` (no K ≥ 2 cell at that T) is
  made evaluation-invalid for both families. `classifier.within` treats another K or T as
  a refusal of that family (`UNSUPPORTED_LAW`, U_proc^R, prereg §3.5 "Cause"). State which
  is meant. Refusing before any read is the safe direction, but it should be a stated
  choice.

### R14D6B2-F-2 (blocker): the look record's life is undefined, so "never twice" is not enforceable as written

- Where: design §2 l.42 ("`now` ... the store's look record time (ledger entry)"), l.61-65
  (steps 4-7), §10 l.212-214; `look_allowed` `c2_confirmation.py:827-837`; DESIGN §2 P18-2
  row ("a second look is refused (look record keyed by cycle)"); Annex A P18-2 ("exactly one
  nomination look per cycle").
- What is missing. `look_allowed(..., looked)` refuses when a look record exists. `now`
  is read from a look record. So for the first look a look record must exist (to give
  `now`) and must not exist (`looked` false). The design does not say which record is
  which, who appends it, at which step, or with what payload.
- Why it matters: the failures after the read. Rev 2 has at least four `CycleError` paths
  **after** `read`: the C-T check and the manifest check (§5), the option (b) mismatch
  (§7), and `seal_family`'s `CycleError`s (`c2_confirmation.py:1976`, `1993`). §10 says
  these leave "no record". Take the two possible readings:
  1. The look record is written only when the look completes. Then a look that read the
     confirmation bars, computed both nominees and aborted leaves nothing in the ledger.
     The next call finds `looked` false and runs again. That is a second look. Between the
     two, records, bounds, or trials' states can change (a running trial completes; at day
     180 the family that was U_ops becomes evaluable).
  2. The store writes the look record before calling. Then either `looked` is already true
     and the first look is refused, or the module must ignore "its own" look record, and
     nothing says how it tells that record from an earlier aborted look's.
- Also unprotected: the ledger is read at step 4 and the bars at step 7. A termination or
  invalidation record appended in between is not seen, and the look proceeds after the
  cycle ended (P18-2 last sentence).
- Minimal correction (proposal). One rule, in the module: after step 6 and before `read`,
  `evaluate_look` itself appends one entry, `aqt.c2.look.v1`, with
  `{cycle_id, decided_at_head, decided_at_count}`, using `append_entry`; it requires the
  returned entry's `sequence == decided_at_count` and `previous_hash == decided_at_head`
  (nothing was appended since step 4), and refuses before the read otherwise. `looked` is
  "any `aqt.c2.look.v1` for this cycle exists in the entries read at step 4". `now` is this
  entry's `recorded_at_utc`, taken from the module's own clock at the append, and recorded
  as a claim (F-14). A look that aborts after the read has then used the cycle's one look:
  say so in §10, and say who records the cycle outcome (F-18). `evaluate_trial` refuses
  when a look or termination record exists (F-3). Tests: a second `evaluate_look` after a
  post-read abort is refused; an entry appended between step 4 and the look entry refuses
  before any read.

### R14D6B2-F-3 (major): result-entry rules and `evaluate_trial`'s preconditions are incomplete

- Where: design §1 l.23-24, §2 l.67, §3 l.88-108; `family_attempts`
  `c2_confirmation.py:730-768`; `trial_states` l.771-824; `attempts.py:54-59`, `365-400`;
  Annex A P18-1 ("ends without writing any result artifact ... Any other failure (partial
  output, second crash, slot already used) is final for that trial").
- What is specified: for every **completed** attempt, exactly one entry in `(start, end)`,
  with matching payload. A test obligation also says "an entry outside the attempt's span
  is refused", which the rule itself does not say.
- What is not specified, with the scenario for each:
  1. **Who writes the start and the outcome.** `evaluate_trial(started, sources, trial_id,
     read)` takes no `attempt_id`. The design says the entry "must lie between the attempt's
     start entry and its outcome entry" but not that `evaluate_trial` requires an open
     attempt for this trial (state `running`, permitted by `trial_states`) before it reads,
     nor which outcome an unavailable run gets. If the store records `failed` for a run
     with `d: null`, the trial is `final`, `nominate` reports "no completed evaluation"
     (U_ops) and §4's split never applies; if it records `completed`, §4 applies. The cause
     code then depends on an unstated store choice.
  2. **Outcome before entry.** The order start, outcome `completed`, entry gives a completed
     attempt with no entry in its span. The look raises `CycleError` at step 4, and because
     the ledger is append-only it does so at every later call: the cycle can never be
     looked at and nothing is recorded. This is reachable without bad intent: the frozen
     `append_entry` cannot append "only if my attempt is still open", so a recovery process
     that records an outcome while a slow `evaluate_trial` is still running produces it.
  3. **Entry inside a crashed attempt.** Start, entry, then outcome `failed` with
     `CRASH_NO_ARTIFACT` (the process died after the append and recovery coded a crash).
     `trial_states` grants the re-run slot. But a result artifact was written, and P18-1
     says such a failure "is final for that trial". Rev 2 only looks at completed attempts,
     so the re-run is accepted and the first result is ignored.
  4. **Second `evaluate_trial` on the same open attempt** (restart after a crash that
     recorded no outcome): two entries in the span; the look is refused for ever, as in 2.
  5. **Record written, entry not.** The record and the entry are two writes. A crash
     between them leaves a stored result with no ledger trace; the attempt is coded
     `CRASH_NO_ARTIFACT` and re-run, although an artifact exists.
  6. **`evaluate_trial` after the look or after a termination record**: steps 1-4 "without
     the look records" then read. Confirmation bars are read for a cycle that has ended.
- Minimal correction (proposal).
  - Put the whole record in the entry: payload = the `aqt.c2.trial_result.v2` record itself
    (hex strings only, so the ledger's no-float rule holds; about 25 KB per trial). The
    artifact then exists if and only if the entry does, one fsynced append; scenario 5
    disappears, the store hands over nothing at the look, and "swap" or "omit" has no
    object left to act on. `record_sha256` stays as the name the evaluation record uses.
  - `evaluate_trial` reads the ledger, requires: no look and no termination record; the
    trial's last attempt open, permitted by `trial_states`, and without any result entry;
    then reads, computes, appends the entry, and itself calls `finish_attempt(completed)`,
    also for an unavailable run (the reason is in the record). It takes `attempt_id` from
    that open start.
  - One global rule at the look, for every `trial_result_entry` of this cycle: it names an
    attempt of this cycle; it lies after that attempt's start; there is at most one per
    attempt. Then by case: completed attempt with exactly one entry before its outcome is
    used; an attempt with outcome `CRASH_NO_ARTIFACT` and an entry is **not** a crash for
    the slot (the trial is final, no re-run permitted); a completed attempt without a valid
    entry, or an entry after the outcome, makes that family's `A_f` fail with a U_ops
    reason that names it, instead of ending the cycle without a record. The last choice
    touches P18-1 and P18-7 wording, so it is the owner's.
  - Tests for each of 1-6.

### R14D6B2-F-4 (major): the anchor does not cover what it is listed as verifying

- Where: design §2 l.37-39, l.46-54; `ledger.py:1-36` (hash chain, no signature);
  `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md` (A-1 accepted as direction only).
- The ledger is a hash chain without signatures. Anyone who can write the file can rebuild
  any suffix with consistent hashes. An anchor fixes the prefix up to the anchor. A-1 takes
  the anchor at declaration time; P18-1 puts every attempt after the declaration. So every
  start, outcome, result entry and look record of the cycle is in the unanchored suffix.
- Scenario. After an unfavourable trial result, the ledger is truncated to the anchor (or
  to any later point) and regrown: the crashed attempt is gone, the trial is "run" again,
  the new entry binds the new record. `verify_ledger` passes, the chain extends the anchor,
  every §3 check passes. The same holds for removing a first crash so that another trial
  gets the slot.
- So the table's "Verified how" for attempt history, pre-look entries and look records is
  true only against accidental damage and against rewriting pre-cycle history. The stated
  residual ("it cannot prove that no second ledger exists") is one case of the real one:
  **nothing after the anchor is authenticated by the module.** That should be the written
  residual, as plainly as the lockbox `Store` docstring puts its own.
- The recommendation's reason. "(a) because the declaration is posted before any attempt
  exists and the anchor must cover appends made later": neither option covers later
  appends. And (a) "a signed or hash-committed cycle record" names no verifier: the module
  has no signature check for it, and a hash commitment needs a place the module already
  trusts. The only such place is the posted declaration, which is option (b). As worded,
  (a) is a store-supplied file, which is what S-1 removed.
- Minimal correction (proposal). Put `ledger_anchor {head_hash, entry_count}` (not the
  path) in the declaration; the existing chain verifies it. Require every entry of this
  cycle to lie after the anchor (a start with this `cycle` before it is refused). State the
  residual as above. After the look the situation is better and the design can say so: the
  evaluation record carries `ledger.head_hash` and the sealing record carries the
  evaluation record's hash, so later consumers can require extension of that head. If the
  owner wants the pre-look history witnessed, the only real means is an outside commitment
  of the head (for example the head hash stored with each result by the same route as the
  declaration); that is an owner decision, not something the module can supply.

### R14D6B2-F-5 (major): the manifest check does not fit the repository's manifests

- Where: design §5 l.132-142, §2 l.40, A-4 l.228; `manifest.py:135-142` (`canonical_hash`
  removes `manifest_sha256`), `195-240` (`encode_bar_series`: the row count and every bar
  are in the bytes), `369-410`, `545` (`parsed_sha256` over the whole partition series of
  one symbol), `735-751` (composite over three partitions per symbol);
  `screen.py:1540-1543` (`model_warmup_hours`: the training months plus the required
  history); `protocols/protocol_v1.yaml:64-66`; `c2_confirmation.py:1542-1563`
  (`data_manifest_hash` is one hash in the Annex B seed).
- Four mismatches with "recompute the served bars' hash ... require the manifest to list
  exactly that hash ... `SHA256(manifest)` equals the cycle's hash":
  1. `read` returns two series; a partition manifest is for one symbol. There are two
     hashes and two manifests, not one.
  2. A partition manifest's `parsed_sha256` is over that symbol's **whole** partition
     series. The served span `[w0 − W, w1)` is a different series (other row count, other
     rows), so its hash is in no exploration-format manifest.
  3. The span crosses partitions. `w0` is 2022-01-01 plus `g`; a model trial's warm-up is
     about two years, so the served bars start in the exploration partition
     (2017-08-17..2021-12-31). No single partition manifest covers them.
  4. A manifest's identity in this repository is `canonical_hash(as_mapping())` with the
     self field removed, and the cycle-level identity is the **composite** manifest's hash,
     not `SHA256` of one manifest's bytes.
- Consequence. With A-4's recommended "exploration-manifest format" the check as written
  always fails; an implementer must invent a served-span manifest, which is a new format
  nobody reviewed, or weaken the check. The S-3 test ("bars from another manifest are
  refused") would then prove whatever the invented format makes it prove.
- Minimal correction (proposal), with frozen functions only: `read` returns, per symbol,
  the confirmation `PartitionManifest`, the exploration one, their full `BarSeries`, and
  the `CompositeManifest`. The module calls `verify_partition_manifest(m, series=s)` for
  the four, `verify_composite_manifest`, requires the four to be the composite's entries
  and `composite.manifest_sha256 ==` the cycle's `data_manifest_sha256`, then cuts
  `[w0 − W, w1)` itself and runs `check_confirmation_read` on the cut. State that the
  module then holds confirmation bars in `[2022-01-01, w0)` (the embargo days) and never
  uses them; that is inside the confirmation partition but should be said, because R-14a
  item 6 is about what is read. If the owner prefers a served-span manifest, its format
  and its builder are a separate reviewed item before §5 can be built.

### R14D6B2-F-6 (major): `D_j` in the record is not Annex B's `D_j`

- Where: design §7 l.170-171, §9 l.201; `dsr.py:170`, `177-178`; Annex B l.70-71:
  `D_j = (T − 1) · var_b(S*_{b,j})`, `z_j = (S_j − S0) · sqrt(T − 1) / sqrt(D_j)`.
- `dsr._mean_var(...)[1]` is `var_b(S*_j)`. The design names it `D_j` and records it as
  `columns[].D_j`. `evaluate` calls the same number `dispersion` and its comment says the
  factor cancels in z. P18-3 and DESIGN §7.2 use `D` in Annex B's sense. A reader who
  recomputes `z_j` from the recorded `S_j`, `S0`, `T`, `D_j` with Annex B's formula gets
  values that are wrong by a factor `sqrt(T − 1)`.
- Two acceptable forms; pick one and state it: record `var_b` under that name, or record
  `D_j = (T − 1) · var_b` as a stated product. In both, `z_j` must be computed as
  `(S_j − S0) / math.sqrt(var_b)`, the expression in `dsr.py:178`. My run shows that going
  through `(T − 1) · var_b` changes the last bit of `z_j` in about a third of the columns,
  and would break the bit-for-bit check on the nominee.

### R14D6B2-F-7 (major): cause precedence across trials, and one reason with two codes

- Where: design §4 l.112-128; `nominate` `c2_confirmation.py:887-897`; `cause_code`
  l.918-923; `U_OPS_REASONS` l.639-640; Annex A P18-7 ("each failure with one exclusive
  cause code by a fixed precedence: infrastructure or governance cause first").
- Precedence. `nominate` walks the trials in ascending id and returns at the first one that
  fails. Today every such return is U_ops, so order does not matter. With the split:
  trial `a` has a record with `TRIAL_CODE_ERROR` (U_proc), trial `b` is `final` after a
  second crash (U_ops). The family is recorded U_proc, with `a`'s reason. P18-7's fixed
  precedence gives U_ops. The same holds inside one trial (hash mismatch and a recorded
  reason).
- Correction: scan all trials; if any has a U_ops cause, the family is U_ops with the
  first such trial's reason; otherwise U_proc with the first U_proc reason. One test per
  ordering.
- One list. §4 puts `DAYS_INCOMPLETE` under U_ops. `U_OPS_REASONS` does not contain it, and
  `cause_code` (gates) uses `U_OPS_REASONS`. After `check_confirmation_read` has accepted
  complete hourly bars, `baseline_d`'s `DAYS_INCOMPLETE` (l.1891-1892) cannot come from
  missing data; it would be the run producing too few days, which is closer to a procedure
  failure. Either way, trials and gates must classify from the same set, and a change to
  that set is the owner's binding (the Fable F-5 note "do not change `U_OPS_REASONS`
  without the binding" still applies). The owner's recorded answer on A-3 is "split by
  reason"; it does not list the reasons, so the list in §4 is still a proposal.
- Coverage of reason strings: `RunUnavailable` carries bare codes without ":" (checked in
  `screen.py` and this module), the three exception names are type names, and the
  catch-all sends unknown reasons to U_proc. That is consistent with `cause_code` and I
  found no reason string left out.

### R14D6B2-F-8 (major): two governance points the design should flag

- Where: design §7 l.177-179; `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md` last paragraph;
  `ADJUDICATION_FABLE_SLICE6_3765910.md` ("if `calibration/c2_confirmation.py` is a
  protected component"); DRAFT_WORDING R-14a items 1, 4, 5; Constitution §16 (enumerated:
  validation engine, promotion gate, ...); DESIGN §3 (b) ("reviewed under §16").
- §16. R-14a item 1, an owner decision carried in the S4 draft, reads: "Each is one file,
  merged under Constitution §16 review, with an independent different-model review record
  and human PR review before merge." The module also holds the G-1..G-14 pass decisions,
  which is the "promotion gate" of §16's list. So the question recorded as "not decided" is
  already answered by the project's own text: every 6b change to this file needs the
  different-model review and the owner's PR review before merge. The design should say so
  instead of leaving an "if". This is a flag for the owner, not something a reviewer or
  the author can settle or waive.
- Option (b) and R-14a item 4: "Where an engine-commit ... function implements a rule, the
  module calls it and does not re-implement it." `dsr.evaluate` implements S0, the
  dispersion and z. Option (b) calls `evaluate` for every decision, and then composes S0,
  the dispersion and `z_j` again in the module from `evaluate`'s helpers, for reporting.
  That is defensible, and the helpers are inside R-8 ("`calibration/dsr.py` `evaluate` and
  the functions it calls"). But it is a second composition of a bound rule inside the
  module, which item 4 speaks to and item 5 requires to be listed in the module's contract.
  The owner chose (b) on the argument "no §16 review for `dsr.py`"; the R-14a item 4
  question was not put to him. Proposal: state in §7 that the recomputed columns are
  report-only, that no gate, nomination or sealing input reads them (G-9 reads
  `nomination.z` only), add them to the §7.2 output-field contract, and put the item 4
  reading in front of the owner with the A-7 contract.
- Also for the record: rev 2 changes reviewed code paths (`family_attempts`, `nominate`,
  `completed_entry`, the trial record schema, possibly `U_OPS_REASONS`). Each is a change
  to code earlier slices reviewed, so the earlier acceptances do not carry over.

### R14D6B2-F-9 (major): `cycle_start` has no source

- Where: design §2 table l.33-44; `look_allowed(states, cycle_start, now, ...)`
  `c2_confirmation.py:827`; DESIGN §2 P18-2 ("day 180 (from the recorded cycle start)").
- The table lists `now` but not `cycle_start`. A caller who supplies a `cycle_start` 180
  days back gets a look while trials are still running. That family is then recorded
  U_ops, which is conservative for it, but the other family is evaluated and the cycle's
  one look is used on the caller's say. Under rev 2's own rule this value needs a governing
  record: a declaration field, or the acceptance record's block, is an owner binding.
  Add it to the table and to the owner items.

### R14D6B2-F-10 (major): the evaluation record omits the Task 12 result

- Where: design §9 l.197-203; `Nomination.task12` `c2_confirmation.py:848`, `900`; Annex A
  A-V1 ("computes its result with V, and also computes and reports the Task 12 numerics;
  if the decisions differ, V's result governs and the difference is disclosed").
- `families.f.dsr` has `{block, S0, columns, T}` from V only. Add the Task 12 `reason`,
  `nominee`, `z`, `S0` and a `decision_differs` field (nominee or G-9 result differ). This
  is an output field of a frozen-text rule, so it belongs in A-7's contract.

### R14D6B2-F-11 (minor): compare every identity field the record carries

- Where: design §3 l.96-104.
- The look compares `configuration_hash`, `estimator_seed`, `data_manifest_sha256` and
  `window_id` with its own values. The record also carries `seed_l266`, `trial_index`,
  `protocol_hash`, `engine_commit`, `confirmation_module_sha256`, `image_digest`, `family`,
  `days`. A record written by a process started under another module build passes. The
  look has every one of these values (`Started`, `derive_seeds`, the window); require
  equality for all of them. This is what F-4 (2) asked for.

### R14D6B2-F-12 (minor): what `drand_chain_hash` is a hash of

- Where: design §6 l.150.
- I could not check drand's definition (no network). From memory, the chain-info hash
  covers the period, the genesis time, the public key, the genesis seed (group hash), and
  for non-default chains the beacon id (and in later versions the scheme). The row list has
  no genesis seed and no beacon id. If that is right, the module cannot recompute the hash
  from the rows. Before building: pin the exact byte layout from the drand source at a
  stated version, add the missing rows, and carry a known-answer test against quicknet's
  published hash (`52db9ba7...c84e971`, `DESIGN_SEED_VERIFIER.md:109`). If the layout
  cannot be pinned, say that the chain hash row is recorded and matched to the relay path
  but not recomputed.

### R14D6B2-F-13 (minor): the capture record has no stated check

- Where: design §6 l.159-161; `ACCEPTANCE_FIELDS` `c2_confirmation.py:2451-2454`,
  `check_acceptance` l.2471-2476 (exact field set); O-6a SPEC §5 (the record holds the
  capture evidence at the freeze point).
- The acceptance record `start` verifies cannot hold `T`: its field set is exact. So the
  capture time comes from another object. "Never from the caller" then needs a check:
  for example the capture record names the acceptance record's hash and tip block hash and
  its own hash is logged, or the acceptance schema (a DESIGN schema, not frozen) gains the
  capture fields. As written, S-8's second half is deferred, not answered. The provenance
  of the acceptance record itself is still the open item R14L2-S-2.

### R14D6B2-F-14 (minor): `now` is a recorded claim

- Where: design §2 l.42; `ledger.py:20-24`, `111-123`, `append_entry(recorded_at_utc=...)`.
- The ledger says timestamps carry no ordering authority and accepts any caller-supplied
  time. Reading `now` from an entry makes it durable and reviewable, which is better than
  a bare argument, but it is not verified. Write "recorded, not verified". A real lower
  bound on time is available if wanted: a drand beacon of a round scheduled at or after
  day 180, checked with the module's own `bls_verify`, proves the day has come. That is
  optional hardening and an owner choice.

### R14D6B2-F-15 (minor): one source per value, exact parses

- `data_manifest_sha256` "if bound in C2; else declaration" (§2 l.40, §6 l.157): fix one
  source in the S4 text, or require equality when both exist. Same pattern as S-9.
- `drand_genesis_time`, `drand_period`, `t_min`, `g_days`, `confirmation_start`,
  `confirmation_end` arrive as quoted strings. State the exact form (canonical decimal
  without sign or leading zeros; the `_time` round trip for instants). `int(" 30 ")` and
  `float("nan")` (`g9` l.332) must not be reachable.
- `z_crit` and `family_block_rule`: see F-1 (equal to the qualification object's values).

### R14D6B2-F-16 (minor): read the ledger once

- `read_entries(path)` alone verifies the chain and raises on damage; the head is
  `entries[-1].entry_hash` and the count `len(entries)`. Calling `verify_ledger` first
  reads the file a second time, and an append in between makes the recorded
  `{head_hash, entry_count}` describe a different state from the entries used.

### R14D6B2-F-17 (minor): unnamed contract changes

- `family_attempts` returns `{trial_id, outcome, reason_code, start, end}` (l.765-767); the
  §3 matching needs `attempt_id`.
- `completed_entry` returns `(hash, days, [])` for an unavailable run (l.2886); `nominate`
  cannot see the reason. Say how it arrives (a fourth element or a separate mapping) and
  keep `MISALIGNED_SERIES` for a real day mismatch.
- `nominate`'s `ops()` builds U_ops only (l.887-888); the U_proc return before
  `dsr.evaluate` is new.

### R14D6B2-F-18 (minor): who records "no pick"

- DESIGN §2: on a pre-pick termination "the module refuses the look and records 'no pick'".
  Design §10: a failure in steps 2-6 leaves no record. `look_allowed` raises. State that
  the cycle-outcome record is the store's, or have the module return a no-pick record.

### R14D6B2-F-19 (info): option (b)

- Bit-for-bit. In one process, with the same `x` (use `nomination.x`, not a rebuilt
  array), the same seed and `result.block`, the recomputation follows `evaluate`'s default
  path line for line (`dsr.py:157-178`). `fast.column_lengths` is not involved because
  `result.block` is reused. My synthetic run agreed in all six cases. I could not run it
  on the pinned runtime; the design's test on the DSR fixtures covers that there.
- Binding. `indices`, `_replicates_v`, `_sharpe_exact`, `_mean_var` are functions
  `evaluate` calls, so R-8 binds them at the engine commit. Calling private names does not
  weaken the frozen-code argument; a change to them changes the engine commit.
- Tightenings: also check the recomputed argmax (highest `S_j`, lowest index on ties)
  equals `result.nominee`; state that a mismatch is treated as the A-V1 "runtime cannot be
  recreated" case and that it happens after the read (so F-2's rule decides what it costs);
  state that `_replicates_v` returning `None` on the recomputation is also a mismatch.

## Answers to the review questions

1. **S-1..S-9, F-3/F-4/F-5.** S-4, S-7 answered. S-6 answered apart from F-6. S-2 and F-3
   answered in direction; open cases in F-3 (this review) and F-4. S-1: `cycle_start`
   (F-9), the bounds document (F-1) and the capture record (F-13) are still caller or
   store values with a better source or no stated check. S-3: not implementable as written
   (F-5). S-5: not fully answered (F-1). S-8: chain hash added but its inputs are
   incomplete (F-12); capture deferred (F-13). S-9: recorded as an S4 condition, which is
   all the module can do. Fable F-4: fields added; comparison incomplete (F-11). Fable F-5:
   answered by the owner's choice; precedence and the list are open (F-7).
2. **Ledger binding.** Swap and replay inside one intact ledger are closed by the
   `record_sha256` and identity checks. Forgery and omission by rewriting the suffix are
   not (F-4). "Between start and outcome" is checkable with the positions, given
   `attempt_id` (F-17); outcome-before-entry and entry-after-crash are undefined and one of
   them ends the cycle silently (F-3). The anchor does not prevent a fork or truncation
   after it (F-4). `now` from a look record is not sound as a clock and the look record
   itself is undefined (F-2, F-14).
3. **Option (b).** Holds (F-19); `D_j` is mislabelled (F-6); item 4 flag (F-8).
4. **Manifest.** F-5.
5. **Classifier.** `for_k` usage is right; `pooled` should not be called at all; the
   `z_crit`/T checks become well defined once the source is the object (F-1).
6. **Cause split.** Consistent with P18-7's definitions; precedence and the single list
   are not (F-7); `nominate`'s contracts need the named changes (F-17).
7. **Order and failure.** No read precedes the checks in steps 1-6. The pre-look records
   (confirmation-derived) are parsed at step 4, before `look_allowed`; nothing is output,
   so I raise no finding. No path writes a record after an invalid step, provided the
   three outputs are returned together at the end; the design should say that. The
   post-read aborts are F-2.
8. **Amendments and §16.** No frozen artifact needs editing for rev 2. New signed rows and
   the output contract go into the unsigned S4 text (owner). §16 and R-14a item 4: F-8.

## What holds

- The rule "handles to governing records, never values" and the step order of §2.
- Declared trials from the verified declaration, as `_check_declared` does; trial objects
  are bound by `screen.trial_sha256` in `_check_records`.
- `record_sha256 = SHA256(cj(record))` as the record's one identity, with `d_sha256` kept
  for A7 step 2.
- `append_entry` for the entry: it verifies the whole chain under the lock.
- `v_runtime_check` runs inside `start` (`verify_code` → `mapping.check_runtime`), so
  method V is verified before `nominate` and before option (b).
- The two-record boundary of §9 and its non-circular hash.
- Seed failures stay read-free (step 3 before step 7).
- A new record type in the attempt ledger does not disturb `attempt_counts`, which reads
  started records only.

## What I could not check

- drand's chain-hash layout (no network; F-12 is from memory and marked so).
- Option (b) on the pinned Linux image; only the local Windows runtime with
  `_V_VERIFIED` set by hand.
- The real declaration layout, the store, the launch route and the signed C2: none exists
  yet. Findings about them are against the design text only.
- `calibration/screen.py` beyond the lines cited; `calibration/fast.py`; the full
  Annex C and Annex D texts; the remaining 7 `RunUnavailable` sites that the search tool
  truncated (the 33 I saw are bare codes).
- I did not re-review slices 1-6a code; I read it only to check the design against it.
