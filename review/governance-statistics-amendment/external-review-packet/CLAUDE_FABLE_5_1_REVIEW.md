# Independent review record — `claude-fable-5-1`

**Status:** `REVIEW RECORD — AI REVIEW, NOT HUMAN OR STATISTICIAN ACCEPTANCE`
**Companion to:** `README.md`, `REVIEW_ADJUDICATION.md`

This file records an independent review of this packet. It is a record of what
the reviewer reported; it is not an amendment, not human acceptance, and not a
qualified statistician's opinion. Under Constitution §16 an AI review satisfies
neither the different-model nor the human PR-review requirement for protected
code, and this packet contains no code in any case.

## 1. Reviewer metadata

| Field | Value |
| --- | --- |
| Reviewer | Claude Fable |
| Exact model ID | `claude-fable-5-1` |
| Access | Read-only |
| Verdict | `REVISION_REQUIRED` |
| Object reviewed | `review/governance-statistics-amendment/external-review-packet/` as prepared at repository HEAD `fad5564044f6d368029bcf153fd879ec04f97fe4` |
| Relationship to author | Independent of the authoring model (`claude-opus-5`); different model family member, same vendor |

`REVISION_REQUIRED` is one of the four verdicts offered by
`REVIEWER_DECISION_FORM.md` §1, and it means the packet itself must be corrected
before a scientific opinion on the binding question is given. It is **not** a
verdict on the binding question, and in particular it is not `KEEP_BLOCKED`,
`AMENDMENT_REQUIRED`, or `BINDING_CANDIDATE`.

## 2. What the reviewer independently verified

The reviewer reported performing its own recalculation and re-derivation, and
reported the following as verified:

| Area verified | Reported result |
| --- | --- |
| All material mathematics in the packet | Verified |
| DSR and PBO semantics as described | Verified |
| Source-document SHA-256 hashes (`README.md` §5) | Verified |
| Packet manifest entries | Verified, 4/4 as the manifest then stood |
| Source-to-claim mappings | Verified |

These verifications were reported by the reviewer. They are recorded here as
reported; this file does not restate them as the author's own independent
result, and no calculation beyond the findings below is attributed to the
reviewer.

## 3. Findings as reported

### F-01 — HIGH — internally inconsistent consumer counts and labels

The reviewer reported that the packet does not present one consistent decision
object, citing five specific inconsistencies:

1. `README.md` and `REVIEWER_DECISION_FORM.md` referred to **nine** remaining
   consumers, while the binding matrix has **thirteen** rows of which two are
   settled and **eleven** remain.
2. The Queue II list labelled matrix rows 11–13 as *amendment-required*, while
   the matrix itself labelled those rows **Undefined**, and `README.md` §4.1 M4
   described the same rows as *information, then governance*.
3. The candidate document stated, near the route comparison, that **five** rows
   require the Constitution §4 process — a claim that depends on a harmonized
   classification that the packet had not made explicit.
4. Route D's falsifying-evidence cell referred to **twelve** clauses, while the
   matrix has **thirteen** rows.
5. The wording describing how many protocol clauses literally use the term
   "paired delta-Sharpe" was inconsistent across documents.

**Reviewer's required fix.** Define one auditable canonical thirteen-row decision
object — rows 1–2 settled, rows 3–13 remaining — partitioned into Queue I,
Queue II, and, if justified, a Queue III for the Undefined rows; then make every
count and every label in the packet consistent with it.

### F-02 — MEDIUM — the decision form cannot pin untracked packet bytes

The reviewer reported that `REVIEWER_DECISION_FORM.md` relied on commit fields
to identify what was reviewed, but the packet files are untracked, so a commit
SHA does not pin the reviewed bytes.

**Reviewer's required fix.** Add explicit verification fields to the decision
form for every manifest entry and for the SHA-256 of `MANIFEST.sha256` itself,
while retaining the existing commit fields.

### F-03 — LOW — incorrect decimal in `TECHNICAL_APPENDIX.md` Example C

The reviewer reported that the decimal given for `(4/93)*sqrt(1095)` in the
Example C table must be `1.4232595`. The exact radical expression `(4/93) *
sqrt(1095)` was reported as correct and unchanged; only the rounded decimal was
wrong.

### F-04 — LOW — `A(2)` derivation is stated without its key step

The reviewer reported that at `N = 2` the packet should state explicitly that the
**first term** of the cited two-term expression vanishes, rather than presenting
the reduced single-term form without explanation.

### F-05 — LOW — unsupported clause in the route-B sign-inversion claim

The reviewer reported that `STATISTICAL_BINDING_CANDIDATE.md` route R-B claimed
sign inversion for gates 3, 4 and 6, while the affected-clause list in
`TECHNICAL_APPENDIX.md` §3 omitted `validation.plateau.pass_rule` — gate 6.

**Reviewer's required fix.** Either support gate 6 explicitly, or remove it from
the claim.

### F-06 — informational — author model metadata

The reviewer noted that Claude Opus 5.1 was the preferred author model, while the
observed author model metadata is `claude-opus-5`, and asked that accurate
metadata be preserved rather than the preferred model be reported.

## 4. Unauthorized actions

**None.** The review was read-only. The reviewer reported no action beyond
reading and recalculation, requested no governance act, and did not author,
merge, activate, or self-approve anything. No frozen artifact, sidecar,
`FROZEN_HASHES.json` entry, source file, test, or pre-existing review record was
modified by the review, and no file outside this packet directory was modified in
responding to it. No simulation, network access, credential use,
confirmation-partition access, or lockbox access occurred.

The reviewer did not, and could not, supply any of the requirements M1–M8 in
`README.md` §4.1: an AI review is not a qualified human statistician's opinion
and is not a Constitution §4 governance act.

## 5. Scope of this record

This file records review facts only. The author's response to each finding —
AGREE, PARTIAL, or DISAGREE, with the exact correction applied and the evidence
for it — is in `REVIEW_ADJUDICATION.md`. Nothing in either file resolves the
binding question, Astra findings B1–B5, or DEC-01 to DEC-03, and nothing in
either file changes the owner's 2026-09-18 DSR `DEFER` decision or the standing
promotion block.
