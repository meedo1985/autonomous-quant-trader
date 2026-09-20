# Adjudication of the `claude-fable-5-1` reviews

**Status:** `AUTHOR RESPONSE — UNSIGNED — NOT AN AMENDMENT — NOT ACCEPTANCE`
**Responds to:** `CLAUDE_FABLE_5_1_REVIEW.md` (verdict `REVISION_REQUIRED`) and
`CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md` (verdict `PASS_WITH_ADVISORIES`)
**Author:** Claude, exact observed model ID `claude-opus-5`
**Scope of changes:** files inside
`review/governance-statistics-amendment/external-review-packet/` only

Every finding below is adjudicated `AGREE`, `PARTIAL`, or `DISAGREE`, with the
exact correction applied and the evidence for it. The corrections are editorial
and arithmetical. **No scientific conclusion of the packet changed**: the
recommendation remains `KEEP_BLOCKED`, routes R-A and R-B remain refuted, DSR
remains diagnostic-only, and promotion remains blocked.

## Summary

| Finding | Severity | Disposition | Correction applied |
| --- | --- | --- | --- |
| F-01 | HIGH | **AGREE** | Canonical thirteen-row decision object with an explicit Queue column and Queue III; all counts and labels harmonized |
| F-02 | MEDIUM | **PARTIAL** | Per-entry verification fields added, commit fields retained; the manifest self-hash is a reviewer-filled blank because an author-filled value has no fixed point |
| F-03 | LOW | **AGREE** | Decimal corrected to `1.4232595`; exact radical unchanged |
| F-04 | LOW | **AGREE** | Vanishing of the first term at `N = 2` stated explicitly |
| F-05 | LOW | **AGREE** | Gate 6 supported explicitly in the appendix (the "support it" branch, not the "remove it" branch) |
| F-06 | informational | **AGREE** | Observed model metadata recorded as observed, with the preference noted as a preference |
| F-07 | LOW | **AGREE** | Overstrong "outcome-determining for all of them" replaced with the precise scope: materially changes the test for all of them, and the outcome for the sign-tested clauses |
| A-01 | author-detected | n/a | Stray generation-artifact trailer lines removed from all five original files |

F-01 through F-06 were reported by the first review (verdict
`REVISION_REQUIRED`) and reported closed by the closure review. F-07 is the
single LOW advisory of the closure review (verdict `PASS_WITH_ADVISORIES`).

## F-01 — HIGH — inconsistent counts and labels

**Disposition: AGREE.** The inconsistency was real, and all five sub-items were
confirmed against the packet as it stood.

**Correction applied.**

1. `STATISTICAL_BINDING_CANDIDATE.md` §5 is retitled *"Canonical decision object
   — the thirteen consumer rows"* and declared normative: every count, queue
   name and status label elsewhere in the packet resolves to a row number there,
   and that table governs any apparent conflict.
2. A **Queue** column was added to the matrix. Rows 1–2 carry `—` (settled, not
   queued). Rows 3–7 carry `I`, rows 8–10 carry `II`, rows 11–13 carry `III`.
3. **Queue III is justified and retained as distinct from Queue II**, which
   resolves sub-item 2 without changing any row's underlying status. The
   distinction is substantive, not cosmetic: Queue II rows (8–10) *do* name a
   statistic that the frozen stored input cannot produce, so a binding is a
   Constitution §4 text change; Queue III rows (11–13) name **no** pass statistic
   at all, so there is nothing to bind and an estimand choice would not make them
   evaluable. Merging them, as the old Queue II list did, would have asserted
   that rows 11–13 already name a statistic. Queue III is therefore *information
   first, then governance*, which is exactly what `README.md` §4.1 M4 already
   said — so the matrix, the queue list and M4 now agree instead of conflicting.
4. Counts harmonized throughout to `2 settled + 5 Queue I + 3 Queue II +
   3 Queue III = 13`, eleven remaining. The audit line appears in both
   `STATISTICAL_BINDING_CANDIDATE.md` §5 and `README.md` §4 step 3.
   - `README.md` §4 step 3: "nine remaining consumers … two disjoint queues" →
     "eleven remaining consumers — rows 3–13 — into three disjoint queues".
   - `REVIEWER_DECISION_FORM.md` §1 `ACCEPT` text: same correction, with row
     ranges.
   - `README.md` §4.1 M4 now names Queue III and rows 11–13 explicitly.
5. `STATISTICAL_BINDING_CANDIDATE.md` §7 closing paragraph: "five of its thirteen
   rows require the Constitution §4 process" → an explicit harmonized statement:
   two rows settled, five (Queue I) within a statistician's reach, and **six**
   outside it — rows 8–10 requiring §4, rows 11–13 requiring information first
   and then §4. The earlier "five" conflated the two kinds of unreachability.
6. Route D falsifying evidence: "all twelve clauses" → "all thirteen rows of §5".
   The R-C cells for *works under frozen wording* and *governance impact* now
   name all three queues with their row ranges.
7. **Protocol literal-count wording.** This is the one sub-item where the fix is
   more than renumbering, because the previous wording — "names a quantity it
   calls paired delta-Sharpe in eleven distinct clauses" — is not literally true
   of the frozen file, and repeating a cleaner but still false count would have
   traded one inconsistency for another. The packet now states the auditable
   fact: eleven of the thirteen rows (3–13) request the paired delta-Sharpe
   quantity; **eight** of those rows contain the literal token
   `paired_delta_sharpe` or "delta-Sharpe" in `protocols/protocol_v1.yaml`
   (rows 3, 4, 6, 8, 9, 10, 11, 12), and **three** refer to the same quantity
   without that exact token (row 5 `btc_min_sharpe_delta_ci_lower_bound` at line
   275; row 7 `paired_fold_win_rate` at 280–282; row 13, the two delay hard
   gates at 284–285, which name no statistic at all).

**Evidence.** Literal occurrences of the token in
`protocols/protocol_v1.yaml` at lines 43, 78, 85, 91, 137, 140, 221, 240, 264,
279 and 283, which map onto rows 3, 4, 6, 8, 9, 10, 11 and 12 of the matrix.
Lines 274–275, 280–282 and 284–285 contain no such token, which is why rows 5, 7
and 13 are described as indirect references. Rows 1–2 correspond to
`validation.dsr.series` (227–231) and
`validation.oos_is_ratio.in_sample_definition` (245–248), both of which name the
paired difference series explicitly; hence `2 + 11 = 13`.

## F-02 — MEDIUM — untracked packet bytes

**Disposition: PARTIAL.** The premise and the required per-entry fields are
accepted in full. One element of the requested fix — an author-supplied SHA-256
of `MANIFEST.sha256` — cannot be satisfied as stated, and is delivered instead
as a stable reviewer-filled field with instructions.

**Premise confirmed.** `git status --short` reports the packet directory as
untracked (`?? ./` from inside it; `?? review/governance-statistics-amendment/
external-review-packet/` from the repository root). No packet file is tracked at
HEAD `fad5564044f6d368029bcf153fd879ec04f97fe4`, so a commit SHA genuinely does
not pin the reviewed bytes.

**Correction applied.** A new `REVIEWER_DECISION_FORM.md` §5.1, *Packet byte
verification (reviewer-completed, mandatory)*, containing:

- a per-file table with one row for **every** manifest entry — `README.md`,
  `STATISTICAL_BINDING_CANDIDATE.md`, `TECHNICAL_APPENDIX.md`,
  `REVIEWER_DECISION_FORM.md`, `CLAUDE_FABLE_5_1_REVIEW.md`,
  `CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md`, `REVIEW_ADJUDICATION.md` — with columns
  for the expected value copied from
  `MANIFEST.sha256`, the reviewer's recomputed value, and `MATCH`/`MISMATCH`,
  plus the exact PowerShell and POSIX commands;
- a completeness check requiring the reviewer to confirm that the manifest lists
  every Markdown file in the directory and does not list itself;
- an explicit `MISMATCH` stop rule;
- a stable, positioned field for `SHA-256(MANIFEST.sha256)`, with date and
  command sub-fields.

The commit fields are **retained**: `REVIEWER_DECISION_FORM.md` §6 still asks for
the repository commit reviewed, now qualified to say that §5.1 is authoritative
for the bytes when the packet is untracked at that commit.

**Why the manifest self-hash is left blank — the cycle.** Filling it in as an
author would be self-defeating, not merely awkward. `REVIEWER_DECISION_FORM.md`
is itself a file that `MANIFEST.sha256` covers. Writing the manifest's digest
into the form changes the form's bytes; that changes the form's entry in the
manifest; that changes the manifest's bytes; that changes the manifest's digest —
which is the value just written. There is no fixed point reachable by editing,
and any value published would be stale the instant it was written. The field is
therefore stable in position and reviewer-filled in value, with that reasoning
stated in the form itself so the blank cannot be read as an oversight. The form
also records the only clean alternative, should a future revision want an
author-supplied digest: publish it in a file the manifest does **not** cover.

## F-03 — LOW — Example C decimal

**Disposition: AGREE.**

**Correction applied.** `TECHNICAL_APPENDIX.md` §4, Example C, Trial 2
`E-IMPROV` cell: `(4/93)*sqrt(1095) ≈ +1.4233671` → `≈ +1.4232595`. The exact
radical `(4/93)*sqrt(1095)` is unchanged, as the reviewer stated.

**Evidence.** `sqrt(1095) = 33.0907842682…`; `4/93 = 0.04301075268…`; the product
is `1.42325954…`, which rounds to `1.4232595` at seven decimal places. The
previous value was wrong in the fifth decimal place. Nothing depends on it: the
rank reversal in Example C follows from the *signs and order* of
`+143.39 > +1.42` against `-0.55 < +49.64`, which the correction does not
disturb.

## F-04 — LOW — `A(2)` and the vanishing first term

**Disposition: AGREE.**

**Correction applied.** `TECHNICAL_APPENDIX.md` §5 now cites the two-term
expression in full, `(1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e))`,
and states explicitly that **the first term vanishes at `N = 2`** because
`Phi^-1(1 - 1/2) = Phi^-1(0.5) = 0`, leaving the single-term form the packet
previously presented without explanation.

**Evidence.** The reduced value is unchanged and was already correct:
`1/(2e) = 0.1839397…`, `Phi^-1(0.8160603…) ≈ 0.9004`, and
`gamma * 0.9004 = 0.5772157 * 0.9004 ≈ 0.5198 < 1`, as stated. Only the missing
step was added; no number moved. The appendix's own caveat that the conclusion is
insensitive to any reasonable error in `A(2)` also stands.

## F-05 — LOW — gate 6 in the route-B claim

**Disposition: AGREE.** Of the two branches the reviewer offered — support gate 6
explicitly, or remove it — the packet takes the **support** branch, because
`STATISTICAL_BINDING_CANDIDATE.md` §5 row 6 already argued that the estimand
materially changes `validation.plateau.pass_rule`; the defect was that the
appendix never carried that argument, so the route-B cell asserted it without
backing.

**Correction applied.**

- `TECHNICAL_APPENDIX.md` §3 affected-clause list now includes
  `validation.plateau.pass_rule` (263–265), followed by a short paragraph giving
  the reason.
- `STATISTICAL_BINDING_CANDIDATE.md` §7 route R-B now cites
  `TECHNICAL_APPENDIX.md` §3 for the claim instead of asserting it.

**Evidence.** The rule is `median available-neighbour value >= 0.5 *
selected-point value`, which is not sign-invariant. On the Example B returns the
selected point's value is `+143.39` under `E-IMPROV` and `-0.55` under `E-DIFF`.
For a positive selected value the rule requires neighbours to retain at least
half of a positive quantity; for a negative one, `0.5 * v > v`, so the rule
instead requires neighbours to be *better* than the selected point by at least
half its magnitude. Both the threshold's sign and the direction of the
requirement change with the estimand, which is the same outcome-determining
mechanism already established for gates 3 and 4.

## F-06 — informational — author model metadata

**Disposition: AGREE.** The observation is correct and the packet now states it
rather than resolving it silently in either direction.

**Correction applied.** `README.md` header: **Prepared by:** Claude, exact
observed model ID `claude-opus-5`, with a parenthetical recording that Claude
Opus 5.1 was the *preferred* author model and that `claude-opus-5` is what was
*observed* in the preparing and revising sessions. A line naming the independent
reviewer and its verdict was added alongside.

**Evidence.** The observed model metadata for the session that prepared the
packet and for the session that applied these corrections is `claude-opus-5`. No
claim is made that any model was changed, and the preferred model is not reported
as though it had been used.

## F-07 — LOW — overstrong scope claim in the affected-clause list

**Disposition: AGREE.** The claim as written was stronger than the evidence in
the appendix supports, and the distinction the reviewer drew is the correct one.

**Correction applied.** `TECHNICAL_APPENDIX.md` §3, closing sentence of the
affected-clause list: "The binding choice is outcome-determining for all of
them." → "The binding choice materially changes the test for all of them, and the
outcome for the sign-tested clauses.", followed by an explicit sentence recording
that for `validation.plateau.pass_rule` the demonstrated effect is a material
change of test and of the direction of the requirement imposed, with no outcome
reversal demonstrated, because the example supplies no neighbour values against
which the rule could be evaluated.

**Evidence.** For the sign-tested clauses the gate is of the form
`paired_delta_sharpe_point_estimate > 0`, and the Example B returns give
`E-IMPROV ≈ +143.3933985` against `E-DIFF ≈ -0.5512070`, so the gate passes under
one binding and fails under the other — a concrete outcome reversal. The plateau
rule is `median available-neighbour value >= 0.5 * selected-point value`;
Example B fixes only the selected point's value (`+143.39` versus `-0.55`) and
supplies no neighbour grid, so the appendix establishes that the threshold's sign
and the direction of the requirement both change, and does not establish a pass
or fail on either side.

**Nothing else changed.** No equation, exact value, decimal, affected-clause
membership, route refutation, or conclusion of the packet is affected;
`validation.plateau.pass_rule` remains in the affected-clause list on the same
evidence, and the route R-B claim it supports is unchanged.

## A-01 — author-detected, not a review finding

Not reported by `claude-fable-5-1`, and recorded separately so that it is not
attributed to the reviewer. All five original packet files ended with stray
generation-artifact lines — `</content>`, and additionally `</invoke>` in
`README.md` — which were not intended content. They were removed. This changes
the bytes of every original file, which is one of the reasons `MANIFEST.sha256`
is regenerated wholesale rather than amended.

## Consequential change to the manifest

Adding `CLAUDE_FABLE_5_1_REVIEW.md` and `REVIEW_ADJUDICATION.md` took the packet
from four Markdown files to six, and adding
`CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md` takes it to **seven**. `MANIFEST.sha256` was
regenerated after all seven were final, covers all seven, and does not cover
itself. The "four Markdown files" and "4/4 match" wording in `README.md` §1 and
`REVIEWER_DECISION_FORM.md` §5 was updated to six and 6/6 at the first revision,
and to seven and 7/7 at this one; the directory file count rose from seven to
eight. The 6/6 figure recorded in `CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md` §3 is left
as reported, because it is what the reviewer verified at review time, before this
file existed.

## What did not change

- The recommendation: `KEEP_BLOCKED` for any single universal binding.
- The status of every one of the thirteen rows. Queue III is a new *name* for the
  three rows the matrix already labelled **Undefined**; no row was reclassified,
  promoted, or demoted.
- Every estimand definition, every worked example's exact arithmetic, and every
  qualitative conclusion: non-identifiability in both directions, sign
  disagreement, rank reversal, selection-event non-equivalence.
- All frozen thresholds, the DSR `DEFER` decision of 2026-09-18, the standing
  promotion block, and the open status of Astra B1–B5 and DEC-01 to DEC-03.
- Every file outside this directory. Nothing was committed or pushed.
