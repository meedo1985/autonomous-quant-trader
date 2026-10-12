# Fable focused check of the D-18 proposal revision 5 at `0da82d3` — NOT READY

Date: 2026-10-03. Focused check (revision 4 → 5 changes only) by the
Anthropic family for R19-2, chosen by the owner in round 5 ("Fix, quick
check, then decide"); run in parallel with, and without sight of,
`SOL_REVIEW_0DA82D3.md`.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_0DA82D3.md` (committed `eaa8a14`), prefix FR5.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR5-1 BLOCKER (no-result event); FR5-2..FR5-7 NON-BLOCKING.
  Nothing is decided by this record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

# Fable focused check of D-18 proposal revision 5 at `0da82d3`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata my session reported; not checked against provider metadata.
**Commit reviewed:** `0da82d3` (HEAD `eaa8a14` adds only `REVIEW_PROMPT_0DA82D3.md`; `git diff --stat 0da82d3 HEAD`). Scope: `git diff 10bb125 0da82d3 -- .../PROPOSAL.md` plus the three revision-4 records. `SOL_REVIEW_0DA82D3.md` not read. Read-only: no edits, commits, pushes or network; no confirmation or lockbox data.
**Verdict: NOT READY.** The only blocker on the definition is FR5-1, fixable in one sentence. Top-Sharpe nomination with no fallback, `E_f = A_f ∩ {z_f* ≥ z_crit}`, `E = E_trend ∪ E_vol` and `F ⊆ E` are correct and complete, including `E_f = ∅` for an undeclared family. Binding verdict: `KEEP_BLOCKED` — the broadened method, the amendment and the calibration do not exist yet.

## Q1 — revision-4 findings

| ID | Status | Reason |
|---|---|---|
| FR4-1 | RESOLVED | P18-0(i) covers evaluation output of any kind; eligibility is in the hashed declaration; the public-price residual is disclosed. |
| FR4-2 | RESOLVED (citations); DEFERRED (route) | Cites §0 line 20, §7 lines 81, 83, §7a line 88; partition assignment of new data left to the amendment (O18-7). |
| FR4-3 | RESOLVED in text | "Shown to the owner before round 5" has no quoted record (FR5-7). |
| FR4-4 | DEFERRED (amendment) | P18-2 names the need for new outcome labels and the §5 change. |
| FR4-5 | RESOLVED | Budget trigger redefined as declared-plan completion, citing §5 line 61; residual FR5-5. |
| FR4-6 | RESOLVED as owner choice | The stated benefit does not hold (FR5-3). |
| FR4-7 | RESOLVED | `A_f` total: started, exactly one completed evaluation, matching hash; trigger defined. |
| FR4-8 | RESOLVED | Only procedure-generated no-results certified; joint cells or allocation in D-19; ineligible cycles excluded. |
| FR4-9 | RESOLVED | 1.972 relabelled as current-candidate-specific. |
| FR4-10 | RESOLVED | Sentence corrected. |
| FR4-11 | RESOLVED | Correction recorded. |
| FR4-12 | PARTLY | Gap only for post-v1 windows and only against data evaluated by an earlier cycle; no calibration cell added (FR5-4). |
| FR4-13 | DEFERRED (owner, to broadened-method design) | Round 5 Q4; O18-3. |
| FR4-14 | RESOLVED as owner choice | Consequence not shown (FR5-6). |
| FR4-15 | RESOLVED as reporting; DEFERRED (D-19) | Rates reported, no target. |
| SR4-1 | PARTLY | Gate states in the numerator, but evaluation order undefined, so Sol's scenario survives (FR5-1). |
| SR4-2 | RESOLVED | Denominator defined; exogenous cancellations monitored separately. |
| SR4-3 | PARTLY | Custody record added; selector information disclosed as a residual, not bound; historical v1 window declared eligible (FR5-2). |
| SR4-4 | DEFERRED (O18-2) | Explicit rule: no D-19 qualification before the method is specified and reviewed. |
| SR4-5 | RESOLVED | P18-6 freezes the whole qualification object; any access burns the held-out namespace. |
| SR4-6 | PARTLY; DEFERRED (amendment) | Order, non-stopping and single outcome bound; window length, gate/lockbox sequencing and post-pick event precedence open (FR5-5). |
| SR4-7 | RESOLVED | §3 carries the conditional wording. |

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR5-1 | BLOCKER (no-result event) | P18-7, P18-5, O18-5 | The no-result event counts "any mandatory gate of a nominee `UNAVAILABLE` or technically invalid" but never says whether gates are computed for a nominee that already failed DSR. A gate not computed is neither `UNAVAILABLE` nor invalid. If gates short-circuit after a failure, a gate's unavailability is counted only in null replications where `E_f` occurs. PBO is enabled only for families of ≥ 20 trials (line 235). Calculation (current method, large-T Gaussian, independent trials, `z_crit = 1.972`, `V` treated as independent of the max — overstates): `P_0(E_f)` ≈ 0.225% at N=20 and 0.058% at N=81, against ≈2.5% in the N=2 worst cell. So an **always**-unavailable PBO adds at most ≈0.45% per cycle and passes the 1% target — SR4-1's exact scenario. | Add: "For the no-result event, every pre-lockbox mandatory gate is computed for every nominee regardless of the DSR or other gate outcomes; a gate not computed counts as `UNAVAILABLE`." The lockbox is read only after eligibility (line 296), so its availability is reported in power cells (FR4-15). |
| FR5-2 | NON-BLOCKING (does not change `E`; owner-facing) | P18-0 "v1 confirmation partition ... is eligible"; §3 | Q2: textually the partition qualifies — no cycle has evaluated it (`OWNER_DECISION.md:10`), matching the owner's round-4 Q1 option ("promotion after cycle 1 waits for fresh data"). Never-mounted-in-sandbox is UNVERIFIED (the record attests only no evaluation-start artifact). But: (a) `ADJUDICATION_10BB125.md:18` accepted a stricter fix ("data that did not yet exist at declaration") and revision 5 departs from it without recording the departure; (b) the window, 2022-01-01 to 2025-05-31 (1,247 days), is public history the declarers know, including the owner, whose own trading rule is a candidate hypothesis — SR4-3's scenario, rated BLOCKER by Sol; the round-4 corrections shown to the owner omit it; (c) §3's "each calibration cell is a fixed design" omits the residual. | Add SR4-3's residual to the corrections shown to the owner; record the departure from the adjudication; add the caveat to §3; owner confirms that C2 may promote on v1 confirmation knowing this. |
| FR5-3 | NON-BLOCKING (decision framing) | P18-1 rerun; round 5 Q2 | The rerun counts against the budget (§9 line 102, line 292). With 81+81 declared — the option text's case — no rerun is possible: crash no-result risk stays **14.96%** at p = 10⁻³ (exact `Fraction`). Comparators: 80+80 with one rerun slot per family 0.614%; a rerun per trial with no budget limit 0.016%. Under the current method any abort fails `A_f` anyway (O18-2), so the rerun helps only if the broadened method tolerates counted attempts exceeding completed evaluations. "Family budget" is ambiguous between per-cycle and lifetime (line 190, `lifetime_accounting: true`). | Show the owner both limits; define which budget applies. |
| FR5-4 | NON-BLOCKING | P18-0(iii) | The rule's own rationale (luck at the end of seen data carries into the next days) applies to v1 confirmation, which starts immediately after mounted exploration with no gap — ≈7 of 1,247 days at a 168-hour horizon, magnitude UNVERIFIED. (iii) also measures the gap only from data evaluated by "any earlier cycle", omitting sandbox exploration jobs between cycles (line 70). `max(label_horizon, embargo)` = `embargo` (line 207). | Measure the gap from the last data mounted or evaluated by any process; state whether v1 is exempt and why; add a boundary calibration cell (FR4-12). |
| FR5-5 | NON-BLOCKING (sweep, protocol item 5) | P18-2(a), (c) | §5 line 61 is invoked only for the budget trigger, but revision 5 also *replaces* the calendar and `candidate_promoted` triggers, and line 61 requires both defined. Satisfiable (180 days plus a fixed window; termination after all nominees processed) but must be stated. Uncited by topic: line 75 (30-day lockbox cooldown — the post-pick window must fit two lockbox reads); §3 line 45 (mid-cycle protocol change); §4 line 48 (no retroactive effect on open promotions — revision or invalidation after the pick). | Amendment states the triggers are redefined, not removed, and binds the cooldown and post-pick event precedence. |
| FR5-6 | NON-BLOCKING (owner-facing) | P18-1 opt-out; round 5 Q3 | Eligibility is per cycle (P18-0(i)). A trend-only C2 exposes the v1 window for volatility too; volatility cannot promote until a new window accrues, plausibly more than 2 years (FR4-3). The option text did not say so. | Show the owner. |
| FR5-7 | NON-BLOCKING (self-description) | §0 round-4 corrections | "Shown to the owner before round 5": unlike every other round, no question or text is quoted (FR2-13), and no committed record other than this proposal and the reviews contains it. | Quote what was shown, or delete the claim. |

## Q3

The event `E` and the selection rule are READY. The no-result event is NOT READY until FR5-1 is fixed. FR5-2..FR5-7 do not change `E`; FR5-2 and FR5-3 should be shown to the owner before he adopts P18-0 or P18-1 with the definition.

## Protocol items run

1 (citations both ways): all cited lines resolve as claimed (Constitution 13, 20, 61, 63, 81, 83, 88, 92, 102, 113–116; protocol 65–67, 74, 96, 192–195, 207, 231, 266, 287, 292, 300); search by topic found uncited protocol 75, 190, 296 and Constitution 45, 48. 2 (referents): §-numbers match headings. 3 (bytes): no hashes recorded; `PROPOSAL.md` `i/lf w/lf eol=lf`. 4 (discriminating): 14.96% vs 0.614% vs 0.016%; 0.23% vs ≈2.5%. 5 (sweep): §5 line 61 argument across all three triggers (FR5-5). 6 (right answer, wrong reason): v1-eligible conclusion matches the owner's choice; justification omits SR4-3. 7 (tooling): no frozen-path diff over `10bb125..0da82d3`; tests/lint N/A for Markdown. 8 (exact arithmetic): rerun figures in `Fraction`; FR5-1 quadrature is an approximation, not calibration. 9: nothing repaired. 10 (self-descriptions): FR5-2(a), FR5-7. 11 (inheritance): FR5-1 is new, introduced by the SR4-1 fix; FR5-2 continues the round-4 option text. 13 (§16 scope): correctly applied.

**Owner/statistician decisions remaining:** gate-evaluation convention (FR5-1); C2 eligibility given selectors' knowledge (FR5-2); rerun and budget scope (FR5-3); v1 boundary gap (FR5-4); D-16/D-17 count (deferred).
**Still not authorized:** closing D-18, amendments, frozen edits, calibration, governed trials, confirmation/lockbox access, promotion, deployment, trading.

## Summary for the owner

1. The core rule (check only the best strategy, no second try) is correctly defined.
2. One sentence is missing: every safety check must run even after a strategy fails, or a broken check can look harmless.
3. The first new cycle may promote on 2022–2025 data, which you and the researchers have lived through as public history; that weakens the 5% claim and you should confirm it knowingly.
4. The "one re-run" rule does nothing if you declare the full 81 strategies per family, because the re-run would exceed the budget.
5. Researching only one family in the first cycle uses up the unseen data for the other family too, possibly for years.
