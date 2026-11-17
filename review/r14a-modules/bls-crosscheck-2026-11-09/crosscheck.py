"""Cross-check calibration.c2_confirmation.bls_verify against drand's own client
(FP3 drand-verify, drand-client 1.4.2) on real quicknet rounds and swapped negatives."""

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

repo, dv = Path(sys.argv[1]), Path(sys.argv[2])
sys.path[:0] = [str(repo), str(repo / "src")]
from calibration import c2_confirmation as cf  # noqa: E402

Q = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
KEY = (
    "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5"
    "776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a"
    "4bc09e76eae8991ef5ece45a"
)
rounds = [1, 2, 3] + [k * 800_000 + 12_345 for k in range(1, 38)]
fetched = []
for r in rounds:
    url = f"https://api.drand.sh/v2/chains/{Q}/rounds/{r}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        body = json.loads(resp.read())
    assert body["round"] == r
    fetched.append({"round": r, "signature": body["signature"]})


def node(beacon: dict, expected: int) -> bool:
    p = dv / "tmp_beacon.json"
    p.write_text(json.dumps(beacon))
    done = subprocess.run(
        ["node", "verify.mjs", "info.json", str(p), str(expected)],
        cwd=dv,
        capture_output=True,
        text=True,
    )
    return json.loads(done.stdout)["signature_verifies"]


rows, agree, t_py = [], 0, 0.0
for i, b in enumerate(fetched):
    nb = fetched[(i + 1) % len(fetched)]
    swapped = {"round": b["round"], "signature": nb["signature"]}  # another round's sig
    for case, beacon in (("real", b), ("swapped", swapped)):
        t = time.time()
        py = cf.bls_verify(KEY, beacon["round"], beacon["signature"])
        t_py += time.time() - t
        js = node(beacon, beacon["round"])
        agree += py == js
        rows.append(
            {"round": beacon["round"], "case": case, "python": py, "drand_client": js}
        )
summary = {
    "rounds": len(fetched),
    "checks": len(rows),
    "agree": agree,
    "real_all_true": all(r["python"] for r in rows if r["case"] == "real"),
    "swapped_all_false": not any(r["python"] for r in rows if r["case"] == "swapped"),
    "python_seconds_per_check": round(t_py / len(rows), 2),
    "responses_sha256": hashlib.sha256(
        json.dumps(fetched, sort_keys=True).encode()
    ).hexdigest(),
}
(dv / "crosscheck_rounds.json").write_text(json.dumps(fetched, indent=0))
(dv / "crosscheck_rows.json").write_text(json.dumps(rows, indent=0))
print(json.dumps(summary))
