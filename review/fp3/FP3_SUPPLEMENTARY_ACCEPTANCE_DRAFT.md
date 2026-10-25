# Supplementary acceptance of the D-19 preregistration: the drand chain (FP3)

**Status: AI WORDING PROPOSAL — NOT ADOPTED — NOT SIGNED — NOT BINDING.** Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, from the owner's choices in `OWNER_PREFERENCES_2026-10-25.md` (route R3-strong, `quicknet`, void after 7 days, re-post with no change), following `GOVERNANCE_OPINION_FP3_FABLE.md` §4. It becomes binding only when the owner adopts it as his own and makes a signed, dated commit of the adopted text personally, before step G. Until then, step G stays blocked.

---

## Text proposed for the owner to adopt

**1. What this is.** I, the owner, accept this record as a supplement to my acceptance of the D-19 preregistration (`review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`, SHA-256 `ffadd2b5cdc72fa663ba5a0661f47fcdc2615ad8f660122b7611eb57e8f09f71`, accepted in `review/d19-engine/ACCEPTANCE_RECORD.md`). It fixes, for D-19 attempts 1 and 2 only, what preregistration §8 calls "the C2 drand chain (DRAFT §2.0)". It does not change the preregistration's text or hash, any frozen file, the Constitution or the protocol. It is not a Constitution §4 amendment.

**2. The chain.** For D-19, "the C2 drand chain" is read as the drand League of Entropy mainnet chain `quicknet`:

| Field | Value |
|---|---|
| Chain hash | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` |
| Public key | `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a` |
| Scheme | `bls-unchained-g1-rfc9380` |
| Period | 3 seconds |
| Genesis time | 1692803367 (UTC seconds) |
| Source record | `review/fp3/drand-info-2026-10-25/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971.info.json`, SHA-256 `3e690bc527c8a4e78232bc06b5a3cff057c51c68f51b208a1a21b2abd6d6b194`, fetched 2026-10-25 from `api.drand.sh` |

**3. The round.** Unchanged from preregistration §8: the first round of this chain whose scheduled time is at or after `T_Qn + 24h`, with `T_Qn` fixed from the attempt's `AQTQ1` post as in O-6a SPEC §5. A round's scheduled time is genesis time + (round − 1) × period.

**4. Verification.** A round's output is valid only if its signature verifies against the public key above under the chain's scheme. Its randomness is the SHA-256 of that signature, as drand defines for this chain. The round number, signature, randomness, the source of each copy and its retrieval time are recorded for Constitution §27. A successful download is not a verification.

**5. If the output does not exist.** The output exists if a verifying output for the round is obtained from any public drand source, by any machine, within 7 days of the round's scheduled time, with its response and retrieval time recorded. The failure of one machine or one source is not a missing output: other sources and machines are tried within the 7 days. If no source can supply a verifying output within those 7 days, the attempt is **void** before any held-out evaluation:
- no held-out run is made, and the attempt's namespace is not burned;
- the attempt's key is used up (DF5-1);
- no other chain or source is ever used for this attempt.

**6. Attempt 2 after such a void.** The same qualification object may be posted again with key `A_Q2`, under namespace `d19-heldout-v2`, on the same chain, with no recorded change. This is the same as preregistration §4 provides after an O-6a void. `D_Q2` is fixed in the attempt-2 record before its post, as the preregistration says.

**7. If the chain stops for good or is retired.** That never allows a switch to another chain. Rule 5 applies to each attempt. If both attempts are void, qualification has not been obtained under this preregistration (§4, DF5-1). Any other chain would need a new, prospective formal binding, with earlier exposure and attempt accounting kept.

**8. Prospective.** This record is committed before step G: before any qualification object is built or posted, and before any round of this chain that could be used has been determined. Nobody can know any future round's output at that time.

**9. C2.** I expect the C2 §4 amendment to fill its §2.0 beacon field with the chain above and to bind this record by hash. If C2 does not do so, the D-19 certification cannot be used by C2.

**10. Signature.** Adopted as my own and committed with my signature on the date of the commit (UTC).

---

## Notes for reviewers (not part of the adopted text)

- Choices behind it: `OWNER_PREFERENCES_2026-10-25.md` items 2-5; route basis: `GOVERNANCE_OPINION_FP3_FABLE.md` §2, §4 (GOV-FP3-3 records that no text expressly authorises this route; Codex FP3-R1 disagreed).
- Rule 5 replaces DRAFT §2.0's bare "exists" with an evidence criterion (FP3-R3). It is a new owner choice, not a consequence of the preregistration.
- Rule 6 answers GOV-FP3-5.
- After adoption, the AI proposes updates to `FREEZE_HELDOUT.md` FP3 and step K (separating the drand check from the O-6a invalidation record, GOV-FP3-6) and a C2 §2.0 wording proposal; the verification tool is pinned and tested before G (FP3-R5).
