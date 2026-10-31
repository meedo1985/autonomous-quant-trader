# Supplementary acceptance of the D-19 preregistration: the drand chain (FP3)

**Adopted by the owner.** Text of draft revision 4 (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md` at `802be05`), accepted by both different-model reviews (`review/fp3/FABLE_FP3_SUPPLEMENTARY_REREVIEW3.md`, `review/fp3/SOL_FP3_SUPPLEMENTARY_REREVIEW3.md`). Binding from the owner's own signed commit of this file, pushed before step G.

**1. What this is.** I, the owner, accept this record as a supplement to my acceptance of the D-19 preregistration (`review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`, SHA-256 `ffadd2b5cdc72fa663ba5a0661f47fcdc2615ad8f660122b7611eb57e8f09f71`, accepted in `review/d19-engine/ACCEPTANCE_RECORD.md`). For D-19 attempts 1 and 2 only:
- it fixes what preregistration §8 calls "the C2 drand chain (DRAFT §2.0)";
- it adds Rules 5 and 6. The preregistration does not contain these rules. They are terms of this supplementary acceptance.

It does not change the preregistration's text or hash, any frozen file, the Constitution or the protocol. It is not a Constitution §4 amendment.

**2. The chain.** For D-19, "the C2 drand chain" is read as the drand chain `quicknet`, served as one of the mainnet chains at `api.drand.sh`:

| Field | Value |
|---|---|
| Chain hash | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` |
| Public key | `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a` |
| Scheme | `bls-unchained-g1-rfc9380` |
| Period | 3 seconds |
| Genesis time | 1692803367 (Unix seconds, UTC) |
| Source record | `review/fp3/drand-info-2026-10-25/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971.info.json`, SHA-256 `3e690bc527c8a4e78232bc06b5a3cff057c51c68f51b208a1a21b2abd6d6b194`, fetched 2026-10-25 from `api.drand.sh` |

**3. The round.** Unchanged from preregistration §8: the first round of this chain whose scheduled time is at or after `T_Qn + 24h`. `T_Qn` is fixed from the attempt's `AQTQ1` post, as in O-6a SPEC §5.
- `T_Qn`, a 14-digit CDX timestamp, is read as UTC and converted to Unix seconds.
- 24h is 86,400 seconds.
- Round `r` is scheduled at 1692803367 + (r − 1) × 3 seconds.
- "At or after" includes a round scheduled exactly at `T_Qn + 86400`.

**4. Verification.** A round's output is valid only if its signature verifies, for that round number, against the public key above under the chain's scheme.
- The randomness is the SHA-256 of the raw 48-byte signature, recorded as 64 lowercase hex characters.
- This computed value is used even if a response carries a different `randomness` field.
- A copy of this round's output may come from any source: any drand endpoint, relay or archive. Valid copies carry the same round and signature.
- The round number, signature, randomness, and each copy's source and retrieval time are recorded for Constitution §27. The verified output is committed before the held-out run starts.
- A successful download is not a verification.

**5. No time limit.** The held-out run of an attempt waits until a verifying output for its round is obtained, from any source, at any time. That output is always the one used.
- A missing, late or hard-to-fetch output never makes the attempt void or failed, and never permits a different round.
- No other beacon, chain or randomness source is ever used.
- The attempt can still end for the preregistration's own reasons (§4: an O-6a invalidation, a failure, certification).

**6. If the chain stops for good or is retired.** The attempt waits. That never allows a switch to another chain or round. The attempt can be released only by a new, prospective formal decision of mine, made under the Constitution's rules. That decision keeps earlier exposure and attempt accounting, and it is made while no output for the attempt's round exists.

**7. Prospective.** This record is pushed before step G. At that time:
- no qualification object exists for D-19;
- no `AQTQ1` post has been made;
- no `T_Qn` is fixed;
- so no round is selected, and no output for it is public.

The protection relies on the fixed chain's security. drand's threshold assumption is that no group of operators at or above the threshold colludes to learn outputs early.

**8. C2.** I expect the C2 §4 amendment to fill its §2.0 beacon field with the chain above and to bind this record by hash. If C2 does not do so, the D-19 certification cannot be used by C2.

**9. Signature.** Adopted as my own and committed by me, signed, on the date of the commit (UTC), and pushed before step G.

