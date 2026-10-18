# Owner decision: which screen set sizes are feasible (prereg §12 item 2), 2026-10-18

The owner answered in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the questions and recorded the answers.

**Evidence:** the third screen pilot, `review/d19-engine/PILOT_SCREEN_EVIDENCE.md` step C (commit `c9a5ad3`). 20 trials × 30 paths, engine `4fed8f5`, pinned runtime. It took 84,135 worker-seconds and 11 h 46 min on 2 workers.

## Question 1, the recommendation shown (verbatim)

> "**Your decision on which set sizes are feasible** (prereg §12 item 2). My recommendation from earlier:
> - **Rules and linear-model sets:** feasible (about 4–20 hours per screen).
> - **LightGBM:** limit it to a few trials per set, since 20 LightGBM trials take about 3 days per screen."

Earlier in the same session, with the cost table, the owner had been told: "This is your call, not mine."

**Answer:** "accept recommendation"

## Question 2, making "a few" exact (verbatim)

> "How should the limit on a set's screen cost be written down?"

| Option | Description shown |
|---|---|
| "60 worker-hours (Recommended)" | "A set can be declared only if its estimated screen cost is at most 60 worker-hours (about 30 hours on your 2 workers). The estimate uses the measured costs: rules 0.43, linear models 2.0, LightGBM 7.3 worker-hours per trial. In practice: every size of 1, 2 or 5 trials is fine, and a 20-trial set can have at most 3 LightGBM trials if the rest are linear models, or 7 if the rest are rules." |
| "Max 3 LightGBM per set" | "A simple count: at most 3 LightGBM trials in any set, with no other limit. Easier to read, but it doesn't cover other expensive mixes." |
| "24 hours wall time" | "A stricter limit: at most 48 worker-hours (one day on 2 workers). A 20-trial set could then have only 1 LightGBM trial with linear models, or 5 with rules." |

**Answer:** "60 worker-hours (Recommended)"

## The decision

A set can be declared in C2 only if its estimated screen cost is **at most 60 worker-hours**. The estimate is the sum over its trials of the measured cost per trial of its kind:

| Kind | Worker-hours per trial (30 paths) |
|---|---|
| Rule (trend, volatility) | 0.43 |
| Linear-family model (linear, ridge, lasso, elastic net, logistic) | 2.0 |
| LightGBM (measured at its largest allowed size) | 7.3 |

Arithmetic check: a 20-trial set with 3 LightGBM trials and 17 linear models costs 21.9 + 34 = 55.9 (allowed); with 4 and 16 it costs 29.2 + 32 = 61.2 (not allowed). With rules, 7 LightGBM trials cost 51.1 + 5.6 = 56.7 (allowed); 8 cost 58.4 + 5.2 = 63.6 (not allowed). Every set of 1, 2 or 5 trials is at most 5 × 7.3 = 36.5 (allowed). 20 linear models cost 40 (allowed).

## What this does and does not do

- It settles §12 item 2 for the screen: no declarable size {1, 2, 5, 20} is infeasible in itself. Only mixes above 60 worker-hours are.
- It changes no accepted preregistration text, threshold or statistic. It runs nothing.
- **Not enforced in code.** `declare` does not check this limit. It is a rule for drafting the C2 declaration. Enforcing it in code would be a separate task, needing its own review.
- **A kind not measured** (for example, a model family outside the six piloted) has no cost figure. Its cost must be measured before a set containing it can be declared.
