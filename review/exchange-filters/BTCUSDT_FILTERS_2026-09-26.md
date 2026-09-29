# BTCUSDT exchange filters checked against Binance (T25-02, T18-06)

Date: 2026-09-29. By Claude Opus 5.5, on the owner's instruction ("do 2
first"). No network call to Binance's trading API, no credential.

## Source

The public snapshot already in `data/raw/exchange_info/` (not committed):
`exchangeInfo-20260926T110846Z.json`, sha256
`d485750d6d38ebca877e1b03a88bb6fe5a04b0a82cab3694975a8202608e3ffc`, from
`https://data-api.binance.vision/api/v3/exchangeInfo?symbols=["BTCUSDT","ETHUSDT"]`
at 2026-09-26T11:08:46Z.

Filter meanings were checked on 2026-09-29 against Binance's official
documentation, <https://developers.binance.com/docs/binance-spot-api-docs/filters>.
Quoted there: "The `MARKET_LOT_SIZE` filter defines the `quantity` … rules
for `MARKET` orders on a symbol"; "`applyMaxToMarket` determines whether
`maxNotional` will be applied to `MARKET` orders"; PERCENT_PRICE_BY_SIDE
bounds a BUY price by `average price × bidMultiplierUp/Down` and a SELL
price by `average price × askMultiplierUp/Down`.

## Comparison with `configs/paper_trading.example.toml`

| Filter | Config | Binance BTCUSDT | Result |
| --- | --- | --- | --- |
| LOT_SIZE stepSize | 0.00001 | 0.00001000 | equal |
| LOT_SIZE minQty | 0.00001 | 0.00001000 | equal |
| LOT_SIZE maxQty | 9000 | 9000.00000000 | equal |
| NOTIONAL minNotional | 5 | 5.00000000 | equal |
| PRICE_FILTER tickSize | 0.01 | 0.01000000 | equal |
| NOTIONAL maxNotional | not set | 9,000,000 (limit orders; `applyMaxToMarket` false) | not modelled; see below |
| MARKET_LOT_SIZE maxQty | not read | 111.96299414 | not applicable; see below |
| PERCENT_PRICE_BY_SIDE | not modelled | BUY ≤ 1.2 × avg, SELL ≥ 0.8 × avg | never binds; see below |

## Conclusions

- **T25-02: resolved.** The example filters equal Binance's BTCUSDT filters
  as of 2026-09-26. The config comment now says so instead of `[OPEN]`.
- **T18-06: not applicable.** `MARKET_LOT_SIZE` applies to `MARKET` orders
  only. The executor and FLATTEN send only immediate-or-cancel limit orders
  with a price cap (Tasks 22-23), so it never applies. If a `MARKET` order
  path is ever added, T18-06 returns.
- **Max notional 9,000,000 USDT per limit order** is not read by the config
  loader. It cannot bind at any order size this project considers (`L-01` is
  0; paper runs use 10,000 USDT). Recorded, not changed: adding it would
  change reviewed loop code for no effect.
- **PERCENT_PRICE_BY_SIDE** allows a BUY up to 20% above and a SELL down to
  20% below the 5-minute average price. The app's caps are 0.05% (S-1) and
  1% (FLATTEN), far inside, so it never binds.
- **Before a live stage:** re-read the filters on the day, since Binance can
  change them. ETHUSDT differs (step 0.0001, maxQty 9000); it is not traded.
