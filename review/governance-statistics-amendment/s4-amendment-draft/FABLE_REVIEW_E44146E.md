# Fable review of the §4 amendment draft rev1 at `e44146e` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `e44146e`) with `{{PREFIX}}` = `FA1`.
- Model metadata: the reviewer reports `claude-fable-5-1`, read from its session
  metadata. The subagent transcript file was empty when this record was written, so the
  recorder could not check that ID independently; the `fable` override is the
  recorder's observation.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

# FA1 review: §4 amendment draft wording, revision 1

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — model ID taken from session metadata, not chosen by me.
**Commit reviewed:** `e44146e` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md`.
**Verdict (prompt scale):** **SOUND WITH FIXES** — usable as a starting text only after the four BLOCKERs below are repaired (BLOCKER here = must be fixed before the owner authors; not a rejection of the approach).
**Verdict (skill scale):** `REVISION_REQUIRED` for the draft; promotion stays `KEEP_BLOCKED`.

**Method.** Read-only. Read the decided basis named in the prompt, the full Constitution and protocol, `schemas/protocol.schema.json`, the D-row matrix and `.gitattributes`; read no other review of this draft. Mandatory checks: **1, 2** (citations both directions; resolution) — every cited line resolves correctly; topic search found the uncited clauses in FA1-11/12/14/15/16. **3** (line endings) — not applicable to the draft's own content (it records no hashes); applied to the activation plan (FA1-16). **4, 8** (exact arithmetic, discriminating) — `Fraction`: halving allowances 1/20, 1/40, 1/80…; seven cycles sum to 127/1280 = 1/10 − 1/1280, versus 7/20 for flat 5% — discriminating; v1 confirmation window 1,247 days. **5** (self-application) → FA1-2, FA1-6. **6** (right answer, wrong reason) → FA1-17. **7** (tooling) — not applicable, no verifier exists for wording. **11** (inherited) — marked in-table. **13** (§16 scope) — not triggered by this Markdown draft; triggered by its implementing code (FA1-15).

## Findings

| ID | Sev. | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FA1-1 | BLOCKER | §2.4 `error_budget`; §1 (missing) | **B-5 binds only C2.** The decided halving schedule appears only in `protocol_v1.1` (`cycle_id: "C2"`); a protocol governs one cycle (§5 l.59), so a C3 protocol could reset α = 0.05 without any amendment, defeating "<0.10 lifetime". `z_crit_m: one value per allowance level` demands infinitely many values, so the draft's own "no placeholder may remain" can never be met. "m-th eligible cycle" undefined for an eligible cycle ending PROTOCOL_REVISION/INVALIDATED/NO_RESULT. | OWNER_DECISION_B l.41–46; draft l.24–25, l.146–148 | Put the schedule in Constitution v1.1 (e.g. a §9 sentence); proposal for the owner to confirm as his reading of B-5: m increments at the declaration of every cycle on an eligible window, whatever its outcome. Protocol v1.1 binds only `z_crit_1` (1/20 whole cycle, 1/40 per family). |
| FA1-2 | BLOCKER | §2.4 `dsr` | **Named-but-unfrozen method.** `aqt.dsr.bootstrap_max.candidate.v2` is named with a compressed definition only — the defect the rationale (l.164) indicts in v1.0. Missing: `u_j`/`psi_j` definitions, PW routine and cap `min(T, ceil(min(3√T, T/3)))`, `B−1`, fsum/two-pass in replicate order, reason-code order and consequence (UNAVAILABLE; U_proc vs U_ops), replicates never dropped, family-seed canonical form (UTF-8, sorted keys, no whitespace), stream purpose/asset/cost multiplier. §27 l.194 reproducibility cannot be met. | DESIGN §2.2–§2.5 | Freeze a method spec (SHA-256 sidecar) and bind its hash in protocol v1.1, or write it inline. |
| FA1-3 | BLOCKER | §0 l.24–26; §4 step 1; §5 | **Open D-rows are not actually marked.** §0 claims D-05/06/08/11/14/15 appear as placeholders; no `<<OPEN D-nn>>` exists in §1–§2. Gate lines carry over unchanged, so a mechanical "no placeholder remains" check passes with those rows open; step 1's "gates kept blocked by explicit text" refers to nothing. | draft l.53–55, 175–177 | Put placeholders at the affected protocol lines (42–44/279/283; 77–78; 83–92; 134–140/289; 234–241; 263–265; 274–275; 280–282; 284–285). |
| FA1-4 | BLOCKER | §3 rationale | **Overclaim.** "caps false promotion at 5%… lifetime total stays under 10%" omits the owner-accepted weaknesses: C2 assumes selection independent of public 2022–2025 prices; the bound is conditional on simulated cells, not a real-market guarantee; global null only; U_ops uncertified; rev 7/rev 3 unrechecked. | PROPOSAL §3 l.370–378; OWNER_DECISION_D18 l.52–55; Constitution §1 l.29 | Reword as conditional; list the accepted weaknesses. Owner's text. |
| FA1-5 | NON-BLOCKING | §1 row §0 l.20 | **§0 l.20 left unchanged** ("Lockbox = future data") while a new sentence sends future segments to confirmation; P18-0 says this assignment "needs the amendment" citing l.20. A confirmation window placed after lockbox data also strains §7 l.81 ("lockbox boundary only moves forward"). Not needed for C2. | PROPOSAL l.222–226; O18-7 | Amend l.20, or defer all post-v1 data entry to the C3 amendment. |
| FA1-6 | NON-BLOCKING | §2.1 `new_data_assignment` | **Assignment at ingest is a choice made on public prices**: the assigner sees the path and can choose lockbox vs confirmation, against P18-0 (iv)'s pre-existence logic. The `<<OPEN: owner, before C3>>` also violates the draft's own §0 rule. | draft l.67–69, 76–78 | Require a calendar rule fixed before the data exist; owner decision, not AI default; move out of the C2 text. |
| FA1-7 | NON-BLOCKING | §2.1 `embargo_days` | **Embargo ambiguity / beyond the decided rule.** (a) Listing line 207 as changed ("now evaluated once") can change the walk-forward/CPCV fold embargo (l.205–214); O18-7 scopes only the gap embargo. (b) Horizon combination and hours→daily-lag reconciliation undefined (168 h: max(7, ≤28) ≤ 28 days). (c) "exploration data only" narrows P18-0's "data outside the window", unmarked. (d) `start:` is an expression, not a timestamp. | P18-0; FR6-5 | Keep `validation.embargo` unchanged; add a separate gap key = max over declared horizons; record the computed timestamp. |
| FA1-8 | NON-BLOCKING | §1 §0-new; §2.4 `minimum_days` | **Eligible-window definition loose.** "As defined by the cycle protocol" lets a protocol redefine it; "seen data" is vaguer than P18-0 (iii) ("mounted… or evaluated by any process"); B-7's T ≥ T_min is an eligibility (pre-computation, non-U_proc) condition but sits only in `dsr` with no consequence; no operative "only eligible windows may nominate/promote"; hashed-declaration contents (window id, manifest, non-overlap, timestamp) missing. | OWNER_DECISION_B l.47–48; DESIGN §2.5 | Reword with P18-0's operative clauses; move T_min into eligibility. |
| FA1-9 | NON-BLOCKING | §2.2–§2.4 | **Decided details missing:** P18-1 (≥1 family; 1 ≤ \|J_f\|; unique stable ids; config hashes; family membership; invalid declaration prevents start; no removal/replacement; counting from `EVALUATION_STARTED`); SR6-2 separate plan-exhaustion time; P18-4 reference-float64 near-ties and exact nominee agreement; P18-6 exact pass/fail agreement; P18-7 U_ops separate reporting, exclusive cause-code precedence, day-180 timeout = U_ops; O18-5 gate list with PASS/FAIL/N/A/UNAVAILABLE behaviour (U_proc depends on it). | PROPOSAL §2, §4 | Add, or bind by reference to a frozen spec. |
| FA1-10 | NON-BLOCKING | §1 §5 l.61; §2.3 | **Calendar cap vs the new §5 sentence.** "Ends only after the post-nomination procedure completes" contradicts the hard `day_180_plus_post_nomination_window` trigger (e.g. a nominee awaiting the owner's APPROVE_AS_IS at day 255). The 75 days assume the 30-day cooldown applies across families. Inherited from P18-2. | P18-2(c) | Owner precedence decision; proposal: the cap wins, no promotion for an unprocessed nominee, recorded as U_ops. |
| FA1-11 | NON-BLOCKING | §1 §5 l.63 | **NO_RESULT narrower than decided; §11 unaddressed.** "Every declared family unavailable" is narrower than P18-2's "no result in every declared family" (which includes a nominee gate UNAVAILABLE/invalid). Whether RESEARCH_ONLY/NO_RESULT opens the deployable-baseline "NO_EDGE_FOUND path" (§0 l.17; §11 l.113–116) is unaddressed, though P18-2 cites §11. | PROPOSAL l.275–278 | Widen the definition; the baseline-path question is the owner's. |
| FA1-12 | NON-BLOCKING | §2.2–§2.4 | **Frozen schema conflict.** `schemas/protocol.schema.json` l.28 requires `trial_accounting` and l.92–98 require `cycle_termination.calendar_days_elapsed`; the draft drops the latter, introduces `trial_budget`, and moves `validation.*`/`promotion.*` keys to top level — with "lines not listed carried over", keys are duplicated or orphaned. Inherited: neither O18-7 nor DESIGN §7 lists schemas. | schema text | Keep v1.0 key paths (e.g. `calendar_days_elapsed: 180` with the redefined meaning), or add a schema amendment to the scope. |
| FA1-13 | NON-BLOCKING | §2.4 `bootstrap.purposes` | **Purposes list omits the carried-over lockbox prediction-interval bootstrap** (l.85); read as exhaustive, it contradicts it. | protocol l.83–86 | Add it, or mark the list as additions (D-11 open). |
| FA1-14 | NON-BLOCKING (part QUESTION) | §0, §5 | **Open-row list incomplete.** D-20 triggers "once any bootstrap-backed clause is bound" (matrix l.72) and this draft binds one (DESIGN §2.4, reference vectors I-10); matrix l.80 ("only two bootstrap-backed rows") is now stale. **QUESTION:** D-02/D-03/D-04/D-07 (promotion-gate estimands, matrix l.34–36, 39) have no recorded response I found — decided? §0 and §5 lists differ. Inherited (OWNER_DECISION_D18 l.63). | matrix | List D-20; owner/recorder to confirm D-02..04/07 status. |
| FA1-15 | NON-BLOCKING | §4 checklist | **Checklist incomplete.** "Version bump" and "written rationale" (§4 l.48) are not explicit owner steps; step 5 names only the promotion gate, but §16 also enumerates protocol-enforcement logic (declaration hash, budget stop, re-run, eligibility/T_min, crash-code channel), lockbox ACL tooling (single read per family, ingest assignment) and the validation engine; if treated as a safety amendment, §4 l.56 (no open incident) applies. "C1 never started" — read, not verified. | Constitution §4, §16 | Add these steps. |
| FA1-16 | NON-BLOCKING | §0 activation plan | **Activation process gaps.** (a) Adding entries to `FROZEN_HASHES.json` edits a preserved file — state the process. (b) The proposed paths are not covered by `.gitattributes` (`git check-attr`: `text: unspecified`; `core.autocrlf=true` here; existing `-text` lines name specific paths), so recorded hashes would not be portable. | `.gitattributes`; check-attr output | Add `-text` entries before hashing; owner process. |
| FA1-17 | NON-BLOCKING | AI defaults | **Mislabelled/unmarked defaults.** `budget_scope: per cycle` is right but not a free choice: it is forced by P18-1 (80+1, owner-confirmed), B-2, and "later cycles need a new window" (a lifetime reading exhausts the budget after C2). Unmarked AI choices: exploration-only embargo, `purposes` list, key renames, T_min placement, m-counting. | — | Relabel as derived; mark the unmarked. |
| FA1-18 | NON-BLOCKING | §2.3 `after_nomination…` | **OPEN precedence has no decider/process.** §4 l.48 ("no retroactive effect on open promotions") bears directly on it. | FR5-5 | Name it as an owner decision in checklist step 1. |
| FA1-19 | NON-BLOCKING | §1 §9 l.104 row; §0 | **Citation errors.** "including every automatic re-run attempt" is credited to B-2 (source is P18-1); "§27 line 196" is self-referential hashing, not hash tooling. | — | Fix citations. |

## AI defaults (question 4)

| Default | Classification |
|---|---|
| New files, not in-place edits | Drafting choice; FROZEN_HASHES/attributes steps are owner process (FA1-16) |
| The two label names | Drafting choice |
| New-data proportion left open | Owner decision, mislabelled as AI default (FA1-6) |
| `budget_scope` per cycle | Derived from decided rules (FA1-17) |
| 75-day post-nomination window | A drafting value under P18-2(c), but because it sets the §5 l.61 calendar limit the owner must confirm it together with the cap precedence (FA1-10) |
| 72-hour wait | Conservative drafting; the safety-amendment classification is the owner's (FA1-15) |
| Reviewer pair | Process drafting |

## Still open for the owner

The B-5 counting rule, the cap precedence, the after-nomination precedence, the NO_EDGE baseline path, the new-data rule (C3), and the status of D-02..04/07.

## Remains unauthorized

Frozen-file edits, activation, any cycle/trial/confirmation/lockbox access, calibration, code, promotion, trading. This review accepts and signs nothing; the owner authors the amendment himself; any later §16-protected code needs a different-model and the owner's review before merge.

## Plain-language summary

1. The draft follows your decisions closely, but four things must be fixed before you adopt it.
2. Your "halve the risk each new cycle" rule sits only in cycle 2's rulebook, so later cycles could quietly ignore it — it belongs in the Constitution.
3. The new scoring method is named but not fully written down — the same flaw the draft criticises in v1.0.
4. The open decisions (D-05 and others) are not actually marked in the text, so a "nothing left blank" check would wrongly pass.
5. The explanation overstates the safety: 5% is a tested estimate under assumptions you accepted, not a guarantee, and should say so.
