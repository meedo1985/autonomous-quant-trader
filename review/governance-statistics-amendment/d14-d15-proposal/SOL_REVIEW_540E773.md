# Sol High review of the D-14/D-15 proposal rev3 at `540e773` — SOUND WITH FIXES

Date: 2026-10-03. This is the OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10281-ee05-7f20-8c15-c01512792f0b`;
  tokens used 188,370; exit 0. (The reviewer's self-report names only "GPT-5 family". The CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R3.md` (committed `540e773`), with `{{PREFIX}}` = `SN3`
  (substituted file SHA-256 `41877f5b928c33f4488a27ebf315af5efd06c7004de604244d9ffffb3e2090c5`).
- The reviewer's final message follows verbatim:

---

Model: **Codex, OpenAI GPT-5 family**; the exact runtime model ID is not exposed to me.  
Commit reviewed: **`540e7739ea5500a782bd0255a2535fd6a7cbc390`**; clean worktree, and the target was last changed at this commit.  
Verdict: **SOUND WITH FIXES**. The central pre-sizing-signal construction is sound, but the proposal is not yet executable or decision-ready.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SN3-1 | BLOCKER | `PROPOSAL.md` §1.2, lines 45–58; §5 Q1 | A hypothesis has an hourly or stateful market signal that cannot be factored into one daily nonnegative signal times inverse hourly volatility. Revision 3 would prohibit it from C2, not merely make G-11 unavailable. | Constitution §8 line 97 requires an exposure mapping but not this separable form; protocol line 55 explicitly enables hourly signal evaluation. The algebra is workable for the stated class, but “changes §8 practice” understates a new C2 eligibility restriction. | Either make the form a preregistered **G-11 applicability** contract, with `N/A` outside the class, or explicitly ask the owner to amend C2 hypothesis eligibility. Define the canonical signal interface, units, timing, normalization, and hash. |
| SN3-2 | BLOCKER | §1.3–1.4 and §1.6 | Two conforming implementations can generate different shifts or availability results. | `g` is undefined; `d+k mod T` is ambiguous for one-based days; the deterministic option does not state `i=0,…,499`; `T` is not defined as complete UTC days; warm-up/missing-bar validity is not fully bound; and revision 3 omits METHOD_CANDIDATE §6.2’s rule that any unavailable null draw makes the gate unavailable with no replacement. `statistics.py:173–200` also makes zero variance and insufficient observations unavailable. | Define `g`, `T`, indexing, `i`, `τ`’s domain, complete-day/input validity, permitted warm-up provenance, all statistic failures, and “any unavailable draw ⇒ gate `UNAVAILABLE`; denominator remains 500; no replacement.” |
| SN3-3 | BLOCKER | §1.2 lines 70–85; §1.6 lines 135–143 | Candidate and all 500 draws tie. | Plus-one and rank-475 fail because zero draws are strictly below. But type-7 gives `q₀.₉₅=x`, and the proposed `candidate >= q₀.₉₅` **passes** at equality. Therefore “all 500 tie, and the gate fails,” “pure-sizing trials always fail,” and the global tie statement are false under one offered rule. | State consequences separately for each pass rule. If ties must fail, remove type-7, change it to strict `>`, or add an explicit tie rejection—while recording that this changes the matrix’s proposed event. |
| SN3-4 | NON-BLOCKING | §1.4; §5 Q4 | The owner selects seeded versus deterministic shifts while the exclusion width remains an embedded AI default. | The 30-day floor is disclosed as unsupported, but §5 does not ask whether to accept it or how `g` is obtained. Seed policy line 266 supplies a seed, not an RNG/permutation/sampling algorithm; the draft correctly recognizes a D-20 dependency. | Add separate choices for the source of `g`, the 30-day floor, and near-identity exclusions. Leave exact random-stream mechanics explicitly blocked on D-20. |
| SN3-5 | NON-BLOCKING | §2.1 | Exposure changes between decision and delayed fill, or the first 00:00 decision occurs with an unset clock. | The revised ordering resolves the revision-2 cancellation defect and matches frozen lines 55–61, but it does not expressly say that an order stores an absolute target exposure or that an unset clock permits the first increase. | Add those two sentences. Retain fill-before-decision, held-exposure comparison, filled-increase clock, and end-of-window cancellation. |
| SN3-6 | BLOCKER | §2.3 lines 200–205; §5 Q9 | G-6 and G-7 could stress different ETH components, but the draft offers one combined “ETH legs stressed / baseline” choice. | The option does not separately bind, for each gate, the ETH candidate inputs/execution, ETH benchmark inputs/execution, and ETH drawdown path. Protocol line 279 fixes 1x **cost**, but does not itself settle feature or execution delay. | Ask separate G-6-ETH and G-7-ETH questions and enumerate candidate, benchmark, cost multiplier, execution, features, and drawdown semantics for each. |
| SN3-7 | NON-BLOCKING | §2.4; §5 Q10 | The owner chooses bounded degradation when baseline improvement is unavailable or chooses an unconstrained `θ`. | The draft governs only a nonfinite stressed statistic. It does not define `θ`’s domain or what happens when unstressed `E-IMPROV` is unavailable. | Require finite stressed and unstressed statistics, define the unavailable outcome, and bind a domain such as `0 ≤ θ ≤ 1` if that is the intended interpretation. Keep `θ` a separate statistical choice. |
| SN3-8 | NON-BLOCKING | §1.2 lines 81–86 | “Frozen `N/A`” may be read as already frozen governance. | The current amendment draft lists G-11 with `na: "never"`; this proposal instead means an applicability result fixed at preregistration. | Rename it **“preregistered `N/A`”** and explicitly label it amendment-required. |

### Direct answers

**1. Construction and declaration**

Yes—the new construction removes the specific revision-1 and revision-2 sizing-estimator misalignment at the target-exposure level.

Exact two-day examples, calculated with `fractions.Fraction`:

- Vol-family trial with nonconstant signal: let `s=[1,1/2]`, `τ=2/5`, own estimator `σ̂=[1/2,1]`, and benchmark target `[3/5,3/5]`. The candidate is `[4/5,1/5]`. Shifting and re-sizing the signal gives `[2/5,2/5]`, whose own-estimator-normalized values are `[1/2,1]`, exactly the shifted signal. Shifting either full exposure or the candidate/benchmark ratio gives `[1/5,4/5]`, normalized as `[1/4,2]`: the old defect.

- Trend trial at target `0.80`: let its signal be `[1,1/2]`, its estimator `[1/2,1]`, and the 0.60 benchmark `[1,3/5]`. The candidate is `[1,2/5]`. Signal shifting gives `[4/5,4/5]`, normalized as `[1/2,1]`. Ratio shifting gives `[2/3,3/5]`, normalized as `[5/12,3/4]`. Thus the redesign also fixes the clipping-driven defect away from target 0.60.

This proves alignment with the trial’s current-hour estimator; it does not prove exchangeability, realized exposure/turnover matching, or error calibration. The declaration is workable only for separable daily-signal strategies and is not fully or correctly labelled as a universal C2 requirement; see SN3-1.

**2. Domain, state, shifts, statistic and pass rules**

- The stated numerical checks and initial state are directionally correct but incomplete under SN3-2.
- With `i=0,…,499`, the deterministic formula yields 500 distinct shifts exactly when `T−2m≥499`: `D=498` produces 499 unique values; `D=499` produces 500.
- Seeded sampling without replacement has the same cardinality boundary, but exact reproducibility remains a D-20 matter.
- `E-IMPROV` and `E-DIFF` are the two relevant registered statistic choices. The L-1 disclosure is correct: with one shared benchmark, ranking `E-IMPROV` is exactly ranking candidate Sharpe.
- Plus-one’s conditional continuous-exchangeability pass probability is correctly `25/501 ≈ 0.049900`; rank-475 gives `26/501 ≈ 0.051896`.
- The design does not establish exchangeability, and the proposal correctly avoids claiming an error rate.
- The type-7 tie behavior is wrong as described and materially changes the pure-sizing consequences; see SN3-3.

**3. Delay contracts**

The §2.1 event contract resolves the substantive revision-2 ambiguity: due fills occur first, rules inspect held exposure, only an emitted order replaces a pending order, and the clock records actual filled increases. That matches frozen lines 55–61 and the frozen next-open/additional-bar semantics. SN3-5 contains two small clarifications needed for a fully mechanical state machine.

The §2.2 feature-delay contract is executable: it selects the cached value last emitted by the baseline pipeline at or before `t−1h`, leaves refits and non-market state unchanged, and fails closed on missing/nonfinite inputs. The amendment should ensure every stateful derived input is declared as either a lagged market-derived input or unchanged non-market state.

**4. Neutrality and completeness**

The G-5, G-6 and G-7 benchmark choices are substantially more neutral: §10 is evidence rather than a purported answer, and G-5’s frozen ETH-at-1x requirement is preserved. The combined ETH choice remains incomplete under SN3-6.

Survival versus bounded degradation is a legitimate high-level choice, and the draft accurately discloses that survival can tolerate large deterioration. Bounded degradation remains underspecified under SN3-7.

Section 5 is not complete: it omits independent acceptance of the universal declaration restriction, the 30-day exclusion floor/source of `g`, the type-7 tie consequence, and separately bound G-6/G-7 ETH semantics.

### Revision-2 finding dispositions

| Finding | Status | One-line disposition |
|---|---|---|
| FN2-1 | RESOLVED | Current-hour own-estimator sizing removes the ratio-null estimator misalignment; pure-sizing treatment is now an owner choice. |
| FN2-2 | RESOLVED | Fill-before-decision, held exposure, actual-fill clock, and replacement eligibility resolve the cancellation defect. |
| FN2-3 | PARTLY | G-5’s 1x ETH cost rule and neutral §10 reading are fixed, but G-6/G-7 ETH semantics remain bundled. |
| FN2-4 | RESOLVED | Realized matching is disclaimed, line 137 is targeted, and tolerance matching is offered. |
| FN2-5 | RESOLVED | The false constant-multiple claim was removed. |
| FN2-6 | RESOLVED | L-1 and `E-DIFF`’s relationship to the departure P&L are disclosed. |
| FN2-7 | PARTLY | Random versus deterministic shifts is exposed, but `g` and the unsupported 30-day floor are not owner choices. |
| FN2-8 | RESOLVED | The false N-1 `T≥840` attribution is replaced by the correct D-19 dependency. |
| FN2-9 | RESOLVED | Protocol line 264 is now identified as a partial bounded-degradation precedent. |
| FN2-10 | RESOLVED | Gross/marginal runs and G-6 re-inference are now distinguished. |
| FN2-11 | PARTLY | Questions are substantially split, but declaration scope, `m`, tie behavior, and ETH details remain omitted. |
| FN2-12 | RESOLVED | The draft explicitly chooses the last-emitted cached value rather than recomputation. |
| FN2-13 | DEFERRED | The inherited line-115/119 citation error is acknowledged and deliberately left to the authorized recorder/owner. |
| SN2-1 | RESOLVED | Shifting the pre-sizing signal with the own real-hour estimator removes the alternative-estimator and clipping defects. |
| SN2-2 | RESOLVED | The proposal now states that realized mean exposure and turnover are reported, not preserved. |
| SN2-3 | PARTLY | Initial state and primary numeric checks were added, but the full operational/availability contract remains incomplete. |
| SN2-4 | PARTLY | The cardinality and rank arithmetic and exchangeability caveat are correct; indexing and `g` remain undefined. |
| SN2-5 | RESOLVED | The former same-instant ordering and pending-order ambiguity is substantively resolved. |
| SN2-6 | RESOLVED | Cutoff, cached state, warm-up, refit state, non-market state, and fail-closed behavior are specified. |
| SN2-7 | PARTLY | G-5/G-6/G-7 benchmark questions are separated, but ETH treatment remains combined and underspecified. |
| SN2-8 | RESOLVED | The workload now uses consistent gross/marginal counts and includes feature re-inference. |
| SN2-9 | PARTLY | Most owner choices are separated, but the remaining omissions in SN3-1, SN3-3, SN3-4 and SN3-6 prevent completeness. |

Authority remains unchanged: D-14 and D-15 require qualified-statistician review followed by the §4 amendment process; this review closes neither row. Exact checks used only in-memory `.venv/Scripts/python.exe -B -` rational arithmetic, with no simulation, network, restricted data, or filesystem writes. Tests, lint, types, and frozen-hash regeneration were N/A because this was a clean-tree document review with no edits. Per repository policy, this R19-2 review is not part of the durable record until an authorized party saves and commits it; I did not do so because the task prohibited editing and committing.

The redesigned null now preserves each trial’s own volatility sizing when its signal is shifted.  
The draft still leaves enough indexing, availability, and declaration details for implementations to disagree.  
The type-7 option would pass an all-tie pure-sizing trial, contrary to the proposal’s stated consequence.  
The delay mechanics are largely repaired, but the ETH stress choices must be separated and made explicit.  
Keep D-14 and D-15 blocked until these fixes are reviewed and committed; this review accepts no method.