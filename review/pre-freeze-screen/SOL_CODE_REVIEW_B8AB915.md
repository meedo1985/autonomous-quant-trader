# Codex Sol code review of the pre-freeze screen change (b8ab915)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a1920f-103c-7633-b2ee-66ca9cd74e55`, 88,090 tokens. Reviewed `git diff ed8aa76 b8ab915 -- calibration/screen.py tests/unit/test_calibration_screen.py` as the freeze review of the changed `screen.py`.

Verdict: **FIX**: 3 BLOCKER (PFSC-S-1..3), all on tests. No gaps in numbering.

Disposition: all three to be repaired in the tests; `screen.py` is not changed by the repair. None left unrepaired.

## Report (verbatim)

**Verdict: FIX.** The changed code routes the nominee seed and constructs the terminal row as design C1/C2 specify. I found no demonstrated code-path regression, but the committed tests do not provide the evidence rev 3 requires for freezing this file.

| ID | Severity | Place | Failure scenario and minimal repair |
|---|---|---|---|
| **PFSC-S-1** | **BLOCKER** | [test_calibration_screen.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_screen.py:2114), [DESIGN.md](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:47) | T1’s committed comparison with `ed8aa76` is absent. The default-versus-explicit-zero assertion cannot detect a change shared by both paths, and the caller’s uncommitted 18-value hash does not cover `screen_job`. Add baseline fixtures and compare the four specified APIs’ scientific values exactly, excluding only timing and changed identity hashes. |
| **PFSC-S-2** | **BLOCKER** | [test_calibration_screen.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_screen.py:2083) | T3 asserts only `set(seeds) == {777, 424242}`. It could pass if an emission fit uses a null seed, or a null fit uses the nominee seed, provided both values occur somewhere. Record seeds by emission, unshifted G-14, and each null draw; assert each route separately. The existing six-class `build_model` reproducibility test helps, but the new walk-forward repeat test covers only two classes. |
| **PFSC-S-3** | **BLOCKER** | [test_calibration_screen.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_screen.py:2169) | T4 checks BTC benchmark targets and fills, plus model emissions. It does not compare candidate targets, decisions and costs, ETH, or fit inputs as rev 3 requires. Its final-price check establishes the derived bar’s open, but does not assert the runner’s final return against that price. Extend the successful synthetic pair through those consumers and assert the final return directly. |

T2’s lowercase-hex mapping and T5’s price, volume, shape, and OHLC checks match [Bar](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/data/bars.py:122). The code keeps `model_seed=0` for existing screen calls; G-14 draws still replace it with their own seed. T1b compares the computed paths vector exactly with the stored value, which is also present at `ed8aa76`, but its pinned-image check was skipped in the caller’s Windows run.

I ran `git diff --check ed8aa76 b8ab915 -- calibration/screen.py tests/unit/test_calibration_screen.py` successfully. I did not rerun pytest or the caller’s one-off hash comparison in this write-nothing review, so the reported suite counts remain caller evidence. Before the object can freeze, the repaired review record and new `screen.py` hash must be committed and named in `FREEZE_REVIEWS.json`; its current entry names the old file.
## Prompt

# Code review: pre-freeze `screen.py` change (D-20 Q2(ii), Q5) at b8ab915

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/quant-code-review/SKILL.md` and `.agents/skills/scientific-reproducibility-review/SKILL.md`. Branch `pre-freeze-screen-q2-q5`. Review `git diff ed8aa76 b8ab915 -- calibration/screen.py tests/unit/test_calibration_screen.py` (Claude Opus 5.5) against the design `review/pre-freeze-screen/DESIGN.md` rev 3 (963bc2b) and its reviews in the same folder. This file is a later object file of the D-19 qualification object (`calibration/qobj.py` `LATER`/`REVIEWED`); this review's record will be the one `review/d19-engine/FREEZE_REVIEWS.json` names for the new `screen.py`, so judge it as the freeze review of the whole changed file, not only the diff.

Context: the R-14a decision is `git show origin/freeze-sheet:review/governance-statistics-amendment/r14-exception/OWNER_DECISION_R14A.md`; D-20 A1b/A6 in `origin/freeze-sheet:review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md` and `PROPOSAL_REV4.md`; Annex C C-6 and C-12 (5) in `origin/freeze-sheet:review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md`.

Caller's evidence (verify, don't trust): full suite on Windows host venv: `pytest --ignore-glob=tests/unit/test_calibration_*` 1856 passed 9 skipped; `pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py` 478 passed 1 skipped (T1b skips off the pinned image); ruff format/check, mypy src, lint-imports clean. A one-off T1 guard script hashed 18 return values (walk_forward and model_column for ridge/logistic/lightgbm at lag 0/1, a G-14 draw, screen_gates for three model trials) with default arguments at ed8aa76 and at the branch: identical hash `793b607d…6906`. That comparison is not in the suite.

Check: 1. defaults bit-identical (screen_job, held-out runner `scripts/d19_heldout.py`, reference vectors); 2. seed routing exactly as design C1 (nominee fits, G-14 un-shifted, null draws unchanged), validation of `model_seed`; 3. `confirmation_path` exactly as C2 incl. validation vs `aqt.data.bars.Bar`; 4. tests T1b-T5 sound (do they test what they claim? would they catch a regression?); 5. anything else that would make this unfit to freeze.

IDs: `PFSC-S-n`, each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
