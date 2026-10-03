# D-18 proposal: selection rule and primary error event

**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). AI proposal only; closes no
D-row, accepts no method, amends no frozen file.
**Owner direction (2026-10-03):** asked "D-18: Which direction should be
written up as the proposal (it then goes to two AI reviews before you decide
for real)?", the owner selected **"Top scorer only, no fallback"** — "Only the
highest-scoring strategy may be submitted; if it fails any other check the
cycle fails. Guarded event = 'any strategy passes on noise'. Simplest to
calibrate, strictest." Other options offered: "Allow fallback to runner-up";
"Keep highest-Sharpe event"; "Explain more first". This is a direction for
the write-up, not a D-18 decision (R19-2: two different-model reviews, then
the owner decides).

## 1. Problem (DEC-02)

`HUMAN_DECISION_MATRIX.md:65` marks D-18 BLOCKING with no candidate. DEC-02
(`../DSR_CALIBRATION_RECONCILIATION.md`): the method candidate selects the
maximum difference-series Sharpe trial, but each trial's DSR denominator uses
its own skewness and kurtosis, so the maximum-Sharpe trial need not have the
maximum DSR score. A calibration of "the max-Sharpe trial passes" says nothing
about "some trial passes", and the latter is the event that leads to a false
promotion when the operator submits whichever trial passes.

Frozen text: `protocols/protocol_v1.yaml:251` says "submitted candidate is one
grid point; family DSR/PBO/plateau account for selection". It does not say
which grid point.

## 2. Proposed rule

- **P18-1 Selection.** The submitted candidate is the family trial with the
  highest DSR score, ties broken by the lowest registered trial id. It is
  fixed before any other gate component is evaluated.
- **P18-2 No fallback.** If the selected trial fails any other gate component
  (PBO, plateau, OOS/IS ratio, intervals, or any other frozen gate), the cycle
  reports no promotable candidate. No other trial may be submitted from that
  cycle.
- **P18-3 Primary error event.** Under the declared null, the event bounded by
  calibration is `E = { max_J DSR_J >= 0.95 }`, the DSR score threshold from
  `protocol_v1.yaml` (`dsr.minimum: 0.95`).

## 3. Why the events coincide

Each trial passes the DSR component iff `DSR_J >= 0.95`. Under P18-1 the
submitted trial `J*` has `DSR_J* = max_J DSR_J`. Hence

`{ DSR_J* >= 0.95 } = { max_J DSR_J >= 0.95 } = { exists J : DSR_J >= 0.95 }`.

So "the submitted trial passes DSR" and "any trial passes DSR" are the same
event; DEC-02's conflict does not arise for the DSR component. Because P18-2
requires the submitted trial to also pass every other component, a false
promotion implies `E`, so `P(false promotion) <= P(E)` under the same null:
calibrating `E` bounds the whole gate's false-promotion probability from
above (conservatively; it ignores the other components' filtering).

## 4. What this does not settle (open, for the reviewers and the owner)

- **O18-1 Null.** Which null `E` is calibrated under: the all-zero-mean global
  null of the method candidate, or also mixed/composite nulls (DEC-02 keeps
  these as secondary). `P(E)` under a mixed null with some truly positive
  trials is not a false-pass probability for the null trials alone.
- **O18-2 Unavailable scores.** If any trial's DSR is unavailable (P-7, AS-3:
  `K=1`, zero/missing dispersion), the maximum is undefined. Proposal: the
  family result is unavailable and nothing is submitted; to be bound with P-7.
- **O18-3 Cross-cycle.** `E` is per cycle. Repeated cycles each get a chance at
  `E`; the lifetime count (owner choice of 2026-10-03,
  `../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`) raises the hurdle but
  is not shown to bound the lifetime probability (Astra AS-2).
- **O18-4 Cost.** No fallback can fail a cycle whose runner-up passes every
  gate. The owner accepted this strictness in the direction above.
- **O18-5 Amendment.** P18-1/P18-2 narrow `protocol_v1.yaml:251`; adopting them
  needs the owner-authored Constitution section 4 amendment (successor cycle
  C2), together with D-16, D-17, D-19 and the other blocking rows.

## 5. Next

Two different-model reviews (R19-2), records committed, then the owner's
D-18 decision. Calibration design (option C) waits for D-18.
