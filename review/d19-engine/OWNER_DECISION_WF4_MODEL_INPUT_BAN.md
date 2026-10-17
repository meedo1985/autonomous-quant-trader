# Owner decision: the REG (A) sizing-estimator ban also covers a model's input features (WF-4)

- Date: 2026-10-17
- Context: screen slice S6 design (`SCREEN_S6_DESIGN.md`, reading WF-4). Annex C rev 4 C-10 (1) (REG (A), D-20 B5) bans `sigma_hat`, the sizing estimator's output and any frozen feature identical to it (currently `ewma_vol_168h` for a trial sized by `EWMA_168h`) from a trial's `s_inputs`. It does not mention the inputs of the trial's model, whose prediction can be an `s_input`.
- Asked (verbatim): "A strategy sizes its position using a volatility estimate, and the rules ban feeding that same estimate into its entry signal, so the signal can't secretly copy the sizing. The ban covers the signal's direct inputs. It doesn't say anything about a model's inputs. A model fed that volatility estimate could pass it into the signal through its prediction. Should the same ban apply to a model's input features?"
- Options offered: "Yes, ban it for models too (Recommended)": stricter, the ban cannot be bypassed through a model, and the other volatility features stay available; "No, signal inputs only": looser, exactly as written.
- Owner's answer, verbatim: "Yes, ban it for models too (Recommended)"
- Recorded meaning: in `calibration/screen.py`, a model's declared input features are checked with the same rule as `s_inputs` (TI-3): never `sigma_hat`, and never the frozen feature identical to the trial's sizing estimator. This is the screen's binding of C-10 (1). It does not amend Annex C; if Annex C is revised before signing, this reading should be written into C-10 (1).
- Recorded by the AI from the owner's answer; the AI did not choose for the owner.
