# Dispositions of the fidelity reviews of the S4 fold-in (c5cb1ff)

**By:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. These are AI repairs, not an authority.

**Reviews:**
- `SOL_FIDELITY_REVIEW_C5CB1FF.md` (gpt-6-sol): FIX, S4F-S-1..11;
- `ASTRA_FIDELITY_REVIEW_C5CB1FF.md` (gpt-6-astra): FIX, S4F-A-1..13.

**Owner choices** on the four items that were the owner's to make: `OWNER_DECISION_S4_FOLDIN.md`.

**Repaired in:** `ANNEX_D_LOCKBOX.md` rev 2 and `DRAFT_WORDING.md`, in the commit that adds this file. No finding is left unrepaired.

| Finding | Disposition | Where |
|---|---|---|
| S-1 ~ A-1 (D11-15 resolved without authority; cap formula and anchor missing) | Accepted. **Owner choice 1:** earlier of the two. `C = min(T + 255 d, look + 75 d)`, with `A = T`, is restated, and "day 255" in P-6 means C. The draft's "informative" reading is deleted. | Annex §D-2.7, §D-1.9, §D-3.9; DRAFT §2.3 `processing_cap`, §4 |
| S-2 (R-14a only referenced) | Accepted. R-14a items 1-8, with rev 3 items 1-2 applied, are inlined in DRAFT §2.0. | DRAFT R-14a |
| S-3 ~ A-13 bullet 2 (R1 "no longer exists") | Accepted. R1 is described as changed, not removed. | Annex §D-2.10 |
| S-4 ~ A-3 (signing-key rules missing) | Accepted. Added: the key lifecycle, private-key custody, publisher verification with the key from the signed C2 and the same library, no replacement, lost key, and compromise with C2's replacement second test. The public key is added to the `<<SIGNING>>` values. | Annex §D-3.6; DRAFT §4, §6 |
| S-5 ~ A-6 (`visible_from` dropped from rejection entries) | Accepted. Restored as the internal insert time `t1`, own insert for both kinds, withheld from the reader. | Annex §D-3.7 |
| S-6 (replay failure paths) | Accepted. The commitment mismatch gives MISMATCH plus a §26 incident; bars that cannot be loaded give MISMATCH; the tests are added. | Annex §D-3.7, §D-3.8 |
| S-7 ~ A-5 (upside, bundle and record contracts incomplete) | Accepted. Restored: `k` strictly below, the p95 comparison and the NOT_COMPUTED values; the sign rule; lineage via `parent_id`; the reason enums; the DEFAULT field rules; PASS's null `cause_class`; the full pre-read-check payload and one record per evaluation; typed `block`; shared encodings; the `evaluation_id` format; the 256-bit nonce. | Annex §D-2.2, §D-3.1a, §D-3.5, §D-3.7 |
| S-8 ~ A-8 (test inventory incomplete) | Accepted. The complete effective list now covers D-12 T-1..T-8, A1a, A1b (including the seed that maps to 0), A5, A6, A7, B1 signing and roles, compromise reconciliation, bundles, replay, `begin_read`, T-S1 with its admission boundaries, and C3's `sign_permit` test. | Annex §D-3.8 |
| S-9 (THREAT_MODEL row lacks running the strategy) | Accepted. | DRAFT §1a THREAT_MODEL row |
| S-10 ~ A-12 part 1 (A7 `code` shape) | **Owner choice 4:** both module hashes. | Annex §D-3.1 |
| S-11 ~ A-12 part 2 (lineage vs budget precedence) | **Owner choice 3:** lineage first. `begin_read` steps 5 and 6 are reordered. | Annex §D-3.7 |
| A-2 (R-14d broadened flat starts) | Accepted. Flat starts are scoped to the confirmation source baseline and the lockbox runs. No other convention, including C-14, changes. | DRAFT R-14d |
| A-4 (worker computes twice) | Accepted. Restored, and kept distinct from R-a replay. | Annex §D-1.8 item 6 |
| A-7 (every-run vector check resurrected) | Accepted. Deleted. Vectors are checked once per process start (rev 3 A5). | Annex §D-3.4 |
| A-9 (pre-freeze conditions abbreviated) | Accepted. All three conditions are restated, with PR #81 / `f715dfe`. | Annex §D-3.1 |
| A-10 (R-14a residuals missing) | Accepted. The five accepted residuals are listed. | Annex §D-3.1 |
| A-11 (history endpoint) | **Owner choice 2:** up to L0, so 31 May is included. | Annex §D-1.8 |
| A-13 (synchronisation) | Accepted. Covered: "visible" now follows the reader projection (§D-2.7); R1 (above); the metric API line (§D-1.2); R-14a inlined now, not "at signing"; `added_purposes` includes `lockbox_prediction`; the §6 checklist is updated. | Annex §D-1.2, §D-2.7; DRAFT §2.4, §6 |

**Re-check:** a focused two-family re-check of rev 2 follows (R19-2).
