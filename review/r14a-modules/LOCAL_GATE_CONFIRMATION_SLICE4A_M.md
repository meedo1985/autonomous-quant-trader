# Local gate: confirmation slice 4a, route M (in-module BLS, line 266 loader)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09, applying the repository
  skills `task-gate-review`, `scientific-reproducibility-review`, `quant-code-review`.
  Self-review by the author; the independent different-model review is Sol
  (`SLICE4A_M_PROMPT_SOL.md`).
- Scope: `DESIGN_SEED_VERIFIER.md` rev 3 (route M, owner's choice). Closes, for review:
  R14S4-S-1 (injected line266 and verifier), LG4-1 (BLS), LG4-6 (line 266 in the image);
  SV2-S-3 (import before protected read), SV2-S-6 (parent DESIGN §5.1 reconciled).
- Finding IDs: LGM-n. **LOCAL GATE: PASS** (no open blocker), items in §5.

## 1. Changed files

- `calibration/c2_confirmation.py`: BLS block (constants, `_Fq`/`_F1`/`_F2`/`_F12`,
  projective point ops, G1/G2 decompression, `_expand_xmd`, `_sswu`, `_iso_map`,
  `_hash_to_g1`, `_twist`, `_line`, `_miller`, `_pow12`, `bls_verify`); `Chain.scheme`;
  `load_line266`; `check_beacon` and `derive_seeds` without injected callables. No new
  top-level import (only `importlib`, `sys`, `types` inside `load_line266`).
- `tests/unit/test_c2_confirmation_bls.py` (new), `tests/unit/test_c2_confirmation_seeds.py`.
- `review/r14a-modules/bls-crosscheck-2026-11-09/` (evidence), `DESIGN_SEED_VERIFIER.md`
  rev 3, `DESIGN.md` §5.1 and §10.

## 2. Validation (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_bls.py` | 29 passed (4.3 s) |
| `pytest tests/unit/test_c2_confirmation_seeds.py tests/unit/test_d19_deploy.py` | 39 passed (engine import test still `['numpy']`) |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py` | 260 passed |
| `ruff format --check .`, `ruff check .` | clean |
| `mypy src` | no issues (56 files) |
| `mypy --strict` module + both seed test files | 10 errors, all in the imported `test_calibration_screen.py`, pre-existing (same at base) |
| `lint-imports` | 7 kept, 0 broken |
| cross-check vs drand-client 1.4.2 (`bls-crosscheck-2026-11-09/`) | 80/80 agree |

Not rerun: the other `calibration` engine suites (nothing they import changed outside
`c2_confirmation`, which they do not import).

## 3. Frozen artifacts

No path under `docs/`, `protocols/`, `schemas/`, `specs/`, no `FROZEN_HASHES.json` or
sidecar touched. `preregistration.py` is imported, never edited.

## 4. Self-review

- Constants: p, r, |x|, h_eff, A', B', Z and the 53 isogeny constants come from RFC 9380
  (§8.8.1, Appendix E.2), the isogeny ones extracted by script, never typed; the RFC's own
  vectors (K.1, J.9.1 including the intermediate map-to-curve point) pass, which pins every
  one. The G2 generator is pinned by the curve and order checks and by real signatures.
- Pairing: bilinearity checked during build (e(2P,Q)e(-P,2Q) = 1, e(P,Q) ≠ 1); the twist bug
  found then (multiply instead of divide by w², w³) is fixed and covered by the twist test.
  The sign of x does not matter for a product-equals-one check (both factors invert alike).
- Fail-closed: malformed points raise `SeedError`; a non-verifying signature returns False
  and `check_beacon` raises; a zero Miller numerator or denominator is refused (it would
  otherwise make both sides 0 and pass).
- Line 266: placeholders always used for that import (never a real jsonschema), restored in
  `finally`; a subprocess test runs the image's case and compares to the frozen function.
- Not constant time: public data only.

## 5. Items left open (not blockers for this slice)

- **LGM-1 (owner, OD-2):** the inert `jsonschema` placeholder during `load_line266`, as
  consistent with R-14 and R-14a items 2-3, disclosed in the module contract.
- **LGM-2 (owner, OD-4):** genesis time, period and scheme join hash and key in the signed C2
  `<<SIGNING>>` beacon row.
- **LGM-3 (slice 6):** the loader calls `load_line266()` before any protected read and the
  R-14 byte check after it; it supplies chain, capture, beacon and records from the governing
  records (LG4-2). The 7-day rule stays operational (LG4-4, SV2-S-4).
- **LGM-4 (lockbox / slice 6):** SV1-S-6 handoff and R14S4-S-3 `(family, trial_id)` lookup.
- **LGM-5:** the cryptography needs a careful independent review (R-14a item 1, §16); the
  cross-check is evidence, not proof.

Claude/Sol status: prompt `SLICE4A_M_PROMPT_SOL.md`, sent with this commit.
