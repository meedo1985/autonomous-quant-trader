# Loss bounds L-01 to L-04 — adoption record

Date: 2026-09-26
Recorded by: Claude Opus 5.5 (`claude-opus-5-5`), coding AI.

## What happened

The coding AI put each bound to the owner with its recommendation. The owner
selected, verbatim:

| Row | Question put to the owner | Owner's selection |
|---|---|---|
| `L-02` | "at least 240 effective decisions of paper trading (no real money) before any real money. Adopt?" | "Adopt as proposed (Recommended)" |
| `L-03` | "automatic HALT if live equity falls 20% below its highest point, restart only via the incident process. Adopt?" | "Adopt 20% (Recommended)" |
| `L-04` | "risk increases need a written reason beforehand, no increase while below the previous peak, plus the existing 72h waits. Adopt?" | "Adopt as proposed (Recommended)" |
| `L-01` | "how much real money may ever be deployed?" | "0 for now, revisit before canary (Recommended)" |

The owner then wrote the decisions and dates into section 6 of
`review/pre-deployment/LOSS_BOUND_DEFAULTS.md` themselves. The AI checked that
only the "Owner decision" and "Date" cells changed and committed the file
alone, exactly as typed.

## Status

| Row | In force as the owner's self-imposed bound |
|---|---|
| `L-01` | **0**: no real capital may be deployed until the owner sets a figure deliberately, before canary |
| `L-02` | ≥ 240 effective decisions of forward paper trading, no real capital |
| `L-03` | HALT at 20% below peak live equity, then the §14 incident process |
| `L-04` | Written record + no increase while below peak + the frozen 72h floors |

These are the owner's own bounds. They change no frozen text. Section 6 of
that document says they "cap the consequence of being wrong" and "do not reduce
the probability of being wrong".

## Effect on the deployment protocol draft

The draft (`review/deployment/DEPLOYMENT_PROTOCOL_v1_DRAFT.md`) marks these as
`[PENDING L-nn]`; they are now adopted. The draft is updated separately.
