"""D-19 development choices (prereg §5 with §13 rev 7g item 3) on
synthetic development records: block rule, availability with the 40k
escape and demotion, the cap rule, and z_crit on the 0.001 grid."""

from __future__ import annotations

import struct
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


def _h(value: float) -> str:
    return struct.pack(">d", value).hex()


def _record(
    reason: str | None, nominee: int, u_g_nominee: int, *, k: float = 1.0,
    z: float | None = 2.0,
) -> dict[str, object]:  # fmt: skip
    """A whole record as dev_replication writes it for this cause code
    (I1R2-1, I1R3-2): z, S0 and a nominee only when available; L from rule 5
    on; max L/T from rule 4 on; per-column lengths from rule 3 on; per-column
    checks matching rules 1-2; a missing length for rule 3, a cap for rule 4."""
    available = reason is None
    has_lengths = reason not in choices.NO_LENGTHS
    entry = {
        "reason": reason,
        "nominee": nominee if available else None,
        "z": None if z is None or not available else _h(z),
        "s0": _h(0.1) if available else None,
        "block": _h(3.0) if available or reason in choices.AFTER_CLASSIFIER else None,
        "length_ratio": _h(0.05)
        if has_lengths and reason != "BLOCK_LENGTH_UNAVAILABLE"
        else None,
    }
    n = int(k)
    checks: list[list[bool | None]] = [[True, True] for _ in range(n)]
    if reason == "INVALID_SERIES":
        checks[0] = [False, None]
    if reason == "ZERO_VARIANCE_COLUMN":
        checks[0] = [True, False]
    columns: list[list[object]] | None = (
        [[_h(3.0), False] for _ in range(n)] if has_lengths else None
    )
    if columns is not None and reason == "BLOCK_LENGTH_UNAVAILABLE":
        columns[0][0] = None
    if columns is not None and reason == choices.CAPPED:
        columns[0][1] = True
    return {
        "diagnostics": {"K": _h(k), "T": _h(9.0), "g": _h(0.5)},
        "largest": entry,
        "median": dict(entry),
        "nominee": u_g_nominee,
        "columns": columns,
        "column_checks": checks,
    }


@pytest.fixture
def toy_classifier(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(choices.classifier, "within", lambda v, u, lo: v["g"] <= u["g"])


ACCEPTS, REFUSES = ({"g": 1.0}, {}), ({"g": 0.0}, {})


@pytest.mark.usefixtures("toy_classifier")
def test_a_record_must_follow_from_its_thresholds_and_nominee() -> None:
    """I1-3, I1R-1: the classifier outcome, the Annex B order of cause
    codes, the fields of an available result, and the nominee."""
    for code in choices.BEFORE_CLASSIFIER:  # rules 1-4 stop first, either way
        assert choices.consistent(_record(code, 0, 0), ACCEPTS) is None
        assert choices.consistent(_record(code, 0, 0), REFUSES) is None
    for code in choices.AFTER_CLASSIFIER:  # rules 5-6 only after acceptance
        assert choices.consistent(_record(code, 0, 0), ACCEPTS) is None
        assert "classifier" in str(choices.consistent(_record(code, 0, 0), REFUSES))
    assert choices.consistent(_record(None, 0, 0), ACCEPTS) is None
    assert choices.consistent(_record("UNSUPPORTED_LAW", 0, 0), REFUSES) is None
    assert "classifier" in str(choices.consistent(_record(None, 0, 0), REFUSES))
    unsupported = _record("UNSUPPORTED_LAW", 0, 0)
    assert "classifier" in str(choices.consistent(unsupported, ACCEPTS))
    assert "nominee" in str(choices.consistent(_record(None, 1, 0), ACCEPTS))
    assert "z does not match" in str(
        choices.consistent(_record(None, 0, 0, z=None), ACCEPTS)
    )
    nan_z = _record(None, 0, 0, z=float("nan"))
    assert "z does not match" in str(choices.consistent(nan_z, ACCEPTS))
    assert "unknown" in str(choices.consistent(_record("OTHER", 0, 0), ACCEPTS))


def _with(record: dict[str, object], **fields: object) -> dict[str, object]:
    entry = {**record["largest"], **fields}  # type: ignore[dict-item]
    return {**record, "largest": entry, "median": dict(entry)}


@pytest.mark.usefixtures("toy_classifier")
def test_fields_that_dsr_evaluate_cannot_produce_are_refused() -> None:
    """I1R2-1: each corruption of an otherwise valid record is caught."""
    available = _record(None, 0, 0, k=2.0)
    assert choices.consistent(available, ACCEPTS) is None
    for bad in (None, 2, -1, True, "0"):  # not an integer in range K = 2
        both = {**_with(available, nominee=bad), "nominee": bad}
        assert "nominee" in str(choices.consistent(both, ACCEPTS)), bad
    capped = _record(choices.CAPPED, 0, 0)
    assert choices.consistent(capped, ACCEPTS) is None
    for field in ("z", "s0", "block"):
        assert choices.consistent(_with(capped, **{field: _h(1.0)}), ACCEPTS)
    assert choices.consistent(_with(capped, nominee=0), ACCEPTS)
    refused = _record("UNSUPPORTED_LAW", 0, 0)
    assert choices.consistent(_with(refused, block=_h(3.0)), REFUSES)
    after = _record("INVALID_REPLICATE", 0, 0)
    assert choices.consistent(after, ACCEPTS) is None
    assert "L does not match" in str(
        choices.consistent(_with(after, block=None), ACCEPTS)
    )
    nan_block = _with(after, block=_h(float("nan")))
    assert "L does not match" in str(choices.consistent(nan_block, ACCEPTS))
    assert choices.consistent(_with(after, z=_h(1.0)), ACCEPTS)


@pytest.mark.usefixtures("toy_classifier")
def test_at_k_1_both_rules_must_be_one_result() -> None:
    """I1R-2: dev_replication reuses one result at K = 1."""
    record = _record(None, 0, 0)
    record["median"] = {**record["median"], "z": _h(2.5)}  # type: ignore[dict-item]
    assert "K = 1" in str(choices.consistent(record, ACCEPTS))
    two = _record(None, 0, 0, k=2.0)
    two["median"] = {**two["median"], "z": _h(2.5)}  # type: ignore[dict-item]
    assert choices.consistent(two, ACCEPTS) is None


def test_a_target_comparison_inside_the_margin_is_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I1-6: every UCB-tau comparison records its margin; too close fails."""
    cells = {"a": {r: _reps(z=[2.5] * 50) for r in choices.RULES}}
    report = choices.choose(cells, 3)
    assert report["margin_ok"] is True and 0 < report["smallest_margin"] < 1
    assert report["status"] == "ok" and report["qualifies_before_coverage"] is True
    monkeypatch.setattr(choices, "MARGIN_MIN", 1.0)
    failed = choices.choose(cells, 3)
    assert failed["margin_ok"] is False and failed["status"] == "margin_failed"
    assert failed["qualifies_before_coverage"] is False  # I1R-4


@pytest.mark.usefixtures("toy_classifier")
def test_outcomes_before_the_block_rule_and_column_fields_must_agree() -> None:
    """I1R3-1, I1R3-2: rule-free outcomes are one result across rules; max
    L/T is rule-free; per-column fields match rules 1-4."""
    for code in (*choices.BEFORE_CLASSIFIER, None, *choices.AFTER_CLASSIFIER):
        valid = _record(code, 0, 0, k=2.0)
        assert choices.consistent(valid, ACCEPTS) is None, code
    early = _record("INVALID_SERIES", 0, 0, k=2.0)
    early["median"] = {**early["median"], "reason": "ZERO_VARIANCE_COLUMN"}  # type: ignore[dict-item]
    assert "before the block rule" in str(choices.consistent(early, ACCEPTS))
    ratio = _record(None, 0, 0, k=2.0)
    ratio["median"] = {**ratio["median"], "length_ratio": _h(0.06)}  # type: ignore[dict-item]
    assert "max L/T differs" in str(choices.consistent(ratio, ACCEPTS))
    refused = _record("UNSUPPORTED_LAW", 0, 0, k=2.0)
    assert choices.consistent(refused, REFUSES) is None
    assert "max L/T" in str(
        choices.consistent(_with(refused, length_ratio=None), REFUSES)
    )
    assert "columns malformed" in str(
        choices.consistent({**refused, "columns": None}, REFUSES)
    )
    series = _record("INVALID_SERIES", 0, 0, k=2.0)
    with_lengths = {**series, "columns": [[_h(3.0), False], [_h(3.0), False]]}
    assert "before rule 3" in str(choices.consistent(with_lengths, ACCEPTS))
    all_finite = {**series, "column_checks": [[True, True], [True, True]]}
    assert "rule 1" in str(choices.consistent(all_finite, ACCEPTS))
    variance = _record("ZERO_VARIANCE_COLUMN", 0, 0, k=2.0)
    no_zero = {**variance, "column_checks": [[True, True], [True, True]]}
    assert "rule 2" in str(choices.consistent(no_zero, ACCEPTS))
    capped = _record(choices.CAPPED, 0, 0, k=2.0)
    uncapped = {**capped, "columns": [[_h(3.0), False], [_h(3.0), False]]}
    assert "rule 4" in str(choices.consistent(uncapped, ACCEPTS))
    missing = _record("BLOCK_LENGTH_UNAVAILABLE", 0, 0, k=2.0)
    complete = {**missing, "columns": [[_h(3.0), False], [_h(3.0), False]]}
    assert "rule 3" in str(choices.consistent(complete, ACCEPTS))
    available = _record(None, 0, 0, k=2.0)
    stray_cap = {**available, "columns": [[_h(3.0), True], [_h(3.0), False]]}
    assert "rule 4" in str(choices.consistent(stray_cap, ACCEPTS))
