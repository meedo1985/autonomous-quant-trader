# Owner decision: O-1..O-7 (§4 amendment draft owner items)

**Date:** 2026-10-04
**Authority:** the owner, in a Claude Code session. The items come from
`DRAFT_WORDING.md` §7, revision 4, commit `fb3be96`. That draft went through
three rounds of two-model review: FA1/SA1, FA2/SA2 and FA3/SA3, with the
adjudications listed in its header. Asked and recorded by Claude Opus 5.5
(`claude-opus-5-5`). No different-model review of these specific answers was
run before asking. The final wording that contains them is reviewed under
§6 step 2.

## Pre-question check for O-7

The O-7 recommendation asked for the G-2 sign convention to be checked
against a worked example before confirmation. Claude Opus 5.5 made that
check. No independent reviewer did.

- In `protocols/protocol_v1.yaml` l.276–278, G-2 reads: "confirmation OOS max
  drawdown point estimate no worse than benchmark by >0.05".
- In `src/aqt/metrics/descriptive.py` l.232–262, `max_drawdown` returns a
  nonnegative fraction. For example, a 30% fall gives `0.30`.
- So the reading is: **pass iff `MDD_candidate − MDD_benchmark ≤ 0.05`**. The
  difference is absolute, in fraction units, so 0.05 means 5 percentage points.
  Worked example: with a benchmark of 0.30, a candidate of 0.34 passes and a
  candidate of 0.36 fails. A difference of exactly 0.05 passes.

## Exchange (verbatim answers; questions as asked)

| Item | Question (abridged) | Options offered | Answer |
|---|---|---|---|
| O-1 | Which cycles use up a step of the halving allowance? | Every eligible cycle (Recommended) / Only cycles with a result | **Every eligible cycle (Recommended)** |
| O-2 | How long is the post-nomination window, and what happens at expiry? | 75 days, expiry = no promotion (Recommended) / 120 days, expiry = no promotion | **75 days, expiry = no promotion (Recommended)** |
| O-3 | After a revision or invalidation following the look, what happens to a nominee being processed? (A reading of the Constitution, so no recommendation was given.) | (a) Stop unless attested / (b) Finish under old rules | **(a) Stop unless attested** |
| O-4 | May `RESEARCH_ONLY` or `NO_RESULT` use the deployable-baseline path? | No, only NO_EDGE_FOUND (Recommended) / Yes, also those outcomes | **No, only NO_EDGE_FOUND (Recommended)** |
| O-5 | Is the amendment safety-relevant? | Safety-relevant (Recommended) / Not safety-relevant | **Safety-relevant (Recommended)** |
| O-6 | How is the C2 family seed chosen? | Public beacon after hashing (Recommended) / Hash of declaration + disclosure | **Public beacon after hashing (Recommended)** |
| O-7 | Confirm G-2 as an absolute difference of 5 points (example above)? | Confirm, absolute 5 points (Recommended) / Relative: within 5% of benchmark | **Confirm, absolute 5 points (Recommended)** |

## Effect

- **O-1:** every cycle declared on an eligible window increments `m`, whatever
  its outcome.
- **O-2:** `post_nomination_window_days: 75` and `calendar_days_elapsed: 255`.
  At the cap, processing ends with no promotion for any nominee not yet
  processed. An expiry is counted as `U_ops` under P18-7 (SA2-6).
- **O-3:** reading (a). "Open promotion" in §4 l.48 means already attested. A
  revision or invalidation after the look ends processing of every nominee not
  yet attested.
- **O-4:** only `NO_EDGE_FOUND` opens the deployable-baseline path. Neither
  `RESEARCH_ONLY` nor `NO_RESULT` does.
- **O-5:** the amendment is safety-relevant. The §4 l.56 incident and cooling-off
  check applies, as does the 72-hour minimum activation delay (§4 l.52).
- **O-6:** the family seed is derived from a named public randomness-beacon
  value, published after the declaration hash is committed. The §5 disclosure
  stays. The beacon, the round-selection rule and the derivation are still to
  be drafted as an AI default, and they are part of the reviewed final
  wording.
- **O-7:** G-2 is operative as written, under the absolute reading above.

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited.
The §4 draft still has to fold these answers in, along with the D-rows decided
since revision 4. D-19, D-11..D-13 and D-20 remain open. Promotion stays
blocked. No cycle, trial, confirmation or lockbox access, deployment or
trading is authorized.
