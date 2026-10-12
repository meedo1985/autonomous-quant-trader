# Sol High focused check of the D-14/D-15 proposal rev5 at `0c16c35` — NOT READY

Date: 2026-10-03. This is the OpenAI-family focused check for R19-2. It ran in parallel with the Fable check, without access to it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a1030e-c145-7c23-a51d-5211fca9b29a`;
  tokens used 68,917; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R5.md` (committed `2caf045`) with `{{PREFIX}}` = `SN5`
  (substituted file SHA-256 `2576816b2bcf8354d84a695a3f54f1249c5b8658bfdc74f78681c0766d6d7628`).
- The reviewer's final message follows, verbatim:

---

Model: **Codex, OpenAI GPT-5 family**; the exact runtime model ID is not exposed to me.  
Commit reviewed: **`0c16c35`**, revision-4-to-5 diff only.  
Verdict: **NOT READY** — owner-question blockers are **SN5-1, SN5-2, and SN5-3**. This review closes no D-row and accepts no method.

### Revision-4 finding status

| Finding | Status | One-line disposition |
|---|---|---|
| FN4-1 | PARTLY | Overlays are re-run and the direct stateful `N/A` bypass is disclosed, but constant `s` plus a timing overlay still receives Q2 `N/A` under the recommendation; SN5-1. |
| FN4-2 | RESOLVED | Q20/N-4 discloses the drift trap and offers three owner choices, including an explicit amendment for exits to zero. |
| FN4-3 | RESOLVED | The proposal now states that the recommended anchor makes the 24-hour test inert for daily decisions. |
| FN4-4 | PARTLY | Restricting `σ̂` closes the estimator-relabeling route, but the gaming analysis overlooks timing placed in the overlay; SN5-1. |
| FN4-5 | RESOLVED | The band is now the trial’s declared band, with the requested frozen citations. |
| FN4-6 | RESOLVED | Lagging now follows each input’s declared emission schedule and prohibits synthesized partial aggregates. |
| FN4-7 | PARTLY | Q10a separates decision and fill direction conceptually, but the recommended fill classification cannot govern the earlier decision without another rule; SN5-2. |
| FN4-8 | RESOLVED | Every fill, including a same-instant baseline fill, atomically updates all relevant state. |
| FN4-9 | PARTLY | Counts were rebuilt per asset and stressed leg, but the ETH zero counts encode one side of the contradictory Q14–Q17 semantics; SN5-3. |
| FN4-10 | PARTLY | Benchmark choices are presented as applying to both assets, but Q15/Q17 option (b) contradicts that statement; SN5-3. |
| FN4-11 | RESOLVED | The ETH 2x point-estimate interpretation is explicitly labelled a reading. |
| FN4-12 | RESOLVED | `g` is correctly described as fixed by the draft rather than an owner question. |
| FN4-13 | RESOLVED | `T` is now the number of UTC days, with incomplete days handled separately. |
| FN4-14 | RESOLVED | Both exact-check qualifiers—volatility-independent signals and no exchangeability proof—are restored. |
| SN4-1 | RESOLVED | Atomic fill-state updating closes the missing baseline transition. |
| SN4-2 | PARTLY | Q10a/Q10b separates classification and anchor, but leaves decision-time eligibility undefined when direction flips before fill; SN5-2. |
| SN4-3 | PARTLY | The direct stateful opt-out is fixed, but an overlay-only timing strategy can still enter Q2’s recommended `N/A`; SN5-1. |
| SN4-4 | RESOLVED | Feature lag is defined by observation emission rather than partial recomputation. |
| SN4-5 | RESOLVED | Q19 explicitly asks the owner to accept the whole event contract. |
| SN4-6 | PARTLY | The table exposes candidate and benchmark columns, but “ETH entirely at baseline” conflicts with the supposedly asset-wide benchmark choice; SN5-3. |
| SN4-7 | PARTLY | The new counts are coherent only if Q15/Q17(b) overrides the benchmark choice, contrary to §2.3; SN5-3. |

Targeted result: **overlay re-run—defect; N-4(iii)—no new defect; Q10a/Q10b—defect; emission-schedule lag—no new defect; §2.3 and §3—defect.**

### Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SN5-1 | **BLOCKER** | `PROPOSAL.md` §1.2, Q1b/Q2; C-2 | A trial declares constant `s` and puts market timing in a stop, take-profit, or hysteresis overlay. | Shifting constant `s` changes nothing. Re-running the overlay on the same price path therefore produces 500 copies identical to the candidate. Q2 nevertheless recommends `N/A` and says the trial “makes no timing claim,” although the changed text expressly permits path-dependent overlays. Thus the revision recreates a promotion-without-G-11 route and contradicts its claim that overlays provide no `N/A` escape. | Define “pure sizing” over the **entire mapping**, including the overlay. If an overlay responds to prices, P&L, or path state, require a null that perturbs that timing, explicitly offer promotion without G-11 evidence, or keep it blocked. |
| SN5-2 | **BLOCKER** | §2.1 decision step; Q10a/Q10b; Q19 | An order is a reduction when decided but becomes an exposure increase before its delayed fill. | From held exposure `3/5` to target `1/2`, a price factor below `2/3` makes pre-fill exposure less than `1/2`; filling then increases exposure. Under recommended Q10a, the order becomes a qualifying increase only at fill, but the clock and 00:00 eligibility tests had to be applied when the order was created. The current contract therefore permits a risk increase that bypassed those tests, or requires a non-causal decision using the future fill price. | Separate **decision eligibility** from **clock reset at fill** and specify direction-flip handling—cancel/reject, clamp, or an expressly accepted bypass. Then make Q10b conditional on that complete rule. |
| SN5-3 | **BLOCKER** | §2.3 Q14–Q17; §3 G-7/G-6 counts | The owner chooses a delayed/lagged benchmark but chooses Q15(b) or Q17(b) for the ETH candidate. | §2.3 says the benchmark choice applies to BTC and ETH alike, yet option (b) says “ETH entirely at baseline.” Section 3 then counts zero ETH runs under (b), even when the benchmark choice says the ETH benchmark is stressed. The owner cannot tell whether option (b) affects only the candidate/drawdown or overrides the independent benchmark choice. | Either make (b) candidate-and-drawdown baseline while the benchmark still follows Q14/Q16, with one stressed ETH run when applicable, or state that (b) overrides the benchmark choice and remove the independence claim. Reconcile §3 accordingly. |

### Plain-language summary

Revision 5 fixes most of the revision-4 findings, including fill updates and the feature-emission lag rule.  
Re-running overlays does not test timing hidden inside an overlay when the declared signal is constant.  
The fill-based increase rule cannot determine at decision time whether a delayed order must satisfy the clock.  
The ETH options and workload counts disagree about whether an ETH benchmark remains stressed.  
Therefore revision 5 is **NOT READY** for the owner until SN5-1 through SN5-3 are repaired.