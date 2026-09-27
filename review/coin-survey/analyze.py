import csv, io, math, sys, zipfile, pathlib, statistics
from datetime import datetime, timezone
root = pathlib.Path(sys.argv[1]) / "klines"
END = datetime(2021, 12, 31, 23, tzinfo=timezone.utc).timestamp() * 1000
COST = 0.0013  # per side: 10 bps fee + 2 bps spread + 1 bp slippage floor (frozen model's minimum)

def load(sym):
    bars = {}
    for z in sorted(root.glob(f"{sym}-1h-*.zip")):
        with zipfile.ZipFile(z) as f:
            for row in csv.reader(io.TextIOWrapper(f.open(f.namelist()[0]))):
                if not row[0].isdigit(): continue
                t = int(row[0])
                if t > 1e14: t //= 1000
                if t > END: continue
                bars[t] = (float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[7]))
    return dict(sorted(bars.items()))

def rule(bars, sl, tp):
    """Enter at the open of each 00:00 UTC bar when flat; exit at the first
    touch of stop or target (stop first if both in one bar, gap-aware)."""
    times = list(bars); trades = []; i = 0
    while i < len(times):
        t = times[i]
        if (t // 3600000) % 24 != 0: i += 1; continue
        entry = bars[t][0]; stop, target = entry * (1 - sl), entry * (1 + tp); exit_px = None
        j = i
        while j < len(times):
            o, h, l, c, _ = bars[times[j]]
            if j > i and o <= stop: exit_px = o; break          # gapped through the stop
            if l <= stop: exit_px = stop; break
            if j > i and o >= target: exit_px = o; break
            if h >= target: exit_px = target; break
            j += 1
        if exit_px is None: break
        gross = exit_px / entry - 1
        trades.append(gross - 2 * COST)
        # next entry: the next 00:00 at least 24h after this entry
        i = j + 1
        while i < len(times) and (times[i] - t < 86400000 or (times[i] // 3600000) % 24 != 0): i += 1
    return trades

def summary(sym, bars, btc_ret):
    times = list(bars); closes = [bars[t][3] for t in times]
    rets = {times[k]: math.log(closes[k] / closes[k-1]) for k in range(1, len(times)) if times[k] - times[k-1] == 3600000}
    days = (times[-1] - times[0]) / 86400000
    dvol = sum(b[4] for b in bars.values()) / days
    vol = statistics.pstdev(rets.values()) * math.sqrt(24 * 365)
    common = [t for t in rets if t in btc_ret]
    corr = statistics.correlation([rets[t] for t in common], [btc_ret[t] for t in common]) if sym != "BTCUSDT" else 1.0
    peak = dd = 0
    for c in closes:
        peak = max(peak, c); dd = max(dd, 1 - c / peak)
    bh = closes[-1] / closes[0] - 1
    # How often does a day's first 0.5% drop come before a +10% rise?
    out = {"sym": sym, "from": datetime.fromtimestamp(times[0]/1000, timezone.utc).strftime("%Y-%m"),
           "days": round(days), "dvol_musd": dvol / 1e6, "ann_vol": vol, "corr_btc": corr,
           "max_dd": dd, "bh": bh}
    for sl in (0.005, 0.05):
        tr = rule(bars, sl, 0.10)
        wins = sum(1 for x in tr if x > 0)
        acct = 1.0
        for x in tr: acct *= 1 + 0.10 * x   # 10% of equity per trade
        out[f"sl{sl}"] = (len(tr), wins / len(tr) if tr else 0, statistics.mean(tr) if tr else 0, acct - 1)
    out["bh10"] = 0.10 * bh  # 10% of equity held throughout, for comparison
    return out

btc = load("BTCUSDT"); bt = list(btc); bc = [btc[t][3] for t in bt]
btc_ret = {bt[k]: math.log(bc[k]/bc[k-1]) for k in range(1, len(bt)) if bt[k]-bt[k-1] == 3600000}
print(f'{"coin":9s} {"from":7s} {"days":>5s} {"$M/day":>8s} {"vol/yr":>7s} {"corrBTC":>7s} {"maxDD":>6s} | {"-0.5% stop: n  win%  avg/trade  acct":>36s} | {"-5% stop: n  win%  avg/trade  acct":>34s} | {"hold10%":>8s}')
for s in ["BTCUSDT","ETHUSDT","ZECUSDT","SOLUSDT","XRPUSDT","NEARUSDT","QNTUSDT"]:
    r = summary(s, load(s) if s != "BTCUSDT" else btc, btc_ret)
    a, b = r["sl0.005"], r["sl0.05"]
    print(f'{s[:-4]:9s} {r["from"]:7s} {r["days"]:5d} {r["dvol_musd"]:8.1f} {r["ann_vol"]:7.0%} {r["corr_btc"]:7.2f} {r["max_dd"]:6.0%} | '
          f'{a[0]:5d} {a[1]:5.1%} {a[2]:+9.2%} {a[3]:+8.1%} | {b[0]:5d} {b[1]:5.1%} {b[2]:+9.2%} {b[3]:+8.1%} | {r["bh10"]:+8.1%}')
