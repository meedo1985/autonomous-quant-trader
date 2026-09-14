"""Smoke checks for the foundation; no trading or data fixtures."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "aqt",
        "aqt.core",
        "aqt.core.version",
        "aqt.core.paths",
        "aqt.data",
        "aqt.research",
        "aqt.features",
        "aqt.models",
        "aqt.benchmarks",
        "aqt.validation",
        "aqt.backtest",
        "aqt.metrics",
        "aqt.metrics.descriptive",
        "aqt.allocation",
        "aqt.governor",
        "aqt.execution",
        "aqt.monitoring",
        "aqt.lockbox_eval",
    ],
)
def test_package_imports(module: str) -> None:
    assert import_module(module).__name__ == module
