# Astra re-check: slice 6b design rev 5 at 24ba994 (verdict FIX)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1d8b2-33d4-7c02-95de-11f9f607263d; 76,906 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV5_PROMPT_ASTRA.md` (commit `5992caa`). Findings R14D6B5-A-1..4. Report below verbatim.

---

**Verdict: FIX.** Rev 5 fixes the original completion-slot example, but three contract gaps remain.

**Model:** Exact runtime model ID is not exposed to me; I cannot verify Astra identity. Findings are proposals, not approval.

Reviewed **`24ba994`**, starting with the requested diff from `9f45303`. The checkout was `confirmation-module` at `5992caa`; later changes were excluded. No files were modified.

| Prior finding | Status | Rev 5 evidence |
|---|---|---|
| R14D6B4-A-1 | **PARTIAL** | Design 43, 69, 298–300 supplies the six headers and derives the correct tip index, but the link comparison reverses the wrong side. Finding A-1 below. |
| R14D6B4-A-2 | **APPLIED** | 113–121, 147–149, 303–304 rewrites both `outcome` and `end`. Synthetic probe confirms A completed, B eligible for retry, and B’s retry accepted. |
| R14D6B4-A-3 | **PARTIAL** | 93–94, 123–133 removes evaluator-written outcomes and specifies family-local duplicate handling. Interaction with strict retry validation remains unresolved: A-3 below. |
| R14D6B4-A-4 | **PARTIAL** | 134–141, 185–188 separates days from identity, but leaves `completed_entry`’s contradictory window check in place. A-2 below. |
| R14D6B4-A-5 | **APPLIED** | 84–90, 162–166 serializes look admission and explicitly makes the loser refuse harmlessly. Lock implementation clarification: A-4 below. |
| R14D6B4-A-6 | **APPLIED** | 58–62 accurately states the asymmetric timestamp constraints and retains chain provenance as a verifier obligation. |

B-1..B-5 remain stated as owner direction, including decided B-3. No owner decision needs reopening; the failures below prevent fully delivering that direction.

**R14D6B5-A-1 — Major: header links compare incompatible byte orders.**

- **Location:** Design 43, 298–300.
- **Evidence:** `hash` is explicitly defined as reversed SHA256d, but the serialized previous-header field contains SHA256d in internal byte order. [Bitcoin header reference](https://developer.bitcoin.org/reference/block_chain.html#block-headers).
- **Failure scenario:** A correctly serialized chain fails the prescribed comparison at its first link. All five correctly encoded links in the synthetic probe failed it.
- **Proposed correction:** Specify `headers[i][4:36] == SHA256d(headers[i-1])` on decoded bytes. Use `SHA256d(header)[::-1].hex()` for comparison with displayed `block_hash` and capture-body hashes. The tip remains `headers[5]`.

**R14D6B5-A-2 — Major: the shifted-days disposition still cannot reach `nominate`.**

- **Location:** Design 134–141, 151, 183–188; `c2_confirmation.py:2876–2881`.
- **Evidence:** `completed_entry` requires `window_id == window_id(days[0], days[-1] + DAY)`. Rev 5 separately requires `window_id` to equal the governing window.
- **Failure scenario:** Canonical consecutive days shifted by one day, with the correct governing `window_id`, raise `"the pre-look window_id is not its days' window"` in the actual decoder. Changing `window_id` to match those days instead violates rev 5’s identity check. Neither route produces the promised family U_ops.
- **Proposed correction:** Explicitly revise this decoder contract: validate `window_id` against the governing identity, validate day representation separately, and route well-formed alignment differences to `MISALIGNED_SERIES`. Preserve malformed-date and `d` integrity checks.

**R14D6B5-A-3 — Major: excluding a breached attempt from the slot can invalidate its existing retry before family reporting.**

- **Location:** Design 84–86, 129–133, 301–304; `c2_confirmation.py:792–809`.
- **Evidence:** `trial_states` raises whenever a trial has two attempts but no longer owns the slot.
- **Failure scenario:** A1 crashes; A2 legitimately starts and completes; recovery then duplicates A1’s outcome. Rev 5 correctly calls this an order breach and excludes A1 from slot selection. But passing the remaining rewritten history through the existing state logic raises `"A: attempt 2 is not permitted"`. An isolated probe reproduced this. Reporting a breach from `family_attempts` alone therefore does not ensure the other family continues.
- **Proposed correction:** Explicitly carry family order-breach status through state evaluation. Preserve the complete attempt history, but prevent slot-admissibility rejection of that already-failed family from becoming a cycle-level exception. Add this duplicate-after-retry regression.

**R14D6B5-A-4 — Minor, non-blocking: distinguish the look lock from the append lock explicitly.**

- **Location:** Design 162–166; `ledger.py:339–366, 391`.
- **Evidence:** `append_entry` independently opens and acquires its sidecar lock. Reusing that same lock for look admission creates nested acquisition through separate handles, which can time out.
- **Failure scenario:** An implementation wraps steps 4–7 in the existing `_exclusive_lock(ledger)` helper; step 7 then cannot acquire its own append lock.
- **Proposed correction:** Name a distinct look-lock sidecar and require exception-safe release, with acquisition order look lock → append lock. A terminated process releases an OS-held lock; a surviving sidecar file is not itself a stale lock. With distinct locks, I found no lock-order cycle in the specified flow.

Files and ranges read at `24ba994`:

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–322; requested diff |
| Same directory: `ASTRA_DESIGN_SLICE6B_9F45303.md` | 1–96 |
| Same directory: adjudication; owner rev-3 decisions | 1–29; 1–18 |
| `calibration/c2_confirmation.py` | 625–965, 1074–1081, 1600–1650, 1728–1734, 1824–1825, 2440–2530, 2620–2690, 2770–2902 |
| `src/aqt/core/ledger.py` | 90–135, 280–415 |
| `src/aqt/core/attempts.py` | 280–405, 430–487 |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 72–110 |
| Constitution; protocol; hash canonicalization; root `AGENTS.md` | 1–199; 1–317; 1–10; 1–48 |

Validation: synthetic, isolated-function probes via `rtk proxy python -B -` exited 0; these were not integration tests. `git diff --check` passed. Protected inventory/blob comparisons, 13 frozen-directory sidecars, seven manifest hashes, Constitution self-hash and checked bindings passed. **Local gate: BLOCKED** by the major findings.

Implementation tests, lint, typing and import-boundary suites were N/A for this document-only re-check; live lock/crash behavior was not exercised. No restricted data was accessed. Per your read-only instruction, this report was not written or committed; repository review-record closure remains outstanding.