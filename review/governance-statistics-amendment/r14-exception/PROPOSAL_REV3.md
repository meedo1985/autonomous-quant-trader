# R-14a, rev 3 (erratum; delta on rev 2)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority. **Status: INACTIVE PROPOSAL.** This is a text-only erratum, and everything not named below stands as in `PROPOSAL_REV2.md` (f1be832). Both rev 2 re-checks are ACCEPT WITH NOTES with no blocker, and both say the proposal is ready for the owner's decision:
- `SOL_RECHECK_F1BE832.md` (gpt-6-sol): R14A2-S-1;
- `ASTRA_RECHECK_F1BE832.md` (gpt-6-astra): R14A2-A-1..2.

No further re-check is planned for this erratum.

| ID | Disposition | Repair |
|---|---|---|
| **R14A2-S-1** (the chain in item 2 is abbreviated; the post carries `declaration_sha256`, not `protocol_hash`) | **Accepted.** | item 1 below |
| **R14A2-A-1** (A7's confirmation-side forecast and sealing could be put only in the lockbox module, where the experiment engine cannot call it) | **Accepted.** | item 2 below |
| **R14A2-A-2** (the later anchor is not proof that no earlier protected read happened) | **Accepted.** | item 3 below |

**Item 1. R-14a item 2 becomes:**

> 2. **Verified before any protected-data read.** The evaluation verifies and logs this chain, and refuses on any mismatch or unverifiable step, reading no protected data:
>    1. the accepted C2 post (DRAFT §2.0, O-6a §3);
>    2. the declaration bytes matching its `declaration_sha256`;
>    3. the declaration's `protocol_hash`;
>    4. the complete signed C2 protocol bytes that hash to it, which contain both module SHA-256 rows of this R-14a;
>    5. the loaded module bytes.
>
>    A module hash recorded anywhere other than those protocol bytes does not satisfy this item. Nothing else is loaded from outside R-14 and this row.

Rev 2's §1a row for R14A-S-5 ~ R14A-A-4 now reads the chain as above.

**Item 2. Added to R-14a item 5 (the contract):**

> The confirmation module's contract allocates D-20 A7's confirmation-side work, so that it runs on the experiment-engine path: recomputing the confirmation source, the forecast (A4) and sealing the prediction artifact. The lockbox module's contract covers only the `lockbox_eval` side. Each contract names the code that produces each A7 field. Which hash or hashes A7's `code.lockbox_module_sha256` field holds is fixed there, in the S4 text, and is not decided by this row.

**Item 3. Added to rev 2 §2, after "Still lost":**

> - **Not proof of earlier reads.** The later public anchor fixes these bytes. It does not independently prove that no protected-data access occurred earlier. The read gates and access records (D-11, Constitution §7/§7a) remain the controls for that.

**Self-check:** one file written; all 3 notes answered; no mechanism, row or owner question added.
