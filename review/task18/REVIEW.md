Model: GPT-6 Astra — independent adversarial reviewer.

Checks were not rerun by me. All supplied check output was produced by the implementer, Claude Opus 5.5, at `cbde71d`. This review uses only the supplied diff and context.

**R-1 — BLOCKER — `src/aqt/execution/simulator.py:246`**
`quantize(step_size)` rounds to the step's decimal exponent, not to a multiple of the step. With the snapshot-shaped step `0.00001000`, quantity `0.5`, and fill fraction `0.3333`, execution becomes `0.16665000`; with numerically equivalent step `0.00001`, it becomes `0.16665`. More decisively, fraction `0.33333333` produces `0.16666666` with the snapshot-shaped step, violating the `0.00001` increment. The simulator credits an invalid executed quantity. Round down the number of step units, then multiply by the step; test trailing-zero and non-power-of-ten increments.

**R-2 — BLOCKER — `src/aqt/execution/simulator.py:263`**
Balance validation checks only the scripted executed quantity. With BTC balance `0.2`, a sell request for `0.3` and `fill_fraction=0.5` succeeds, selling `0.15`. This contradicts the stated rejection of sells above the free base balance and lets an executor's oversized order pass the test double. Validate the requested sell quantity against available inventory before applying the partial-fill fault; add this combination to the balance tests.

**R-3 — BLOCKER — `src/aqt/execution/simulator.py:260`**
Balance arithmetic uses the caller's decimal context despite `_DEC` being explicit elsewhere; `quantize` also uses that ambient context. Run the supplied `0.5` BTC buy inside `localcontext()` with precision `6`: the resulting USDT balance is `949.434`, versus `949.43435` under the default context, while recorded notional and cost remain `50.5` and `0.06565`. Thus the ledger no longer reconciles with its recorded fill, and identical inputs produce different results. Use one explicit context throughout quantity rounding and ledger arithmetic, and verify reconciliation under differing caller contexts.

**R-4 — BLOCKER — `src/aqt/execution/simulator.py:104`**
The advertised `NOTIONAL` reader retains only `minNotional`, dropping the maximum and market-applicability fields. A supplied `NOTIONAL` filter with minimum `10`, maximum `40`, and `applyMaxToMarket=true` still permits the fixture's `0.5` buy: decision notional is `50`, and fill notional is `50.5`. This violates the supplied cap despite the report claiming `NOTIONAL` enforcement. Preserve and enforce the supported market bounds and applicability flags, or explicitly reject unsupported filter configurations.

Deviation assessment:

- **T18-01:** Acceptable for the stated market-only scope.
- **T18-02:** Acceptable; explicit filter inputs avoid silently assigning contemporary rules to historical bars.
- **T18-03:** Acceptable as a disclosed bar-resolution approximation. Calling decision close a “causal equivalent” overstates it: causality does not establish equivalence to a recent average.
- **T18-04:** Acceptable as the explicitly required simulator idempotency contract. It provides no evidence that venue retries are safe; actual Binance reuse behavior remains unverified in this review.

Verdict: **FIX**.