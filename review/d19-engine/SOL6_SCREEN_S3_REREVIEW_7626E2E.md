# §16 different-model re-review of the screen slice S3 at 7626e2e

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14613-afee-7823-845d-2170f19e6367)
- Date: 2026-10-16
- Prompt: `SCREEN_S3_REREVIEW_PROMPT.md`; packet: the prompt, its review of 40d1402, `ADJUDICATION_SCREEN_S3_40D1402.md`, Annex C C-12 (1), frozen protocol models block, the diff 40d1402..7626e2e, `calibration/screen.py` and its test at 7626e2e
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S3R-R1 (High), S3R-R2 (High), S3R-R3 (High, needs a decision), S3R-R4 (Medium). S3-R4, S3-R5 resolved; S3-R6 helper resolved (runner obligation stays); S3-R1..R3 partly resolved. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S3 at `7626e2e`. The repair closes several original findings, but three bindings remain unresolved.

| ID | Severity | Location | Finding and concrete failure scenario |
|---|---|---|---|
| S3R-R1 | High | `calibration/screen.py:412,420` | `load` does execute the declared module’s hashed bytes, fixing the cached-target case. But `find_spec("pkg.signal")` imports `pkg` first, contrary to TI-2’s claim that package `__init__` is unused. The hashed signal can also import an arbitrary local helper. Changing `pkg/__init__.py` or that helper while leaving `signal.py` unchanged can change the result; the stated S7 check covers loaded `aqt`/`calibration` modules, not these dependencies. Python [documents the parent import](https://docs.python.org/3.13/library/importlib.html#importlib.util.find_spec). Bind or restrict these imports, and state the S7 boundary explicitly. |
| S3R-R2 | High | `calibration/screen.py:315,333,402` | Tau and sigma neighbours are now expressible, and signal parameters reach `signal(inputs, params)`. Model parameters remain ambiguous: a trial can declare `model.params={"alpha":"1"}` and `parameter_point={"alpha":"10"}` with an alpha grid. It passes, while `signal_params` sends `"10"` only to the signal and nothing binds the model fit or its G-8 neighbours to that point. |
| S3R-R3 | High | `calibration/screen.py:319,397` | The declared sign objective repairs the logistic preregistration gap, but G-14 applicability needs a clause-specific decision. C-12 (1) says “fit a model of the vol-scaled target”; a logistic model declared with `sign_of_vol_scaled_target` fits sign labels. TI-5 treats that as automatically within C-12. Decide and record whether G-14 is mandatory or frozen `N/A` for this target before accepting the binding. |
| S3R-R4 | Medium | `tests/unit/test_calibration_screen.py:298,338` | The refusal tests would miss relevant regressions: the load test uses only a top-level module, and the G-14 test validates a logistic declaration but never asserts `g14_applies(logit)`. No valid vol-family case tests a sigma point that differs from the top-level sigma. Those paths could regress while these tests pass. |

**Earlier findings:** S3-R4 and S3-R5 are resolved by the family and mapping-key checks. S3-R6’s helper checks the stated overlay rule; its use on every run remains a later runner obligation. S3-R1 through R3 are only partially resolved as detailed above.

I could not rerun validation: the local shell failed before process creation. The reported 46 passing tests are the supplied result. This read-only response makes no repository review record or commit.