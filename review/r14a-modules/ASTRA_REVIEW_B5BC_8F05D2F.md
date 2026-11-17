# Astra review of 6b build B5b and B5c at 8f05d2f (verbatim record)

- Reviewer: Codex CLI `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s read-only`; the CLI log shows `model: gpt-6-astra`, `provider: openai`. The reviewer itself says the model ID is not exposed to it. A first run was stopped by Claude Code for low system memory and produced no output; this is the second run.
- Prompt: `B5BC_REVIEW_PROMPT_ASTRA.md` (commit 42c7680). Recorded 2026-11-15 by Claude Opus 5.5 without edits below the line. Note: the owner accepted B5B-D-1 in `73bbc5f`, after this run started.

---

**Verdict: FIX.** Reviewed `8f05d2f` through notes-only successor `42c7680`; working tree unchanged.

**Model:** Codex. The exact runtime model ID is not exposed, so I cannot attest that this was an Astra run. Findings are proposals, not approval.

**B5BC-A-1 — HIGH: gate unavailability loses its cause classification.**  
Location: [evaluation_record](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:4327), lines 4323–4347.

- **Evidence:** `cause` always comes from `nom.cause`. Successful nomination leaves that `None`, even when subsequent gates produce `NO_RESULT`. An in-memory reproduction with `SIGMA_UNBOUND` and `DAYS_INCOMPLETE` produced `outcome="NO_RESULT", cause=None`; their existing classifications are respectively `U_ops` and `U_proc`.
- **Failure scenario:** operational gate failures disappear from explicit cause accounting, contrary to P18-7 and design §11. Individual gate records contain no cause field either.
- **Correction:** derive and record gate-caused unavailability using the existing classifier and infrastructure-first precedence. Add procedure-only, infrastructure-only, and mixed-cause record tests. Also explicitly resolve `BENCHMARK_SPEC_MISSING`: the current classifier defaults it to `U_proc`, although missing infrastructure is `U_ops` under P18-7. Do not silently revise the owner-bound reason list.

**B5BC-A-2 — MEDIUM: the record drops the remaining ledger-breach evidence.**  
Location: [evaluation_record](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:4317), lines 4317–4348.

- **Evidence:** `FamilyLedger` retains every breach and rewritten attempt, but the record copies neither. With two breached attempts, the generated record retained only `LEDGER_ORDER:attempt-a0`; the second breach, breach kinds, positions, and attempt history were absent.
- **Failure scenario:** the evaluation record cannot provide the complete breach accounting promised by design §3, lines 239–247.
- **Correction:** preserve that computed audit evidence. Explicitly reconcile §10’s abbreviated field layout with §3’s existing requirement; add a multiple-breach record test.

**B5BC-A-3 — MEDIUM: the narrowed C-14 test does not enforce its claimed boundary.**  
Location: [test_no_code_path_reads_the_report](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_cpcv.py:363), lines 363–384.

- **Evidence:** the scanner checks only identifiers/attributes named `cpcv_report` or `cpcv`. This in-memory insertion after report computation still passed both assertions:
  ```python
  if c14.get("status") != "COMPUTED":
      gates_["G-9"] = Gate(FAIL)
  ```
- **Failure scenario:** a future gate can depend directly on the diagnostic through `c14`, while this mandatory guard remains green. **The current production code does not contain that dependency.**
- **Correction:** constrain report-value uses to the production/storage/serialization statements, rather than allowing whole scopes by name. Add a negative mutation test for the example above.

**Readings and deviation**

| ID | Assessment |
|---|---|
| B5B-D-1 | **PARTIAL:** the local specification’s raw SHA-256 is supported by S4 §1a; missing specification correctly gives UNAVAILABLE/NO_RESULT. Cause classification needs A-1’s correction; owner acceptance remains outstanding. |
| B5B-R-1 | **AGREE:** one lazy protected read; each nominee receives its own warm-up cut. |
| B5B-R-2 | **AGREE:** last derived-completed result is selected only for a currently completed trial. |
| B5B-R-3 | **AGREE:** no nominee means empty gates, no protected read, and status (b). |
| B5B-R-4 | **PARTIAL:** current production flow is diagnostic-only; the claimed test enforcement fails A-3. |
| B5C-R-1 | **PARTIAL:** listed fields, hashes, float conversion and pre-look ledger identity agree; cause and breach evidence have A-1/A-2’s omissions. |
| B5C-R-2 | **AGREE:** `differs` compares nominee, reason and G-9 result; `decision` records Task 12’s reason/nominee. |
| B5C-R-3 | **AGREE:** declaration entry, selected `d_sha256`, four code hashes and beacon round are correctly passed. |
| B5C-R-4 | **AGREE:** persist receives canonical bytes; closing hashes those same bytes and follows successful persist under the lock. |
| B5C-R-5 | **AGREE:** post-look termination remains a release veto even if closing subsequently succeeds. |
| B5C-R-6 | **AGREE:** Store states the scoped obligations; their implementation and release tests remain the store build’s responsibility. |

No regression found in `of_cycle`: an in-memory anchor check rejected a foreign-cycle result naming this cycle’s attempt; an unrelated result remained excluded.

Additional useful tests: different warm-ups for the two nominees; nominee/reason changes in `differs`; failure during sealing after evaluation serialization. Existing recorder tests cover wiring well but do not cover these cases.

**Validation**

All commands used `rtk proxy`. Here, `T` expands to the four requested test paths, in their supplied order; `F` expands to `calibration/c2_confirmation.py` followed by `T`.

| Command/check | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest T -q -p no:cacheprovider`, with `PYTHONDONTWRITEBYTECODE=1` | Exit 1 before collection: no writable temporary directory. Full suite **not verified**. |
| `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_look_records.py tests/unit/test_c2_confirmation_cpcv.py -q -p no:cacheprovider --capture=sys -k 'plain_refuses or no_code_path or groups_are or the_28_splits or every_split_lies or training_rows_purge or test_group_labels'` | **7 passed, 15 deselected**. |
| `.venv/Scripts/python.exe -B -m ruff check --no-cache F` | Pass. |
| `.venv/Scripts/python.exe -B -m ruff format --check --no-cache F` | Pass, five files. |
| `.venv/Scripts/python.exe -B -m mypy --no-incremental --cache-dir=nul F` | Exit 1: ten errors in imported, unchanged `test_calibration_screen.py`, matching the build notes’ reported limitation. |
| `.venv/Scripts/lint-imports.exe --no-cache --no-logo` | **7 kept, 0 broken**. |
| Read-only Python reproductions and AST mutation | Confirmed A-1–A-3 and the anchor attribution behavior. |
| Frozen-artifact verification | **28 protected files**, **14 sidecars**, manifest, Constitution self-hash and protocol bindings matched; protected paths unchanged from baseline. |
| Git status, staged/unstaged diffs, base/target and target/HEAD comparisons | Clean; successor adds only the two review-note files. |

**Principal ranges read**

- `calibration/c2_confirmation.py`: 391–547, 882–1025, 2029–2157, 2836–2882, 3335–3585, 3652–3713, 3730–3828, 3887–3974, 4074–4524.
- Requested tests: families 1–248; look records 1–251; open 1–327; CPCV 1–384.
- Build notes 1–72; B5a adjudication 1–38; `DESIGN_SLICE6B.md` 1–479; `DESIGN.md` 71–237.
- Supporting DSR implementation 45–184; Annex A 150–190; S4 draft 96–121; Constitution, protocol and hash-canonicalization rules.

**Local gate: BLOCKED.** Full tests remain unavailable and type checking is not clean. No files were modified or committed; this report must be committed before being treated as the completed repository review record.