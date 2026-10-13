# Fable narrow re-check of the D-20 (rest) and D-13 proposal, revision 4, at 4645e0a

- Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), run as a read-only subagent of this Claude Code session; the model line below is the reviewer's own statement
- Date: 2026-10-13
- Reviewed: both rev 3 re-check records, `ADJUDICATION_DBA31FB.md`, the diff rev 3 -> rev 4 and the full rev 4 (packet), plus repository files it read itself
- Findings: DF4-R1..DF4-R3 (notes; DF4-R3's wording fix needed before adoption). Verdicts: Q1 READY, Q2 READY, Q2b READY WITH FIXES ((a) recommended), Q3 READY WITH FIXES ((b) recommended), Q4 READY.
- The reviewer's final report follows verbatim.

---

Model: Claude Fable 5.1 (claude-fable-5-1)

# Narrow re-check of the D-20/D-13 proposal rev 4 at 4645e0a

This check was read-only: I edited, created and committed nothing. HEAD is 4645e0a. Between dba31fb and 4645e0a the diff touches only PROPOSAL.md, plus the two re-check records and the adjudication. To check the claims I read:
- `calibration/qobj.py` (ENGINE, LATER, REVIEWED);
- `calibration/mapping.py` `check_engine`;
- `calibration/rundef.py` (`is_code`, `loaded_outside`, `run_plan`, gating);
- `calibration/dsr.py` `runtime_identity`;
- `deploy/calibration/Dockerfile` and `PILOT_FE7.md`;
- prereg l.530–542 and the re-pilot lines;
- Annex C C-10 and C-13;
- DRAFT l.85 and l.159.

## 1. Are the rev 3 findings repaired, and is the adjudication right?

| ID | Repaired? | Evidence |
|---|---|---|
| DF3-R1 / DC3-R1 | Yes | The two checks are now disjoint. `qobj.LATER` does hold `mapping.py`, `screen.py` and `heldout.py` (= `scripts/d19_heldout.py`), and REVIEWED lists those three. Replacing the engine entry matches `check_engine` l.116 (`inventory[SELF] = ...`). The entry-point case is covered. Q1 names the object-bytes binding. One gap the new wording exposes: DF4-R1. |
| DC3-R2 / DF3-R2 / DF3-R3 | Yes | (1) The libraries are bound through the image digest. Prereg l.532 puts the digest in the gating identity, and l.536 requires the same image. (2) No new identity is added. (3) The OpenBLAS side effect is stated correctly: `core.parent.rglob("*openblas*")`, where `core.parent` is site-packages. (4) Byte-identical canary and reference-vector outputs are required. (5) Transitive pins, the NumPy 2.5.3 resolution and `libgomp1` are listed. Open: re-pilot carry-over (DF4-R2). |
| DC3-R3 | Mostly | The per-attempt `U_G` claim and the `2p − p²` example are correct. Selection away from a no-result outcome is conservative for an unavailability bound, so that holds. The new statement that `m` is "a correction" needs a qualifier (DF4-R3). |
| DF3-R4 | Yes | The wording is as I asked. |
| DC3-R4 | Yes | Verified: for `p` in 1..7, `g ↦ g XOR p` is a fixed-point-free involution, so it gives a perfect matching. Each split `{a, b}` lies in exactly one path, `p = a XOR b`, which is never 0. The 28 splits are therefore each used once, and both test groups of a split share a path. The path 1 example is correct. |
| DF3-R5 | Yes | The flat start matches C-10 (4) (exposure 0, no pending order, unset clock, fresh overlay). The benchmark is the window's series, sliced by group. |

**The adjudication's correction on `m`: right in part.**
- **What holds.** The halving allowance does act as a union bound across attempts. P(some attempt falsely promotes) ≤ Σ 0.05/2^(m−1) < 0.10. Adaptive stopping does not break this, because invalidated attempts promote nothing.
- **What it needs.** The bound requires each attempt's test to be valid at its own allowance. That requires each attempt's declaration to be independent of the window's data. See DF4-R3.

## 2. New findings

**DF4-R1 (note; §1 "Two bindings"). The C2 evaluator's own code fits neither binding, so the rule implicitly forces it into the engine commit.**
- The rule as written:
  - check 1 makes every loaded `calibration` or `aqt` module that is not an object file equal the engine commit's file;
  - `rundef.loaded_outside` refuses any unhashed module inside the root, and any `aqt` or `calibration` module from elsewhere;
  - `is_code` admits only `calibration/*.py`, `src/aqt/**` and `scripts/d19_*.py`;
  - `qobj.LATER` is itself fixed in the engine commit.
- The consequence: the C2 evaluation code does not exist yet. That code holds the B2 input validation, §4 (b)'s `trial_seed_j`, the §6 path assembly, and the C2 entry point. It can load only if it is already in the engine commit, which means written before the full run starts, or if it lives in an object file such as `screen.py`.
- **Repair (one sentence):** "The C2 evaluation's own code must be in the engine commit or in an object file (for example `screen.py`); no third location can load under these checks."
- Without that sentence, the owner is not told that the build order is constrained.

**DF4-R2 (note; §3a (a)). The rebuilt image does not say what happens to the FE-7 re-pilot and the go-ahead.**
- The re-pilot ran on the current image. It measured `U_G` and DSR-availability rates in the thin categories, the run's cost, and the interrupt/resume byte-identity (prereg l.493, 515, 565–579). The go-ahead estimate uses those measurements.
- `rundef.run_plan` records "the image, re-pilot and go-ahead are done (FE-4, FE-7)".
- Rev 4 says only that no earlier qualification carries over. The re-pilot is not a qualification ("qualifies nothing"), so the text says nothing about it.
- **Repair:** state either:
  - that the re-pilot results and the go-ahead carry over on the strength of the proven-identical canary and reference-vector outputs (the engine imports none of the new libraries); or
  - that the CPU probe, the resume test and any part of the re-pilot are redone on the rebuilt image.
- Also note that FE-4's "image done" status reopens.

**DF4-R3 (note, but the wording fix is needed before adoption; §4 retry paragraph and the "false-promotion" bullet). "The total over all attempts stays below 0.10" is stated without its condition.**
- **Where the bound holds:** a re-declaration whose trial set does not depend on the window's data, including what earlier attempts revealed.
- **Where it fails:** §4 itself keeps open "a search over the strategy itself by a declarer with offline access". A declarer who sees attempt 1's results on the same eligible window (the window stays eligible, O-9 (a)) and re-declares an adapted trial set has a test that is not valid at the attempt's allowance. No allowance corrects that.
- **Repair:** "a correction under the allowance rule's own assumption, that each attempt's declaration is fixed independently of the window's outcome; a re-declaration adapted to earlier results on the same window is the disclosed open route (DF-R10), which the allowance does not correct."
- **Also stale:** "(b) meets it, except for the priced retries above". Under the new per-attempt claim, (b) meets the transfer assumption for every attempt. Retries affect only uncertified pass frequencies over retained cycles. Reword to match.

Nothing else in the diff is wrong. M13, B6, the `U_G` conservativeness argument and the D-13 assembly all hold.

## 3. Verdicts

1. **Code bindings (§1, §2): READY.** DF4-R1 is a one-sentence note.
2. **Null-test streams and `s_inputs` (§3, §5): READY.**
   - 2b. **Model libraries (§3a): READY WITH FIXES**, (a) still recommended. Apply DF4-R2.
3. **Seed source in C2 (§4): READY WITH FIXES**, (b) still recommended. Apply DF4-R3's qualifier.
4. **D-13 (§6): READY.**

## 4. What I could not check

- **Library packaging.** Whether scikit-learn, LightGBM and SciPy wheels exist for CPython 3.14 and resolve against `numpy==2.5.3`. Whether `python:3.14-slim` lacks `libgomp1`. Whether the libraries' seed behaviour matches §3. None of them is installed.
- **Unproven outputs.** That the canary and reference-vector outputs really are byte-identical on a rebuilt image. That remains a claim the image PR must prove.
- **Re-pilot evidence.** Whether the FE-7 re-pilot results or the go-ahead are recorded in a way tied to the current image digest. I read only the code comment and the command sheet.
- **Review status.** Whether `dsr.py` received the owner's §16 PR review (carried over from my rev 3 check).
- **No tests were run.** The XOR path property was checked by reasoning, not by execution.
