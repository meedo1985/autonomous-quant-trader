# Astra review: slice 6b design rev 4 at 9f45303 (verdict FIX)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1d8a9-be0f-7c21-925e-be742ca0ab38; 123,646 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV4_PROMPT_ASTRA.md` (commit `014db41`). Findings R14D6B4-A-1..6. Report below verbatim.

---

**Verdict: FIX.** Rev 4 addresses most prior findings, but its capture-record and attempt-completion contracts still have implementation-blocking gaps.

**Model:** Exact runtime model ID is not exposed to me; I cannot verify the requested Astra identity. Findings are proposals, not approval.

Reviewed Git blobs at **`9f45303`**. The actual checkout was `confirmation-module` at `014db41`; later changes were excluded. No files were modified.

All design locations below refer to [DESIGN_SLICE6B.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN_SLICE6B.md) at the requested commit.

| Prior finding | Status | Rev 4 evidence |
|---|---|---|
| R14D6B3-F-1 | PARTIAL | Lines 62–75 remove the impossible declaration commitment and adopt B-1, but the required acceptance-tip hash has no schema field. A-1 below. |
| R14D6B3-F-2 | APPLIED | Lines 43, 279–280 specify the inclusion header and derived day 0. Residual wording needs correction: A-6. |
| R14D6B3-F-3 | APPLIED | Lines 45, 85–88, 145–149 use one whole-second clock value before appending. |
| R14D6B3-F-4 | APPLIED | Lines 151–161, 264–268 define aborted-look handling, distinguish intervening cycles, and leave B-3 undecided. Concurrent looks remain a separate gap: A-5. |
| R14D6B3-F-5 | PARTIAL | Lines 111–140 derive completion and adopt family U_ops, but existing state and outcome readers still reject honest histories. A-2/A-3. |
| R14D6B3-F-6 | APPLIED | Lines 189–204 verify the composite, bind cycle/protocol, and verify served bars against its embedded manifests. |
| R14D6B3-F-7 | PARTIAL | Lines 165–177 supply full precedence, but §3 rejects day-index mismatches before that precedence can apply. A-4. |
| R14D6B3-F-8 | APPLIED | Lines 173–175 retain `DAYS_INCOMPLETE` as U_proc and leave the broader list under review. |
| R14D6B3-F-9 | APPLIED | Lines 182–185 specify termination payload, ledger, writer, both entry-point refusals, and residual. |
| R14D6B3-F-10 | APPLIED | Lines 208–220 require exact enumeration membership and qualification-object equality. |
| R14D6B3-F-11 | APPLIED | Lines 41–55, 277–285 name contract changes, remove the posted path, and require cycle entries after the anchor. |
| R14D6B3-F-12 | APPLIED | Lines 232–235 require declaration-time threshold checks and refuse unsupported looks before the bar read. |
| R14D6B3-F-13 | APPLIED | Lines 133–134, 229–230, 239–256 address late results, naming, Task-12 comparison, CPCV isolation, and eight steps. |

B-1, B-2, B-4 and B-5 are faithfully stated **as owner direction**. B-1 and B-4 are not yet executable as promised because of the findings below. B-3 remains explicitly open. I found no claim that AI approved an amendment or settled P18/S4 wording.

**R14D6B4-A-1 — Major: the capture check requires a nonexistent acceptance-tip field.**

- **Location:** Design lines 67–71, 279–280.
- **Evidence:** `c2_confirmation.py:2450–2491` accepts exactly seven fields, including the inclusion `block_hash`, but no acceptance-tip hash. Rev 4 adds only `block_header`. SPEC §5, lines 82–95, distinguishes the inclusion block from the acceptance tip at `h+5`.
- **Failure scenario:** The first offline capture check cannot obtain its comparison value. Reusing `block_hash` compares against the wrong block; introducing an unchecked caller value defeats the stated source rule.
- **Proposed correction:** Explicitly add the frozen acceptance-tip hash to the acceptance-record contract, validate its representation, and expose it through authenticated startup inputs. Retain the node/verifier provenance obligation.

**R14D6B4-A-2 — Major: rewriting `outcome` leaves completed attempts blocking the retry slot.**

- **Location:** Design lines 82–84, 111–120, 281.
- **Evidence:** `family_attempts` leaves `end=None` without an outcome (`c2_confirmation.py:764–767`). `trial_states:800–803` treats any sufficiently early attempt with `end=None` as potentially unfinished, regardless of its rewritten `outcome`.
- **Failure scenario:** Trial A writes its result and dies before `finish_attempt`; trial B subsequently crashes without an artifact. The prescribed rewrite produces A=`completed`, B=`undetermined`. Starting B’s otherwise eligible retry raises “attempt 2 is not permitted.” An isolated execution of the actual functions reproduced both results.
- **Proposed correction:** Make retry-slot determination recognize derived completion even without an outcome entry. Preserve actual crash-outcome positions for ordering; specify this additional contract change and regression case.

**R14D6B4-A-3 — Major: the prescribed recovery race fails before family U_ops handling.**

- **Location:** Design lines 91–92, 118–140.
- **Evidence:** `finish_attempt` checks that a start exists but does not reject an existing outcome (`attempts.py:384–400`). `family_attempts` rejects duplicate outcomes immediately (`c2_confirmation.py:745–751`), before §3’s proposed handling.
- **Failure scenario:** Recovery observes no result and writes a crash outcome. The evaluator then appends its result and its mandatory `completed` outcome. The next call raises “attempt … has two outcome records,” preventing B-4’s family-local U_ops record and continuation of the other family. The synthetic probe reproduced this rejection.
- **Proposed correction:** Define serialized outcome-writing responsibility and prevent the evaluator from blindly appending a second outcome. Specify how the corresponding race history reaches family-local order-breach handling before the strict duplicate-outcome rejection.

**R14D6B4-A-4 — Major: day-index mismatch has two incompatible dispositions.**

- **Location:** Design lines 127–132 versus 167–169.
- **Evidence:** §3 compares `days` against the derived window and makes every mismatch a cycle-level `CycleError`. §5 promises family U_ops for a day-index mismatch. Existing `nominate:895–897` implements the latter; `completed_entry:2867–2881` separately checks canonical consecutive dates and window consistency.
- **Failure scenario:** An otherwise valid record contains a consecutive day vector shifted by one day. §3 terminates the cycle before §5 can record that family U_ops.
- **Proposed correction:** Distinguish malformed/foreign identities from well-formed alignment failures and assign one disposition to each. Make §3, §5 and the proposed tests agree; do not leave the implementer to select the policy.

**R14D6B4-A-5 — Major: concurrent look calls can terminate the winning look.**

- **Location:** Design lines 145–161, 182–185.
- **Evidence:** `ledger.append_entry:391–414` serializes individual appends, not admission of a whole look. The stated store obligation prohibits runner writes but does not explicitly serialize competing `evaluate_look` calls.
- **Failure scenario:** Two calls inspect the same pre-look ledger. Call A appends, rechecks and begins evaluation. Call B appends, discovers A’s intervening entry, and follows `LOOK_WITHOUT_RECORD` termination handling—even though A is producing the cycle’s valid record.
- **Proposed correction:** Require exclusive per-cycle look admission, or an equivalent reservation mechanism. A losing concurrent invocation must not consume another look entry or terminate the winning invocation. Keep the exact termination wording under open B-3.

**R14D6B4-A-6 — Minor: the block-time residual incorrectly implies a symmetric two-hour bound.**

- **Location:** Design lines 58–60.
- **Evidence:** Bitcoin requires header time above the previous 11-block median and limits future timestamps relative to the validating node’s clock. It does not guarantee header time within ±2 hours of real inclusion time. [Bitcoin block-header reference](https://developer.bitcoin.org/reference/block_chain.html#block-headers).
- **Failure scenario:** A lagging median permits a timestamp more than two hours behind real time; the stated maximum error in the 180-day deadline is therefore unsupported.
- **Proposed correction:** State the actual asymmetric constraints without promising bounded real-time error. The 80-byte layout, offset 68–71, little-endian time and reversed double-SHA256 comparison are otherwise correct. Header/hash consistency still depends on the accepted chain-provenance obligation.

The look’s **bar-read gate** remains after its entry. “Before any read” should be understood narrowly: step 4 already reads ledger payloads containing `d`, and `evaluate_trial` intentionally reads bars before the shared look. I found no additional pre-entry bar read in the specified `evaluate_look` sequence.

Files and ranges read at `9f45303`:

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–300; requested rev-3→rev-4 diff |
| Same directory: Fable recheck; adjudication; owner rev-3; owner rev-2 | 1–335; 1–40; 1–17; 1–18 |
| `review/r14a-modules/DESIGN.md` | 90–150 |
| `calibration/c2_confirmation.py` | 625–960, 1489–1700, 1845–1894, 2440–2902 |
| `calibration/dsr.py`; `classifier.py`; `reduce.py`; `choices.py` | 1–265; 1–141; 1–80; 1–75 |
| `scripts/d19_heldout.py` | 172–197 |
| `src/aqt/core/ledger.py`; `attempts.py` | 100–125, 296–415; 290–400 |
| `src/aqt/data/manifest.py` | 530–838 |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 1–140 |
| Same root: `s4-amendment-draft/ANNEX_A_SELECTION_RULE.md` | 51–105, 144–190 |
| Constitution; protocol v1; hash canonicalization; root `AGENTS.md` | 1–199; 1–317; 1–10; 1–48 |

Validation: the corrected in-memory probes exited 0; they used synthetic records and isolated functions, not an integration run. The read-only hash check passed all 14 sidecars, seven manifest file hashes, Constitution self-hash and checked bindings; protected inventory/blob IDs were unchanged from `5cd2a29`. Git staged/unstaged checks were clean. Tests, lint, typing and import-boundary suites were N/A for this document-only review.

No restricted data or unrelated implementation was reviewed. No review record was written or committed, as requested; the repository’s committed-review-record requirement remains outstanding.