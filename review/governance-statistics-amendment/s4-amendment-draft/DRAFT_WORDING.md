# Constitution §4 amendment — draft wording for C2 (DSR and selection)

**Status:** `AI WORDING PROPOSAL — NOT AN AMENDMENT — NOT AUTHORED — NOT SIGNED — NOT ACTIVE`
**Date:** 2026-10-03, revision 2
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). Constitution §4 line 50:
an AI "may propose but not author/merge/activate/self-approve amendments".
This file only proposes wording; the amendment exists only if the owner
adopts it as his own text and makes the signed, dated commit (§4 line 48).
**Basis:** owner decisions D-18 (`../d18-proposal/OWNER_DECISION_D18.md`,
rev. 7 `9718fdc`) and B-1..B-7 (`../broadened-method/OWNER_DECISION_B.md`,
design rev. 3 `a3d2c59`); scope D-18 O18-7 and design §7.
**History:** revision 1 `e44146e`; reviews Fable FA1 SOUND WITH FIXES, Sol SA1
UNSOUND (`2ecf18f`); adjudication `ADJUDICATION_E44146E.md` (`ff3c7f8`).
Revision 2 applies every disposition there.
**Labels:** `[AI default]` = drafting choice, not an owner decision.
`[derived]` = follows from decided rules. `<<OWNER O-n>>` = owner decision
still needed (list in §6). `<<D19: x>>` = value only the D-19 calibration can
supply. `<<DECLARATION: x>>` = value computed at C2's declaration.
`<<OPEN D-nn>>` = clause governed by an open decision row. **The amendment
cannot be signed while any `<<…>>` marker remains.** The annex hashes are those of
the revision-2 drafts and are recomputed at activation.

## 0. Structure and activation

The amendment consists of: Constitution v1.1 changes (§1), protocol v1.1 for
cycle C2 (§2), and two normative annexes that the protocol binds by hash:

| Annex | Content | SHA-256 (LF, as committed) |
|---|---|---|
| `ANNEX_A_SELECTION_RULE.md` | D-18 rev. 7 §2 (P18-0..P18-7) verbatim, plus clause A-B7 (owner decision B-7) | `836adec7a40c8d0b494352e71116752ea577dd3403d59b0c8769a2445d388480` |
| `ANNEX_B_DSR_METHOD.md` | broadened method rev. 3 §2.1–§2.6 verbatim | `80ad6b785de337568e806d6feda9168f2ec9b07aed2d8e1e5c14c955ff2b25d0` |

Annex text wins over any summary in §1–§2. On activation [AI default]: new
files `docs/RESEARCH_CONSTITUTION_v1.1.md`, `protocols/protocol_v1.1.yaml` and
the two annexes under `specs/`, each with a SHA-256 sidecar, beside the
preserved, unchanged v1.0 files; their `-text` entries are added to
`.gitattributes` **before** hashing; and the `FROZEN_HASHES.json` additions
are made in the owner's signed activation commit, as an append that changes no
existing entry (FA1-16).

## 1. Constitution v1.1 — clause changes

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| header l.2, 5, 8 | `Research Constitution v1.0`; effective 2026-09-11; content hash | `v1.1`; effective = activation date; content hash recomputed per `HASH_CANONICALIZATION_v1.md` |
| §0 new, after l.19 | — | "Eligible confirmation window = a confirmation segment meeting every eligibility condition of the selection rule frozen with the cycle protocol. A cycle may nominate and promote only on an eligible window; a protocol may add conditions but not remove them." |
| §5 l.61 | "Every cycle protocol must define family-budget exhaustion, calendar/time limit, and candidate-promotion termination. Otherwise invalid." | unchanged, plus: "When the protocol has a single nomination look, budget exhaustion means completion of the declared plan, and termination follows the protocol's post-nomination procedure." |
| §5 l.63 | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `PROTOCOL_REVISION`, `INVALIDATED`." | "Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `RESEARCH_ONLY` (no eligible window; no nomination possible), `NO_RESULT` (eligible cycle with no result in every declared family: the family is unavailable, or a mandatory pre-lockbox gate of its nominee is unavailable or technically invalid), `PROTOCOL_REVISION`, `INVALIDATED`." [AI default: label names]. Whether `RESEARCH_ONLY` or `NO_RESULT` opens the deployable-baseline path of §0 l.17 / §11: `<<OWNER O-4>>` |
| §5 l.67 | "Prior-cycle results are not pooled into later DSR/PBO matrices; lifetime trial counts persist." | "... lifetime trial counts persist: they are recorded and reported with every result, and do not enter the DSR score." (B-2) |
| §7 new, after l.81 | — | "An exposed segment rolled into confirmation is never part of an eligible confirmation window." |
| §7a l.92 | "Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation." | "... and, for a trial attempt that wrote no result artifact, one fixed crash code. Crash diagnostics stay outside the sandbox." (O18-7) |
| §8 new, after l.97 | — | "A cycle's complete trial set is declared and hashed before its first evaluation; no hypothesis or grid point is registered into that cycle afterwards." (P18-1) |
| §9 l.104 | "All failures count. Lifetime family accounting persists." | "All failures count, including every automatic re-run attempt (P18-1). Lifetime family accounting persists as recorded and reported counts (B-2)." |
| §9 l.106 | "If no frozen effective-count method exists, raw count is used." | "The frozen DSR method uses no effective trial count. Raw current-cycle and lifetime counts are recorded and reported with every result." (B-1) |
| §9 new, after l.106 | — | "False-promotion allowance: the m-th eligible cycle, counted from the first cycle declared on an eligible window, has a whole-cycle allowance of 0.05 / 2^(m−1), split equally between families. Every finite lifetime total is below 0.10, and the limit is 0.10. A cycle protocol may set a smaller allowance, never a larger one." (B-5; FA1-1, SA1-8). Which cycles increment `m`: `<<OWNER O-1>>` |
| §27 l.194 | "Promotion-relevant artifacts must reproduce from recorded hashes/seeds or are void." | "... from recorded hashes/seeds, including the family seeds of the frozen DSR method, or are void." |

Not changed in v1.1 (FA1-5, SA1-5): §0 l.20, §7 l.81 and l.83. C2 uses only
the v1 confirmation partition. Admitting post-v1 data to confirmation needs
a later amendment, before C3, which decides the assignment rule in advance
of the data (FA1-6).

## 2. Protocol v1.1 (cycle C2) — clause changes

`protocol_version: "1.1"`, `cycle_id: "C2"`, `constitution_version: "1.1"`,
every bound hash recomputed. v1.0 key paths and schema-required keys are kept
(`schemas/protocol.schema.json` l.28, l.95; FA1-12). Lines not listed carry
over unchanged, **except** that every line in §3 carries an `<<OPEN D-nn>>`
marker.

### 2.1 Partitions and embargo (v1.0 lines 64–67, 205–214)

```yaml
partitions:                                   # keys unchanged
  exploration: {start: "2017-08-17T00:00:00Z", end: "2021-12-31T23:59:59Z"}
  confirmation:
    start: <<DECLARATION: 2022-01-01T00:00:00Z plus gap_embargo, as an exact UTC timestamp>>
    end: "2025-05-31T23:59:59Z"
  lockbox: {start: "2025-06-01T00:00:00Z", end: "2026-08-31T23:59:59Z"}
selection_rule:
  annex: "ANNEX_A_SELECTION_RULE.md"
  sha256: "836adec7a40c8d0b494352e71116752ea577dd3403d59b0c8769a2445d388480"
  c2_window: "v1 confirmation partition; eligible only if the job log shows it was never mounted in the sandbox and never evaluated (P18-0)"
  t_min_days: <<D19: T_min>>                  # A-B7: eligibility, checked before computation
gap_embargo:
  rule: "max over declared horizons of max(label_horizon, target_autocorr_cutoff), in whole days, computed once before declaration from data outside the window"
  value_days: <<DECLARATION: computed value>>
  # validation.embargo (v1.0 lines 205-214) is unchanged and still governs folds
```

[AI default] "data outside the window" is P18-0's wording; for C2 that data
is exploration data, because nothing later has been mounted.

### 2.2 Declaration and budget (v1.0 lines 184–190, 292)

```yaml
trial_accounting:                             # key unchanged
  trend_budget: 81                            # 80 declared + 1 automatic re-run slot
  volatility_budget: 81
  budget_scope: "per cycle"                   # [derived] P18-1, B-2; Constitution §0 l.12
  lifetime_accounting: "recorded and reported; not in the DSR score"   # B-2
  declaration: "Annex A P18-1"
promotion:
  trial_budget_hard_stop: "no evaluation outside the declared set and its re-run slot"
```

### 2.3 Nomination, lockbox and termination (v1.0 lines 74, 192–195, 251, 300)

```yaml
nomination: "Annex A P18-2 to P18-5"
lockbox_policy:
  max_evaluations_per_family_per_cycle: 1     # was 2; P18-5 no replacement
validation:
  configuration_selection:
    value: "each grid point is one fixed trial; no per-fold reselection; the nominee is chosen by Annex A P18-4; DSR, PBO and plateau account for selection"
cycle_termination:                            # keys kept; meanings redefined (Constitution §5 l.61)
  calendar_days_elapsed: 180                  # nomination look at the latest; then post-nomination window
  post_nomination_window_days: <<OWNER O-2: recommended 75>>
  ends_when_any:
    - "all_family_trial_budgets_exhausted"    # = declared plan complete AND post-nomination procedure done
    - "calendar_days_elapsed"                 # = day 180 + post_nomination_window_days
    - "candidate_promoted"                    # recorded once, after every nominee is processed
    - "protocol_revision"
    - "cycle_invalidated"
  outcomes: ["CANDIDATE_PROMOTED","NO_EDGE_FOUND","RESEARCH_ONLY","NO_RESULT","PROTOCOL_REVISION","INVALIDATED"]
  recorded_times: ["declaration","plan_exhaustion","nomination_look","each_gate_and_lockbox_read","outcome"]   # SR6-2
post_nomination_procedure:
  order: "trend nominee, then volatility nominee; a promotion of one never stops processing of the other"
  per_nominee: "every mandatory pre-lockbox gate is computed; only a nominee that is ELIGIBLE (Constitution §13) requests a lockbox read; then attestation with 72 h cooling-off (line 300)"
  lockbox_cooldown_days: 30                   # line 75, applied between the two families' reads [AI default]
  calendar_cap_vs_unprocessed_nominee: <<OWNER O-2>>
  revision_or_invalidation_after_look: <<OWNER O-3>>
  before_look: "no nomination and no promotion"
```

### 2.4 DSR method and error budget (v1.0 lines 223–233, 266, 287)

```yaml
validation:
  bootstrap:
    type: "stationary_block"
    block_method: "politis_white"
    iterations: 2000
    added_purposes: ["dsr_family_max_null"]   # existing purposes, incl. the lockbox interval (line 85), unchanged
  dsr:
    series: "BTC candidate_minus_VOL_TARGET_BUY_AND_HOLD paired OOS return series (E-DIFF), complete UTC days"
    method: "aqt.dsr.bootstrap_max.candidate.v2"
    annex: "ANNEX_B_DSR_METHOD.md"
    sha256: "80ad6b785de337568e806d6feda9168f2ec9b07aed2d8e1e5c14c955ff2b25d0"
    family_block_rule: <<D19: largest or median>>
    minimum: "replaced by z-test: Annex A P18-6"   # key kept
    z_crit: <<D19: z_crit_1, certified on held-out replications at alpha_1>>
    effective_trial_count_method: "none"      # B-1; replaces line 232
    fallback: "none"                          # B-1; replaces line 233
  random_seed_policy:
    trial: "SHA256(protocol_hash,hypothesis_hash,trial_index) -> deterministic seed"   # unchanged
    family: "Annex B §2.4"
error_budget:
  eligible_cycle_index_m: 1                   # if C2 is eligible; Constitution v1.1 §9
  alpha_whole_cycle: 0.05
  alpha_per_family: 0.025
  procedure_no_result: "U_proc <= 0.01, Annex A P18-7; allocation <<D19: joint cells or per-family split>>"
  calibration_events: "Annex A P18-7 (event, denominator, simultaneous confidence family, U_proc/U_ops split, cause-code precedence, day-180 timeout)"
promotion:
  dsr_minimum: "Annex A P18-6"                # key kept; was 0.95
```

The support classifier is not protocol text. It belongs to the D-19
preregistration that certifies `z_crit` (A-B7).

## 3. Clauses carried over but still blocked

Each line below carries over with the marker shown, and is not operative
until the row is decided and its wording is inserted (FA1-3, SA1-7):

| v1.0 lines | Clause | Marker |
|---|---|---|
| 263–265, 286 | plateau pass rule | `<<OPEN D-04, D-05>>` |
| 201–204, 280–282 | fold unit, paired fold win rate | `<<OPEN D-06, D-07>>` |
| 234–241, 288 | PBO matrix, ranking, observation unit, ties | `<<OPEN D-08, D-09, D-10>>` (D-08 must adopt E-DIFF, D-18 O18-6) |
| 74–92 (except 74), 294–296 | lockbox prediction, attestation fields, pass rule | `<<OPEN D-11, D-12>>` |
| 134–140, 289 | random-exposure null pass event | `<<OPEN D-14>>` |
| 267–268, 284–285 | delay hard gates | `<<OPEN D-15>>` |
| 42–44, 279, 283 | ETH sanity gate and 2x cost stress estimand | `<<OPEN D-02>>` (no decision record found) |
| 274–275 | paired 90% CI and BTC lower bound estimand | `<<OPEN D-03>>` (no decision record found) |
| bootstrap-backed clauses (this draft binds one) | reference-vector review | `<<OPEN D-20>>` (matrix line 80 is now stale) |

## 4. Rationale, as §4 requires (the owner writes the final words)

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
> from the supported kind of return series. For C2 they assume that the
> strategies were chosen independently of 2022–2025 prices, which are public
> and which the declarers lived through; this cannot be verified.
> Infrastructure failures are counted, not certified. No human statistician
> reviewed this; two different AI model families did, and two revisions were
> finished without a further check.

## 5. §4 and §16 checklist (owner steps, in order)

1. Fill every `<<…>>` marker: D-19 preregistered, run and accepted; rows in §3
   decided, or the owner explicitly keeps those gates blocked; owner items
   O-1..O-5 answered.
2. Two different-model reviews of the final wording, records committed
   (R19-2). If the owner edits the reviewed text materially, it is re-reviewed.
3. Classify the amendment as safety or not (`<<OWNER O-5>>`). If safety: no
   open incident or post-HALT cooling-off (§4 l.56), and the 72-hour minimum
   activation delay (§4 l.52).
4. Version bump of the Constitution and protocol, and the written rationale
   (§4 l.48).
5. C1 is formally terminated with outcome `PROTOCOL_REVISION`, after
   checking that no C1 trial ever started (§4 l.48 "cycle termination").
6. The owner authors the text and makes the signed, dated commit; history is
   preserved (§4 l.48).
7. §16-protected code is merged only after a different-model review and the
   owner's PR review. That includes the DSR/promotion gate, protocol
   enforcement (declaration hash, budget stop, automatic re-run, eligibility
   and `T_min`, crash-code channel), lockbox access tooling (one read per
   family), and the validation engine.
8. Activation happens before C2's declaration (§4 l.48), following the §0
   activation steps.
9. No retroactive effect: confirm that no promotion is open (§4 l.48).

## 6. Owner items (asked together when the text is near signable)

- **O-1** Which cycles count toward `m`. Recommendation: every cycle declared
  on an eligible window, whatever its outcome (conservative).
- **O-2** Post-nomination window length and calendar-cap precedence.
  Recommendation: 75 days; if the cap arrives first, an unprocessed nominee
  is not promoted, recorded as `U_ops`.
- **O-3** Precedence of a protocol revision or invalidation after the look.
  Recommendation: it ends processing; no promotion; the outcome is the
  revision or invalidation (§4 l.48 "no retroactive effect" protects only
  promotions already attested).
- **O-4** Whether `RESEARCH_ONLY` / `NO_RESULT` may use the deployable-baseline
  path. Recommendation: no; only `NO_EDGE_FOUND` does.
- **O-5** Safety classification. Recommendation: treat as safety-relevant
  (72 hours, incident check).

## 7. Next

[AI default] A focused re-check of revision 2 by both model families, then
the D-19 calibration preregistration, which supplies the `<<D19>>` values.
