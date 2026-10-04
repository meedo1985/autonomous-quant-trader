# Sol §16 third focused re-review of Task 29 repair at `0ddddae`: FIX

Date: 2026-10-04. Focused re-review of the S29R2-1 repair (`REPAIRS_DA27588.md`), finding IDs `S29R3-n`. Prompt scope: `git diff fbffd0b 0ddddae`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a105f1-c518-7b20-91ba-aa079fd81e31`. The final message is reproduced below unchanged, except that local file links were shortened to repository-relative form.

---

Model: OpenAI Codex Sol (`gpt-5.6-sol` requested; exact serving variant not exposed), GPT-5 family  
Commit: `0ddddae7a24499590eb97eece43d9d24df99dad4`  
Verdict: **FIX**

### S29R2-1

**NOT RESOLVED — partially repaired.**

Startup, owner-command, pre-send, ordinary hour-end, busy-skip, and final saves are correct. Long reconciliations no longer silently omit later hours, and the final-save false alarm is fixed.

### New finding

| ID | Severity | Location | Scenario / evidence | Fix |
|---|---|---|---|---|
| S29R3-1 | **BLOCKER** | [paper_loop.py](src/aqt/app/paper_loop.py:900), [paper_loop.py](src/aqt/app/paper_loop.py:920), [paper_loop.py](src/aqt/app/paper_loop.py:951), [paper_loop.py](src/aqt/app/paper_loop.py:1011) | Successful `FREEZE_EXIT`, failed HALT reconciliation, and successful HALT override save after the command hour’s durable work is complete; the code explicitly treats the override attempt as ending that hour. Nevertheless, `unfinished` remains that command hour. If reconciliation saves at H+2 and the process dies immediately, `unfinished_hours()` reports H–H+2. H is a false alarm; only H+1–H+2 were skipped. The new crash test has no owner/FREEZE/HALT scenario, so it misses these save sites. | At these terminal reconciliation saves, atomically advance `unfinished_from` to H+1. Move any required post-save event before the save, or move the save after it. Add crash tests for successful `FREEZE_EXIT` and failed/successful HALT override with multi-hour reconciliation. |

No other new defect found.

### Compatibility and behavior

The field does not otherwise change replay or restart selection: restart still derives from the journal save timestamp, and replay ignores `unfinished_from`. Old snapshots remain exact-parse compatible because a missing field becomes `None` and serialization omits it again. An in-memory old/new exact-parse probe passed.

### Commands and results

```text
git diff --check fbffd0b 0ddddae -- <scope>
PASS

git diff --quiet fbffd0b 0ddddae -- docs protocols schemas specs FROZEN_HASHES.json
PASS — frozen scoped paths unchanged

ruff check --no-cache <five changed code/test files>
PASS

ruff format --check --no-cache <five changed code/test files>
PASS — 5 files formatted

mypy --no-incremental --no-sqlite-cache --cache-dir=NUL <three source files>
PASS — no issues

lint-imports --no-cache
PASS — 6 contracts kept

pytest --collect-only -s -p no:cacheprovider <two changed test files>
PASS — 44 tests collected; not executed because `tmp_path` is unavailable here

In-memory exact-parse/range probe
PASS — old/new mappings parse exactly; H saved at H+2 produces H–H+2

git status --porcelain=v1 --untracked-files=all
PASS — clean
```

No network, credentials, confirmation data, lockbox data, edits, commits, or pushes were used.

Do not merge `0ddddae` yet.  
The common crash paths are repaired, but FREEZE/HALT reconciliation saves can falsely report a completed hour as unfinished.  
Advance those terminal saves to the next hour, add crash tests, then re-review and commit the review record.
