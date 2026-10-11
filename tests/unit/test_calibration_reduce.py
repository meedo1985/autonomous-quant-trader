"""D-19 reduction (prereg §3.5 item 2): stored draws decode bit-exactly;
development thresholds are, per T level, each tail's extreme over every
cell of that level, of any K; K and T stay exact checks."""

from __future__ import annotations

import math
import struct

import pytest

from calibration import classifier, reduce


def test_a_stored_draw_decodes_bit_exactly() -> None:
    values = {"a": -0.0, "b": 1e-308, "c": math.nan}
    stored = {n: struct.pack(">d", v).hex() for n, v in values.items()}
    back = reduce.decode(stored)
    assert struct.pack(">d", back["a"]) == struct.pack(">d", -0.0)
    assert back["b"] == 1e-308 and math.isnan(back["c"])


def _cell(k: int, t: int, top: float, bottom: float) -> reduce.Bounds:
    """A full threshold set for K = k: every tail at +-1, except
    max_excess_kurtosis = top and min_skewness = bottom."""
    need = classifier.required(k)
    upper = {n: 1.0 for n in need & set(classifier.UPPER)}
    lower = {n: -1.0 for n in need & set(classifier.LOWER)}
    upper["max_excess_kurtosis"], lower["min_skewness"] = top, bottom
    exact = {"K": float(k), "T": float(t)}
    return exact | upper, exact | lower


def test_pooled_takes_each_tails_extreme_per_t_level_over_every_k() -> None:
    """Owner decision 2026-10-11 (I2BW-1): §3.5 item 2 as written."""
    pools = reduce.pooled(
        [_cell(1, 9, 5.0, -1.0), _cell(2, 9, 3.0, -0.5), _cell(5, 9, 2.0, -2.0),
         _cell(2, 10, 7.0, -7.0)]
    )  # fmt: skip
    assert set(pools) == {9, 10}
    up, lo = pools[9]
    assert "K" not in up and up["T"] == 9.0
    assert up["max_excess_kurtosis"] == 5.0  # from the K = 1 cell
    assert lo["min_skewness"] == -2.0  # from the K = 5 cell
    assert pools[10][0]["max_excess_kurtosis"] == 7.0  # never mixes T levels


def test_for_k_makes_an_exact_k_threshold_set_from_the_pool() -> None:
    pools = reduce.pooled([_cell(1, 9, 5.0, -1.0), _cell(5, 9, 2.0, -2.0)])
    for k in (1, 2, 5):
        upper, lower = reduce.for_k(pools[9], k)
        assert (upper["K"], upper["T"], lower["K"], lower["T"]) == (k, 9, k, 9)
        assert set(upper) | set(lower) == classifier.required(k)
        assert upper["max_excess_kurtosis"] == 5.0
        values = dict.fromkeys(classifier.required(k), 0.0) | {"K": k, "T": 9}
        assert classifier.within(values, upper, lower)  # a complete, valid set
    only_k1 = reduce.pooled([_cell(1, 9, 5.0, -1.0)])
    with pytest.raises(ValueError, match="no candidate cell has"):
        reduce.for_k(only_k1[9], 2)  # no correlation tails at this level


def test_a_qj_threshold_chain_needs_one_record_per_family_on_every_draw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I2BS2-1: every QJ draw is exactly {"trend", "vol"}; one per family set."""
    import types

    from calibration import chunks

    def draw(value: float) -> dict[str, str]:
        return {"K": struct.pack(">d", 2.0).hex(), "T": struct.pack(">d", 9.0).hex(),
                "max_excess_kurtosis": struct.pack(">d", value).hex()}  # fmt: skip

    good = [{"trend": draw(1.0), "vol": draw(2.0)} for _ in range(3)]
    chain = types.SimpleNamespace(cell_id="qj")
    fitted: list[list[dict[str, float]]] = []

    def fit(draws: list[dict[str, float]]) -> list[dict[str, float]]:
        fitted.append(draws)
        return draws

    monkeypatch.setattr(classifier, "fit_thresholds", fit)
    monkeypatch.setattr(chunks, "reduce", lambda _: good)
    assert len(reduce.cell_thresholds(chain, joint=True)) == 2  # type: ignore[arg-type]
    assert [d[0]["max_excess_kurtosis"] for d in fitted] == [1.0, 2.0]
    for bad in ({**good[0], "extra": draw(3.0)}, {"trend": draw(1.0)}, draw(1.0)):
        monkeypatch.setattr(chunks, "reduce", lambda _, b=bad: [*good, b])
        with pytest.raises(ValueError, match="not one record per family"):
            reduce.cell_thresholds(chain, joint=True)  # type: ignore[arg-type]
