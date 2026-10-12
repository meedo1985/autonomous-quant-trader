<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12ea6-1509-7351-8760-677e9fe3119a. Tokens used: 12,172. Made from a packet built from commit 5e56d18: the prompt below, the review and adjudication sections of SOL6_S16_REVIEW_99BB49C.md, git diff 99bb49c 5e56d18 -- calibration scripts tests deploy, and calibration/choices.py from _passes to _joint. -->

> # Focused re-review: repairs of S16-1..S16-4 (99bb49c..5e56d18)
> 
> You are an independent adversarial reviewer working read-only, not an authority. Your shell may not start, so everything is attached. Review ONLY whether S16-1..S16-4 (your §16 review of PR #48 at 99bb49c, recorded below with its adjudication) are resolved by the diff, or acceptably deferred where the adjudication says so. Verdict ACCEPT or FIX; any new finding gets a stable ID S16R-n with severity, file:line and a concrete failure scenario.
> 
> ## Your review and its adjudication (verbatim from the committed record)

## Review (final message, verbatim)

## Verdict: FIX — `5e56d18`

S16-1 is resolved. The pilot path unconditionally sets both qualification fields to `false`.

S16-2 and S16-4 are acceptably deferred **at this head**, as adjudicated. The runbook now requires a committed definition before threshold draws; the qualification object still owes the pre-run check and the host-provenance hashes.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| **S16R-1** | Medium | `calibration/choices.py:453–456` | S16-3 remains unresolved for large finite `z_f*`. Give 500 replications `z_f* = 2**50` and the same restrictive error target used by `test_z_crit_has_no_ceiling`. The computed upper grid value is `2**50 + 0.001`, but its binary64 conversion rounds back to `2**50`. Every event still passes, so `z_crit` returns `None`. A later grid value above the binary64 midpoint, such as `2**50 + 0.126`, converts to a larger float and qualifies. Extend the upper bound until its converted value exceeds the largest relevant finite stored `z_f*`, then test this case. |

This is a review of the attached material only. I ran no checks and made no repository changes.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

| ID | Decision | Repair |
|---|---|---|
| S16R-1 Medium | AGREE, repaired | `z_crit`'s upper grid index is now the ceiling of the next binary64 after the largest stored finite `z_f*` (`math.nextafter`), divided by the grid step. That grid value is at least that float as an exact decimal, and round-to-nearest is monotone, so its binary64 is above every stored `z_f*` and no event remains. The `+ 1` is dropped. `test_z_crit_has_no_ceiling` adds 500 × `z_f* = 2**50`: the result converts above `2**50`, and the grid value one step below it converts back to `2**50`, so the smallest one is chosen. |

S16-1 accepted as resolved, and S16-2 and S16-4 as acceptably deferred, by this re-review. Local: ruff check and format clean, `mypy calibration` clean, the 3 `z_crit` tests pass. The full suite runs in CI on PR #48.
