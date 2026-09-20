# Independent adversarial review — `v1.1-method-candidate/` and `V1_1_CANDIDATE_REVIEW.md`

**Reviewer:** Claude, exact observed model ID `claude-fable-5-1` (the session's
own runtime metadata; recorded as observed, not as preferred). AI reviewer;
read-only analysis plus in-place correction of three demonstrated defects.
**Date:** 2026-09-20
**Repository HEAD at review:** `a7f6a5cfdc1d2a3f77b6757201889fe4b49f06f2`
**Environment:** Windows 11 Pro 10.0.26200; Windows PowerShell 5.1.26100.9444
(Desktop, .NET Framework 4.0.30319.42000); `pwsh` absent; Python 3.14.7
(no `sympy` — exact arithmetic used `fractions.Fraction`); Git Bash.
**Skills applied:** `.agents/skills/statistical-binding-review/SKILL.md`,
`.agents/skills/scientific-reproducibility-review/SKILL.md`,
`.agents/skills/task-gate-review/SKILL.md`, under root `AGENTS.md`.
**Bytes reviewed (before my corrections):** `MANIFEST.sha256` verified 4/4 —
`README.md` `5118544a…`, `METHOD_CANDIDATE.md` `b9e36d4a…`,
`HUMAN_DECISION_MATRIX.md` `ea6db518…`, `PREREGISTRATION_TEMPLATE.md`
`85e08f4e…`; `V1_1_CANDIDATE_REVIEW.md` `ab424eb1…` (sha256 prefix of its
14,624 bytes).

## 0. Verdicts

| Question | Verdict |
| --- | --- |
| Statistical binding question (rows 1–13) | `KEEP_BLOCKED` — unchanged. No row is closed, no recommendation is altered. |
| The packet as an artifact to put before a human statistician | `REVISION_REQUIRED` → three corrections `A-1`–`A-3` applied (§5); the packet is now internally consistent. Three substantive questions (§6, `F-Q1`–`F-Q3`) are left for the statistician and were deliberately not written into the candidate. |
| `V1_1_CANDIDATE_REVIEW.md` (the Opus review) | Its executable and arithmetic claims all reproduce. Its bookkeeping verdicts were incomplete in three places (§4). Recorded as disagreements; its text was not altered. |

This review is not human, owner, or statistician acceptance; it does not satisfy
Constitution §4 or §16; it authorizes no code, simulation, data access, trial,
promotion, or trading. No simulation was run, no confirmation or lockbox data was
touched, no network or exchange call was made, no credential exists or was used,
and no git state was changed.

## 1. Authority and status (unchanged from the Opus review §1)

Frozen: `protocols/protocol_v1.yaml`, `docs/RESEARCH_CONSTITUTION.md` v1.0 `C1`,
byte-unchanged (§3). Owner decisions: 2026-09-15 (C1 never started; DSR
diagnostic-only; ETH 1x) and 2026-09-18 (**DEFER**). Accepted inactive
implementation fact: `src/aqt/metrics/statistics.py`. Unaccepted AI proposals:
everything else, including both reviewed directories and both AI reviews.

## 2. Symbols (as reviewed; separation preserved)

`E-IMPROV = A*S(c) - A*S(b)`; `E-DIFF = A*S(c - b)`; `S(x) = mean/sd`, `sd`
denominator `n-1`; `A = sqrt(365)`; DSR consumes the **unannualized** `S(d)` of a
difference column. No silent substitution of one for another was found in any of
the four files; §6 `F-N1` notes one *labelling* looseness at row 1.

## 3. Executable checks — exact results

All commands run from the repository root unless stated.

| Check | Command | Result |
| --- | --- | --- |
| Working tree | `git status --untracked-files=all --short`; `git diff --stat`; `git diff --cached --stat`; `git diff --check` | Only untracked files (this directory, both review files); no tracked change; `--check` silent |
| Byte state of packet and frozen files | Python: count `\r\n`, bare `\r`, `\n`, BOM | Every packet file, both review files, Constitution, protocol, canonicalization spec, `FROZEN_HASHES.json`: `CRLF=0`, `BOM=False`, UTF-8 decodes. (A Git Bash `grep -c $'\r'` artefact initially suggested CRLF; Python byte counts are authoritative.) `review/task1/protected-before.json` is CRLF in the working tree (`i/lf w/crlf`), harmless to its JSON parse. Root `.gitattributes` pins `-text` on every frozen path and on `*.sha256` |
| Frozen verifier, original | `powershell.exe -NoProfile -File .\review\task6\verify_frozen.ps1` | **exit 1** at line 57: `[System.Convert] does not contain a method named 'ToHexString'`; `[Convert].GetMethods()` count for `ToHexString` = 0 on this runtime. `N-3` confirmed |
| Frozen verifier, reimplemented from the spec | Python (`hashlib`, `re`, `json`) | baseline entries 28 `PASS`; protected inventory exact match `PASS`; baseline byte hashes 28/28 `PASS`; sidecar count 14 `PASS`; sidecar targets 14/14 `PASS`; `FROZEN_HASHES.json` `release=v1.0`, `status=FROZEN` `PASS`; `constitution_content_hash` binding `PASS`; embedded spec bindings 7/7 `PASS`; protocol top-level bindings 7/7 `PASS`; nested cost/feature/benchmark bindings `PASS`; `HASH_CANONICALIZATION_v1.md` sidecar value `189e3525…` equals the value embedded in the Constitution header `PASS` |
| Constitution canonical self-hash, rule discrimination | Python | Rule 5 (replace **only the 64-hex value** with the empty string, backticks retained), rule 1 (LF; a no-op on these bytes), rule 6 (UTF-8 **without BOM**) → `4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7` — **reproduced exactly**. Deliberately wrong treatments do **not** reproduce it: whole field removed → `6d6da2b2…`; UTF-8 with BOM → `a441ccc9…`; CRLF → `b2b9b158…`. So the reproduction is discriminating, not accidental |
| Source inventory | Python: parse `README.md` §5, recompute 21 hashes | 21 rows, 0 mismatches |
| Packet manifest before edits | `sha256sum -c` over the four non-comment lines | 4/4 OK |
| Packet manifest after edits | same | 4/4 OK (values in §5) |
| Exact arithmetic | Python `fractions.Fraction` (+ `math.erf` bisection for `Phi^-1`) | see §3.1 |
| Cross-reference sweep | `grep -o` over `D-nn`, `I-n`, `F-n`, `L-1`, `B1–B5`, `DEC-nn`, `M1–M8`, `R-n`, `N-n`, `Q1–Q5` per file | `D-01`–`D-20` all present in `METHOD_CANDIDATE.md`, `HUMAN_DECISION_MATRIX.md`, `PREREGISTRATION_TEMPLATE.md`; `M5`, `M6` resolve to `external-review-packet/README.md` §4.1 (`M1`–`M8` exist); `B1`–`B5` resolve to `ASTRA_REVIEW.md`; `DEC-01`–`DEC-03` resolve to `DSR_CALIBRATION_RECONCILIATION.md`; one wrong referent found (`A-1`, §5) |
| Tests, Ruff, mypy, import-linter | — | `N/A`: Markdown only, no code, configuration, dependency, or import boundary changed |

### 3.1 Exact arithmetic — every published value reproduced

| Claim | Exact recomputation | Result |
| --- | --- | --- |
| `S(b)^2 = 1/12`, `S(c_1)^2 = 243/4`, `S(c_2)^2 = 507/3844`, `S(d_1)^2 = 3/3604` (sign −), `S(d_2)^2 = 27/4` | rationals, `n-1` variance | all `True` |
| `(S(c_1)-S(b))/sqrt3 = 13/3`; `(S(c_2)-S(b))/sqrt3 = 4/93` | `9/2 - 1/6`, `13/62 - 1/6` | `True`, `True` |
| `E-IMPROV_1/2`, `E-DIFF_1/2` | `143.39339826737722`, `1.4232595361526281`, `-0.5512069292029372`, `49.63617632332289` | identical to published radicals to double precision |
| Ranking reversal; Lemma `L-1` | `E-IMPROV` 1>2, `E-DIFF` 2>1, own-Sharpe 1>2 | confirmed; `L-1` is exact in general (translation by `A*S(b)`) |
| Example A / A2 | `S(c)^2 = 3`, `3/5`, `S(d)^2 = 3`, ratio² `5`; A2 `S(d)^2 = 1/3` | all `True` |
| `C(16,8)` | `12870 = 2*6435` | `True` |
| `N = 2` PBO branches | ranks `1`, `2`, `3/2` → `omega` `1/3`, `2/3`, `1/2`; logit `∓0.6931471805599453`, `0`; scores `1`, `0`, `1/2` | confirmed. **Addition:** the `0.5` branch is also reachable **without ties** for odd `N` (e.g. `N = 21`, rank `11`, `omega = 1/2`), so it is live above the activation threshold whenever `N` is odd, not only under exact ties |
| Plateau inversion | `v ∈ {-2, -0.5}`: `0.5v > v` `True`; `v ∈ {0.5, 2}`: `False` | confirmed |
| Example D (DSR) | `S_X^2 = 3/20`, `S_Y^2 = 3*(89/400)^2`, `k_X = 41/25`, `D_X = 128/125 = 1.024`, `k_Y = 1`, `D_Y = 1` exact; `A(2) = 0.5197553442805937` (`Phi^-1(1-1/(2e)) = 0.9004525966…`); `V = 1.8375e-6`, `S0 = 7.0455e-4`; `score_X = 0.74592`, `score_Y = 0.74738` | all match; Y scores higher though X selected |
| DSR draft R2 | `(T-1)S^2/D = 225/512`; `Phi(15/(16 sqrt 2)) = 0.746306736608969` | `True`, matches |

### 3.2 DSR equation transcription

`METHOD_CANDIDATE.md` §3.1 matches `DSR_METHOD_PREREGISTRATION_DRAFT.md`
lines 27–33 term for term (`A(N)`, `S0`, `D`, `Phi(...)sqrt(T-1)/sqrt(D)`,
`gamma` Euler–Mascheroni, moment conventions). Against the literature baseline
(Bailey & López de Prado 2014, expected-maximum approximation and PSR-form
deflation), the form recalled by this reviewer agrees; the specific equation
numbering and page citation could not be fetched (network prohibited) and is
recorded as `UNVERIFIED_EXTERNAL_ASSUMPTION`, exactly as the skill requires.

### 3.3 Frozen citation audit — exhaustive, all resolve

Every `protocol_v1.yaml` and `RESEARCH_CONSTITUTION.md` line reference in the
four files was re-read at HEAD: `42–44`, `77–78`, `83–86`, `83–91`, `87–89`,
`90–91`, `93–95` (appendix), `134–140`, `137`, `139`, `150`, `177–190`,
`178–180`, `190`, `201`, `202–204`, `215–222`, `216`, `220–221`, `223–226`,
`227–231`, `232`, `233`, `234–241`, `235`, `236`, `237–239`, `237–240`, `239`,
`240`, `242–244`, `245–248`, `263–265`, `267–268`, `274–275`, `279`, `279–283`,
`280–282`, `283`, `284–285`, `289`, `290`; Constitution `47–56`, `58–67`, `67`,
§16. All resolve to the asserted clause. Non-frozen citations also resolve:
`statistics.py` `208–233` (decorator at 208, class at 209, `return` at 233);
`IMPLEMENTATION_CONVENTIONS.md` `9–23`; `TECHNICAL_APPENDIX.md` `49–178`;
`STATISTICAL_BINDING_CANDIDATE.md` `96–148`, `150–173`; `DRAFT_AMENDMENT_PROPOSAL.md`
`101`, `101–104`, `123–133`, `129`, `139–144`; `DSR_CALIBRATION_RECONCILIATION.md`
`37–48` and `97–116` (header is at 96 — off by one, trivial, not edited);
`ASTRA_REVIEW.md` `26–29`; `SKILL.md` `92–108`. `N-2` (line 201 omitted) stands.
**What the audit missed** is not a wrong line but an absent one: Constitution
§9 line 106 (see `A-3`).

## 4. Verification of each Opus claim

| Opus claim | Verdict | Evidence |
| --- | --- | --- |
| `R-1` `D-03` → `D-20` fix correct and complete | **PARTIALLY CONFIRMED** | The `D-03` fix is correct. But Opus cited as evidence the matrix's dependency note "`D-20` is triggered by … `D-03`, `D-08`, or `D-11`", which itself contains a wrong referent: `D-08` (PBO) is not bootstrap-backed, so it cannot trigger the bootstrap-migration decision `D-20`. Opus's "Decision/invariant IDs `PASS` … bidirectionally complete" therefore passed a note with the same class of defect as `R-1`. Fixed as `A-1` |
| `R-2` `I-1`–`I-9` mapping | **CONFIRMED** | `STATISTICAL_BINDING_CANDIDATE.md` §6 items 1–9 checked one by one against the uses: `I-7` = item 7 (fail-closed, `INDETERMINATE`/`BLOCKED`); `I-9` = item 9 (interval/point/percentile/prediction-quantile distinct); no `I-n` token exists in the external packet; the declaration now in §7 is accurate |
| `N-1` exclusivity overstated | **CONFIRMED** | `statistics.py:218–233` returns `difference_series_sharpe` (`E-DIFF`) in the same dataclass |
| `N-2` line 201 omitted | **CONFIRMED** | `reporting_fold_months: 3` is line 201; rows cite `202–204` |
| `N-3` verifier cannot run on PS 5.1 | **CONFIRMED** | ran it: exit 1 at line 57; `pwsh` absent; no `#Requires` |
| `N-4` no `.gitattributes` | **CONFIRMED, with a qualification** | True for `*.md`. Root `.gitattributes` already pins `*.sha256 -text`, so the manifest file itself is safe; only the four `.md` entries are exposed. Not applied (the packet §6.2 defers this to the owner, and applying it would require changing five self-descriptions for a packaging choice the packet expressly reserves) |
| `N-5` "bias phi" overstated | **CONFIRMED** | Dropping one orientation halves the split sample; a systematic effect requires a non-random orientation rule. Wording only; no edit |
| `Q-1` `partitions: 16` unowned | **CONFIRMED** as a question | No `D-nn` row owns the reading |
| Reimplemented verifier PASS incl. self-hash `4cb6c7d3…` | **CONFIRMED** | §3; rule-5 value-only treatment reproduces, alternatives do not |
| All exact-arithmetic values reproduce | **CONFIRMED** | §3.1, all from exact rationals |
| Every frozen citation resolves | **CONFIRMED for resolution; INCOMPLETE as an audit** | §3.3: all cited lines resolve; the audit did not detect the *omitted* frozen clause at Constitution §9 line 106 that contradicts `F-1`'s wording (`A-3`) |
| "Bytes reviewed" first-revision hashes `32b49c45…`, `53fea11c…`, `e02d70fb…` | **NOT CHECKED** | The first revision is untracked and not preserved anywhere; unverifiable. `85e08f4e…` for the template is verified (still byte-identical) |
| `LOCAL GATE: PASS` | **DISAGREE at the time it was declared** | README §6 "Working tree" row was already stale when Opus wrote its §4 (which itself described the tree correctly). Now `PASS` after `A-2` |

## 5. Corrections applied (`A-1`–`A-3`) and final manifest

| ID | File / location | Defect and evidence | Exact change |
| --- | --- | --- | --- |
| `A-1` | `HUMAN_DECISION_MATRIX.md` §7 line 80 | Note listed `D-08` as a `D-20` trigger. `D-20`'s own scope: "once any bootstrap-backed clause is bound". PBO (`protocol_v1.yaml:234–241`, `METHOD_CANDIDATE.md` §4) enumerates `C(16,8)` splits and uses no bootstrap; only rows 5 (`D-03`, 2,000-attempt CI) and 9 (`D-11`, prediction bootstrap) do | "… among `D-03` or `D-11`, the only two bootstrap-backed rows; `D-08` (PBO, `protocol_v1.yaml:234–241`) uses no bootstrap and does not trigger it." |
| `A-2` | `README.md` header, §1, §6 rows "Decision-ID referent", "Frozen citation audit", "Working tree"; new §6.4 | §6 said the working tree held only the five-file directory while §1 said six files were added; `git status --untracked-files=all` showed six. Self-descriptions must stay true, and they must now also account for this review | Review-count and file-count statements updated to two reviews / seven files; working-tree row corrected; check-table rows extended; §6.4 added recording `A-1`–`A-3` |
| `A-3` | `METHOD_CANDIDATE.md` §3.3 table row and `F-1`, §8 traceability; `HUMAN_DECISION_MATRIX.md` `D-16` evidence; `README.md` §4 `Q4` | `F-1` asserted "The fallback trigger condition is undefined in frozen text." `docs/RESEARCH_CONSTITUTION.md` §9 line 106: "If no frozen effective-count method exists, raw count is used." That is frozen trigger text, uncited by the packet, the external packet, or the Opus review. Its applicability turns on whether the method *named but undefined* at protocol line 232 "exists", which is undecided — so `D-16` remains `BLOCKING` and no candidate value was added | Sentences replaced to cite line 106 and state that its applicability is part of `D-16`; traceability row and `D-16` evidence extended; `Q4` wording aligned |
| `MANIFEST.sha256` | comment line 14 and the four digests | regenerated over LF bytes after `A-1`–`A-3`; verified 4/4 | see below |

No recommendation, estimand, threshold, decision status, frozen input, or
governance status was changed. `PREREGISTRATION_TEMPLATE.md` is byte-identical
to its first revision.

Final `MANIFEST.sha256` digests (raw LF bytes, `sha256sum -c` → 4/4 OK):

```text
d5ee7f463e307fa9674bc45353fa6396a995504115a3b4955a01e67f79586432  HUMAN_DECISION_MATRIX.md
61ab9095675cb3cbfd98d87f7bf7c20cee8ddc206a87b8e91c7639bfc41e3964  METHOD_CANDIDATE.md
85e08f4e6453045b82638f64e5a7a741b6041daf300f427afa4b53138059ad66  PREREGISTRATION_TEMPLATE.md
569d7ccc11d260245bd64153642c8ca1407ba586a95ea6552dc35e1272c73dd5  README.md
```

## 6. New findings not repaired — for the human statistician

These bear on the *substance* of `PROPOSED` items. Under the review discipline,
a change to a recommendation is a proposal to the human, not an edit; they are
recorded here and pointed to from `README.md` §6.4. They answer `README.md` §4
`Q5` ("is any `PROPOSED` value in fact unsupported…?").

- **`F-Q1` (`QUESTION`, material) — Lemma `L-1` collapses the row-12 pairing.**
  `METHOD_CANDIDATE.md` §6.2 / `D-14`(a) proposes: pass iff realized `E-IMPROV`
  `>=` the type-7 `0.95` quantile of 500 null `E-IMPROV` values. Every null draw
  and the candidate share the same benchmark leg `b` on the same window, so
  `E-IMPROV_i = A*S(x_i) - A*S(b)` for all `i`; the quantile is
  translation-equivariant; hence the event is **exactly** `S(c) >= q_0.95{S(null_i)}`.
  The benchmark cancels: "versus `VOL_TARGET_BUY_AND_HOLD`" (protocol lines
  137, 140) becomes inert for the pass decision. This is the same `L-1`
  collapse the packet uses *against* `E-IMPROV` in `D-08` ("reduces to the
  candidate's own Sharpe, contradicting the incremental objective"), applied
  inconsistently: it is invoked for row 8 and unnoticed for row 12. Under `E-DIFF`
  the benchmark does not cancel. The statistician should decide whether
  `D-14`(a) with `E-IMPROV` is acceptable *knowing* the pairing is vacuous for
  this row, or whether row 12 should be demoted to a placeholder or re-proposed.
  (Rows 3–7 do **not** collapse: sign tests compare `S(c)` with `S(b)`; the
  plateau `0.5*` rule is not translation-invariant; the CI is on the difference.)
- **`F-Q2` (`QUESTION`) — is `D-08`(a) an amendment or an interpretation?** The
  same undefined token `paired_delta_sharpe` is classified *interpretive* in
  rows 3–7 but reading it as `E-DIFF` in row 8 is classified *amendment-required*
  ("amends one clause's wording"). Row 8 is the one clause whose frozen stored
  input (a difference matrix, 237–239) is *consistent* with the `E-DIFF` reading,
  so under the packet's own Queue definitions option (a) could equally be
  "interpretive, input-constrained". The conservative classification errs toward
  more human process and is inherited from the external packet, so it is not a
  defect; but a statistician answering `Q2` should know the classification is a
  choice, not a consequence.
- **`F-Q3` (`QUESTION`) — internal-usage evidence the Queue I candidates do not
  weigh.** The protocol's own use of "delta-Sharpe" at line 85 ("compute
  delta-Sharpe per path" on a resampled *difference* path) is coherent only if
  the drafter meant a difference-path Sharpe (`E-DIFF`-type); lines 229–230 and
  239 frame the objective as "incremental evidence rather than BTC beta". This is
  textual evidence that the drafter's `paired_delta_sharpe` may be `E-DIFF`, and
  it cuts against the `E-IMPROV` candidates in `D-02`, `D-03`, `D-04`, `D-07`,
  whose stated basis is "the literal reading of 'delta-Sharpe' as a delta of
  Sharpes". The opposite evidence — the de-risker justification at lines 93–95,
  which `TECHNICAL_APPENDIX.md` §3 shows favours `E-IMPROV` for sign gates — is
  already in the packet. Both should be weighed explicitly; neither is.
- **`F-N1` (`NON-BLOCKING`) — row-1 label.** Row 1 is labelled `E-DIFF —
  CONFIRM ONLY`, but `E-DIFF` is defined *annualized* (`A*S(d)`) while §3.1
  correctly feeds DSR the **unannualized** `S(d)`; DSR is not scale-invariant in
  `S`, so the distinction is material. §3.1 states it; the row label does not.
  Not edited (touches an estimand label).
- **`F-N2` (`NON-BLOCKING`) — undisclosed reversal of a prior AI proposal.**
  `DRAFT_AMENDMENT_PROPOSAL.md:129` proposed ranking PBO by **paired Sharpe
  improvement** (`E-IMPROV`); `D-08` recommends `E-DIFF`. The packet cites line
  129 only for the tie rule and does not say that `D-08` reverses the earlier
  proposal. A human should see that two AI proposals disagree.
- **`F-N3` (`NON-BLOCKING`) — `0.5` branch reachability understated.** §4.1
  says the zero-logit branch is reached under an exact two-way OOS tie; it is
  also reached without ties whenever `N` is odd and the IS-best trial sits at the
  exact OOS median rank `(N+1)/2`. The branch is therefore live at, e.g.,
  `N = 21`, above the activation threshold. The rule as written handles it.
- **`F-N4` (`NON-BLOCKING`) — `N-4` remedy partly redundant.** Root
  `.gitattributes` already contains `*.sha256 -text`, so §6.2's second line
  (`MANIFEST.sha256 text eol=lf`) duplicates existing protection; the `*.md`
  line is the one that matters. Harmless; not edited.

## 7. Local gate

`LOCAL GATE: PASS` for the reviewed scope after `A-1`–`A-3`, on the same basis
as the Opus review §7, with two rows amended: "Decision/invariant IDs" is `PASS`
only after `A-1`; "Frozen citations" is `PASS` for resolution and the omitted
frozen clause is now cited (`A-3`).

## 8. What remains blocked, who must decide, what is prohibited

Unchanged: every one of `D-01`–`D-20` is open; `D-05`, `D-06`, `D-09`, `D-11`,
`D-12`, `D-15`, `D-16`, `D-17`, `D-18` are blocking placeholders; `D-19` is under
the owner's **DEFER**; `D-08`, `D-12`, `D-14` are §4 questions; `A(N)`'s count,
the effective-count construct and trigger (now with Constitution §9 line 106 in
evidence), the selection event, and the `0.95` claim are unresolved. Astra
`B1`–`B5` and `DEC-01`–`DEC-03` are open. `F-Q1`–`F-Q3` are for a qualified
statistician; `F-Q1` may lead to demoting a `PROPOSED` item, which only a human
may do.

Still prohibited and not authorized by anything here: authoring, merging,
activating, or self-approving an amendment; Task 13; a calibration engine; any
simulation or Monte Carlo run; confirmation-partition or lockbox access; a
governed trial; an eligibility decision; promotion; deployment; trading; editing
`review/task6/verify_frozen.ps1` (reported as `N-3`, not repaired). The
`dsr_minimum: 0.95` gate remains unsatisfied and promotion remains blocked.

Constitution §16 requires different-model **and** human PR review before any
protected component merges; two AI reviews of different model families are not
that human review and do not substitute for statistician acceptance.

**Claude adversarial-review status:** this document is the adversarial review.
**Human/statistician review status:** `NOT SENT`.
