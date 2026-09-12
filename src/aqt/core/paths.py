"""Paths for the source checkout; no directory creation or data access."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).absolute().parents[3]
