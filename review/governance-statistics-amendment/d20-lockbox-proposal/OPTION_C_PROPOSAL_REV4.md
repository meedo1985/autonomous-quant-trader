# D-20 lockbox bindings, option C: release on request (revision C4; delta on C3)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`, this session's environment metadata), main Claude Code session, 2026-10-30. AI drafting, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL, UNREVIEWED.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. R19-2 requires a two-family re-check before any owner decision. No human statistician has reviewed it.

**Owner direction (2026-10-30):** "Yea go": C4 fixing the C3 re-check findings. All six are text fixes. **No record type, lock, operation or role is added.**

**Answers** (both read in full):
- `SOL_OPTION_C3_REVIEW_415A0DE.md` (gpt-6-sol): FIX, D20C3-S-1..2;
- `ASTRA_OPTION_C3_REVIEW_415A0DE.md` (gpt-6-astra): FIX, D20C3-A-1..4.

**How to read it:** a **delta on `OPTION_C_PROPOSAL_REV3.md`**. Each item names the C3, C2 or rev 8 text it replaces. Everything else stands.

**VERDICT: `AMENDMENT_REQUIRED`.**

## 1a. Dispositions

| ID | Disposition | Repair |
|---|---|---|
| **D20C3-A-1** (BLOCKER; VOID could follow an effective certificate) | **Accepted.** `sign_permit` returns without writing when an ATTESTATION delivery or VOID entry already exists, before any cap or revision test. | item 1 |
| **D20C3-S-1 ~ D20C3-A-2** (BLOCKER; §7 row does not match the interface) | **Accepted.** The reader gets an explicit field projection, and the §7 row lists exactly that projection. Paragraph (b) is scoped to `request_release`'s response. Rejection reasons (Q2b), VOID reasons and invalidation entries are included. The commitment and record hashes are withheld from the reader. The cap warning is deleted. | items 2-4 |
| **D20C3-A-3** (BLOCKER; QC3 closing sentence) | **Accepted.** | item 5 |
| **D20C3-S-2 ~ D20C3-A-4** (NON-BLOCKING; leftover supersessions) | **Accepted.** T-S2's `release` call must be at or after `R_0` and refuse before it; C2 TC-6's closed-cycle assertion is replaced; C2's "`STOPPED` reveals that an incident occurred" is replaced; rev 8 T-S1's `state`/`guard_state` calls are replaced. | item 6 |

## 1. Replacements

**Item 1. `sign_permit` (replaces C3 §1.5b's first bullet; D20C3-A-1).** Under `L_store`, in this order:
1. If an ATTESTATION delivery entry or a VOID entry exists for the evaluation, **return the existing state and write nothing**. An effective certificate is final, and so is VOID (C2 §1.5 four facts; P-6 "an attested nominee is unaffected").
2. Otherwise, if the release is PASS and the RESULT delivery exists, but the clock is at or after C, or a revision or invalidation entry follows the pre-read entry, append the VOID entry and refuse.
3. Otherwise, apply C2's permit conditions.

The same "already final, write nothing" test is the first step of `record_delivery(ATTESTATION)`, since C2's "if a delivery entry of this kind exists, return it" does not cover an existing VOID. **TC-4 adds:** `sign_permit` and `record_delivery(ATTESTATION)` called after C, and again after a revision, on an evaluation whose certificate is already effective. Each writes nothing and the code stays `PASS_CERTIFIED`. The same calls on a VOID evaluation also write nothing.

**Item 2. Reader projection (replaces C3 §1.1's reader row; D20C3-S-1, A-2).** The reader sees only these fields, and only under these visibility rules:

| Record | Fields the reader sees | Visible |
|---|---|---|
| pre-read entry | evaluation ID, family, nominee ID, prediction-artifact hash, eligibility ID, lockbox ID, `R_0`, EXPOSED | always |
| rejection entry (`PRE_READ_REJECTION`, `BARRED_DESCENDANT`) | family, nominee ID, kind, reason code (D-12 Q2b, including `ANCESTOR_UNRELEASED`), ancestor evaluation ID | always |
| release entry | evaluation ID, result, `released_at` | after its RESULT delivery entry, or from its cycle's termination, whatever the cause (C3 §1.6) |
| delivery entry | evaluation ID, kind, `delivered_at` | always |
| VOID entry | evaluation ID, reason (CAP or REVISION) | always |
| revision or invalidation entry | kind, `at` | always |
| cycle report | per counted read: the result if visible under the release row, else `PENDING_RELEASE`; complete or incomplete | from the cycle's termination |
| pending list | the evaluation IDs it lists (C3 §1.6) | always |

**Withheld from the reader:** the commitment, record and file hashes, nonces, and every other field of any record.

**The RESULT delivery file becomes `{evaluation_id, result, released_at}`.** C2's `release_entry_hash` is dropped from the file. The publisher keeps the release entry hash for its own P-8 checks. The attestation's frozen fields (Constitution §13) are unchanged; the owner holds the attestation itself, as C2 §1.4 says.

**Item 3. The cap warning (deletes C2 §1.5's sentence "`request_release` warns when `now + 72 h` is past C"; D20C3-A-2).** Deleted. It was a message outside the six codes. The promotion guard alone enforces the cap. TC-7's warning case is deleted.

**Item 4. Proposed Constitution §7 row (replaces C3 §1.8's proposed text; D20C3-S-1, A-2).**

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except as follows. (a) The cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. (b) The lockbox service's release request answers only with one of these fixed responses: not yet; FAIL; PASS, certificate pending; PASS, certified; PASS, not certifiable; or stopped, a refusal whose cause is withheld. (c) Research may see these accounting records, with only the fields the protocol lists for each: a read's identity, exposure and earliest release time; a pre-read rejection or barred descendant with its reason code; a released result with its release time; delivery kinds and times; a certificate refused as not certifiable, with its reason (cap or revision); revision and invalidation entries; the pending list; and the cycle report, complete or incomplete. (d) How quickly the service answers any request, and a stopped answer; a delay of any length in a release, its delivery or its certification; an expiry at the processing cap caused by such a delay; and a technical fail caused by a delay before the worker deadline are not results under this rule, even where they allow a guess about a result or about another read's progress. This exception permits no other research-visible field, message, record or diagnostic. No component may vary its timing to convey a result." |

The protocol's field list for (c) is item 2's table. It goes into C2 with the S4 text. (c) covers the D-12 Q2b reason codes, which C2 must carry anyway.

**Item 5. QC3 closing (replaces the sentence "None of this can change a result" kept from C2 §4; D20C3-A-3).** It becomes:

> Once a result is released, these delays cannot change it. The Constitution says research receives PASS/FAIL only, so allowing these hints needs the written exception in §1.8, which you would sign in C2 after a person reviews it.

QC3's list also gains one line, from item 2:
> You and research also see the bookkeeping: which tests ran and when they may be released, the reason a test was refused before it started, when results were released and copied to you, and whether a certificate could not be issued and why (day 255 or a revision).

**Item 6. Leftover supersessions (append to C3 §1.10a; D20C3-S-2, A-4).**

| Inherited | Superseded by |
|---|---|
| C3 §1.10a's T-S2 replacement ("a concurrent `release` waits and then shows it") | "a concurrent `release` called before `R_0` is refused (`STOPPED`, logged) and shows nothing; one called at or after `R_0` waits for the finish's hold and then shows its result". T-S2's clock advance past `R_0 − 21,600` is replaced by an advance past `R_0`. |
| C2 TC-6, "an unknown or closed-cycle ID gives `STOPPED`" | "an ID with no pre-read entry gives `STOPPED`; a terminated-cycle ID is served" (C3 TC-5) |
| C2 §1.7, "`STOPPED` reveals that an incident occurred, for example a RESULT bundle that failed to verify, which implies a finished record existed" | "`STOPPED` reveals only that a request was refused; its cause (a §26 stop, a failed request, an unknown ID) is withheld. A refusal during an incident can still correlate with the incident's cause, for example a RESULT bundle that failed to verify, which implies a finished record existed; this is part of the timing and refusal residual in §1.8 (d)." |
| rev 8 T-S1, "each concurrent `state`, reader-row, `guard_state` and `begin_read` call returns only after the append and shows it" | "each concurrent reader-row, `release` (at or after `R_0`), `sign_permit` and `begin_read` call returns only after the append and shows it" |

Row 3's refusal correlation is covered by item 4's (d), which lists "a stopped answer" alongside timing effects.

## 2. Findings, remaining, unauthorised, self-check

**New findings** (continuing):
- **D20L-97 BLOCKER (repaired; item 1).** `sign_permit` could VOID an effective certificate (D20C3-A-1).
- **D20L-98 BLOCKER (repaired; items 2-4).** The §7 row and the reader interface differed (D20C3-S-1 ~ A-2).
- **D20L-99 BLOCKER (repaired; item 5).** QC3 kept "None of this can change a result" (D20C3-A-3).
- **D20L-100 NON-BLOCKING (applied; item 6).** Leftover supersessions (D20C3-S-2 ~ A-4).

**Remaining:** as C2 §5, with the R19-2 re-check now of C4.

**Unauthorised:** as C2. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-check:**
- one file written in this step;
- all 6 C3 findings answered;
- new findings D20L-97..100, no gaps;
- no new record type, lock, operation or role;
- removed: the cap warning, and `release_entry_hash` from the RESULT delivery file;
- added: the reader projection table; the "already final" first step of `sign_permit` and `record_delivery(ATTESTATION)`; "and a stopped answer" in §7 (d).
