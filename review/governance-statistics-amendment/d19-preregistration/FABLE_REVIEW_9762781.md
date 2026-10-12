# Fable review BF3 of the D-19 preregistration §13 rev 7d at `9762781`: SOUND WITH FIXES

Date: 2026-10-04. R19-2 independent statistical narrow re-review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. This is R19-2 independent statistical narrow re-review BF3, run as a Claude Code subagent. It was read-only: I made no edits, ran no state-changing git commands, used no network, and did not touch data/, confirmation data or lockbox data. The only computation was in-memory exact-binomial arithmetic in `.venv` Python.

**Commit reviewed:** `9762781` (docs/d19-recommendation). Scope: `git diff 09b0fb9 9762781 -- review/governance-statistics-amendment/d19-preregistration/`. That diff covers §13 rev 7d, the history rows and `ADJUDICATION_09B0FB9.md`. I read it against §1–§12 (rev 6), BF2, BS2, and Annex A clauses A-B7, A-U1 and A-V1.

**Verdict: SOUND WITH FIXES.** I found no blocker. The statistical claims hold. Two MAJOR findings are in the new runtime text: as written, the start/resume checks cannot be run, and two of its rules contradict each other. Both need short text fixes before the owner accepts.

**Numbers I reproduced.** All use exact Clopper–Pearson at α = 0.025/M, M = 322 and 340, with a held-out pass probability of 0.999.

- **Targets:**
  - τ_G(40k) = 0.00045124, critical count 32;
  - τ_G(20k) = 0.00020216, critical count 11.
- **Development 90% UCB at 12k replications:**

  | `U_G` events | UCB | Result |
  |---|---|---|
  | 0 | 1.9186e-4 | passes at 20k |
  | 1 | 3.2410e-4 | escape (40k) |
  | 2 | 4.4347e-4 | escape (40k) |
  | 3 | 5.5665e-4 | fails |

  So 0 events means 20k, 1–2 events means 40k, and 3 or more means demotion. This is correct.
- **Chance demotion, P(3 or more events at 12k):**

  | True rate p | 2e-5 | 5e-5 | 1e-4 | 2e-4 |
  |---|---|---|---|---|
  | P(demoted) | 0.0019 | 0.0231 | 0.1205 | 0.4303 |

  This matches the §13 table.
- **Held-out failure in escaped cells at 40k** is below 1e-10 at these rates.

## 1. BF2/BS2 resolution

| Finding | Status |
|---|---|
| BS2-1 (BLOCKER) | RESOLVED for the data chain. The run-definition hash comes before the threshold run. The qualification object carries the chain heads and reduced results. Held-out chunks are bound to the object hash. Each chunk records its own content hash and the final heads are recorded. The same circularity remains for the canaries and the reference vectors: see BF3-1. |
| BF2-1 | RESOLVED. The escape is valid: N_i is fixed from development data, which is independent of held-out, before the freeze. M is unchanged, because the escape changes N, not the test count. In escaped cells, the error and DSR tests at 40k are checked against the 20k targets (τ_err(20k) for `z_crit`, τ_DSR(20k) for availability), which is conservative. Demoted cells are reported from development plus §9 only, as required. The cost side is BF3-3. |
| BS2-2 | RESOLVED. §1 and §3.3 are overridden, the challenge-cell definition is extended, and the "Unchanged" list is corrected. |
| BF2-3, BS2-3 | RESOLVED. The C2-only argument is sound. A `g` mismatch makes the declaration invalid, so T ≤ T_C2. A-B7's floor with T_min = T_C2 forces T = T_C2 without amending A-B7, so withdrawing A-B7-EQ is correct. §12 is overridden and requires a separately recorded affirmative answer to O18-4-T. |
| BF2-2, BS2-4 | PARTLY RESOLVED. The container by digest, libm canary, CPU model and features in the identity, the wording change and the owner disclosure are all done. The residual defects are BF3-1 and BF3-2. |
| BF2-4 | RESOLVED. One chain per (namespace, cell), delete-unread recompute, the access definition, and chunk times of 45/90 minutes. |
| BF2-5 | RESOLVED: `nice 19`, `MemoryMax` 2.5 GB, and the re-pilot runs with forward paper running. |
| BF2-6 | RESOLVED: integer ranks (299,997 and 4) and §3.5, §3.6 and §10 overridden with the new values. |
| BF2-7 | RESOLVED: Sharpe 0.5, 1.0 and 2.0 at 2k, with the mixed-null resolution disclosed. |
| BS2-5 | RESOLVED. |

## 2. Findings

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| BF3-1 | MAJOR | §13 item 6, "Pinned runtime" and "Start and resume"; A-V1 | **The checks need values that do not exist yet when the run starts.** Both canaries are "recorded on the server at the freeze". A-V1 records the reference vectors "at the D-19 freeze". Yet every start and resume of the threshold and development runs must pass "both canaries and the full frozen reference-vector suite" first. Those runs come before the freeze, so the expected values do not exist yet. This is the same ordering defect as BS2-1, moved to the runtime checks. The run-definition hash also leaves these values out, so the pre-freeze chunks are not bound to them. | §13 item 6: "Both canaries are recorded on the server at the freeze"; "On every start and resume … the full frozen reference-vector suite … must pass before any chunk runs". A-V1: "recorded at the D-19 freeze". | Record both canaries and the reference-vector expected outputs on the server **before the threshold run**, and include them in the run-definition hash. Carry them unchanged into the qualification object, which is how they become "recorded at the freeze" in A-V1's sense. Say that any later change to them voids the pre-freeze chunks. |
| BF3-2 | MAJOR | §13 item 6, "Integrity" versus "After a host change"; A-V1 | **Two rules contradict each other.**<br>• The runtime identity now includes the host CPU model, and "a chunk is accepted only if its recorded runtime identity equals the frozen one".<br>• The host-change rule says that after a CPU model change with the same dispatch features, "the chunks count".<br>Both cannot hold. The same conflict reaches C2's evaluation: A-V1 requires the "frozen runtime", and §13 says a machine with "the same CPU dispatch features" is enough. If the identity includes the CPU model, a C2 host on a different model fails `v_runtime_check`, and A-V1 voids the evaluation. Before the freeze there is also no "frozen one" to compare against (linked to BF3-1). | §13 item 6 bullets; `runtime_identity` | Split the identity into two parts.<br>• **Gating part:** image digest, dispatch features, platform, and the canary and vector results. This is what chunk acceptance and A-V1's "frozen runtime" compare.<br>• **Recorded-only part:** the CPU model. It is logged and disclosed, never compared.<br>Before the freeze, compare against the identity committed in the run definition. |
| BF3-3 | MINOR | §13 item 6, "Estimate" | **The escape's cost is understated.** "About 300" core-hours has to cover QJ's double cost, the threshold run, the reported-only runs and every escape. Each escaped cell adds 20k × 4.5 s, about 25 laptop-core-hours. The chance of escaping (1–2 development events) is 0.21, 0.43 and 0.58 at p = 2e-5, 5e-5 and 1e-4. At p = 5e-5, about 45 of 104 cells escape, adding about 1,100 hours (about 1,350 server-core-hours, roughly 1 extra month). | Exact binomial above | State the escape cost as a function of the `U_G` rate. Have the re-pilot's `U_G` measurement (now only in the thin categories) give an all-cells estimate of the escape fraction before the full-run go-ahead. Give the owner the duration range (about 3½–5 months). |

Nothing else new is wrong. The run-definition hash, the qualification-object order and the chain heads are coherent. The access definition is consistent with P18-6. The integer ranks, the tail count and the refusal arithmetic are correct.

## 3. Decided records

- **O18-4:** the change is correctly gated on a recorded O18-4-T answer. All other categories are kept.
- **P18-1:** |J_f| of at most 20, per owner direction 3. No conflict.
- **P18-6:** held-out independence is preserved, demotion and escape happen before the freeze, and "access" is now defined.
- **P18-7, A-U1, U-1:** the allocation is unchanged, and the escape is a choice of N, not a reallocation.
- **A-B7:** unchanged. The withdrawal is correct.
- **A-V1:** BF3-1 (when the vectors are recorded) and BF3-2 (what "frozen runtime" compares). Both need text fixes, not an amendment.
- **P18-2..P18-5:** no conflict found.

## 4. For the owner, in plain terms

1. The statistics are now right. A pass would mean what it says, and the new "bigger final run" rule removes most of the risk of losing test cases by bad luck.
2. Two small wording fixes are still needed in the server rules. The safety checks are told to compare against values that are only recorded months later, and one rule says a processor change voids results while another says it does not.
3. The bigger final runs may add up to about a month of server time if rare glitches turn out to be common. The trial run should measure this first.
