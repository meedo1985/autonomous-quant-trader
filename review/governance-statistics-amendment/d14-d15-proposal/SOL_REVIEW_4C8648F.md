# Sol High focused check of the D-14/D-15 proposal rev6 at `4c8648f` — NOT READY

Date: 2026-10-03. This is the OpenAI-family focused check for R19-2. It ran in parallel with the Fable check and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10317-e1b0-71d3-829a-e1777a84e009`;
  tokens used 77,346; exit 0. (The reviewer's self-report names only "GPT-5 family". The CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R6.md` (committed `5d851d6`), with `{{PREFIX}}` = `SN6`
  (substituted file SHA-256 `b1eb29f464e5bd2cd8036961e16dabda9727cf1db727f42b7b92b0c3e177a553`).
- The reviewer's final message follows verbatim.

---

Model: **Codex, OpenAI GPT-5 family**; exact runtime model ID is not exposed.  
Commit reviewed: **`4c8648f`** (`0c16c35..4c8648f`, changed text only).  
Verdict: **NOT READY**. This review closes no D-row and accepts no method.

### Revision-5 finding status

- **FN5-1 — PARTLY:** The constant-signal overlay escape is fail-closed, but the promised mechanical classification is undefined and the owner’s incompatible fixed-size rule is classified only hypothetically.
- **FN5-2 — RESOLVED:** Decision-time classification plus the reduction clamp prevents a delayed reduction from becoming an increase.
- **FN5-3 — RESOLVED:** Model outputs now have one stated treatment and the l.267 interpretation is labelled as a reading; revision 6 introduces a separate coarser-emission defect.
- **FN5-4 — RESOLVED:** Overlay triggers, the band target, and current-price held exposure are distinguished.
- **FN5-5 — RESOLVED:** The zero-exit exception applies at all decision times and cites all three affected frozen clauses.
- **FN5-6 — RESOLVED:** The drift-trap boundary is correctly limited to prices below entry.
- **FN5-7 — RESOLVED:** Q13 has an alternative and Q15/Q17 explicitly state their ETH overrides.
- **FN5-8 — RESOLVED:** Shared benchmark runs are separated from per-nominee candidate runs.
- **SN5-1 — PARTLY:** Q2/Q2b remove promotion through overlay-only `N/A`, but the class boundary is not operationally defined.
- **SN5-2 — RESOLVED:** The direction-flip handling is causal and explicit.
- **SN5-3 — RESOLVED:** Q14–Q17 now state when ETH overrides the benchmark choice.

Targeted result: the Q2/Q2b policy is fail-closed, but its classifier and treatment of the recorded rule remain incomplete. The clamp works; the recommended clock anchor changes the frozen clock meaning without saying so. The model-output rule is coherent once its inputs are defined, but §2.2 omits direct signal inputs and falsely equates a one-hour cutoff with one coarser emission. Q14–Q17 are repaired; Q13 is ambiguous. The §3 shared-run split is sound, but one ETH count is wrong.

### Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SN6-1** | **BLOCKER** | §1.2 lines 76–132; Q2/Q2b | A model- or code-defined `s` must be assigned to a class at declaration, or the owner’s fixed-10% rule is evaluated. | A hash identifies an interface but does not mechanically establish that an arbitrary signal is constant. No declaration field, validation domain, or rejection rule is supplied. The proposal also admits that the recorded fixed-size rule cannot satisfy `s·τ/σ̂`, then nevertheless calls it constant-`s` and overlay-timed. Its G-11 outcome is therefore only conditional on an unresolved eligibility question. | Define an explicit hashed class declaration and deterministic validation/rejection rule. Decide fixed-size eligibility first; describe the owner rule’s Q2b outcome conditionally until then. |
| **SN6-2** | **BLOCKER** | §2.1 lines 256–266; Q10 | A 00:00 increase decision fills at 01:00 under stress. | Frozen l.57 measures 24 hours since the **last risk increase**. The actual increase occurs at 01:00, but recommended Q10(b) records 00:00. At the next 00:00 only 23 hours have elapsed since the actual increase, although the proposed clock permits it. Thus Q10(b) changes l.57/l.113; option (c) misleadingly suggests that amendment is a separate alternative. | Label the decision-time anchor as an amendment to l.57/l.113, or use fill time. Make Q10’s choices and governance consequences mutually exclusive. |
| **SN6-3** | **BLOCKER** | §2.2 lines 272–299; Q11 | A rule-based `s` reads prices or returns directly rather than through model features. | §1.2 permits `s` to use market data, but the new exhaustive input list names model inputs, `σ̂`, overlay inputs, and the resulting target—not the market-data inputs used directly by `s`. “Lagged `s`” does not say whether to recompute it from lagged inputs or use an earlier emitted value. | Add every direct market-data input of `s` and specify recomputation/emission semantics. |
| **SN6-4** | **BLOCKER** | §2.2 lines 286–295; Q11 | A daily feature emits at 00:00 and is consumed at a 12:00 decision. | The rule selects the last emission at or before 11:00: today’s 00:00 value, exactly the baseline value. It therefore adds zero delay, not “one emission.” At a 00:00 decision it instead selects yesterday’s value. The claimed equivalence between `t−1h` and one coarser emission is false and phase-dependent. | Choose either a uniform one-clock-hour cutoff or the immediately preceding feature emission; do not describe them as equivalent. Then restate the model-output consequence. |
| **SN6-5** | **BLOCKER** | §2.3 Q12–Q13, line 314 | The owner selects Q12(ii), leaving the benchmark unchanged, and Q13(a). | Q13(a) says the ETH point estimate—“candidate and benchmark, following Q12”—is at 2x. Under Q12(ii), however, the benchmark remains at baseline; §3 likewise counts no stressed benchmark. The row does not determine whether Q13(a) overrides or follows Q12. | State separately: candidate cost, benchmark cost under each Q12 choice, and drawdown cost. |
| **SN6-6** | **NON-BLOCKING** | §3 lines 340–347 | The owner selects Q13(b), putting the whole ETH sanity rule at baseline. | The per-nominee G-5 table still counts one stressed ETH candidate run. Q13(b) and the text below §2.3 say ETH is not stressed at all. | Change the ETH G-5 count to “1 under Q13(a), 0 under Q13(b).” |

**Owner readiness:** **NOT READY** — the owner-question blockers are **SN6-1 through SN6-5**. SN6-6 does not itself block the questions.

No files, network, confirmation data, or lockbox data were accessed or changed. No simulation was run; the checks above use direct timing and exact algebraic counterexamples.

### Plain-language summary

1. Revision 6 successfully closes the obvious overlay-only promotion escape.
2. It still does not say how a trial is mechanically assigned to one of the three classes.
3. The proposed decision-time clock permits a new increase only 23 hours after the actual stressed fill.
4. The feature-delay and ETH-cost choices remain ambiguous in scenarios the owner can select.
5. Fix those owner-facing ambiguities before presenting D-14 or D-15.