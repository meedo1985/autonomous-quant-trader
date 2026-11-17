# Governance re-review of the FP3 supplementary acceptance draft, revision 2 (8f56934)

Agent `senior-statistical-governance` (same agent as `FABLE_FP3_SUPPLEMENTARY_REVIEW.md`), read-only, checkout `aqt-freeze-sheet` at `d83e9bc`, prompt `FP3_SUPPLEMENTARY_REREVIEW_PROMPT.md`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Received 2026-10-25. Report verbatim below (harness indentation removed).

---

**Observed model:** Claude Fable 5.1 (`claude-fable-5-1`). Read-only re-review of `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, head `d83e9bc` (working tree clean; draft unchanged since `8f56934`). Independent reviewer, not an authority: nothing here is an acceptance or a signature, and nothing is activated.

**Verdict: FIX.** Revision 2 resolves all eight of my earlier findings. The new Rule 5 leaves one case undefined, and that case decides whether a certification counts.

## 1. My earlier findings (FP3S-G1..G8)
Checked against `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md` rev 2. `review/fp3/FABLE_FP3_SUPPLEMENTARY_REVIEW.md` records my report, with 8 G-findings present; I did not compare it byte for byte.

| ID | Status |
|---|---|
| G1 | Resolved as stated: the gap between "exists" and "void" is closed, and an output obtained from any source at any time is used. The new Rule 5 leaves the residual case FP3S2-G1. |
| G2 | Resolved: Rule 1 says it adds Rules 5–7. |
| G3 | Resolved: status conditions 1–4 and Rule 10 (push before G). |
| G4 | Resolved: round number, raw 48 bytes, the computed value overrides the response, committed before the run. |
| G5 | Resolved: Rule 3 conversion. It matches my worked example: T = 20261101000000 gives round 33,591,412, scheduled exactly at T + 86400. |
| G6 | Resolved: Rule 8 states the threshold assumption. |
| G7 | Resolved: labelled an AI drafting proposal. |
| G8 | Resolved as a pre-G condition in the Notes (pinned tool with a negative test); the "League of Entropy" label was removed. |

## 2. New findings

**FP3S2-G1 — BLOCKER — Rule 5 "False void", with Rule 6.**
- **Defect:** a void can be shown false after attempt 2 was posted with no recorded change, or even after attempt 2 was certified. Rule 5 then makes attempt 1 *failed*, and a failed attempt means "any further attempt needs a recorded change". Attempt 2 had none, so its status (valid, void or failed) is undefined.
- **Failure:** both void-check endpoints are down while quicknet is live and another relay serves the round. The owner voids in good faith and re-posts. Attempt 2 passes. Months later, someone shows the round was available at that relay. Whether the PASS stands cannot be decided from the text.
- **Why it can happen honestly:** the falsity test is broader than the void check. "Publicly available" means anywhere, while the check covers only two endpoints. So this happens even when the owner follows the procedure exactly.
- **Minimal repair (an owner decision, either):**
  - (a) Add: "A void shown false makes attempt 1 failed and any attempt 2 posted without a recorded change void, with its key used up. If no key remains, qualification has not been obtained."
  - (b) Add a horizon, following the preregistration's own DF4-2 pattern: a false void counts only if shown before attempt 2's `AQTQ1` post. After that, the final void stands.

**FP3S2-G2 — NON-BLOCKING — Rule 5 "Cutoff".**
- **Defect:** "Until `C`, the held-out run waits" reads as unconditional. Taken literally, every attempt is delayed until 7 days after the round even when a verifying output is in hand. That adds a timing condition beyond preregistration §4/§8 and conflicts with sheet step K (fetch about day 6–7, run after that).
- **Repair:** "While no verifying output has been obtained, the held-out run waits. No void check is made before `C`."

**FP3S2-G3 — NON-BLOCKING — Rule 5 "Void check", and the Notes.**
- **Defect:** the two-check rule deters a void made after peeking at the output, but does not remove it. A void check is a record the owner commits himself, and "later shown publicly available *when the check was made*" needs evidence about time that is hard to obtain after the fact.
- **Cheap repair, which makes a false void visible in the committed record itself:**
  - Each void-check request also records the endpoint's `/info` and its `public/latest` round.
  - Wording: "A check at which any endpoint reports a latest round ≥ r is not a void check."
  - In the Notes, change "remove the free-second-draw incentive" to "reduce" (the conclusion is right; the stated reason was too strong).

**FP3S2-G4 — QUESTION, for the owner — Rule 5 versus his item 3 and C2 §2.0.**
- **Question:** the owner's answer was "never published within 7 days → void". Rev 2 also uses an output first published after `C` but before the void is final, so it departs from his literal answer and from the C2 draft's rule.
- **My view:** I agree that lateness gives no choice of outcome, because the value is unique (BLS uniqueness is an `UNVERIFIED_EXTERNAL_ASSUMPTION`, standard for the scheme). The Notes disclose the change.
- **What is needed:** the owner should explicitly confirm this departure when he adopts the text.

**FP3S2-G5 — NON-BLOCKING — Rule 4.**
- **Defect:** "Valid copies are identical" is not true of the bytes. Round 1,000,000 fetched from api.drand.sh and from drand.cloudflare.com comes back with the JSON fields in a different order, while the round, signature and randomness are equal.
- **Repair:** "Valid copies carry the same round and signature."

## 3. Is Rule 5 sound?
- **Faithful to "judged by existence, not by retrieval":** yes. Use depends on whether the output exists, and a void needs a negative check made after the cutoff and repeated.
- **Gaps:** apart from G1 (consequence undefined) and G3 (fabricated void checks only deterred), I found no outcome-selection route. With no output there is nothing to select; with an output, it must be used.

## Decisions left to the owner
Option (a) or (b) for G1; confirming the G4 departure; the final wording, adoption, signed commit and push.

## Not authorised
Step G, the post, any edit or commit, amendment, activation, acceptance, frozen-file or hash changes, merge, cycle start, promotion, trading.

Not checked: the Codex re-review; BLS cryptography (no library available). The checks run were the diff against HEAD, reading Rule 5 against the preregistration's §4 attempt rules and sheet step K, and a live fetch from two endpoints.
