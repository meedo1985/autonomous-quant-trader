# Fable review of the D-18 proposal at `690fa97` — UNSOUND as written

Date: 2026-10-03. First of the two different-model reviews required by R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); reviewers chosen by the
owner ("Fable 5.1 + Sol High").

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_690FA97.md` (SHA-256
  `7a6a8503e6c7cb7623f7bf4301645714006917914de4a9a9d516d5cb58183551`), prefix FR.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR-1..FR-4 BLOCKER (FR-4 on decision framing); FR-5..FR-13
  NON-BLOCKING; FR-14 QUESTION. Nothing is decided by this record; no finding
  is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

# Fable review of the D-18 proposal at `690fa97`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata observed in this session.
**Commit reviewed:** `690fa97` (HEAD `00dac52` adds only `REVIEW_PROMPT_690FA97.md`).
**Verdict: UNSOUND as written.** The §3 core identity is correct; the bound claim on the whole gate fails under the frozen cycle mechanics. Statistical-binding verdict: `REVISION_REQUIRED`; D-18 stays `KEEP_BLOCKED`.
Read-only: nothing edited, committed, or pushed; no network; no confirmation/lockbox data.

## Answers to the five questions

**Q1 — identity correct, conditionally.** For a fixed family snapshot with every score available and finite, and with the ranking taken on the same values compared to 0.95, `{DSR_J* ≥ 0.95} = {max_J DSR_J ≥ 0.95}` holds for any tie rule (S0 is shared). It breaks when: (a) the score changes with look time (FR-1); (b) NaN — Python `max([nan, 0.99])` returns `nan`, while `max([0.99, nan])` returns `0.99`, so non-finite values must become unavailable before the max (FR-8); (c) Φ saturates — in double precision `Φ(8.3) = Φ(12) = 1.0`, so ranking on Φ breaks ties by ID, not by the larger statistic (E unaffected; identity of the submitted trial affected, FR-8).

**Q2 — the inequality holds only as a set inclusion for a fixed look and a fixed family.** It survives mixed nulls (but the global-null calibrated number does not transfer, FR-6), unavailable trials (if E is defined to require all scores available, FR-7), and PBO (an extra AND). It fails across looks, families, and the frozen replacement candidate (FR-1, FR-2, FR-3). The stated reason is wrong: false promotion ⊆ E holds under *any* rule that requires the submitted trial to pass DSR, fallback included, so P18-2 is not what produces the bound (FR-4).

**Q3 — labelling incomplete.** `protocol_v1.yaml:74` ("One primary and one replacement candidate") is a governing clause the proposal does not cite, and P18-2 contradicts it (FR-3). `cycle_termination` (lines 192–195) has no outcome for a failed single submission (FR-2). The PBO ranking metric (line 240) models a Sharpe-ranked selector, not a DSR-ranked one (FR-5). A section 4 amendment is needed, and its scope must include line 74 and lines 192–195.

**Q4 — O18-1..O18-5 are not complete.** Missing: the look schedule (FR-1); per-family versus per-cycle scope of E and how families combine (FR-2); disposition of the replacement candidate (FR-3); the denominator of E and the treatment of attempts without a return vector (FR-7); the ranking key and parity of the selected trial (FR-8); the selector mismatch with PBO and S0 (FR-5); non-Gaussian, correlated calibration cells (FR-12).

**Q5 — "top DSR scorer, no fallback" is neither the strictest option nor the simplest to calibrate.** Top-Sharpe, no fallback guards E_S ⊆ E: it is stricter and consistent with PBO and S0; its cost is failing a cycle in which another trial passes DSR. Top-DSR (P18-1) is always at least as powerful and admits more null passes at the same 0.95 threshold (exact example below). Fallback keeps the same bound E; its real cost is that the downstream gates (CI, null percentile, lockbox) are applied more than once and lose their single-test meaning — lockbox retries are already capped by line 74 and Constitution §7 line 85. The real benefit of no fallback is that each downstream gate is applied once, to one trial fixed in advance; the proposal does not state this reason.

## Calculations

All deterministic, in memory, `.venv/Scripts/python.exe -B -`.

A(2) = 0.519755, A(3) = 0.852804, A(27) = 2.029601, A(81) = 2.455554; z_c = 1.6448536.

- **Example 1 (look time).** Same trial: T = 1247, S = 0.115, √V = 0.028, g = 0, k = 3. At N = 27: S0 = 0.056829, z = 2.0466, DSR = 0.9797, **pass**. At N = 81: S0 = 0.068756, z = 1.6270, DSR = 0.9481, **fail**. The outcome depends on when selection happens.
- **Example 2 (mixed null, one realization).** N = K = 3, T = 365, null trial 1 with S1 = 0.10, g = 0, k = 3. If the other two have realized S = 0.0: S0 = 0.049237, trial 1 DSR = 0.833, **fail**. If the other two are truly positive with S = 0.099 and 0.101, g = −1, k = 40: S0 = 0.000853; scores 0.9704, 0.9567, 0.9594; the selected trial is **null trial 1** — a false promotion.
- **Example 3 (exact `Fraction` arithmetic; E strictly contains E_S).** T = 365, K = 2. X: S = 0.088, k = 40; Y: S = 0.0875, k = 1.2; both g = 0. Even with S0 = 0, z_X² = 2.6209 < 2.7055 < z_c², so X, the top-Sharpe trial, fails. Even with S0 = 0.001, z_Y² = 2.7225 > 2.7056 > z_c², so Y passes. Actual S0 = 0.000184. Inclusion: if DSR at J_S ≥ 0.95 then max_J DSR_J ≥ 0.95, so E_S ⊆ E.

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR-1 | BLOCKER | P18-1, P18-3 | The selection time is undefined. Frozen text allows a cycle to end mid-way on `candidate_promoted` (protocol line 194); trials are counted at evaluation start (§9 line 102), so N, K and V grow during the cycle. An operator who submits at the first look where max ≥ 0.95 makes false promotion ⊆ ∪_t E_t, not E. Example 1. | Bind one preregistered look, or a finite look schedule calibrated as a union. Add as O18-6. |
| FR-2 | BLOCKER | P18-1 "family" vs P18-2 "cycle" | Two family budgets (protocol lines 184–189). A per-family E_f does not bound the cycle: P(false promotion) ≤ P(∪_f E_f). Astra already said this (`ASTRA_REVIEW_597DDC8.md:208`, "cross-family or lifetime"). Whether one family's failure ends the cycle is unspecified, and lines 192–195 have no matching outcome. | Owner decides the scope and the cycle termination after a failed submission. |
| FR-3 | BLOCKER | P18-2, O18-5 | Frozen `lockbox_policy.max_evaluations_per_family_per_cycle: 2`, justified "One primary and one replacement candidate" (line 74), is not cited, and P18-2 forbids that replacement. Under the frozen text there are two submissions per family, so the bound must cover both. Constitution §7 line 85 bars only descendants. The omission is shared with the method candidate and the decision matrix. | Add line 74 to the amendment scope. Owner decides: repeal the replacement, or calibrate a two-submission union. |
| FR-4 | BLOCKER (decision framing) | Owner direction text; §3 | "Strictest" is false: E_S ⊊ E (Example 3). "Simplest to calibrate" is overstated: false promotion ⊆ E under fallback too. The conclusion that E is a valid upper bound is right; the reason given ("because P18-2") is wrong. | Give the owner the corrected comparison (Q5) before the D-18 decision. |
| FR-5 | NON-BLOCKING | P18-1 vs protocol lines 240, 251 | PBO ranks by `paired_delta_sharpe`, and S0 is the expected maximum *Sharpe*; neither models selection by DSR. Line 251's "family DSR/PBO/plateau account for selection" no longer holds literally for PBO. | Disclose in O18 and in the amendment rationale; owner decides. |
| FR-6 | NON-BLOCKING | §3, O18-1 | The inclusion holds for any data-generating process, but a global-null calibration does not bound mixed nulls (Example 2). Whether the probability rises is `UNVERIFIED`; Example 2 is one realization, not a probability. | O18-1 should state that no mixed-null bound is claimed. Add mixed-null challenge cells using the event {selected trial is null and passes}. |
| FR-7 | NON-BLOCKING | O18-2 | E must mean "all required scores available AND max ≥ 0.95", with unavailable replications kept in the denominator (DEC-02's availability event). An attempt without a return vector counts in N_lifetime but not in K. With the owner's lifetime-count choice (D-17) and the method candidate supporting only equal counts (DEC-01), any abort or prior-cycle attempt makes the family unavailable, so nothing can ever be submitted. | Bind with AS-3 and P-7. |
| FR-8 | NON-BLOCKING | P18-1 ties | Φ saturates to exactly 1.0, and a `max` over NaN depends on input order. The rule that reference and implementation must agree exactly (reconciliation lines 118–119) must extend to the identity of the selected trial. | Rank on the pre-Φ statistic or state the key; convert non-finite values to unavailable before the max. |
| FR-9 | NON-BLOCKING | P18-1 "fixed before…" | Unenforceable: each trial's evaluation computes all of its metrics (§7a line 92). "Submitted candidate" also clashes with the §0 definition of a Candidate (a hypothesis that has *passed* eligibility). | Restate as "selection is a function of the DSR score vector and trial IDs only"; call it the "nominated trial". |
| FR-10 | NON-BLOCKING | P18-2 gate list | "OOS/IS ratio" has no frozen threshold (it appears only at protocol lines 245–249); "intervals" is vague. | List the gates explicitly from protocol lines 90–91 and 270–292. |
| FR-11 | NON-BLOCKING | O18-3 "(Astra AS-2)" | Wrong referent. AS-2 (Astra line 303) concerns the matched-N lemma; the "no lifetime bound shown" statement is at line 208, which also says "cross-family". New defect in this proposal. | Cite line 208 instead. |
| FR-12 | NON-BLOCKING | Calibration for option C | Reasoning, not computed: under the DEC-02 baseline's Gaussian independent generator, sample skew and kurtosis stay near 0 and 3, so the top-DSR and top-Sharpe trials almost always coincide. The property that motivates D-18 appears only in heavy-tail cells, which the baseline treats as non-qualifying. R19-5 also shows results depend on correlation between trials. | Option C needs qualifying non-Gaussian, correlated cells. |
| FR-13 | NON-BLOCKING (inherited) | `HUMAN_DECISION_MATRIX.md:65` | D-18's authority is `STAT` only, while lines 63–64 give `STAT` then §4. O18-5 is correct. The matrix is committed. | Owner decides whether to correct the matrix. |
| FR-14 | QUESTION | Dependency order | Matrix §7 says D-18 requires D-16, which is not closed. The definition of E does not depend on D-16; its calibration does. | Does the owner accept deciding D-18 first? |

## Verification protocol items run

1 (citations both ways): found protocol line 74, lines 192–195 and 184–189, Constitution §0 and §7 line 85, Astra line 208. 2 (referents): found FR-11 and FR-13; matrix line 65 and protocol line 251 point where claimed. 3 (bytes): the proposal records no hashes; `git ls-files --eol` shows `i/lf w/lf attr/text eol=lf`, so line endings are attribute-protected. 4 (discriminating reproduction): Examples 1 and 3 each show the alternative treatment giving a different decision. 5 (sweep the argument across options): the inclusion argument applied to fallback and top-Sharpe (FR-4). 6 (right answer, wrong reason): FR-4. 7 (verifiers): frozen-hash verifier not applicable; `690fa97` and `00dac52` touch only `review/`. 8 (exact arithmetic): Example 3. 11 (inherited defects): FR-3 and FR-13 inherited; FR-11 new. 13 (§16 scope): not applicable to this Markdown proposal; §16 governs any later promotion-gate or protocol-enforcement code implementing P18.

**Remaining owner decisions:** look schedule; per-family or per-cycle scope; disposition of the line 74 replacement; top-Sharpe versus top-DSR selection; denominator and no-return-vector attempts; ranking key; section 4 amendment scope.
**Still not authorized:** closing D-18; any amendment or frozen edit; a calibration engine or simulations; governed trials; confirmation or lockbox access; promotion; deployment; trading.

## Plain-language summary for the owner

1. The proposal's core logic is right: if you may submit only the top DSR scorer, "it passes" and "anything passes" are the same event.
2. But the safety bound assumes one fixed moment of choice; the rules let you choose mid-cycle, when passing is easier.
3. Your protocol already allows a second "replacement candidate" per family, and the proposal never mentions it.
4. There are two strategy families per cycle, so two chances, and one family's bound does not cover both.
5. You were told "top scorer, no fallback" is strictest; it is not — "top Sharpe, no fallback" passes fewer no-edge strategies.
6. You were told it is simplest to calibrate; a fallback has the same calibration target.
7. The real benefit of no fallback is that the later checks are each applied once, so they keep their meaning.
8. Nothing here is accepted or activated; these points go to you and the second reviewer before you decide D-18.
