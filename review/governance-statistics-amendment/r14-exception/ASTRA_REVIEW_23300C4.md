# Codex Astra review of proposed R-14a (23300c4)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a191dc-4a52-7732-8cdb-4f61d28fcb4c`, 85,101 tokens. Reviewed `review/governance-statistics-amendment/r14-exception/PROPOSAL.md` at `23300c4`, independently of Sol's review (run after it, prompt forbids relying on any other review; none was in the repository).

Verdict: **FIX**: 3 BLOCKER (R14A-A-1..3), 2 NON-BLOCKING (R14A-A-4..5). No gaps in numbering.

Disposition: none repaired yet; all to be answered in R-14a rev 2.

## Report (verbatim)

**Verdict: FIX.** Reviewed `23300c4` on `freeze-sheet`, independently and read-only. The two-file exception is defensible, but its “only calls frozen rules” restriction and residual-risk claims need correction before an informed owner decision.

| Authority / consumer | Assessment |
|---|---|
| Frozen Constitution §§5–7a, §16 | Still governs; this proposal activates nothing. |
| R-8 / confirmation statistics | Existing numerical implementations remain bound; their inputs and composition also require review. |
| R-13 / seeds | Item 5 preserves the intended separation between the nominee’s estimator seed and beacon-protected gate seeds. |
| R-14 / executable bytes | Two additional file hashes can form an explicit exception without weakening the existing two checks. |
| D-11 / lockbox prediction and access | Requires its own decided statistical implementation and identity restrictions; neither follows merely from an import allowlist. |

**R14A-A-1 — BLOCKER**  
**Place:** [PROPOSAL.md:18](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL.md:18), item 4; §3’s claim that R-8 is unchanged.

**Failure scenario:** The proposed restriction does not accommodate the lockbox implementation it serves. D-20 A4 specifies an `m ≠ n` bootstrap generator with the `lockbox_prediction` stream; existing `statistics.bootstrap_indices` fixes both output length and seed length to `n`. `dsr.indices` also generates `n` indices and uses the DSR stream. Calling either unchanged does not implement A4. D-20 A6 additionally calls for an R-8 extension binding the lockbox module itself.

Read strictly, “only loads … calls … records” blocks the required implementation. Read narrowly as excluding D-11 rules, it permits later statistical code and contradicts §2’s assertion that every scientific rule remains in earlier code.

**Minimal repair:** Permit the two files to **implement explicitly signed D-11/D-20 rules**, while requiring reuse of the existing bound primitives and forbidding different scientific choices. Identify the accompanying R-8 extension. Do not claim all statistical implementation was frozen at `AQTQ1`.

**R14A-A-2 — BLOCKER**  
**Place:** [PROPOSAL.md:18](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL.md:18), item 4 and §2’s “cannot change … statistic” claim.

**Failure scenario:** An unchanged statistic can produce a different decision after loading or alignment changes its sample. Independent exact example: daily candidate-minus-benchmark returns, in percentage points,

`d = [-8, 1, 2, 3]`.

Their mean is `−1/2` and sample variance is `77/3`, so E-DIFF is negative. If an alignment operation discards the first day, `[1, 2, 3]` has mean `2` and sample variance `1`: E-DIFF becomes positive. The same frozen Sharpe function now passes the positive-sign condition. Hashing the resulting series records the error; it does not establish correct provenance.

This would violate the intended rules, but counting calls or identifying a function as “loading” cannot detect it.

**Minimal repair:** Replace the categorical assurance with a reviewable requirement: trace signed inputs through exact timestamp selection, pairing, transformations, availability handling and recorded decisions. Require focused synthetic tests for missing/duplicate/misaligned observations and fail-closed behavior. Reuse C-0/A6 requirements rather than inventing another specification.

**R14A-A-3 — BLOCKER**  
**Place:** [PROPOSAL.md:25](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL.md:25), §2.

**Failure scenario:** “Neither module can be tuned on them” is false. D-11’s owner decision explicitly retains a **historical held-back check**, acknowledges that its prices are public, and says it cannot detect strategies shaped by those prices. Sealing repository data does not remove external knowledge of the market history. Later code can also contain outcome-affecting mistakes in alignment, exception handling or gate aggregation.

“That is caught only by §16” overstates review as a guarantee and omits tests as evidence.

**Minimal repair:** State that authorized access remains restricted, while public-history influence and undetected implementation defects remain possible. Describe §16 review and tests as controls, not guarantees. Disclose that these later implementations are outside the posted qualification object; reuse of qualified primitives alone does not establish qualification of their composition.

**R14A-A-4 — NON-BLOCKING**  
**Place:** [PROPOSAL.md:24](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL.md:24), signed-hash timing claim.

**Failure scenario:** A signature authenticates committed content; it does not independently prove when signing or the first data read occurred. The sentence conflates required ordering with evidence of ordering.

However, an additional timestamp mechanism appears unnecessary: DRAFT §2.0 posts the canonical C2 declaration through O-6a, and Annex B §2.4 includes `protocol_hash`. That supplies the chain:

`accepted declaration post → protocol hash → two module hashes → loaded bytes`.

**Minimal repair:** Cite and require verification of this existing chain before evaluation, with the applicable access records. Distinguish this later anchor from `AQTQ1`. The loss of the earlier freeze remains real; another timestamp immediately before confirmation would not restore it.

**R14A-A-5 — NON-BLOCKING**  
**Place:** [PROPOSAL.md:17](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL.md:17), mutual imports and data access.

**Failure scenario:** A builder could mistake permission to import the lockbox module for permission to invoke its reader under experiment-engine identity. Code hashes and import restrictions do not enforce operating-system identities or partition boundaries.

**Minimal repair:** Add one explicit sentence: this is a code-location exception only; confirmation access remains under the registered engine, lockbox reads remain exclusively under `lockbox_eval`, and D-11’s authorized history range and handoff restrictions remain binding. Verify those boundaries at §16 review.

**Answers to §4:** Item 4 is insufficient as written; alignment and filtering can change the statistic without replacing its function. R-14a grants no lawful additional data access, but does not itself enforce that boundary. Signed C2 hashes are suitable content bindings; the existing public declaration chain can provide the later timing anchor, subject to verification. No new timestamp system is justified by the evidence reviewed.

The smallest coherent route is an explicit exception for **two reviewed implementations of signed rules**, with honest disclosure of their later freeze. If the owner instead requires every statistical implementation to precede `AQTQ1`, the necessary code must move before step G; the proposed small pre-freeze change alone is insufficient.

No files were written. Git status and working/index diff checks returned no changes. Calculations above are exact hand checks; runtime tests, lint, type and import checks are N/A to this wording review. No restricted data was accessed, and no implementation or qualification result was validated. The caller must preserve this report before counting it as a committed review record.
## Prompt

# Review: proposed C2 row R-14a (exception for the lockbox and confirmation modules)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. The repository checkout is on branch `freeze-sheet`. Review `review/governance-statistics-amendment/r14-exception/PROPOSAL.md` (Claude Opus 5.5, commit 23300c4). Context as needed: `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` (R-8, R-13, R-14 ~l.145-152) and `ANNEX_C_GATE_DEFINITIONS.md`; `review/governance-statistics-amendment/d20-d13-proposal/OWNER_DECISION_D20_D13.md`; `review/governance-statistics-amendment/d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md`, `PROPOSAL_REV3.md` (A1b, A6, A7, D20L-31), `PROPOSAL_REV4.md`, `PROPOSAL_REV5.md`; `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §16, l.73); `calibration/qobj.py`; `deploy/calibration/FREEZE_HELDOUT.md`; and the design it serves, `git show origin/pre-freeze-screen-q2-q5:review/pre-freeze-screen/DESIGN.md` with `SOL_DESIGN_REVIEW_CEB12C3.md` (PFS-S-1).

Review independently of any other R-14a review; none is in the repository. Direction: simplify rather than patch; claim only what is true and testable. Check: 1. Is R-14a consistent with R-8, R-13, R-14, D-11 and Constitution l.73, §16? 2. Is item 4 ("defines no rule ... only loads, checks, calls, records") checkable at §16 review, or can a statistic hide in alignment, filtering or record code? 3. Is binding by the signed C2 hash instead of the posted object hash an honest, sufficient anchor, and are §2's residuals complete and true? 4. Answer §4's questions. 5. Is anything missing that the owner must know before deciding?

IDs: `R14A-A-n`. Use exactly that prefix; the caller verifies the model from the CLI header. Each finding: severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
