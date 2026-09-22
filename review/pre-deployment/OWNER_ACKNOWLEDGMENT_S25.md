# §25 Owner acknowledgment — prepared for signature

**Status:** `PREPARED FOR OWNER SIGNATURE — UNSIGNED — NOT SATISFIED`
**Prepared:** 2026-09-22 by Claude, observed model ID `claude-opus-5`, AI author
**Requirement:** `docs/RESEARCH_CONSTITUTION.md` §25, lines 187–188
**Constitution content hash at preparation:**
`4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7`
(recomputed per `schemas/HASH_CANONICALIZATION_v1.md` on 2026-09-22; matches)

## 0. What this is and what it is not

§25 requires the owner to sign and date an acknowledgment of nine specific
clauses **before the first equity curve**. No equity curve has been produced;
cycle `C1` never started. The requirement is therefore not yet breached, and it
is also not yet met.

This document is the acknowledgment **written out in full and prepared for
signature**. It is unsigned. An AI cannot sign it, cannot sign it on the owner's
behalf, and signing it is not a formality — §25 exists precisely because the
clauses below are the ones a person is most likely to have absorbed vaguely.

Signing this **does not** authorize trading, deployment, shadow trading,
promotion, calibration, lockbox access, or a cycle start. It removes one blocker
among several. The statistical verdict remains `KEEP_BLOCKED`, `D-15`–`D-19`
remain open, and §19's deployment protocol still does not exist.

Nothing here amends the Constitution. §25's text is frozen; the clause wordings
below expand it for comprehension and the frozen text governs where they differ.

## 1. The nine clauses

§25 enumerates nine acknowledgments. Each is restated below with what it
actually commits you to, and the frozen source.

### C-1. `NO_EDGE_FOUND` is an acceptable outcome

The project may conclude that there is no exploitable edge, and that is a
**successful scientific result, not a failure to be worked around**. You accept
in advance that the correct response to `NO_EDGE_FOUND` is to stop, not to
loosen a gate, re-run with different parameters until something passes, or seek
a second opinion until one agrees.

*Source: §25; the validity of `NO_EDGE_FOUND` is a standing project rule.*

### C-2. BTC and ETH are not independent replication

A result that holds on both BTC and ETH is **not** two confirmations. The two
assets are strongly correlated, particularly in the drawdowns that matter most.
You accept that "it worked on ETH too" carries far less evidential weight than
it intuitively feels like it carries, and does not constitute out-of-sample
replication.

*Source: §25.*

### C-3. De-risking may lag buy-and-hold

Spot maximum exposure is 100%, which means volatility management is
**de-risking, not alpha**. The strategy may underperform simply holding the
asset during bull markets. You accept that this underperformance **alone is not
grounds for override** — not for increasing exposure, not for disabling the
vol-management, not for abandoning the protocol.

*Source: §12 line 119, quoted directly; §25.*

### C-4. No bypass of the risk-increase process

Risk increases require formal review and cooling-off: at least 72 hours
(`§4` line 52, `protocol_v1.yaml:303–304`), only at 00:00 UTC and only if 24
hours have passed since the last increase (`protocol_v1.yaml:56–58`). You accept
that there is **no exception for a case that seems obvious at the time**. The
process exists for exactly the moments when bypassing it feels justified.

Risk *reductions* remain immediate and unilateral and are never gated.

*Source: §14 lines 129–131; §4 line 52.*

### C-5. No HALT override without the incident process

Overriding a HALT requires all five of: a **written incident record**, an
**identified or bounded cause**, a **successful reconciliation**, **explicit
owner action**, and a **timestamp**. Trading resumes only after incident closure
plus successful reconciliation — not at your discretion in the moment.

You accept that "I know what happened" is not an identified cause until it is
written down, and that reconciling means reconciling, not assuming.

*Source: §14 lines 133–135, all five elements quoted.*

### C-6. The AI is advisory only

No LLM is in the live decision path, and no AI review in this repository carries
authority. Every Claude, Codex, Fable or other model review here is **advisory
input to be adjudicated on evidence**, never an approval. You accept that no AI
has approved this system, that an AI cannot sign as a qualified statistician,
and that the AI reviews recorded in `review/` do not add up to one.

This bears directly on your stated position that you are not a statistician and
cannot obtain one. The AI work does not close that gap; it documents it.

*Source: §25; §2 line 34 (no LLM in the live decision path).*

### C-7. The total deployed allocation can be lost

The entire deployed amount can be lost through **mechanisms no backtest
captures** — exchange failure or insolvency, custody loss, a bug in code that
tested clean, a regime the sample never contained, a counterparty or regulatory
event. You accept that the backtest bounds none of these, and that a good
backtest is not evidence against them.

*Source: §25.*

### C-8. Only fully-loss-acceptable capital may be deployed

The deployed amount must be capital you can lose **entirely** without
consequence you are unwilling to accept. §25 freezes this principle; it does not
name an amount.

The amount is `L-01` in `review/pre-deployment/LOSS_BOUND_DEFAULTS.md`, where it
currently stands at **zero**, declined by the AI on the ground that the missing
input is your finances rather than expertise. Signing this clause commits you to
the principle. It does not set the figure, and the figure must be set separately
and deliberately by you.

*Source: §25.*

### C-9. You have read §§12 and 14

§25 requires acknowledging that you have read **§12** (vol-managed constraint,
line 118–119) and **§14** (owner clauses, lines 128–135) specifically. Both are
short and both are reproduced in substance above, at `C-3` for §12 and `C-4` and
`C-5` for §14. Read them in the Constitution itself before signing, not only
here: this document is an aid, and the frozen text is the thing you are
acknowledging.

*Source: §25.*

## 2. Signature

§25 requires the owner's signature and date. This must be completed by the owner
in his own hand. An AI has not supplied it and cannot.

I have read §§12 and 14 of `RESEARCH_CONSTITUTION.md` in full, and I acknowledge
clauses `C-1` through `C-9` above.

| Field | Value |
| --- | --- |
| Owner name | |
| Signature | |
| Date | |
| Constitution content hash acknowledged | `4cb6c7d3…4fb8d7` |

## 3. What this does not resolve

Signing removes one blocker. It does not touch:

1. **§19's deployment protocol, which does not exist.** `protocols/` contains
   `protocol_v1.yaml` and nothing else. Shadow trading is blocked by a missing
   document independently of everything statistical.
2. **`D-15`–`D-19`**, all open, several `BLOCKING — no candidate`. `D-16` and
   `D-17` govern the effective trial count; `A(N)` is monotone in `N`, so an
   undercount lowers the promotion hurdle.
3. **`dsr_minimum: 0.95`**, unsatisfied, with promotion blocked under the owner
   `DEFER` decision of 2026-09-18.
4. **`L-01`–`L-04`**, proposed but unadopted.
5. **No independent review** of `.agents/skills/sharpe-selection-statistics/`.

The verdict remains `KEEP_BLOCKED`.
