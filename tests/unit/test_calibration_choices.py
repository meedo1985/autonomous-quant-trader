"""D-19 development choices (prereg §5 with §13 rev 7g item 3) on
synthetic development records: block rule, availability with the 40k
escape and demotion, the cap rule, and z_crit on the 0.001 grid."""

from __future__ import annotations

from decimal import Decimal

import pytest

from calibration import choices
from calibration.choices import Rep

N = 12_000
TAU = choices.targets(322)


def _reps(
    *, dsr: int = 0, u_g: int = 0, capped: int = 0, z: list[float] | None = None
) -> list[Rep]:
    reps = [Rep(None, -1.0, None) for _ in range(N)]
    for i in range(capped):
        reps[i] = Rep(choices.CAPPED, None, None)
    for i in range(capped, capped + dsr):
        reps[i] = Rep("UNSUPPORTED_LAW", None, None)
    for i in range(u_g):
        reps[-1 - i] = Rep(reps[-1 - i].reason, reps[-1 - i].z, "G-1")
    for i, value in enumerate(z or []):
        reps[N // 2 + i] = Rep(None, value, None)
    return reps


@pytest.mark.parametrize(
    ("u_g", "status", "held_out"),
    [(0, "qualifying", 20_000), (1, "qualifying", 40_000),
     (2, "qualifying", 40_000), (3, "demoted_availability", None)],
)  # fmt: skip
def test_u_g_events_choose_20k_the_40k_escape_or_demotion(
    u_g: int, status: str, held_out: int | None
) -> None:
    """§13 item 3: 0 events need 20k, 1-2 need 40k, 3 or more fail."""
    result = choices.availability("c", _reps(u_g=u_g), TAU)
    assert (result.status, result.held_out) == (status, held_out)


@pytest.mark.parametrize(
    ("dsr", "status"), [(9, "qualifying"), (10, "demoted_availability")]
)
def test_more_than_nine_dsr_events_demote(dsr: int, status: str) -> None:
    """§13 item 3: DSR availability demotes at more than 9 events."""
    assert choices.availability("c", _reps(dsr=dsr), TAU).status == status


@pytest.mark.parametrize(("capped", "status"), [(0, "qualifying"), (1, "demoted_cap")])
def test_the_cap_rule_compares_the_cap_rate_ucb_with_a_quarter_of_tau_dsr(
    capped: int, status: str
) -> None:
    """§3.2: UCB(0 of 12k) = 1.92e-4 <= 3.0e-4 < UCB(1 of 12k) = 3.24e-4."""
    assert choices.availability("c", _reps(capped=capped), TAU).status == status


def test_the_block_rule_with_the_smaller_worst_cell_rate_wins_ties_to_largest() -> None:
    hot = _reps(z=[3.0] * 300)
    cold = _reps(z=[3.0] * 200)
    cells = {
        "a": {"largest": hot, "median": cold},
        "b": {"largest": cold, "median": cold},
    }
    assert choices.block_rule(cells)[0] == "median"
    tie = {"a": {"largest": cold, "median": cold}}
    assert choices.block_rule(tie)[0] == "largest"


def test_z_crit_is_the_smallest_grid_value_meeting_every_cells_target() -> None:
    """Brute force over the grid agrees with the search."""
    zs = [1.5 + i / 400 for i in range(400)]  # 400 available z values above 1.5
    qualifying = {"a": _reps(z=zs), "b": _reps(z=zs[::2])}
    tau = {"a": TAU[20_000]["error"]["tau"], "b": TAU[40_000]["error"]["tau"]}
    chosen = choices.z_crit(qualifying, tau)
    limit = {c: choices.allowed(N, tau[c]) for c in qualifying}

    def ok(z: Decimal) -> bool:
        return all(
            sum(
                r.z is not None and r.reason is None and r.z >= float(z)
                for r in qualifying[c]
            )
            <= limit[c]
            for c in qualifying
        )

    grid = [Decimal(m) / 1000 for m in range(1400, 2600)]
    assert chosen == next(z for z in grid if ok(z))
    assert ok(chosen) and not ok(chosen - choices.Z_STEP)


def test_no_grid_value_means_no_qualifying_choice() -> None:
    reps = _reps(z=[99.0] * 500)
    assert choices.z_crit({"a": reps}, {"a": TAU[20_000]["error"]["tau"]}) is None


def test_choose_reports_every_step() -> None:
    report = choices.choose({"a": {r: _reps(z=[2.5] * 50) for r in choices.RULES}}, 3)
    assert report["family_block_rule"] == "largest"
    assert report["z_crit"] is not None
    assert report["cells"]["a"]["status"] == "qualifying"
