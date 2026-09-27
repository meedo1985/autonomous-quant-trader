# Survey of other coins, and the owner's trading rule, on exploration data

Date: 2026-09-27. Analyst: Claude Opus 5.5 (`claude-opus-5-5`).
Permission: `OWNER_PERMISSION.md`. Scripts: `fetch.py`, `analyze.py` (this
directory). Data: session scratchpad only, not committed. This is
**exploration**: biased, free-form, and not evidence of an edge.

## 1. Which coins

The public 24h ticker (`data-api.binance.vision/api/v3/ticker/24hr`) was read
on 2026-09-27, after the lockbox end (SHA-256 of the saved response
`151831d49efec410f08d061d09f4ba18a479d4338838964a2b4b868c0475b106`). By quote volume, the top USDT pairs excluding stablecoins
were: BTC 651M, **ZEC 300M**, ETH 267M, **SOL 219M**, **XRP 175M**,
**NEAR 173M**, **QNT 79M**. The five besides BTC and ETH are the bold ones.

Caveats: one day's volume is noisy (ZEC's figure looks like a spike). Ranking
by today's volume favours coins that survived and grew, which is
survivorship bias.

## 2. Data

Monthly 1h kline archives from `data.binance.vision`, each verified against
its published SHA-256 `.CHECKSUM`, **exploration months only** (2017-08 to
2021-12). No confirmation or lockbox month was fetched for any coin. Coins
listed later have shorter histories: SOL from 2020-08, NEAR from 2020-10,
and QNT only from 2021-07 (156 days, too short to judge).

## 3. Method

- Volume: average daily quote volume inside the window. Volatility:
  annualized standard deviation of hourly log returns. Correlation: hourly
  log returns against BTC over common hours. Max drawdown: largest
  peak-to-trough fall of the close.
- **The owner's rule** (`review/owner-input/TRADING_RULE_2026-09-27.md`):
  buy at the open of the 00:00 UTC bar when flat (at most one entry per 24h,
  as the protocol requires). Exit at the first touch of +10% or of the stop.
  The stop is checked first when both fall in one bar, and a gap through a
  level exits at the bar's open. Position size is 10% of equity. Cost is
  0.13% per side: the frozen model's fee and spread plus its **minimum**
  slippage, so real costs for thinner coins would be higher.
- The same rule was also run with a −5% stop, which is 0.5% of the account
  at a 10% position.
- For comparison, "hold 10%" puts 10% of equity in the coin at the start and
  keeps it.

## 4. Results

| Coin | From | Days | $M/day | Vol/yr | Corr. BTC | Max DD | −0.5% stop: trades, win%, avg/trade, account | −5% stop: trades, win%, avg/trade, account | Hold 10% |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 2017-08 | 1598 | 1042 | 89% | 1.00 | 84% | 1257, 5.6%, −0.18%, **−20.1%** | 427, 35.6%, +0.08%, +2.3% | +97.3% |
| ETH | 2017-08 | 1598 | 584 | 108% | 0.79 | 94% | 1346, 5.3%, −0.20%, **−23.8%** | 548, 35.2%, +0.02%, −0.2% | +111.9% |
| ZEC | 2019-03 | 1017 | 26 | 128% | 0.65 | 83% | 914, 5.0%, −0.23%, **−19.3%** | 430, 34.7%, −0.06%, −3.7% | +15.6% |
| SOL | 2020-08 | 508 | 250 | 177% | 0.52 | 76% | 500, 4.2%, −0.32%, **−14.8%** | 344, 34.0%, −0.16%, −6.1% | +565.9% |
| XRP | 2018-05 | 1338 | 236 | 119% | 0.61 | 87% | 1163, 4.0%, −0.34%, **−32.5%** | 458, 31.7%, −0.51%, −21.7% | −1.0% |
| NEAR | 2020-10 | 444 | 54 | 179% | 0.53 | 79% | 435, 6.4%, −0.08%, **−3.7%** | 315, 40.0%, +0.74%, +25.2% | +100.1% |
| QNT | 2021-07 | 156 | 19 | 157% | 0.36 | 64% | 147, 5.4%, −0.19%, −2.8% | 85, 28.2%, −1.02%, −8.5% | +5.5% |

Check by hand, BTC with the −0.5% stop: 5.6% wins at +9.74% and 94.4% losses
at about −0.76% average −0.17% per trade. The script gives −0.18%.

## 5. What this says, and what it does not

1. **The −0.5% stop lost money on every coin**, from −2.8% to −32.5% of the
   account. Normal hourly moves hit it about 95% of the time, and each
   stopped trade costs about 0.76% after costs. This matches the arithmetic
   given to the owner beforehand.
2. **The −5% stop was near zero on BTC and ETH and negative on four of the
   five other coins.** NEAR was the exception (+25%), in a period when NEAR
   itself rose about tenfold. Simply holding it did four times better
   (+100%). One coin in one bull run is not an edge.
3. **Holding beat both rules on six of seven coins.** That is because
   2017-2021 was mostly a rising market. It is *not* a reason to hold: 2022
   (the unseen confirmation period) was a deep bear market, and the drawdowns
   here were already 64% to 94%.
4. **Other coins move with BTC** (correlation 0.36 to 0.79). They are more
   volatile (128% to 179% a year against BTC's 89%), and most trade far less
   (ZEC about 26M and QNT about 19M USD a day in the window, against BTC's
   1042M). Adding them spreads risk less than it seems, and they cost more
   to trade.
5. **No coin here showed an edge, with either rule.** Everything above is
   descriptive, on biased exploration data, and the costs are the frozen
   model's minimum. A real test needs a preregistered hypothesis in Cycle C1,
   judged on the confirmation period and against the benchmark.

## 6. If the owner still wants more coins

Liquidity and history favour **SOL** and **XRP**, with NEAR as a smaller
third. ZEC's volume looks like a one-day spike, and QNT has too little
history. Adding any coin still needs a section 4 amendment written and
signed by the owner (the AI may only propose), a 72-hour activation delay,
code changes to the symbol lists, and new exploration data through the
project downloader.
