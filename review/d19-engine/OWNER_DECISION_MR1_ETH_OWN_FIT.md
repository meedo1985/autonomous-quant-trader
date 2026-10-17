# Owner decision: a model trial's ETH run fits on ETH's own data (MR-1, S6B-R2)

- Date: 2026-10-17
- Context: screen slice S6b, reading MR-1; the Sol review of S6b at b00d59b (S6B-R2) found that "BTC and ETH evaluated jointly inside the same trial" (protocol `trial_unit`) settles trial accounting, not whether G-3's ETH run fits its own models or reuses the BTC-fitted ones, and that this is the owner's to decide.
- Asked (verbatim): "A model strategy is tested on Bitcoin, and also on Ethereum as a sanity check (G-3: it must not lose against the ETH benchmark). For the Ethereum check, should the strategy train its own models on Ethereum data (same settings, Ethereum's own history), or reuse the models trained on Bitcoin and just feed them Ethereum's inputs?"
- Options offered: "Train on Ethereum's own data (Recommended)": the same recipe retrained on Ethereum; "Reuse the Bitcoin-trained models": a transfer test.
- Owner's answer, verbatim: "Train on Ethereum's own data (Recommended)"
- Recorded meaning: in `calibration/screen.py` (MR-1), every run of a model trial on a symbol runs the trial's whole walk-forward on that symbol's own rows; G-3's ETH run fits on ETH. G-14's rows stay BTC only (C-12 (2)). This binds the screen's reading for C2; it does not amend Annex C.
- Recorded by the AI from the owner's answer; the AI did not choose for the owner.
