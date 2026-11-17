# Astra review of the store build design rev 1 at 1633831 (verbatim record)

- Reviewer: Codex CLI `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s read-only`; the CLI log shows `model: gpt-6-astra`, `provider: openai`.
- Prompt: `DESIGN_STORE_REV1_PROMPT_ASTRA.md` (commit `1633831`). Findings ST1-A-1..5.
- Recorded 2026-11-17 by Claude Opus 5.5 without edits below the line.

---

**Verdict: FIX.**

Reviewed commit `1633831753a00a06e69844b3233d3d1500d723d5`. Observable reviewer configuration: **`gpt-6-astra`, high effort**; provider-side runtime attestation was unavailable. Findings are proposals.

**ST1-A-1 — BLOCKER: no durable handoff between the two ledgers.**  
**Location:** [DESIGN_STORE.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/store/DESIGN_STORE.md:42), lines 42–53, 106–108, 127, 138.

- **Evidence:** Confirmation appends its closing entry under the look lock (`c2_confirmation.py:4549–4557`). The writer flushes before fsync (`ledger.py:411–414`); ledger readers are unlocked. Store admission uses `L_store`, whose durability helper syncs only the lockbox index and directories.
- **Failure:** The store observes a complete closing line before its fsync and durably admits a lockbox read. A machine crash preserves admission but loses the closing entry. The recovered cycle has no valid pick.
- **Correction:** Keep two ledgers, but specify writer/read coordination, lock ordering and durability of closing evidence before use. Test both a writer stalled before fsync and a crashed writer leaving a complete unsynced line. Chain verification alone is insufficient.

**ST1-A-2 — BLOCKER: failure to persist the stop marker can lose the incident stop.**  
**Location:** [DESIGN_STORE.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/store/DESIGN_STORE.md:106), lines 106–113.

- **Evidence:** An fsync error triggers a §26 stop implemented by another sealed create on the same file layer. Annex D lines 505–509 requires stopping on fsync failures and errors after writing starts.
- **Failure:** An append leaves a complete line, its fsync fails, and marker persistence also fails. After a crash, the line survives but the marker does not. Startup sees an intact chain and can resume without human reconciliation.
- **Correction:** Define fail-closed restart behavior when marker persistence fails, assigning any supervisor enforcement explicitly. Inject failures throughout marker persistence and verify that bars, releases and permits remain blocked until human clearance.

**ST1-A-3 — BLOCKER for coverage: confirmation obligations lack operation/test assignments.**  
**Location:** [DESIGN_STORE.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/store/DESIGN_STORE.md:119), lines 119–129, 164–175.

- **Evidence:** `c2_confirmation.Store:4566–4568` requires one common ledger path, never replaced or forked after its anchor. Lines 4593–4595 require declaration validation before posting, including frozen thresholds for every `(K_f,T)`. Neither has an explicit §4 assignment. §5 also lacks test assignments for the runner, launch, termination, confirmation-read and capture obligations.
- **Failure:** An invalid posted declaration spends the cycle, or separate anchored ledger branches pass local checks, while the listed release tests still pass.
- **Correction:** Add an obligation→operation/build→test mapping. Assign declaration construction explicitly if external. State enforcement of ledger identity and non-forking. Assign genuine/earliest capture provenance to external verification; synthetic tests cannot establish it.

**ST1-A-4 — BLOCKER for coverage: the promotion guard has no implementation owner.**  
**Location:** [DESIGN_STORE.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/store/DESIGN_STORE.md:143), lines 30–34, 143–153, 166–175.

- **Evidence:** Annex D lines 248–253 requires effective certification, completed cooling-off and `t_dec ≤ C`; Option C rev 2 lines 298–301 specifies TC-7. The design promises TC-7’s store side but assigns no promotion-guard operation or external build.
- **Failure:** Every listed operation passes while no component enforces rejection at `cooling_off_start + 259199`, acceptance at `+259200`, and rejection after C.
- **Correction:** Name the guard’s owning build and its interface to durable store evidence; assign TC-7 accordingly. Certificate effectiveness alone does not implement this guard.

**ST1-A-5 — NON-BLOCKING: S3’s test gate depends on S4 operations.**  
**Location:** [DESIGN_STORE.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/store/DESIGN_STORE.md:166), lines 166–175, 181–185.

- **Evidence:** Effective T-S1 includes concurrent `release`/`sign_permit`; T-S2 requires concurrent `release`. Those operations arrive in S4, although S3 promises these tests. §5 also names superseded T-S5 and crash rows 10/13.
- **Failure:** S3 cannot independently pass its stated integration gate. “As replaced there” preserves authority precedence but leaves the executable gate ambiguous.
- **Correction:** Put independent read-side tests in S3 and cross-operation assertions in S4. Enumerate the effective tests and crash rows.

Other conclusions:

- D-1 is reasonable after ST1-A-1 is resolved. D-2, D-3, D-4 and D-6 are compatible at design level; production roles must derive from authenticated OS credentials.
- The stated lookup→fsync→use order and `L_store` scope match Annex D. Incorporated time rules permit an on-time save to finish after its deadline; they do not permit a post-fsync deadline recheck.
- **ST-O-5’s reading is correct:** bind `C = min(A + 255 days, recorded look + 75 days)` once the actual look exists. Distinguish initial configuration from this later binding; recovery reuses the recorded look and fixed C.
- Publisher, signer, owner-command and provisioning exclusions are reasonable. Existing owner/S4 decisions remain open.

**Files and inclusive line ranges read:** authority paths below are under `review/governance-statistics-amendment/` and were read using `git show 3abcafb:<path>`.

| File | Lines |
|---|---|
| `review/store/DESIGN_STORE_REV1_PROMPT_ASTRA.md` | 1–38 |
| `review/store/DESIGN_STORE.md` | 1–206 |
| `s4-amendment-draft/ANNEX_D_LOCKBOX.md` | 1–327, 432–618 |
| `d20-lockbox-proposal/PROPOSAL_REV8.md` | 1–38, 50–258 |
| `d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md` | 1–344 |
| `d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md` | 1–220 |
| `d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md` | 1–98 |
| `d20-lockbox-proposal/OPTION_C_PROPOSAL_REV5.md` | 1–61 |
| `calibration/c2_lockbox.py` | 1180–1290 |
| `calibration/c2_confirmation.py` | 3860–3910, 4500–4612 |
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–190, 215–237, 280–320, 448–480 |
| `src/aqt/core/ledger.py` | 1–415 |
| `src/aqt/core/attempts.py` | 1–487 |
| `pyproject.toml` | 1–121 |
| `docs/RESEARCH_CONSTITUTION.md` | Entire file |
| `protocols/protocol_v1.yaml` | Entire file |
| `schemas/HASH_CANONICALIZATION_v1.md` | 1–10 |

**Validation:** Working tree and staged diff remained clean. Frozen verification passed: 28 protected files, 14 sidecars, Constitution self-hash and manifest/protocol bindings. `git diff --exit-code 92e6f52 HEAD -- docs protocols schemas specs FROZEN_HASHES.json '*.sha256'` returned 0.

Tests, lint, type and import execution were N/A for this read-only design review. Filesystem/clock guarantees remain unverified external assumptions. No files were modified or committed; all findings remain unrepaired as required by the prompt.
