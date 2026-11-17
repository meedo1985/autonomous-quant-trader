# Adjudication: Sol re-review of the seed verifier design rev 2, at dc4256c

- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the author, 2026-11-09. Not approval.
- Review: `SOL_SEED_VERIFIER_DESIGN_REV2_DC4256C.md` (committed 15ebd8c), verdict FIX.

## Findings

| ID | Decision |
|---|---|
| SV2-S-1 (ledger entry selection unbound) | Accepted. |
| SV2-S-2 (CI execution evidence self-asserted) | Accepted. |
| SV2-S-3 (lazy import escapes the startup byte check; normal-import branch) | Accepted. Repair: import and byte-check `preregistration` and its imports before any protected read; placeholder only on the qualified image; restore `sys.modules` on every exit. Sol confirms the import-time claim itself. |
| SV2-S-4 (fetch failure vs the 7-day outcome merged) | Accepted. |
| SV2-S-5 (consumer checks incomplete) | Accepted. |
| SV2-S-6 (parent DESIGN §5.1 says BLS inside the module) | Accepted; reconcile once the route is chosen. |

## The common cause, and a route decision for the owner

SV2-S-1, S-2, S-4 and S-5 all come from one fact: **the evaluation image has only the
standard library's `hashlib` for cryptography, so it cannot check any signature itself.**
Every external record (ledger entry, CI run, GitHub push) must then be authenticated by
something outside the image, and each round of review finds the next unauthenticated link.
More records will not end this.

Two routes end it:

- **Route E (external, governed):** keep rev 2, add the repairs (signed-C2 ledger identity and
  "first entry for this post" rule; CI attestation checked by a person and recorded; a
  separate deadline outcome), and have the owner accept in the S4 text that the BLS check is a
  governed external verification with a disclosed residual (OD-1). Item 7's "verifies
  itself" is then met by interpretation, not literally.
- **Route M (in-module BLS):** implement BLS12-381 signature verification (quicknet's G1
  signature, exactly §3.2) in pure Python using only the standard library, **inside the
  confirmation module**. A valid signature for round r under the fixed key cannot be forged,
  so the beacon then needs **no authority at all**: whoever supplies it, the module checks it
  itself. SV2-S-1, S-2 and S-5 disappear, SV1-S-1/S-2 close, item 7 is met literally, and R-14a
  item 4 allows it (seed_disclosure states the rule; no engine function implements it). Cost:
  several hundred lines of pairing arithmetic, slow (seconds per check, run once), needing a
  careful different-model cryptographic review and cross-checks against drand's own client
  (the FP3 verifier) on many real rounds plus negatives. The 7-day rule (SV2-S-4) stays an
  operational record in either route.

**Author's recommendation: Route M.** It removes the trust problem instead of documenting it,
needs no new governance mechanism, and keeps line 266's in-image route (§2, with SV2-S-3's
repair). Rev 1 rejected in-module BLS as "a large unreviewed cryptographic rule"; that was
wrong on item 4 (the signed text states the rule) though right that it needs a strong review.

## Status

Rev 2 **FIX**. Waiting on the owner's choice of Route E or Route M before rev 3.
