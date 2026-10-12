# Fable focused check of the D-18 proposal revision 6 at `52ef945` — NOT READY

Date: 2026-10-03. Focused check (revision 5 → 6 changes only) by the
Anthropic family for R19-2; the focused-check format was an AI default
(round 6 Q4, owner delegated drafting choices). Run in parallel with, and
without sight of, `SOL_REVIEW_52EF945.md`.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_52EF945.md` (committed `a722a0e`), prefix FR6.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR6-1 BLOCKER (no-result event); FR6-2..FR6-7 NON-BLOCKING.
  Nothing is decided by this record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

# Fable focused check of D-18 proposal revision 6 at `52ef945`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata my session reported; not checked against provider metadata.
**Commit reviewed:** `52ef945` (HEAD `a722a0e` adds only `REVIEW_PROMPT_52EF945.md`; `git diff --stat 52ef945 HEAD`). Scope: `git diff 0da82d3 52ef945 -- .../PROPOSAL.md` and the two revision-5 records. `SOL_REVIEW_52EF945.md` not read. Read-only: no edits, commits, pushes or network; no confirmation or lockbox data.
**Verdict: NOT READY.** One defect blocks the definition: FR6-1, a one-sentence fix. Top-Sharpe nomination with no fallback, `E_f = A_f ∩ {z_f* ≥ z_crit}`, `E = E_trend ∪ E_vol` and `F ⊆ E` remain correct. Binding verdict: `KEEP_BLOCKED` — the broadened method, the amendment and the calibration do not exist yet.

## Q1 — revision-5 findings

| ID | Status | Reason |
|---|---|---|
| FR5-1 | PARTLY | Gates now computed for every nominee; a gate not computed counts as `UNAVAILABLE`. The same rewrite dropped "technically invalid" (FR6-1). |
| FR5-2 | PARTLY; DEFERRED (owner) | Weakness disclosed in P18-0 and §3; departure from the adjudication recorded. Not yet shown to the owner; he confirms at the D-18 decision. Scope understated (FR6-2). |
| FR5-3 | PARTLY | Slot reserved (≤ 80 per family); exact arithmetic reproduces 0.614%, 14.96%, 0.016%. "Per-cycle" stated as fact citing lines 184–189, which do not say it (FR6-6). The re-run still helps only under the broadened method (O18-2). Cost to the 3×27 grid undisclosed (FR6-3). |
| FR5-4 | PARTLY | Gap now measured from any mounted or evaluated data and applies to v1. Embargo length not fixed; no boundary calibration cell (FR6-5). |
| FR5-5 | RESOLVED | Three triggers stated as redefined, not removed (§5 line 61); line-75 cooldown and §3 line 45 / §4 line 48 precedence named as amendment items. |
| FR5-6 | RESOLVED (disclosure) | Omission recorded; answered by an AI default that reverses an owner choice (FR6-3). |
| FR5-7 | RESOLVED in text | Chat text now quoted. That it was shown is UNVERIFIED (no committed chat record). |
| SR5-1 | DEFERRED (owner) | Sol's fix (remove the v1 exception) not adopted; it became a disclosed assumption the owner must confirm. I agree this does not block the definition of `E`, but the disclosure is too narrow (FR6-2). This is my position, not a rewrite of Sol's. |
| SR5-2 | RESOLVED | Re-run automatic: exactly once, immediate, first crash only, partial output final, every attempt counted and recorded. Residuals FR6-6. |
| SR5-3 | PARTLY | `U_proc` / `U_ops` split; 1% applies only to `U_proc`. "Disjoint" holds only across sample spaces (FR6-4); `U_proc` not exhaustive (FR6-1). |

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR6-1 | BLOCKER (no-result event) | P18-7 `U_proc` | Revision 5 counted any nominee gate "`UNAVAILABLE` or technically invalid"; revision 6 counts only "`UNAVAILABLE`". P18-5 (line 272) still lists "technically invalid" as a separate no-promotion state, which no frozen file defines (grep of Constitution and protocol: none); O18-5 lists only PASS/FAIL/N/A/UNAVAILABLE. SR4-1's own case: PBO technically invalid in every replication — no promotion ever possible, yet `U_proc` = 0% and the 1% passes. Second hole: the family list "`D <= 0`" misses `D = +inf`; P18-3 fails it ("finite positive `D`") but `z = 0` is finite, so it lands in neither event. | Since crashes are not modelled in simulation (line 319), define `U_proc` = any declared family whose `A_f` fails, or any pre-lockbox mandatory gate of a nominee `UNAVAILABLE` or technically invalid (frozen N/A excepted), in a simulated replication; or define technically invalid as a subset of `UNAVAILABLE` in both P18-5 and P18-7. |
| FR6-2 | NON-BLOCKING (owner-facing; fix before the owner confirms round-6 Q1) | P18-0 lines 180–196; §3 lines 338–340 | Revision 6 says the adjudication's rule ("data that did not yet exist at declaration") "applies only to windows after v1", and §3 limits the caveat to C2. But (i)–(iii) never require declaration before the window's first observation; the natural workflow — wait ~2 years for data, then declare — leaves every later cycle with the same public-history weakness, undisclosed. The operative gap is inherited from revision 5; the overclaim is new (protocol item 5 sweep). | Proposal to author and owner: add "(iv) for windows after v1, the declaration timestamp precedes the window's first observation", or extend the disclosure to every cycle. A design choice, not an edit. |
| FR6-3 | NON-BLOCKING (labelling) | §0 round 6; §5 | The Q3 default reverses the owner's round-5 Q3 selection ("Yes, allow it — avoids token strategies") without saying so or that it restores the filler incentive he rejected. The Q2 default (≤ 80) removes the line-186 design of three 27-trial grids (3×27 = 81). §5 asks the owner to confirm Q1 "in particular", not Q2 and Q3. "The owner declined to answer the round-6 questions" conflicts with "(not shown to the owner)". | State that Q3 reverses round-5 Q3 and give the Q2 grid cost; have the owner confirm all four defaults; say whether the questions were shown. |
| FR6-4 | NON-BLOCKING | P18-7 lines 311–321 | Not disjoint in real cycles: a trend crash exhausting the re-run can co-occur with a volatility `D <= 0`. In operation, procedure no-results are recorded nowhere (`U_ops` lists only operational causes; `U_proc` exists only in simulation), yet they are the only real-world check on the calibration. A trial unfinished at day 180 is unclassified. | Record both kinds in operation with a precedence rule; classify the day-180 timeout explicitly. |
| FR6-5 | NON-BLOCKING | P18-0(iii); O18-7 | Protocol line 207 defines embargo as `max(label_horizon, target_autocorr_cutoff)`, which varies by strategy and is data-estimated; the window gap needs one value fixed before declaration from data outside the window. Trimming the v1 confirmation partition (line 66) is missing from O18-7's scope. No boundary cell yet (FR5-4). | Bind in the amendment; add the boundary cell to the D-19 grid. |
| FR6-6 | NON-BLOCKING (defer to broadened method or amendment) | P18-1 re-run | After a re-run the counted trials (§9 line 102) total `|J_f|+1` while calibration uses `|J_f|` (line 319); the cell classifier or `S0` must handle this. The crash code is a confirmation-to-sandbox channel beyond §7a line 92. Lines 184–189 do not say per-cycle; Constitution line 12 ("current-cycle and lifetime trial accounting") supports it and is uncited. | Cite line 12; put the crash-code channel and the count mapping into O18-2 and O18-7. |
| FR6-7 | NON-BLOCKING (referent) | P18-7 "(line 296)" | Protocol line 296 is `descendant_retry_same_cycle_after_fail`; "allowed_only_after_eligibility" is line 295 (index blob at `52ef945`; `i/lf w/lf`, so line numbers are portable). Inherited from my own family's revision-5 record: FR5-1's proposed text at `FABLE_REVIEW_0DA82D3.md:58` gave 296. | Change to line 295. |

## Q3

The selection rule and `E` are READY. The no-result event is NOT READY because of FR6-1. FR6-2 and FR6-3 do not change `E`, but must be fixed before the owner confirms the round-6 defaults.

## Protocol items run

1 (citations both ways): every changed citation resolves except line 296 (FR6-7); search by topic found Constitution line 12 uncited (FR6-6). 2 (referents): FR6-7; FR5-x and SR5-x tags match their records. 3 (bytes): no hashes recorded; PROPOSAL `i/lf w/lf eol=lf`; protocol `i/lf w/lf -text`. 4 (discriminating reproduction): 0.614% vs 14.96% vs 0.016%, plus "80 with no re-run" 14.79%. 5 (sweep): public-history argument across post-v1 windows gives FR6-2. 6 (right answer, wrong reason): "per-cycle" defensible but backed by the wrong lines. 7 (tooling): no frozen-path diff over `0da82d3..52ef945`; tests/lint N/A for Markdown. 8 (exact arithmetic): `Fraction`. 9: nothing repaired. 10 (self-descriptions): FR6-3 (shown vs not shown). 11 (inheritance): FR6-2's gap and FR6-7 inherited; FR6-1 new in revision 6. 13 (§16 scope): correctly stated (O18-7).

**Owner/statistician decisions remaining:** FR6-1 wording; whether later windows must be declared before their data exists (FR6-2); the four round-6 defaults (FR6-3); embargo value (FR6-5); D-16/D-17 count (deferred).
**Still not authorized:** closing D-18, amendments, frozen edits, calibration, governed trials, confirmation or lockbox access, promotion, deployment, trading.

## Summary for the owner

1. The core rule (test only the best strategy, no second try) is correctly defined.
2. One phrase was lost in the rewrite: a check that produces an "invalid" result must count as "no result", or a broken check looks harmless.
3. The "weaker because you lived through the data" warning is not only about the first cycle; later cycles have it too unless strategies are declared before the new data exists.
4. Three of the AI's default answers change things you chose earlier (forcing both families, capping at 80 so no longer three full 27-strategy grids, using the 2022–2025 data); confirm all of them, not just the last.
5. After those fixes the definition can be decided; nothing becomes active until the method, the amendment and the calibration exist.
