# Adjudication of the re-checks of D-11 revision 3, and the owner-facing text

Records: `SOL_REREVIEW2_6CE228C.md` (gpt-6-sol, FIX; its findings are recorded as D11R3-S-1..S-5) and `ASTRA_REREVIEW2_6CE228C.md` (gpt-6-astra, FIX, D11R3-A-1..A-3). Adjudicated by Claude Opus 5.5 (the coordinator, not the proposal's author), 2026-10-25.

| ID | Disposition |
|---|---|
| S-1 (executable lookup assumed; current `experiment.schema.json` and trial-record writer do not establish where trial code, configuration and model seed are stored) | **Accepted. It becomes a condition carried into D-20.** The D-11 binding is conditional on D-20 defining the stored artifact identity and a verified retrieval path for the nominee's trial code, configuration and model seed. Until then, the lockbox cannot run. Not repaired in the D-11 text. |
| S-2 (day-255 cap and 75-day window both apply unless displaced) / A-1 (Q3 overstates the cost: reading (ii) needs timing changes only for a window longer than `L+35` days; reading (i) fits 215 days with a day-120 look) | **Accepted, both.** The owner-facing Q3 below says what both reviewers support: a future window is constrained by both timing rules unless the amendment displaces one; a short window (≈3–7 months) may fit some schedules and is a weaker test; a 15-month window needs the cycle cap raised to ≈497 days; every variant needs the partition and "15 months" amendments. D11-15 stays open for the S4 draft. |
| S-3 (the 7-day allowance placed before the read although run and verification follow it) | **Accepted.** The §9 figures are illustrative upper bounds. The exact future-window schedule is not decided here; it is not the recommended option. |
| S-4 (sealing statuses (c) and (d) overlap) | **Accepted:** (d) `UNAVAILABLE` takes precedence over (c). |
| S-5 / A-2 (Q2 states the matching start as fact; it depends on binding the confirmation baseline start, D11-16) | **Accepted.** Q2 below says so. |
| A-3 (starting flat does not force a day-one entry cost) | **Accepted.** Q2 below: each leg pays its entry cost when its first permitted entry occurs. |
| Sol: "every option needs code" should exclude Keep blocked | **Accepted** in Q1 below. |

**Review loop stopped here by the coordinator** (`quant-model-handoff` step 6: stop at resolved findings). Three rounds were run (R19-2 review, re-check, re-check 2) by gpt-6-sol and gpt-6-astra; every finding was accepted and either repaired or carried forward as a stated condition. The repairs in this file were **not** re-reviewed, and **no ACCEPT verdict was obtained**. The owner decides with that disclosed.

## Owner questions as asked

**Q1.** What should the lockbox's main BTC test measure? (Every option except "Keep blocked" needs new reviewed code: the lockbox rows of D-20.)
- "Average daily difference, as written (Recommended)": BTC passes only if its average daily return over the lockbox beats the benchmark's (it need not win every day) and is not unexpectedly low against the range predicted from confirmation. The frozen rule text is kept, and the test checks the same claim your luck test certifies. A smoother strategy that earns less on average fails; how often that happens to good strategies is unknown.
- "Sharpe minus Sharpe": the frozen rule text must be rewritten, and the test checks a claim the luck test never certified.
- "Keep blocked": C2 cannot be signed as drafted.

**Q2.** May the lockbox checker read the price history from 2022-11-13 to 2025-05-31 and run the strategy exactly as registered? It would look up and check the registered strategy by fingerprint (where that is stored is still for D-20 to define), retrain it itself, and start both the strategy and the benchmark with no position on 1 June 2025. Each pays its entry cost when it first enters. This is a new choice; it matches the confirmation runs only once D-20 binds their start the same way. Research gets only PASS/FAIL; the attestation record gets the coarse fields D-12 decides; you receive the attestation.
- "Yes, add it to the C2 amendment (Recommended)": this changes Constitution §7a and the threat model. Data flows only into the most locked-down program.
- "No / decide later": the lockbox cannot run, so there is no promotion in C2.

**Q3.** The lockbox period (June 2025 to August 2026) had already ended when the rules were frozen, and its prices are public. What should happen?
- "Keep it as a held-back historical check (Recommended)": the amendment adds a Constitution sentence, "future" = later than confirmation and held back from research. You give up any claim that it is a fresh test: it catches over-fitting to confirmation, not strategies shaped by public 2025–26 prices. Later paper trading is fresh only under its own rules, fixed in advance.
- "Use a truly future window": a short window (about 3–7 months, a weaker test) may fit the current timing rules for some schedules; 15 months needs the cycle limit raised to about 497 days; every version needs amendments, and the lockbox read waits until the window has passed.
- "Decide later": the lockbox cannot run until decided.
