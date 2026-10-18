"""S8 pilot signal: exposure from the model's prediction."""


def s(row, params, state):
    return max(0.0, 0.5 + row["model:m"])
