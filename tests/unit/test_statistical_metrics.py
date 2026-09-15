"""Synthetic identities and independent arithmetic for inactive Task 12."""

import ast
import hashlib
import json
import math
import random
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import UTC, datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from statistics import mean, variance

import pytest

from aqt.backtest.costs import CostBreakdown
from aqt.backtest.engine import BacktestResult, SegmentRecord
from aqt.benchmarks.canonical import RebalanceAction
from aqt.metrics import statistics as s

START = datetime(2020, 1, 1, tzinfo=UTC)
BREAKDOWN = CostBreakdown(10.0, "fallback", 2.0, 1.0, 20.0, 1.0)


def hourly_result(returns, *, cost=0.0, start=START):
    equity = 1.0
    segments = []
    for i, gross in enumerate(returns):
        time = start + i * s.HOUR
        charged = cost if i == 0 else 0.0
        after_cost = equity * (1 - charged)
        after = after_cost * (1 + gross)
        segments.append(
            SegmentRecord(
                i,
                time,
                time,
                time + s.HOUR,
                100.0,
                gross,
                1.0,
                1.0,
                1.0,
                1.0,
                RebalanceAction.HOLD,
                "synthetic",
                None,
                0.0,
                BREAKDOWN,
                charged,
                equity,
                after_cost,
                after,
            )
        )
        equity = after
    return BacktestResult("BTCUSDT", 1.0, tuple(segments))


def stream(n=32, **changes):
    end = START + timedelta(days=n)
    window = json.dumps(
        [START.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")],
        separators=(",", ":"),
    )
    return replace(
        s.ReplicateStream(
            "a" * 64,
            s.CONVENTION_DOCUMENT_SHA256,
            "BTCUSDT",
            "1.0",
            window,
        ),
        **changes,
    )


def test_compound_each_leg_then_subtract_and_keep_entry_cost():
    a = hourly_result([0.1, -0.1] + [0.0] * 22 + [0.2] + [0.0] * 23, cost=0.001)
    b = hourly_result([0.02, 0.02] + [0.0] * 46)
    pair = s.paired_daily_returns(a, b)
    assert pair.candidate.returns == pytest.approx((0.999 * 1.1 * 0.9 - 1, 0.2))
    assert pair.benchmark.returns == pytest.approx((1.02**2 - 1, 0))
    assert pair.difference[0] == pytest.approx(0.999 * 1.1 * 0.9 - 1.02**2)
    wrong = (1 + (0.999 * 1.1 - 1) - 0.02) * (1 - 0.1 - 0.02) - 1
    assert pair.difference[0] != pytest.approx(wrong)
    assert pair.candidate.days == (START, START + timedelta(days=1))
    assert pair.candidate.convention == s.CONVENTION


@pytest.mark.parametrize(
    "count,start,code",
    [
        (0, START, "INSUFFICIENT_OBSERVATIONS"),
        (23, START, "PARTIAL_DAY"),
        (25, START, "PARTIAL_DAY"),
        (24, START + s.HOUR, "PARTIAL_DAY"),
        (24, START.replace(tzinfo=None), "INVALID_RESULT"),
        (24, START.replace(tzinfo=timezone(timedelta(hours=2))), "INVALID_TIMESTAMP"),
    ],
)
def test_reject_incomplete_days(count, start, code):
    with pytest.raises(s.StatisticsError) as error:
        s.daily_net_returns(hourly_result([0.0] * count, start=start))
    assert error.value.code == code


@pytest.mark.parametrize(
    "mutation",
    ["gap", "duplicate", "overlap", "duration", "offset", "nan", "equity", "cost"],
)
def test_reject_invalid_hourly_records(mutation):
    result = hourly_result([0.001] * 24)
    rows = list(result.segments)
    row = rows[12]
    if mutation == "gap":
        rows[12:] = [
            replace(
                x,
                execution_time=x.execution_time + s.HOUR,
                segment_end_time=x.segment_end_time + s.HOUR,
            )
            for x in rows[12:]
        ]
    elif mutation == "duplicate":
        rows[12] = replace(row, execution_time=rows[11].execution_time)
    elif mutation == "overlap":
        rows[12] = replace(
            row, execution_time=row.execution_time - timedelta(minutes=30)
        )
    elif mutation == "duration":
        rows[12] = replace(
            row, segment_end_time=row.segment_end_time + timedelta(minutes=10)
        )
    elif mutation == "offset":
        rows[12] = replace(
            row,
            segment_end_time=row.segment_end_time.astimezone(
                timezone(timedelta(hours=2))
            ),
        )
    elif mutation == "nan":
        rows[12] = replace(row, equity_after_return=math.nan)
    elif mutation == "equity":
        rows[12] = replace(row, equity_before=2.0)
    else:
        rows[12] = replace(row, equity_after_cost=0.3)
    with pytest.raises(s.StatisticsError):
        s.daily_net_returns(replace(result, segments=tuple(rows)))


@pytest.mark.parametrize("change", ["asset", "cost", "start", "length"])
def test_pair_identity_rejection(change):
    a = hourly_result([0.0] * 24)
    b = a
    if change == "asset":
        b = replace(a, symbol="ETHUSDT")
    if change == "cost":
        b = replace(a, stress_multiplier=2.0)
    if change == "start":
        b = hourly_result([0.0] * 24, start=START + timedelta(days=1))
    if change == "length":
        b = hourly_result([0.0] * 48)
    with pytest.raises(s.StatisticsError, match="MISALIGNED_PAIR"):
        s.paired_daily_returns(a, b)


def test_daily_ratio_overflow_and_rounded_total_loss():
    # Every one-hour return remains finite; only daily aggregation loses domain.
    with pytest.raises(s.StatisticsError):
        s.daily_net_returns(hourly_result([-0.99] * 24))


def test_sharpe_hand_identity_and_distinct_estimands():
    result = s.sharpe((1.0, 2.0, 3.0))
    assert result.mean == 2 and result.variance == 1 and result.daily == 2
    assert result.scaled == 2 * math.sqrt(365)
    pair = s.paired_sharpe_statistics((2.0, 4.0, 6.0), (1.0, 2.0, 3.0))
    assert pair.paired_sharpe_improvement == 0
    assert pair.difference_series_sharpe.daily == 2
    identical = s.paired_sharpe_statistics((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))
    assert identical.paired_sharpe_improvement == 0
    assert identical.difference_series_sharpe.reason == "ZERO_VARIANCE"
    assert s.sharpe((-3.0, -2.0, -1.0)).daily == -2


@pytest.mark.parametrize(
    "values,reason",
    [
        ((), "INSUFFICIENT_OBSERVATIONS"),
        ((1.0,), "INSUFFICIENT_OBSERVATIONS"),
        ((0.0,) * 16, "ZERO_VARIANCE"),
        ((0.1,) * 17, "ZERO_VARIANCE"),
        ((1e308, 1e308, -1e308), "NONFINITE_RESULT"),
        ((1e-300, 2e-300), "NONFINITE_RESULT"),
    ],
)
def test_undefined_sharpe(values, reason):
    result = s.sharpe(values)
    assert not result.available and result.reason == reason
    assert result.daily is None and result.scaled is None


@pytest.mark.parametrize(
    "values",
    [(True, 1), (math.inf, 1), (math.nan, 1), (10**1000, 1), "123", {1, 2}, (None, 1)],
)
def test_invalid_sequences_reject_without_fallback(values):
    for method in (
        s.sharpe,
        s.block_length,
        lambda x: s.effective_sample_size(x, horizon_hours=24),
    ):
        with pytest.raises(s.StatisticsError):
            method(values)


def test_paired_generated_overflow_is_unavailable():
    result = s.paired_sharpe_statistics((1e308, -1e308), (-1e308, 1e308))
    assert result.difference_series_sharpe.reason == "NONFINITE_RESULT"
    with pytest.raises(s.StatisticsError, match="MISALIGNED_PAIR"):
        s.paired_sharpe_statistics((1, 2), (1,))


def exact_covariances(values):
    x = tuple(Fraction(v) for v in values)
    centered = tuple(v - sum(x) / len(x) for v in x)
    return tuple(
        sum(centered[j] * centered[j - k] for j in range(k, len(x))) / len(x)
        for k in range(len(x))
    )


@pytest.mark.parametrize(
    "values,hours",
    [
        ((0, 0, 1, 1), 24),
        ((-1, 1, -1, 1), 24),
        (tuple(range(20)), 168),
        ((1, 2), 10000),
    ],
)
def test_newey_west_against_exact_fraction_quadratic_form(values, hours):
    result = s.effective_sample_size(values, horizon_hours=hours)
    n = len(values)
    lag = min(n - 1, max((hours + 23) // 24 - 1, math.floor(4 * (n / 100) ** (2 / 9))))
    gamma = exact_covariances(values)
    omega = gamma[0] + 2 * sum(
        (1 - Fraction(k, lag + 1)) * gamma[k] for k in range(1, lag + 1)
    )
    assert result.lag == lag
    assert result.gamma_zero == pytest.approx(float(gamma[0]))
    assert result.omega == pytest.approx(float(omega))
    assert result.value == pytest.approx(max(1, min(n, float(n * gamma[0] / omega))))
    assert result.method == "NEWEY_WEST"


def test_autocovariance_zero_lag_identity_and_dependence_direction():
    assert s._autocovariance((-1.0, 0.0, 1.0), 0) == pytest.approx(2 / 3)
    positive = s.effective_sample_size((0, 0, 1, 1), horizon_hours=24)
    negative = s.effective_sample_size((-1, 1, -1, 1), horizon_hours=24)
    assert positive.value < 4
    assert negative.value == 4  # no negative-correlation sample-size bonus
    # The approved automatic bandwidth never selects L=0 for integer n>=2;
    # test the covariance identity instead of adding an unauthorized override.


def test_ess_fallback_retains_diagnostics_and_does_not_clamp():
    result = s.effective_sample_size((0.0, 0.0), horizon_hours=168)
    assert result.value == 2 / 7 and result.method == "HORIZON_FALLBACK"
    assert result.fallback_reason == "ZERO_VARIANCE"
    assert result.gamma_zero == result.omega == 0 and result.lag == 1
    assert (
        s.effective_sample_size((), horizon_hours=24).reason
        == "INSUFFICIENT_OBSERVATIONS"
    )
    for values in ((1e308, 1e308, -1e308), (1e-300, 2e-300)):
        invalid = s.effective_sample_size(values, horizon_hours=24)
        assert invalid.reason == "NONFINITE_RESULT" and invalid.method is None


def test_nonpositive_nw_numerical_fallback(monkeypatch):
    # Bartlett covariance is nonnegative mathematically; exercise its explicit
    # numerical-failure branch without pretending this mock is observed data.
    monkeypatch.setattr(s, "_autocovariance", lambda x, k: 1.0 if k == 0 else -10.0)
    result = s.effective_sample_size((1.0, 2.0, 3.0), horizon_hours=24)
    assert result.fallback_reason == "NONPOSITIVE_LONG_RUN_VARIANCE"
    assert result.omega < 0 and result.lag is not None


@pytest.mark.parametrize("horizon", [0, -24, True, 24.0, None])
def test_invalid_horizon(horizon):
    with pytest.raises(s.StatisticsError):
        s.effective_sample_size((1.0, 2.0), horizon_hours=horizon)


def test_influence_uses_population_scale_and_sample_sharpe():
    a, b = (1.0, 2.0, 4.0, 8.0), (-1.0, 0.0, 1.0, 2.0)

    def reference(x):
        center = mean(x)
        population_sd = math.sqrt(sum((v - center) ** 2 for v in x) / len(x))
        sr = center / math.sqrt(variance(x))
        return [
            (v - center) / population_sd
            - sr / 2 * ((v - center) ** 2 / population_sd**2 - 1)
            for v in x
        ]

    expected = [x - y for x, y in zip(reference(a), reference(b), strict=True)]
    assert s.paired_sharpe_improvement_influence(a, b).values == pytest.approx(expected)
    assert s.paired_sharpe_improvement_influence(a, a).values == (0.0,) * 4
    assert (
        s.paired_sharpe_improvement_influence((0, 0), (1, 2)).reason == "ZERO_VARIANCE"
    )


@pytest.mark.parametrize(
    "values,cutoff,bandwidth,clipping",
    [
        ((15,) + (-1,) * 15, 1, 2, "LOWER"),
        (tuple(range(16)), 3, 6, None),
        (tuple(i % 4 for i in range(32)), None, 11, "UPPER"),
        (tuple(range(128)), None, 17, None),
    ],
)
def test_ppw_exact_reference_fixtures(values, cutoff, bandwidth, clipping):
    result = s.block_length(values)
    gamma = exact_covariances(values)
    weights = [
        Fraction(1) if 2 * k <= bandwidth else 2 * (1 - Fraction(k, bandwidth))
        for k in range(1, bandwidth + 1)
    ]
    spectral = gamma[0] + 2 * sum(w * gamma[k] for k, w in enumerate(weights, 1))
    capital_g = 2 * sum(w * k * gamma[k] for k, w in enumerate(weights, 1))
    raw = float(capital_g**2 * len(values) / spectral**2) ** (1 / 3)
    assert result.cutoff == cutoff and result.bandwidth == bandwidth
    assert result.long_run_variance == pytest.approx(float(spectral), rel=1e-13)
    assert result.capital_g == pytest.approx(float(capital_g), rel=1e-13)
    assert result.raw == pytest.approx(raw, rel=1e-12)
    assert result.clipping == clipping
    assert result.value == pytest.approx(min(result.maximum, max(1, raw)))
    assert result.restart_probability == 1 / result.value


def test_ppw_rejects_negative_spectrum_and_degenerate_boundaries():
    bad = s.block_length(tuple(i % 3 for i in range(16)))
    assert bad.reason == "NONPOSITIVE_LONG_RUN_VARIANCE"
    assert bad.long_run_variance < 0 and bad.value is None
    flat = s.block_length((0.1,) * 16)
    assert flat.value == 1 and flat.degenerate and flat.window == 5
    assert s.block_length((0.0,) * 15).reason == "INSUFFICIENT_OBSERVATIONS"
    assert s.block_length((1e308, -1e308) * 8).reason == "NONFINITE_RESULT"
    assert s.block_length((1e-300, 2e-300) * 8).reason == "NONFINITE_RESULT"


def test_seed_material_and_index_golden_vector():
    identity = stream()
    material = json.dumps(
        [
            "aqt.statistics.stream.v1",
            "a" * 64,
            s.CONVENTION_DOCUMENT_SHA256,
            "paired_sharpe_ci",
            "BTCUSDT",
            "1.0",
            '["2020-01-01T00:00:00Z","2020-02-02T00:00:00Z"]',
            32,
            0,
        ],
        separators=(",", ":"),
    ).encode()
    assert (
        s.replicate_seed_material(identity, output_length=32, replicate_index=0)
        == material
    )
    digest = "d7e27667891ef75e48e7f754a5dfa88846968424b8172d1de5f0beaa9b07b17d"
    assert hashlib.sha256(material).hexdigest() == digest
    assert s.replicate_seed(identity, output_length=32, replicate_index=0) == digest
    assert s.bootstrap_indices(
        identity, observations=32, replicate_index=0, block=2.5
    ) == (
        8,
        9,
        6,
        4,
        5,
        13,
        14,
        15,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        31,
        0,
        1,
        2,
        7,
        8,
        9,
        15,
        10,
        11,
        12,
        13,
        14,
        15,
        15,
        16,
        17,
    )


def test_convention_hash_matches_approved_document():
    document = (
        Path(__file__).parents[2]
        / "review"
        / "task12"
        / "IMPLEMENTATION_CONVENTIONS.md"
    )
    assert hashlib.sha256(document.read_bytes()).hexdigest() == (
        s.CONVENTION_DOCUMENT_SHA256
    )


def test_stream_separation_and_order_independence():
    base = stream()
    changes = [
        replace(base, trial_seed_hex="c" * 64),
        replace(base, asset="ETHUSDT"),
        replace(base, cost_multiplier="2.0"),
        stream(33),
    ]
    digests = {
        s.replicate_seed(x, output_length=32, replicate_index=0)
        for x in [base, *changes]
    }
    assert len(digests) == 5
    reverse = {
        i: s.bootstrap_indices(base, observations=32, replicate_index=i, block=2.5)
        for i in (2, 1, 0)
    }
    forward = {
        i: s.bootstrap_indices(base, observations=32, replicate_index=i, block=2.5)
        for i in (0, 1, 2)
    }
    assert forward == reverse


def test_rejection_sampling_and_restart_wraparound(monkeypatch):
    class Fake(random.Random):
        def __init__(self, *args):
            self.words = iter((7, 3, 2, 1, 0))

        def getrandbits(self, bits):
            return next(self.words)

        def random(self):
            return 0.99

    assert s._uniform_index(Fake(), 4) == 3  # reject 7, not modulo 4
    monkeypatch.setattr(s.random, "Random", Fake)
    assert s.bootstrap_indices(
        stream(4), observations=4, replicate_index=0, block=4
    ) == (3, 0, 1, 2)
    assert s.bootstrap_indices(
        stream(4), observations=4, replicate_index=0, block=1
    ) == (3, 2, 1, 0)


@pytest.mark.parametrize(
    "change",
    [
        {"trial_seed_hex": "A" * 64},
        {"statistical_convention_hash": "short"},
        {"statistical_convention_hash": "c" * 64},
        {"asset": "DOGEUSDT"},
        {"cost_multiplier": "1"},
        {"purpose": "prediction"},
        {"evaluation_window_id": "x"},
        {"evaluation_window_id": "[1,2]"},
        {"evaluation_window_id": '["2020-01-02T00:00:00Z","2020-01-01T00:00:00Z"]'},
    ],
)
def test_bad_stream_identity(change):
    with pytest.raises(s.StatisticsError, match="INVALID_IDENTITY"):
        stream(**change)


@pytest.mark.parametrize(
    "n,index,block",
    [
        (0, 0, 1),
        (True, 0, 1),
        (4, -1, 1),
        (4, 2000, 1),
        (4, True, 1),
        (4, 0, 0.5),
        (4, 0, 5),
        (4, 0, math.inf),
    ],
)
def test_bad_index_arguments(n, index, block):
    with pytest.raises(s.StatisticsError):
        s.bootstrap_indices(
            stream(), observations=n, replicate_index=index, block=block
        )


@pytest.mark.parametrize(
    "q,expected", [(0, 0), (0.25, 7.5), (0.5, 15), (0.95, 28.5), (1, 30)]
)
def test_type_seven_hand_quantiles(q, expected):
    values = [30.0, 0.0, 20.0, 10.0]
    assert s.type_seven_quantile(values, q) == pytest.approx(expected)
    assert values == [30, 0, 20, 10]


@pytest.mark.parametrize(
    "values,q", [((), 0.5), ((1.0, 2.0), -1), ((1.0, 2.0), 2), ((1.0, 2.0), math.nan)]
)
def test_bad_quantiles(values, q):
    with pytest.raises(s.StatisticsError):
        s.type_seven_quantile(values, q)


def test_interval_exactly_2000_shared_indices_and_no_recentering(monkeypatch):
    a, b = tuple(i / 100 for i in range(32)), tuple((i % 7) / 100 for i in range(32))
    observed = s.paired_sharpe_statistics(a, b).paired_sharpe_improvement
    calls = []

    def rotate(identity, *, observations, replicate_index, block):
        calls.append(replicate_index)
        return tuple((i + replicate_index) % observations for i in range(observations))

    monkeypatch.setattr(s, "bootstrap_indices", rotate)
    result = s.paired_sharpe_improvement_interval(a, b, stream=stream())
    assert result.available and result.attempts_executed == 2000
    assert calls == list(range(2000))
    assert result.point_estimate == observed
    assert result.lower == pytest.approx(observed) and result.upper == pytest.approx(
        observed
    )
    assert result.replicate_statistics == pytest.approx((observed,) * 2000)


def test_invalid_replicates_are_all_recorded_without_retry_or_early_stop(monkeypatch):
    calls = []

    def bad_indices(identity, *, observations, replicate_index, block):
        calls.append(replicate_index)
        return (
            (0,) * observations
            if replicate_index in (0, 1999)
            else tuple(range(observations))
        )

    monkeypatch.setattr(s, "bootstrap_indices", bad_indices)
    values = tuple(i / 100 for i in range(32))
    result = s.paired_sharpe_improvement_interval(values, values, stream=stream())
    assert result.reason == "INVALID_REPLICATE" and not result.available
    assert result.lower is result.upper is None
    assert result.attempts_executed == 2000 and calls == list(range(2000))
    assert result.invalid_replicates == ((0, "ZERO_VARIANCE"), (1999, "ZERO_VARIANCE"))
    assert result.replicate_statistics[0] is result.replicate_statistics[-1] is None
    assert len(result.replicate_statistics) == 2000


def test_real_interval_rerun_no_mutation_global_rng_or_io(monkeypatch):
    identity = stream()
    values = [i / 100 for i in range(32)]
    before, rng = list(values), random.getstate()

    def forbidden(*args, **kwargs):
        raise AssertionError("prohibited I/O")

    monkeypatch.setattr("builtins.open", forbidden)
    first = s.paired_sharpe_improvement_interval(values, values, stream=identity)
    second = s.paired_sharpe_improvement_interval(values, values, stream=identity)
    assert first.available and first.lower == first.upper == 0
    assert first == second and first.stream == identity
    assert json.dumps(asdict(first), sort_keys=True, allow_nan=False) == json.dumps(
        asdict(second), sort_keys=True, allow_nan=False
    )
    assert random.getstate() == rng and values == before
    assert "3.12" in first.python_runtime
    with pytest.raises(FrozenInstanceError):
        first.lower = 1


def test_invalid_original_executes_no_replicates(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("unexpected replicate")

    monkeypatch.setattr(s, "bootstrap_indices", forbidden)
    for a, b in [((1.0,) * 32, (2.0,) * 32), ((1.0, 2.0), (2.0, 3.0))]:
        result = s.paired_sharpe_improvement_interval(a, b, stream=stream())
        assert not result.available and result.attempts_executed == 0
    with pytest.raises(s.StatisticsError):
        s.paired_sharpe_improvement_interval((1, 2), (1,), stream=stream())


def test_module_has_no_external_access_or_protected_imports():
    tree = ast.parse(Path(s.__file__).read_text(encoding="utf-8"))
    imported = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not any(
        name and name.startswith(("aqt.validation", "aqt.lockbox_eval", "aqt.governor"))
        for name in imported
    )
    assert not any(
        isinstance(node, ast.Import)
        and any(
            alias.name in {"os", "socket", "requests", "subprocess"}
            for alias in node.names
        )
        for node in ast.walk(tree)
    )
