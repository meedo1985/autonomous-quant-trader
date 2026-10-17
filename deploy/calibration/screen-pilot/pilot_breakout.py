"""S8 pilot signal: long while within k% of the 30-day high."""


def s(row, params, state):
    return 1.0 if row["breakout_720"] > -params["k"] / 100 else 0.0
