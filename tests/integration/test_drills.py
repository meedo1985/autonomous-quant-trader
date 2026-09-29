"""Task 25: the drill script checks what it claims (synthetic data only)."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import socket
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

from aqt.app.paper_loop import load_config
from aqt.data.bars import Bar, BarSeries

ROOT = Path(__file__).resolve().parents[2]
T0 = datetime(2020, 1, 1, tzinfo=UTC)
HOUR = timedelta(hours=1)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _drills() -> ModuleType:
    path = ROOT / "scripts" / "run_drills.py"
    spec = importlib.util.spec_from_file_location("run_drills", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_drills"] = module  # dataclasses resolve their module
    spec.loader.exec_module(module)
    return module


def _series(hours: int, gap_at: int | None = None) -> BarSeries:
    rng = random.Random(7)
    price, bars = 10_000.0, []
    for i in range(hours):
        if i == gap_at:
            continue
        close = round(price * math.exp(rng.gauss(0.0, 0.002)), 2)
        high, low = max(price, close) * 1.001, min(price, close) * 0.999
        bars.append(
            Bar(T0 + i * HOUR, price, round(high, 2), round(low, 2), close, 5.0)
        )
        price = close
    return BarSeries("BTCUSDT", tuple(bars))


def _config() -> object:
    config = load_config(ROOT / "configs" / "paper_trading.example.toml")
    return replace(config, start=T0 + 5 * 24 * HOUR, end=T0 + 17 * 24 * HOUR)


def test_the_freeze_drill_recovers_from_a_lost_reply(tmp_path: Path) -> None:
    drills = _drills()
    # A gap long before the window: the drill must still use the unbroken run.
    out = tmp_path / "freeze"
    result = drills.drill_freeze_reconcile(_series(24 * 20, gap_at=3), _config(), out)
    assert result.passed, result.observed
    steps = json.loads((out / "steps.json").read_text("utf-8"))
    assert "SimulatedTimeout" in steps[0]
    assert steps[1].startswith("blind check refused")
    assert steps[-1].startswith("after the full check: HALT")


def test_a_freeze_from_a_rejection_does_not_count_as_the_drill() -> None:
    drills = _drills()
    assert drills.controller_froze_on_timeout(["SimulatedTimeout: no response"])
    assert not drills.controller_froze_on_timeout(["NO_FILL_BAR: gapped history"])
    assert not drills.controller_froze_on_timeout([])


def test_drills_never_overwrite_earlier_evidence(tmp_path: Path) -> None:
    """A25-3: an existing output is refused, not cleared."""
    drills = _drills()
    (tmp_path / "freeze").mkdir()
    (tmp_path / "freeze" / "incidents.jsonl").write_text("earlier", "utf-8")
    with pytest.raises(FileExistsError):
        drills.drill_freeze_reconcile(_series(24 * 20), _config(), tmp_path / "freeze")
    assert (tmp_path / "freeze" / "incidents.jsonl").read_text("utf-8") == "earlier"
    config = ROOT / "configs" / "paper_trading.example.toml"
    code = drills.main(["--config", str(config), "--out", str(tmp_path)])
    assert code == 2
