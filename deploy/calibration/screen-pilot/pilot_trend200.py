"""S8 pilot signal: long above the 200-day SMA."""


def s(row, params, state):
    return 1.0 if row["trend_200d"] > 0 else 0.0
