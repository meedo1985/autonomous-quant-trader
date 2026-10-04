"""D-19 calibration engine: the accelerated path is bit-identical to the
pure-Python reference and to production routines; seeds and generator are
deterministic. Synthetic data only."""

from __future__ import annotations

import json

import numpy as np

from aqt.metrics import statistics as st
from calibration import dsr
from calibration.generator import Cell, generate, sigma_matrix
from calibration.seeds import family_seed, outer_seed, stream


def _legs(k: int, t: int, dep: str = "independent", law: str = "gaussian"):
    seed = outer_seed("0" * 64, "test", "unit", 0)
    cell = Cell("test", k, t, law, dep)
    return seed, generate(cell, stream(seed, "market"), stream(seed, "columns"))


def test_indices_follow_the_production_bootstrap_algorithm(monkeypatch) -> None:
    """With the production purpose, the seed and indices equal
    `bootstrap_indices`; the DSR purpose changes only the seed (Annex B §2.4)."""
    window = json.dumps(["2022-01-01T00:00:00Z", "2025-06-01T00:00:00Z"],
                        separators=(",", ":"))  # fmt: skip
    production = st.ReplicateStream(
        "a" * 64, st.CONVENTION_DOCUMENT_SHA256, "BTCUSDT", "1.0", window
    )
    expected = st.bootstrap_indices(
        production, observations=40, replicate_index=3, block=4.0
    )
    dsr_purpose = dsr.indices("a" * 64, 40, 3, 4.0)
    monkeypatch.setattr(dsr, "PURPOSE", "paired_sharpe_ci")
    assert dsr.indices("a" * 64, 40, 3, 4.0) == list(expected)
    assert dsr_purpose != list(expected)


def test_accelerated_path_is_bit_identical_to_the_reference() -> None:
    for dep, law in (("independent", "gaussian"), ("equi0.9", "garch"),
                     ("opposites", "t5"), ("near_duplicates", "ar0.5")):  # fmt: skip
        seed, legs = _legs(5, 120, dep, law)
        fam = family_seed(seed, "test", "agnostic", 5, "0" * 64, 0)
        for rule in ("largest", "median"):
            a = dsr.evaluate(legs.x, fam, rule, reference=True)
            b = dsr.evaluate(legs.x, fam, rule)
            assert a == b  # every field, exact floats


def test_block_length_is_bit_identical_to_production() -> None:
    from calibration import fast

    fast.self_check()
    rng = np.random.default_rng(7)
    for n in (16, 120, 365, 1247):
        sparse = np.where(rng.random(n) < 0.9, 0.0, rng.standard_normal(n))
        for x in (rng.standard_normal(n), np.cumsum(rng.standard_normal(n)), sparse):
            expected = st.block_length(x.tolist())
            value, capped = fast.block_length(x)
            assert value == expected.value
            assert capped == (expected.clipping == "UPPER")


def test_g1_availability_matches_the_production_routine() -> None:
    from calibration import gates

    seed, legs = _legs(2, 120)
    cand = legs.candidates[:, 0]
    assert gates.g1(cand, legs.benchmark, seed) == gates.g1(
        cand, legs.benchmark, seed, reference=True
    )


def test_columns_have_the_declared_correlation_and_zero_mean() -> None:
    _, legs = _legs(5, 20000, "equi0.9")
    corr = np.corrcoef(legs.x.T)
    assert abs(corr[0, 1] - 0.9) < 0.02
    assert np.all(np.abs(legs.x.mean(axis=0)) < 4 * legs.x.std(axis=0) / np.sqrt(20000))


def test_dependence_matrices_are_positive_semidefinite() -> None:
    rng = np.random.default_rng(0)
    for dep in ("opposites", "clusters", "factor", "near_duplicates", "equi0.99"):
        for k in (5, 20, 80):
            w = np.linalg.eigvalsh(sigma_matrix(Cell("c", k, 10, dependence=dep), rng))
            assert w.min() > -1e-12
