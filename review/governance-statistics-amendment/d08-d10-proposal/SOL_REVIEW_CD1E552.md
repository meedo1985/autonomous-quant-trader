# Sol High review of the D-08..D-10 proposal rev1 at `cd1e552` — SOUND WITH FIXES

Date: 2026-10-03. The OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10223-b58f-73a0-a0dc-191bfaa7f2ed`;
  tokens used 103,097; exit 0. (The reviewer's self-report names only "GPT-5"; the CLI header
  is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `cd1e552`) with `{{PREFIX}}` = `SB8`
  (substituted file SHA-256 `7050e5c5210719f06aa37177ba6b1213b7529e46a5df0f33f539a2bca57f75d9`).
- The reviewer's final message, verbatim:

---

Model: GPT-5, OpenAI GPT family; exact runtime model ID is not exposed to me.  
Commit reviewed: `cd1e552ddaae12b600783433be022a33ae85b145` (the scoped files remained unchanged after HEAD advanced concurrently).  
Verdict: **SOUND WITH FIXES**

D-08 is sound and required conditional on retaining the frozen difference matrix and the proposed D-18 selection rule. `E-IMPROV` is not identifiable from that matrix; Lemma L-1 makes its ranking equivalent to candidate-only Sharpe; and D-18 nominates by `E-DIFF`. The §4 wording consequence is correct.

D-09’s per-half Sharpe calculation and `|J_f|` enablement count are conceptually correct. On `A_f`, every declared trial has one completed evaluation, so rerun attempts do not increase the frozen 20-trial trigger.

D-10 is correct when the complete IS-best tie class consists of identical columns. The statement needs qualification for mixed ties.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| `SB8-1` | **BLOCKER** | §3, D-09 minimum | D-19 has not frozen a sufficiently large `T_min`, or sets it below 160. | The proposal simultaneously says “no extra minimum” and introduces an AI-default 10-days-per-block floor. The decision matrix records the minimum as blocking. Per-half `n >= 2` makes Sharpe arithmetically defined but does not ensure 16 nonempty chronological blocks. | Bind one rule now: no per-block Sharpe minimum, but require 16 nonempty blocks (`T >= 16`) and a valid Sharpe on every half; alternatively specify an explicit block minimum. Delete the conditional AI default, or keep D-09 blocked until D-19 fixes the dependency. |
| `SB8-2` | **BLOCKER** | §5 C-4 | The owner accepts D-09 believing no amendment wording is required. | The decision matrix assigns D-09 authority `STAT then §4`, while C-4 says D-09 is only `STAT`. The amendment draft also retains the PBO clause as open. | Change C-4 to state that D-09 requires a statistical definition and its formal §4 binding; D-10 remains `STAT` unless its definition is also inserted into normative amendment text. |
| `SB8-3` | **BLOCKER** | §6 owner question | The owner treats D-18 and the omitted D-09 branch as already settled. | The authorized D-18 source labels itself a non-binding AI proposal, but §6 says “your D-18 decision already requires.” The question also omits the unresolved block rule and does not present the lowest-ID alternative or its consistency tradeoff. | Say “if the proposed D-18 rule is adopted,” state the complete D-09 rule, and present uniform averaging versus lowest-ID explicitly. Do not offer one bundled acceptance until `SB8-1` is resolved. |
| `SB8-4` | **NON-BLOCKING** | §4, “For duplicate trials…” | Exact duplicate columns share an IS tie with a nonduplicate column having the same IS Sharpe. | Exact rational check: with duplicate columns `A=B`, a duplicate-only tie example gave `phi_uniform = phi_lowest-id = 1/3`. But a mixed tie example gave `5/36` versus `1/12`. Identical columns always share their OOS midrank; equality follows only when the whole relevant tie class is identical, or all tied members receive the same OOS score. | Qualify the claim accordingly. Remove “probability near zero” unless a continuous, unrounded return law is explicitly assumed. The uniform-average recommendation remains sound and label-invariant. |
| `SB8-5` | **NON-BLOCKING** | §5 C-2 | “The bound covers only DSR” is read as saying the final promotion bound no longer applies. | P18-7 defines the bounded event through DSR; final promotion adds further gates and is therefore a subset. PBO has no separate calibrated error interpretation, but as an additional filter it cannot inflate that false-promotion bound. Its failures can affect power and `U_proc`. | State this distinction explicitly: PBO is not separately error-controlled, while the DSR bound still upper-bounds final false promotion under the qualified procedure. |

E-DIFF is the right ranking if PBO is to evaluate the same selection used by D-18.  
The 20-trial trigger correctly counts declared trials, not rerun attempts.  
Duplicate-only ties give the same result under averaging and lowest-ID selection.  
D-09 still needs one unambiguous block-length rule and formal amendment binding.  
The owner question must describe D-18 conditionally and show the actual remaining choices.