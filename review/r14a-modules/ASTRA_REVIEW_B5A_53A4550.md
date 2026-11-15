# Astra review of 6b build B5a at 53a4550 (verbatim record)

- Reviewer: Codex CLI `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s read-only`; the CLI log shows `model: gpt-6-astra`, `provider: openai`. The reviewer itself says the model ID is not exposed to it.
- Prompt: `B5A_REVIEW_PROMPT_ASTRA.md` (commit 4dd0e92). Recorded 2026-11-15 by Claude Opus 5.5 without edits below the line.

---

**Verdict: FIX.** One blocking intervening-entry gap and one test weakness.

**Model:** Codex; the exact runtime model ID is not exposed. I cannot verify that this run used Astra.

Reviewed implementation exclusively at `53a4550`, against `3ca103a`. No files modified.

**B5A-A-1 — HIGH / BLOCKER — An intervening result can escape cycle attribution.**  
Location: [c2_confirmation.py:4142–4144](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:4142).

- **Evidence:** `ours` contains this cycle’s attempt IDs, but `of_cycle` uses only `cycle_id` for result entries. Unlike `family_ledger` at lines 3388–3390, it does not detect a result claiming another cycle while naming our attempt.
- **Failure scenario:** A writer bypassing the look lock appends such a result between step 4 and the look append—the same class of writer the existing intervening-entry test simulates. `open_look` returns successfully with stale family state.
- **Reproduction:** An in-memory probe using the target implementation and hash-valid synthetic ledger chains produced:
  ```
  Same result visible at step 4: result entry 1 names another cycle
  Wrong-cycle result inserted before look: RETURNED Look; t0=running
  ```
- **Proposed correction:** Extend the interval predicate locally to reject result entries whose `attempt_id` belongs to `ours`, even when their claimed `cycle_id` differs. Add this regression test; the look entry must remain, but opening must raise.

**B5A-A-2 — MEDIUM / NON-BLOCKING — The concurrency test does not force contention.**  
Location: [test_c2_confirmation_open.py:196–221](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_open.py:196).

- **Evidence:** The barrier synchronizes `inputs()`, before qualification and the ledger read. Scheduling can still let one call finish before the other reads.
- **Failure scenario:** Removing the look lock can pass this test under serialized scheduling. The reported successful mutation detection establishes one observed run, not a reliable regression test.
- **Proposed correction:** Hold the first opener inside the locked section using events; establish that the second has attempted entry and cannot reach its ledger read until release. Assert one successful open and one refusal.

Otherwise, static inspection supports the required ordering: ledger writes follow the step 4–6 refusals; the append remains inside the lock and receives the truncated step-5 clock. Qualification comparisons preserve exact string equality.

**Readings**

| Reading | Assessment |
|---|---|
| B5A-R-1 | Agree: classifier `K_f` is the declared family trial count. |
| B5A-R-2 | Agree: qualification verification before locking is independent of ledger state; bounds precede append. |
| B5A-R-3 | Agree on interval boundaries; attribution needs A-1. A late result remains outside the interval. |
| B5A-R-4 | Agree: family-ledger refusal precedes append. |
| B5A-R-5 | Agree: declared families are sorted by `look_entry`. |
| B5A-R-6 | Agree on retaining the step-4 snapshot. Clarify that the re-read also validates cycle structure and the appended look’s identity. |

**Test quality:** Each existing test has assertions against a plausible regression; this is static assessment, since pytest could not run.

| Test lines | Plausible regression detected |
|---|---|
| 74–87 | Wrong timestamp, truncation, payload, bounds count, or returned snapshot |
| 90–95; 98–101 | Premature opening or incorrect day-180 boundary |
| 104–111 | Waiting for a breached family |
| 114–122 | Allowing a second look or terminated cycle |
| 125–130 | Omitting the ledger clock floor |
| 136–141 | Numeric normalization of `z_crit` or omitted rule comparison |
| 144–153 | Appending before classifier refusal |
| 156–160 | Skipping result identity validation |
| 176–184 | Omitting same-cycle intervening detection |
| 187–193 | Rejecting every intervening entry indiscriminately |
| 196–221 | Duplicate concurrent looks, subject to A-2 |

Missing tests: A-1; deterministic contention; late-result exclusion; foreign-cycle **outcomes**; exactly one clock read; second-family classifier failure leaving no append; distinct per-family bounds and verification that the verified report reaches `classifier_bounds`.

**Commands and results**

- `git diff 3ca103a 53a4550`: only the requested two files changed; no frozen-file changes in this range.
- Target module loaded from `git show 53a4550:calibration/c2_confirmation.py`, then `pytest.main(['tests/unit/test_c2_confirmation_open.py', '-q', '-p', 'no:cacheprovider'])`, with bytecode disabled: **blocked before collection**, no writable temporary directory.
- `.venv/Scripts/python.exe -B -m ruff check --no-cache --stdin-filename <file> -`, fed each target blob: **both passed**.
- `mypy.api.run(['--no-incremental', '--cache-dir', 'nul', '--follow-imports=silent', '-c', <target source>])`: **passed**, scoped source check.
- In-memory probe: **A-1 reproduced**; correctly labelled same-cycle result refused; foreign start and late result allowed. Filesystem locking was mocked, not validated.
- Import-boundary execution: N/A to this bounded review; the diff introduces no imports.

**Read coverage:** target module lines 730–877, 3162–3205, 3351–3638, 3710–3915, 4038–4148; target tests 1–221; trial fixtures 1–147; signed fixtures 1–90; ledger 240–415; relevant attempt parsing/writing helpers. Design rev 16 §§2, 4, 7, 8, 13 and supporting §3; build notes 1–43 from `4dd0e92`; Constitution, protocol and canonicalization specification.

Validation remains blocked by pytest’s environment failure. This report is uncommitted under the read-only instruction; preserve its metadata and both findings in the committed review record before treating the §16 review as complete.