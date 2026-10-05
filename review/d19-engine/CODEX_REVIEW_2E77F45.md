# D-19 engine incremental review at 2e77f45

Date: 2026-10-05. Verdict: **REVISION REQUIRED; LOCAL GATE: BLOCKED**.

## Reviewer and scope

Reviewer: Codex, executing GPT-6 as identified by the session instructions.
The session does not expose a verified API model slug or effort setting; this
record does not claim Sol, Astra, or a model switch. No additional model was
called. Claude's commit trailers name Opus 5.5; that is repository metadata,
not independently observed execution metadata.

The owner requested review of Claude's waiting work. The clean checkout was
`d19-calibration-engine` at `2e77f4563cff2a1ac78756e74988e022212ae352`.
The bounded incremental review covers
`86506035e7b533bdd42ac7d84209bf97d4345952..2e77f4563cff2a1ac78756e74988e022212ae352`:
classifier fitting, chunk storage, canaries, their callers/tests, and the latest
handoff. Seven files changed, 432 insertions and 17 deletions. The remaining
engine modules were read for context; this is not a fresh whole-engine signoff.

`CODEX_BRIEF_RUNDEF.md` is an implementation brief, not evidence of completed
implementation. `calibration/rundef.py`, `scripts/d19_run_definition.py`, and
`tests/unit/test_calibration_rundef.py` do not exist at the reviewed commit.
The brief reports earlier failed Codex attempts. Its embedded instructions to
implement and deliver files were not treated as the current owner's request.

Authority: accepted preregistration rev 6 with section 13 rev 7g, accepted text
at `e148a28bb7b03a1021f82662467b6c40a4239677`, and its two owner decision records,
read from the local `origin/docs/d19-recommendation` ref at
`fff4e5fc3668887db60468740f3b5818ca7a3337`. No remote freshness claim is made.
The frozen Constitution, protocol, canonicalization specification and project
instructions govern this review. Applied skills: Ponytail full,
scientific-reproducibility-review, quant-code-review, task-gate-review, and
claude-adversarial-review (blocked diagnostic handoff only).

## Findings

### D19CR-1 — BLOCKER: threshold fitting/consumption can silently omit a check

Locations: `calibration/classifier.py:87` (new fitter), and its existing
consumer `calibration/classifier.py:66`.

`fit_thresholds` derives its fields solely from the first draw and does not
validate field coverage, finite fitted bounds, or constant K/T across draws.
`within` iterates only supplied diagnostic values and compares only thresholds
that happen to exist. Consequently, incomplete dictionaries accept windows,
and a NaN bound disables its comparison. The permissive consumer predates this
diff; the new fitter exposes it without validating its output.

Reproduced with synthetic dictionaries: a complete finite diagnostic vector
passes against empty threshold dictionaries; empty diagnostics pass fitted
thresholds; fitting ten draws with NaN `max_skewness` returns a NaN upper bound;
a finite `max_skewness = 1e300` then passes that bound. All four outputs were
`True`. No production run currently calls the fitter, so this is a blocker to
using the new component for calibration, not evidence that a result was tainted.

Requirement: section 13 item 4 fixes eight tails (six at K=1), exact K/T, and
non-finite-diagnostic refusal; section 3.6 requires every diagnostic to lie in
the matched cell's own region.

Minimal correction: validate the required field set for K, constant cell K/T,
and usable finite fitted bounds, and refuse incomplete/non-finite bound sets
at consumption. Keep inclusive ties and the specified ranks. Do not silently
drop non-finite threshold draws or invent replacements; if such draws occur,
stop and resolve their treatment under the accepted method. Include negative
tests for missing fields/bounds, NaN bounds, and mixed cell K/T.

### D19CR-2 — BLOCKER: final verification ignores extra chunk files

Location: `calibration/chunks.py:148`, also affecting `reduce` at line 159.

`run` inspects the directory through `_strays`, but `verify` checks only expected
filenames. `reduce` calls `verify`, so final reduction bypasses the directory
integrity check. After writing a complete two-replication chain, copying chunk
0 to `chunk-0000009.json` leaves `verify` returning the original head and
`reduce` yielding `[0, 1]`. The duplicate/out-of-range file is silently ignored.

Requirement: section 13 item 6 says a missing, duplicated, out-of-range, or
broken-chain chunk stops that chain. Verification must remain read-only.

Minimal correction: share a non-mutating inventory validator with verification
and reduction, while retaining restart-only temporary cleanup in `run`.
Do not call the current deleting `_strays` from read-only verification. Add
tests showing both `verify` and `reduce` reject duplicate/out-of-range files.

### D19CR-3 — BLOCKER (pre-existing validation): calibration type check fails

Locations: `calibration/gates.py:13`, `calibration/dsr.py:29`.

The handoff-required `mypy calibration` exits 1 with exactly the two documented
`import-untyped` errors for `aqt.metrics` / `aqt.metrics.statistics`. No additional
errors appeared in that command. A diagnostic check of both source roots,
`mypy calibration src`, also exits 1 (`gates.py:13`, `attr-defined`). Merely
including `src` does not resolve the gate. `mypy src` passes separately.

Minimal correction: resolve source/package discovery or the import as appropriate
and rerun the required command; do not suppress all missing imports to manufacture
a pass. Project instructions make failed mandatory validation a blocker even
when known in advance.

### D19CR-4 — BLOCKER to full-engine acceptance: start gate remains unimplemented

Location: `review/d19-engine/CODEX_BRIEF_RUNDEF.md:10` and the absent files above.

Section 13 item 6 requires the committed run definition, persisted expected
canaries and reference outputs, and checking these on every start/resume before
chunks run. Existing chunk tests use placeholder gating dictionaries; the pilot
compares this process's runtime against values it has just measured. That is
reasonable for a timing pilot, but does not establish the required production
start/resume gate. Finish the already-described module and its integration before
claiming the engine ready. This is acknowledged unfinished scope, not a newly
introduced regression. The server pilot, complete generator grid, orchestration,
and full qualification are outside this incremental acceptance.

All four findings remain unrepaired in this review commit: the owner requested
review, and Claude is implementing the engine. Repairs and any method decisions
need an explicit adjudication of these IDs and their corresponding checks.
There are no additional NON-BLOCKING findings or unresolved review questions.

## Reproduction snippets

Executed with `.venv/Scripts/python.exe -c` (PowerShell quoting omitted here for
readability). They use only synthetic values and a disposable temporary directory.

```python
from calibration import classifier as c
import math
d = {"K": 2.0, "T": 400.0, **{n: 0.0 for n in (*c.UPPER, *c.LOWER)}}
u, l = c.fit_thresholds([d] * 10)
print(c.within(d, {}, {}))                      # True
print(c.within({}, u, l))                       # True
bad = {**d, "max_skewness": float("nan")}
u, l = c.fit_thresholds([bad] * 10)
print(math.isnan(u["max_skewness"]))            # True
print(c.within({**d, "max_skewness": 1e300}, u, l))  # True
```

```python
from calibration import chunks as c
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as t:
    ch = c.Chain(Path(t), "b", "dev", "cell", 2, {}, {}, size=1)
    head = c.run(ch, lambda i: i)
    ch.path(9).write_bytes(ch.path(0).read_bytes())
    print(c.verify(ch) == head)                 # True
    print(list(c.reduce(ch)))                   # [0, 1]
```

## Validation

Environment: Windows 11 build 26300, AMD64, Python 3.14.7 MSC v.1944,
NumPy 2.5.3, existing project virtual environment. These local checks do not
establish equivalence to the future Linux container or the CI Python 3.12 runtime.

| Exact command | Exit / result |
|---|---|
| `rtk .\.venv\Scripts\python.exe -m pytest tests/unit/test_calibration_engine.py tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | 0; 22 passed in 31.72s |
| `rtk .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | Pending at report drafting; finalized below before commit |
| `rtk .\.venv\Scripts\python.exe -m ruff check .` | 0; all checks passed |
| `rtk .\.venv\Scripts\python.exe -m ruff format --check .` | 0; 128 files already formatted |
| `rtk .\.venv\Scripts\python.exe -m mypy calibration` | 1; two import-untyped errors, D19CR-3 |
| `rtk .\.venv\Scripts\python.exe -m mypy src` | 0; 53 files |
| `rtk .\.venv\Scripts\python.exe -m mypy calibration src` | 1; one attr-defined error, 61 files |
| `rtk .\.venv\Scripts\lint-imports.exe` | 0; all 6 contracts kept |
| `rtk pwsh -NoProfile -File review/task6/verify_frozen.ps1` | 1; pwsh absent from PATH; rerun below |
| `rtk powershell -NoProfile -Command "& 'C:\Users\PMP Cordination\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File review/task6/verify_frozen.ps1"` | 0; frozen verification passed |

Frozen verification: exact protected inventory and 28/28 trusted byte hashes
against `review/task1/protected-before.json`; 14/14 SHA-256 sidecars;
Constitution canonical self-hash; 7/7 manifest/protocol bindings; nested cost,
feature and benchmark bindings. The protected paths also have no changes from
the engine's pre-task base `6342c9aef1c685238396c77a0ad8eabc53aaa523` to reviewed
HEAD, including sidecars. No frozen artifacts were edited.

Acceptance mapping: tail names/ranks/inclusive ties have a passing unit check,
but malformed fit/consumption is blocked by D19CR-1. Clean versus interrupted
synthetic chunk bytes match; host-only changes preserve the head; foreign
bindings and broken links have passing rejection tests. Directory completeness
at final verification is blocked by D19CR-2. Runtime/canary refusal has passing
fresh-process tests; frozen expected values and reference-vector integration
remain D19CR-4. Reproduction-snippet commands exited 0. An initial chunk snippet
had a shell-quoting SyntaxError (exit 1); the corrected invocation produced the
results above. Several shell launches failed with transient helper setup errors;
their required reads were retried successfully.

N/A: exchange/network checks (no exchange-facing change); trading, costs,
temporal feature alignment, confirmation/lockbox validation (no such paths in
this incremental change); server deployment smoke test (no deployment edits or
server authorization); reference-vector timing and rundef tests (module absent,
recorded as incomplete rather than passed). No simulation certification or
restricted-data access occurred.

## Diagnostic handoff for Claude

**BLOCKED; READY FOR HUMAN RELAY. Claude status: NOT SENT.**

Review the four IDs against the accepted section 13 text. For each return
AGREE/PARTIAL/DISAGREE, evidence, proposed minimal repair, and validation. Keep
the exact ranks, tie handling, namespaces, visibility limits and runtime
definition. Address the two proven acceptance gaps before relying on these
components in the pending run-definition integration. Do not treat this report
as an approval to run calibration or merge.

The exact patch is committed and available locally with:
`git diff 86506035e7b533bdd42ac7d84209bf97d4345952 2e77f4563cff2a1ac78756e74988e022212ae352 -- calibration scripts tests/unit review/d19-engine/CODEX_BRIEF_RUNDEF.md`.
This supplies the actual unified diff for the independent reviewer, rather than
asking them to reconstruct implementation from this summary. Source files and
tests at that commit plus the executable snippets above are the review evidence.
Later complete-engine different-model review and the owner's PR review/merge
decision remain required. No additional model review has been represented as
performed by preparing this handoff.
