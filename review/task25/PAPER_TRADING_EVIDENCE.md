# Task 25: paper-trading acceptance run and evidence packet

Date: 2026-09-28. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`), on the
owner's instruction ("let make task 25 and let astra agent make the review").
Branch: `task25-drills-evidence`, on `main` at `a1832f5` (Tasks 13-24 merged).

This packet closes the paper-trading roadmap. It shows that the app runs and
that its safety drills behave as specified. **It is not evidence of an
edge.** A simulated run on exploration data says nothing about future
returns.

## 1. How it was produced

```
python scripts/run_drills.py --config configs/paper_trading.example.toml \
    --raw data/raw --out review/task25/drills
```

- Adapter: the deterministic simulator only. No credentials, no network, no
  exchange call, no confirmation or lockbox data.
- Data: BTCUSDT exploration partition, Task 14 manifest
  `5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b`. The raw
  archives are not committed (`data/raw/` is ignored); the manifest hash
  identifies them.
- Window: 2020-07-06 to 2020-11-29, inside the longest unbroken run of bars
  (2020-06-28 to 2020-11-30). The clean and HALT drills use all of it; the
  others use its first 30 days (to 2020-08-05).
- The script refuses a non-empty output directory and never clears an
  earlier attempt's logs (A25-3). The first committed outputs (commit
  `01f10ad`) were removed with `git rm` and regenerated after the Astra
  review; they remain in git history.
- Configuration: `configs/paper_trading.example.toml`. Owner-set values:
  S-1 0.05% price limit, S-2 2-minute approvals, T21-Q1, T22-Q1, T23-Q1,
  T23-Q2, S-5 health limits. The exchange filters are still `[OPEN]` example
  values.
- Every drill writes its report, hash-chained operations log and incident
  log under `review/task25/drills/<drill>/`; `summary.json` lists each
  drill's expected and observed outcome. Result: **6 of 6 drills met their
  expected outcome.**

## 2. Section 23 reporting

| Item | Value |
| --- | --- |
| Raw decisions | 3,504 hourly decisions; 146 scheduled (00:00 UTC) decisions; 2 governor authorizations; 2 orders; 3,502 refusals (`INSIDE_REBALANCE_BAND`). Bar count is not sample size. |
| Overlap factor | Not applicable: no return statistic is estimated or reported. The run is one path of one benchmark. |
| ESS and method | Not computed. No inference is made, so no effective sample size is claimed. |
| Trial counts | **Zero.** Cycle `C1` has not started and no trial is registered. |
| Comparison benchmark | The predictor *is* the frozen benchmark `VOL_TARGET_BUY_AND_HOLD` (owner answer Q5, baseline only). Nothing is compared against it. |
| Costs | The frozen cost model (`cost_model_hash` `3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae`): fee 10 bps per side fallback, plus spread and volatility-scaled slippage (1-15 bps), charged on every simulated fill. |
| Protocol hash | `d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26` |
| Confirmation-period limitations | None was used. Exploration data only; the confirmation and lockbox partitions were not touched. |

Clean-run outcome, for the record only: from 10,000 USDT, final 0.95595 BTC
plus 2,430.77 USDT, mode RUNNING. This is one simulated path of a
buy-and-hold benchmark in 2020, a rising market. It is not a performance
claim.

## 3. The drills

Each excerpt is taken from the drill's `operations.jsonl` (fields shortened).

### 3.1 Clean multi-month run — met

Expected: the full window runs without refusal, no FREEZE.

```
2020-07-06T00:00 STARTUP  INFO  decision START
2020-07-06T00:00 ORDER    INFO  BUY  1.09908 FILLED
2020-11-26T09:00 ORDER    INFO  SELL 0.14313 FILLED
2020-11-29T00:00 SHUTDOWN INFO  mode RUNNING
```

The loop's determinism across two runs is covered by
`test_a_multi_month_run_is_deterministic` (Task 24).

### 3.2 HALT drill — met

Expected: owner HALT on 2020-07-16, over the full window. The clean run
(the control) places an order after that time; with the HALT there is none;
ends in HALT.

```
control (clean): 2020-11-26T09:00 ORDER INFO SELL 0.14313 FILLED
halt:            2020-07-06T00:00 ORDER            INFO     BUY 1.09908 FILLED
                 2020-07-16T00:00 STATE_TRANSITION CRITICAL RUNNING -> HALT OWNER_HALT
                 2020-11-29T00:00 SHUTDOWN         INFO     mode HALT
```

Orders after the HALT: 0, against 1 in the control. The coins are kept
(HALT sells nothing). A first version ran only 30 days, where no order was
due anyway, so it could not tell a working HALT from a broken one (Astra
A25-1). With trading in HALT forced on, this drill now fails (see
`ADJUDICATION.md`).

### 3.3 FLATTEN drill — met

Expected: owner FLATTEN on 2020-07-16. Each logged sell is at most half of
the holding before it, one per hour, and each starts from what the last one
left. Then HALT with a non-negative remainder.

```
2020-07-16T00:00 STATE_TRANSITION CRITICAL RUNNING -> FLATTEN OWNER_FLATTEN
2020-07-16T00:00 ORDER FLATTEN held_before 1.09908 orig_qty 0.54954
2020-07-16T01:00 ORDER FLATTEN held_before 0.54954 orig_qty 0.27477
2020-07-16T02:00 ORDER FLATTEN held_before 0.27477 orig_qty 0.13738
   … 10 steps in all (flatten/steps.json) …
2020-07-16T10:00 STATE_TRANSITION CRITICAL FLATTEN -> HALT FLATTEN_DONE
                 "no sellable step within the bound; BTC left: 0.00108"
```

Largest step: exactly 0.5000 of the holding. 0.00108 BTC is left, because
half of it is below the 5 USDT minimum order. The first version checked
only the remainder, and would have accepted one 100% sell (Astra A25-2). It
now checks every step from the audit log, and a 100% step fails it.

### 3.4 Ambiguous-order drill — met

Expected: the first order times out and its status cannot be read; the
section 21 path ends in FREEZE with one incident; nothing more is sent.

```
2020-07-06T00:00 ORDER            CRITICAL BUY  state FREEZE
2020-07-06T00:00 STATE_TRANSITION CRITICAL RUNNING -> FREEZE AMBIGUOUS_ORDER
                 "aqt-57b008164bd94267260509d7f884a5d0 unknown"
2020-08-05T00:00 SHUTDOWN         INFO     mode FREEZE
```

Orders: 1 for the whole 30 days. Open incidents: 1.

### 3.5 FREEZE-and-reconcile drill — met

The paper loop never leaves FREEZE within a run (leaving it is a human
procedure), so this drill drives the same components directly: the safety
controller, the simulator on the same data, and reconciliation.

Expected: a FLATTEN sell that goes through but whose reply is lost enters
FREEZE; an account check that ignores that order is refused; a check that
looks it up passes and leaves FREEZE for HALT, never straight to trading.

```
2020-07-16T00:00 RUNNING -> FLATTEN OWNER_FLATTEN
2020-07-16T00:00 FLATTEN -> FREEZE  FLATTEN_FAULT "SimulatedTimeout: no response for aqt-flat-770c…"
blind check refused: reconciliation failed: BTC: venue 0.50000, expected 1;
                     USDT: venue 4592.71, expected 0
full check passed=True, resolved=['aqt-flat-770c921e6dc5bd21578cb39ff39']
2020-07-16T01:00 FREEZE -> HALT     FREEZE_EXIT "reconciliation fb4e1129…"
```

The steps are in `freeze_reconcile/steps.json`.

A first version of this drill passed **for the wrong reason**. It gave the
simulator the full gapped history, so the sell was rejected (NO_FILL_BAR) and
the lost reply never happened. The AI found this from the log before
committing. The drill now uses the loop's gap-free window and requires the
FREEZE to come from the timeout and the sell to have filled.
`tests/integration/test_drills.py` guards both.

### 3.6 REFUSE_START drill — met

Expected: a start with the ambiguous drill's incident still open, and a
start with a Binance key variable set, are both refused with no order. The
variable's value is never logged.

```
refuse_start_open_incident: STARTUP CRITICAL REFUSE_START
    "open incidents: e557431089162db5c08239ed2ab2920ebb5b811e9d40928bf900c1ab925f2249"
refuse_start_credential:    STARTUP CRITICAL REFUSE_START
    "credential present: … credential variables are set (BINANCE_API_KEY) …"
```

The variable held a dummy value (`drill-dummy-not-a-key`). The drill checks
that it does not appear in the log. The other REFUSE_START conditions (hash
mismatch, no alert sink, damaged log, data gap, reconciliation mismatch,
health breach, crash marker) are each tested in `tests/integration/test_paper_loop.py`.

## 4. Findings disclosed by this task

- **T25-01. FLATTEN sells were not logged as orders — repaired.** The
  operations log recorded FLATTEN only as mode changes. After Astra's A25-2
  review, the loop (`src/aqt/app/paper_loop.py`) logs each FLATTEN sell
  whose reply arrives as an `ORDER` event with `state FLATTEN`, its
  quantities and the holding it was sized from. This is a change to the
  Task 24 loop, reviewed under Task 25. **Gap (Astra A25R-4):** a FLATTEN
  sell whose reply is lost is not logged as an `ORDER` event or counted in
  `orders_sent`; its client order id is in the FREEZE transition and the
  incident, and trading stops. To be repaired with the Tasks 23-24
  post-merge findings.
- **T25-02. The exchange filters — resolved after the drills.** The
  configured filters were checked against Binance's BTCUSDT exchange
  information of 2026-09-26 and are equal (PR #33,
  `review/exchange-filters/BTCUSDT_FILTERS_2026-09-26.md`); T18-06 does not
  apply to limit orders. The drills ran with these same values. They must be
  re-read on the day before any stage using real prices.

## 5. What is still not satisfied

- **Section 19 is not satisfied for anything beyond paper.** The deployment
  protocol exists only as a draft with open values. No shadow stage has
  begun. No key exists, and no live or testnet order has ever been placed.
- **Section 25** was signed on 2026-09-26, which allowed this paper equity
  curve. The signature authorizes no deployment.
- Cycle `C1` has not started. No hypothesis is preregistered. `D-16`,
  `D-17` and every other statistical binding remain open.
- `L-01` (money at risk) is 0.
- **No live gate is opened by this task.** `KEEP_BLOCKED` and
  `NO_EDGE_FOUND` remain valid and untouched.
