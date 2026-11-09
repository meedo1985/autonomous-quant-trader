"""R-14a confirmation module, slice 5b: the C-14 CPCV diagnostic report
(Annex C C-14; protocol_v1.yaml l.215-222; DESIGN §5.4). Synthetic data only
(the screen tests' path and trial fixtures)."""

from __future__ import annotations

import ast
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

import aqt.metrics.statistics as st
from aqt.backtest.costs import (
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
)
from aqt.backtest.event_contract import run_event_contract
from aqt.features.columns import feature_columns
from calibration import c2_confirmation as cf
from calibration import screen

ROOT = Path(__file__).resolve().parents[2]
ON = cf.Gate(cf.PASS, None, {"ess": 250.0})


# --- groups, splits, paths ----------------------------------------------------


def test_groups_are_chronological_with_the_remainder_first() -> None:
    assert cf.cpcv_groups(30) == [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20),
                                  (20, 24), (24, 27), (27, 30)]  # fmt: skip
    assert cf.cpcv_groups(8) == [(g, g + 1) for g in range(8)]
    assert cf.cpcv_groups(1247)[-1] == (1092, 1247)
    with pytest.raises(screen.TrialError, match="8 window days"):
        cf.cpcv_groups(7)


def test_the_28_splits_are_lexicographic() -> None:
    splits = cf.cpcv_splits()
    assert len(splits) == 28 == len(set(splits))
    assert splits == sorted(splits)
    assert splits[0] == (0, 1) and splits[-1] == (6, 7)


def test_every_split_lies_on_exactly_one_path_through_both_its_groups() -> None:
    seen: list[tuple[int, int]] = []
    for p in cf.CPCV_PATHS:
        per_group = cf.cpcv_path_splits(p)
        assert all(g in s for g, s in enumerate(per_group))
        assert len(set(per_group)) == 4  # each split serves its two groups
        seen += sorted(set(per_group))
    assert sorted(seen) == cf.cpcv_splits()
    assert cf.cpcv_path_splits(1)[:2] == [(0, 1), (0, 1)]


def test_training_rows_purge_and_embargo() -> None:
    t0 = datetime(2022, 1, 1, tzinfo=UTC)
    times = [t0 + timedelta(days=k) for k in range(20)]
    w1 = t0 + timedelta(days=20)
    test = [(t0 + timedelta(days=5), t0 + timedelta(days=8))]  # days 5, 6, 7
    # H = 48 h: day 4's label [4, 6) meets the test group, day 3's [3, 5) does
    # not; embargo 2 days drops days 8, 9; the last day's label is unrealised
    rows = cf.cpcv_training_rows(times, test, 48, 2, w1)
    assert rows == [0, 1, 2, 3, *range(10, 19)]
    assert cf.cpcv_training_rows(times, test, 24, 0, w1) == [
        *range(5), *range(8, 20)
    ]  # fmt: skip
    two = [*test, (t0 + timedelta(days=12), t0 + timedelta(days=14))]
    assert cf.cpcv_training_rows(times, two, 24, 1, w1) == [
        0, 1, 2, 3, 4, 9, 10, 11, *range(15, 20)
    ]  # fmt: skip


# --- the switch ---------------------------------------------------------------


def test_below_250_effective_decisions_nothing_is_computed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)

    def no(*_: object, **__: object) -> None:
        raise AssertionError("computed")

    monkeypatch.setattr(cf, "feature_columns", no)
    off = cf.Gate(cf.FAIL, None, {"ess": 249.99})
    got = cf.cpcv_report(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0, off)
    assert got == {"role": "diagnostic_only", "status": "CPCV not enabled",
                   "ess": 249.99}  # fmt: skip
    # a PASSing G-12 below 250 is still off: the switch is ESS, not the gate
    passing = cf.Gate(cf.PASS, None, {"ess": 120.0})
    got = cf.cpcv_report(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0, passing)
    assert got["status"] == "CPCV not enabled"
    gone = cf.Gate(cf.UNAVAILABLE, "ZERO_VARIANCE", {})
    got = cf.cpcv_report(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0, gone)
    assert got == {"role": "diagnostic_only", "status": "UNAVAILABLE",
                   "reason": "ZERO_VARIANCE"}  # fmt: skip


def test_inputs_are_checked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    path = ts._screen_path()
    with pytest.raises(screen.TrialError, match="path length"):
        cf.cpcv_report(trial, path[:-1], ts.W0, ts.WINDOW_H, 0, ON)
    with pytest.raises(screen.TrialError, match="estimator_seed"):
        cf.cpcv_report(trial, path, ts.W0, ts.WINDOW_H, 2**31, ON)
    unbound = {**trial, "family": "vol", "sigma": "HAR_RV"}
    got = cf.cpcv_report(unbound, path, ts.W0, ts.WINDOW_H, 0, ON)
    assert (got["status"], got["reason"]) == ("UNAVAILABLE", "SIGMA_UNBOUND")


# --- a non-model trial ----------------------------------------------------------


def _independent(trial: dict[str, Any], path: Any) -> tuple[float, float]:
    """C-14 (3)-(4) written out for a trial without a model or overlay: every
    group from flat with the window's targets, the window's benchmark."""
    warmup = trial["warmup_hours"]
    series = screen.path_series(path, 0, ts.W0 - timedelta(hours=warmup))
    first, columns = feature_columns(series)
    sigma = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    closes = [b.close for b in series.bars]
    signal = screen.load(trial["signal"], trial["signal_sha256"])
    targets, _ = screen.leg_targets(trial, signal, None, columns, first, closes,
                                    warmup, ts.WINDOW_H, 0)  # fmt: skip
    cand: list[float] = []
    for a, b in cf.cpcv_groups(ts.WINDOW_H // 24):
        run = run_event_contract(series, targets[24 * a : 24 * b], warmup + 24 * a,
                                 sigma_bps=sigma)  # fmt: skip
        cand += screen.daily_returns(run)
    bench = screen.daily_returns(run_event_contract(
        series, screen.benchmark_targets(columns, first, warmup, ts.WINDOW_H), warmup,
        sigma_bps=sigma))  # fmt: skip
    stats = st.paired_sharpe_statistics(cand, bench)
    assert stats.paired_sharpe_improvement is not None
    assert stats.difference_series_sharpe.scaled is not None
    return stats.paired_sharpe_improvement, stats.difference_series_sharpe.scaled


def test_a_non_model_trial_restarts_every_group_flat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    path = ts._screen_path()
    got = cf.cpcv_report(trial, path, ts.W0, ts.WINDOW_H, 0, ON)
    assert got["role"] == "diagnostic_only" and got["status"] == "COMPUTED"
    assert got["groups"][0] == ["2022-01-01T00:00:00Z", "2022-01-05T00:00:00Z"]
    assert got["groups"][-1] == ["2022-01-28T00:00:00Z", "2022-01-31T00:00:00Z"]
    improv, diff = _independent(trial, path)
    assert [p["path"] for p in got["paths"]] == list(range(1, 8))
    for p in got["paths"]:  # no fit: every path is the same
        assert (p["E-IMPROV"], p["E-DIFF"], p["reason"]) == (improv, diff, None)
    assert got["summaries"] == {
        "E-IMPROV": {"median": improv, "p05": improv},
        "E-DIFF": {"median": diff, "p05": diff},
    }
    # the flat restarts matter: the continuous baseline pair differs
    d = cf.baseline_d(trial, path, ts.W0, ts.WINDOW_H, 0)
    assert st.sharpe(d).scaled != diff


def test_each_group_gets_a_fresh_overlay_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    code = (
        "def o(t, m, state):\n"
        "    state['n'] = state.get('n', 0) + 1\n"
        "    return 0.0 if state['n'] <= 24 else t\n"
    )
    digest = ts._module(tmp_path, monkeypatch, "cpcv_overlay", code)
    trial = ts._screen_trial(tmp_path, monkeypatch, overlay="cpcv_overlay:o",
                             overlay_sha256=digest)  # fmt: skip
    runs: list[list[float]] = []
    real = run_event_contract

    def spy(series: Any, targets: Any, start: int, **kw: Any) -> Any:
        runs.append(list(targets))
        return real(series, targets, start, **kw)

    monkeypatch.setattr(cf, "run_event_contract", spy)
    got = cf.cpcv_report(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0, ON)
    assert got["status"] == "COMPUTED"
    groups = runs[1:]  # the first run is the window benchmark
    assert len(groups) == 8  # a non-model trial runs each group once
    assert all(t[:24] == [0.0] * 24 and any(t[24:]) for t in groups)


# --- a model trial ------------------------------------------------------------


def test_a_model_trial_fits_once_per_split_without_its_test_groups(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._model_trial(tmp_path, monkeypatch)
    seeds: list[int] = []
    real_build = screen.build_model

    def build(cls: str, params: Any, seed: int) -> Any:
        seeds.append(seed)
        return real_build(cls, params, seed)

    kept: list[tuple[list[tuple[datetime, datetime]], list[datetime]]] = []
    real_rows = cf.cpcv_training_rows

    def rows(times: Any, test: Any, hours: int, e: int, w1: datetime) -> list[int]:
        out = real_rows(times, test, hours, e, w1)
        kept.append((list(test), [times[i] for i in out]))
        return out

    monkeypatch.setattr(screen, "build_model", build)
    monkeypatch.setattr(cf, "cpcv_training_rows", rows)
    got = cf.cpcv_report(trial, ts._long_path(), ts.W0, ts.WINDOW_H, 7, ON)
    assert got["status"] == "COMPUTED"
    assert seeds == [7] * 28  # one fit per split, the nominee's estimator seed
    groups = cf.cpcv_groups(ts.WINDOW_H // 24)
    tested = sorted(
        tuple(groups.index(((s - ts.W0).days, (e - ts.W0).days)) for s, e in test)
        for test, _ in kept
    )
    assert tested == cf.cpcv_splits()
    for test, times in kept:  # training is window days outside the test groups
        assert times and all(ts.W0 <= t for t in times)
        assert not any(s <= t < e for t in times for s, e in test)
    values = [p["E-DIFF"] for p in got["paths"]]
    assert None not in values and len(set(values)) > 1  # the splits differ
    assert got["summaries"]["E-DIFF"] == {
        "median": st.type_seven_quantile(values, 0.5),
        "p05": st.type_seven_quantile(values, 0.05),
    }


def test_one_failed_split_makes_its_path_and_the_summaries_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._model_trial(tmp_path, monkeypatch)
    calls = {"n": 0}
    real_build = screen.build_model

    def build(cls: str, params: Any, seed: int) -> Any:
        calls["n"] += 1
        if calls["n"] == 1:  # the first fit is split (0, 1), on path 1 only
            raise RuntimeError("library failure")
        return real_build(cls, params, seed)

    monkeypatch.setattr(screen, "build_model", build)
    got = cf.cpcv_report(trial, ts._long_path(), ts.W0, ts.WINDOW_H, 0, ON)
    first, *rest = got["paths"]
    assert (first["E-IMPROV"], first["E-DIFF"], first["reason"]) == (
        None, None, "MODEL_FIT_ERROR"
    )  # fmt: skip
    assert all(p["E-DIFF"] is not None and p["reason"] is None for p in rest)
    assert got["summaries"] == {"E-IMPROV": {"result": "UNAVAILABLE"},
                                "E-DIFF": {"result": "UNAVAILABLE"}}  # fmt: skip


# --- role: nothing reads the report ---------------------------------------------


def test_no_code_path_reads_the_report() -> None:
    # C-14 (5): no gate, screen, mapping, DSR test, nomination or promotion
    # reads it; slice 6 only writes it to the record
    users = []
    for f in [*ROOT.joinpath("calibration").rglob("*.py"),
              *ROOT.joinpath("src").rglob("*.py")]:  # fmt: skip
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            name = getattr(node, "id", None) or getattr(node, "attr", None)
            if name == "cpcv_report":  # any reference other than its def
                users.append(f.name)
    assert users == []
