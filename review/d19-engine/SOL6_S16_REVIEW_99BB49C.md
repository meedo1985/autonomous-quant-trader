<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12e81-3811-7e11-9ae2-7a37c8732492. Tokens used: 154,607. Made from a packet built from origin/d19-calibration-engine 99bb49c (git show only): the prompt below, the whole PREREGISTRATION.md from docs/d19-recommendation fff4e5f, the HEAD text of every non-review, non-test file PR #48 changes (29 files), the names of every test function, and the list of earlier review records. The packet itself (259 KB) is not committed; it is rebuilt from those commits. -->

# Constitution §16 different-model review of PR #48 (head 99bb49c)

## Prompt (verbatim, before the attached material)

> You are an independent, adversarial reviewer working read-only, not an authority. Your shell may not start in this environment, so everything is attached below.
> 
> **Scope.** The whole engine as it would merge into main: calibration/, scripts/d19_*.py, deploy/calibration/, the CI jobs. Each component was already reviewed separately (records under review/d19-engine/, listed at the end), so concentrate on what those reviews could not see:
> 1. cross-component integration: does the end-to-end path (run definition -> seeds -> generator -> rules/DSR/U_G -> chunks -> reduce -> choices -> qualification refusal) implement preregistration §13 rev 7g and §§4-8 as attached, with no gap between components;
> 2. any path by which a qualification result could be produced, or a frozen/accepted value changed, before its preconditions (T_C2, accepted prereg hash, owner key record);
> 3. determinism and resume identity; silent data deletion or correction; error handling that could hide a failure;
> 4. launcher safety on the owner's server (forward paper must be unaffected; no secrets).
> 
> Verdict ACCEPT or FIX. Give every finding a stable ID S16-n with severity (High/Medium/Low), file:line, and a concrete failure scenario. Do not repeat findings already resolved in the listed records unless the resolution is wrong. Say plainly what you could not check.
> 
> ## Preregistration (accepted §13 rev 7g; branch docs/d19-recommendation fff4e5f)
> 

## Review (final message, verbatim)

## Verdict: FIX — PR #48, head `99bb49c`

The current qualification guard refuses every qualification manifest, so I found no path to a **held-out certification result** before `T_C2`, the accepted preregistration hash, and the owner key record. The following gaps remain in the engine and its run procedure.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| **S16-1** | High | [scripts/d19_choose.py:149](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/scripts/d19_choose.py#L149), [calibration/rundef.py:246](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/calibration/rundef.py#L246) | A permitted `pilot-` manifest can use 11,999 development and 299,999 threshold draws across cells covering every category. With favorable event counts, the JSON can say **`"qualifies": true`** before any qualification preconditions hold. The `measurement_only` prose added for earlier finding I1R-5 does not constrain that machine-readable result; it also assumes pilots have fewer than about 7,700 development draws, which `run_plan` does not require. Force the qualification decision false for every pilot. |
| **S16-2** | Medium | [deploy/calibration/RUNBOOK.md:83](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/deploy/calibration/RUNBOOK.md#L83), [RUNBOOK.md:93](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/deploy/calibration/RUNBOOK.md#L93) | §13 requires the run definition to be committed **before** the threshold run. The full-run procedure writes `definition.json`, prints its hash, then starts threshold draws without a pre-run commitment step or a check against one. A replaced definition and new store could be internally hash-consistent without proving which definition preceded the draws. Add and verify the required pre-run commitment before enabling qualification. |
| **S16-3** | Medium | [calibration/choices.py:23](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/calibration/choices.py#L23), [choices.py:446](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/calibration/choices.py#L446) | §5 asks for the smallest qualifying value on the 0.001 grid; it sets no ceiling of 20. If too many stored `z_f*` values are 21, the code returns “no qualifying choice” at 20 although 21.001 qualifies. This adds an unregistered failure condition. |
| **S16-4** | Medium | [calibration/chunks.py:58](https://github.com/meedo1985/autonomous-quant-trader/blob/99bb49c/calibration/chunks.py#L58) | The chunk digest excludes `host`. Removing or changing its recorded CPU, microcode, kernel, or library provenance leaves verification and every chain head unchanged. §13 permits host provenance to differ between chunks; it still requires that provenance to be recorded and disclosed with integrity. Commit it in the chunk hash or a separately verified record. |

**Limits of this review.** I inspected the supplied engine, selected earlier adjudications, and PR #48’s file list; the list shows no changed frozen `docs/`, `protocols/`, `schemas/`, or `specs/` files. The shell failed to start, so I ran no tests, lint, type checks, frozen-byte verification, or server check. The qualification object, held-out runner, declaration mapping, and screen are not implemented at this head; their eventual behavior cannot be certified here. I did not inspect every earlier review record.

Reviewer metadata: Codex, GPT-6 based; the exact serving model ID is not exposed. This read-only response is **not a committed review record**. The project’s §16 process requires the findings and their disposition to be committed before merge.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

| ID | Decision | Repair |
|---|---|---|
| S16-1 High | AGREE, repaired | `scripts/d19_choose.py`: for a `pilot` manifest, `qualifies` and `qualifies_before_coverage` are now always `false`, and the `measurement_only` text no longer assumes pilots stay below about 7,700 development replications. The pilot end-to-end test in `tests/unit/test_calibration_rundef.py` asserts both fields and the text. That test's two replications per cell could not produce `true` under the old code either, so it guards the field and text, not the old failure; the repair is one unconditional assignment. |
| S16-2 Medium | AGREE, repaired in the procedure; check deferred | `deploy/calibration/RUNBOOK.md` step 3 now requires the run definition to be committed to the repository and pushed, with the commit id returned to the owner, before `run threshold`. **Deferred, with an obligation:** the check that this commit predates the first threshold chunk belongs to the qualification object, which is not implemented at this head and is refused by `run_plan` (DR2-1). That item must implement the check. The FE-7 pilot is unaffected: it is not a qualification run. |
| S16-3 Medium | AGREE, repaired | `calibration/choices.py`: `Z_MAX` is removed. `z_crit` searches up to one grid step above the largest stored finite `z_f*` (in any qualifying cell or QJ pair), where no event remains, so any finite set of `z_f*` has a qualifying grid value when the limits allow it, as §5 step 3 says. `None` now arises only from infinite `z_f*` values or a negative limit. Tests: `test_z_crit_has_no_ceiling` (500 × `z_f* = 99.0` gives 99.001; the old code gave `None`), and the `None` test now uses `inf`. |
| S16-4 Medium | PARTLY AGREE (Low), not repaired at this head | `host` is outside the chunk digest by design (`calibration/chunks.py` docstring). It keeps chain heads independent of the host, so a recomputed chunk or a rerun on another machine with the same gating identity reproduces the chain heads that §13 binds into the qualification object. Putting `host` into the digest would make those heads depend on CPU model, microcode and kernel, which §13 says are "never compared". Sol's point stands that the recorded provenance can be edited without detection, which weakens the "disclosed" duty. The threat is an edit to chunk files on the owner's own server, which already has every other way to tamper, so it is Low. **Deferred, with an obligation:** the qualification object, at the freeze, records a hash of each chain's host provenance list next to its chain head, so the disclosed provenance is fixed by the object that held-out chunks bind to. |

Sol's limits are accepted as stated. The qualification object, held-out runner, declaration mapping and screen are not implemented. The S16-2 and S16-4 obligations are recorded for that work.
