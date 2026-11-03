# ASTRA review of R-14a modules design rev 1 (3f141fb)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-astra`), 2026-11-01.
- Prompt: scratchpad `r14d_prompt_A.md` (reproduced below the report).
- Finding IDs: R14D-A-n.

## Report (verbatim)

**Verdict: FIX — 3 BLOCKER findings, 2 NON-BLOCKING findings.**

Reviewed `DESIGN.md` at `3f141fb`, governing text at `8a1ec72`, engine code at `eeaa728`, and later object files at `eba1c21`. This is a read-only review; no statistical rules are proposed.

**R14D-A-1 — BLOCKER — Seven gates are incorrectly inventoried as implemented.**

[DESIGN.md:33](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:33) says G-3, G-5, G-6, G-7, G-8, G-11 and G-14 need “glue only”; [§4.3](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:128) consequently calls `screen.screen_gates`.

At `eba1c21`, `calibration/screen.py:1060` implements **availability**, not these gates’ pass decisions:

- Lines 1241–1252 discard `run()`’s statistics and return `None` when computation succeeds.
- Lines 1259–1261 compute plateau neighbours but discard their values; there is no median/boundary pass comparison.
- `g11_check`, lines 1173–1203, computes each draw’s statistics but discards them.
- `g14_check`, lines 1205–1236, computes ICs but discards them.

Thus finite negative ETH improvement produces the same availability result as positive improvement. Likewise, 500 tied null statistics are available, although C-10 and C-12 require FAIL.

**Correction:** inventory the available primitives separately from missing aggregation, reporting and pass comparisons. Allocate all seven complete gate decisions under Q-P1. Do not interpret `None` as PASS.

The remaining inventory resolves as follows. Code references below use the specified revisions.

| Rule | Verified implementation and remaining work |
|---|---|
| Annex B / G-9 | `eeaa728:calibration/dsr.py:evaluate:120` implements numerical refusal rules, bootstrap quantities and nomination. It does not validate timestamps, declaration completeness or evaluation records. `calibration/choices.py:_passes:372` already implements the available-and-`z >= threshold` comparison for its calibration record interface. |
| C-0 / C-6 | `statistics.sharpe:203`, `paired_sharpe_statistics:218`, and `backtest/event_contract.py:run_event_contract:119` exist. The governed caller still owns window/identity/integrity checks. These deserve explicit inventory rows. |
| C-1 / G-1 | Correct: `statistics.paired_sharpe_improvement_interval:591` exists; the governed comparison and caller contract remain. |
| C-2 / G-2 | Correct: `descriptive._max_drawdown:232` exists; `gates.g2:72` checks availability only. |
| C-4 / G-4 | Correct that the production fold statistic/pass rule is missing. `gates.g4:81` is only the calibration length-based availability check—not calendar partitioning or integrity validation. |
| C-9 / G-10 | Correct that PBO scoring/pass is missing. However, `gates.SPLITS:18` already enumerates 12,870 splits, and `gates.g10:87` implements availability calculations. The split machinery is not wholly absent. |
| C-11 / G-12 | `statistics.effective_sample_size:261` exists. Apply the threshold to the nominee’s **declared horizon**; `gates.g12:110` checking all three horizons is a calibration availability routine. |
| C-14 | No complete report implementation found. Existing statistics, quantiles and model helpers are reusable; split training and path construction remain. |
| G-13 | Missing from the design inventory. `DRAFT_WORDING.md:317` requires matching the amended canonical benchmark hash. |
| Annex D / L-1–L-4 | The listed primitives exist, but add `paired_sharpe_statistics`, execution/refit helpers, explicit L-condition evaluation and availability mapping. A4, A6 and bundle construction remain missing as stated. |

**R14D-A-2 — BLOCKER — The proposed verifier rejects the proposed modules.**

[DESIGN.md:102](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:102) says the modules call existing `screen.check_object` for R-14 verification.

At `eba1c21`:

- `screen.check_object:1859` supplies only the object copies of `mapping.py` and `screen.py` as exceptions.
- `mapping.loaded:81` includes every loaded `calibration`/`aqt` module.
- `screen.check_screen_code:1894` rejects anything absent from the engine inventory and supplied exceptions.

Neither proposed `calibration/c2_*.py` exists at `eeaa728`. Importing either and following §3 therefore fails before evaluation. I reproduced this using the unchanged verifier function with synthetic dependencies: the engine-only inventory passed; adding `calibration/c2_lockbox.py` raised `the loaded calibration/c2_lockbox.py is not the run's`.

**Correction:** specify how the existing lower-level checks receive exactly the additional module bytes authenticated through R-14a’s signed chain. Preserve rejection of every other extra module. This can be orchestration of existing functions; it does not require weakening R-14.

The self-hash at [line 99](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:99) also needs an explicit loading contract. Reading `__file__` authenticates the current source file, not automatically the executed code. Preserve `eeaa728:calibration/rundef.py:bytecode_problem:323` and its **before-import** requirements. Test both valid startup and rejection of cached/substituted code; broken-chain tests alone miss the valid-start failure above.

**R14D-A-3 — BLOCKER — The confirmation flow does not yet allocate Annex A’s operative rules.**

[DESIGN.md:39](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:39) defers Annex A’s inventory, but §§4 and 8 already describe the confirmation implementation and build order.

`dsr.evaluate` cannot substitute for the selection procedure. Its nominee is a column index, with ties broken by column order (`eeaa728:calibration/dsr.py:183`); it knows nothing about declared IDs, configuration hashes, completed attempts or the shared look.

The design must allocate:

- P18-0/P18-1 eligibility, complete declared membership and permitted rerun accounting;
- P18-2’s single shared look;
- P18-3’s complete-family availability;
- P18-4’s declared-ID tie order and P18-5’s no-fallback rule;
- every mandatory nominee gate regardless of earlier failures, and P18-7 cause precedence;
- the supported-law classifier and A-V1’s Task-12 comparison/disclosure.

Relevant existing pieces include `classifier.diagnostics:22` and `within:86`, `dsr.evaluate`’s **optional** classifier argument at line 126, and `core/attempts.py`’s accounting functions. That module explicitly disclaims budget/eligibility enforcement at lines 81–90.

For example, omitting an unfinished declared trial from the matrix could produce an available nominee although P18-3 requires the family to be unavailable. Calling `evaluate` without its classifier silently omits that check.

**Correction:** finish the Annex A consumer inventory and name each enforcement function or later-module responsibility before treating §4.3 as complete. Include G-13 and the no-short-circuit rule.

**R14D-A-4 — NON-BLOCKING — Q-P1 is permissible, but its framing and recommendation need revision.**

[DESIGN.md:51](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:51) presents a legitimate placement choice. **Option (a) does not inherently require another governance exception.**

`eeaa728:calibration/qobj.py:56` already includes `screen.py` in `LATER`; line 63 includes it in `REVIEWED`; `_reviewed:199` requires committed bytes, their matching hash and a committed review record. R-14 binds the eventual object copy, not the present `eba1c21` copy forever.

For implementations of already-decided rules, the required route is the stated independent review, owner §16 PR review, updated `FREEZE_REVIEWS.json`, selected build commit and refreshed G0/G evidence. Changing decided rules or the qualification method would be a different matter.

However:

- Option (b) is already owner-decided and authorized; it is not a newly enlarged exception merely because the inventory becomes accurate.
- Earlier binding under (a) is a real benefit, but the recommendation currently rests on an incomplete work estimate.
- “Glue only” understates the remaining result-sensitive orchestration even under (a).
- Lines 63–65 suggest A4’s location is irrevocably fixed, while line 151 offers moving it into `screen.py`. R-14a item 4 is conditional on whether a bound function exists.

Present (b) as the accepted baseline and (a) as an optional earlier-binding change, with corrected scope and schedule costs. Keep C-14 explicitly diagnostic.

**R14D-A-5 — NON-BLOCKING — The acknowledged contract placeholders remain signing blockers.**

[DESIGN.md:187](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:187) correctly labels §6 an outline. Its completion must remain a hard prerequisite to signing, alongside the build/review requirements already listed at lines 15–18.

In particular, the contracts need to make these existing requirements executable:

- Validate original timestamps **before** `screen.path_series` reconstructs timestamps from row positions (`eba1c21:screen.py:911`).
- Specify A6’s exact interval, start, length and positive-equity checks; keep BTC E-DIFF availability independent of ETH/individual-leg availability; do not use `screen.leg_stats` for the lockbox adapter.
- Allocate every A7 field, including **both** module hashes (`ANNEX_D_LOCKBOX.md:327,409`).
- Seal every declared family before the first read, preserving no-nominee status and `(d)` precedence over `(c)` (`Annex D:88`).
- Finish independent beacon verification and the confirmation access path, currently deferred at design lines 115 and 225.

R-14b is already written in `DRAFT_WORDING.md:160`; the remaining obligation is carrying the correct bindings into the signed bytes.

The other requested fidelity checks found **no changed rule in the outline**: seed separation, accepting estimator seed zero, `m=457` sampling over `[0,n)`, the initial draw followed by 456 restart decisions, sealing rerun/hash comparison, 30-day refits, flat starts, final-hour construction and bundle precedence agree with Annex D.

Duplicating A4 and chain-check code is permissible, although not mandated: shared eligible frozen helpers remain allowed. File names do not change a scientific rule. `open_read` is an acceptable interface name provided it preserves the store’s authenticated read gate and per-bar deadline checks; publisher-owned `begin_read` must remain separate.

Validation: `git diff --check 3f141fb^ 3f141fb` passed; the targeted verifier reproduction confirmed R14D-A-2; independent Python checks passed all 28 trusted frozen files, 14 sidecars, Constitution self-hash and manifest/protocol bindings. The protected-file diff from `eeaa728` is empty.

No implementation suite, lint/type/import suite or pinned-image numerical run was performed: this change is a design document. No protected data was accessed. Reviewer: this Codex session; exact runtime model ID was not exposed. The findings remain uncommitted under the requested read-only scope, so the repository’s committed-review requirement is still outstanding.

## Prompt (verbatim)

You are an independent adversarial reviewer (read-only). Review the design document review/r14a-modules/DESIGN.md (rev 1, commit 3f141fb, branch r14a-modules-design) in the repository D:/PMP-programs-for-sharawi/autonomous-quant-trader. Finding IDs: R14D-A-n where {X} is given below. Severity per finding: BLOCKER, NON-BLOCKING, or QUESTION. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.

Governing text (read it; the design must not change any decided rule): the C2 draft on branch freeze-sheet, checked out at D:/PMP-programs-for-sharawi/aqt-freeze-sheet (commit 8a1ec72):
- review/governance-statistics-amendment/r14-exception/OWNER_DECISION_R14A.md, PROPOSAL_REV2.md, PROPOSAL_REV3.md
- review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md (R-13, R-14, R-14a..R-14d around l.155-162), ANNEX_D_LOCKBOX.md (§D-1, §D-3), ANNEX_C_GATE_DEFINITIONS.md, ANNEX_A_SELECTION_RULE.md, ANNEX_B_DSR_METHOD.md
Frozen code: engine commit eeaa728 (`git show eeaa728:calibration/...`, `git show eeaa728:src/aqt/...`), later object files calibration/screen.py, mapping.py, heldout.py at main eba1c21.

Check in particular:
1. The §1 inventory: is each row accurate? Is any C2 gate or rule (Annex A selection, Annex B DSR, Annex C C-0..C-14, Annex D L-1..L-4) actually implemented in frozen code where the design says it is missing, or missing where it says present? Name file and function.
2. Is Q-P1 posed correctly and neutrally, and is option (a) (adding gate statistics to screen.py before step G) compatible with R-14, R-14a and the freeze rules (qobj LATER/REVIEWED, FREEZE_REVIEWS.json), or does it need a governance step the design omits? Is the recommendation justified?
3. Does any [DESIGN] choice change a decided rule or a result (e.g. the module self-hash at import, duplicated chain-check code, duplicated A4 generator Q-D1, file names, store interface)?
4. Fidelity of §4-§5 to Annex D (seeds, sealing order, A4 generator draw order and m != n, pre-read checks, refits, start state, final hour, adapter, bundle precedence).
5. Anything missing that R-14a's conditions require before C2 signing.
Be concrete; cite file:line. Do not propose new statistical rules.
