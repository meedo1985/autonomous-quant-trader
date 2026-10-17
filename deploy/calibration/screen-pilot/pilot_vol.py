"""S8 pilot signal: more exposure when short-term vol is low against
the 30-day vol (vol family)."""


def s(row, params, state):
    ratio = row["rv_720"] / row["rv_24"]
    return max(0.0, min(2.0, ratio * params["k"] / 10))
