"""D-19 re-pilot checks (FE-7), run inside the calibration image by d19.sh:

  nonfinite <store>        count non-finite threshold diagnostics per cell
  compare <store> <store>  the threshold chains of two stores are identical

`nonfinite` reads only the diagnostic values of threshold records (binary64
hex, per family for a QJ cell) and refuses anything else (FE7-5). `compare`
shows that an interrupted and resumed threshold run equals a clean one: the
same chunk files, byte for byte (FE7-2, FE7R-1). Run both after
`d19.sh choose`, which has verified every chain."""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

FAMILIES = {"trend", "vol"}


def _chunks(store: Path, cell: str) -> list[dict[str, object]]:
    files = sorted((store / "threshold" / cell).glob("chunk-*.json"))
    if not files:
        raise SystemExit(f"no threshold chunks for {cell} in {store}")
    return [json.loads(f.read_bytes()) for f in files]


def _cells(store: Path) -> list[str]:
    root = store / "threshold"
    cells = (
        sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir() and not p.name.startswith(".")  # .locks: chain locks
        )
        if root.is_dir()
        else []
    )
    if not cells:
        raise SystemExit(f"no threshold chains in {store}")
    return cells


def nonfinite(store: Path) -> int:
    total = bad = 0
    for cell in _cells(store):
        n = values = 0
        for chunk in _chunks(store, cell):
            for draw in chunk["results"]:  # type: ignore[union-attr]
                draws = draw.values() if set(draw) == FAMILIES else [draw]
                for diagnostics in draws:
                    for value in diagnostics.values():
                        x = struct.unpack(">d", bytes.fromhex(value))[0]
                        values += 1
                        n += not math.isfinite(x)
        print(f"{cell}: {n} non-finite of {values} diagnostic values")
        total, bad = total + values, bad + n
    print(f"all cells: {bad} non-finite of {total}")
    return 0


def compare(a: Path, b: Path) -> int:
    """Every cell's chunk files, byte for byte (FE7R-1): equal bytes give
    equal content hashes and so the same chain head."""
    differ = []
    for cell in _cells(a):
        _chunks(b, cell)  # refuses a missing chain
        left, right = ((s / "threshold" / cell) for s in (a, b))
        names = sorted(f.name for f in left.glob("chunk-*.json"))
        same = names == sorted(f.name for f in right.glob("chunk-*.json")) and all(
            (left / n).read_bytes() == (right / n).read_bytes() for n in names
        )
        print(f"{cell}: {len(names)} chunks", "identical" if same else "DIFFER")
        if not same:
            differ.append(cell)
    if differ or _cells(a) != _cells(b):
        print("FAIL: the resumed and the clean threshold runs differ")
        return 1
    print("PASS: the resumed threshold run equals the clean run")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["nonfinite"] and len(argv) == 2:
        return nonfinite(Path(argv[1]))
    if argv[:1] == ["compare"] and len(argv) == 3:
        return compare(Path(argv[1]), Path(argv[2]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
