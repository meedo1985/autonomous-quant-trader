# Sol review: R-14a confirmation module, slice 4a (seeds), at ef33d67

- Reviewer: Codex CLI v0.164.0, model `gpt-6-sol` (as requested on the command line and
  printed in the session header), reasoning effort high, sandbox read-only, session
  `01a1bf8b-fd8a-7b21-b352-5b642a6e8ce4`, 2026-11-09. The reviewer itself reports only
  "GPT-6 based"; the exact deployment ID is not exposed. Tokens used: 90,492.
- Prompt: `review/r14a-modules/SLICE4A_CONFIRMATION_PROMPT_SOL.md` (diff `15941ad..ef33d67`
  over `calibration` and `tests`).
- A first run (session `01a1bf50-e50a-7d81-8d82-397404954f49`) was stopped by the host
  for low memory before producing any finding; it has no output to record.
- Author: Claude Opus 5.5. The review is independent feedback, not approval.
- Adjudication: in a separate record (`ADJUDICATION_SLICE4A_EF33D67.md`).

## Reviewer output (verbatim)

**Verdict: FIX.** This is independent, read-only feedback, not approval. The seed formulas and local beacon checks match the cited rules, but the line-266 seed is not authenticated.

- **R14S4-S-1 — BLOCKER — [c2_confirmation.py:1168](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1168).** A caller can supply `line266=lambda **kw: "0"*64`; `derive_seeds` accepts it and records an estimator seed of 0, even when the frozen `trial_seed` returns another value. The lockbox [takes `seed_l266` from the request](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:642) and recomputes only the estimator seed from it. This violates R-8’s frozen-function binding and DESIGN §5.1’s requirement to verify seeds against governing records. Resolve LG4-6 with a verified route to the exact frozen function on the pinned image, and refuse evaluation until that route is bound. A 64-hex output check alone is insufficient.

- **R14S4-S-2 — NON-BLOCKING for this slice — [c2_confirmation.py:1103](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1103).** Duplicating `t000` within one family with a distinct trial index passes `derive_seeds`; three declared entries become two entries in its returned trial map. P18-1 requires unique trial IDs, and Constitution §27 requires every seed to be recorded. The earlier `check_declaration` rejects this input, so the eventual caller must demonstrably run it before seed derivation; a uniqueness check here would also prevent silent loss from direct use.

- **R14S4-S-3 — NON-BLOCKING for this slice, integration defect — [c2_lockbox.py:718](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_lockbox.py:718).** The seed test’s `trend:t000` and `vol:t000` pass `check_declaration`, which requires uniqueness within each family. The lockbox declaration lookup matches only `trial_id`, finds two entries and refuses either nominee. Match the `(family, trial_id)` pair before the lockbox integration is accepted; this is a separate lockbox change, not a new seed rule.

The R-7 named-object bytes, Annex B §2.4 fields and list order, canonical JSON, round boundary calculation, lowercase hex checks, signature-to-randomness hash, and false/error verifier refusals match the cited text. The tests pin down those cases. They do **not** independently pin down the R-13 trial-seed bytes, and the zero-estimator test calls `screen.estimator_seed` rather than `derive_seeds`; add an independent R-13 vector and a zero result through the full derivation.

**Validation:** 25 seed tests passed; Ruff check and format, seven import contracts, and `git diff --check` passed. The broader confirmation run had 75 passes and 12 setup errors because this read-only environment has no writable temporary directory. No frozen path changed in `15941ad..HEAD`; no new module import was added, and the earlier slices’ code was untouched. I could not verify real BLS verification, the signed loader, the seven-day operational rule, or a complete regression run. No restricted data or network was used.

Reviewer metadata available here identifies Codex as GPT-6 based; the exact deployment ID is not exposed. This review remains **uncommitted** because the workspace is read-only, so the repository’s required recorded-review gate is not complete.
