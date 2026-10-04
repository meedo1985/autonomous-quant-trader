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

## Second direction (2026-10-04, after finding 3, `37680d0`)

### Question (verbatim)

> "The calibration pilot has found the real cost. Keeping the exact original arithmetic is impossible here (tens of thousands of CPU-hours). The clean fix: define the inside-the-bootstrap Sharpe calculation as ONE fast, fixed method used identically in the calibration AND in every real evaluation (so there is no 'fast vs exact' doubt that Sol objected to). Even then the full calibration is about 8,000-12,000 CPU-hours: roughly 2-3 months on this laptop, or about a week on rented computers (likely a few hundred US dollars, not yet quoted). How do you want to proceed?"

### Options shown

- "Fast method, then decide compute (Recommended)": "I draft the binding (D-20) for the one fast method, get it reviewed by Fable and Sol, re-measure, then ask you laptop-months vs rented-week. No money spent until you choose."
- "Shrink the test"
- "Pause D-19"

### Answer

**"Fast method, then decide compute (Recommended)"**

### What this authorizes

- **Authorized now:** drafting the D-20 binding of the DSR replicate Sharpe to one deterministic vectorised method `V`, with the matching wording change to draft R-8; its two reviews; building `V` into the engine; re-measuring.
- **Not authorized yet:** the D-20 decision itself (owner), and any compute run or spending (owner).

## Third direction (2026-10-04, after the compute plan `706df5a`)

### What the owner said (verbatim)

> "its alot of money i cant handel that can we do less i can sped 3-10$ in month that all"

### The question (verbatim)

> "With a budget of $3-10/month, renting computers is out. How should the calibration be done?"

### Options shown

- **"Shrink it, run on laptop (Recommended)"**: "Free. About 100 scenarios instead of 380: only C2's real data length, families of at most 20 strategies (not 80), 10,000+10,000 runs instead of 22,000+20,000. About 2,000 CPU-hours = roughly 2.5-3 weeks of the laptop on mains power (pausable, e.g. nights only). Trade-offs: covers only cycle C2 (later windows need their own calibration, years away); you could declare at most 20 strategies per family; the pass bar gets slightly stricter (a real edge is a bit harder to detect). Needs a plan amendment reviewed by Fable and Sol, then your OK."
- **"Full plan on laptop"**
- **"Pause D-19"**

### Answer

**"Shrink it, run on laptop (Recommended)"**

### Effect

- **Spending.** The owner's budget is $3–10 a month, so no rental is planned and the `COMPUTE_PLAN.md` options A and B are set aside.
- **What is authorized now:** drafting preregistration rev 7 (the budget version); its two reviews; finishing the engine for a laptop run.
- **What still needs the owner:**
  - accepting rev 7;
  - the go-ahead for the runs.
- **To be put to the owner at acceptance.** Certifying one data length narrows decided O18-4 ("unequal clusters and `T`"). That narrowing is asked explicitly.
