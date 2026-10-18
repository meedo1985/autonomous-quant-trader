# Review prompt: D-19 screen S1 path-builder fix (37680a8)

You are an independent adversarial reviewer working read-only, not an authority. The S8 cost pilot (engine ebdf208) stopped on the server after 36 s:

```
aqt.data.bars.BarSemanticsError: high 158.36103274821556 is below open/low/close (156.35606198642708, 155.04359757328257, 158.3610327482157) at 2021-06-27T11:00:00+00:00
```

Cause: `reconstruct` (S1, accepted at f47ce17) computed `log_close = log(o0) + cumsum(c)` and `high = exp(log_open + hi)`, two different addition orders, so a source bar closing at its high or low could give a path high below its close (or low above it). Commit 37680a8 (diff attached) computes `log_close = cumsum([log(o0); c])[1:]`, so each `log_close[t]` is `fl(log_open[t] + c[t])`, the same rounded addition as `log_open[t] + hi[t]`. It also adds a regression test. Prereg wording (§7.2 as adjudicated): "OHLC is mirrored in log space about the open under a sign flip; volume is kept".

Local evidence: with the old code all 30 pilot paths built from the real exploration data (pilot trial-set seed, full path length) raise BarSemanticsError when every bar is passed through `Bar`. With 37680a8 all 30 pass. The new test fails on the old code and passes on the new. The 180 screen and semi tests pass, ruff and mypy are clean, and the frozen g11/g14 reference vectors are unchanged. `FROZEN_REFERENCE_VECTORS["paths"]` is still None (it is frozen from the server pilot).

Check:
1. Is the fix faithful to §7.2 and S1 (chaining, sign flip, first open), with no clamping or other silent alteration?
2. Does `h >= max(o, c)` and `lo <= min(o, c)` now hold for every bar? The argument is: the source bar is valid; division and `np.log` are monotone; `fl(x + a) >= fl(x + b)` when `a >= b`; `np.exp` is monotone; the flip negates exactly. Name any step that is not guaranteed on the pinned image (glibc libm, numpy 2.5.3). If one is not, say whether a remaining violation fails closed.
3. Is there any other caller of `reconstruct`, or any recorded value, that this change silently invalidates?
4. Any other way a real exploration bar could make `path_series` raise for a whole screen run, given that `screen_job` catches only `PathUnavailable`?

Verdict ACCEPT or FIX. Give new findings stable IDs S1F-Rn.
