# Local gate: R-14a lockbox module (`calibration/c2_lockbox.py`)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, applying the repository
  skills `task-gate-review`, `scientific-reproducibility-review` and `quant-code-review`
  (`.agents/skills/`). The same model wrote the module; this is a self-review, not the
  independent different-model review R-14a item 1 requires.
- Scope: the lockbox module of DESIGN.md rev 5.1 §6, §7.1 and §4 (worker side), built in
  slices `5ad19dc`, `8b62696`, `da366bf`, `031ffd5`, `00d7967`, plus the repairs of this
  gate (LG-1, LG-2, LG-3) in the commit that adds this file. Base: `fb3142f` (owner
  decision Q-P1 (b)). Out of scope: the confirmation module; the store, publisher and
  signer (separate builds, Annex D §D-3.9); the S4 text.
- Finding IDs: LG-n. **LOCAL GATE: PASS** (no open blocker), with the pre-signing items of
  §4 below, which block signing C2, not this design-stage build.

## 1. Changed files (branch vs `main`)

`calibration/c2_lockbox.py` (new), `tests/unit/test_c2_lockbox.py`,
`test_c2_lockbox_preread.py`, `test_c2_lockbox_run.py`, `test_c2_lockbox_chain.py`,
`test_c2_lockbox_worker.py` (new), and `review/r14a-modules/*` (design and review records).
No other path. The worktree was clean apart from this gate's repairs.

## 2. Validation (Windows 11, repo `.venv`, Python 3.14.7, numpy 2.5.3, scikit-learn 1.9.1)

| Command | Result |
|---|---|
| `pytest tests` (at slice 1, `5ad19dc`) | 2352 passed, 10 skipped, exit 0 |
| `pytest tests/unit/test_c2_lockbox*.py` (after LG-1..LG-3) | 89 passed, exit 0 |
| `pytest` of the six tests that scan `calibration/` (`test_binance_public`, `test_calibration_chunks`, `test_calibration_heldout`, `test_dashboard`, `test_monitoring`, `test_calibration_rundef`) | 150 passed; rundef: 76 passed in 674.12s (0:11:14); exit 0 |
| `ruff check`, `ruff format --check` (module and tests) | clean |
| `mypy` (strict, module and tests) | no issues |
| `lint-imports` | 7 contracts kept, 0 broken |

The full suite was not rerun after slice 1: every later slice changed only the new module
and its tests, which nothing else imports, and the tests that scan the `calibration/` tree
were rerun at each slice. Two background runs were stopped by Claude Code's low-memory
reaper (not failures) and rerun in the foreground. A full-suite run before the PR merges
is recommended (LG-12).

## 3. Frozen artifacts

`git diff main...HEAD` touches no path in `docs/`, `protocols/`, `schemas/`, `specs/` or
`FROZEN_HASHES.json`. Independently, from git blob bytes at HEAD (not the CRLF working
tree): all 13 sidecars match their files; each `*_sha256` entry of `FROZEN_HASHES.json`
equals a sidecar of the expected file (protocol, cost model, feature factory, benchmarks,
backtester spec, threat model, hash canonicalization); the Constitution's canonical
self-hash (rule 5 of `HASH_CANONICALIZATION_v1.md`) verifies. Baseline: `main`.

## 4. Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| LG-1 | BLOCKER (repaired) | `verify_chain` logged `post_txid` as the double SHA-256 of the raw bytes, which for a segwit post is the wtxid, so the §27 record would name the wrong transaction. | Repaired: `txid()` hashes the serialization without marker, flag and witnesses; test checks it equals the legacy serialization's hash and differs from the wtxid. |
| LG-2 | BLOCKER (repaired) | `run_evaluation` took `startup_check_id` and the `startup` record separately; the sealed check record could name a startup record other than the one the check used. | Repaired: the id is read from the record the check used (`None` if there is none); test added. |
| LG-3 | NON-BLOCKING (repaired) | The worker tests stub the compute, so the wiring (code install into the code directory, `screen.load` from it, the real run, two reads, bundle) was untested end to end. | Repaired: `test_end_to_end_with_the_real_run`. |
| LG-4 | NON-BLOCKING | `run_legs` maps every non-adapter exception to `RUN:RUN_FAILED`, as Annex D §D-3.3 requires; a bug in the post-freeze glue would therefore appear as a technical FAIL, not a crash. | Disclosed; this is R-14a's accepted residual. Review should read `run_asset` against `screen_gates`' run closure. |
| LG-5 | NON-BLOCKING | An equity `EventContractError` is recognised by its message (`event_contract.py` l.177, l.212). | `shortcut:` comment in code; upgrade if the engine gains an error code. |
| LG-6 | NON-BLOCKING (pre-signing) | `FROZEN_VECTORS_SHA256` is `None`, so every startup records `REFERENCE_VECTOR_MISMATCH` until it is computed on the qualified image (Annex D §D-3.4). | Build item before signing. |
| LG-7 | NON-BLOCKING (pre-signing) | Format bindings the S4 text does not fix, chosen in code as **[DESIGN]**: module-hash and `outpoint_F` rows as `name: "value"` once each; the declaration as canonical JSON with top-level `protocol_hash`; A1a item kinds `trial`/`signal`/`overlay`. | To be stated in the signed C2. |
| LG-8 | NON-BLOCKING (pre-signing) | The launch route (R14D3-S-2, R14D4-A-3): `verify_chain`, `verify_code` and `load_verified` exist, but nothing in the module can run before the module itself, so what starts the process, and that `record_startup` runs only after the chain and code checks, is not enforced in code. | Open pre-signing item; may need an owner decision on R-14a's wording. |
| LG-9 | NON-BLOCKING | The chain verifies the post transaction's form, its spend of F and its declaration hash, not its *acceptance* (6 confirmations, first post), which needs a validating node; it logs the acceptance record's hash. | Disclosed in code. |
| LG-10 | QUESTION | Readings marked **[DESIGN]** where Annex D leaves room: asset, series, start, interval and length failures map to `DAYS_INCOMPLETE`; a twice-run mismatch maps to `RUN:RUN_FAILED`; the pre-read check order decides which code is reported first; the published synthetic `d` and the encoding of non-float `BlockLength` fields. | For the independent review and the owner's §16 review. |
| LG-11 | NON-BLOCKING | Reproducibility evidence is local (Windows, Python 3.14.7), not the qualified Linux image; byte-exact reproduction on the image is unverified (bound to LG-6). | Build item. |
| LG-12 | NON-BLOCKING | Full suite last run at slice 1 (§2). | Run before the PR merges. |

Quant review notes (no finding): the decision reads bar `j - 1` and fills at the next
open through the frozen `leg_targets` and `run_event_contract`; model refits follow the
frozen `walk_forward` (`refit_instants(L0, L1)` gives `k = 0..15`, training rows purged
by the frozen `training_rows`); the run reads only `[S_pre, L1)` plus the derived final
row, never the bar at L1; BTC and ETH runs depend only on their own bars; both legs start
flat at L0 with equity 1.0.

## 5. Outstanding before merge

The independent different-model review (R-14a item 1; Sol, prompt
`RECHECK_LOCKBOX_PROMPT_SOL.md`), its committed record and adjudication, and the owner's
Constitution §16 PR review. Status of the independent review: NOT SENT at the time this
file was written.
