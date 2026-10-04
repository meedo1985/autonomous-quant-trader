# Fable review BF2 of the D-19 preregistration §13 rev 7c at `09b0fb9`: SOUND WITH FIXES

Date: 2026-10-04. R19-2 independent statistical narrow re-review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. This is R19-2 independent statistical review BF2, run as a Claude Code subagent. It was read-only: no edits, no state-changing git commands, no data/ access. The only computation was in-memory exact-binomial arithmetic in `.venv` Python (scipy is not installed, so the binomial was coded by hand).

**Commit reviewed:** `09b0fb9` (docs/d19-recommendation). Scope: `git diff c09337f 09b0fb9 -- review/governance-statistics-amendment/d19-preregistration/`. That diff covers §13 rev 7c, the history rows and `ADJUDICATION_C09337F.md`. I read it against §1–§12 (rev 6) and Annex A clauses A-B7, A-U1 and A-V1. I also read D-18 O18-4 and P18-6/P18-7, `OWNER_DECISION_D20_V.md`, `V_BINDING.md`, and `runtime_identity`/`v_runtime_check` on branch `d19-calibration-engine` (`calibration/dsr.py`).

**Verdict: SOUND WITH FIXES.** I found no blocker. The certified false-pass and no-result claims are valid as written. Two MAJOR findings need text changes before the owner's acceptance: one on feasibility and one on whether the runtime can be recreated.

**Numbers I reproduced.** All use exact Clopper–Pearson, α = 0.025/M, and a held-out pass probability of 0.999 at N = 20,000.

- **Targets at M = 322–340:**
  - error: critical count 418 (417 at M = 340), τ = 0.017956 (0.017910);
  - DSR availability: 40, τ = 0.0012014;
  - `U_G`: 11, τ = 0.00020216;
  - QJ `P_0(E)`: 884, τ = 0.03988;
  - QJ `U_proc^R`: 148, τ = 0.00571.
- **Development at 12k (90% UCB):**
  - 0 `U_G` events gives 1.9186e-4, which passes; 1 event gives 3.2410e-4, which fails;
  - DSR availability passes with up to 9 events;
  - the error UCB is at most τ_err with up to about 196 events (rate 0.0163).
- **Threshold ranks:** 299,997 and 4 (binary64: 0.99999·n = 299997.0 exactly and 0.00001·n = 3.0000000000000004, so both formulas land correctly). Expected exceedance is 1.3333e-5 per tail and 1.0667e-4 over 8 tails.
- **Estimate:** 104 × 32,000 × 4.5 s = 4,160 h; +300 h ×1.2 gives about 5,400 h; ÷2 vCPU gives about 112 days.

## 1. BF1/BS1 resolution

| Prior finding | Status |
|---|---|
| BF1-1 / BS1-1 | RESOLVED. 12k development and 20k held-out are coherent, and the restated §5 step 2 can be satisfied. Side effect: see BF2-1. |
| BF1-2 / BS1-3 | RESOLVED in substance. A residual inconsistency remains (BF2-3). |
| BF1-3 / BS1-2 | RESOLVED. There are exactly 8 tails (6 at K = 1), the ranks are correct, inclusive ties keep (n+1−k)/(n+1) as a bound even for discrete statistics such as zero-day share, and the rate is called "expected". Residual stale text: BF2-6. |
| BF1-4 / BS1-4 | RESOLVED. The estimate is arithmetically consistent and labelled not measured. |
| BF1-5 / BS1-5 | (a)–(d) RESOLVED. (e) only PARTLY: the claim that the runtime can be rebuilt is overstated (BF2-2). |
| BF1-6 | Mostly RESOLVED. §10 still names an 80-trial screen (BF2-6). |
| BF1-7, BF1-8 | RESOLVED. |

## 2. Findings

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| BF2-1 | MAJOR | §13 item 3 (availability demotion), with the coverage rule in §3.2 | **Validity is fine; feasibility is fragile and not disclosed.**<br>**Why validity holds:** demotion happens in development, before the freeze. Held-out runs in its own namespace and certifies only the final cells. The mapping (§3.6) and the frozen thresholds use only final cells. The allocation is unchanged. This is not a P18-6 rescue, since cap-rule demotion is the same kind of step and was accepted in rev 6.<br>**Why feasibility is fragile:** rev 7c deleted rev 6's 40k fallback, so a single development `U_G` event demotes a cell even when that cell would almost surely pass held-out. Several O18-4 categories rest on only 2–3 cells at `T_C2`: QJ has 2 (and 2 family `U_G` tests per cell), Q1 unequal clusters has 2, Q2m has 3. Random demotions can therefore remove a whole category, and the method then fails coverage by noise, not by poor behaviour. | True rate p = 2e-5, 5e-5, 1e-4, 2e-4:<br>• P(demoted at 12k) = 0.21, 0.45, 0.70, 0.91<br>• P(held-out pass, ≤11 events at 20k) = 1.0, 1.0, 0.999999, 0.99909<br>QJ at p = 5e-5 per family: P(both QJ cells demoted) ≈ 0.49. | Choose one:<br>(a) Restore a held-out escape: development UCB of at most τ_G(40k) (computed at the actual M) lets the cell run at 40k held-out instead of being demoted. This costs only where it binds.<br>(b) Keep the rule, but disclose to the owner that one event demotes a cell, give the table above, and have the re-pilot measure `U_G` rates in the thin categories before the full run.<br>Either way, state that demoted cells are reported only from their development replications plus §9. |
| BF2-2 | MAJOR | §13 item 6, "Pinned runtime" and "Risk disclosed"; A-V1 | **(i) The runtime cannot be rebuilt on another machine as claimed.** `runtime_identity()` includes `cpu_features` (the hash of NumPy's dispatch features) and the platform. The lock file rebuilds the software, but not the CPU feature set. A-V1 voids every real evaluation, C2's included, if the frozen runtime "cannot be recreated". On a shared cloud vCPU host the CPU class is not under the owner's control. So the host-migration risk reaches past this run: it can void C2's evaluation.<br>**(ii) Security updates.** The text says they "may install, because the check below catches any change". The identity hashes only the interpreter and the NumPy/OpenBLAS binaries, and the canary is a BLAS matrix product. System glibc/libm is not covered, yet V squares through C `pow`. A libc update could change results without detection. If the check is extended to cover libc, any libc security update during a run of about 4 months would stop the run permanently.<br>**(iii)** `V_CANARY` was recorded on the Windows laptop, and nothing yet shows it matches on Linux. | `calibration/dsr.py`: `runtime_identity`, `v_runtime_check`; `V_BINDING.md` §3 ("Bit-reproduction on other hardware is not claimed"); A-V1 last sentence | Pin the whole userland in a container image by digest, including libc. Add a libm known-answer canary (pow/exp/log), or hash libc/libm into the identity. Hold package updates inside the image for the run. Replace "can be rebuilt on another machine" with "can be rebuilt on a machine with the same CPU dispatch features". Disclose to the owner that the C2 evaluation must run on such a machine. The re-pilot should confirm or re-record the canary on the server. |
| BF2-3 | MINOR | §13 item 2 versus §1 "C2's `g` must equal the frozen value" | For C2, a valid declaration already forces T = T_C2 (a g mismatch makes the declaration invalid). The only way to get T ≠ T_C2 is missing complete days, and that is ineligible under the floor reading as well. So A-B7-EQ only matters if the object is reused beyond C2. The same g/T event has two consequences stated in two places (invalid declaration, or ineligible window). Narrowing A-B7, an owner-decided Annex A clause, needs an owner decision record, not only a preregistration-acceptance item. | A-B7 (Annex A line 188); §1; §3.2 `T_C2 = 1247 − g` | Choose one: (a) state that the object certifies C2 only and drop A-B7-EQ; or (b) keep A-B7-EQ, record it as an Annex A decided clause (like A-U1/A-V1), and say which consequence takes precedence. |
| BF2-4 | MINOR | §13 item 6, run rules | (a) It does not say whether the hash chain is per (namespace, cell) or per cell; dev and held-out share cell ids. (b) It does not give the recovery for a missing or corrupt chunk; "stops the run" has no restart rule. It also does not say whether deleting a corrupt held-out chunk unread and recomputing it from its deterministic seeds is an "access". (c) P18-6 "access" is not defined: verifying the chain reads held-out bytes. (d) A chunk takes about 45 min at 5.4 s/rep and about 90 min in QJ, not "about 40 minutes". | P18-6 | Chain per (namespace, cell). A corrupt chunk is deleted unread and recomputed, and that is not an access. Define access as any display, export or aggregation of event content before the final reduction. Correct the chunk times. |
| BF2-5 | MINOR | §13 item 6, "Machine" | The calibration shares 2 vCPU and 4 GB with the forward-paper process. Two workers on 2 vCPU for about 4 months can starve it, or the OOM killer can kill it, which damages a separate evidence record. The estimate assumes 100% of both vCPUs. | Owner direction (shared server); BS1-5 memory concern | Run the workers at lowest priority with a memory cap, for example with `nice` and a systemd `MemoryMax`, so forward paper always comes first. Measure memory and throughput in the re-pilot while forward paper is running. |
| BF2-6 | MINOR | §13 items 1 and 4 versus §3.5, §3.6 and §10 | Stale rev 6 text is not listed as overridden:<br>• §3.5 "per-tail at most about 1.1e-5 … 1.3e-4" and "10⁶ samples";<br>• §3.6 "accepted with probability about 1 − 1.3e-4" (now about 1 − 1.07e-4);<br>• §10 "screen of an 80-trial set" and "up to 80 trials".<br>Also, the rank formulas should be bound in integer arithmetic (they happen to be correct in binary64). | §3.5, §3.6, §10 | Add these sections to the override list with the new values. |
| BF2-7 | MINOR | §13 item 5 | The power cells keep only a true Sharpe of 1.0. The owner, who trades his own capital, loses the curve at 0.5, which is the most decision-relevant point, even though it costs only about 15–30 core-hours at 2k replications. At 2k, mixed nulls have SE ≈ 0.0035 at 0.025, so they cannot detect excesses smaller than about 0.007. | §9; reported-only cost | Restore Sharpe 0.5 (and 2.0) at 2k replications. Disclose the mixed-null resolution. |

## 3. Decided records

- **O18-4:** dropping the "unequal `T`" category is correctly put to the owner (`<<OWNER O18-4-T>>`). The other categories are kept, subject to the BF2-1 feasibility risk.
- **P18-1:** `|J_f|` of at most 20 is the owner's direction 3. No conflict.
- **P18-6:** held-out independence is preserved, and demotion happens before the freeze. The definition of "access" is BF2-4.
- **P18-7 / A-U1 / U-1:** the allocation is unchanged (0.0035 + 0.0015 per family, 0.01 per cycle in QJ). Certification is in every final qualifying cell, as already precedented by the cap rule.
- **A-B7:** BF2-3.
- **A-V1:** BF2-2. This is the only substantive tension with a decided record.

## 4. For the owner, in plain terms

1. The repaired plan is statistically valid now: if it passes, the pass means what it says. It is not yet ready to accept, because two practical gaps need fixing first.
2. As written, a single rare glitch in a practice run removes a test case. A few groups have only 2–3 cases, so the whole calibration could fail by bad luck after months of running. A cheap rule change (a bigger final run only where needed) fixes this.
3. The results stay usable only if the exact same software and processor type can be used again for C2. A rented server can change hardware or install updates, so the software should be frozen in a fixed container image. The calibration should also be set to give way to your paper trading on the shared server.
