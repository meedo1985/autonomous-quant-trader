# Codex Sol review of the pre-freeze screen change design (ceb12c3)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a191c6-05e5-7da2-a3a3-d2064c9d141a`, 109,394 tokens. Reviewed `review/pre-freeze-screen/DESIGN.md` at `ceb12c3`.

Verdict: **FIX**: 3 BLOCKER (PFS-S-1..3), 1 NON-BLOCKING (PFS-S-4), 1 QUESTION (PFS-S-5). No gaps in numbering.

Disposition: none repaired yet. PFS-S-1 (and PFS-S-5 with it) turns on how far R-14's frozen-file route reaches, which is an owner choice; PFS-S-2..4 will be applied in the design revision.

## Report (verbatim)

**Verdict: FIX.** The seed and terminal-price changes follow the owner’s selected Q5 and Q2(ii) options, but the design does not yet preserve the claimed guard or satisfy R-14 at freeze time. This is a read-only design review; no code or tests were run.

| ID | Severity | Place | Failure scenario and minimal repair |
|---|---|---|---|
| **PFS-S-1** | **BLOCKER** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:23), C3 and §3 | `confirmation_gates` returns screen gate *availability*. The design leaves confirmation loading, paired statistics, and the C2 record to later code. Under the proposed R-14, that evaluation code must already be in the engine commit or a frozen later object file. Commit the required C2 coordinator in an eligible later object file before step G, or obtain a formal R-14 change before treating the freeze as preserving this route. The fixed `eeaa728` engine commit cannot supply code added afterward. |
| **PFS-S-2** | **BLOCKER** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:9), T1 | “Every existing output” cannot be bit-identical: `run_screen` records `screen_sha256`, which must change; `screen_job` records elapsed `seconds`, which is not repeatable even on `main`. A new qualification-object hash also changes the held-out seed anchor for a new attempt. Narrow the guard to scientific values for identical inputs and runtime; compare timing and expected identity hashes separately. Keep exact checks for all frozen reference vectors. |
| **PFS-S-3** | **BLOCKER** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:20), T5 | “Rows are finite and positive” and “zero rows” would reject a valid OHLCV bar with zero volume. `Bar` permits finite, **non-negative** volume, and the proposed terminal row itself has volume 0. Require positive finite **prices**, non-negative finite volume, the full `(hours, len(SYMBOLS), 5)` shape, and valid OHLC ordering. Test zero volume as accepted; test zero price as refused. |
| **PFS-S-4** | **NON-BLOCKING** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:41), §4 | The freeze list omits the changed object and downstream identity consequences. The new `screen.py` bytes change the qualification-object manifest and posted object hash; held-out attempts derived from that object will have different anchors. State this explicitly, and update the pinned G command, FP2/G0 evidence, review record, and build checkout together. Do not claim an old and a new object produce identical held-out artifacts. |
| **PFS-S-5** | **QUESTION** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:24), C3 | The wrapper accepts `seed_l266`, `trial_seed`, `window_id`, and `g_days` from its caller without binding them to the trial and C2 declaration. A wrong but well-formed value could produce a reproducible, incorrect evaluation. Specify which frozen C2 entry point verifies their derivation and records the signed policy and seed; this can be resolved as part of PFS-S-1. |

**Design questions**

- **Q-a:** Pass `model_seed` to G-14’s unshifted pipeline. It is the nominee’s own fit. Each null pipeline must continue to replace it with its independently derived `g14_draw` seed; numerical equality by chance is allowed.
- **Q-b:** The runner uses the terminal row’s **open** for the final gross return. `feature_columns` also computes features through the terminal row, and `hourly_log_returns_bps` plus the EWMA computes an extra terminal close-to-close return. Their terminal values are not used by decisions, fits, or fill costs inside the window on the traced paths. Zero terminal volume is safe under `Bar` and these consumers. T4 should distinguish *computed* terminal values from *used* values.
- **Q-c:** **C3 is insufficient under R-14 as drafted.** The C2 evaluation coordinator must be in an eligible frozen file before step G, unless the owner formally changes that binding. The later separate lockbox module follows Q4’s proposed exception and does not supply the missing confirmation coordinator.

T2 and T3 are sound in direction. T4 needs assertions at the actual consumer boundaries; T5 needs the volume correction. T1 needs the narrower guard above. Frozen-vector equality requires the pinned image for S8’s float path; no byte-for-byte validation has been performed in this design-only review.
## Prompt

# Review: design of the pre-freeze `screen.py` change (D-20 Q2(ii), Q5)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/quant-code-review/SKILL.md` and `.agents/skills/scientific-reproducibility-review/SKILL.md` where they apply to a design. The repository is on branch `pre-freeze-screen-q2-q5`. Review `review/pre-freeze-screen/DESIGN.md` (Claude Opus 5.5). No code is written yet.

Ground truth to check it against:
- `calibration/screen.py` (current; `walk_forward` ~l.1499-1565, `screen_gates` ~l.1032, G-14 ~l.1160-1200, `screen_job` ~l.1858), `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`), `review/d19-engine/FREEZE_REVIEWS.json`, `scripts/d19_heldout.py`, `src/aqt/backtest/event_contract.py`, `src/aqt/backtest/costs.py`, the reference-vector tests under `tests/`.
- The governance text lives on the `freeze-sheet` branch (read it with `git show origin/freeze-sheet:<path>`): `review/governance-statistics-amendment/d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md`, `PROPOSAL_REV3.md` (A1b, A6, D20L-31, D20L-34), `PROPOSAL_REV4.md` (A1b, D20L-44, D20L-47, D20L-48), `PROPOSAL_REV5.md` (D20L-55); `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` (R-8, R-13, R-14 ~l.145-152) and `ANNEX_C_GATE_DEFINITIONS.md` (C-0, C-6, C-12 (5)); `deploy/calibration/FREEZE_HELDOUT.md` (FP2, G0, G).

Check:
1. Does the design implement exactly what Q2(ii) and Q5 (A1b `L266_MOD_2_31`, A6 final hour) require, no more and no less?
2. The guard: with defaults, is every existing output (D-19 screen, held-out run, every frozen reference vector) provably bit-identical? Name anything that could break it.
3. Answer the design's questions Q-a (G-14's un-shifted pipeline seed), Q-b (what reads the terminal row; is volume 0 safe; the cost-volatility series), and Q-c (is C3 enough for R-14 at freeze time, or must more of the C2 evaluation be in a later object file before the freeze? Consider R-8's engine commit `eeaa728`, which is already fixed).
4. Are the tests T1-T5 sufficient and sound, and is the freeze-consequence list (§4) complete and correct?

IDs: findings `PFS-S-n`, each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Use exactly that prefix; the caller verifies the model from the CLI header. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
