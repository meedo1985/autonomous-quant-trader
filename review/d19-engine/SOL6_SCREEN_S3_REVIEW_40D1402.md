# §16 different-model review of the screen slice S3 (trial interface) at 40d1402

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1460e-93ff-79d1-881b-af55a9cb4255)
- Date: 2026-10-16
- Prompt: `SCREEN_S3_REVIEW_PROMPT.md`; packet: the prompt, Annex C rev 4 C-0 excerpt, C-8, C-10, C-12, DRAFT §2.5, frozen protocol lines 108-175, FEATURE_FACTORY_v1, `calibration/screen.py` and its test at 40d1402, local validation results
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only and did not rerun pytest.
- Findings: S3-R1 (High), S3-R2 (High), S3-R3 (High), S3-R4 (Medium), S3-R5 (Medium), S3-R6 (Medium). Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX.** The direct REG (A) falsifier is implemented, and TI-3, TI-4, and the local TI-7 comparison follow the attached text. The following gaps prevent the S3 interface from binding a trial unambiguously.

| ID | Severity | Location | Finding and concrete failure scenario |
|---|---|---|---|
| S3-R1 | High | `calibration/screen.py:345` | `load` hashes `spec.origin`, then returns a function from `import_module`. If that module was imported before its source changed, the hash can match the new file while the returned function remains cached old code. Importing a child can also execute an unhashed package `__init__`. The test covers neither case. TI-2’s code binding is therefore unsound. |
| S3-R2 | High | `calibration/screen.py:291`, `:359` | The grid has no binding to executed parameters. A trial with top-level `tau="0.80"` and `parameter_point={"tau":"0.40"}` passes, while G-8 would treat 0.40 as the selected point. Signal code receives only the input arrays, so a grid change to a signal parameter such as `span` has no declared way to change its behavior. Later neighbour runs cannot reliably implement C-8 from this interface. |
| S3-R3 | High | `calibration/screen.py:274` | TI-5 equates having a model with fitting the vol-scaled target, but the declaration has no target or objective field from which to fix C-12 applicability. It also accepts `logistic` with empty params and no preregistered sign objective, contrary to the frozen protocol. A G-14 `N/A` versus mandatory decision cannot be recovered reliably later. |
| S3-R4 | Medium | `calibration/screen.py:257`, `:269` | Any nonempty `family` is accepted; `"fixed_size"` passes and receives the default sigma. C-10 expressly excludes a fixed-size class. The tests do not exercise this declaration. |
| S3-R5 | Medium | `calibration/screen.py:283`, `:296`, `:330` | Keys in `model.params`, `parameter_point`, and `grid` need not be strings. Thus `{1: 72}` and `{"1": 72}` pass validation; ordinary JSON object serialization gives them the same key spelling, creating a trial-hash ambiguity, or a canonical serializer may fail only after validation. Require canonical string keys before hashing. |
| S3-R6 | Medium | `calibration/screen.py:261`, `:345` | An overlay reference to a callable that returns `0.5 * target` passes S3, although C-10 allows only the target or zero. The later runner needs an explicit output check on every run; the present tests would not catch its omission. |

TI-1’s ordered set hash and the named `s_inputs` ban appear faithful on the supplied code. The required falsifier test rejects both `sigma_hat` and the identical `ewma_vol_168h` feature for `EWMA_168h` sizing. The materially different readings are TI-2’s assumption that hashing a file binds the imported callable, TI-5’s assumption that every declared model fits the G-14 target, and TI-6’s treatment of an unbound grid as executable trial parameters.

**Validation limit:** the shell failed before starting a process, so I could not inspect the repository or run pytest. The reported 55 passing tests are the supplied local result, not an independently reproduced result. No files were modified.