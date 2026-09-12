# Task 3 scientific disposition — APPROVED BY USER

Approval evidence: user explicitly replied "اعتمد" (Approve) in the current conversation after reading the proposal and its limitations. Recorded 2026-09-12T21:35:40.1740380+03:00. Approval covers the five implementation conventions below only; it is not a frozen amendment, live-trading authorization, or final code-review sign-off.

Approved conventions for this implementation:
1. Use hourly close-to-close log returns, consistent with FEATURE_FACTORY_v1.
2. Preserve the current sample variance (ddof=1) over available returns 2..168. From return169 use v_t=d*v_previous+(1-d)*r_t^2, d=2^(-1/168); sigma=sqrt(v). This is the existing zero-mean second-moment convention, not a centered rolling variance. Constant nonzero returns therefore yield positive estimates after initialization. No claim of immateriality on real markets is made.
3. Compute volatility from information available at the decision. Delay stress changes fill time/price and point-in-time fee, but not the volatility information cutoff.
4. Reject any gap in the supplied history up to the decision. Do not delete history, reset EWMA, fill missing returns, or silently select a post-gap segment. This is a guard against unresolved inputs, not approval of outage recovery. An explicit future ingestion/orchestration policy must resolve missing data before such histories can be processed. A caller must not evade this rule by silently slicing the history.
5. Future feature/sizing consumers must explicitly establish estimator equivalence before reusing the EWMA_168h label; this task does not implement them.

These items preserve the frozen interval, half-life, seed, fee/spread/slippage constants and causal execution. They clarify currently unspecified behavior and restrict unresolved inputs. If the owner determines any item changes the frozen contract, it must not be accepted through this note; apply Constitution amendment rules instead. No AI approval is recorded.

Plain-language meaning: retain the current measure of the size of hourly price moves, including persistent moves; stop calculations on incomplete history; use only information known when the decision was made. This approves an implementation convention, not an investment strategy or readiness to trade.

