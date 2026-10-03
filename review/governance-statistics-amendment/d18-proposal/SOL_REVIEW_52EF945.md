# Sol High focused check of the D-18 proposal revision 6 at `52ef945` — READY

Date: 2026-10-03. Focused check (revision 5 → 6 changes only) by the OpenAI
family for R19-2; focused-check format an AI default (round 6 Q4). Run in
parallel with, and without sight of, `FABLE_REVIEW_52EF945.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a100ac-38af-7131-984f-8f685b623032`;
  tokens used 78,910; exit 0. (Self-report names only "GPT-5 family"; the
  CLI header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_52EF945.md` (committed `a722a0e`) with `{{PREFIX}}`
  replaced by `SR6` (substituted file SHA-256
  `8ba4f600d33e4c51136a119636b27ff6809a5c24f1ab1ca53995ea1e77dd3839`).
- Findings: SR6-1..SR6-3 NON-BLOCKING. Nothing is decided by this record; no
  finding is repaired here.

Below is the reviewer's final message, verbatim.

---

Model: Codex — OpenAI GPT-5 family; exact serving variant is not exposed to me.  
Commit reviewed: `52ef9450f424ffbafb5ea72fb26ee48a1ed41402`  
Verdict: **READY** for the owner to decide the D-18 definition. No new blocker; activation remains blocked on the broadened method, amendment, and D-19 calibration.

### Revision-5 findings

- **FR5-1 — RESOLVED:** every pre-lockbox gate must run for every nominee; omission counts as `UNAVAILABLE`.
- **FR5-2 — PARTLY:** the historical-data weakness, prior-adjudication departure, and unverifiable independence assumption are explicit; owner confirmation remains pending.
- **FR5-3 — PARTLY:** the 80-trial reserve makes one retry possible, but lifetime-budget treatment remains ambiguous; see SR6-1.
- **FR5-4 — DEFERRED (D-19):** the boundary rule and C2 exemption are explicit; the requested boundary calibration cell belongs in D-19.
- **FR5-5 — DEFERRED (amendment):** all triggers, cooldown, and change/invalidation precedence are identified, but exact termination semantics remain to be bound; see SR6-2.
- **FR5-6 — RESOLVED:** both families are mandatory whenever an eligible window exists.
- **FR5-7 — RESOLVED:** the previously unrecorded owner-facing explanation is now quoted.
- **SR5-1 — PARTLY:** C2’s outcome-informed-selection risk remains, but it is accurately disclosed as an unverifiable, weaker claim requiring knowing owner confirmation.
- **SR5-2 — PARTLY:** retry discretion and information leakage are resolved; interaction with lifetime capacity remains; see SR6-1.
- **SR5-3 — PARTLY:** calibration and operational failures now have separate targets and denominators, but operational cause classification is not fully exclusive; see SR6-3.

The round-6 choices are unmistakably labelled **AI defaults**, not owner decisions. The C2 weakness and dropped initial embargo are disclosed; the automatic retry and both-families rule are deterministic.

### Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SR6-1** | NON-BLOCKING | P18-1 | A later cycle has prior counted attempts, yet declares 80 trials plus a reserved retry as though all 81 slots were newly available. | The proposal calls 81 a “per-cycle” budget, while frozen protocol line 190 says `lifetime_accounting: true`. | In the broadened-method/amendment work, define available capacity as remaining lifetime budget or explicitly amend lifetime accounting. |
| **SR6-2** | NON-BLOCKING | P18-2 | The declared plan completes before post-pick gates. The redefined exhaustion trigger becomes true immediately and, under `ends_when_any`, can terminate the cycle before steps (b)–(d). | Protocol line 194 makes exhaustion a termination trigger; revision 6 simultaneously defines it as plan completion and says termination waits for post-pick completion. Constitution line 61 requires exhaustion to be defined, not necessarily to end the cycle immediately. | The amendment must make termination occur only after post-pick finalization, while separately recording when plan exhaustion occurred. |
| **SR6-3** | NON-BLOCKING | P18-7 | A mandatory gate is `UNAVAILABLE` because its worker crashes. That matches both “any gate … `UNAVAILABLE`” in `U_proc` and “any infrastructure failure” in `U_ops`. | The simulated `U_proc` target is clear because infrastructure failures are excluded there, but the claimed operational disjointness lacks a cause-precedence rule. | In the amendment, give every failure one exclusive cause code and precedence rule; infrastructure-caused gate failures belong only to `U_ops`. |

The top-Sharpe nominee and no-fallback rule are ready to decide.  
`E_f` and the two-family union event are complete and mathematically coherent.  
The simulated procedure-no-result target is sufficiently defined for D-18.  
Using the old C2 window knowingly gives no verified real-market 5% guarantee.  
Nothing here accepts a method, activates governance, or closes D-18.