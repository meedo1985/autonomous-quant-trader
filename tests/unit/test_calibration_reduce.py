"""D-19 reduction (prereg §3.5 item 2): stored draws decode bit-exactly;
development thresholds are, per K, the extreme over cells."""

from __future__ import annotations

import math
import struct

import pytest

from calibration import reduce


def test_a_stored_draw_decodes_bit_exactly() -> None:
    values = {"a": -0.0, "b": 1e-308, "c": math.nan}
    stored = {n: struct.pack(">d", v).hex() for n, v in values.items()}
    back = reduce.decode(stored)
    assert struct.pack(">d", back["a"]) == struct.pack(">d", -0.0)
    assert back["b"] == 1e-308 and math.isnan(back["c"])


def _cell(k: int, t: int, top: float, bottom: float) -> reduce.Bounds:
    return (
        {"K": k, "T": t, "max_kurtosis": top},
        {"K": k, "T": t, "min_skewness": bottom},
    )


def test_pooled_takes_the_extreme_per_k_and_never_mixes_k() -> None:
    pooled = reduce.pooled(
        [_cell(2, 9, 1.0, -1.0), _cell(2, 9, 3.0, -0.5), _cell(5, 9, 2.0, -2.0)]
    )
    assert pooled[2] == _cell(2, 9, 3.0, -1.0)
    assert pooled[5] == _cell(5, 9, 2.0, -2.0)


def test_pooled_refuses_cells_of_one_k_with_different_t() -> None:
    with pytest.raises(ValueError, match="differ in T"):
        reduce.pooled([_cell(2, 9, 1.0, -1.0), _cell(2, 10, 1.0, -1.0)])
