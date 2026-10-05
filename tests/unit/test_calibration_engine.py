"""D-19 calibration engine: the accelerated path is bit-identical to the
pure-Python reference and to production routines; seeds and generator are
deterministic. Synthetic data only."""

from __future__ import annotations

import json

import numpy as np
import pytest

from aqt.metrics import statistics as st
from calibration import classifier, dsr
from calibration.generator import Cell, generate, sigma_matrix
from calibration.seeds import family_seed, outer_seed, stream


@pytest.fixture(autouse=True)
def _v_verified(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests exercise V's arithmetic on whatever runtime runs them; the
    pinned-runtime gate itself is tested in a subprocess below."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)


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
            a = dsr.evaluate(legs.x, fam, rule, numerics="reference")
            b = dsr.evaluate(legs.x, fam, rule, numerics="task12")
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


def test_method_v_is_deterministic_and_close_to_the_task12_numerics() -> None:
    """V is its own definition (D-20 proposal): repeatable bit for bit, and
    within rounding of the Task 12 numerics on ordinary data."""
    seed, legs = _legs(20, 365, "equi0.9", "garch")
    fam = family_seed(seed, "test", "agnostic", 20, "0" * 64, 0)
    v1 = dsr.evaluate(legs.x, fam, "largest")
    v2 = dsr.evaluate(legs.x, fam, "largest")
    exact = dsr.evaluate(legs.x, fam, "largest", numerics="task12")
    assert v1 == v2
    assert (v1.reason, v1.nominee, v1.block) == (
        exact.reason,
        exact.nominee,
        exact.block,
    )
    assert v1.z is not None and exact.z is not None
    assert abs(v1.z - exact.z) <= 1e-9 * max(1.0, abs(exact.z))


def test_method_v_refuses_a_constant_replicate_column() -> None:
    """VF1-1: Annex B rule 5 exactly, though rounding may leave var > 0."""
    t = 200
    x = np.zeros((t, 1))
    x[:5, 0] = [0.01, -0.02, 0.03, 0.01, -0.01]  # 5 active days, 195 zero days
    draws = [list(range(5, t)) + [5] * 5] + [list(range(t))] * 3  # rep 0: zeros
    assert dsr._replicates_v(x, draws) == (None, None)  # noqa: SLF001


def test_method_v_runtime_check_needs_the_pinned_runtime() -> None:
    """VF1-2: known-answer canary in a fresh process with the pinned
    environment; refused without it."""
    import os
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    code = (
        "from calibration import dsr; "
        "dsr.v_runtime_check(dsr.runtime_identity(), dsr.canaries()); print('ok')"
    )
    env = {
        **os.environ,
        **dsr.V_ENVIRONMENT,
        "PYTHONPATH": f"{root}{os.pathsep}{root / 'src'}",
    }
    done = subprocess.run([sys.executable, "-c", code], env=env, cwd=root,
                          capture_output=True, text=True, check=False)  # fmt: skip
    assert done.stdout.strip() == "ok", done.stderr
    wrong = (
        "from calibration import dsr; i = dsr.runtime_identity(); "
        "i['numpy'] = '0.0'; dsr.v_runtime_check(i, dsr.canaries())"
    )
    differs = subprocess.run([sys.executable, "-c", wrong], env=env, cwd=root,
                             capture_output=True, text=True, check=False)  # fmt: skip
    assert "runtime differs" in differs.stderr
    bare = {k: v for k, v in env.items() if k not in dsr.V_ENVIRONMENT}
    refused = subprocess.run([sys.executable, "-c", code], env=bare, cwd=root,
                             capture_output=True, text=True, check=False)  # fmt: skip
    assert "U_ops" in refused.stderr
    canary = (
        "from calibration import dsr; c = dsr.canaries(); c['libm'] = '0' * 64; "
        "dsr.v_runtime_check(dsr.runtime_identity(), c)"
    )
    failed = subprocess.run([sys.executable, "-c", canary], env=env, cwd=root,
                            capture_output=True, text=True, check=False)  # fmt: skip
    assert "known-answer canary failed" in failed.stderr


def test_method_v_variance_is_two_pass_stable() -> None:
    """VS1-2: a resample drawn from a tight cluster far from the column mean
    (large local mean, tiny local variance) keeps the Task 12 variance to a
    few ulps; a one-pass formula fails here."""
    t = 365
    x = np.where(np.arange(t) % 2 == 0, 0.001, -0.001)[:, None]
    x[::2, 0] += np.linspace(0, 1e-13, len(x[::2, 0]))  # positive cluster spread
    cluster = list(range(0, t, 2))
    draws = [(cluster * 2)[:t]]
    star, null = dsr._replicates_v(x, draws)  # noqa: SLF001
    assert star is not None
    drawn = x[np.asarray(draws[0]), 0]
    from calibration import fast

    mean, var = fast.mean_var(drawn)  # Task 12 numerics
    assert abs(star[0][0] - mean / var**0.5) <= 1e-6 * abs(mean / var**0.5)


def test_method_v_refuses_without_a_verified_runtime(monkeypatch) -> None:
    """VF2-1: V does not compute until the full identity check has passed,
    and a differing identity is refused."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", False)
    x = np.random.default_rng(1).standard_normal((30, 2))
    with pytest.raises(RuntimeError, match="U_ops"):
        dsr._replicates_v(x, [list(range(30))])  # noqa: SLF001


def test_method_v_refuses_overflowing_inputs() -> None:
    """VS2-2: finite but extreme values make fsum overflow: a refusal."""
    x = np.full((20, 1), 1e308)
    x[::2, 0] = -1e308
    x[0, 0] = 1e308
    assert dsr._replicates_v(x, [list(range(20))]) == (None, None)  # noqa: SLF001


def test_method_v_rule_5_holds_when_distinct_values_merge_after_centring() -> None:
    """VS3-2 / VF2-2: two raw values 1 ulp apart merge in Y = X - mu when mu
    is far away; V must still find the replicate valid, as Task 12 does."""
    t = 40
    a = 1.0
    b = float(np.nextafter(a, 2.0))
    x = np.empty((t, 1))
    x[: t // 2, 0] = -2000.0
    x[t // 2 :, 0] = [a, b] * (t // 4)
    near = list(range(t // 2, t))
    draws = [(near * 2)[:t]]
    mu = sum(x[:, 0].tolist()) / t
    assert (x[t // 2, 0] - mu) == (x[t // 2 + 1, 0] - mu)  # merged after centring
    from calibration import fast

    assert fast.mean_var(x[np.asarray(draws[0]), 0])[1] > 0  # Task 12: valid
    star, null = dsr._replicates_v(x, draws)  # noqa: SLF001
    assert star is not None and np.isfinite(star[0][0])


def test_classifier_ranks_tails_and_exact_checks() -> None:
    """§13 rev 7g item 4: integer ranks, eight tails without L/T, ties
    accepted, K and T exact."""
    assert classifier.ranks(300_000) == (299_997, 4)
    _, legs = _legs(5, 400)
    names = set(classifier.diagnostics(legs.x))
    assert names == {"K", "T", *classifier.UPPER, *classifier.LOWER}
    draws = [{"K": 5.0, "T": 400.0, "max_skewness": float(i)} for i in range(10)]
    upper, lower = classifier.fit_thresholds(draws)
    assert upper == {"K": 5.0, "T": 400.0, "max_skewness": 9.0}
    assert lower == {"K": 5.0, "T": 400.0}
    tie = {"K": 5.0, "T": 400.0, "max_skewness": 9.0}
    assert classifier.within(tie, upper, lower)
    assert not classifier.within({**tie, "T": 401.0}, upper, lower)
