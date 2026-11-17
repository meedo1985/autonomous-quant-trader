# Astra short check of the Fable 6b repairs, joined test and deviation list at 2a02f45 (verbatim record)

- Reviewer: Codex CLI `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s read-only`; the CLI log shows `model: gpt-6-astra`, `provider: openai`. The reviewer itself says the model ID is not exposed to it.
- Prompt: `B6F_REPAIRS_REVIEW_PROMPT_ASTRA.md` (commit `2a02f45`). Scope: `f1974a7`, `867fcc6`, `89c1f83`. Findings B6FR-A-1..3.
- Recorded 2026-11-17 by Claude Opus 5.5 without edits below the line.

---

**Verdict: FIX.** Reviewed `confirmation-module` at `2a02f45`; no files changed.

**Model:** exact executing model ID is not exposed in this session. I cannot certify this as an Astra run.

1. **B6FR-A-1 — Major: both joined tests expire with wall-clock time.**  
   Location: [test_c2_confirmation_joined.py:73](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_joined.py:73), lines 207–220, 312–324.  
   The fixture freezes only `cf._now` at `2026-11-17T12:00:00Z`. Attempt and result entries retain the ledger’s real clock. Once their timestamps exceed that instant, `look_allowed` refuses before either test reaches its assertions. An in-memory reproduction with a ledger timestamp one second later raised the expected `CycleError`.  
   **Correction:** freeze the ledger clock as well, keeping real append/hash behavior and deterministic timestamps at or before the look clock.

2. **B6FR-A-2 — Minor: F-4 remains incomplete in the downstream readers.**  
   Location: [c2_confirmation.py:775](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:775), lines 775–781 and 3434–3437.  
   `attempt_counts` validates starts only. Consequently, `family_attempts` still raises `TypeError` for an outcome with `attempt_id=[]`, and `KeyError` when that key is missing. A foreign-cycle result with `attempt_id=[]` also raises `TypeError` in `family_ledger`. All three were reproduced without filesystem writes. The added test checks only `of_cycle`, so misses these consumers.  
   **Correction:** validate outcome/result identifiers before indexing or membership tests; refuse malformed records with `CycleError`. Add consumer-level regression cases. These paths fail closed, but still violate the promised refusal contract.

3. **B6FR-A-3 — Minor: the deviation list omits a relocation and overstates review status.**  
   Location: [DEVIATIONS_SLICE6B_REV16.md:21](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DEVIATIONS_SLICE6B_REV16.md:21), lines 21, 33–34, 58–59.  
   B6F-D-1 records the additional `prepare` checks but omits moving `open_look`’s classifier bounds outside the lock and before `look_allowed`, superseding B5A-R-2. The final sentence also calls owner review the remaining merge condition, although the Fable adjudication explicitly leaves F-1 conditional on this check passing. An owner could therefore review an incomplete ordering/status summary.  
   **Correction:** record the relocation and superseded reading; retain the pending repair-review condition. The three claimed owner acceptances do have recording commits: `3ca103a`, `73bbc5f`, `24f0c95`.

Otherwise, source inspection supports F-2/F-3’s early checks, the diagnostic-only scope of F-6, and F-7’s cap before decompression. The joined test connects real producers and consumers across the named seed, identity, cut and sealed-`d` interfaces; its stated stand-ins preserve those connections. F-5 copies the pre-look ledger and excludes the appropriate diagnostic/hash fields, subject to B6FR-A-1.

**Files and ranges read** — paths abbreviated within the repository:

| File | Ranges |
|---|---|
| `calibration/c2_confirmation.py` | 748–882, 1660–1795, 1930–2135, 2880–2965, 3110–3255, 3370–3495, 3529–3640, 3950–4558; remaining repair hunks |
| `tests/unit/test_c2_confirmation_joined.py` | 1–332 |
| Other changed confirmation tests | Repair hunks; prepare 276–352, look 375–399, CPCV 366–420 |
| `src/aqt/core/attempts.py` | 150–309, 435–487 |
| `src/aqt/core/ledger.py` | 108–126, 366–415 |
| Review prompt, final Fable record/adjudication, deviation list | Whole |
| B1–B5 build notes and adjudications | Whole |
| `DESIGN_SLICE6B.md` | 1–145, 185–225, 345–410 |
| Constitution, protocol, hash canonicalization | Whole |

**Validation commands and results** — commands used the `rtk proxy` prefix:

| Command/check | Result |
|---|---|
| Prompt’s five-file pytest command, with Python `-B` and `-p no:cacheprovider` | Exit 1 before collection: no writable temporary directory |
| `.venv/Scripts/ruff.exe check --no-cache calibration tests/unit/` | Exit 0; passed |
| `.venv/Scripts/mypy.exe --no-incremental --no-sqlite-cache --cache-dir=NUL calibration/c2_confirmation.py` | Exit 0; passed. Initial SQLite-cache invocation failed on `NUL\3.12` |
| `.venv/Scripts/lint-imports.exe --no-cache` | Exit 0; seven contracts kept |
| Inline Python reproductions | Three malformed-record exceptions and clock refusal confirmed |
| Git diffs/status and inline hash verification | Clean worktree; 32 protected files/sidecars unchanged against `95e5574`; sidecars, manifests, Constitution self-hash and checked bindings pass |

**Local gate: BLOCKED.** Pytest remains unverified, and findings remain proposals. This response is uncommitted: the prompt’s read-only restriction prevents satisfying the project’s committed-review-record requirement.
