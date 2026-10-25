# Supplementary acceptance of the D-19 preregistration: the drand chain (FP3)

**Status: AI WORDING PROPOSAL — NOT ADOPTED — NOT SIGNED — NOT BINDING.** Revision 2. Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, from the owner's choices in `OWNER_PREFERENCES_2026-10-25.md` (route R3-strong, `quicknet`, void judged by existence, re-post with no change), following `GOVERNANCE_OPINION_FP3_FABLE.md` §4, and repaired after the reviews `FABLE_FP3_SUPPLEMENTARY_REVIEW.md` and `SOL_FP3_SUPPLEMENTARY_REVIEW.md` (`ADJUDICATION_FP3_SUPPLEMENTARY.md`).

**It becomes binding only when all of these hold, before step G:**
1. The two different-model reviews of the final text are committed with their findings and model metadata. They are the governance reviewer's (`senior-statistical-governance`) and Codex's, each ending in ACCEPT.
2. The owner adopts the text below as his own.
3. The owner personally makes a verifiably signed commit of the adopted text, with a UTC date.
4. That commit is pushed to GitHub. GitHub's recorded push time is the evidence that it came before G, because Git commit dates are set by their author.

Until then, step G stays blocked.

---

## Text proposed for the owner to adopt

**1. What this is.** I, the owner, accept this record as a supplement to my acceptance of the D-19 preregistration (`review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`, SHA-256 `ffadd2b5cdc72fa663ba5a0661f47fcdc2615ad8f660122b7611eb57e8f09f71`, accepted in `review/d19-engine/ACCEPTANCE_RECORD.md`). For D-19 attempts 1 and 2 only:
- it fixes what preregistration §8 calls "the C2 drand chain (DRAFT §2.0)";
- it adds Rules 5, 6 and 7. The preregistration does not contain these rules. They are terms of this supplementary acceptance.

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

**5. If the chain does not reach the round within 7 days.** Let `r` be the attempt's round and `C` its cutoff: `r`'s scheduled time + 604,800 seconds (7 days).
- **The governing fact** is whether this chain had reached round `r` by `C`. Evidence that it had is either of these, from any public source with a time at or before `C`:
  - a verifying output for `r`;
  - a report by a drand endpoint serving this chain (its `/info` matches Rule 2) of a latest round ≥ `r`.
- **Bound endpoints:** `api.drand.sh`, `api2.drand.sh`, `api3.drand.sh` and `drand.cloudflare.com`. At a given check, an endpoint is **functioning** if its `/info` response matches Rule 2.
- **A check** asks each bound endpoint for its `/info`, its `public/latest` and round `r`. Each raw response and its UTC time are recorded, then committed and pushed the same day.
- **Checks to make:**
  - from `r`'s scheduled time, until a verifying output for `r` is obtained: at least one check per UTC day, as evidence;
  - if no output has been obtained by `C`: the **decisive check**, made between `C` and `C` + 86,400 seconds. It may be repeated within that period if fewer than two endpoints are functioning.
- **Use.** A verifying output for `r` obtained from any source is used (Rule 4), except as stated under "Late output" below.
- **No output yet.** While no verifying output has been obtained, the held-out run waits. Once one is obtained, the run may proceed as the preregistration and the sheet say. The run does not wait for `C`.
- **Void.** The attempt is **void** only if all of these hold:
  1. no verifying output for `r` has been obtained;
  2. at a decisive check, at least two bound endpoints were functioning;
  3. every functioning endpoint reported a latest round below `r`;
  4. no other evidence shows that the chain had reached `r` by `C`.

  Because a chain's latest round never decreases, a latest round below `r` after `C` shows that the chain had not reached `r` by `C`.
- **No void:**
  - If any functioning endpoint reports a latest round ≥ `r` at a decisive check, there is no void. The output is taken to exist and is fetched until obtained. This holds even in the rare case where the chain restarted within the 24 hours after `C`. The output's value is fixed, so this gives no choice.
  - If no valid decisive check is made by `C` + 86,400 seconds (a check needs at least two functioning endpoints), no void is possible. The output of `r` is used when obtained.
  - A failed request never counts as evidence that the output is missing.
- **Late output.** If the attempt is void, an output of `r` that appears later is not used.
- **Consequences of a void.** No held-out run is made, and the namespace is not burned. The attempt's key is used up (DF5-1).
- **Evidence found later.** If, **before attempt 2's `AQTQ1` post**, evidence shows that the chain had reached `r` by `C`, the void is cancelled and attempt 1 continues with the output of `r`. Once attempt 2 has been posted, the void of attempt 1 stands, whatever evidence appears later.
- **No substitute source.** No other beacon, chain or randomness source is ever used. Copies of this chain's round from any source are allowed under Rule 4.

**6. Attempt 2 after a void under Rule 5.** The same qualification object may be posted again with key `A_Q2`, under namespace `d19-heldout-v2`, on the same chain, with no recorded change. This is the same as preregistration §4 provides after an O-6a void. `D_Q2` is fixed in the attempt-2 record before its post, as the preregistration says. Attempt 2 is checked under Rule 5 in the same way.

**7. If the chain stops for good or is retired.** That never allows a switch to another chain. Rule 5 applies to each attempt. If both attempts are void, qualification has not been obtained under this preregistration (§4, DF5-1). Any other chain would need a new, prospective formal binding, with earlier exposure and attempt accounting kept.

**8. Prospective.** This record is pushed before step G. At that time, no qualification object exists for D-19, no `AQTQ1` post has been made, no `T_Qn` is fixed, and therefore no round is selected and its output is not public. The protection relies on the fixed chain's security. drand's threshold assumption is that no group of operators at or above the threshold colludes to learn outputs early.

**9. C2.** I expect the C2 §4 amendment to fill its §2.0 beacon field with the chain above and to bind this record by hash. If C2 does not do so, the D-19 certification cannot be used by C2.

**10. Signature.** Adopted as my own and committed by me, signed, on the date of the commit (UTC), and pushed before step G.

---

## Notes for reviewers (not part of the adopted text)

- Rule 5 (revision 3) is an **AI drafting proposal** implementing the owner's choices "Void after 7 days … judged by whether it exists, not whether your laptop could fetch it" and "Deadline at attempt-2 post" (`OWNER_PREFERENCES_2026-10-25.md` items 3 and 6). It is not the owner's wording until he adopts it.
- The void depends on a public fact, whether the chain reached the round by `C`, witnessed through several fixed endpoints. It does not depend on whether a fetch succeeded. An outage of the endpoints that serve outputs cannot void the attempt while any endpoint shows the chain past `r`. A void cannot be chosen after seeing the output: if the output existed by `C`, the chain had reached `r` and the void fails. The daily records are committed and pushed the same day, so they cannot be made up after the fact. This **reduces** the risk of a selective void, but cannot exclude a fabricated record; the committed daily evidence and the cancellation rule are the safeguards (FP3S-G1, FP3S2-G3, FP3S2-R1..R3).
- Late output (the chain reached `r` only after `C`) gives a void. This matches the owner's literal choice and the C2 draft (FP3S2-G4; the earlier revision 2 departure is withdrawn).
- Rule 6 answers GOV-FP3-5.
- Before G, the pinned verification tool must verify a historical quicknet round, including a negative test with a changed signature, and its result must be committed (FP3-R5, FP3S-G8). It goes into the H/I/M rewrite, together with updates to `FREEZE_HELDOUT.md` FP3 and step K (separating the drand check from the O-6a invalidation record, GOV-FP3-6) and a C2 §2.0 wording proposal.
