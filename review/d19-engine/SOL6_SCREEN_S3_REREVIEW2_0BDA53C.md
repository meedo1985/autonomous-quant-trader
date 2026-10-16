# §16 different-model re-review 2 of the screen slice S3 at 0bda53c

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14618-8fc7-7a23-bf83-ea8ef7770628)
- Date: 2026-10-16
- Prompt: `SCREEN_S3_REREVIEW2_PROMPT.md`; packet: the prompt, its re-review of 7626e2e, `ADJUDICATION_SCREEN_S3_7626E2E.md`, the diff 7626e2e..0bda53c, `calibration/screen.py` and its test at 0bda53c
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S3R2-R1 (High), S3R2-R2 (Medium), S3R2-R3 (Medium). S3R-R4 resolved; S3R-R3 default and PENDING marking stated correctly. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S3 at `0bda53c`. The repair addresses the named test gaps, but the source and diff show three remaining defects.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| S3R2-R1 | High | `calibration/screen.py:460–473` | `check_code` checks an import’s root, so it accepts `from numpy import load` and `from numpy import *`. A hashed signal can call `load("unhashed.npy")`; changing that file changes the result without changing the declared source hash or image. The NumPy file reading path is also accepted as `np.load`, as the new test demonstrates. TI-2’s self-contained claim remains false. |
| S3R2-R2 | Medium | `calibration/screen.py:290,480` | `load` rejects a dotted module before `find_spec`, resolving the package execution risk. But `_code_ref` lets `check_trial` and `trial_set_sha256` accept `signal="calibration.seeds:sha"`; the test fixture itself uses that value. The interface hashes a declaration that execution must refuse. |
| S3R2-R3 | Medium | `calibration/screen.py:379` | The `model.<name>` point comparison uses Python equality. With `model.params={"alpha": True}` and point/grid value `{"model.alpha": 1}`, `check_trial` accepts the distinct JSON value, and `model_params` supplies `1` to the fit. The new test covers string mismatches but misses this case. |

**S3R-R4:** The added tests cover the previously requested package rejection, logistic G-14 default, and vol-family sigma point. The import and model tests do not catch the scenarios above. The attribute scan also refuses a harmless local `obj.open()` method; that matches TI-2’s stated blanket name ban, so I have not counted it as a separate defect.

**S3R-R3:** `g14_applies` keeps G-14 mandatory for every model trial, and TI-5 explicitly marks the logistic sign-target binding **PENDING** for the owner. That states the intended stricter default and pending status correctly.

This is a read-only packet review. The local command runner failed before process creation, so I could not independently verify the reported 55 tests or lint, type, and import checks. I made no repository review record or commit.