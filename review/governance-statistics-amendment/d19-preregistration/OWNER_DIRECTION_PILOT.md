# Owner direction after the measured pilot (2026-10-04)

The owner answered in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the question and recorded the answer.

## The question, verbatim

> "The measured pilot shows the D-19 calibration is a big computation: about 13,000 CPU-hours as built (about 3 months on this laptop), or roughly 3,000-4,500 CPU-hours after speed-ups (about a month here, or a few days of rented computing, likely a few hundred US dollars, not yet quoted). The speed-ups compute the same numbers a faster way, which the accepted plan doesn't yet allow, so they need a small plan amendment checked by Fable and Sol plus your OK. How should we proceed?"

## The options shown

| Option | Description shown |
|---|---|
| "Speed up, then decide (Recommended)" | "I draft the amendment (fast maths + a 1% exact cross-check that voids the run on any mismatch), get it reviewed, optimise the engine, re-measure, then you choose laptop vs rented compute. No money spent until you choose." |
| "Pause D-19" | "Stop the calibration work here (engine and findings stay saved). Promotion stays blocked; forward paper trading continues. Focus elsewhere." |
| "Run as built, locally" | "No amendment: use the exact maths on this laptop. Very slow (months), and the laptop's 8 GB memory may interrupt runs." |

## The answer

**"Speed up, then decide (Recommended)"**

## What this authorizes

- **Authorized now:**
  - drafting the rev 7 amendment;
  - its two reviews;
  - optimising the engine on its branch;
  - re-measuring the pilot.
- **Still needs the owner:**
  - accepting rev 7;
  - any compute choice or spending;
  - any threshold, development or held-out run.
- **Changes no accepted text.** Rev 6 stands until rev 7 is accepted.

## Note on what the question said and what rev 7 proposes

Rev 7 keeps the **1%** exact cross-check that was shown to the owner. It adds an exact recomputation of every replication close to the threshold.

One point is stricter than the question's wording ("voids the run"), and it is put to the owner when rev 7 is reviewed:
- a mismatch found in a **held-out** run counts as a **failed attempt** (P18-6), so no free retry is possible;
- in development, a mismatch means the engine is fixed and development is re-run.
