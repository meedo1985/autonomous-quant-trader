"""Development choices of prereg §5 with §13 rev 7g item 3, from decoded
development records (one per replication, as `scripts/d19_run.py` stores
them for family-agnostic cells).

Order: `family_block_rule` (step 1), availability with the 40k escape and
demotion (step 2, §13 item 3), the cap rule (§3.2), `z_crit` (step 3).
`T_min = T_C2` by §13 item 2. The coverage rule (step 4) needs each cell's
O18-4 category from the frozen cell manifest and is not decided here.

Targets: tau at `M` = the candidate manifest's test count (§5: `M_max`,
conservative), each test at its own `N_i`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from calibration import binomial, classifier, reduce

RULES = ("largest", "median")  # tie -> largest (§5 step 1)
Z_SCREEN = 1.96  # §5 step 1
Z_STEP = Decimal("0.001")  # §5 step 3
Z_MAX = Decimal("20.000")  # no qualifying z_crit above this grid end
BOUNDS = {"error": 0.025, "dsr": 0.0035, "u_g": 0.0015}  # prereg §6
HELD_OUT = (20_000, 40_000)  # §13 item 3
CAPPED = "BLOCK_LENGTH_CAPPED"
# I1-6: the targets carry about 1e-9 relative error (lgamma at N = 40k);
# a comparison closer than this is flagged, never decided silently.
MARGIN_MIN = 1e-6


@dataclass(frozen=True, slots=True)
class Rep:
    """One development replication of one cell, for one block rule."""

    reason: str | None  # DSR availability: None = available (A_f)
    z: float | None  # z_f* when available
    u_g: str | None  # None = every U_G gate available


@dataclass
class CellResult:
    cell_id: str
    n: int
    dsr_events: int
    u_g_events: int
    capped: int
    status: str  # "qualifying" | "demoted_availability" | "demoted_cap"
    held_out: int | None  # 20k or 40k when qualifying
    error_events_at_z: int | None = None
    margin: float = float("inf")  # smallest relative |UCB - tau| / tau used
    notes: list[str] = field(default_factory=list)


def _ucb(x: int, n: int) -> float:
    return binomial.upper(x, n, binomial.DEVELOPMENT_CONFIDENCE)


def _within(result: CellResult, ucb: float, tau: float) -> bool:
    """ucb <= tau, recording the relative margin of the comparison (I1-6)."""
    result.margin = min(result.margin, abs(ucb - tau) / tau)
    return ucb <= tau


# Annex B §2.5 order (dsr.evaluate): rules 1-4 stop before the classifier,
# the classifier refuses with UNSUPPORTED_LAW, rules 5-6 can fail after it.
BEFORE_CLASSIFIER = frozenset(
    {"INVALID_SERIES", "ZERO_VARIANCE_COLUMN", "BLOCK_LENGTH_UNAVAILABLE", CAPPED}
)
AFTER_CLASSIFIER = frozenset({"INVALID_REPLICATE", "INVALID_ARITHMETIC"})


def _finite_hex(value: object) -> bool:
    if not isinstance(value, str):
        return False
    number = reduce.decode({"v": value})["v"]
    return number == number and abs(number) != float("inf")


def consistent(record: dict[str, object], bounds: reduce.Bounds) -> str | None:
    """Why a development record cannot have come from `dev_replication`
    with these thresholds, or None (I1-3, I1R-1, I1R-2): each cause code in
    the Annex B order (a rule 1-4 code whatever the classifier says;
    otherwise UNSUPPORTED_LAW iff the classifier refuses; a rule 5-6 code
    only after it accepts); every field is what that return of
    `dsr.evaluate` sets (I1R2-1): an available result has finite z_f*, S0
    and L and nominated the U_G nominee (an integer in range K); a rule 5-6
    refusal has a finite L and nothing else; any other refusal has none of
    them; at K = 1 both rules are one result."""
    values = reduce.decode(record["diagnostics"])
    refused = not classifier.within(values, *bounds)
    for rule in RULES:
        entry = record[rule]
        if not isinstance(entry, dict):
            return f"{rule}: malformed"
        reason = entry["reason"]
        known = BEFORE_CLASSIFIER | AFTER_CLASSIFIER | {"UNSUPPORTED_LAW", None}
        if reason not in known:
            return f"{rule}: unknown cause code {reason!r}"
        if reason not in BEFORE_CLASSIFIER and refused != (reason == "UNSUPPORTED_LAW"):
            return f"{rule}: classifier outcome does not follow from the thresholds"
        if reason is None:
            if not all(_finite_hex(entry[f]) for f in ("z", "s0", "block")):
                return f"{rule}: an available result without finite z, S0 or L"
            j = entry["nominee"]
            if type(j) is not int or not 0 <= j < values["K"]:
                return f"{rule}: an available result without a valid nominee"
            if j != record["nominee"]:
                return f"{rule}: DSR nominee differs from the U_G nominee"
            continue
        if any(entry[f] is not None for f in ("z", "s0", "nominee")):
            return f"{rule}: a refusal carries z, S0 or a nominee"
        has_block = entry["block"] is not None
        if has_block != (reason in AFTER_CLASSIFIER) or (
            has_block and not _finite_hex(entry["block"])
        ):
            return f"{rule}: L does not match the cause code"
    if values["K"] == 1 and record["largest"] != record["median"]:
        return "K = 1: the two rules differ"
    return None


def _passes(rep: Rep, z: float) -> bool:
    """E_f: available and z_f* >= z (P18-6 comparison)."""
    return rep.reason is None and rep.z is not None and rep.z >= z


def block_rule(cells: dict[str, dict[str, list[Rep]]]) -> tuple[str, dict[str, float]]:
    """§5 step 1: the rule with the smaller worst-cell P^_0(E_f) at 1.96."""
    worst = {
        rule: max(
            sum(_passes(r, Z_SCREEN) for r in reps[rule]) / len(reps[rule])
            for reps in cells.values()
        )
        for rule in RULES
    }
    return min(RULES, key=lambda rule: (worst[rule], RULES.index(rule))), worst


def targets(m: int) -> dict[int, dict[str, dict[str, float]]]:
    """tau per test kind at each held-out N."""
    return {n: binomial.targets(m, BOUNDS, n) for n in HELD_OUT}


def availability(
    cell_id: str, reps: list[Rep], tau: dict[int, dict[str, dict[str, float]]]
) -> CellResult:
    """§13 item 3 step 2 and the §3.2 cap rule for one cell."""
    n = len(reps)
    dsr_events = sum(r.reason is not None for r in reps)
    u_g_events = sum(r.u_g is not None for r in reps)
    capped = sum(r.reason == CAPPED for r in reps)
    result = CellResult(cell_id, n, dsr_events, u_g_events, capped, "", None)
    tau_dsr = tau[20_000]["dsr"]["tau"]
    if not _within(result, _ucb(capped, n), tau_dsr / 4):
        result.status = "demoted_cap"
        return result
    if not _within(result, _ucb(dsr_events, n), tau_dsr):
        result.status = "demoted_availability"
        result.notes.append("DSR availability")
        return result
    u_g = _ucb(u_g_events, n)
    for held_out in HELD_OUT:
        if _within(result, u_g, tau[held_out]["u_g"]["tau"]):
            result.status, result.held_out = "qualifying", held_out
            return result
    result.status = "demoted_availability"
    result.notes.append("U_G")
    return result


def allowed(n: int, tau: float) -> int:
    """The largest event count whose 90% UCB at `n` is within `tau`, or -1
    (the UCB rises with the count)."""
    lo, hi = -1, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _ucb(mid, n) <= tau:
            lo = mid
        else:
            hi = mid - 1
    return lo


def z_crit(
    qualifying: dict[str, list[Rep]], tau_error: dict[str, float]
) -> Decimal | None:
    """§5 step 3: the smallest z on the 0.001 grid at which every qualifying
    cell's 90% UCB of P_0(E_f) is within its tau_err (at the cell's N_i).
    The decimal is compared as its nearest binary64 (P18-6). None if no grid
    value up to Z_MAX qualifies."""
    limit = {c: allowed(len(reps), tau_error[c]) for c, reps in qualifying.items()}

    def ok(z: Decimal) -> bool:
        value = float(z)
        return all(
            sum(_passes(r, value) for r in reps) <= limit[c]
            for c, reps in qualifying.items()
        )

    lo, hi = 0, int(Z_MAX / Z_STEP)  # events fall as z rises: monotone
    if not ok(hi * Z_STEP):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid * Z_STEP):
            hi = mid
        else:
            lo = mid + 1
    return (lo * Z_STEP).quantize(Z_STEP)


def choose(cells: dict[str, dict[str, list[Rep]]], m: int) -> dict[str, object]:
    """Steps 1-3 in order, as a JSON-ready report. `cells`: per cell id, the
    replications under each block rule; `m`: the candidate manifest's test
    count."""
    rule, worst = block_rule(cells)
    tau = targets(m)
    results = {c: availability(c, reps[rule], tau) for c, reps in cells.items()}
    qualifying = {
        c: cells[c][rule] for c, r in results.items() if r.status == "qualifying"
    }
    tau_error = {
        c: tau[r.held_out]["error"]["tau"]
        for c, r in results.items()
        if r.held_out is not None
    }
    chosen = z_crit(qualifying, tau_error) if qualifying else None
    for c, reps in qualifying.items():
        a = allowed(len(reps), tau_error[c])
        for x in (a, a + 1):  # the two counts the limit sits between
            if 0 <= x <= len(reps):
                _within(results[c], _ucb(x, len(reps)), tau_error[c])
        if chosen is not None:
            results[c].error_events_at_z = sum(_passes(r, float(chosen)) for r in reps)
    margin = min((r.margin for r in results.values()), default=float("inf"))
    return {
        "family_block_rule": rule,
        "worst_cell_rate_at_1.96": worst,
        "m": m,
        "targets": tau,
        "cells": {c: vars(r) for c, r in sorted(results.items())},
        "z_crit": None if chosen is None else str(chosen),
        # I1R-4: never read as a choice when a comparison is too close
        "status": "ok" if margin >= MARGIN_MIN else "margin_failed",
        "qualifies_before_coverage": chosen is not None and margin >= MARGIN_MIN,
        "smallest_margin": margin,
        "margin_ok": margin >= MARGIN_MIN,
    }
