# Synthetic readiness audit adjudication

Date: 2026-09-19

| ID | Decision | Evidence and disposition |
|---|---|---|
| T12R-01 | AGREE | Replaced aliased tuple snapshots with independent scalar tuples for every bar and target. |
| T12R-02 | AGREE | Synthetic bars now have distinct valid open, close, high, and low values, so the execution-price assertion distinguishes the next open. |
| T12R-03 | AGREE | Increased the short-cycle synthetic amplitude, asserted vol-target differs from buy-and-hold, asserted interior exposures, and proved at least one inside-band hold. |
| T12R-04 | AGREE | Added scheduled-increase and intraday-reduction invariants plus the no-trade CASH path. |
| T12R-05 | AGREE | Kept the intentional 16-day minimum boundary but now asserts the minimum explicitly and records positive long-run variance and an available block length before accepting the interval. |
| T12R-06 | AGREE | Added a positive control proving the mutated series differs before prefix equality is accepted. |
| T12R-07 | PARTIAL | Renamed the test to its exact post-import scope and added `io.open`, `os.system`, `os.popen`, and `socket.getaddrinfo` tripwires. It does not claim to intercept import-time access or every possible API. |
| T12R-08 | AGREE | Added specific message matching, a truncated next-open failure, and a noncanonical stream-identity rejection. |
| T12R-09 | AGREE | The result report identifies the benchmark-to-engine-to-metrics path as the new evidence and does not claim the repeated unit properties as new. |
| T12R-10 | PARTIAL | Local Windows timing is recorded. GitHub CI is required after push; no cross-platform performance threshold is introduced. |
| T12R-11 | AGREE | Added this adjudication, the Claude record, and `LOCAL_REPORT.md`. |
| T12R-12 | AGREE | Renamed the sole decision record to `OD-T12R-001`. |
| T12R-13 | AGREE | The result record states that symbol, dates, prices, and seed are synthetic/API labels, with no registry or trial record. |
| T12R-14 | AGREE | Replaced count literals with `_DECISION_COUNT` and renamed the evaluated paths `vol_target` and `buy_and_hold`. |
| T12R-15 | AGREE | Local commands were rerun after every correction; exact final outcomes are recorded below. Claude's limitation remains explicit. |

No production source, frozen artifact, accepted oracle/canary, schema, protocol,
or scientific convention changed. No blocker remains.
