# §16 different-model review: the D-19 held-out runner

You are an independent adversarial reviewer (read-only). You are not an
authority and you cannot approve a merge; the owner's PR review is separate.

## What to review

`git diff main...d19-heldout`: the new `scripts/d19_heldout.py` and
`tests/unit/test_calibration_heldout.py`. It is the held-out runner that the
qualification object lists as `heldout.py` (`calibration/qobj.py` `LATER`,
`REVIEWED`), built before the freeze under the owner's build-order decision
(`review/d19-engine/OWNER_DECISION_BUILD_ORDER.md`).

Governing text, in
`review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`:
§4 (object, freeze order steps 5-7), §6 (held-out tests, bounds, N), §8 (seeds: namespaces, held-out anchor, streams, family seed),
§3.5 item 3 (frozen final thresholds), and §13 rev 7g items 3 (20k/40k) and 6
(chunks, binding to `qualification_object_sha256`, start checks, P18-6
held-out visibility).

Code it reuses, already reviewed: `scripts/d19_run.py` (`_family_record`,
`dev_replication`, the worker pool), `scripts/d19_choose.py` (`development`),
`calibration/choices.py` (`consistent`, `_passes`, `_either`, `_unavailable`,
`test_manifest`, `BOUNDS`), `calibration/chunks.py`, `calibration/binomial.py`,
`calibration/mapping.py` (`check_engine`, `check_runtime`, MP-4),
`calibration/qobj.py` (what the object holds: `choices.json`,
`definition.json`, `freeze.json` with `allocation`, `mapping.py`,
`heldout.py`).

## The runner's proposed readings (HO-1..HO-4, in its docstring)

Accept, reject or amend each.

## Questions

1. Seeds: does every held-out replication use exactly §8's outer seed
   (namespace `d19-heldout-v{n}`, the held-out anchor) with the family seed
   unchanged from development? Could any path mix anchors within a chain
   (HO-3)?
2. Record and reduction: is reusing the development record (both block
   rules) with the frozen final thresholds correct for §6's tests, and does
   `certify` read the frozen `family_block_rule` and `z_crit` with the same
   predicates development used? Is each test's event definition right,
   including the QJ joint tests?
3. Bounds: one-sided Clopper-Pearson at alpha = 0.025/M with M = the
   object's full test manifest (HO-2). Is that the right M? Are tests of
   demoted cells correctly left uncertified?
4. Code identity (HO-1): can a different engine module, driver, mapping or
   runner compute or reduce held-out chunks without refusal? Does the import
   order keep `rundef.bytecode_problem` meaningful? Do spawned workers run
   their own gate?
5. P18-6: can `run` display, export or aggregate any held-out event content
   before `certify`? Does `certify` verify every chain before reading any
   result?
6. Anything else that would make a certification wrong, irreproducible, or
   accepted when it should fail.

## Output

Stable IDs `HO-R1`, `HO-R2`, ... each marked blocking or note, with
file/line, the triggering scenario, evidence and a minimal repair; a table
deciding HO-1..HO-4; then a verdict: ACCEPT or CHANGES REQUESTED. Say what
you could not check. Make no edits.
