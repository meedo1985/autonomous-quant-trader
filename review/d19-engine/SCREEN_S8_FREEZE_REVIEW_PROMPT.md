# Review prompt: screen S8 freezes the `paths` reference vector at 5e24942

You are an independent adversarial reviewer working read-only, not an authority. This is the Constitution §16 different-model review of the screen PR's delta since your accepted re-review 4 (`4fed8f5`). The only code change is `f475f46`: `FROZEN_REFERENCE_VECTORS["paths"]` in `calibration/screen.py` goes from `None` to the value the third server pilot printed. The other commits are records.

Attached are:
- the diff `4fed8f5..5e24942` for `calibration/` and `tests/`;
- the pilot evidence record (step C holds the value and the runtime line);
- the local gate record;
- the owner's feasibility decision;
- `declare`, `run_screen`'s return value and `screen_reference_vectors` from `calibration/screen.py`;
- the head of `scripts/d19_screen.py`.

Check:
1. Is the frozen value the one the pinned image computed, under the pinned runtime, for the code that `declare` will run? Is the provenance chain in the evidence complete?
2. Does any path let `declare` accept vectors that differ from the frozen ones, or skip the check?
3. Does the test change keep the `not frozen yet` refusal tested without weakening any other assertion?
4. Does the feasibility decision record state anything that the evidence does not support?

Keep to findings that would let a wrong reference vector pass, or that misstate the evidence. Verdict ACCEPT or FIX. Give findings stable IDs S8F-n.
