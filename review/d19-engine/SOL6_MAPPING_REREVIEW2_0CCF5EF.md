# §16 different-model re-review 2 of the §3.6 mapping at 0ccf5ef

- Reviewer: Codex CLI, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1319a-b563-75b2-9df8-37da6a3653fa)
- Date: 2026-10-12
- Reviewed: a self-contained packet with both earlier records, the full calibration/mapping.py and tests/unit/test_calibration_mapping.py at 0ccf5ef, and the rundef and qobj excerpts they use.
- Outcome: MP-R1, MP-R2, MP-R4 resolved; MP-R3 deferred to the declaration task (left unrepaired here deliberately: the declaration pipeline that builds the E-DIFF input does not exist yet); no new findings. Readings MP-1..MP-4 accepted (MP-1 subject to MP-R3). Verdict: ACCEPT.
- The reviewer's output follows verbatim.

---

| Finding | Status | Basis |
|---|---|---|
| MP-R1 | **Resolved** | `load()` verifies the posted manifest hash and the digests of `choices.json`, `definition.json`, and `mapping.py`; `map_design()` records the posted hash. |
| MP-R2 | **Resolved** | `check_engine()` binds the recorded engine inventory to the commit, checks loaded `calibration` and `aqt` source files, and calls the bytecode safeguard. `check_runtime()` checks the recorded runtime, canaries, image digest, and reference vectors. |
| MP-R3 | **Deferred** | The declaration pipeline must still validate and bind complete, ordered exploration E-DIFF rows after warm-up. |
| MP-R4 | **Resolved** | The loaded `grid.py`, including the source of `T_C2`, is checked against the recorded engine commit before comparison. |

**New findings:** None from the supplied code.

**Readings:** MP-1 is accepted subject to MP-R3 at declaration; MP-2 is accepted; MP-3 is accepted; MP-4 is accepted for this mapping path, with the declaration entry script covered by MP-R3.

This was a static review of the supplied packet. I ran no tests and edited no files. The review record still needs to be committed under the project rule.

**ACCEPT.**