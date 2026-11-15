"""Slice 6b build B3c: reading and the data manifest (DESIGN_SLICE6B rev 16 §6).
Synthetic bars only (the screen tests' path fixture)."""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

from aqt.data import manifest as dm
from calibration import c2_confirmation as cf
from calibration import screen
from calibration.semi import SYMBOLS

H = timedelta(hours=1)
WARMUP = 4801
EXTRA = 10  # exploration bars before the cut: held, never used
P = "a" * 64
START = ts.W0 - WARMUP * H  # w0 - W
END = ts.W0 + ts.WINDOW_H * H  # w1
SPLIT = ts.W0 - 100 * H  # the warm-up reaches back into exploration
LOCK_END = END + 1000 * H


def _rows() -> tuple[np.ndarray, datetime]:
    rows = ts._screen_path(WARMUP + EXTRA)[:-1]
    return rows, START - EXTRA * H


def _manifest(
    part: str, series: Any, lo: datetime, hi: datetime
) -> dm.PartitionManifest:
    snap = dm.available("f" * 64, lo)
    return dm.build_partition_manifest(
        partition=part, series=series,
        raw_artifacts=(dm.RawArtifact(name=f"{part}.csv", content=b"x"),),
        parser_code_sha256="e" * 64, window_start_utc=lo, window_end_exclusive_utc=hi,
        fees=snap, exchange_filters=snap, symbol_status=snap,
    )  # fmt: skip


def world(
    cycle: str = "c1", protocol: str = P
) -> tuple[Any, dict[Any, Any], np.ndarray]:
    """A composite over exploration [first, SPLIT), confirmation [SPLIT, END),
    a sealed lockbox; the served whole partitions; the rows of the cut."""
    rows, first = _rows()
    k = (SPLIT - first) // H
    served: dict[tuple[str, str], Any] = {}
    parts: list[Any] = []
    for s, sym in enumerate(SYMBOLS):
        for part, lo, hi, chunk in (
            ("exploration", first, SPLIT, rows[:k]),
            ("confirmation", SPLIT, END, rows[k:]),
        ):
            series = screen.path_series(chunk, s, lo)
            served[(part, sym)] = series
            parts.append(_manifest(part, series, lo, hi))
        parts.append(dm.sealed_partition_reference(
            partition="lockbox", symbol=sym, interval_label="1h",
            window_start_utc=END, window_end_exclusive_utc=LOCK_END,
            manifest_sha256="d" * 64))  # fmt: skip
    comp = dm.build_composite_manifest(cycle_id=cycle, protocol_sha256=protocol,
                                       partitions=parts)  # fmt: skip
    return comp, served, rows[EXTRA:]


def decl(comp: Any) -> cf.Declaration:
    return cf.Declaration(
        cycle_id="c1", entries=[], declared={}, trials=[],
        data_manifest_sha256=comp.manifest_sha256, last_seen=START, embargo_days=0,
        anchor_head_hash="0" * 64, anchor_entry_count=0, screen_record_sha256="7" * 64,
    )  # fmt: skip


def read(comp: Any, served: Any, d: cf.Declaration | None = None,
         start: datetime = START) -> np.ndarray:  # fmt: skip
    return cf.check_read(comp, served, decl=d or decl(comp), protocol_hash=P,
                         start=start, end=END)  # fmt: skip


def test_a_true_composite_gives_exactly_the_cut() -> None:
    comp, served, rows = world()
    np.testing.assert_array_equal(read(comp, served), rows)


def test_only_the_confirmation_partition_when_the_warm_up_stays_inside_it() -> None:
    comp, served, rows = world()
    conf = {k: v for k, v in served.items() if k[0] == "confirmation"}
    start = SPLIT
    got = cf.check_read(comp, conf, decl=decl(comp), protocol_hash=P, start=start,
                        end=END)  # fmt: skip
    np.testing.assert_array_equal(got, rows[(SPLIT - START) // H :])


def test_a_cut_that_misses_the_warm_up_is_refused() -> None:
    comp, served, _ = world()
    conf = {k: v for k, v in served.items() if k[0] == "confirmation"}
    with pytest.raises(cf.CycleError, match="C-T"):
        read(comp, conf)  # exploration not served: the warm-up is short


def test_another_cycle_or_protocol_is_refused() -> None:
    for comp, served, _ in (world(cycle="c2"), world(protocol="b" * 64)):
        d = dataclasses.replace(decl(comp), data_manifest_sha256=comp.manifest_sha256)
        with pytest.raises(cf.CycleError, match="another cycle or protocol"):
            read(comp, served, d)


def test_a_self_consistent_composite_that_is_not_the_declared_one_is_refused() -> None:
    true, _, _ = world()
    other, served, _ = world(protocol="b" * 64)  # verifies on its own
    with pytest.raises(cf.CycleError, match="not the declared one"):
        read(other, served, decl(true))


def test_the_right_manifest_with_other_bars_is_refused() -> None:
    comp, served, _ = world()
    key = ("confirmation", "BTCUSDT")
    rows, first = _rows()  # same hours and count, other prices: parsed hash differs
    other = screen.path_series(rows[(SPLIT - first) // H :] * 1.01, 0, SPLIT)
    with pytest.raises(cf.CycleError, match="not its manifest"):
        read(comp, {**served, key: other})


def test_a_tampered_composite_is_refused() -> None:
    comp, served, _ = world()
    bad = dataclasses.replace(comp, cycle_id="c9")  # hash no longer matches
    with pytest.raises(cf.CycleError, match="does not verify"):
        read(bad, served, decl(comp))
    with pytest.raises(cf.CycleError, match="not a composite"):
        read(comp.as_mapping(), served, decl(comp))


@pytest.mark.parametrize("key", [("lockbox", "BTCUSDT"), ("confirmation", "SOLUSDT")])
def test_a_partition_that_is_not_readable_is_refused(key: tuple[str, str]) -> None:
    comp, served, _ = world()
    with pytest.raises(cf.CycleError, match="not a readable one"):
        read(comp, {**served, key: served[("confirmation", "BTCUSDT")]})


def test_a_series_served_under_another_symbol_is_refused() -> None:
    comp, served, _ = world()
    swapped = {
        **served,
        ("confirmation", "BTCUSDT"): served[("confirmation", "ETHUSDT")],
    }
    with pytest.raises(cf.CycleError, match="not its manifest"):
        read(comp, swapped)
