# Owner decision: S16S-3, vol-family sizing in C2 is EWMA_168h only

- Date: 2026-10-17
- Finding: S16S-3 (`SOL6_SCREEN_S16_REVIEW_FC51735.md`, adjudication `ADJUDICATION_SCREEN_S16_FC51735.md`)
- Asked, through the session's question tool, verbatim: "Sol's finding S16S-3: the trading protocol allows volatility trials to size their positions using 5 different volatility measures, but the screen can only test one of them (the 168-hour EWMA). Any trial using another measure is refused today, which is safe but narrows what you can declare. What should the rule be for the C2 test?"
- Options offered: "168h EWMA only (Recommended)"; "Add the 2 other EWMAs"; "Add all 4 measures".
- Owner's answer, verbatim: "168h EWMA only (Recommended)"
- Recorded by the AI from the owner's answer; the AI did not choose for him.

**Effect.** For C2, a vol-family trial is declarable only with sizing estimator `EWMA_168h`. A trial sized by `EWMA_72h`, `EWMA_336h`, `HAR_RV` or `GARCH_1_1` keeps getting `SIGMA_UNBOUND` on every screened gate, so its screen outcome is `INVALID`, until an hourly definition of that estimator is bound and reviewed. No code change. The frozen protocol is not amended: this narrows what C2 can declare and does not change what the protocol permits.
