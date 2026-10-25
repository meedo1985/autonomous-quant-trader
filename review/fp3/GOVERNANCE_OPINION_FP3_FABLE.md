# Governance opinion on the FP3 route (senior-statistical-governance agent)

Requested by Claude Opus 5.5 at the owner's choice "Expert opinion first (Recommended)" (`OWNER_PREFERENCES_2026-10-25.md`). Agent: `senior-statistical-governance`, read-only, on checkout `aqt-freeze-sheet` at `5d1c875`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Received 2026-10-25. Report below verbatim (the harness's indentation removed).

---

# FP3 governance opinion: how to bind the drand chain before step G

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`. Read-only AI opinion; not an acceptance, amendment or signature.
**Checkout:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, head `5d1c875` (includes `review/fp3/OWNER_PREFERENCES_2026-10-25.md`: quicknet, void-after-7-days, "expert opinion first").
**Verdict: `KEEP_BLOCKED`** (step G) until one binding act is performed by the owner; recommended: R3 in its strong form (§4 below), with R1 as the text-authority fallback.

Protocol items run: 1 (topic search for governing clauses: §1, §3, §4, §5, §8, OWNER_STEP0, prereg l.259/272), 2 (referents checked), 3 (bytes of the prereg and drand files), 4 (key comparison that would catch a wrong value), 5 (the referent argument applied to every route), 6, 9, 11, 12, 13, 14. N/A: 7 (no verifier bears on this), 8 (no numeric identity at stake).

## 1. Smallest valid R1 (a Constitution §4 amendment)

**Authority.** `docs/RESEARCH_CONSTITUTION.md` §3 (l.41–43): "Constitution → Schemas/Threat Model → Cycle Protocol → … This binds owner, humans, AIs, and software." A §4 act at Constitution or protocol level binds anything below it.

**Target document.** FP3_OPTIONS never names one. The smallest real target is a new `protocols/protocol_v1.1.yaml`. Amending only the Constitution still changes the protocol: the protocol carries `constitution_hash` (protocol l.5) and its `freeze_sequence` has "update protocol constitution_hash". A new protocol hash means a new cycle (§5 l.59: "One frozen protocol hash per cycle").

**§4 elements (l.48):**
- **Version bump:** protocol v1.1 as a new file beside the unchanged v1.0. It copies every v1.0 value and must define budget exhaustion, a calendar limit and a promotion-termination rule, or it is invalid (§5 l.61). It adds one block: chain hash, public key, scheme, period, genesis, the round rule and the missing-output rule.
- **Written rationale.**
- **Owner-of-record signed and dated commit,** made by the owner personally (FP3-R4).
- **Cycle termination:** C1 has not started (`review/pre-deployment/S25_SIGNATURE_RECORD.md` l.28). Termination is a recorded `PROTOCOL_REVISION` outcome for C1 (protocol l.192–195), after a check that no C1 trial ever began.
- **Pre-new-cycle activation:** the amendment activates before any cycle record exists under v1.1.
- **72-hour rule:** applies only if the owner classes the change as safety-relevant; the owner should state the classification.
- **Preserved history:** v1.0 and its sidecars untouched.
- **No retroactive effect:** state that no promotion is open.

**Interaction with C2.** R1 uses up the C2 draft's own reserved steps: its files are `docs/RESEARCH_CONSTITUTION_v1.1.md` and `protocols/protocol_v1.1.yaml` (DRAFT_WORDING l.67–68), and its step 5 is "C1 is formally terminated with outcome PROTOCOL_REVISION" (l.408). After R1, C2 becomes v1.2: it must terminate the R1 cycle (also never started) and rename its files, references and precedence text.

**Frozen files.** New files, each with a sidecar; `.gitattributes` `-text` entries added before hashing; entries appended to `FROZEN_HASHES.json` with no v1.0 entry changed. This follows the C2 draft's own pattern (l.70–73), which is an AI default, not a rule. `FROZEN_HASHES.json` does not cover the D-19 preregistration (0 matches for "d19").

## 2. Is there a valid R3 (an owner act short of §4)?

**The case for R3.** Partial disagreement with Codex FP3-R1, which compared the acceptance record and the reading decisions.
- The D-19 preregistration has never been a §4 instrument. All its binding force comes from owner acceptance acts: `OWNER_STEP0_DECISION.md` l.59 ("This is not a Constitution section 4 amendment") and `OWNER_DECISION_D19_ACCEPT.md`.
- Owner acts have already changed both its content and its timing:
  - D19_ACCEPT effect 1 (l.58–59) moved "at the preregistration's acceptance" to a later committed record "before the development phase", on the stated purpose that "no key can be chosen after any held-out-relevant information exists".
  - `OWNER_DECISION_S13_ACCEPT.md` effect 1 (l.50): "§13 rev 7g … overrides the rev 6 sections that it names".
  - The preregistration names a further acceptance as its own way of extending itself (l.259): "Any further key needs a new acceptance".
- A chain fixed before G, when every chain's future output is unknown, cannot steer the result, which is FP3's whole purpose.
- D-19 becomes governance only when the C2 §4 amendment binds it "by hash" (prereg §11 l.448). That signing finally judges whether D-19 counts, whichever route is used now.

**The case against R3.**
- No text allows adding content after acceptance was completed (2026-10-20) and the hash was pinned; both precedents came before completion.
- The referent in prereg §8 l.397 points to the C2 protocol ("fixed in this protocol … at signing", DRAFT l.161), not to the owner.
- Constitution §8 ("Immutable after preregistration") concerns trading hypotheses, so it does not apply by its own terms, but its spirit weighs against R3.

**What the documents support.** They neither authorise nor forbid R3. They support the instrument class (owner acceptance) more than FP3_OPTIONS rev 2 credits, and less than an express authorisation would.

**The referent gap affects every route (GOV-FP3-2).** R1, unless it *is* the C2 protocol, does not literally fill "the C2 drand chain" either. Each route needs a reading clause ("for D-19, read as chain X"), revised C2 draft wording that fills §2.0 with X, and ratification at the C2 signing.

## 3. Is R4 materially costlier than R1?

**Yes, by far.**
- `calibration/qobj.py` l.235–237 and l.347–349 refuse to build if the prereg hash differs from the run definition's.
- The run definition pins `prereg_sha256` = `ffadd2b5…`, and so does `calibration/rundef.py` l.270.
- Development seeds are anchored on the prereg hash (§8 l.390; `seed_spec.anchor`).
- A new preregistration therefore means a new run definition and none of the threshold or development chunks count: months of reruns, plus a §16-protected change to the pin.
- R1 and R3 leave the pinned bytes untouched. Independently verified: the working tree and the index blob both hash to `ffadd2b5…` (`eol=lf` by attribute, 0 CR).

The preregistration's "recorded change" is only the route to attempt 2 after a failure (l.258, l.277); it cannot amend attempt 1's seed source.

## 4. Recommendation and steps for the owner

**Least-cost route I judge valid:** R3 as a **supplementary owner acceptance**. **Fallback:** R1 (protocol v1.1), if the owner wants authority resting on text and accepts renumbering C2.

**Steps:**
1. **The AI drafts a short record, labelled as an AI proposal.** It contains:
   - **Scope:** D-19 attempts 1–2 only, as a reading of §8's "the C2 drand chain (DRAFT §2.0)".
   - **Chain values:** quicknet hash, public key, scheme, period and genesis, plus the SHA-256 of the stored `/info` bytes.
   - **Rules:** the round rule (unchanged) and the verification rule.
   - **Missing output:** if no verifying output for the round is shown to exist within 7 days (existence, not retrieval), the attempt is void before the held-out run, its key is used up, and no fallback chain is ever used.
   - **Attempt 2 after a drand void** (GOV-FP3-5).
   - **Permanent halt:** what follows if the chain stops for good.
   - **Statements:** no change to `PREREGISTRATION.md` or any frozen file; prospective and made before G; C2 is expected to fill §2.0 with the same chain and bind this record by hash, and if it does not, the D-19 certification cannot be used.
2. **Reviews:** two different-model reviews, each committed (R19-2, AGENTS.md). This opinion counts as one only once committed.
3. **Owner signs:** the owner adopts the text as his own and personally makes a verifiably signed commit with a UTC date, and pushes it before G. GitHub's push time gives third-party timing.
4. **AI follow-up proposals:** update FREEZE_HELDOUT FP3 and step K; propose C2 §2.0 wording that fills in quicknet.

**Residual risk.** Reviewers at the C2 signing may find R3 insufficient, and then D-19 would need redoing under R4. The same dependence on C2 exists under R1.

**Could not determine:** whether any rule outside the files read governs non-frozen owner records; the owner's safety classification for an R1; the drand facts (BLS signature uniqueness, randomness = SHA-256(signature), how chain hashes are derived), which are `UNVERIFIED_EXTERNAL_ASSUMPTION` because I did not fetch from drand.

## Findings

- **GOV-FP3-1 (BLOCKER, against the FP3_OPTIONS §4 R1 row and Codex FP3-R2).** "R1 is the only presently established route" is overstated: R1's target document, cycle identity and collision with the C2 draft (l.67–68, l.408) are not worked out. *Would change if* a text applied §4 directly to non-frozen preregistrations.
- **GOV-FP3-2 (BLOCKER, prereg l.397 against DRAFT l.161).** The referent gap is shared by R1 and R3: each needs a "read as" clause and C2 ratification.
- **GOV-FP3-3 (QUESTION, for the owner).** R3 is supported by the instrument class (D19_ACCEPT l.58–59, S13_ACCEPT l.50, prereg l.259), but no text authorises it. Partial disagreement with Codex FP3-R1. *Would change if* a clause forbidding post-acceptance supplements turned up.
- **GOV-FP3-4 (NON-BLOCKING, qobj.py l.235/347, rundef.py l.270).** Any edit of the preregistration breaks the freeze. R3 must be a separate file; R4 implies reruns.
- **GOV-FP3-5 (BLOCKER for the binding text, prereg l.259/272).** Re-posting with "no recorded change" is allowed only after an O-6a void. The binding must say what follows a drand void. Under the owner's "void" preference, a permanent halt would use up both keys, and qualification under this preregistration would be lost.
- **GOV-FP3-6 (NON-BLOCKING, inherited, FREEZE_HELDOUT step K l.106).** The drand check sits inside the O-6a "invalidation check" record; separate it after binding (related to FP3-R3).
- **GOV-FP3-7 (NON-BLOCKING, `review/fp3/drand-info-2026-10-25/*.headers.txt`).** The header files are LF in the index, CRLF in the working tree, with no attribute, so "raw responses" (FP3_OPTIONS l.3) is not byte-true for headers. The `.info.json` files have no line endings and are byte-stable. Independently matched: the quicknet key (192 hex) is the same across the info file, OWNER_PREFERENCES and FP3_OPTIONS, and a copy with one character changed did not match.
- **GOV-FP3-8 (NON-BLOCKING, signing).** Earlier acceptances were AI-recorded session answers (D19_ACCEPT l.4). Owner-authored signing (FP3-R4) is stronger and should be used.
- **GOV-FP3-9 (QUESTION, R1 only).** Is an R1 safety-relevant (72-hour rule, §4 l.52)? Not applicable to R3. §16 does not apply to a Markdown record.

## Decisions left to the owner

Route (R3-strong or R1); attempt-2 behaviour after a drand void; the final wording and signature, both by the owner.

## Not authorised by this opinion

Step G, any edit or commit, amendment, activation, acceptance, change to frozen files or hashes, merge, cycle start, promotion or trading.

This report must be committed with its findings, per AGENTS.md, before anyone cites it.

Not checked: drand behaviour against live sources. Risk: the R3 recommendation rests on judgement, not express text.

---

## Note by the recorder (Claude Opus 5.5)

The two reviews disagree on one point. Codex FP3-R1 says R3 is not established. This opinion (GOV-FP3-3) says the documents neither authorise nor forbid it, and that R3 is supported by the instrument class. Both agree that no text expressly authorises R3, that R4 is the costliest route, and that whichever route is used, C2's signing must ratify the chain. The choice between R3-strong and R1 is the owner's (GOV-FP3-3, a QUESTION). GOV-FP3-7: `.gitattributes` `-text` for the header files is proposed for the next commit touching them.
