# C2 §2.0 beacon: wording proposal to carry the FP3 chain

**Status: AI WORDING PROPOSAL — NOT AN AMENDMENT — NOT AUTHORED — NOT SIGNED.** Claude Opus 5.5, 2026-10-25. It is for the C2 §4 amendment, which the owner authors and signs after D-19 (`review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` §2.0). The draft itself is not edited here.

## Why

The owner's signed supplementary acceptance (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, commit `d7720be`) reads "the C2 drand chain" as `quicknet` for D-19. Rule 8 expects the C2 amendment to fill its beacon field with the same chain and bind that record by hash. If C2 does not, the D-19 certification cannot be used by C2.

## Proposed replacement for the `beacon:` line of DRAFT §2.0

> beacon: "the drand chain `quicknet`, chain hash `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`, public key `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a`, scheme `bls-unchained-g1-rfc9380`, period 3 s, genesis 1692803367; the same chain as the owner's D-19 supplementary acceptance, bound here by its SHA-256 `<<SHA-256 of FP3_SUPPLEMENTARY_ACCEPTANCE.md at d7720be>>`; the declaration cannot choose it"

The value to fill is `67b5c16528ca8c1b800005b0efbfaf4bd455a97bcdb53a670a58bd09259c4a7b` (recorded in `FP3_BINDING_EVIDENCE.md`). It is left as a marker because the bytes must be re-checked at signing.

The `verification:` line can stay as it is. Adding "randomness = SHA-256 of the raw signature bytes" would make it match FP3 Rule 4.

## A decision C2 will need: its own 7-day failure rule

DRAFT §2.0 `failure:` says "If no verifying output for the round exists within 7 days of its scheduled time, the cycle is INVALIDATED". The FP3 reviews found that such a cutoff needs proof of **when** drand published. That proof cannot be obtained cleanly from outside: endpoints can be stale or unreachable, and three repair rounds each left a narrow selective-void route (`review/fp3/SOL_FP3_SUPPLEMENTARY_REREVIEW*.md`, `FABLE_FP3_SUPPLEMENTARY_REREVIEW*.md`). For D-19 the owner chose no time limit instead.

The C2 rule has the same weakness. When C2 is written, the owner should choose either to:
- (a) use the same no-time-limit rule as D-19, with no invalidation for a missing output and release only by a new prospective formal decision; or
- (b) keep the 7-day rule and accept the residual, stated in the text.

This is a proposal only. The choice is the owner's, at C2.
