# Owner permission: survey of other coins

Date: 2026-09-27

## What the owner said

After the AI explained that BTC/USDT and ETH/USDT are the only symbols in the
frozen protocol (section 2, "initially"), and that adding one takes a section
4 amendment the owner signs, the AI offered to download public data for other
coins and asked for approval. The owner answered, verbatim:

> yes check the top 5 coins and check if there in another coins that can make
> money

## What this permits, as read by the AI (Claude Opus 5.5)

An extension of the owner's section 15 reading in
`review/roadmap/OWNER_ANSWERS_Q3_Q4.md`, with the same limits:

- The coding AI may read Binance's public, credential-free market data for
  **symbols other than BTCUSDT and ETHUSDT**. That means the monthly 1h kline
  archives on `data.binance.vision` and the public 24h ticker on
  `data-api.binance.vision`, used only to rank symbols by current volume.
- Price history **only from the exploration months** (2017-08 to 2021-12).
  The confirmation (2022-01 to 2025-05) and lockbox (2025-06 to 2026-08)
  periods are not fetched for any symbol. The 24h ticker read on 2026-09-27
  lies after the lockbox end and is used only for the ranking.
- The data goes in the session scratchpad, **not** in `data/raw`, and is not
  a project data manifest. Only the survey's findings are committed.
- Only before Cycle 1. No credentials. No change to the protocol, the
  downloader's `ALLOWED_SYMBOLS`, or any frozen artifact. Adding a symbol
  still needs a section 4 amendment written and signed by the owner.
- "Can make money" is answered only descriptively, on biased exploration
  data. No result here is evidence of an edge (sections 7a and 13).
