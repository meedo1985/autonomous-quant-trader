# Owner decision: G-14 applies to sign-target (logistic) model trials (S3R-R3)

- Date: 2026-10-16
- Context: Sol re-review of screen S3 at 7626e2e, finding S3R-R3 (`SOL6_SCREEN_S3_REREVIEW_7626E2E.md`). Annex C rev 4 C-12 (1) makes G-14 mandatory for "trials that fit a model of the vol-scaled target (l.103-105)" and does not say whether a logistic model of that target's sign is one.
- Asked (verbatim): "Some strategies use a model that only predicts whether the price will go up or down over the next 1, 3 or 7 days, not by how much (a logistic model). Should those strategies also have to pass the shuffled-labels safety test (G-14)? That test checks the model does better than one trained on scrambled answers. The rules say it applies to models of 'the vol-scaled target' and don't say whether an up/down model counts."
- Options offered: "Yes, apply it (Recommended)": stricter, every model strategy must beat scrambled answers; "No, skip it for up/down models": looser, one less check.
- Owner's answer, verbatim: "Yes, apply it (Recommended)"
- Recorded meaning: in `calibration/screen.py` TI-5, G-14 is mandatory for every model trial, including `logistic` with target `sign_of_vol_scaled_target`; it is a frozen N/A only for trials without a model. This is the screen's binding of C-12 (1). It does not amend Annex C; if Annex C is revised before signing, this reading should be written into C-12 (1).
- Recorded by the AI from the owner's answer; the AI did not choose for the owner.
