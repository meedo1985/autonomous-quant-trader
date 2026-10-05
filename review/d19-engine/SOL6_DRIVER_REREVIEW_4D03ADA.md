# GPT-6 Sol re-review of the D-19 run driver at 4d03ada

- Prompt: `review/d19-engine/DRIVER_REREVIEW_PROMPT.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10c5f-0201-7bb2-b5d3-a1ca8963a9bb, 80,909 tokens.
- Verdict FIX (DR2-1..DR2-3). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant unavailable)  
FIX

- **DR2-1 — BLOCKER — [calibration/rundef.py:210](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:210), [calibration/generator.py:48](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/generator.py:48).** A manifest labelled `qualification` can contain one supported cell at `T=16`. It passes validation and can complete 300,000 draws, although rev 7g requires `T=T_C2` and the threshold run over every enumerated candidate cell. Refuse qualification manifests until the complete frozen cell manifest and its supported generators can be verified.

- **DR2-2 — BLOCKER — [scripts/d19_run_definition.py:128](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run_definition.py:128), [scripts/d19_run.py:72](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run.py:72).** `seed_spec` is recorded without validation; the test fixture records `{"anchor":"x"}`, while the driver seeds from `prereg_sha256`. The run definition can therefore contain a seed specification that contradicts its draws. Reject a conflicting anchor or record the effective anchor unambiguously. Using `prereg_sha256` as the §8 preregistration hash is otherwise consistent with the recorded file hash.

- **DR2-3 — NON-BLOCKING — [tests/unit/test_calibration_rundef.py:630](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_rundef.py:630).** The changed-plan test changes both the replication count and the cell list. It would still refuse the second definition if count binding broke. Keep the cells identical and change only the count.

The spawn path re-executes the driver as `__mp_main__`, with `sys.modules["__main__"]` pointing to that module. Bytecode settings precede engine imports; each worker gates before `chunks.run`; a worker exception prevents a success return. The namespace, K=1 fields, bit-pattern encoding, and chunk binding appear correct. Focused pytest could not collect tests because the read-only sandbox has no writable temporary directory.
