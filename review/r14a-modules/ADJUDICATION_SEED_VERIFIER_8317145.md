# Adjudication: Sol design review of the seed verifier rev 1, at 8317145

- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the author, 2026-11-09. Not approval.
- Review: `SOL_SEED_VERIFIER_DESIGN_8317145.md` (committed 1e8c780), verdict FIX.

All eight findings are accepted: each names a real gap in rev 1, checked against the cited
text. None is repaired yet; rev 1 stays a draft. Where each goes:

| ID | Decision | Where it is resolved |
|---|---|---|
| SV1-S-1 (no authoritative source for the record hash) | Accepted. Rev 1's "governing input manifest" is caller-controllable, and binding the hash in protocol bytes is circular. | Design rev 2 plus the S4 text: a signed-C2-authorized, append-only post-beacon acceptance record for the verification hash, resolved by the slice-6 loader before any gate. The S4 wording is a governance proposal for the owner. |
| SV1-S-2 (the record asserts its own verification) | Accepted. The pins in rev 1 check claims inside the record. The route transfers trust to a verified process; it cannot remove it. | Design rev 2: bind the executed verifier bytes, lock and real image identity at launch (as FE-4's host-inspected digest), an independent rebuild or validation for the re-run, and consumer-side checks of `engine_commit` and `image_digest`. Whether an authenticated external check satisfies R-14a item 7's wording goes to the owner with SV1-S-3. |
| SV1-S-3 (R-8 binds the function on the qualification object's image) | Accepted. Calling the identical source in a new image is not literal R-8 compliance. | **Owner decision** (governance, not code): an explicit interpretation or exception in the signed C2 contract for this one external computation, keeping the engine-commit byte check and the evaluation image. |
| SV1-S-4 (two supplied inputs matching authenticates neither) | Accepted; the record also lacks chain hash and scheme. | Design rev 2: name each authoritative loader source (signed chain hash, key and metadata; the freeze-point acceptance record for T; the posted declaration for ordered trials), add chain hash and scheme, refuse missing or extra fields. |
| SV1-S-5 (BLS message bytes unspecified) | Accepted. | Design rev 2: message = SHA-256 of the round as 8-byte unsigned big-endian; signature G1, key G2, DST `BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_`; point and subgroup checks; known answer on the real vector plus negatives. To be checked against drand's own source before build. |
| SV1-S-6 (lockbox handoff still caller-controllable) | Accepted. | Design rev 2 plus slice 6 / store: the sealing record carries the accepted verification hash and seeds; the lockbox request is filled from the immutable sealing entry; a coherent request+artifact substitution test. Touches the accepted lockbox, so its own review. |
| SV1-S-7 (verifier env omits numpy; check_beacon combines local and BLS) | Accepted. | Design rev 2: pin numpy in the verifier env (simplest; no rule copied); split `check_beacon` into the local checks the module keeps and the BLS call the verifier makes. |
| SV1-S-8 (seven-day evidence undefined) | Accepted as a QUESTION. | Design rev 2 names dated, independently checkable availability evidence, checked before evaluation; the rule stays operational (LG4-4). |

Q1-Q5 recommendations noted: Q1 demonstrate the exact G1-signature call and packaging before
choosing; Q2 as SV1-S-1; Q3 treat as §16 protected; Q4 a second host or CI identity that
validates or rebuilds, not the same image twice; Q5 as SV1-S-8.

Reviewer basis note: `DRAFT_WORDING.md` on this branch is rev 9 without R-14a; Sol read
R-14a from `origin/freeze-sheet` (8a1ec72). Rev 2 cites that branch's text.

## Status

Rev 1 **FIX**. Three items (SV1-S-1 and S-6's S4 wording, SV1-S-3) are governance proposals
that need the owner; the rest are design work for rev 2.
