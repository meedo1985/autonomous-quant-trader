# Owner decision: accept D-19 §13 budget version rev 7g, and O18-4-T

**Date:** 2026-10-04
**Authority:** The owner decided in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the questions and recorded the answers.

## Decided object

`PREREGISTRATION.md` §13, rev 7g, at commit `e148a28` (branch `docs/d19-recommendation`).

**Reviews (R19-2):**

| Rev | Fable | Sol | Adjudication |
|---|---|---|---|
| 7b `c09337f` | BF1 UNSOUND `7c7cf49` | BS1 UNSOUND `769f966` | `ADJUDICATION_C09337F.md` |
| 7c `09b0fb9` | BF2 SOUND WITH FIXES `aa6caa7` | BS2 UNSOUND `aa6caa7` | `ADJUDICATION_09B0FB9.md` |
| 7d `9762781` | BF3 SOUND WITH FIXES `ff9eb3a` | BS3 SOUND WITH FIXES `564ebea` | `ADJUDICATION_9762781.md` |
| 7e `9d811e6` | BF4 READY WITH FIXES `23ce5f4` | BS4 READY WITH FIXES `026a23a` | `ADJUDICATION_9D811E6.md` |
| 7f `02c14e5` | BF5 READY WITH FIXES `d69fe25` | BS5 READY WITH FIXES `d46c870` | `ADJUDICATION_02C14E5.md` |

The BF5 and BS5 fixes were minor; they are applied in rev 7g, with no further review.

## Exchange (verbatim)

### Question 1

> "Accept the cheaper calibration plan (D-19 §13 rev 7g)? It runs free on your new server for about 4–5 months (one-strategy families up to 20 strategies, C2 only). It has slightly less power to confirm a real edge than the full plan, but a pass still means what it says. Fable and Sol both checked it over five rounds; last verdicts 'ready', minor fixes applied. Nothing runs until the engine is finished and reviewed."

| Option | Description shown |
|---|---|
| "Accept (Recommended)" | "Plan becomes binding; next I finish the calibration engine and its review." |
| "Not yet" | "Keep it as a proposal; nothing is built for the run." |

**Answer:** **"Accept (Recommended)"**

**Drafter's correction of the question wording.** "One-strategy families up to 20 strategies" was garbled. §13 item 1 means: each family declares 1, 2, 5 or 20 strategies.

### Question 2 (`<<OWNER O18-4-T>>`)

> "The plan tests only C2's exact data length, so it drops the 'unequal lengths' test case you approved earlier (O18-4). Do you agree to drop it?"

| Option | Description shown |
|---|---|
| "Drop it (Recommended)" | "Needed for the cheaper plan; the result covers C2 only, and a later cycle is calibrated again." |
| "Keep it" | "Then the cheaper plan cannot be accepted as written; it would cost far more compute time." |

**Answer:** **"Drop it (Recommended)"**

## Effect

1. **§13 rev 7g is accepted.** It overrides the rev 6 sections that it names, so the accepted preregistration is now rev 6 as modified by §13 rev 7g.
2. **`<<OWNER O18-4-T>>` is answered affirmatively.** The O18-4 "unequal `T`" coverage category is dropped for this qualification object. The object certifies C2 only. A-B7 is unchanged.

## Still required

Acceptance under `OWNER_DECISION_D19_ACCEPT.md` (`ec35a29`) stays incomplete until the owner commits the key record: `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2`.

## Not changed by this decision

- No calibration run, threshold run or pilot on the server is started.
- No cycle starts, no confirmation or lockbox data is read, and no trading is authorized.
- No frozen file is edited, and nothing is activated.
- The engine still needs to be finished, then pass the §16 different-model review and the owner's PR review. It merges only on the owner's word.
- The full-run go-ahead comes later, after the re-pilot on the server has measured the real rates.
