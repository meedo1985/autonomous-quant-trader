# Adjudication of the Fable 5.1 review of PR #44 (FABLE_REVIEW.md)

| ID | Decision | Evidence / repair |
|---|---|---|
| FF44-1 (medium) | Accepted, repaired | Reproduced in the test: a trailing unknown-outcome snapshot followed by a midnight with a close gave 2 returns (pre-send balances used for a midnight after the unknown). `snapshots()` now also returns the time of the first snapshot in a trailing unknown run; `daily_equity_returns(..., until=)` values no midnight after it; `l02_count` passes it. Docstring corrected. Mutation check: with `until` not passed, the new assertion fails (`raw_decisions == 1` gets 2). |
| FF44-2 (low) | Accepted as documented approximation | An unknown resolved later in the same step leaves midnights between send and resolution valued at pre-send balances; bounded by one step. Stated in the `snapshots()` docstring. |
| FF44-3 (low) | Accepted, repaired | The test now asserts `raw_decisions == 1` for the ordinary run, `== 1` with a trailing unknown and a later close, and `== 2` once a known snapshot follows. |

No finding left unrepaired. Checks after repair: `pytest -q` 1787 passed, 9 skipped; `ruff check` and `ruff format --check` clean; `mypy src` clean; `lint-imports` 6 kept.
Re-check: GPT-6 Astra (owner: "if sol not available you can use astra to check", 2026-10-05).
