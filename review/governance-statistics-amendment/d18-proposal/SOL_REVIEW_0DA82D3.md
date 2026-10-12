# Sol High focused check of the D-18 proposal revision 5 at `0da82d3` — NOT READY

Date: 2026-10-03. Focused check (revision 4 → 5 changes only) by the OpenAI
family for R19-2, chosen by the owner in round 5 ("Fix, quick check, then
decide"); run in parallel with, and without sight of, `FABLE_REVIEW_0DA82D3.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10096-b0fb-7820-a352-b0ba66238d36`;
  tokens used 78,343; exit 0. (Self-report names only "GPT-5 family"; the
  CLI header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_0DA82D3.md` (committed `eaa8a14`) with `{{PREFIX}}`
  replaced by `SR5` (substituted file SHA-256
  `4bcde2c2d6817f50795ef6fa24fa810e2f51b55c07001a5ba6e0a5006721fce0`).
- Findings: SR5-1..SR5-3 BLOCKER. Nothing is decided by this record; no
  finding is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

Model: Codex — OpenAI GPT-5 family; exact serving variant is not exposed to me.  
Commit reviewed: `0da82d35934d2747fc09d471748992ce51dd8a12`  
Verdict: **NOT READY**

The top-Sharpe/no-fallback event is correct. Three defects still block the D-18 definition itself: first-cycle eligibility, discretionary reruns, and the internally inconsistent no-result event.

### Revision-4 finding disposition

- **FR4-1 — PARTLY:** broader output and declaration records are covered, but the historical v1 exception still permits outcome-informed selection.
- **FR4-2 — RESOLVED:** the relevant frozen data-entry clauses and required amendment route are now identified.
- **FR4-3 — RESOLVED:** the approximately 27.6-month example and window-consumption cost are disclosed.
- **FR4-4 — DEFERRED to amendment:** new outcomes for ineligible and no-result cycles remain owner-authored amendment text.
- **FR4-5 — DEFERRED to amendment:** declared-plan completion is proposed as the replacement budget trigger.
- **FR4-6 — PARTLY:** the owner chose one rerun, but the rule is not yet deterministic; see SR5-2.
- **FR4-7 — RESOLVED:** start, completion, hash-match, and exclusion-from-`V` requirements are explicit.
- **FR4-8 — PARTLY:** the denominator and joint-allocation dependency are stated, but the certified event contradicts its exclusions; see SR5-3.
- **FR4-9 — RESOLVED:** 1.972 is correctly limited to the current method and model.
- **FR4-10 — RESOLVED:** the false “both consequences re-asked” description is corrected.
- **FR4-11 — RESOLVED:** the claim is narrowed to conditional evidence over named simulated classes.
- **FR4-12 — PARTLY:** the gap applies to post-v1 windows but not the proposed v1-confirmation exception; see SR5-1.
- **FR4-13 — DEFERRED to the broadened method:** the lifetime-count decision is explicitly reopened there.
- **FR4-14 — RESOLVED:** the owner selected family opt-out and its event treatment is defined.
- **FR4-15 — DEFERRED to D-19:** power- and mixed-null availability reporting is specified as later work.
- **SR4-1 — RESOLVED:** mandatory-gate unavailability and technical invalidity enter the no-result event.
- **SR4-2 — PARTLY:** eligible attempts are the denominator, but exogenous no-picks/failures are simultaneously included and excluded; see SR5-3.
- **SR4-3 — PARTLY:** manifests and lineage improved, but C1 not starting does not make historical public outcomes independent of selection.
- **SR4-4 — DEFERRED to the broadened method:** qualification is expressly prohibited until that method is specified and reviewed.
- **SR4-5 — RESOLVED:** the entire qualification object is frozen and held-out namespaces burn upon access.
- **SR4-6 — DEFERRED to amendment:** family order and continued processing are proposed; duration and exact execution semantics remain amendment work.
- **SR4-7 — RESOLVED:** the text now disclaims an unconditional real-market guarantee.

### Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SR5-1** | **BLOCKER** | P18-0 | Researchers choose `J_f` using the public 2022–2025 BTC path, without ever running C1 or receiving engine output. The v1 confirmation partition nevertheless passes the new rule. | C1 not starting proves only absence of cycle evaluation. The frozen confirmation window is historical, not future; condition (iii)’s purge/embargo applies only to post-v1 windows. The accepted adjudication required data that did not exist at declaration. | Remove the v1 exception. Require a genuinely future window declared before its outcomes exist, with the boundary gap; alternatively produce a separately reviewed custody rule that actually establishes outcome-unavailability to every selection actor. |
| **SR5-2** | **BLOCKER** | P18-1–P18-3 | After a crash, an operator may rerun or wait until day 180. Crash diagnostics or partial durable output can be outcome-correlated even when no formal output was “returned or seen.” These choices change `A_f` and the no-result event. | “One rerun … is allowed” is discretionary. Same seed/hash does not establish deterministic replay after infrastructure or numerical failure, nor define whether partial output burns the attempt. | Make the retry rule prospective and mechanical: automatically rerun exactly once when a precisely defined atomic no-output condition holds; otherwise fail availability. Bind execution identity, diagnostics visibility, budget handling, and attempt records. |
| **SR5-3** | **BLOCKER** | P18-2, P18-3, P18-7 | An eligible authorized cycle is invalidated before its pick, or a trial suffers a real infrastructure failure. It enters the stated numerator through “no pick” or `A_f = false`, yet the next paragraph says those events are not certified. | The same occurrence is simultaneously part of the “whole-cycle no-result rate” capped at 1% and excluded from calibration. No-pick under P18-2 occurs specifically through revision/invalidation. | Define two disjoint events: a calibrated procedure-generated no-result event and an operational cancellation/failure event, each with its own denominator. State explicitly that the 1% target applies only to the former. |

The family opt-out introduces no defect: an undeclared family has `E_f = ∅`, does not enter the no-result event, and one-family designs can be handled in D-19. The post-pick changes are adequate as an amendment proposal, but exact duration, gate short-circuiting, failure precedence, and outcome labels must be bound before calibration or activation.

1. Choosing the top-Sharpe trial with no fallback is now defined correctly.
2. The old confirmation partition is not made statistically unseen merely because C1 never started.
3. The rerun decision must be automatic and outcome-blind, not optional.
4. The 1% rule must separate method failures from cancellations and infrastructure failures.
5. D-18 is not ready for decision until those three definition defects are repaired and the review is committed.