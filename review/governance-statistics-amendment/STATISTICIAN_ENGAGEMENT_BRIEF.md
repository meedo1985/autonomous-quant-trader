# Engagement brief — external statistical review

**Status:** `BRIEF ONLY — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**For:** a qualified statistician being approached about this work
**Prepared:** 2026-09-21 by Claude (observed model ID `claude-opus-5`), AI author
**Deliberately outside both review packets**, so that adding it changes no
manifest, no recorded hash, and no packet's file inventory.

This is the orientation document. It is short on purpose: the review packet is
long, and a reviewer should be able to decide whether to take the engagement
without reading it first.

## 1. The engagement in one paragraph

A private quantitative research project operates under a frozen governance
document and a frozen cycle protocol. The protocol requires a "paired
delta-Sharpe" statistic in thirteen distinct clauses and **defines an estimator
for none of them**. Two mathematically distinct candidate estimands exist, they
disagree in sign on admissible data and reverse trial rankings, and the frozen
clauses are not all satisfiable by the same one. No trading, no trial, and no
research cycle has ever run; everything is halted pending this question. We are
asking one qualified person for one bounded scientific judgement.

## 2. The exact question

> Given the frozen protocol wording, can the eleven unresolved consumers be bound
> to estimators **by scientific reasoning alone** — without changing any frozen
> input, threshold, or clause meaning — and if so, to which estimator is each
> bound?
>
> If they cannot, state which are blocked, whether each is blocked by *missing
> information* (a definition you can supply) or by *incompatible frozen text*
> (requiring a governance amendment), and the minimum set of facts or decisions
> that would unblock each.

## 3. "Everything is blocked" is a complete and accepted answer

This matters more than anything else in this brief. The project's own
recommendation, carried into review, is `KEEP_BLOCKED`. A reviewer who concludes
that the evidence supports no binding has given a complete, useful, and final
answer, and **no follow-up work is expected or requested**. There is no
commercial pressure toward a permissive result, and nothing here is contingent on
a favourable one. If the honest answer is that the frozen text is internally
incompatible and must be amended before anything proceeds, that is the answer we
need, and saying so ends the engagement successfully.

## 4. What you are *not* being asked to do

- Not to design, endorse, validate, or calibrate a trading strategy.
- Not to author, approve, or activate a governance amendment. That process
  requires the owner's signature and is explicitly outside your role.
- Not to certify that any method is safe, profitable, or fit to deploy.
- Not to review code. The question is about estimand definitions and clause
  readings, and the relevant implementation is inactive.
- Not to access market data, exchange credentials, or any held-out partition.
  Nothing in the packet requires or grants data access.

## 5. Scope, so you can size it

Twenty numbered decisions are laid out in
`v1.1-method-candidate/HUMAN_DECISION_MATRIX.md`, each with its options,
evidence, the consequence of getting it wrong, a recommended candidate you are
free to reject, and a stated falsifier.

| Authority marked on the row | Count | Meaning |
| --- | ---: | --- |
| `STAT` | 9 | A statistician can close it alone |
| `STAT` then `§4` | 6 | Your judgement, then an owner governance step |
| `§4` or `§4 + STAT` | 3 | Blocked by frozen text; amendment required |
| `§16 + STAT` | 1 | Also requires code review before any implementation |
| `OWNER` then `STAT` | 1 | Already deferred by the owner; not open |

Nine rows are closable by you alone. Answering only those, and marking the rest
`defer`, is a legitimate and useful outcome. Each row takes a single response
code — accept, revise, reject, or defer — plus your rationale.

## 6. Expertise this actually needs

The binding question turns on **inference about Sharpe ratios under selection**.
The specific literature in play is the deflated Sharpe ratio, probability of
backtest overfitting, combinatorial purged cross-validation, and stationary
bootstrap block-length selection. Several open rows are precisely about multiple
testing over maxima, where a reviewer unfamiliar with that literature may not see
the trap: one recorded finding is that two candidate effective-trial-count
constructions are both unvalidated for selection over a maximum.

A generalist statistician without that background is likely to find the packet
hard to engage with. Econometrics or quantitative finance backgrounds fit well.

## 7. What you would receive

Everything is plain Markdown in a Git repository, self-contained, no tooling
required.

| Read in this order | What it is |
| --- | --- |
| `external-review-packet/README.md` | Cover: the question, scope boundary, source inventory with hashes |
| `external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` | Symbols, units, estimands, the canonical thirteen-row consumer table, invariants, four admissible routes |
| `external-review-packet/TECHNICAL_APPENDIX.md` | Five deterministic worked examples: non-identifiability, sign disagreement, rank reversal, selection-event non-equivalence |
| `v1.1-method-candidate/METHOD_CANDIDATE.md` | Proposed per-row bindings, DSR and PBO candidates, failure behaviour |
| `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` | The twenty decisions, one row each |
| `external-review-packet/REVIEWER_DECISION_FORM.md` | What you complete and sign |

The worked examples are exact rationals and can be checked by hand.

## 8. Prior review, stated honestly

The packets have been reviewed several times **by AI models only**, and those
reviews are included in full, including the findings they got wrong. They carry
no scientific or governance authority and are provided as working papers, not as
endorsements. They found and corrected defects in the write-up; they did not
resolve the binding question, and they recommend `KEEP_BLOCKED`.

One review record was lost before it was committed; four of its findings are
unrecoverable, identifiable only by a gap in the numbering. This is recorded
rather than hidden, in `v1.1-method-candidate/README.md` §6.5, and the process
rule that now prevents a recurrence is in `AGENTS.md`.

You are the first qualified human to look at any of it.

## 9. Verifying what you were sent

Both packets carry a `MANIFEST.sha256` over their Markdown files, and every
Markdown file in this directory tree is pinned to LF line endings, so the digests
reproduce on any platform:

```sh
cd <packet directory>
grep -v '^#' MANIFEST.sha256 | sha256sum -c -
```

Record the digest of the bytes you reviewed on the decision form. If any value
does not match, stop and report it — that is itself a finding.

## 10. Returning your decision

Complete `external-review-packet/REVIEWER_DECISION_FORM.md`. It asks for one
response code per decision row with your rationale, plus your name,
qualification, conflict disclosure, date, and the SHA-256 of the bytes you
reviewed. Return it however the owner has arranged; it is a plain text file.

Your rationale matters more than your verdict. A recorded reason is what a later
reader needs in order to check your reasoning rather than defer to it.

---

**For the owner, to complete before sending:** engagement terms, fee, timeline,
confidentiality, how the completed form comes back, and whether the reviewer may
be named in the repository record. None of those are decided here.
