# Sol High focused check of the D-14/D-15 proposal rev4 at `83fc993` — NOT READY

Date: 2026-10-03. This is the OpenAI-family focused check for R19-2. It ran in parallel with the Fable check and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10304-298f-7611-a992-c9f68891d437`;
  tokens used 90,988; exit 0. (The reviewer's self-report names only "GPT-5 family". The CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R4.md` (committed `cb8102b`), with `{{PREFIX}}` = `SN4`
  (substituted file SHA-256 `42e037df8e962c8be24cb76b9b3e647c02cd8f2c7356380cc3920aed2d3e8dbd`).
- The reviewer's final message follows, verbatim.

---

Model: **Codex, OpenAI GPT-5 family**; exact runtime model ID is not exposed to me.  
Commit reviewed: **`83fc993`**, revision-3-to-4 diff only.  
Verdict: **NOT READY** — blockers are SN4-1 through SN4-6. This review closes no D-row and accepts no method.

### Revision-3 findings

| Finding | Status | One-line disposition |
|---|---|---|
| FN3-1 | RESOLVED | Q10 exposes the fill-time 23-hour problem and offers decision-time, fill-time, or amendment routes. |
| FN3-2 | PARTLY | Instants and same-instant baseline filling are defined, but the baseline fill lacks an explicit post-fill state transition; see SN4-1. |
| FN3-3 | RESOLVED | Hourly signals, data-only dependencies, exclusions, and the applicability alternative are now explicit. |
| FN3-4 | RESOLVED | The alignment claim is limited to `σ̂`, and Q3 exposes variance timing in `s`. |
| FN3-5 | RESOLVED | Tie consequences are correctly separated by pass rule. |
| FN3-6 | RESOLVED | `T`, `g`, indexing, scope, cost, and unavailable-draw handling are restored. |
| FN3-7 | RESOLVED | The 0.10 band is explicitly applied to scheduled increases. |
| FN3-8 | RESOLVED | Held exposure is explicitly defined to drift with price; its clock interaction creates SN4-2. |
| FN3-9 | PARTLY | Both lag readings are offered, but recommended option (a) is not defined for calendar-frequency features; see SN4-4. |
| FN3-10 | RESOLVED | The correct excluded-days clause is cited and warm-up is Q5. |
| FN3-11 | RESOLVED | The G-11 `na` amendment and P18-7 exception are identified. |
| FN3-12 | RESOLVED | G-5 semantics are assigned to proposed N-3 and its ETH point estimate is Q13. |
| FN3-13 | UNRESOLVED | The revised G-6/G-7 workload counts remain internally inconsistent; see SN4-7. |
| FN3-14 | RESOLVED | The history now attributes the signal-shift design to SN2-1. |
| FN3-15 | RESOLVED | The frozen ETH citation is corrected to lines 42–43. |
| SN3-1 | PARTLY | An applicability contract now exists, but the recommended N/A route creates an undisclosed mandatory-gate bypass; see SN4-3. |
| SN3-2 | RESOLVED | Operational domain, indexing, validity, denominator, and no-replacement rules are stated. |
| SN3-3 | RESOLVED | All-tie behavior is correctly stated for each offered rule. |
| SN3-4 | RESOLVED | The floor is Q6 and random-stream mechanics remain explicitly dependent on D-20. |
| SN3-5 | PARTLY | Absolute targets and the initially unset clock are added, but fill/state/clock transitions remain incomplete; see SN4-1 and SN4-2. |
| SN3-6 | PARTLY | Separate questions exist, but G-7 ETH cannot express candidate-only stress and costs are not fully enumerated; see SN4-6. |
| SN3-7 | RESOLVED | The `θ` domain and unavailable-baseline outcome are supplied. |
| SN3-8 | RESOLVED | “Preregistered N/A” replaces the misleading “frozen N/A” wording and is labelled amendment-required. |

### Revision-4 findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SN4-1 | **BLOCKER** | `PROPOSAL.md` §2.1, lines 183–200 | A baseline order is created and filled at step 5. | Held exposure and the clock are updated only in step 2, before that order exists. Nothing says the same-instant fill updates either state, so literal implementations can carry stale state into the next instant. | State that every fill atomically updates position, equity, held exposure, and—when applicable—the clock, including a baseline step-5 fill. |
| SN4-2 | **BLOCKER** | §2.1 lines 175–210; Q10 | A delayed order was an increase when decided but becomes a reduction before filling because exposure drifts. | Exact example: decision held exposure `2/5`, target `1/2`; after price doubles, held exposure is `4/7`, so filling to `1/2` reduces exposure. Recommended Q10 nevertheless resets the “risk-increase” clock because the decision was an increase. That conflicts with frozen line 57’s “last risk increase” and invalidates the claim that only the timestamp anchor is being chosen. | Separate two choices: what qualifies as a risk increase—actual pre/post-fill exposure increase versus decision classification—and which timestamp anchors a qualifying fill. |
| SN4-3 | **BLOCKER** | §1.2 lines 40–64, 78–85; Q1b/Q2 | A timing strategy adds path dependence, or is naturally stateful, and receives G-11 N/A. | The frozen null is intended to remove beta/time-in-market advantage. The proposed N/A covers stops, hysteresis, and the owner’s rule, supplies no replacement test, and would invoke P18-7’s N/A exception rather than fail unavailable. This material promotion bypass is not disclosed to the owner and is gameable at declaration. | Tell the owner explicitly that N/A permits promotion without G-11 evidence. Offer: accept that gap, require an alternate null, restrict eligibility, or keep blocked; make applicability mechanically auditable. |
| SN4-4 | **BLOCKER** | §2.2 lines 215–229; Q11 | A feature is defined from completed UTC-day bars and evaluated at 00:00. | At `t−1h = 23:00`, the same completed-day feature is not available. Using the preceding completed day gives the “last-emitted” one-day lag; building through 23:00 uses an incomplete or shifted aggregate and changes the feature definition. Thus option (a) is not generically a one-bar lag. | Define lagging by each feature’s declared observation unit and emission schedule. Do not synthesize partial daily features unless that alternate feature is separately declared. |
| SN4-5 | **BLOCKER** | §2.1; §4 C-3; §5 | The owner answers Q10 but is never asked to accept the rest of the event contract. | Instant semantics, same-instant baseline fill, price drift, absolute targets, and the increase-band reading are new bindings or AI defaults. Section 5 contains no event-contract question, while C-3 mentions only the band and clock anchor. | Add an explicit D-15 event-contract owner question covering all these bindings and their proposed amendment wording. |
| SN4-6 | **BLOCKER** | §2.3 lines 238–243; Q12–Q17 | The owner chooses an unchanged G-7 benchmark to isolate candidate delay. | Q14 permits candidate-only stress on BTC, but Q15 offers only both ETH legs delayed or all ETH baseline—no delayed ETH candidate against an unchanged ETH benchmark. Q17 does inherit Q16, so G-6 and G-7 expose inconsistent option structures. Q14–Q17 also leave the 1x cost binding implicit. | Enumerate candidate, benchmark, cost, feature/execution treatment, and drawdown path independently for each gate and asset; include coherent candidate-only ETH stress. |
| SN4-7 | **NON-BLOCKING** | §3 lines 255–262 | D-19 consumes the workload table. | G-7 starts with “4, or 2” and then adds ETH again, although those were revision 3’s two-asset totals. G-6 says “as G-7,” thereby referring to Q15 instead of its own Q17 semantics. | Recalculate per gate from explicit BTC and ETH candidate/benchmark legs, distinguishing gross from marginal cached runs. |

### Plain-language summary

Revision 4 fixes most of the earlier drafting findings, but its delayed-order state machine is still incomplete.  
Price movement can turn a planned increase into an actual reduction, so the clock rule needs two decisions rather than one.  
The recommended feature-lag rule changes some daily features instead of merely delaying them.  
The proposed N/A route lets stateful strategies bypass the mandatory timing null without replacement evidence.  
The proposal should be revised and focused-checked again before the owner is asked Q1–Q18.