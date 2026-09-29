# Task 25 review of `01f10ad` (OpenAI Codex, GPT-6 Astra requested)

Date: 2026-09-28

- Requested by the owner ("let astra agent make the review").
- Invocation: `codex exec -s read-only -m gpt-6-astra - < t25_astra_prompt.md`
  (Codex CLI v0.157.1). The CLI header recorded `model: gpt-6-astra`,
  `provider: openai`, `sandbox: read-only`, `reasoning effort: high`. The
  model itself reports only the GPT-6 family (quoted below), so the exact
  Astra variant is not independently certified.
- Implementation: Claude Opus 5.5. Different provider and model family.
- The reviewer's final message follows verbatim.

---

**Verdict: FIX.** The committed outputs reproduce, but two drills can pass with the behavior they claim to test broken, and reruns erase prior incident evidence.

Reviewer: Codex, GPT-6 family. GPT-6 Astra was requested; this interface does not expose exact serving-model metadata, so I cannot independently certify the Astra variant.

Reviewed commit: `01f10ad875d771b74b675cb95edb5cfd39239146`, against `main` at `a1832f55a5298e3d691a988bea8f79345af5187e`.

All reproductions below used `rtk proxy .venv/Scripts/python.exe -B -` with an inline harness. Output files were redirected to memory; mutations affected only the running Python process. No repository files were changed, and no network, credentials, confirmation, or lockbox data were used.

**A25-1 — BLOCKER: HALT passes when trading in HALT is enabled.**

Evidence: [scripts/run_drills.py:130](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/run_drills.py:130), especially the acceptance predicate at line 138; packet lines 73–83.

The drill checks final mode and absence of orders after HALT, but its window contains no subsequent order opportunity. The clean run’s next order occurs on November 26, beyond the HALT drill’s August 5 endpoint.

Reproduced on the actual exploration data by replacing `SafetyController.may_trade` with:

```python
lambda self: self.mode in (Mode.RUNNING, Mode.HALT)
```

Output:

```text
HALT_GATE_BYPASSED: passed=True
orders after HALT 0, final HALT
scheduled 30
refusals {'INSIDE_REBALANCE_BAND': 719}
```

Thus, governor inactivity masks a broken HALT gate. Use a control run proving an order would occur after the HALT timestamp, then demonstrate its suppression. Extending this drill through the existing November order is one concrete option.

**A25-2 — BLOCKER: FLATTEN’s remainder check does not establish bounded selling.**

Evidence: [scripts/run_drills.py:147](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/run_drills.py:147), particularly lines 158–162; packet lines 87–97.

The predicate checks the final remainder and transition to HALT. Selling everything in one oversized step also satisfies it. No committed per-step quantities establish the claimed 50% bound.

Reproduced by wrapping `SafetyController.tick` to substitute `max_step_fraction=Decimal(1)` while leaving the drill configuration at `0.5`.

Actual-data output:

```text
FLATTEN_100_PERCENT: passed=True
final HALT, BTC left 0.00000
sells [('1.09908', '1.09908')]
```

The tuple is `(holding before step, quantity sold)`: the drill accepts selling 100%.

Capture and assert each order’s quantity against its preceding balance, including the configured fraction, hourly step restriction, and nonnegative remainder. Preserve that trace in the evidence packet. T25-01 accurately discloses missing order logs, but deferring logging does not establish this acceptance criterion.

**A25-3 — BLOCKER: rerunning drills deletes prior incident evidence.**

Evidence: [scripts/run_drills.py:94](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/run_drills.py:94), lines 96–99; the same reset occurs at lines 228–230. The documented command reuses `review/task25/drills`.

Before startup verification, the runner unlinks existing operations and incident ledgers. A previous failed attempt’s incident can therefore disappear without reconciliation or closure. This conflicts with §26’s append-only incident requirement. Git preserves committed versions, but uncommitted failed-run evidence is lost.

Reproduced entirely in memory by opening a `PRIOR_DRILL_FAILURE` incident, then calling `_Runner.run("probe", ...)` on that same output path:

```text
BEFORE incident entries 1
AFTER RUNNING refused () prior incident exists False
```

Require a fresh output directory or preserve separate attempt directories. Do not silently delete existing evidence.

The acceptance assessment is:

| Drill | Assessment |
|---|---|
| Clean multi-month run | **Met** |
| HALT | **Not met** — A25-1 |
| FLATTEN | **Not met** — A25-2 |
| FREEZE-and-reconcile | **Met**, within its disclosed controller-level scope |
| Ambiguous order | **Met** |
| REFUSE_START | **Met** |

The positive checks are substantial:

- The fresh execution reproduced all **18 committed drill artifacts**: all 11 ledger files matched byte-for-byte; report and step JSON matched; the generated summary matched `summary.json`.
- All **11 committed ledgers** have intact hash chains.
- The ambiguous fault targets exactly `aqt-57b008164bd94267260509d7f884a5d0`, matching the recorded order.
- The credential drill genuinely checks non-echo: an in-memory mutation that included the dummy value in the refusal message changed its result from passing to failing. The actual credential report, operations log, and summary contain no dummy value.
- FREEZE recovery uses the reviewed simulator, controller, and reconciliation functions. The lost-reply sell fills, blind reconciliation fails, full reconciliation resolves the order, and recovery ends in HALT. Its exclusion from the paper loop is honestly disclosed.
- The §23 table covers the required reporting fields without presenting bars as sample size or claiming edge. Uncomputed ESS and inapplicable overlap are explicit. Sections 19 and 25 plainly open no live gate.
- T25-02 correctly identifies the filters as examples. It remains a disclosed limitation of simulator evidence.

Validation performed:

| Command/check | Result |
|---|---|
| `ruff check --no-cache .` | Passed |
| `ruff format --check --no-cache .` | 101 files formatted |
| `python -B -m mypy --no-incremental --cache-dir=nul src scripts` | Passed, 53 files |
| `lint-imports --no-cache --no-logo` | 6 kept, 0 broken |
| `git diff --check main task25-drills-evidence` | Passed |
| Frozen verification | 29 baseline blobs unchanged; 14 sidecars, Constitution self-hash, manifest and protocol bindings passed |
| No-file Task 25 pytest test, with `-s -p no:cacheprovider` | 1 passed |
| Both Task 25 test functions using memory-backed output | Passed |

The full pytest suite was **not independently rerun**: default capture failed because the sandbox has no writable temporary directory. The committed `1575 passed, 4 skipped` result remains the author’s validation record.

Worktree remained clean. This final message is the review record; it has not been committed. Human §16 approval remains outstanding.
