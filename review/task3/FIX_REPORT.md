# Task 3 corrective work

Base HEAD: 853cb62b199d0f8f6c3ab5844eba3657285927af. Working-tree changes; no commit/push performed.

A1: removed silent post-gap slicing. Every supplied historical bar through the decision is validated; a gap raises rather than resetting volatility. Future gaps do not affect prior costs. This rejects unresolved histories, not a scientific resumption policy.
A2: public resolve_execution rejects nonhourly series for baseline and delay paths.
A4: scale basis points before multiplication and reject nonfinite cost_quote output.
A3: recurrence unchanged; user approval is recorded in SCIENTIFIC_DECISION.md. Decision-time sigma under delay stress also explicitly included.
Documentation: removed exact-spec/total-function overclaim; code docstring describes the approved convention and gap rejection. Earlier LOCAL_REPORT.md is historical pre-fix evidence, superseded on these points by this note; its no-silent-dropping claim was not true before this correction.

Validation on corrected working tree:
- .venv/Scripts/pytest.exe -q: exit0,112 passed (106 prior +6 regression cases).
- .venv/Scripts/ruff.exe check .: exit0.
- .venv/Scripts/ruff.exe format --check .: exit0,22 files.
- .venv/Scripts/mypy.exe src: exit0,18 sources.
- .venv/Scripts/lint-imports.exe: exit0,4 kept/0 broken.
- .venv/Scripts/pre-commit.exe validate-config: exit0.
- Existing Python3.12.10, runpy verify_task1.py governance()/configuration() with .venv/Lib/site-packages: exit0;28 protected bytes/inventory,14 sidecars,canonical bindings,schemas,configuration PASS.
- git diff --check: exit0.

New regressions: long volatile history with sufficient post-gap flat history raises; future gap preserves earlier quote; daily resolver rejected for delay0 and1; large representable cost stays finite; truly unrepresentable cost raises. No dependency added; no frozen bytes changed.

Final validation after user approval:
All commands above rerun successfully; pytest112 passed in0.60s. Original verify_task1.py governance/configuration/boundaries assertions all ran, with only evidence output redirected to review/task3 and existing site-packages supplied to portable Python child processes. 20 direct/indirect mutation probes rejected, all controls passed; boundary-probes.json contains evidence. Task1 historical evidence untouched. No validation assertion changed.

User approved SCIENTIFIC_DECISION.md explicitly. Astra focused correction review PASS (ASTRA_FINAL_REVIEW.md); all material code findings addressed. LOCAL GATE: PASS for Task3 cost-model scope. Prior Fable findings adjudicated; corrected snapshot has not been resent to Fable. Review packet prepared, Claude status NOT SENT for this snapshot. Scientific approval does not authorize live trading or any frozen amendment. Task4 not started. GitHub CI outcome will be checked after commit.

Later status: Claude Fable 5.1 independently reviewed the corrected current
Task 3 snapshot at repository HEAD `3054805` and returned **PASS**, confirming
A1, A2, and A4 are closed and the approved scientific conventions are applied.
See `review/FABLE_5_1_TASKS_2_3_4_REVIEW.md` and its model-proof JSON. The
paragraph above is retained as the truthful status at correction time.
