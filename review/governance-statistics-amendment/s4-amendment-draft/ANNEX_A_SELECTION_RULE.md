# Annex A — selection rule (normative text for the amendment)

**Status:** AI-extracted copy for the §4 draft; not an amendment until the owner authors it.
Source: `d18-proposal/PROPOSAL.md` at `9718fdc` (owner-decided D-18 rev. 7), lines 184–360, copied verbatim. The amendments decided by the owner are the clauses at the end: A-B7 (B-7, `broadened-method/OWNER_DECISION_B.md`), A-U1 (U-1, `d19-preregistration/OWNER_DECISION_UPROC_SCOPE.md`) and A-V1 (D-20 partial, `d20-proposal/OWNER_DECISION_D20_V.md`). Citations such as FR-n/SR-n refer to the review records in `d18-proposal/`.

---

## 2. Proposed rule

Estimand: E-DIFF, the BTC candidate-minus-benchmark paired OOS return series;
`S` is its unannualized daily Sharpe (`METHOD_CANDIDATE.md:96`). D-08 must
adopt E-DIFF for the PBO alignment in O18-6. (FR2-7, FR2-8, FR3-8)

- **P18-0 Promotion eligibility (unseen data).** A cycle may nominate and
  promote only if its confirmation window is **eligible**: (i) the window has
  never been mounted in the research sandbox (§7a line 88), and no evaluation
  output of any kind (per-trial or family-level, §7a line 92) on any part of
  it existed before this cycle's declaration; (ii) it does not overlap any
  segment exposed to an earlier cycle, including exposed lockbox data rolled
  forward (protocol line 96, Constitution §7 line 81); and (iii) the window
  starts at least `max(label_horizon, embargo)` (= `embargo`, protocol line
  207) after the last observation mounted in the sandbox or evaluated by any
  process (cycle or exploration job, line 70), so luck selected at the end of
  seen data cannot carry into it; a window created after v1 is assigned at
  ingest to a partition never mounted in the sandbox; and (iv) for a window
  created after v1, the declaration timestamp precedes the window's first
  observation, so its data did not exist when the trial set was chosen (AI
  default, round 7; FR6-2). The `embargo` used for the gap is one value fixed
  before declaration from data outside the window (FR6-5). The v1 confirmation
  partition, on which no cycle has evaluated (C1 never started), is eligible
  for the first amended cycle (C2) with its first `embargo` dropped under
  (iii) (AI default, round 6 Q1; owner direction round 4 Q1); later cycles
  need a new window, which may take years to accrue (FR4-3). That the v1
  confirmation partition was never mounted in the sandbox is to be verified
  from the job log before C2 declares. The window id, its data manifest, its
  non-overlap with every exposed segment and the declaration timestamp are
  recorded in the hashed declaration. **Disclosed weakness:** market prices
  are public, and the v1 window (2022-01-01 to 2025-05-31) is history the
  declarers, including the owner, lived through, so strategies may be chosen
  knowing it. "Unseen" means never tested through the engine and its outputs,
  not unknown; the per-cycle bound for C2 therefore assumes selection
  independent of that window, which cannot be verified. This departs from
  `ADJUDICATION_10BB125.md` line 18 ("data that did not yet exist at
  declaration") for the v1 window only; windows after v1 meet it by (iv). (FR4-1, SR4-3,
  SR5-1, FR5-2, FR5-4) A cycle with no eligible window may research but has no
  pick and cannot promote. The frozen text governs how new data enters
  (Constitution §0 line 20 "Lockbox = future data", §7 lines 81 and 83,
  protocol lines 65–67, 96); assigning post-v1 data to an eligible
  confirmation window needs the amendment. (FR3-1, FR4-1, FR4-2, FR4-12,
  SR4-3)
- **P18-1 Declared trial set.** Before the first evaluation of the cycle, each
  family `f` (trend, volatility) declares its complete trial set `J_f` (every
  hypothesis and grid point), frozen by hash. In a cycle **without** an
  eligible window a family may instead be declared **not researched**
  (`|J_f| = 0`: no pick, `E_f = ∅`, excluded from the no-result target); in a
  cycle **with** an eligible window both families must be declared, because
  the window is used up for both (AI default, round 6 Q3; FR5-6). At least one
  family must be declared. A declared family is valid only if
  `1 <= |J_f| <= 80` (one slot of the family budget of 81, protocol lines
  184–189, read as per cycle under Constitution line 12 — to be confirmed in
  the amendment against lifetime accounting, line 190 (SR6-1, FR6-6) — is
  reserved for the re-run below; AI default, round 6 Q2;
  FR5-3), trial ids are unique and stable, and every trial carries a complete
  immutable configuration hash and belongs to `f`; this is checked before the
  cycle starts, and an invalid declaration prevents the cycle from starting.
  No trial may be added, removed or replaced later. **Automatic re-run**
  (owner direction round 5 Q2; mechanical per SR5-2): if an attempt ends
  without writing any result artifact (no metrics, report, partial result or
  stored output; the only thing visible to research is a fixed crash code, and
  crash diagnostics are kept from research), the system re-runs that trial
  exactly once, immediately, with the same declared hash and deterministic
  seed (protocol line 266), using the reserved slot; no person chooses whether
  or when. Only the first such crash in the family can use the slot. Any other
  failure (partial output, second crash, slot already used) is final for that
  trial. Every attempt, including the re-run, counts as an attempt (§9 line
  102, protocol line 292, lifetime accounting line 190) and is recorded. A
  declared trial counts from `EVALUATION_STARTED` (Constitution §0 line 13).
  (FR2-1, FR2-9, SR3-3, FR3-7, FR4-6, FR4-14, FR5-3, FR5-6, SR5-2)
- **P18-2 One shared pick and post-pick procedure.** There is exactly one
  nomination look per cycle, for all declared families together, at the
  earlier of: every declared trial has finished evaluation (completed, or
  crashed with its one rerun used or unavailable), or day 180. No promotion is
  possible before it. Proposed procedure after the pick, to be bound in the
  amendment: (a) the research phase ends at the pick; the cycle ends only when
  (b)–(d) complete, replacing the day-180 and `candidate_promoted` triggers of
  `cycle_termination` (lines 192–195); `all_family_trial_budgets_exhausted`
  is redefined as completion of the declared plan, because counting from
  `EVALUATION_STARTED` would fire it when the last trial starts; all three
  triggers are redefined, not removed, as Constitution §5 line 61 requires
  (calendar: day 180 plus the fixed post-pick window; promotion: recorded at
  (d)); the post-pick window must fit the lockbox cooldown (protocol line 75)
  for every nominee, and the amendment binds the precedence of a protocol
  change or invalidation after the pick (Constitution §3 line 45, §4 line 48)
  (FR5-5); (b) every nominee is processed
  through every gate, lockbox read and attestation (protocol line 300) in a
  fixed order, trend then volatility, and a promotion of one never stops
  processing of the other; (c) the post-pick window length is a fixed value
  set in the amendment; (d) the cycle outcome is recorded once, after all
  nominees are processed. Cycles with no eligible window, or with no result
  in every declared family, need outcome labels other than `NO_EDGE_FOUND`
  (Constitution §5 line 63, protocol line 195, §11 lines 113–116), which
  changes §5. If the cycle ends before the pick (protocol revision,
  invalidation), there is no pick and no promotion. (SR2-1, FR-1, SR3-1,
  SR3-2, FR3-6, FR4-4, FR4-5, SR4-6)
- **P18-3 Availability.** `A_f` = every trial in `J_f` was started and has
  exactly one completed evaluation (original or its one rerun) whose
  configuration hash matches the declaration, and for each: finite `S`, valid
  `T`, finite positive `D`, and (with a finite shared `S0`) finite pre-Φ `z`.
  A hash mismatch or a trial without a completed evaluation fails `A_f`; no
  such trial enters `V`. (FR4-7)
  The value `Φ(z)` is never used as an availability test. If `A_f` fails,
  nothing is nominated from `f` (family result `UNAVAILABLE`); one unavailable
  non-nominee blocks the family, which matches DEC-02 and is a deliberate cost
  (FR2-12). (SR-1, FR-7, FR3-5, SR3-6)
- **P18-4 Nomination.** On `A_f`, the nominated trial `J_f*` is the trial with
  the highest `S`, ties broken by lowest declared trial id; nomination depends
  only on the `S` vector and the ids. The reference implementation's exact
  float64 result decides near-ties, and the implementation must agree with
  the reference on the nominee's identity exactly (extends
  reconciliation lines 118–119). (FR2-10, SR-4)
- **P18-5 No fallback, no replacement.** Only `J_f*` may proceed. If it fails,
  or any gate is `UNAVAILABLE` or technically invalid, family `f` has no
  promotable trial this cycle; no other trial is nominated, and the line 74
  replacement allowance is not used. A technical failure is never a reason to
  nominate or re-read another trial. (FR-3, SR-5, SR2-8)
- **P18-6 DSR comparison.** The DSR pass test compares the pre-Φ statistic
  `z_f* = (S − S0)·sqrt(T−1)/sqrt(D)` (`METHOD_CANDIDATE.md:92`) of the
  nominee with **one global** decimal threshold `z_crit`, as `z_f* >= z_crit`
  in the reference implementation, with `z_crit` parsed from its decimal
  string to the nearest binary64; implementation and reference must agree on
  this pass/fail decision exactly. `z_crit` is fixed before qualification,
  analytically or from development replications only, then certified on
  held-out replications at that frozen value. Before any held-out replication
  is generated, the whole qualification object is frozen: method, generator,
  cell classifier, support boundary, confidence family, acceptance rule and
  `z_crit`. Any access to held-out results burns that seed namespace: any
  change to the object afterwards needs fresh held-out replications, and
  certification failure is never followed by re-tuning against the same set.
  It replaces `dsr.minimum: 0.95` (protocol lines 231, 287) by amendment. For
  the **current** method candidate in the large-T Gaussian model, the worst
  known cell needs `z_crit` of about 1.972 before margins; under the
  broadened method this figure must be recomputed (FR3-4, FR4-9). (SR2-2,
  FR2-2, FR3-3, FR3-5, SR3-4, SR4-5)
- **P18-7 Error and availability targets.** Under the all-zero-mean global
  null, `E_f = A_f ∩ {z_f* >= z_crit}` and `E = E_trend ∪ E_vol`. The
  calibration must show, in **every** preregistered qualifying cell, at a
  preregistered simultaneous confidence level covering every cell, family and
  bound:
  - a one-sided upper bound of `P_0(E_f) <= 0.025` for each family (so
    `P_0(E) <= 0.05` for any dependence between them); and
  - a one-sided upper bound `<= 0.01` on the whole-cycle **procedure
    no-result** event `U_proc`, in a simulated replication: any declared
    family whose `A_f` fails (P18-3), or any pre-lockbox mandatory gate of a
    nominee `UNAVAILABLE` or technically invalid (frozen `N/A` excepted;
    including PBO when enabled) (FR6-1). For `U_proc`,
    every pre-lockbox mandatory gate is computed for every nominee regardless
    of the DSR or other gate outcomes, and a gate not computed counts as
    `UNAVAILABLE` (FR5-1). The lockbox is read only after eligibility (line
    295; FR6-7); its availability is reported in power cells (FR4-15).

  Two events are kept apart (SR5-3). `U_proc` above is generated by
  the procedure in simulation, is the only event the 1% target applies to,
  and its denominator is simulated eligible cycle replications with at least
  one declared family. `U_ops` — no pick because of a protocol revision or
  invalidation, a crash that exhausts the automatic re-run, a hash mismatch,
  or any other infrastructure or governance failure — cannot be simulated, is
  not certified, and is counted and reported separately in operation over
  eligible, authorised real cycle attempts; it has no calibrated target. In
  operation **both** kinds are recorded, each failure with one exclusive cause
  code by a fixed precedence: infrastructure or governance cause first (then
  `U_ops`; an infrastructure-caused gate failure is `U_ops` only), otherwise
  procedure cause (`U_proc`-type, the real-world check on the calibration);
  a trial unfinished at day 180 is `U_ops` (timeout). The two can co-occur in
  one real cycle across families. (FR6-4, SR6-3) In
  calibration, crash and infrastructure failure are not modelled, so every
  simulated trial completes. Ineligible (research-only) cycles and undeclared
  families are excluded from both. The whole-cycle bound on `U_proc` needs
  joint (two-family) cells or a per-family allocation summing to at most 1%,
  chosen in D-19. A method failing either target does not qualify; error
  control cannot pass on unavailability. No-result replications stay in the
  denominator as non-events; `P_0(E_f | A_f)`, the reach-pick rate, and
  availability in power and mixed-null cells are also reported. (FR2-2,
  FR2-3, FR2-4, SR2-3, SR2-7, SR3-2, SR3-5, FR4-8, FR4-15, SR4-1, SR4-2)


---

- **A-B7 (owner decision B-7).** P18-0 has a fifth condition: (v) the window has `T >= T_min` complete UTC days of the E-DIFF series, where `T_min` is fixed in the D-19 development phase and frozen with the qualification object. Failing (v) makes the window ineligible; this is checked before computation and is not a `U_proc` event. The supported-law classifier named in D-18 O18-2 is specified in the D-19 preregistration, not in the method.
- **A-U1 (owner decision U-1).** P18-7's whole-cycle procedure no-result target of at most 0.01 applies to `U_proc^R`: the no-result event of the DSR method (including the supported-law classifier) and of gates G-1, G-2, G-4, G-10, G-12 and G-13, whose availability is simulated or proved deterministically. Gates G-3, G-5, G-6, G-7, G-8, G-11 and G-14 are excluded from the calibrated target; a fail-closed screen runs the actual trial set on simulated null data before the declaration is committed, and a set that fails it cannot be declared (no `m` spent). Their unavailability on the window is a procedure no-result event, recorded with its cause code, without a certified rate. `P_0(E_f) <= 0.025` per family is unchanged.
- **A-V1 (owner decision D-20, partial).** For P18-6's exact implementation/reference agreement, the DSR replicate Sharpes are computed by method V (`d20-proposal/V_BINDING.md` rev 3), and the reference is the set of frozen reference vectors: V's expected outputs and decisions for fixed inputs, recorded at the D-19 freeze and cross-checked against the Task 12 numerics (agreement required except on vectors designated near-degenerate before the freeze, where differences are disclosed). Every real evaluation reproduces the vectors bit for bit on the frozen runtime, computes its result with V, and also computes and reports the Task 12 numerics; if the decisions differ, V's result governs and the difference is disclosed. If the frozen runtime cannot be recreated, the evaluation is void and requires requalification.
