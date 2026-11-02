# Sol re-check 3 of the R-14a lockbox module (87ff5e0)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-sol`; session 01a19c8a-c03d-78d2-a510-0a2fe046364f; 102,148 tokens), 2026-11-02.
- Prompt: review/r14a-modules/RECHECK3_LOCKBOX_PROMPT_SOL.md (committed 0c4e719).
- Finding IDs: R14L3-S-1 (BLOCKER). Verdict: **FIX**.
- Adjudication: `LOCKBOX_ADJUDICATION_87FF5E0.md` (with the repair).

## Report (verbatim)

What this change does: it checks the nominee against a declaration carried from `start()`, validates the acceptance record’s block hash and height fields, and rejects an image digest mismatch before appending a startup record. **Verdict: FIX.**

### Finding

**R14L3-S-1 — BLOCKER** — [calibration/c2_lockbox.py:1225](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:1225), [calibration/c2_lockbox.py:1330](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:1330). `Started` is frozen, but its verified declaration is a mutable dictionary. In a synthetic probe, I changed its nominee `trial_index` from 3 to 4 after construction, then changed the request and artifact coherently and recomputed the fit seed. The declaration hash changed, yet `pre_read_check` returned **`PASS`**. The new tests do not exercise mutation after `start()`.

Annex D §D-3.2 requires the fit seed to use the index in the nominee’s C2 trial record; §D-3.5 requires rederivation from that record, and R-14a item 2 requires the posted declaration chain to remain verified. A caller holding `Started` can therefore select a different fit seed after verification. Carry the verified declaration as immutable bytes through evaluation, check its hash against the verified post, and add a synthetic test that changes the handoff after `start()`.

### Other checks

- **R14L2-S-2:** The new field checks reject malformed block hashes and heights. The record’s truth and provenance remain an explicitly open **owner decision** under O-6a SPEC §§3–5; the code does not claim to verify them.
- **R14L2-S-3:** `start()` rejects a supplied image digest that differs from the signed digest before `append_startup`. How the running image is measured remains part of the open launch route.
- The declaration’s per-entry `family` and `trial_index` are correctly marked **[DESIGN]** additions beyond Annex B §2.4 for S4 binding. The launch route, acceptance provenance, qualified-image vectors, and S4 format bindings are still described as open. `FROZEN_VECTORS_SHA256` remains `None`.
- The new wrong-index test fails when `_check_declared` is removed, but misses R14L3-S-1. I found no other regression in the changed paths.

**Validation:** 19 targeted tests passed. A broader read-only run had 67 passes and 3 setup errors because no temporary directory was writable. Ruff checks and all 7 import contracts passed; mypy could not complete in this sandbox. The 13 frozen-file sidecars matched Git blob bytes, and the reviewed diff changes no frozen path.

**Not verified:** the qualified Linux image, node-backed acceptance evidence, actual launch route, protected-data run, or the complete test suite. This read-only response made no repository changes; the review record still needs to be committed under `AGENTS.md`.
