<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12ea8-7b93-7132-ab1b-297ab02f6e3b. Tokens used: 11,890. Made from a packet built from commit e975ddd: the prompt below, the review and adjudication sections of SOL6_S16_REREVIEW_5E56D18.md, git diff 5e56d18 e975ddd -- calibration tests, and z_crit at e975ddd. -->

> # Focused re-review 2: repair of S16R-1 (5e56d18..e975ddd)
> 
> You are an independent adversarial reviewer working read-only, not an authority. Everything is attached. Review ONLY whether S16R-1 (recorded below with its adjudication) is resolved by the diff. Verdict ACCEPT or FIX; any new finding gets a stable ID S16R2-n with severity, file:line and a concrete failure scenario.
> 

## Review (final message, verbatim)

## Verdict: FIX — `e975ddd`

The new bound resolves the supplied `2**50` case, but S16R-1 is still unresolved across finite binary64 inputs.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| **S16R2-1** | Medium | `calibration/choices.py:455–456` | Store `sys.float_info.max` as `z_f*` in 500 replications. `math.nextafter(max_float, math.inf)` is infinity, so converting the computed upper grid index to `int` raises instead of finding a qualifying grid value. |
| **S16R2-2** | Medium | `calibration/choices.py:465` | Store `2.0**100` as `z_f*` in 500 replications with the same restrictive error target. Under the default 28-digit Decimal context, the qualifying grid value needs more than 28 coefficient digits at `.001` precision. The final `quantize(Z_STEP)` raises `InvalidOperation` instead of returning `z_crit`. |

This is a read-only review of the attached code. I ran no checks or made repository changes.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

| ID | Decision | Repair |
|---|---|---|
| S16R2-1 Medium | AGREE, repaired | `z_crit` now searches exact integer grid indices `i` (z = i / 1000). When the next binary64 after the largest stored `z_f*` is infinite, the upper index is `2**1024 · 1000`, the overflow point. `_nearest(i)` gives the nearest binary64 of `i / 1000` through `Fraction`, and infinity on overflow, as IEEE rounding does. |
| S16R2-2 Medium | AGREE, repaired | The `Decimal` grid arithmetic (`mid * Z_STEP`, `quantize`) under the 28-digit default context is gone. The result is built as `Decimal(lo).scaleb(-3)` in a context with enough digits, so it is exact at any size and still has exponent −3. For values the old code handled, results are unchanged: correctly rounded `Fraction` to float equals correctly rounded exact `Decimal` to float. |

Tests: `test_z_crit_has_no_ceiling` adds `2.0**100` and `sys.float_info.max`. Each must give a grid value with exponent −3 whose binary64 is above `z_f*`, while the value one step below is not (checked at 400-digit precision). Local: the 4 `z_crit` tests pass, ruff check and format clean, `mypy calibration` clean. Neither case is realistic: in the pilot about 3% of `z_f*` exceeded 1.96 (`worst_cell_rate_at_1.96`). The repairs are kept because §5 sets no ceiling.
