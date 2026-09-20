# Reviewer decision form

**Packet:** `review/governance-statistics-amendment/external-review-packet/`
**Repository HEAD at preparation:** `fad5564044f6d368029bcf153fd879ec04f97fe4`
**All fields below are intentionally blank.**

Completing this form records a qualified external statistician's scientific
opinion. It does **not** author, merge, activate, or self-approve an amendment,
and it does not authorize Task 13, a calibration engine, any simulation,
confirmation or lockbox data access, a governed trial, promotion, deployment, or
trading. Activation additionally requires the Constitution §4 process and an
owner-of-record signed and dated commit, neither of which this form supplies.

Please answer every question. Where a question does not apply, write `N/A` and
say why; blank answers are treated as unanswered, not as agreement.

## 1. Primary decision

Select exactly one.

```text
[ ] ACCEPT   — the narrowest next decision in README.md §4 (register two
               estimands; confirm the two settled difference-series inputs,
               rows 1-2; partition the eleven remaining consumers, rows 3-13,
               into Queue I (rows 3-7), Queue II (rows 8-10) and Queue III
               (rows 11-13) as defined in STATISTICAL_BINDING_CANDIDATE.md
               section 5; change nothing else) is scientifically sound and may
               be put to the owner as written.

[ ] REVISE   — the decision is sound in structure but must be changed before it
               is put to the owner. Specify every required change in §3.

[ ] REJECT   — the decision should not be put to the owner. Specify in §3 whether
               the correct outcome is to retain the current pause unchanged, or
               something else.
```

Overall verdict on the binding question (select one):

```text
[ ] BINDING_CANDIDATE   — a defensible clause-specific binding exists now
[ ] AMENDMENT_REQUIRED  — binding requires the Constitution §4 process
[ ] KEEP_BLOCKED        — evidence is insufficient to bind; record and pause
[ ] REVISION_REQUIRED   — the packet itself must be corrected before an opinion
```

**Required rationale (mandatory, 150 words minimum).** State the scientific basis
for your selection, naming the specific clauses and evidence you relied on. A
selection without rationale is incomplete.

```text



```

## 2. Question-by-question responses

Answer each with `YES`, `NO`, or `CANNOT DETERMINE`, plus a one- to three-sentence
reason. A bare `YES`/`NO` is incomplete.

| # | Question | Answer | Reason |
| ---: | --- | --- | --- |
| Q1 | Are `E-IMPROV` and `E-DIFF` correctly defined in `STATISTICAL_BINDING_CANDIDATE.md` §3, including the observation unit, variance convention, and `sqrt(365)` annualization? | | |
| Q2 | Is Example A (`E-IMPROV` not identifiable from a difference series) correct, and does it correctly imply that `validation.pbo.series_matrix`, `validation.dsr.series`, and `lockbox_policy.prediction_interval` cannot produce `E-IMPROV`? | | |
| Q3 | Is Example A2 (`E-DIFF` not identifiable from the two leg Sharpes) correct? | | |
| Q4 | Is Example B (opposite signs on admissible data) correct, and does it make the estimand choice outcome-determining for `eth_gate`, `eth_sanity_rule`, `survive_2x_cost_rule`, `btc_min_sharpe_delta_ci_lower_bound`, and `paired_delta_sharpe_sign`? | | |
| Q5 | Is Example C (complete PBO rank reversal) correct? | | |
| Q6 | Is Example D (max difference-Sharpe trial is not the max-DSR trial under the proposed candidate) correct, and does it support DEC-02's conclusion that the two error events are not interchangeable? | | |
| Q7 | Is the consumer matrix (`STATISTICAL_BINDING_CANDIDATE.md` §5) complete — are any frozen protocol consumers of a Sharpe-like paired statistic missing? | | |
| Q8 | Is the Settled / Interpretive / Amendment-required / Undefined classification, and the corresponding `— / I / II / III` queue assignment, of each of the thirteen rows in `STATISTICAL_BINDING_CANDIDATE.md` §5 correct? In particular, is Queue III (rows 11–13, no pass statistic named) justified as distinct from Queue II (rows 8–10, statistic named but not computable from the frozen input)? Identify every row you would reclassify or requeue. | | |
| Q9 | Do you agree that **no single** estimand satisfies all the frozen clauses simultaneously (routes R-A and R-B are both refuted)? | | |
| Q10 | Is `KEEP_BLOCKED` the correct present verdict, or does the evidence already support at least one clause-specific binding? If the latter, name the clause and the estimand. | | |
| Q11 | Is the minimum-requirements list (`README.md` §4.1, M1–M8) complete and correctly attributed between statistician and governance? | | |
| Q12 | Does the packet correctly preserve the frozen DSR difference-series input, i.e. does it avoid proposing any substitution of `E-IMPROV` into `validation.dsr.series`? | | |
| Q13 | Does any wording in this packet overstate its authority — could it be mistaken for an amendment, for human or statistician acceptance, or for permission to simulate, access data, promote, or trade? | | |
| Q14 | Is any assertion in the packet scientifically wrong, unsupported, or misleading in a way that could change a future promotion outcome? | | |

Additional findings, with stable IDs and severity `BLOCKER`, `NON-BLOCKING`, or
`QUESTION`. Cite file and section, give evidence, state the impact, and state the
minimal resolution.

```text
ID | Severity | File / section | Evidence | Impact | Minimal resolution
---+----------+----------------+----------+--------+-------------------



```

## 3. Required changes (mandatory if REVISE or REJECT)

List each required change as a separate numbered item, naming the file, the
section, and the exact replacement wording or the specific analysis needed.

```text
1.
2.
3.
```

## 4. Conflict-of-interest and independence disclosure

All four items are mandatory.

```text
Financial or other interest in this project, its owner, or any strategy,
counterparty, or venue referenced (state "none" or describe in full):


Prior involvement in authoring, reviewing, or advising on any document in this
repository, including any AI-assisted contribution (state "none" or describe):


Any relationship to the owner of record or to other reviewers of this packet
(state "none" or describe):


Use of AI assistance in preparing this review (state "none", or name the models
and describe exactly what they contributed and what you verified yourself):

```

I confirm that I reviewed the source documents listed in `README.md` §5 and did
not rely on the packet's summaries alone, except where noted:

```text
[ ] Confirmed        [ ] Confirmed with exceptions (list them):

```

## 5. Deterministic checks recorded at packet preparation

Recorded by the preparing agent; the reviewer is invited to re-run them.

| Check | Command (from repository root) | Result |
| --- | --- | --- |
| Frozen protected bytes and inventory | `Get-ChildItem <docs\|protocols\|schemas\|specs> -File -Recurse \| Get-FileHash -Algorithm SHA256`, plus `FROZEN_HASHES.json` and its sidecar, compared entry by entry against the Task 1 baseline `review/task1/protected-before.json` | `PASS` — 28/28 hashes identical to the baseline; inventory exact (`docs/README.md` excluded as in the verifier); the 14 `.sha256` sidecars are among those 28 and are unchanged |
| Frozen manifest and protocol bindings | Compared `protocols/protocol_v1.yaml` lines 6–11 and the corresponding `FROZEN_HASHES.json` fields against the recomputed file hashes | `PASS` — 6/6 file-hash bindings match (`cost_model`, `feature_factory`, `benchmark_set`, `backtester_spec`, `threat_model`, `hash_canonicalization_spec`) |
| Constitution canonical self-hash | Not recomputed | See note below |
| Packet manifest generated | `Get-FileHash -Algorithm SHA256` over the seven packet Markdown files, after they were final | Written to `MANIFEST.sha256` |
| Manifest verification | Recompute each hash and compare to `MANIFEST.sha256` | `PASS` — 7/7 match |
| Packet link and path check | Every repository-relative path and every intra-packet file reference resolved against the working tree | `PASS` — all paths exist |
| Whitespace | `git diff --check` | `PASS` — no output |
| Working tree | `git status --short` | Only the untracked directory `review/governance-statistics-amendment/external-review-packet/` (eight files); no modification, rename, or deletion elsewhere |
| Protected-path diff | Frozen artifacts, sidecars, `FROZEN_HASHES.json`, source, tests, and existing review records | Empty — unchanged |
| Tests, Ruff, mypy, import-linter | — | N/A: review Markdown only; no executable code, configuration, or import boundary changed |

**Note on the frozen verifier.** `review/task6/verify_frozen.ps1` could not be
executed in the preparing session, which ran non-interactively without script-
execution permission. The byte-level checks above reproduce the verifier's first
two assertions directly from file hashes and are strictly stronger for those
assertions, because they compare against the recorded Task 1 baseline rather than
only against the manifest. The verifier's Constitution canonical self-hash step
(which strips the embedded hash field and re-hashes the remainder) was **not**
re-executed. It is not weakened: `docs/RESEARCH_CONSTITUTION.md` is byte-identical
to the Task 1 baseline, so its self-hash is necessarily unchanged. A reviewer or
the owner should nonetheless run the verifier directly to obtain its own `PASS`
lines.

Nothing was committed or pushed. No simulation, network access, credential use,
confirmation-partition access, or lockbox access occurred.

### 5.1 Packet byte verification (reviewer-completed, mandatory)

**Why this section exists.** The packet was never committed. At preparation, and
at the time this form was written, every file in
`review/governance-statistics-amendment/external-review-packet/` was **untracked**
(`git status --short` reports the directory, not individual tracked paths). A
commit SHA therefore does **not** pin the bytes you reviewed, and the commit
fields in §6 — which are retained and still mandatory — are not by themselves
sufficient evidence of what you read. Record the bytes here as well, so that a
later reader can establish exactly which version of the packet your opinion
attaches to.

**Instructions.** From this directory, run
`Get-FileHash -Algorithm SHA256 <file>` (PowerShell) or
`sha256sum <file>` (POSIX) for each row. Copy the **expected** value from
`MANIFEST.sha256`; enter the value **you** computed; mark `MATCH` or `MISMATCH`.
Do not transcribe expected values from any other document. A `MISMATCH` on any
row means the packet you read is not the packet that was prepared: stop, record
it here, and report it before completing the rest of this form.

```text
File                               | Expected (from MANIFEST.sha256) | Recomputed by reviewer | MATCH / MISMATCH
-----------------------------------+---------------------------------+------------------------+-----------------
README.md                          |                                 |                        |
STATISTICAL_BINDING_CANDIDATE.md   |                                 |                        |
TECHNICAL_APPENDIX.md              |                                 |                        |
REVIEWER_DECISION_FORM.md          |                                 |                        |
CLAUDE_FABLE_5_1_REVIEW.md         |                                 |                        |
CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md |                                 |                        |
REVIEW_ADJUDICATION.md             |                                 |                        |
```

Number of manifest entries verified (must equal the number of entry lines in
`MANIFEST.sha256`, and that file must list every Markdown file in this
directory and must not list itself):

```text
Entries in MANIFEST.sha256:            ____ of ____ Markdown files present
Entries verified MATCH:                ____
Manifest lists itself (must be "no"):  ____
```

**SHA-256 of `MANIFEST.sha256` itself — reviewer-filled, deliberately blank.**

```text
SHA-256(MANIFEST.sha256) as computed at review time:

________________________________________________________________

Computed on (UTC, ISO 8601):  ______________________
Command used:                 ______________________
```

This field is left blank by construction, and the blank is not an omission. The
manifest cannot hash itself, and this form is one of the files the manifest
covers: writing the manifest's digest into this form would change this form's
bytes, which would change this form's entry in the manifest, which would change
the manifest's own digest — a fixed-point cycle with no stable solution. The
field is therefore stable in *position* but reviewer-filled in *value*: compute
it yourself at review time with the command above and record the result here and
in your returned form. If a future revision of this packet needs a
self-consistent, author-supplied manifest digest, it must be published in a file
that the manifest does **not** cover, not in this one.

## 6. Reviewer identity, qualifications, signature, and date

```text
Full name:

Professional qualification and basis for statistical review
(degree, certification, relevant experience):

Institutional affiliation (or "independent"):

Contact:

Scope of this review (what you examined, and what you deliberately did not):

Signature:

Date (UTC, ISO 8601):

Repository commit reviewed (HEAD at the time you read the packet; note that the
packet files themselves may be untracked at that commit, in which case §5.1 is
the authoritative record of the bytes you read):

Packet bytes reviewed: §5.1 completed?  [ ] Yes   [ ] No (explain):
```

## 7. Acknowledgements the reviewer is asked to confirm

```text
[ ] I understand this review is advisory and is not an amendment.
[ ] I understand it does not activate governance, start a cycle, permit Task 13,
    a calibration engine, or any simulation.
[ ] I understand it grants no access to confirmation or lockbox data and no
    permission to promote, deploy, or trade.
[ ] I understand that DSR remains diagnostic-only, that the mandatory 0.95 gate
    remains unsatisfied, and that promotion remains blocked regardless of my
    answer.
[ ] I understand that Astra findings B1-B5 and DEC-01 to DEC-03 are not resolved
    by this review.
[ ] I understand that owner trust in an AI review, and ordinary owner acceptance
    of a pull request, do not constitute statistician qualification or
    Constitution §4 activation.
```

---

Return the completed form to the owner of record. Do not modify any file in this
repository; a completed form is recorded by the owner as new review evidence
alongside, not inside, this packet.
