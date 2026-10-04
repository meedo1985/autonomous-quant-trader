# Constitution §4 amendment — draft wording for C2 (DSR and selection)

**Status:** `AI WORDING PROPOSAL — NOT AN AMENDMENT — NOT AUTHORED — NOT SIGNED — NOT ACTIVE`
**Date:** 2026-10-04, revision 5
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). Constitution §4 line 50:
an AI "may propose but not author/merge/activate/self-approve amendments".
This file only proposes wording; the amendment exists only if the owner
adopts it as his own text and makes the signed, dated commit (§4 line 48).
**Basis:** owner decisions D-18 (`../d18-proposal/OWNER_DECISION_D18.md`,
rev. 7 `9718fdc`) and B-1..B-7 (`../broadened-method/OWNER_DECISION_B.md`,
design rev. 3 `a3d2c59`); scope D-18 O18-5, O18-7 and design §7. Revision 5
adds the gate decisions D-01..D-10, D-14, D-15, N-1..N-4 (records listed in
Annex C) and the owner items O-1..O-7 (`OWNER_DECISION_O1_O7.md`).
**History:** rev. 1 `e44146e` — Fable FA1 SOUND WITH FIXES, Sol SA1 UNSOUND
(`2ecf18f`), adjudication `ff3c7f8`. Rev. 2 `afed53e` — focused checks Fable
FA2 NOT READY (`b38204b`), Sol SA2 NOT READY (`9f67598`), adjudication
`ADJUDICATION_AFED53E.md`. Rev. 3 `fcc0cf2` — focused checks Fable FA3 NOT
READY (`5ba2c05`), Sol SA3 NOT READY (`5f09df9`), adjudication
`ADJUDICATION_FCC0CF2.md`. Rev. 4 `fb3be96` applied every disposition there
(not reviewed). Rev. 5 folds in every decision listed under Basis and adds
Annex C; it has not been reviewed.
**Labels:** `[AI default]` = drafting choice, not an owner decision.
`[derived]` = follows from decided rules. `<<OWNER REG-n>>` = owner decision
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
| `ANNEX_C_GATE_DEFINITIONS.md` | operative definitions of gates G-1..G-14 and the event contract, consolidated from the decided rows (not verbatim; see its fidelity rule) | computed at signing: the annex still carries `<<…>>` markers |

**Precedence** (FA2-1, FA2-12, SA2-1), highest first:
1. Constitution v1.1.
2. The reading and override clauses R-1..R-10 in §2.0.
3. The annex text.
4. The other protocol v1.1 clauses.

Annexes A and B stay verbatim, so their hashes stay those of the decided
text; corrections live only in §2.0. Annex C is a consolidated restatement,
and a divergence from a cited owner record is corrected in Annex C itself
before signing. The hashes are recomputed at activation if the
owner edits an annex, and the edited text is then re-reviewed (§6 step 2).

**On activation** [AI default]: new files `docs/RESEARCH_CONSTITUTION_v1.1.md`,
`protocols/protocol_v1.1.yaml`, `specs/BACKTESTER_SPEC_v1.1.md`,
`specs/CANONICAL_BENCHMARKS_v1.1.md` (§1a) and the three annexes under `specs/`, each with a
SHA-256 sidecar, sit beside the preserved, unchanged v1.0 files. Their `-text`
entries are added to `.gitattributes` before hashing. The `FROZEN_HASHES.json`
additions are made in the owner's signed activation commit, as an append that
changes no existing entry.

## 1. Constitution v1.1 — clause changes

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| header l.2, 5, 8 | `Research Constitution v1.0`; effective 2026-09-11; content hash | `v1.1`; effective = activation date; content hash recomputed per `HASH_CANONICALIZATION_v1.md` |
| §0 new, after l.19 | — | "Eligible confirmation window = a confirmation segment meeting at least conditions (i)–(v) of the eligibility rule in the selection-rule annex frozen with the C2 protocol (never mounted in the sandbox and never evaluated before declaration; no overlap with any exposed segment; separated from all mounted or evaluated data by the gap embargo; for post-v1 data, declared before its first observation; at least `T_min` days). A cycle may nominate and promote only on an eligible window. A later protocol may add conditions but not remove these." (FA2-9) |
| §5 l.61 | "Every cycle protocol must define family-budget exhaustion, calendar/time limit, and candidate-promotion termination. Otherwise invalid." | unchanged, plus: "When the protocol has a single nomination look, budget exhaustion means completion of the declared plan, termination follows the protocol's post-nomination procedure, and the calendar limit includes the post-nomination window." (FA3-7) |
| §5 l.63 | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `PROTOCOL_REVISION`, `INVALIDATED`." | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `RESEARCH_ONLY` (no eligible window; no nomination possible), `NO_RESULT` (eligible cycle with no result in every declared family: the family is unavailable, a mandatory gate of its nominee is unavailable or technically invalid, or its lockbox read failed technically), `PROTOCOL_REVISION`, `INVALIDATED`. Only `NO_EDGE_FOUND` opens the deployable-baseline path; `RESEARCH_ONLY` and `NO_RESULT` do not." [AI default: the label names] (O-4; FA2-11) |
| §5 l.67 | "Prior-cycle results are not pooled into later DSR/PBO matrices; lifetime trial counts persist." | "... lifetime trial counts persist: they are recorded and reported with every result, and enter neither the DSR score nor PBO enablement." (B-2; D-09. The D-09 proposal cites this override as "l.61"; it means this row.) |
| §7 new, after l.81 | — | "An exposed segment rolled into confirmation is never part of an eligible confirmation window." |
| §7a l.92 | "Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation." | "... and, for a trial attempt that wrote no result artifact, one fixed crash code. Crash diagnostics stay outside the sandbox." (O18-7) |
| §8 new, after l.97 | — | "A cycle's complete trial set is declared and hashed before its first evaluation; no hypothesis or grid point is registered into that cycle afterwards." (P18-1) |
| §9 l.104 | "All failures count. Lifetime family accounting persists." | "All failures count, including every automatic re-run attempt (P18-1). Lifetime family accounting persists as recorded and reported counts (B-2)." |
| §9 l.106 | "If no frozen effective-count method exists, raw count is used." | "If the frozen DSR method uses an effective trial count and none is frozen, the raw count is used. A frozen DSR method may instead use no count at all; the method frozen with the C2 protocol uses none. Raw current-cycle and lifetime counts are always recorded and reported with every result." (B-1; FA2-14) |
| §9 new, after l.106 | — | "False-promotion allowance: the m-th eligible cycle, counted from the first cycle declared on an eligible window, has a whole-cycle allowance of 0.05 / 2^(m−1), split equally between its families. After n eligible cycles the total is 0.10·(1 − 2^(−n)), always below 0.10. A cycle protocol may set a smaller allowance, never a larger one. Every cycle declared on an eligible window increments `m`, whatever its outcome." (B-5; O-1) |
| §27 l.194 | "Promotion-relevant artifacts must reproduce from recorded hashes/seeds or are void." | "... from recorded hashes/seeds, including the family seeds of the frozen DSR method, or are void." |

Not changed in v1.1: §0 l.20, §7 l.81 and l.83. C2 uses only the v1
confirmation partition. Admitting post-v1 data to confirmation needs a later
amendment, before C3, that fixes the assignment rule before the data exist.

## 1a. Frozen specification and protocol lines changed by the event contract (D-15, N-4)

Annex C §C-6 governs every run. It requires these v1.1 texts:

| File, line | v1.0 text (abridged) | v1.1 text |
|---|---|---|
| protocol l.57 | `only_at_00_00_UTC_and_only_if_24h_since_last_risk_increase` | `only_at_00_00_UTC_and_only_if_24h_since_the_decision_time_of_the_last_filled_risk_increase` (Annex C C-6 (5)) |
| protocol l.60 | `only_reduce_exposure_if_target_is_at_least_0.10_below_current` | `only_reduce_exposure_if_target_is_at_least_0.10_below_held_exposure_or_target_is_0` (N-4) |
| protocol l.113 | `minimum_holding_hours_for_risk_increase: 24` | unchanged value; meaning per new l.57 (justification key added) |
| protocol l.137 | "match candidate mean exposure and turnover on BTC; ..." | "shift the declared signal by whole days, re-size with the trial's own estimator and re-run its overlay; realised mean exposure and turnover of every draw are reported, not matched; evaluate per Annex C C-10" (D-14 Q4) |
| protocol l.240 | `ranking_metric: "paired_delta_sharpe"` | `ranking_metric: "E-DIFF"` (D-08) |
| `BACKTESTER_SPEC` l.9 | "... subject to the 24h minimum-hold rule." | "... subject to the 24h minimum-hold rule, measured from the decision time of the last filled risk increase." |
| `BACKTESTER_SPEC` l.10 | "Intraday hourly actions are allowed only for exposure reductions when the 10pp band is crossed." | "... when the 10pp band is crossed, or to exit to zero exposure, which the band never blocks." |
| `CANONICAL_BENCHMARKS` l.11 | "Risk increases respect the 24h minimum-holding rule." | "... measured from the decision time of the last filled risk increase." |
| `CANONICAL_BENCHMARKS` l.12 | "Intraday band-triggered actions are allowed only to reduce exposure." | "... only to reduce exposure; an exit to zero is never blocked by the band." |

The canonical benchmarks change too, so every benchmark hash is recomputed,
and G-13 compares against the v1.1 hash. [derived]

## 2. Protocol v1.1 (cycle C2) — clause changes

`protocol_version: "1.1"`, `cycle_id: "C2"`, `constitution_version: "1.1"`,
every bound hash recomputed. **Every v1.0 key path and leaf shape is kept**
(`{value, justification}` objects stay objects, booleans stay booleans;
SA2-4), with two named exceptions: `validation.dsr.minimum` and
`promotion.dsr_minimum` change from the number `0.95` to text naming the
z-test (FA3-4; no code reads them). New meaning goes into `justification` or into new keys. Lines not
listed carry over unchanged, except the clauses marked in §4.

### 2.0 Reading and override clauses (prevail over the annex text)

```yaml
annex_reading:
  R-1: "Line numbers in the annexes refer to docs/RESEARCH_CONSTITUTION.md and protocols/protocol_v1.yaml v1.0 at their frozen hashes. Finding ids (FR-n, SR-n, FB-n, SB-n), file citations, code paths, the status header, and the labels 'Proposed', 'AI default' and 'to be bound/confirmed in the amendment' are informative, not normative, except the code references that R-8 binds."   # FA2-6, SA3-4
  R-2: "Where Annex A says something is 'to be bound in the amendment', this protocol's explicit clause binds it; where none exists, the matter is unbound and blocks the cycle."
  R-3: "For C2, 'its first embargo dropped' in P18-0 means: the first gap_embargo.value_days days of the v1 confirmation partition are excluded, so the eligible window starts at partitions.confirmation.start."   # SA2-1, SA3-1, FA3-5
  R-4: "P18-0's text on windows created after v1 has no effect under this protocol; no post-v1 window is eligible until a later amendment."   # FA2-6
  R-5: "P18-1's 'to be confirmed in the amendment' on budget scope is resolved as per cycle (trial_accounting below)."   # derived
  R-6: "P18-2(a) 'the cycle ends only when (b)-(d) complete' is subject to the calendar limit cycle_termination.calendar_days_elapsed and to calendar_cap_rule below."   # FA2-1, SA2-1, SA2-3
  R-7: "In Annex B §2.4, the family seed is fixed by seed_disclosure.procedure, after the declaration is committed and before the first evaluation and any stream use; the sentence 'Seeds are fixed before any data exists ... cannot be gamed' is informative and does not hold for C2 (see seed_disclosure)."   # SA2-2, FA2-7
  R-8: "Annex B's references to existing code (bootstrap_indices, the replicate-seed construction, the Politis-White routine) bind to that code at a hash fixed under <<OPEN D-20>>."   # FA1-2 residue
  R-9: "In P18-0 (iii), the embargo used for the gap is gap_embargo.value_days, computed by gap_embargo.rule; 'data outside the window' is replaced by 'data mounted in the sandbox or evaluated before declaration'. No confirmation or lockbox data not already so mounted or evaluated may be used."   # SA3-2
  R-10: "Annex C defines every promotion gate in promotion.gates and the event contract for all runs. Where an Annex A or B clause and Annex C both bear on a gate, Annex A P18-7's availability and cause-code rules apply to Annex C's UNAVAILABLE results."   # derived
seed_disclosure:                               # O-6
  value: "The C2 family seeds are derived from public randomness published after the declaration is committed."
  procedure:                                   # [AI default] mechanics, to be reviewed (§6 step 2)
    commit: "The SHA-256 of the C2 declaration, and nothing else, is posted once in a public channel with a server-assigned timestamp, fixed in this protocol before signing <<OWNER O-6a: channel>>; a declaration cannot choose it, or one hash per channel would reopen the search. The first such post for C2 governs; a second post for C2 invalidates the cycle."
    beacon: "A drand League of Entropy mainnet chain, named in the declaration by its chain hash."
    round: "The first round of that chain whose scheduled time is at least 24 hours after the post's server timestamp."
    derivation: "family_seed_f = SHA256(declaration_sha256 || beacon_randomness || family_id), reduced to Annex B's seed width; byte encoding <<OPEN D-20>>."
    unavailable_beacon: "If the round is not published within 7 days of its scheduled time, the cycle is INVALIDATED before any evaluation."
  disclosure: "kept as in §5"
```

The public post reveals only a hash, not the declaration. A private
commitment alone cannot stop someone from trying many declarations and
choosing among them after the beacon is published, because private
commitments can be multiplied. Only a single public post closes that route.
If the owner does not want any public post, the alternative is a trusted
third party who receives the hash. In that case O-6 is re-asked.

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
  excluded_days_status: "the first value_days days of the v1 confirmation partition are not exploration, are never mounted in the sandbox, are reachable only through the engine, and are never part of the eligible window"   # [AI default] FA3-11
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
  post_nomination_window_days: 75              # O-2
  calendar_days_elapsed: 255                   # O-2; 180 + 75, the hard calendar limit
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
  per_nominee: "every gate in promotion.gates with stage pre_lockbox is computed; only a nominee that is ELIGIBLE (Constitution §13) requests a lockbox read; then attestation with the 72 h cooling-off (line 300)"
  lockbox_cooldown_days: 30                    # line 75, applied between the two families' reads [AI default]
  calendar_cap_rule: "at day 255 processing ends; no nominee not yet attested is promoted; the expiry is recorded with cause U_ops (Annex A P18-7)"   # O-2; SA2-6
  revision_or_invalidation_after_look: "ends processing of every nominee not yet attested; an attested promotion is unaffected ('open promotion' in Constitution §4 l.48 means attested)"   # O-3 reading (a)
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
  procedure_no_result: "U_proc <= 0.01, Annex A P18-7, over promotion.gates; allocation <<D19: joint cells or per-family split>>"
promotion:
  dsr_minimum: "Annex A P18-6"                 # was 0.95
```

The support classifier is not protocol text. It belongs to the D-19
preregistration that certifies `z_crit` (A-B7).

## 3. Gate list (D-18 O18-5) — protocol text

This block is part of `protocol_v1.1.yaml` (FA3-3). It defines the `U_proc`
domain, which is each nominee's mandatory pre-lockbox gates
(`stage: pre_lockbox`). For every gate, "technically invalid" and "not
computed" both mean `UNAVAILABLE` (P18-3, P18-7). The operative definition of
each gate is the Annex C section named in `def`.

```yaml
promotion:
  gates:
    G-1:  {lines: "274-275", def: "Annex C C-1", na: "never", stage: pre_lockbox, status: "decided D-03"}
    G-2:  {lines: "276-278", def: "Annex C C-2", na: "never", stage: pre_lockbox, status: "decided O-7"}
    G-3:  {lines: "42-44, 279", def: "Annex C C-3", na: "never", stage: pre_lockbox, status: "decided D-02, N-3"}
    G-4:  {lines: "201-204, 280-282", def: "Annex C C-4", na: "never", stage: pre_lockbox, status: "decided D-06, D-07"}
    G-5:  {lines: "283", def: "Annex C C-5", na: "never", stage: pre_lockbox, status: "decided D-02, N-3"}
    G-6:  {lines: "267, 284", def: "Annex C C-7", na: "never", stage: pre_lockbox, status: "decided D-15"}
    G-7:  {lines: "268, 285", def: "Annex C C-7", na: "never", stage: pre_lockbox, status: "decided D-15"}
    G-8:  {lines: "260-265, 286", def: "Annex C C-8", na: "no ordered numeric tunable dimension (line 264)", stage: pre_lockbox, status: "decided D-04, D-05"}
    G-9:  {lines: "287", def: "Annex A P18-6", na: "never", stage: pre_lockbox, status: "<<D19 values>>; code binding <<OPEN D-20>>"}
    G-10: {lines: "234-241, 288", def: "Annex C C-9", na: "declared family trials |J_f| < 20 (line 235)", stage: pre_lockbox, status: "decided D-08, D-09, D-10"}
    G-11: {lines: "134-140, 289", def: "Annex C C-10", na: "g11_class constant_signal, fixed at preregistration", stage: pre_lockbox, status: "decided D-14; registration <<OWNER REG-1, REG-2>>; shift sampling <<OPEN D-20>>"}
    G-12: {lines: "242-244, 290", def: "Annex C C-11", na: "never", stage: pre_lockbox, status: "decided N-1"}
    G-13: {lines: "291", def: "benchmark hash matches the v1.1 canonical benchmark hash (§1a)", na: "never", stage: pre_lockbox, status: "defined"}
    G-14: {lines: "141-145, 289", def: "Annex C C-12", na: "trial fits no model of the vol-scaled target, fixed at preregistration", stage: pre_lockbox, status: "decided N-2 (a); seed stream <<OPEN D-20>>"}
    L-1:  {lines: "83-91", pass: "BTC lockbox delta-Sharpe >= 5th percentile of the prediction distribution", na: "never", stage: lockbox, status: "<<OPEN D-11>>"}
    L-2:  {lines: "91", pass: "BTC lockbox delta-Sharpe > 0", na: "never", stage: lockbox, status: "<<OPEN D-11>>"}
    L-3:  {lines: "91", pass: "DD(BTC) (Annex C C-0) holds on the lockbox", na: "never", stage: lockbox, status: "<<OPEN D-11>>"}
    L-4:  {lines: "91", pass: "Annex C C-3 rule on the lockbox (E-IMPROV, D-02)", na: "never", stage: lockbox, status: "<<OPEN D-11>>"}
  informative:
    oos_is_ratio: {lines: "245-249", note: "no frozen threshold: reported, not a gate; N/A for rule-based models (line 249)"}
  enforcement:
    trial_budget_hard_stop: {lines: "292", rule: "a violation invalidates the cycle"}   # [AI default] FA3-10
```

Changes from revision 4:
- G-1..G-8, G-10..G-12 and G-14 now point to Annex C.
- G-11 and G-14 gain frozen `N/A` cases, by explicit decision (D-14 Q2 and
  Q2b (A); N-2 (a)). §4's rule that a gate may become `N/A` only by an
  explicit decision is met.
- G-13 now compares against the v1.1 benchmark hash.

Lockbox gates (`stage: lockbox`) are read only after eligibility (line 295)
and are outside `U_proc`. A technically failed lockbox read is a `NO_RESULT`
cause (§1).

## 4. Clauses still blocked

These lines carry over with the marker shown. They are not operative until
the item is decided and its wording inserted.

| v1.0 lines / place | Clause | Marker |
|---|---|---|
| 215–222 | CPCV diagnostic report (its ESS input is Annex C C-11) | `<<OPEN D-13>>` |
| 77–79 | lockbox attestation coarse fields | `<<OPEN D-12>>` |
| 83–92 | lockbox prediction interval and pass rule (L-1..L-4) | `<<OPEN D-11>>` |
| §2.0 R-8; §2.0 seed derivation; §2.4 `added_purposes`; Annex C C-1, C-10 (3), C-12 (5) | code bindings, stream conventions and reference vectors | `<<OPEN D-20>>` |
| Annex C C-10 (1) | whether a fixed-size rule can be registered; whether `s` may depend on `σ̂` | `<<OWNER REG-1>>`, `<<OWNER REG-2>>` |
| §2.1, §2.4, G-9 | `T_min`, `family_block_rule`, `z_crit`, `U_proc` allocation | `<<D19>>` |
| §2.0 seed channel | the public channel for the declaration hash | `<<OWNER O-6a>>` |
| §2.1 start, gap | values fixed at declaration | `<<DECLARATION>>` |

**D-19 also has to settle how each gate enters the `U_proc` certification**
(N-2 proposal §3). Either D-19 computes every gate in every replication, at
price, position and model level, or this amendment explicitly authorises a
certification route for named gates. Candidates are deterministic
availability arguments, such as the one for G-12. Such a route needs clause
wording here, and that wording is drafted with the D-19 preregistration.
`<<OPEN D-19 route>>`

**There is no "keep blocked" option for the gates** (FA2-3). Under P18-5 and
P18-7, a mandatory gate that cannot be computed makes every nominee
unavailable. Each remaining marker must therefore be filled before signing.

## 5. Rationale, as §4 requires (the owner writes the final words)

> The v1.0 DSR clause names an effective-count method that was never
> defined, and a 0.95 threshold with no stated error rate (D-16, D-19). This
> amendment fixes one selection rule: each family's best-Sharpe declared
> trial, one look, no replacement. Only confirmation data never evaluated
> before may promote. A bootstrap of the family's own returns replaces the
> count-based penalty. The target is that, when no strategy has an edge, a
> false promotion happens in at most 5% of first eligible cycles, halving in
> each later one. It also gives every promotion gate an operative definition
> (Annex C) and fixes how orders, fills and exits work in every run.
>
> These are calibration targets under simulated conditions, not guarantees.
> They are checked only under the all-no-edge null and assume the data come
> from the supported kind of return series. The other gates are filters with
> no error rate of their own. The family seed comes from public randomness
> published after the declaration is committed, but the strategies were
> still chosen by people who lived through 2022–2025 prices, and that cannot
> be verified. Infrastructure failures are counted, not certified. No human
> statistician reviewed this; two different AI model families did. The
> review history is in the records listed above.

## 6. §4 and §16 checklist (owner steps, in order)

1. Fill every `<<…>>` marker (FA3-12). **Done:** every row that governs a
   gate's availability (D-01..D-10, D-14, D-15, N-1..N-4) and O-1..O-7.
   **Remaining, in this order:**
   - REG-1, REG-2 and O-6a;
   - the D-19 preregistration, including the certification route, run and
     accepted, so that its frozen qualification object covers the final gates;
   - then D-11..D-13 and D-20.

   N-1..N-4 are proposed for the decision matrix; adding them is the owner's
   act.
2. Two different-model reviews of the final wording, records committed
   (R19-2). These include a fidelity check of Annex C against the owner
   records. If the owner edits the reviewed text or an annex materially, it
   is re-reviewed.
3. **Safety-relevant (O-5).** No open incident or post-HALT cooling-off
   (§4 l.56), and the 72-hour minimum activation delay (§4 l.52).
4. Version bump of the Constitution, protocol, `BACKTESTER_SPEC` and
   `CANONICAL_BENCHMARKS`, and the written rationale (§4 l.48).
5. C1 is formally terminated with outcome `PROTOCOL_REVISION`, after
   checking that no C1 trial ever started.
6. The owner authors the text and makes the signed, dated commit; history is
   preserved (§4 l.48).
7. §16-protected code is merged only after a different-model review and the
   owner's PR review. That covers:
   - the DSR/promotion gate;
   - protocol enforcement: declaration hash, budget stop, automatic re-run,
     eligibility and `T_min`, crash-code channel, the seed beacon;
   - lockbox access tooling (one read per family);
   - the validation engine;
   - the backtester event contract (Annex C C-6).
8. Activation happens before C2's declaration, following the §0 steps.
9. No retroactive effect on open promotions (§4 l.48): confirm that none is
   open.

## 7. Owner items

**Decided 2026-10-04** (`OWNER_DECISION_O1_O7.md`):
- **O-1:** every eligible cycle counts.
- **O-2:** 75 days, cap at day 255, expiry means no promotion.
- **O-3:** reading (a), stop unless attested.
- **O-4:** only `NO_EDGE_FOUND` opens the baseline path.
- **O-5:** safety-relevant.
- **O-6:** public beacon after hashing. The mechanics in §2.0 are an AI
  default.
- **O-7:** G-2 absolute, 5 points.

**Still open** (left open by the D-14/D-15 addendum, FC7-3):
- **REG-1** Can a fixed-size rule be registered for C2, for example the
  owner's fixed 10%, which `s·τ/σ̂` with the restricted `σ̂` cannot express?
  If yes, Annex C C-10 needs a class and a G-11 treatment for it.
- **REG-2** May the signal `s` depend on `σ̂`? This bears on whether the
  sizing restriction in C-10 (1) can be bypassed.
- **O-6a** Which public channel carries the single declaration-hash post
  (§2.0). It posts a bare hash and reveals nothing about the strategies. If
  the owner wants no public post at all, O-6 is re-asked (trusted third
  party).

A proposal with two-model review comes first; then both items go to the
owner together.

## 8. Next

[AI default]
1. Write the REG-1/REG-2 proposal and have it reviewed; O-6a goes with them.
2. Ask the owner.
3. Run the D-19 calibration preregistration, which supplies the `<<D19>>`
   values and the certification route.
4. Run the two-model review of the final wording, including Annex C fidelity.
