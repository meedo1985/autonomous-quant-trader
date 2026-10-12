# Adjudication of the Sol High re-review of the D-19 engine at c8942db

Review: `review/d19-engine/SOL_REREVIEW_C8942DB.md` (RR-1..RR-5). Adjudicated
and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| RR-1 BLOCKER | AGREE, repaired | `gates.u_g` evaluates all five gates again (as at aa3457b) and returns the first unavailable reason; an engine fault in a later gate is never hidden by an earlier refusal. Test: with G-2 refusing first, an exception in G-12 still propagates. |
| RR-2 BLOCKER | AGREE, repaired | The code inventory now includes the `scripts/d19_*.py` entry points (and the future driver, if named `d19_*`). The script puts this checkout's root and `src` first on `sys.path`. `start_gate` first refuses if any loaded `aqt`/`calibration` module's file is outside the checkout (`loaded_outside`). Test: `loaded_outside` names `aqt.metrics.statistics` and `calibration.rundef` for a foreign root and nothing for the repository. FE-5 stays a driver requirement: the driver must call `start_gate` before workers or chunks start. |
| RR-3 MAJOR | AGREE, repaired | `record` no longer trusts `git status`: it lists HEAD's engine paths with `git ls-tree` and compares every file's canonical hash with `git show HEAD:<path>`, so skip-worktree/assume-unchanged files, ignored extra files, and missing files are all refused. The preregistration is read with `git show <prereg-commit>:<path>` and hashed; `--prereg-file` is removed. Tests: a skip-worktree edit and an ignored extra `.py` (both invisible to `git status`) are refused. |
| RR-4 MAJOR | AGREE, repaired | Code hashes use canonical bytes (CRLF read as LF), so one commit has one identity on Windows and Linux. Note: this checkout had 0 CRLF engine files when checked, but `core.autocrlf=true` and Windows text-mode writes can produce them, so the risk was real. Test: a CRLF copy and an LF copy hash equally. |
| RR-5 MINOR | AGREE, repaired | Tests now: G-10 and G-12 trace changes each change the K = 20 outputs without changing availability; the K = 20 case traces all four kinds (`g1_block`, `g1_replicate`, `g10_var`, `g12_ess`) with horizons 24/72/168; outputs include the benchmark hash; the unavailable case's cause is `INVALID_SERIES`; eager evaluation (RR-1); canonical hashing (RR-4); loaded-module provenance (RR-2). |

Dispositions confirmed by the review: FE-6 repaired; FE-7 (re-pilot rate, then
owner) acceptable; FE-4 and FE-5 acceptable only as explicit pre-driver
operational requirements. They are recorded as such: the driver must (a) call
`start_gate(defn, root)` before any worker or chunk, (b) build every `Chain`
from `definition_sha256(defn)` and the returned gating, and (c) be launched
with `AQT_IMAGE_DIGEST` taken from `docker inspect` on the host.

Nothing left unrepaired.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1829 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |

Next re-review: Codex `gpt-6-sol` (owner instruction 2026-10-05: "next time use sol 6 not 5.6").
