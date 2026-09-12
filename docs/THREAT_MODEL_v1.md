# THREAT_MODEL_v1.md

Actors: owner, research AI, coding AI, research user, experiment-engine identity,
lockbox_eval identity, predictor, governor, executor, watchdog/alerter, exchange.

Core permissions:
- Research AI/coding AI: exploration only; no direct confirmation/lockbox.
- Experiment engine: may evaluate confirmation after registered hypothesis verification.
- lockbox_eval: lockbox read + attestation signing only; no exchange credentials.
- Predictor: approved live inputs/model, no exchange key.
- Governor: proposal/account/market state + signing key, no exchange key.
- Executor: only holder of exchange trading key; no research/lockbox access.
- Owner: approvals/change-control, but no default raw lockbox access.

Core threats:
- preregistration bypass by exploration on confirmation,
- repeated lockbox probing,
- coding agent weakening tests/referee,
- owner risk escalation during drawdown,
- duplicate order after ambiguous timeout,
- credential leakage,
- stale/mismatched deployed config,
- exchange/custody/stablecoin failure.

Controls are defined by the Constitution and protocols; this document does not weaken them.
