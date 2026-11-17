# Independent re-review 2: FP3 supplementary acceptance draft, revision 3

You are an independent adversarial reviewer (read-only), not an authority. Your re-review of revision 2 (Codex: `review/fp3/SOL_FP3_SUPPLEMENTARY_REREVIEW.md`, FP3S2-R*; governance reviewer: `review/fp3/FABLE_FP3_SUPPLEMENTARY_REREVIEW.md`, FP3S2-G*), the owner's new choice (item 6 of `review/fp3/OWNER_PREFERENCES_2026-10-25.md`) and the adjudication `review/fp3/ADJUDICATION_FP3_SUPPLEMENTARY_REREVIEW.md` led to revision 3. The repair diff is below.

Check only: (1) is each of your FP3S2 findings resolved; (2) is the new Rule 5 (governing fact = chain reached r by C; decisive check between C and C+24h with >=2 functioning bound endpoints; monotonic latest round; no void if any endpoint shows >= r or no valid decisive check; late output after a void not used; evidence before attempt-2 post cancels the void) sound, not gameable, and faithful to the owner choices; (3) any new defect. New findings: Codex `FP3S3-R1..`, governance reviewer `FP3S3-G1..`. Verdict: ACCEPT or FIX. Do not re-open resolved findings unless the repair broke them.

## Repair diff (`git diff 8f56934 631541e -- review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md`)

```diff
diff --git a/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md b/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md
index 967cb56..aba99ed 100644
--- a/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md
+++ b/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md
@@ -40,19 +40,38 @@ It does not change the preregistration's text or hash, any frozen file, the Cons
 **4. Verification.** A round's output is valid only if its signature verifies, for that round number, against the public key above under the chain's scheme.
 - The randomness is the SHA-256 of the raw 48-byte signature, recorded as 64 lowercase hex characters.
 - This computed value is used even if a response carries a different `randomness` field.
-- A copy of this round's output may come from any source: any drand endpoint, relay or archive. Valid copies are identical, because the signature is unique.
+- A copy of this round's output may come from any source: any drand endpoint, relay or archive. Valid copies carry the same round and signature.
 - The round number, signature, randomness, and each copy's source and retrieval time are recorded for Constitution §27. The verified output is committed before the held-out run starts.
 - A successful download is not a verification.
 
-**5. If the output is missing.** The round's output exists, and is used, if a verifying output for the round is obtained from any source at any time. The attempt is **void** only through a void check, as follows:
-- **Cutoff.** `C` = the round's scheduled time + 604,800 seconds (7 days). Until `C`, the held-out run waits.
-- **Void check.** After `C`, requests for the round go to at least two independent public drand endpoints, for example `api.drand.sh` and `drand.cloudflare.com`. None returns a verifying output. Each request's raw response and UTC time are recorded, committed and pushed before anything else is done for the attempt.
-- **Final.** The void becomes final only if a second void check, made at least 24 hours after the first, again finds no verifying output at two independent endpoints. If any check, or anyone, obtains a verifying output for the round before the void is final, there is no void and that output is used.
-- **Consequences.** No held-out run is made, and the namespace is not burned. The attempt's key is used up (DF5-1).
-- **False void.** If it is later shown that a verifying output was publicly available when a void check was made, the attempt counts as **failed**, not void. Its namespace is burned, and any further attempt needs a recorded change.
-- **No substitute source.** No other beacon, chain or randomness source is ever used. Copies of this chain's round from any source are allowed, under Rule 4.
-
-**6. Attempt 2 after a final void under Rule 5.** The same qualification object may be posted again with key `A_Q2`, under namespace `d19-heldout-v2`, on the same chain, with no recorded change. This is the same as preregistration §4 provides after an O-6a void. `D_Q2` is fixed in the attempt-2 record before its post, as the preregistration says.
+**5. If the chain does not reach the round within 7 days.** Let `r` be the attempt's round and `C` its cutoff: `r`'s scheduled time + 604,800 seconds (7 days).
+- **The governing fact** is whether this chain had reached round `r` by `C`. Evidence that it had is either of these, from any public source with a time at or before `C`:
+  - a verifying output for `r`;
+  - a report by a drand endpoint serving this chain (its `/info` matches Rule 2) of a latest round ≥ `r`.
+- **Bound endpoints:** `api.drand.sh`, `api2.drand.sh`, `api3.drand.sh` and `drand.cloudflare.com`. At a given check, an endpoint is **functioning** if its `/info` response matches Rule 2.
+- **A check** asks each bound endpoint for its `/info`, its `public/latest` and round `r`. Each raw response and its UTC time are recorded, then committed and pushed the same day.
+- **Checks to make:**
+  - from `r`'s scheduled time, until a verifying output for `r` is obtained: at least one check per UTC day, as evidence;
+  - if no output has been obtained by `C`: the **decisive check**, made between `C` and `C` + 86,400 seconds. It may be repeated within that period if fewer than two endpoints are functioning.
+- **Use.** A verifying output for `r` obtained from any source is used (Rule 4), except as stated under "Late output" below.
+- **No output yet.** While no verifying output has been obtained, the held-out run waits. Once one is obtained, the run may proceed as the preregistration and the sheet say. The run does not wait for `C`.
+- **Void.** The attempt is **void** only if all of these hold:
+  1. no verifying output for `r` has been obtained;
+  2. at a decisive check, at least two bound endpoints were functioning;
+  3. every functioning endpoint reported a latest round below `r`;
+  4. no other evidence shows that the chain had reached `r` by `C`.
+
+  Because a chain's latest round never decreases, a latest round below `r` after `C` shows that the chain had not reached `r` by `C`.
+- **No void:**
+  - If any functioning endpoint reports a latest round ≥ `r` at a decisive check, there is no void. The output is taken to exist and is fetched until obtained. This holds even in the rare case where the chain restarted within the 24 hours after `C`. The output's value is fixed, so this gives no choice.
+  - If no valid decisive check is made by `C` + 86,400 seconds (a check needs at least two functioning endpoints), no void is possible. The output of `r` is used when obtained.
+  - A failed request never counts as evidence that the output is missing.
+- **Late output.** If the attempt is void, an output of `r` that appears later is not used.
+- **Consequences of a void.** No held-out run is made, and the namespace is not burned. The attempt's key is used up (DF5-1).
+- **Evidence found later.** If, **before attempt 2's `AQTQ1` post**, evidence shows that the chain had reached `r` by `C`, the void is cancelled and attempt 1 continues with the output of `r`. Once attempt 2 has been posted, the void of attempt 1 stands, whatever evidence appears later.
+- **No substitute source.** No other beacon, chain or randomness source is ever used. Copies of this chain's round from any source are allowed under Rule 4.
+
+**6. Attempt 2 after a void under Rule 5.** The same qualification object may be posted again with key `A_Q2`, under namespace `d19-heldout-v2`, on the same chain, with no recorded change. This is the same as preregistration §4 provides after an O-6a void. `D_Q2` is fixed in the attempt-2 record before its post, as the preregistration says. Attempt 2 is checked under Rule 5 in the same way.
 
 **7. If the chain stops for good or is retired.** That never allows a switch to another chain. Rule 5 applies to each attempt. If both attempts are void, qualification has not been obtained under this preregistration (§4, DF5-1). Any other chain would need a new, prospective formal binding, with earlier exposure and attempt accounting kept.
 
@@ -66,7 +85,8 @@ It does not change the preregistration's text or hash, any frozen file, the Cons
 
 ## Notes for reviewers (not part of the adopted text)
 
-- Rule 5's void-check procedure is an **AI drafting proposal** implementing the owner's choice "judged by whether it exists, not whether your laptop could fetch it". It is not the owner's wording until he adopts it.
-- The rule differs from the C2 draft's "no verifying output exists within 7 days": an output first published after `C` but before a void is final is used. Its value is unique, so lateness gives no choice. The two-check, two-endpoint requirement and the false-void-means-failed rule remove the free-second-draw incentive (FP3S-G1).
+- Rule 5 (revision 3) is an **AI drafting proposal** implementing the owner's choices "Void after 7 days … judged by whether it exists, not whether your laptop could fetch it" and "Deadline at attempt-2 post" (`OWNER_PREFERENCES_2026-10-25.md` items 3 and 6). It is not the owner's wording until he adopts it.
+- The void depends on a public fact, whether the chain reached the round by `C`, witnessed through several fixed endpoints. It does not depend on whether a fetch succeeded. An outage of the endpoints that serve outputs cannot void the attempt while any endpoint shows the chain past `r`. A void cannot be chosen after seeing the output: if the output existed by `C`, the chain had reached `r` and the void fails. The daily records are committed and pushed the same day, so they cannot be made up after the fact. This **reduces** the risk of a selective void, but cannot exclude a fabricated record; the committed daily evidence and the cancellation rule are the safeguards (FP3S-G1, FP3S2-G3, FP3S2-R1..R3).
+- Late output (the chain reached `r` only after `C`) gives a void. This matches the owner's literal choice and the C2 draft (FP3S2-G4; the earlier revision 2 departure is withdrawn).
 - Rule 6 answers GOV-FP3-5.
 - Before G, the pinned verification tool must verify a historical quicknet round, including a negative test with a changed signature, and its result must be committed (FP3-R5, FP3S-G8). It goes into the H/I/M rewrite, together with updates to `FREEZE_HELDOUT.md` FP3 and step K (separating the drand check from the O-6a invalidation record, GOV-FP3-6) and a C2 §2.0 wording proposal.
```
