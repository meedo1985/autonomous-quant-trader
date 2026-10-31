# Supplementary acceptance of the D-19 preregistration: the drand chain (FP3)

**Status: AI WORDING PROPOSAL — NOT ADOPTED — NOT SIGNED — NOT BINDING.** Revision 4. Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, from the owner's choices in `OWNER_PREFERENCES_2026-10-25.md`: route R3-strong (item 4), `quicknet` (item 2), and no time limit for a missing output (item 7, which supersedes items 3, 5 and 6). It follows `GOVERNANCE_OPINION_FP3_FABLE.md` §4 and was repaired through three review rounds (`ADJUDICATION_FP3_SUPPLEMENTARY*.md`).

**It becomes binding only when all of these hold, before step G:**
1. The two different-model reviews of the final text are committed with their findings and model metadata: the governance reviewer's (`senior-statistical-governance`) and Codex's, each ending in ACCEPT.
2. The owner adopts the text below as his own.
3. The owner personally makes a verifiably signed commit of the adopted text, with a UTC date.
4. That commit is pushed to GitHub. GitHub's recorded push time is the evidence that it came before G, because Git commit dates are set by their author.

Until then, step G stays blocked.

---

## Text proposed for the owner to adopt

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

---

## Notes for reviewers (not part of the adopted text)

- Revision 4 replaces revision 3's void rule. The owner chose "No time limit (Recommended)" (item 7) after three review rounds showed that any 7-day cutoff needs proof of *when* drand published. Endpoints can be stale or unreachable, so that proof cannot be obtained cleanly from outside, and each repair left a narrow selective-void route (FP3S3-R1..R3, FP3S3-G1..G2).
- With no void for a missing output, there is no outcome to select. The output is unique, and it is the one used whenever it exists.
- Rules 6 and 7 of revision 3 (attempt 2 after a drand void; the deadline for evidence found later) are withdrawn. They no longer have a case to apply to.
- Rule 6 here: "prospective … while no output for the attempt's round exists" prevents a release decision made after seeing the output.
- This departs from the C2 draft's 7-day rule for C2. This record concerns D-19 only, and C2 keeps its own rule unless the C2 amendment changes it.
- Preregistration §4 "Timing" already makes the held-out run wait for "the publication of the drand round". Rule 5 only removes any time limit on that wait.
- Before G, the pinned verification tool must verify a historical quicknet round, including a negative test with a changed signature, and its result must be committed (FP3-R5, FP3S-G8). It goes into the H/I/M rewrite, together with updates to `FREEZE_HELDOUT.md` FP3 and step K (the 7-day stop in step K is replaced by Rule 5; the drand check is separated from the O-6a invalidation record, GOV-FP3-6) and a C2 §2.0 wording proposal.
