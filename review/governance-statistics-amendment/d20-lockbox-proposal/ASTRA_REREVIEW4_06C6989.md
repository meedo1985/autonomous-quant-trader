# Codex Astra re-check of D-20 lockbox revision 5 (06c6989)

Prompt: `REREVIEW4_PROMPT.md`, prefixed with "Do NOT open or read SOL_REREVIEW4_06C6989.md or any other SOL_* file in that folder; review independently. Use finding IDs D20LR5-A-n." Reviewer metadata from the Codex CLI header (2026-10-27): model `gpt-6-astra`, provider openai, sandbox read-only, reasoning effort high, Codex CLI v0.164.0, session id `01a17c22-3b8e-7301-aaca-81dc1796df99`, 75,481 tokens. Reviewed HEAD `27b027d`. Independence check: the CLI log's only `SOL_REREVIEW4` hits are the prompt prefix and a reference inside `d12-proposal/PROPOSAL_REV7.md` (a different file); the D-20 Sol record was not opened.

Verdict: **FIX** (2 BLOCKER, 1 NON-BLOCKING). Findings D20LR5-A-1..3. Dispositions: D20LR4-A-1 FIX (-> A-1); D20LR4-A-2 ACCEPT WITH NOTES; Q5 wording ACCEPT; Q2(ii) ACCEPT; consolidation deferral ACCEPT WITH NOTES.

Convergence with Sol (`SOL_REREVIEW4_06C6989.md`): A-1 ~ S-3 (timing/availability residual across the fix boundary); A-2 = S-2 (snapshot crash recovery); A-3 = S-4 (Q1 omits state-boundary move). Sol-only: S-1 (cap recheck at every write).

No finding is left unrepaired yet; dispositions go in revision 6.

## Report (verbatim)

**Verdict: FIX — two BLOCKERs remain.** Statistical-binding status: **REVISION_REQUIRED**.

Reviewed HEAD `27b027d20881c7b6426449d166fc28f492dad7b0`. I wrote nothing and opened no `SOL_*` file. IDs use **D20LR5-A-n** as requested; the caller’s CLI header must establish the exact reviewer model.

| Authority | Status |
|---|---|
| Frozen Constitution/protocol | Controlling |
| D-11/D-12 owner decisions | Recorded decisions; binding through signed C2 |
| Revision 5 and inherited bindings | Inactive proposals; this review activates nothing |

**Dispositions of prior Astra findings and notes**

| Rev-5 disposition | Decision | Evidence |
|---|---|---|
| **D20LR4-A-1**, timing channel | **FIX** | Separate locks remove direct contention, but the fix step and late-response exception still expose sealed activity. See A-1 below. |
| **D20LR4-A-2**, processing after cap | **ACCEPT WITH NOTES** | `D*=min(d_w,C)` now governs bars, bundle writes and completion. Post-cap reconciliation preserves evidence without reopening access. Snapshot recovery remains a separate defect, A-2 below. |
| Q5 wording | **ACCEPT** | “No estimator-seed change” correctly preserves the confirmation-adapter requirement. |
| Q2(ii), R-14 placement | **ACCEPT** | The alternative remains limited to files R-14 actually permits. |
| Consolidation deferred to S4 | **ACCEPT WITH NOTES** | Acceptable for this focused re-check. The final signing/build specification must consolidate effective bindings and resolve replacement precedence; five chained revisions should not become the implementation contract. |

**New findings**

1. **D20LR5-A-1 — BLOCKER: sealed activity still changes public timing and availability.**

   **Place:** [rev-5 fix step and response schedule, lines 90–97](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:90), contention tests at lines 118–122.

   **Failure scenario:** compare two executions with eventual FAIL. In one, the worker crashes and releases `L_seal`; the scheduler fixes DEFAULT promptly. In the other, a worker operation holds `L_seal` across `D*` and beyond `R_0−21,600`. At the public boundary, the first returns `fixed:true,result:FAIL`; the second returns `fixed:false` and misses publication. The six-hour buffer provides slack, **not a bound** on that wait.

   Separately, line 97 explicitly returns an over-Δ operation whenever it finishes. Shared worker fsync/CPU activity can therefore distinguish a finished FAIL from a crashed worker. Logging an incident records the disclosure; it does not remove it. D-12’s accepted signing residual affects PASS, whereas this residual can distinguish FAIL executions.

   The proposed contention test does not close either channel. If “hold indefinitely” crosses the fix boundary, equal response bytes cannot hold under the specified fallback. If it starts after fixation, it misses that failure. A common latency band and 1,000 observations also do not establish equal timing distributions.

   **Minimal repair:** specify public payload, timing and availability independence across the fix boundary, including overruns and incident visibility; remove variable completion-time responses from the claimed protected behavior. Test matched eventual-FAIL executions while contention crosses both boundaries. If a residual cannot be eliminated, explicitly propose its disclosure to the owner and revise the security claim; it is not already accepted under R1–R4.

2. **D20LR5-A-2 — BLOCKER: the new snapshot lacks crash recovery.**

   **Place:** [rev-5 snapshot and reconciliation, lines 84–101](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:84).

   **Failure scenario:** the store fsyncs a pre-read index entry, then crashes before replacing `P`. On restart, the index contains the consumed-budget entry but `P` does not. `begin_read` returns the existing entry with “nothing written”; the read gate consults stale `P` and cannot authorize it. The inherited crash-after-append recovery guarantee is lost.

   The same crash window after a release append leaves a committed release absent from readers’ snapshot. That conflicts with the retained rule that a crash after commit leaves the release effective.

   Atomic replacement prevents a **partial snapshot**, but does not synchronize two separate durable writes.

   **Minimal repair:** define `P` as a recoverable projection of authoritative durable records. Require startup reconciliation/reconstruction before serving affected operations, preserving fixed results, release times and consumed budgets. Add crash tests between index fsync and snapshot replacement for both pre-read and release entries, including restart after C.

3. **D20LR5-A-3 — NON-BLOCKING: Q1 omits the boundary change and overstates protection.**

   **Place:** [rev-5 Q1, lines 149–156](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md:149).

   **Failure scenario:** the owner adopts the listed defaults without being told explicitly that publisher result access moves six hours later. “This stops the timing … hinting at a result” also conceals A-1’s admitted exception.

   **Minimal repair:** explicitly list the boundary move and explain its operational effect. Describe Δ as a qualified configuration value fixed before exposure, and state any remaining disclosure risk accurately. Choosing its numeric value during build qualification is reasonable; claiming unconditional protection is not.

**Assessment of D20L-51..55**

| Finding | Assessment |
|---|---|
| **51** | Real BLOCKER; attestation repair accepted. Non-null is required exactly for pre-cap PASS. Signature, evaluation ID and `cooling_off_start` checks are explicit. An invalid/missing attestation creates **no release row**, but not “no other trace”: inherited P-7/T-8 require an incident and missed-release handling; the pre-read record and consumed try remain. |
| **52** | Real BLOCKER; cap/access repair accepted. Order is reconciliation → cap → entitlement → budget → order/cooldown. `record_pre_read_check` is refused at C; worker operations and bars stop at `D*`. Existing records remain reconcilable. |
| **53** | Real BLOCKER, **not fully repaired**. Direct shared-lock contention is removed; A-1 remains, and the replacement snapshot introduces A-2. |
| **54** | Correct NON-BLOCKING errata. Eight note rows confirmed. Code inspection confirms default volatility calculation rejects non-hourly series, while supplied `sigma_bps` bypasses that path. |
| **55** | Wording and deletion applied correctly, subject to A-3. Uniform `CAP_REACHED` applies to new requests reaching admission checks; existing entries deliberately return through reconciliation first. |

**Boundary checks and owner fairness**

Independent integer arithmetic under Python 3.14.7 reproduced:

| Start | Time available until `D*` |
|---|---:|
| Ordinary uncapped read | 561,600 seconds = 6.5 days |
| `t_s=C−3,600` | 3,600 seconds |
| `t_s=C−1` | 1 second |

The moved state boundary is exactly 21,600 seconds after `d_w`.

A read **unfinished at C** becomes FAIL/DEADLINE, spends its try and leaves the nominee expired. That consequence is fair to present without inventing an admission cutoff. “Usually” is an unverified runtime expectation; the precise statement is “may fail if insufficient time remains.” A quick successful completion before C retains its result even if publication occurs later.

Q2–Q5 are otherwise fair and answerable. Q1 needs the corrections above. Dropping `earliest` is sound; no essential audit, deadline or transaction machinery is droppable. Owner answers, S4 resolution and signed C2 remain necessary.

**Validation and limits:** read-only Python checks passed all 14 frozen sidecars, seven manifest bindings, seven protocol bindings and the Constitution self-hash. Frozen inventory matched HEAD; `docs/README.md` differed only through CRLF checkout conversion. Git diffs were empty, with a global-ignore permission warning. Implementation tests, lint, types and import checks were N/A for this proposal-only review; no production contention test was run.

**LOCAL GATE: BLOCKED. Claude status: NOT SENT.** This response is uncommitted review evidence; the caller must preserve it with verified model metadata before counting it as completed R19-2 evidence.