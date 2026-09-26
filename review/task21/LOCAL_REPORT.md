# Task 21 local implementation and gate report

Date: 2026-09-26
Base commit: `fbc4abc` (`main`)
Branch: `task21-governor`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Roadmap Task 21, approved in `review/roadmap/OWNER_APPROVAL.md`. Its blocking
decision Q2 is answered (`review/roadmap/OWNER_ANSWER_Q2.md`: GPT-6 Astra is the
different-model reviewer). The owner said "ok then conetue" on 2026-09-26 after
the Task 17 pull request was opened; the AI took that as permission to continue
with the next roadmap task, **not** as the owner's review of PR #25.

**Section 16:** the governor is an enumerated protected component. Merging it
requires a different-model review (Astra, per Q2) **and** the owner's own PR
review, recorded before merge.

## Scope

- `src/aqt/governor/authorization.py` (new, 197 lines): `Proposal`,
  `ActualState`, `Authorization`, `Refusal`, `RefusalCode`, `GovernorConfig`.
- `src/aqt/governor/machine.py` (new): `Governor.decide` and
  `Governor.redeem`.
- `tests/unit/test_governor.py` (new, 13 tests).

No existing module, frozen artifact or import contract changed. The existing
contract "Governor cannot reach execution or model training" covers both new
modules.

## Design

- **Rules come from one place.** `decide` calls the frozen rules in
  `aqt.benchmarks.canonical`: `rebalance`, `reaches_rebalance_band` and
  `is_scheduled_decision`. So the governor applies exactly the scheduling,
  band and minimum-hold rules the backtester and benchmarks use. A `HOLD`
  becomes a `Refusal` with a stable code.
- **Actual state only.** `ActualState` holds base quantity, quote balance
  (both including locked amounts), mark price, time, and the last filled
  risk-increase time. There is no intended-state input. The governor keeps no
  exposure of its own, only the nonces it issued and used.
- **Authorization (section 20).** It holds the proposal hash, the
  current-state reference (SHA-256 of the exact state), the symbol, the side,
  the current and target exposure, `max_base_quantity`, `max_slippage_bps`,
  `issued_at`, `expires_at` and a 128-bit random nonce. The quantity bound is
  exact `Decimal`: the base quantity the target implies at the mark price,
  minus the base quantity held.
- **Redeem.** `redeem` refuses an authorization that this governor did not
  issue (including an altered copy), one already used, one expired, or one
  whose state reference no longer matches the actual state. Otherwise it
  marks it used.
- **Refusals, not clipping.** A target outside `[0, 1]`, NaN or infinite is
  refused (`scope.max_exposure_per_asset` 1.0). So are an unknown symbol, a
  symbol mismatch, zero equity, a decision or state from the future, and a
  **stale decision**.

### Deliberate differences and open values

- **T21-01. Roadmap tests 1 and 2 use unreachable times.** Risk increases
  happen only at 00:00 UTC, and `ExposureState` accepts a last-increase time
  only at 00:00. So the time between increases is always a whole number of
  days, and "25h elapsed" and "23h after" cannot occur as written. The tests
  use the reachable equivalents: 03:00 is refused (not scheduled); 00:00 with
  24h elapsed is authorized; 23:00 is refused (not scheduled); a second
  increase at the same 00:00 is refused (minimum hold).
- **T21-02. Stale decisions are refused** (added by the AI; not in the
  roadmap). Without it, a proposal stamped 00:00 but presented at 03:00 was
  authorized as a scheduled risk increase. This was confirmed before the fix
  (`Authorization BUY 0.8` issued at 03:00). A decision is now accepted only
  within one bar of its `decision_time`.
- **T21-03. `max_slippage_bps`, `authorization_ttl` and `decision_window` have
  no defaults.** All are `[OPEN]` values for the owner (the window was added by
  Astra R-1), so `GovernorConfig` requires them. The tests use 15 bps, 5 minutes
  and 10 minutes only as fixtures.
- **T21-04. Nonces live in memory.** After a restart, an earlier authorization
  is refused as `NOT_ISSUED_HERE`, which fails safe. Persistence belongs to the
  executor and paper loop (Tasks 22-24).
- **T21-05. The state reference is exact.** Any change to the state (a new mark
  price or a new `as_of`) makes `redeem` refuse with `STATE_CHANGED`. The
  executor must redeem against the same snapshot it was authorized on, and
  re-ask the governor otherwise.
- **T21-06. Property test without a new dependency.** `hypothesis` is not
  installed, so acceptance test 8 is a seeded random search: 5000 cases,
  asserting that every authorized increase is at 00:00 and at least 24h after
  the last one. More than 50 increases are reached.

## Acceptance criteria (roadmap Task 21)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Increase at 03:00 refused; at 00:00 after the hold, authorized | `test_a_risk_increase_happens_only_at_the_scheduled_decision` (see T21-01) |
| 2 | Increase inside the 24h hold refused | `test_a_risk_increase_inside_the_minimum_hold_is_refused` (see T21-01) |
| 3 | Intraday reduction of 0.09 refused, 0.11 authorized | `test_intraday_reductions_must_reach_the_band` |
| 4 | Target above 1.0 or below 0.0 refused | `test_a_target_outside_0_to_1_is_refused` (also NaN, infinity) |
| 5 | Every section 20 field present; a nonce never repeats | `test_an_authorization_carries_every_section_20_field`, `test_nonces_never_repeat` |
| 6 | An expired authorization is refused at use time | `test_an_authorization_is_single_use_unexpired_and_bound_to_its_state` |
| 7 | After a partial fill, decisions use the actual exposure | `test_after_a_partial_fill_decisions_use_the_actual_exposure` |
| 8 | No input increases exposure outside 00:00 UTC | `test_no_input_increases_exposure_outside_the_scheduled_window` (see T21-06) |

Also: `test_a_stale_scheduled_proposal_cannot_increase_risk_later` (T21-02).

Mutation checks, each failing at least one test: a governor that uses its own
intended exposure (2 fail); no expiry check; no state binding; reusable
authorizations; nonce repeats allowed; no stale-decision check (1 each).

An implementer error was caught by the tests: the first version computed the
quantity bound from float exposures (0.5 - 0.35 gave 1.5000000000000002 BTC).
It now uses exact `Decimal` from holdings.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Result |
| --- | --- |
| `pytest -q` | 1383 passed, 4 skipped in 170.08s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 84 files already formatted |
| `mypy src scripts` | Success: no issues found in 43 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |
| `git diff --check main...HEAD` | clean |

Frozen verification: `git diff --name-only main` lists only the three new
files and this report.

## Outstanding

- GPT-6 Astra review (section 16, Q2): FIX, blockers R-1 (late issue or
  redemption), R-2 (overlapping authorizations) and R-3 (quantity rounding).
  All three were reproduced and repaired; see `REVIEW.md` and
  `ADJUDICATION.md`. The repairs are not re-reviewed.
- The owner's own PR review is required before merge (section 16).
