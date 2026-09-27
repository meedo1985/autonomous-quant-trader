import hashlib
import pathlib
import sys
import urllib.error
import urllib.request

out = pathlib.Path(sys.argv[1]) / "klines"
out.mkdir(exist_ok=True)
symbols = ["ZECUSDT", "SOLUSDT", "XRPUSDT", "NEARUSDT", "QNTUSDT", "BTCUSDT", "ETHUSDT"]
months = [
    (y, m) for y in range(2017, 2022) for m in range(1, 13) if (y, m) >= (2017, 8)
]
base = "https://data.binance.vision/data/spot/monthly/klines"


def get(url):
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "aqt-survey"}),
            timeout=60,
        ).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


for s in symbols:
    got = missing = 0
    for y, m in months:
        assert (y, m) <= (2021, 12)  # exploration only
        name = f"{s}-1h-{y}-{m:02d}.zip"
        path = out / name
        if path.exists():
            got += 1
            continue
        url = f"{base}/{s}/1h/{name}"
        data = get(url)
        if data is None:
            missing += 1
            continue
        check = get(url + ".CHECKSUM").decode().split()[0]
        if hashlib.sha256(data).hexdigest() != check:
            raise SystemExit(f"checksum mismatch {name}")
        path.write_bytes(data)
        got += 1
    print(s, "months:", got, "not listed:", missing, flush=True)
