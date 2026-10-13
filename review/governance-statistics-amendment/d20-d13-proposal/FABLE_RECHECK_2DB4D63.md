# Fable re-check of the D-20 (rest) and D-13 proposal, revision 2, at 2db4d63

- Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), run as a read-only subagent of this Claude Code session; the model line below is the reviewer's own statement
- Date: 2026-10-13
- Reviewed: revision 2, the adjudication `ADJUDICATION_37F20C8.md`, both rev 1 reviews and supporting code (packet), plus repository files it read itself
- Findings: DF2-R1, DF2-R2 (blocking); DF2-R3..DF2-R8 (notes). Partial adjudications DC-R5 and DC-R6 judged correct. Verdicts: Q1-Q4 READY WITH FIXES ((b) still recommended for Q3).
- The reviewer's final report follows verbatim.

---

Model: Claude Fable 5.1 (claude-fable-5-1)

# Re-check of the D-20/D-13 proposal rev 2 at 2db4d63

This was a read-only review. I edited nothing and ran no git command that writes. HEAD is 2db4d63. I checked the proposal against these files:
- `calibration/{dsr,gates,rundef,mapping,qobj,seeds}.py`
- `src/aqt/metrics/statistics.py`, `descriptive.py`, `benchmarks/canonical.py`, `core/preregistration.py`
- `deploy/calibration/requirements.lock`, `pyproject.toml`
- `protocols/protocol_v1.yaml` (l.66, 153–175, 215–222, 266)
- the S4 draft (DRAFT_WORDING, Annexes A, B and C)
- the D-19 prereg §7.2 and §8

## 1. My rev 1 findings: are they repaired?

| ID | Repaired? | Notes |
|---|---|---|
| DF-R1 | Yes | M12 added. G-9 is bound to `dsr.evaluate`, which defaults to `numerics="v"`. |
| DF-R2 | Yes | `seed_material` and `trial_seed` exist (domain `aqt.trial_seed.v1`). The new code's home is `screen.py`, which is in `qobj.LATER` and `REVIEWED`. |
| DF-R3 | Yes | — |
| DF-R4 | Yes | — |
| DF-R5 | Yes, with a defect | See DF2-R3. |
| DF-R6 | Partly | See DF2-R2. |
| DF-R7, DF-R8, DF-R9 | Yes | — |
| DF-R10 | Yes | — |
| DF-R11 | Yes, with a small inconsistency | See DF2-R4. |
| DF-R12 | Yes | Moving the mapping into `screen.py` before the freeze is stronger than the conditions I asked for. |
| DF-R13 | Yes | — |
| DF-R14 | Yes | `check_engine` (mapping.py:97) and `loaded_outside` (rundef.py:185) exist as cited. |

I also confirmed that every routine in the §1 table exists at the cited files.

**DC-R5 (accepted in part): the adjudication is right.**
- I checked each cited clause against the decided text:
  - P18-1 freezes `J_f`, and "No trial may be added, removed or replaced later".
  - Trial ids are in the Annex B family seed, which the post commits.
  - The round comes from the capture time plus 24h, so it is not yet published when the capture is taken.
  - P18-3 means a missing or crashed trial fails `A_f` for the whole family. A post-beacon selective withdrawal is therefore impossible.
  - The automatic re-run uses the l.266 seed and is mechanical.
- No new rule is needed. One route is not zero, though: see DF2-R6.

**DC-R6 (accepted in part): the calibration argument holds, but needs two qualifiers (DF2-R6).**
- I verified the model it relies on. In the D-19 engine, G-1 availability is computed with a `ReplicateStream` keyed by `sha({"seed": outer, "stream": "g1_ci"})` (gates.py; prereg §8). That seed is fixed in advance and does not depend on the data.
- Option (b)'s seed is a hash of verified drand randomness and the committed declaration. It is independent of the data law, so the certified G-1 availability rate transfers at least as well as under (a).
- G-9 already uses the beacon seed under R-7, so it is unchanged.

## 2. New findings

**DF2-R1 (blocking, §1 table and M12): the Annex B replicate-seed binding contradicts the code. It also leaves an Annex B obligation silently open.**
- Evidence:
  - The §1 table binds "Annex B replicate seeds" to `statistics.replicate_seed_material` and `replicate_seed`. Those take a `ReplicateStream`, which refuses any purpose other than `"paired_sharpe_ci"` (statistics.py:465–467).
  - The real G-9 path, `dsr.evaluate` → `dsr.indices` → `dsr._replicate_seed` (dsr.py:57–81), re-implements the layout inline with purpose `dsr_family_max_null`.
  - Annex B §2.4 (l.110–113) still says the build "would extend the conventions (IMPLEMENTATION_CONVENTIONS.md), the stream, and regenerate and review reference vectors (I-10)". The proposal neither does this nor supersedes it. §2.4 `added_purposes` lists `dsr_family_max_null`, but M7 cites only the G-11 purposes.
  - dsr.py:42 hard-codes `WINDOW = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'`. In C2, `w0 = 2022-01-01 + gap_embargo.value_days` (DRAFT l.180, C-0), and that is at least 1 day. So the bound G-9 seed's window field never equals the C-0 window, which §3 uses for the null streams and C2's G-1 stream would use.
- Scenario: the implementer has three instructions that disagree: the table, Annex B §2.4 and the frozen dsr.py. Two outcomes are possible:
  - C2 passes the real window, which changes a bound routine and trips the §1 falsifier.
  - C2 keeps the constant, which contradicts "the existing replicate-seed construction" over the stream's window.
- Repair:
  - Remove "Annex B replicate seeds" from the statistics.py row.
  - State that the G-9 seed and indices are `dsr._replicate_seed` and `dsr.indices` as frozen, including the window constant, which is a fixed domain label and not the C-0 window.
  - State that this supersedes Annex B §2.4's "extend the stream / regenerate I-10 vectors" sentence. The D-19 reference-vector suite, which runs `dsr.evaluate` with `numerics="v"`, serves as the I-10 vectors.
  - Add `dsr_family_max_null` to the `added_purposes` closure.

**DF2-R2 (blocking, §3 runtime, Q2): scikit-learn is no more in a pinned runtime than LightGBM is. The runtime for the G-14 refits is not bound to any record or freeze point.**
- Evidence:
  - `deploy/calibration/requirements.lock` pins only numpy. No repository manifest names scikit-learn or LightGBM (`pyproject.toml` has none; the only mention is `review/task1/authorized-spec.txt`).
  - `requirements.lock` and `Dockerfile` are ENGINE files frozen in the qualification object (qobj.py:49–55).
  - `dsr.runtime_identity` hashes only the interpreter and the NumPy/BLAS binaries.
  - Prereg §7.2 runs 500 G-14 refits per trial and path inside the screen, before the declaration, using frozen `screen.py`.
- Scenario:
  - As written, no model-fitting trial (G-14 mandatory) has a recorded runtime, so the screen cannot run it, or runs it on an unrecorded one.
  - "Until a runtime with it is recorded and reviewed" implies a library can be added later. That would change the object's runtime after the freeze, which means requalification.
- Repair: state the following.
  - The model-library runtime (scikit-learn and LightGBM versions and binary hashes, in the object's image) is recorded in the qualification object before the freeze, under the same `v_runtime_check`-style identity.
  - A model class whose library is absent from that recorded runtime cannot be declared for any cycle under that object. There is no later addition without a new object.
  - The text should name scikit-learn as well as LightGBM.

**DF2-R3 (note, §3 B4): the "linear" class cannot take `random_state`.**
- If "linear" means scikit-learn `LinearRegression`, that class has no `random_state` parameter, so passing it raises a `TypeError`.
- Repair: say "to every class whose constructor accepts `random_state`". Map each protocol class name (linear, ridge, lasso, elastic_net, logistic) to its exact scikit-learn class in `screen.py`.

**DF2-R4 (note, §2 B2): two follow-ons.**
- The same `||` formula also appears in `seed_disclosure.derivation` (DRAFT l.157). The amendment must replace it there too, not only in R-7.
- "`round`: a positive integer" is right for drand. But the engine's synthetic calls use `round = rep`, which is 0-based (prereg §8), and the reference vectors use `rep = 0`. Say the validation applies to the C2 builder, and that the shared `calibration.seeds.sha` step does not validate.

**DF2-R5 (note, B6): B6 is sound, but it extends accepted prereg §7.2, and the screen's window id is undefined.**
- Prereg §7.2 fixes only the screen seed. B6 adds sub-derivations, and that should be recorded as a clarification of the accepted prereg, not only as D-20.
- In the screen, §3's `evaluation_window_id` field has no defined value, because the paths are simulated.
- How the screen's bootstrap and sign streams derive from `screen_seed` is also unstated (prereg §8 lists only the calibration stream names). The frozen `screen.py` fixes it de facto. Either bind it or state that the code is the binding.
- Grinding the trial set to pass the screen is possible, because the seed has no nonce. That is pre-existing, and it only weakens the screen's power claim.

**DF2-R6 (note, §4 "Why no new route opens" and the calibration argument): "the declarer cannot choose" the seed should read "can re-draw it only at the cost of one `m` per draw".**
- After the beacon, a declarer with offline window access can compute G-1, G-11 and G-14 under the beacon seeds. If they look unfavourable, a second post from A invalidates the cycle. That costs one `m`, the window stays eligible under O-9 (a), and the declarer re-declares.
- This is the FA5-3 residual, already disclosed in DRAFT l.170. It is dominated by (a)'s free offline search, so (b) is still strictly better. But the surviving seed is then selected conditional on the data, at a charged price, so the calibration paragraph should say this.
- It should also say that G-11 and G-14 have no certified rate (prereg l.61, screened gates), so the calibration argument matters only for G-1.

**DF2-R7 (note, §1 "the calibration already uses this code"): this slightly overstates it.**
- `gates.g1` by default (reference=False, which is also the path the reference vectors take) calls the production `bootstrap_indices`, `block_length` and the influence routine. It recomputes the replicate Sharpes through `calibration.fast`, and checks availability only.
- So the D-19 vectors do not exercise `paired_sharpe_improvement_interval`, `_sharpe` or `type_seven_quantile`. Its availability semantics do match: any invalid replicate gives `INVALID_REPLICATE`.
- The acceptance condition therefore rests on the Task 12 tests for the interval itself. Say so.

**DF2-R8 (note, §6): the CPCV path assembly and the per-path routine are still unspecified.**
- Sol's DC-R10 named "exact path aggregation", and rev 2 fixed only the quantile and unavailability rules.
- Repair: name the split-to-path assignment (which test group of which split forms each of the 7 paths), and the routine for each path's `E-IMPROV` and `E-DIFF` (`paired_sharpe_statistics`).
- It is diagnostic only, so this is a note.

## 3. Markers still silently open

I mapped every `<<OPEN D-20>>` and `<<OPEN D-13>>` marker:
- Annex C l.53, 56, 81, 149, 272, 291, 334 and 352;
- DRAFT R-8, l.157, l.287 (G-1), l.295 (G-9), l.297 (G-11), l.300 (G-14), and the l.330 and l.333 rows.

Each maps to M1–M12. The only silently open item is the Annex B §2.4 stream-extension and I-10 obligation, together with the `dsr_family_max_null` entry in §2.4 `added_purposes` (DF2-R1). Nothing is marked there, but the item is unresolved.

## 4. Verdicts

1. **Code bindings (§1, §2): READY WITH FIXES.** DF2-R1 is blocking and is a scoping repair of a few sentences. DF2-R4 and DF2-R7 are wording fixes.
2. **Null-test streams and `s_inputs` (§3, §5): READY WITH FIXES.** DF2-R2 is blocking and must say where the model-library runtime is recorded, and that it is recorded before the freeze. DF2-R3 and DF2-R5 are notes. The stream maths, B6 and moving `s_inputs` into `screen.py` are sound.
3. **Seed source in C2 (§4): READY WITH FIXES, (b) still recommended.** The DC-R5 and DC-R6 partial adjudications are correct. The calibration argument holds once DF2-R6's two qualifiers are added: re-drawing costs one `m`, and only G-1 carries a certified rate.
4. **D-13 (§6): READY WITH FIXES.** Specify the path assembly (DF2-R8). The STAT acceptance is recorded as absent.

## 5. What I could not check

- LightGBM and scikit-learn behaviour: neither is installed. DF2-R3 relies on the documented `LinearRegression` signature.
- The O-6a SPEC §3–§7 capture and round mechanics beyond the quoted text, and the Constitution v1.1 §9 meaning of `m`.
- The Task 12 test suite and whether it passes at any commit. I ran no tests.
- The D-13 matrix row's exact option wording, and the full IMPLEMENTATION_CONVENTIONS.md.
- Whether an owner decision record already supersedes Annex B §2.4 l.110–113 outside the S4 draft.
