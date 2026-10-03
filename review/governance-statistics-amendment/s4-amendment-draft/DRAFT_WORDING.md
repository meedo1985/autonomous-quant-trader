# Constitution §4 amendment — draft wording for C2 (DSR and selection)

**Status:** `AI WORDING PROPOSAL — NOT AN AMENDMENT — NOT AUTHORED — NOT SIGNED — NOT ACTIVE`
**Date:** 2026-10-03, revision 3
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). Constitution §4 line 50:
an AI "may propose but not author/merge/activate/self-approve amendments".
This file only proposes wording; the amendment exists only if the owner
adopts it as his own text and makes the signed, dated commit (§4 line 48).
**Basis:** owner decisions D-18 (`../d18-proposal/OWNER_DECISION_D18.md`,
rev. 7 `9718fdc`) and B-1..B-7 (`../broadened-method/OWNER_DECISION_B.md`,
design rev. 3 `a3d2c59`); scope D-18 O18-5, O18-7 and design §7.
**History:** rev. 1 `e44146e` — Fable FA1 SOUND WITH FIXES, Sol SA1 UNSOUND
(`2ecf18f`), adjudication `ff3c7f8`. Rev. 2 `afed53e` — focused checks Fable
FA2 NOT READY (`b38204b`), Sol SA2 NOT READY (`9f67598`), adjudication
`ADJUDICATION_AFED53E.md`. Rev. 3 applies every disposition there.
**Labels:** `[AI default]` = drafting choice, not an owner decision.
`[derived]` = follows from decided rules. `<<OWNER O-n>>` = owner decision
still needed (§7). `<<D19: x>>` = value only the D-19 calibration can supply.
`<<DECLARATION: x>>` = value computed at C2's declaration. `<<OPEN D-nn>>` =
clause governed by an open decision row. **The amendment cannot be signed
while any `<<…>>` marker remains.**

## 0. Structure, precedence and activation

The amendment consists of Constitution v1.1 changes (§1), protocol v1.1 for
cycle C2 (§2–§4), and two annexes that the protocol binds by hash:

| Annex | Content | SHA-256 (LF, as committed) |
|---|---|---|
| `ANNEX_A_SELECTION_RULE.md` | D-18 rev. 7 §2 (P18-0..P18-7) verbatim, plus clause A-B7 (owner decision B-7) | `836adec7a40c8d0b494352e71116752ea577dd3403d59b0c8769a2445d388480` |
| `ANNEX_B_DSR_METHOD.md` | broadened method rev. 3 §2.1–§2.6 verbatim | `80ad6b785de337568e806d6feda9168f2ec9b07aed2d8e1e5c14c955ff2b25d0` |

**Precedence** (FA2-1, FA2-12, SA2-1), highest first:
1. Constitution v1.1.
2. The reading and override clauses R-1..R-8 in §2.0.
3. The annex text.
4. The other protocol v1.1 clauses.

The annexes stay verbatim, so their hashes stay those of the decided text;
corrections live only in §2.0. The hashes are recomputed at activation if the
owner edits an annex, and the edited text is then re-reviewed (§6 step 2).

**On activation** [AI default]: new files `docs/RESEARCH_CONSTITUTION_v1.1.md`,
`protocols/protocol_v1.1.yaml` and the two annexes under `specs/`, each with a
SHA-256 sidecar, sit beside the preserved, unchanged v1.0 files. Their `-text`
entries are added to `.gitattributes` before hashing. The `FROZEN_HASHES.json`
additions are made in the owner's signed activation commit, as an append that
changes no existing entry.

## 1. Constitution v1.1 — clause changes

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| header l.2, 5, 8 | `Research Constitution v1.0`; effective 2026-09-11; content hash | `v1.1`; effective = activation date; content hash recomputed per `HASH_CANONICALIZATION_v1.md` |
| §0 new, after l.19 | — | "Eligible confirmation window = a confirmation segment meeting at least conditions (i)–(v) of the eligibility rule in the selection-rule annex frozen with the C2 protocol (never mounted in the sandbox and never evaluated before declaration; no overlap with any exposed segment; separated from all mounted or evaluated data by the gap embargo; for post-v1 data, declared before its first observation; at least `T_min` days). A cycle may nominate and promote only on an eligible window. A later protocol may add conditions but not remove these." (FA2-9) |
| §5 l.61 | "Every cycle protocol must define family-budget exhaustion, calendar/time limit, and candidate-promotion termination. Otherwise invalid." | unchanged, plus: "When the protocol has a single nomination look, budget exhaustion means completion of the declared plan, and the calendar limit includes the post-nomination window." |
| §5 l.63 | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `PROTOCOL_REVISION`, `INVALIDATED`." | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `RESEARCH_ONLY` (no eligible window; no nomination possible), `NO_RESULT` (eligible cycle with no result in every declared family: the family is unavailable, a mandatory gate of its nominee is unavailable or technically invalid, or its lockbox read failed technically), `PROTOCOL_REVISION`, `INVALIDATED`." [AI default: the label names] Whether `RESEARCH_ONLY` or `NO_RESULT` opens the deployable-baseline path (§0 l.17, §11): `<<OWNER O-4>>` (FA2-11) |
| §5 l.67 | "Prior-cycle results are not pooled into later DSR/PBO matrices; lifetime trial counts persist." | "... lifetime trial counts persist: they are recorded and reported with every result, and do not enter the DSR score." (B-2) |
| §7 new, after l.81 | — | "An exposed segment rolled into confirmation is never part of an eligible confirmation window." |
| §7a l.92 | "Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation." | "... and, for a trial attempt that wrote no result artifact, one fixed crash code. Crash diagnostics stay outside the sandbox." (O18-7) |
| §8 new, after l.97 | — | "A cycle's complete trial set is declared and hashed before its first evaluation; no hypothesis or grid point is registered into that cycle afterwards." (P18-1) |
| §9 l.104 | "All failures count. Lifetime family accounting persists." | "All failures count, including every automatic re-run attempt (P18-1). Lifetime family accounting persists as recorded and reported counts (B-2)." |
| §9 l.106 | "If no frozen effective-count method exists, raw count is used." | "If the frozen DSR method uses an effective trial count and none is frozen, the raw count is used. A frozen DSR method may instead use no count at all; the method frozen with the C2 protocol uses none. Raw current-cycle and lifetime counts are always recorded and reported with every result." (B-1; FA2-14) |
| §9 new, after l.106 | — | "False-promotion allowance: the m-th eligible cycle, counted from the first cycle declared on an eligible window, has a whole-cycle allowance of 0.05 / 2^(m−1), split equally between its families. After n eligible cycles the total is 0.10·(1 − 2^(−n)), always below 0.10. A cycle protocol may set a smaller allowance, never a larger one." (B-5). Which cycles increment `m`: `<<OWNER O-1>>` |
| §27 l.194 | "Promotion-relevant artifacts must reproduce from recorded hashes/seeds or are void." | "... from recorded hashes/seeds, including the family seeds of the frozen DSR method, or are void." |

Not changed in v1.1: §0 l.20, §7 l.81 and l.83. C2 uses only the v1
confirmation partition. Admitting post-v1 data to confirmation needs a later
amendment, before C3, that fixes the assignment rule before the data exist.

## 2. Protocol v1.1 (cycle C2) — clause changes

`protocol_version: "1.1"`, `cycle_id: "C2"`, `constitution_version: "1.1"`,
every bound hash recomputed. **Every v1.0 key path and leaf shape is kept**
(`{value, justification}` objects stay objects, booleans stay booleans;
SA2-4). New meaning goes into `justification` or into new keys. Lines not
listed carry over unchanged, except the clauses marked in §4.

### 2.0 Reading and override clauses (prevail over the annex text)

```yaml
annex_reading:
  R-1: "Line numbers in the annexes refer to docs/RESEARCH_CONSTITUTION.md and protocols/protocol_v1.yaml v1.0 at their frozen hashes. Finding ids (FR-n, SR-n, FB-n, SB-n), file citations, code paths, the status header, and the labels 'Proposed', 'AI default' and 'to be bound/confirmed in the amendment' are informative, not normative."   # FA2-6
  R-2: "Where Annex A says something is 'to be bound in the amendment', this protocol's explicit clause binds it; where none exists, the matter is unbound and blocks the cycle."
  R-3: "For C2, 'its first embargo dropped' in P18-0 means: the first gap_embargo.value_days days of the v1 confirmation partition are excluded, so the eligible window starts at partitions.confirmation.start.value."   # SA2-1
  R-4: "P18-0's text on windows created after v1 has no effect under this protocol; no post-v1 window is eligible until a later amendment."   # FA2-6
  R-5: "P18-1's 'to be confirmed in the amendment' on budget scope is resolved as per cycle (trial_accounting below)."   # derived
  R-6: "P18-2(a) 'the cycle ends only when (b)-(d) complete' is subject to the calendar limit cycle_termination.calendar_days_elapsed and to calendar_cap_rule below."   # FA2-1, SA2-1, SA2-3
  R-7: "In Annex B §2.4, the family seed is fixed at declaration, before the first evaluation and before any stream use; the sentence 'Seeds are fixed before any data exists ... cannot be gamed' is informative and does not hold for C2 (see seed_disclosure)."   # SA2-2, FA2-7
  R-8: "Annex B's references to existing code (bootstrap_indices, the replicate-seed construction, the Politis-White routine) bind to that code at a hash fixed under <<OPEN D-20>>."   # FA1-2 residue
seed_disclosure: <<OWNER O-6>>
```

### 2.1 Partitions and gap embargo (v1.0 lines 64–67; lines 205–214 unchanged)

```yaml
partitions:                                    # keys unchanged
  confirmation:
    start: <<DECLARATION: exact UTC timestamp = 2022-01-01T00:00:00Z + gap_embargo.value_days>>
    end: "2025-05-31T23:59:59Z"
selection_rule:
  value: {annex: "ANNEX_A_SELECTION_RULE.md", sha256: "836adec7a40c8d0b494352e71116752ea577dd3403d59b0c8769a2445d388480"}
  justification: "D-18 rev. 7 and B-7; read with annex_reading."
  c2_window: "v1 confirmation partition, eligible only if the job log shows it was never mounted in the sandbox and never evaluated (P18-0)"
  t_min_days: <<D19: T_min>>                   # A-B7: eligibility, checked before computation
gap_embargo:
  rule: "ceiling, in whole days, of the maximum over declared horizons of max(label_horizon, target_autocorr_cutoff), computed once before declaration from data mounted in the sandbox or evaluated before declaration"   # FA2-10
  value_days: <<DECLARATION: computed value>>
```

`validation.embargo` (v1.0 lines 205–214) is unchanged and still governs folds.

### 2.2 Declaration and budget (v1.0 lines 184–190, 292)

```yaml
trial_accounting:
  trend_budget:
    value: 81
    justification: "Per cycle [derived: P18-1, B-2, Constitution §0 l.12]: at most 80 declared trials plus one automatic re-run slot (Annex A P18-1)."
  volatility_budget:
    value: 81
    justification: "As trend_budget."
  lifetime_accounting: true                    # meaning per Constitution v1.1 §5 l.67, §9: recorded and reported, not in the DSR score
promotion:
  trial_budget_hard_stop: true                 # no evaluation outside the declared set and its re-run slot
```

### 2.3 Nomination, lockbox and termination (v1.0 lines 74, 192–195, 251, 300)

```yaml
lockbox_policy:
  max_evaluations_per_family_per_cycle:
    value: 1
    justification: "One nominee per family; no replacement (Annex A P18-5)."
validation:
  configuration_selection:
    value: "each grid point is one fixed trial; no per-fold reselection; the nominee is chosen by Annex A P18-4; DSR, PBO and plateau account for selection"
    justification: "Annex A P18-2 to P18-5."
cycle_termination:
  nomination_deadline_days: 180                # the single nomination look happens by this day
  post_nomination_window_days: <<OWNER O-2: recommended 75>>
  calendar_days_elapsed: <<OWNER O-2: 180 + post_nomination_window_days, recommended 255>>   # the hard calendar limit
  plan_complete_rule: "the declared plan is complete at the nomination look; a trial unfinished then is a U_ops timeout (Annex A P18-7)"   # FA2-8
  ends_when_any: ["all_family_trial_budgets_exhausted","calendar_days_elapsed","candidate_promoted","protocol_revision","cycle_invalidated"]
  ends_when_any_meaning:
    all_family_trial_budgets_exhausted: "plan complete AND every nominee processed"
    calendar_days_elapsed: "hard limit above"
    candidate_promoted: "recorded once, after every nominee is processed"
  outcomes: ["CANDIDATE_PROMOTED","NO_EDGE_FOUND","RESEARCH_ONLY","NO_RESULT","PROTOCOL_REVISION","INVALIDATED"]
  recorded_times: ["declaration","plan_exhaustion","nomination_look","each_gate_and_lockbox_read","outcome"]
post_nomination_procedure:
  order: "trend nominee, then volatility nominee; a promotion of one never stops processing of the other"
  per_nominee: "every gate in §3 is computed; only a nominee that is ELIGIBLE (Constitution §13) requests a lockbox read; then attestation with the 72 h cooling-off (line 300)"
  lockbox_cooldown_days: 30                    # line 75, applied between the two families' reads [AI default]
  calendar_cap_rule: <<OWNER O-2>>
  revision_or_invalidation_after_look: <<OWNER O-3>>
  before_look: "no nomination and no promotion"
```

### 2.4 DSR method and error budget (v1.0 lines 223–233, 266, 287)

```yaml
validation:
  bootstrap:                                   # type, block_method, iterations unchanged
    added_purposes: ["dsr_family_max_null"]    # existing purposes, incl. the lockbox interval (line 85), unchanged
  dsr:
    series: {value: "BTC candidate_minus_VOL_TARGET_BUY_AND_HOLD paired OOS return series (E-DIFF), complete UTC days", justification: "unchanged"}
    minimum: "z-test, Annex A P18-6"           # was 0.95
    method: {annex: "ANNEX_B_DSR_METHOD.md", sha256: "80ad6b785de337568e806d6feda9168f2ec9b07aed2d8e1e5c14c955ff2b25d0", id: "aqt.dsr.bootstrap_max.candidate.v2"}
    family_block_rule: <<D19: largest or median>>
    z_crit: <<D19: z_crit_1, certified on held-out replications at alpha 0.05 whole cycle / 0.025 per family>>
    effective_trial_count_method: "none"       # B-1; replaces line 232
    fallback: "none"                           # B-1; replaces line 233
  random_seed_policy: "trial: SHA256(protocol_hash,hypothesis_hash,trial_index) -> deterministic seed (unchanged); family: Annex B §2.4 read with R-7"
error_budget:
  eligible_cycle_index_m: 1                    # if C2 is eligible; Constitution v1.1 §9
  alpha_whole_cycle: 0.05
  alpha_per_family: 0.025
  procedure_no_result: "U_proc <= 0.01, Annex A P18-7, over the gates of §3; allocation <<D19: joint cells or per-family split>>"
promotion:
  dsr_minimum: "Annex A P18-6"                 # was 0.95
```

The support classifier is not protocol text. It belongs to the D-19
preregistration that certifies `z_crit` (A-B7).

## 3. Gate list (D-18 O18-5)

Each nominee's mandatory pre-lockbox gates. "Technically invalid" and "not
computed" both mean `UNAVAILABLE` (P18-3, P18-7). A gate marked `<<OPEN>>`
has no operative definition yet (§4).

| # | Gate (v1.0 line) | PASS / FAIL | N/A (frozen) | Status |
|---|---|---|---|---|
| G-1 | BTC paired 90% CI lower bound > 0 (274–275) | lower bound > 0 | never | `<<OPEN D-03>>` |
| G-2 | BTC drawdown constraint (276–278) | MDD no worse than benchmark by > 0.05 | never | defined |
| G-3 | ETH sanity (42–44, 279) | point estimate > 0 and drawdown holds at 1x | never | `<<OPEN D-02>>` |
| G-4 | Paired fold win rate ≥ 0.60 (280–282) | as written | never | `<<OPEN D-06, D-07>>` |
| G-5 | Survive 2x cost (283) | as written | never | `<<OPEN D-02>>` |
| G-6, G-7 | Feature- and execution-delay hard gates (267–268, 284–285) | no statistic | never | `<<OPEN D-15>>` |
| G-8 | Parameter plateau (263–265, 286) | as written | no ordered numeric tunable dimension (line 264) | `<<OPEN D-04, D-05>>` |
| G-9 | DSR (287) | Annex A P18-6 | never | defined (values from D-19) |
| G-10 | PBO ≤ 0.30 (234–241, 288) | as written | family trials < 20 (line 235) | `<<OPEN D-08, D-09, D-10>>` |
| G-11 | Random-exposure null (134–140, 289) | no event | never | `<<OPEN D-14>>` |
| G-12 | Minimum effective decisions ≥ 120 (242–244, 290) | as written | never | defined |
| G-13 | Benchmark hash matches (291) | as written | never | defined |
| — | OOS/IS ratio (245–249) | no frozen threshold: reported, not a gate | rule-based models (line 249) | informative |
| — | Trial budget hard stop (292) | enforcement: a violation invalidates the cycle | — | defined |

The lockbox stage (lines 83–92) comes after eligibility and is not part of
`U_proc` (P18-7). Its technical failure is a `NO_RESULT` cause (§1).

## 4. Clauses carried over but still blocked

These lines carry over with the marker shown and are not operative until the
row is decided and its wording inserted. **No clause is both bound and
marked** (SA2-5). Lines 75, 76, 80–82, 294–296 and 300 stay in force.

| v1.0 lines | Clause | Marker |
|---|---|---|
| 263–265, 286 | plateau | `<<OPEN D-04, D-05>>` |
| 201–204, 280–282 | fold unit, fold win rate | `<<OPEN D-06, D-07>>` |
| 234–241, 288 | PBO | `<<OPEN D-08, D-09, D-10>>` (D-08 must adopt E-DIFF, D-18 O18-6) |
| 215–222 | CPCV diagnostic report | `<<OPEN D-13>>` (FA2-13) |
| 77–79 | lockbox attestation coarse fields | `<<OPEN D-12>>` |
| 83–92 | lockbox prediction interval and pass rule | `<<OPEN D-11>>` |
| 134–140, 289 | random-exposure null pass event | `<<OPEN D-14>>` |
| 267–268, 284–285 | delay hard gates | `<<OPEN D-15>>` |
| 42–44, 279, 283 | ETH sanity and 2x-cost estimand | `<<OPEN D-02>>` (no decision record found) |
| 274–275 | paired CI estimand | `<<OPEN D-03>>` (no decision record found) |
| §2.0 R-8; §2.4 `added_purposes`, family seed | reference vectors for bootstrap-backed clauses | `<<OPEN D-20>>` (matrix line 80 is stale) |

**No "keep blocked" option for gates G-1..G-13** (FA2-3). Under P18-5 and
P18-7, a mandatory gate that cannot be computed makes every nominee
unavailable. D-19 could then never certify the 1% target, and running C2
would use up the only eligible window for both families with no chance of
promotion. Each `<<OPEN>>` gate must therefore be decided before signing. A
gate may become `N/A` only by an explicit §4 decision, never by being left
blocked.

## 5. Rationale, as §4 requires (the owner writes the final words)

> The v1.0 DSR clause names an effective-count method that was never
> defined, and a 0.95 threshold with no stated error rate (D-16, D-19). This
> amendment fixes one selection rule: each family's best-Sharpe declared
> trial, one look, no replacement. Only confirmation data never evaluated
> before may promote. A bootstrap of the family's own returns replaces the
> count-based penalty. The target is that, when no strategy has an edge, a
> false promotion happens in at most 5% of first eligible cycles, halving in
> each later one.
>
> These are calibration targets under simulated conditions, not guarantees.
> They are checked only under the all-no-edge null and assume the data come
> from the supported kind of return series. For C2 they also assume that the
> strategies, and therefore the family seed, were chosen independently of
> 2022–2025 prices, which are public and which the declarers lived through;
> this cannot be verified. Infrastructure failures are counted, not
> certified. No human statistician reviewed this; two different AI model
> families did. The review history is in the records listed above.

## 6. §4 and §16 checklist (owner steps, in order)

1. Fill every `<<…>>` marker: D-19 preregistered, run and accepted; every row
   in §4 decided; owner items O-1..O-6 answered.
2. Two different-model reviews of the final wording, records committed
   (R19-2). If the owner edits the reviewed text or an annex materially, it
   is re-reviewed.
3. Classify the amendment as safety or not (`<<OWNER O-5>>`). If safety: no
   open incident or post-HALT cooling-off (§4 l.56), and the 72-hour minimum
   activation delay (§4 l.52).
4. Version bump of the Constitution and protocol, and the written rationale
   (§4 l.48).
5. C1 is formally terminated with outcome `PROTOCOL_REVISION`, after
   checking that no C1 trial ever started.
6. The owner authors the text and makes the signed, dated commit; history is
   preserved (§4 l.48).
7. §16-protected code is merged only after a different-model review and the
   owner's PR review. That covers the DSR/promotion gate; protocol
   enforcement (declaration hash, budget stop, automatic re-run, eligibility
   and `T_min`, crash-code channel); lockbox access tooling (one read per
   family); and the validation engine.
8. Activation happens before C2's declaration, following the §0 steps.
9. No retroactive effect on open promotions (§4 l.48): confirm that none is
   open.

## 7. Owner items (asked together when the text is near signable)

- **O-1** Which cycles count toward `m`. Recommendation: every cycle declared
  on an eligible window, whatever its outcome (conservative).
- **O-2** Post-nomination window and calendar-cap rule. Recommendation: 75
  days, a limit of 255 days, and the cap ends processing with no promotion
  for any unprocessed nominee. The schedule (two lockbox reads 30 days apart,
  plus 72 h cooling-off) fits well inside 75 days, so expiry can happen only
  through an owner decision not being made, or through an infrastructure
  delay. Both are governance or infrastructure causes, counted as `U_ops`
  under P18-7's precedence, not procedure causes (SA2-6).
- **O-3** A protocol revision or invalidation after the look. Two readings of
  §4 l.48 "no retroactive effect on open promotions" (FA2-5, SA2-7):
  (a) "open" means already attested, so a revision ends processing of any
  nominee not yet attested; (b) promotion is the whole sequence eligibility →
  lockbox → attestation (§0 l.21), so a nominee already `ELIGIBLE` keeps being
  processed under the old rules. No recommendation: this is a reading of the
  Constitution.
- **O-4** Whether `RESEARCH_ONLY` or `NO_RESULT` (including a technically
  failed lockbox read) may use the deployable-baseline path. Recommendation:
  no; only `NO_EDGE_FOUND` does.
- **O-5** Safety classification. Recommendation: treat as safety-relevant
  (72 hours, incident check).
- **O-6** Family seed for C2 (FA2-7). Someone could try many declarations
  against private replays of public data and pick a favourable seed (effect
  about 0.03 standard deviations on `z`). Recommendation: disclose it as a
  weakness (done in §5), and also require every declaration attempt to be
  logged, so that only the first hashed declaration of C2 is valid.

## 8. Next

[AI default] A focused re-check of revision 3 by both model families, then
the D-19 calibration preregistration, which supplies the `<<D19>>` values.
