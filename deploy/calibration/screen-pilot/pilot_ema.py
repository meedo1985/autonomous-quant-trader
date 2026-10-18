"""S8 pilot signal: long while close is above its 168 h EMA by k/1000."""


def s(row, params, state):
    return 1.0 if row["ema_dist_168"] > params["k"] / 1000 else 0.0
