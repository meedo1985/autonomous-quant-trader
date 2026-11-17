# Sol review of the freeze/held-out sheet draft (6e8c646)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: prompt; the sheet; prereg §4-§6, §8, §13 rev 7g; O-6a SPEC rev 5 §2-§7; DRAFT_WORDING lines 155-165, 336-342; `calibration/qobj.py` excerpts; `scripts/d19_heldout.py` header; `d19.sh` command list at `eeaa728`; the `FREEZE_REVIEWS.json` absence check; Electrum 4.8.2 `payment_identifier.py` excerpts (all pasted; its shell cannot run here).
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX (FH-1..FH-7). Sol confirmed FP2 and FP3 are real and the Electrum line gives the exact 39-byte script.

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| FH-1 | BLOCKER | The freeze read (J) kept only response bodies, not the O-6a §4 evidence (query URI, every page, headers, status, time, SHA-256, the bound `id_` fetch). | **Accepted, repaired:** the AI makes the one-time read from the owner's laptop with `curl`, saving and committing every page with headers, status, time and SHA-256, and the `id_` fetch bound to its CDX row. |
| FH-2 | BLOCKER | An invalidation found after L starts could still lead to acceptance at M. | **Accepted, repaired:** M repeats the chain and capture checks (never the CDX read) before the owner's decision; anything found at or after the start fails the attempt. |
| FH-3 | BLOCKER | K accepted any verifying drand output, ignoring DRAFT §2.0's 7-day rule. | **Accepted, repaired as a stop:** K records the round's scheduled time and output and stops before L if no verifying output exists within 7 days. Whether that rule binds D-19 is part of the FP3 governance step, so the sheet does not decide void or fail itself. |
| FH-4 | MAJOR | "Two records" listed three items; the start-time record was undefined. | **Accepted, repaired:** record 1 is the invalidation check (with the drand evidence in it); record 2 defines the start as the first launch after its commit, with docker's recorded start time appended after the launch. |
| FH-5 | MAJOR | G ran `d19.sh freeze` from the pinned `eeaa728` checkout, which lacks it. | **Accepted, repaired:** FP2 (d) requires the new launcher in a second checkout `/opt/aqt-d19/build`, verified on the server; G, L and M run from there; `/opt/aqt-d19/app` stays the run's checkout. |
| FH-6 | MAJOR | The fee was "the estimate for 6 blocks", not the verifier node's `estimatesmartfee 6`. | **Accepted, repaired:** H uses and records the node's estimate; Electrum's or an explorer's does not count. |
| FH-7 | MAJOR | No way to move the object's files to the laptop. | **Accepted, repaired:** an `scp -r` line, then the AI checks the file list, manifest and hash with `qobj.read` before the PR. |

Wording point (FP3 rationale: "once beacon outputs are known", not round times): accepted.

No finding is left unrepaired.

## Reviewer's final output (verbatim)

**Verdict: FIX.** The sheet correctly marks the attempt as unusable while FP2 and FP3 are open. It also has gaps that could let an attempt proceed without the required freeze evidence or accept a result after invalidation.

| ID | Severity | Sheet location | Concrete failure case | Smallest fix |
|---|---|---|---|---|
| FH-1 | BLOCKER | J, freeze read | The owner sends copied CDX response bodies, but the one-time read lacks response headers, status, retrieval time, exact query URI, or a complete page. A purported earliest capture then cannot be verified under O-6a §4–§5. | Give the owner an exact capture procedure that preserves **every page** of both CDX responses with those fields and SHA-256. Preserve the qualifying `id_` body, headers and status, and verify its URL, timestamp and digest against the exact CDX row before fixing `T_Q1`. |
| FH-2 | BLOCKER | K–M | A later spend, chain change, or newly shown earlier qualifying capture is found after L begins. `certify` exits 0 and M still offers acceptance, although the attempt has failed. | Add an invalidation check at certification and immediately before the owner’s decision; route any condition found at or after run start to **failed attempt**. Keep the CDX freeze read itself a one-time read. |
| FH-3 | BLOCKER | K.1 | A valid drand output first appears more than seven days after its scheduled round time. K accepts it merely because its signature verifies, despite DRAFT §2.0’s failure rule. | Record the round, signature, randomness, scheduled time and first available verifying output; stop before L if no verifying output exists within seven days. |
| FH-4 | MAJOR | K.1–K.3 | “Two committed records” is followed by three items, and the sheet does not say how a record committed *before* L states the time L starts. The owner can launch without a compliant DF5-2 start record. | Name the two required records explicitly and specify the precommitted start-time procedure and launcher check. Record the actual launch evidence as well; resolve any difference under the frozen rule before running. |
| FH-5 | MAJOR | FP2, G | The build change is merged, but G still calls `/opt/aqt-d19/app/deploy/calibration/d19.sh` from the pinned `eeaa728` checkout, which has no `freeze` command. | Add a reviewed deployment step that verifies and runs the new launcher from its build commit while keeping `eeaa728` as `run_root`. Make successful installation a checked FP2 condition. |
| FH-6 | MAJOR | H.3 | Electrum’s or an explorer’s six-block estimate is lower than the verifier node’s `estimatesmartfee 6`; the post violates O-6a §7. | Obtain and record the node’s six-block estimate and instruct the owner to set a fee rate at least that high, subject to FP6. |
| FH-7 | MAJOR | G | “Copy the directory to your laptop (Notepad file then)” does not tell the owner how to transfer the object’s files. A hash alone cannot be committed and checked before H. | Provide exact file-transfer instructions and a check of the transferred directory’s files and hash before the object PR is merged. |

**FP2 is real:** the pasted launcher lacks all three commands and `FREEZE_REVIEWS.json` is absent. **FP3 is real:** the cited C2 draft leaves the chain hash and public key blank. Binding the chain before the post is the right guard against later chain selection; FP3 is already required before G, which is safer. The rationale should refer to choosing after *beacon outputs are known*: scheduled round times alone reveal no randomness. A draft placeholder does not bind the chain.

With a 64-hex-digit hash substituted without spaces, the Electrum expression pushes `AQTQ1` (5 bytes) plus the hash (32 bytes): `6a 25 41 51 54 51 31` plus 32 bytes, **39 bytes total**. The sheet proposes no governance change and gives the AI no key.
