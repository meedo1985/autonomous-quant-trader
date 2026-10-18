"""S8 pilot overlay: exit after a 10% one-day drop."""


def o(target, market, state):
    return 0.0 if market["ret_24h"] < -0.1 else target
