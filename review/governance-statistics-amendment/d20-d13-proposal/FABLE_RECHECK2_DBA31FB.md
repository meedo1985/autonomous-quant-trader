# Fable narrow re-check of the D-20 (rest) and D-13 proposal, revision 3, at dba31fb

- Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), run as a read-only subagent of this Claude Code session; the model line below is the reviewer's own statement
- Date: 2026-10-13
- Reviewed: both rev 2 re-check records, `ADJUDICATION_2DB4D63.md`, the diff rev 2 -> rev 3 and the full rev 3 (packet), plus repository files it read itself
- Findings: DF3-R1 (blocking, one-sentence fix); DF3-R2..DF3-R5 (notes). DC2-R4 partial adjudication judged correct. Verdicts: Q1 READY WITH FIXES, Q2 READY, Q2b READY ((a) recommended), Q3 READY ((b) recommended), Q4 READY WITH FIXES.
- The reviewer's final report follows verbatim.

---

Model: Claude Fable 5.1 (claude-fable-5-1)

# Narrow re-check of the D-20/D-13 proposal rev 3 at dba31fb

This was read-only. HEAD is dba31fb. I edited, created and committed nothing. To check the claims I read `calibration/{qobj,mapping,rundef,dsr}.py`, `deploy/calibration/{Dockerfile,requirements.lock,PILOT_FE7.md}`, `protocol_v1.yaml` l.210–224, prereg l.532–541, Annex C C-9, C-11 (5) and C-12 (1), and DRAFT l.159–170.

## 1. Are the rev 2 re-check findings repaired?

| ID | Repaired? | Evidence |
|---|---|---|
| DF2-R1 | Yes | The statistics row no longer claims the Annex B seeds. The G-9 row binds `_replicate_seed` and `indices` and treats `WINDOW` as a domain label. M13 supersedes §2.4, and M7 covers all three purposes. The claim that "the D-19 suite runs `dsr.evaluate`" holds: `rundef._reference_outputs` calls `dsr.evaluate(..., numerics="v")`. |
| DF2-R2 / DC2-R3 | Yes, in substance | §3a forces the choice before the run definition is recorded, and no library can be added later. The `Dockerfile` and `requirements.lock` are both ENGINE object files (qobj.py l.49–55), so the timing is right. See DF3-R2 and DF3-R3 for the parts still missing. |
| DF2-R3 / DC2-R2 | Yes | — |
| DF2-R4 | Yes | — |
| DF2-R5 / DC2-R6 | Yes | — |
| DF2-R6 / DC2-R5 | Yes | "Increments `m`" agrees with DRAFT l.159 `invalidation_after_post`. |
| DF2-R7 | Yes | — |
| DF2-R8 / DC2-R7 | Mostly | See DF3-R5. |
| DC2-R1 | Mostly | The wording is self-contradictory. See DF3-R1. |

**DC2-R4 (accepted in part): the adjudication is right.**
- The certified `U_G` is a joint probability over the data law and a hash seed drawn per replication: prereg §8 keys each replication by `sha({"seed": outer, "stream": "g1_ci"})`.
- If C2's seed is a fresh unpredictable draw independent of the data, it realises that same joint law. So the transfer rests on exactly the random-oracle assumption that the calibration itself already makes. Rev 3 now says so honestly.
- Sol's objection is therefore not specific to (b). Removing "safe fallback" for (a) is correct.
- One wording problem remains: see DF3-R4.

## 2. New findings

**DF3-R1 (blocking, a one-sentence fix; §1 "Two binding times" and owner question 1). The C2 byte check, as written, cannot be satisfied for the object files.**
- The text requires that "every `calibration` and `aqt` module" equal the engine commit's file, and that each object file *also* equal the object's copy.
- `mapping.py` (merged, PR #53) and `scripts/d19_heldout.py` (PR #54) already exist, and `screen.py` will be in `calibration/`. `rundef.is_code` covers `calibration/` and `scripts/d19_*.py`. So these files are either in the engine commit's inventory or absent from it. Either way, an object copy that differs from the engine commit's version, or a file the engine commit lacks, fails the first condition.
- `mapping.check_engine` (mapping.py l.116) resolves this by *overriding*: `inventory[SELF] = reviewed`. The generalisation has to say the same.
- "Code written after the run started" is also wrong. `mapping.py` and the held-out runner were written before any full run. qobj.py's own description is "built before the freeze in a later checkout".
- Owner question 1 says only that the named code binds to the engine commit. It omits the object-bytes binding for `screen.py`.
- **Repair:**
  - "Each loaded module that is not an object file must equal the engine commit's file. Each object file must equal the object's copy, which replaces the engine commit's entry, as in `check_engine`."
  - Re-label the second binding time as "object files (LATER), reviewed separately and frozen at the freeze".
  - Add one clause to question 1.

**DF3-R2 (note; §3a (a), "What does change", second bullet). The added "runtime identity" has no mechanism, and the existing identity changes as a side effect.**
- `dsr.runtime_identity` is engine code. The proposal says "the engine code is not changed", so nothing would record the scikit-learn and LightGBM binary hashes.
- The image digest already gates every byte in the image, including the libraries. The simplest repair is to say the libraries are bound through the image digest, and either drop the extra identity or name where it is computed (for example, `screen.py`).
- Side effect: `runtime_identity` hashes `core.parent.rglob("*openblas*")` (dsr.py l.269), and `core.parent` is the whole site-packages directory. Adding SciPy, which scikit-learn and LightGBM both require, adds SciPy's bundled `libscipy_openblas*.so` to the A-V1 gating identity.
- That is harmless if it happens before the run definition. But "Effect on the engine: None" should read: "its numbers are unchanged; its recorded gating identity changes".

**DF3-R3 (note; §3a (a), "How"). "Pin both" is not enough to build the image.**
- The Dockerfile installs with `--require-hashes --only-binary :all:`. The transitive dependencies (SciPy, joblib, threadpoolctl) must all be hash-pinned.
- LightGBM's Linux wheel needs the system `libgomp1`, which `python:3.14-slim` does not ship, as far as I know. That means an `apt-get` addition, gated only through the image digest.
- The lock must also resolve against `numpy==2.5.3` on CPython 3.14. Otherwise the NumPy pin, and with it method V's identity, moves.
- State all three in the instruction for the §16 image PR.

**DF3-R4 (note; §4 Calibration). "The owner accepts it as such" is written as if it were already decided.**
- An AI proposal should not record the owner's acceptance.
- Reword: "Adopting (b) records the owner's acceptance of this assumption. If the owner does not accept it, neither option transfers the rate."
- The substance is otherwise correct.

**DF3-R5 (note; §6 path assembly). The per-group returns of path-dependent strategies are still unspecified.**
- The split-to-path rule is the standard, valid assignment: each path takes each group exactly once. G-10's remainder rule matches Annex C C-9 (2).
- A test split such as {0, 2} is non-adjacent, and trials carry path state ("own path state" overlay, rebalance band, C-6). A group's daily returns therefore depend on the strategy's state at the group's first day, and this is not stated. Is the split simulated through the training gap, or does each test group start flat?
- Concatenating groups from different splits then gives different path Sharpes under different implementations. That is the reproducibility gap DC2-R7 named.
- The benchmark should also be stated as the window's single benchmark series, sliced by group.
- **Repair:** one sentence fixing the state at each test group's start (for example, flat at its first 00:00 UTC decision) and saying the benchmark is the window's series. This is diagnostic only.

Nothing else new is wrong:
- M13 is accurate.
- §3a (b)'s "G-14 always N/A" matches C-12 (1).
- B6, and the "within one cycle / across attempts" split, are sound.

## 3. Verdicts

1. **Code bindings (§1, §2): READY WITH FIXES.** DF3-R1 is blocking but needs only a one-sentence repair.
2. **Null-test streams and `s_inputs` (§3, §5): READY.**
   - 2b. **Model libraries (§3a): READY**, recommending (a). Apply notes DF3-R2 and DF3-R3 in the wording, or in the §16 image PR's brief.
3. **Seed source in C2 (§4): READY**, (b) still recommended. DF3-R4 is a wording note.
4. **D-13 (§6): READY WITH FIXES.** DF3-R5 is a note, because the output is diagnostic only.

## 4. What I could not check

- Whether scikit-learn and LightGBM wheels exist for CPython 3.14 and are compatible with NumPy 2.5.3. I also could not check LightGBM's `libgomp` dependency or the libraries' seed behaviour: neither is installed, so DF3-R3 relies on what I remember of their packaging.
- Whether `dsr.py` received the owner's §16 PR review, as M13's "reviewed under §16 with the engine" implies. Engine review records mention `dsr.py`, but I did not trace the owner's approval.
- Whether a full run has already started or an image digest is already recorded. My reading is that none has (the run definition is not yet committed), and §3a (a) depends on this.
- How C-6 path state is initialised in the existing walk-forward code, which DF3-R5 relies on. No tests were run.
