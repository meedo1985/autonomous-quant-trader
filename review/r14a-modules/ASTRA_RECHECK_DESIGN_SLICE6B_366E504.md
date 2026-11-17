# Astra re-check: slice 6b design rev 6 at 366e504 (verdict ACCEPT WITH NOTES)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1d8b8-76c3-76c1-9683-116997c33a3c; 53,401 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV6_PROMPT_ASTRA.md` (commit `fa37823`). No findings with IDs; two wording notes (called N-1 step 4 qualifier, N-2 'as recorded' meaning by the adjudicator). Report below verbatim.

---

**Verdict: ACCEPT WITH NOTES.** No blocking or major defect found in the rev 6 changes. Findings are proposals, not approval.

**Model:** Exact runtime model ID is not exposed to me; I cannot verify Astra identity.

Reviewed `366e504` against `24ba994`. Checkout HEAD is `fa37823`; its only subsequent change is the review prompt. B-1..B-5 were not reopened.

| Prior finding | Status | Evidence in rev 6 |
|---|---|---|
| R14D6B5-A-1 | **APPLIED** | Design line 46 explicitly compares decoded previous-hash bytes with unreversed SHA256d and reserves reversed hex for displayed hashes. This matches the [Bitcoin header reference](https://developer.bitcoin.org/reference/block_chain.html#block-headers). |
| R14D6B5-A-2 | **APPLIED** | Lines 141–152, 318–319 replace the decoder’s days-derived window check with governing-window identity validation. Canonical, consecutive, nonempty days and `d` integrity remain required. Shifted days can now reach `MISALIGNED_SERIES`. |
| R14D6B5-A-3 | **APPLIED** | Lines 132–140, 158–163, 316–317 explicitly bypass breached-family admissibility checks and require the duplicate-after-legitimate-retry regression. This removes the conflict with `trial_states` lines 805–809. |
| R14D6B5-A-4 | **APPLIED** | Lines 173–179 specify a distinct sidecar, exception-safe release and look → append acquisition order. This avoids recursively acquiring the append lock at `ledger.py:391`. |

**New findings:** None meeting blocking or major severity; no R14D6B6-A IDs assigned.

The breached-family bypass does **not**, under the stated contract, permit a failed family to pass:

- Completion still derives from result entries, not the runner’s outcome word.
- Full attempt history remains recorded; retry admissibility is bypassed only for an already-failed family.
- Every result still undergoes identity and integrity validation under §3 rule 2.
- §5 independently makes an order breach `U_ops`, regardless of reported trial states. Unbreached families retain `trial_states` validation.

These are **design-contract fixes**, not implemented behavior: the inspected code still contains the old decoder and retry checks, expressly scheduled for change by §13.

Minor wording notes: qualify step 4’s unconditional “then `trial_states`” at lines 88–89 with “for unbreached families.” Clarify that “states … as recorded” at line 138 preserves §3’s derived completion semantics rather than trusting raw outcome words.

Files and ranges read:

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–333; requested diff |
| Same directory: `ASTRA_RECHECK_DESIGN_SLICE6B_24BA994.md` | 1–68 |
| Same directory: `ADJUDICATION_RECHECK_DESIGN_SLICE6B_24BA994.md` | 1–26 |
| `calibration/c2_confirmation.py` | 700–975, 2610–2695, 2770–2902 |
| `src/aqt/core/ledger.py` | 20–45, 280–415 |
| Constitution; protocol; hash canonicalization; root `AGENTS.md` | 1–199; 1–317; 1–10; 1–48 |

Validation: `rtk proxy git diff --check 24ba994 366e504` passed (exit 0). The protected-path/sidecar comparison against `24ba994` also exited 0 with no changes. Working-tree and staged diffs were empty.

Implementation tests, lint, typing and import-boundary checks were N/A for this narrow document review; live locking/crash behavior was not exercised. No files were modified. Committing this review record remains outstanding under the repository rule.