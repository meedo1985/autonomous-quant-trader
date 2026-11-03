# Governance re-review 2 of the FP3 supplementary acceptance draft, revision 3 (631541e)

Agent `senior-statistical-governance`, read-only, checkout `aqt-freeze-sheet` at `3d2c4c5`, prompt `FP3_SUPPLEMENTARY_REREVIEW2_PROMPT.md`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Received 2026-10-25. Report verbatim below (harness indentation removed).

---

**Observed model:** Claude Fable 5.1 (`claude-fable-5-1`). Read-only re-review of `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `3d2c4c5` (working tree clean; draft unchanged since `631541e`). Independent reviewer, not an authority; nothing here is an acceptance or a signature, and nothing is activated.

**Verdict: FIX.** All five FP3S2 findings are resolved. The new Rule 5 has one wording blocker (G1) and one question the owner must decide (G2).

## 1. FP3S2 findings
- **G1: resolved.** The owner chose option (b) (item 6), and Rule 5 implements it in "Evidence found later". That option has a side effect, raised as FP3S3-G2.
- **G2: resolved.** "The run does not wait for `C`."
- **G3: resolved.** `/info` and `public/latest` are recorded, a latest round ≥ `r` rules out a void, and the notes say "reduces".
- **G4: resolved.** Late output after a void is not used; the restart residual is disclosed in Rule 5.
- **G5: resolved.**

## 2. Checked myself today (fetched, not read)
- `api.drand.sh`, `api2.drand.sh` and `api3.drand.sh` serve quicknet `/info` byte-identical to the source record (SHA `3e690bc5…`).
- The three drand.sh hosts all report `Server: nginx/1.28.3`, at AWS addresses in three regions.
- `drand.cloudflare.com` serves the same JSON plus one trailing `\n` (SHA `1ae9f581…`).
- The latest rounds reported by the four endpoints were within 1 of each other.
- Who operates each endpoint is an `UNVERIFIED_EXTERNAL_ASSUMPTION`.

## 3. New findings

**FP3S3-G1 — BLOCKER (wording) — Rule 5, "Checks to make", "Void" item 3 and "No void" bullet 1.**
- **What the text allows:**
  - A ≥ `r` report rules out a void only if it comes from a *functioning* endpoint at a *decisive* check.
  - A check with fewer than two functioning endpoints can be repeated.
  - "Functioning" depends on a response arriving, and a request the owner's own machine blocks or drops makes that endpoint non-functioning.
- **Failure:**
  - The chain is halted at `C` and restarts within `[C, C+24h]`, or the relays lag behind the chain.
  - Endpoint A reports ≥ `r` at a check where only A responded; that check is invalid, so it is repeated.
  - At the repeat, two lagging endpoints report < `r`. The attempt is void, against a ≥ `r` report already on record.
  - Once the output is public, the same lever lets someone who has seen it pick void or no void by choosing which endpoints respond.
- **The Notes overclaim:**
  - "A void cannot be chosen after seeing the output" holds only for outputs that existed by `C`.
  - "Late output gives a void" leaves out the restart-in-window exception that Rule 5 discloses.
  - "A chain's latest round never decreases" is true of the chain, not of what one endpoint reports.
- **Minimal repair (wording):**
  - "A report of a latest round ≥ `r` by any bound endpoint at any check made at or after `C`, valid or not, rules out the void."
  - "The decisive check is the first check at or after `C` at which at least two bound endpoints function. Once it is valid, it is not repeated."
  - Correct the two Notes sentences.

**FP3S3-G2 — QUESTION, for the owner — Rule 5 "Evidence found later" (item 6). My own option (b) created this.**
- **How it arises:** after a wrong void (stale relays while the chain was live), `r`'s output becomes public. The owner alone decides when attempt 2 is posted, and how hard to look for evidence that the chain had reached `r` by `C`.
- **Why it matters:** if attempt 1's result looks good, he searches and delays; if it looks bad, he posts attempt 2 at once. Either way he can choose based on the result.
- **How narrow:** it needs a wrong void and the output to become public before the post.
- **Proposal (owner decision; I am not changing his choice):** a fixed evidence window that does not depend on the post, e.g. "evidence shown within 7 days after the void is recorded cancels it, and attempt 2 is not posted before that window ends".
- **Alternative:** accept this residual explicitly in the text.

**FP3S3-G3 — NON-BLOCKING — Rule 5 "Bound endpoints".**
- **What is wrong:** "Its `/info` response matches Rule 2" is ambiguous. Rule 2 includes the source record's SHA-256; read as byte-match, Cloudflare (trailing LF) is never functioning. The two functioning endpoints could then both be drand.sh hosts, which look like one operator. Revision 2's "independent" requirement was dropped.
- **Repair:** define "matches" as the hash, public key, scheme, period and genesis fields equalling Rule 2's values, with byte equality not required; require the two functioning endpoints to include at least two operators, or require Cloudflare to be one of them.

**FP3S3-G4 — NON-BLOCKING — Rule 5 "Checks to make", daily checks.**
- **What is wrong:** daily checks start "from `r`'s scheduled time", but `r` is fixed only at the freeze read, about 6 days later (O-6a §5, sheet step J). That duty cannot be met, although missing it has no consequence.
- **Repair:** "from the freeze read (earlier checks of the provisional round are optional)".

**FP3S3-G5 — NON-BLOCKING — Status header.** The header says "Revision 2"; the text is revision 3. **Repair:** "Revision 3".

## Decisions left to the owner
G2 (a fixed evidence window, or accept the residual); the final wording, adoption, signed commit and push before G.

## Not authorised
Step G, the post, any edit or commit, amendment, activation, acceptance, frozen-file or hash changes, merge, cycle start, promotion, trading.

**Not checked:** the Codex re-review; BLS cryptography (no library available); who operates each endpoint.

**Risk:** until G1 is fixed, a void in the rare restart or lagging-relay case can be chosen after the output is known.
