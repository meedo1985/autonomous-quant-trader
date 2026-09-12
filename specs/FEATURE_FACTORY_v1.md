# FEATURE_FACTORY_v1.md

Status: Cycle-1 frozen feature definitions.

All features are causal and computed only from data available at the decision timestamp.

## Returns
- `ret_1h = log(close_t / close_t-1)`
- `ret_24h = log(close_t / close_t-24)`
- `ret_72h = log(close_t / close_t-72)`
- `ret_168h = log(close_t / close_t-168)`

## Trend
- `ema_24 = EMA(close, span=24)`
- `ema_72 = EMA(close, span=72)`
- `ema_168 = EMA(close, span=168)`
- `ema_dist_24 = close / ema_24 - 1`
- `ema_dist_72 = close / ema_72 - 1`
- `ema_dist_168 = close / ema_168 - 1`
- `sma_4800 = SMA(close, window=4800)`  # 200 days of 1h bars
- `trend_200d = close / sma_4800 - 1`
- `breakout_720 = close / rolling_max(close, 720) - 1`  # 30 days

## Volatility
Hourly log returns are used throughout.
- `rv_24 = std(ret_1h, trailing=24) * sqrt(8760)`
- `rv_168 = std(ret_1h, trailing=168) * sqrt(8760)`
- `rv_720 = std(ret_1h, trailing=720) * sqrt(8760)`
- `ewma_vol_168h = EWMA_std(ret_1h, halflife=168) * sqrt(8760)`
- `atr_24 = ATR(high, low, close, window=24) / close`

No volume-derived alpha, spread, order-book, trade-imbalance, or seasonality features are allowed in Cycle 1.

Any change to a formula or window creates a new feature-factory hash and ends the active cycle.
