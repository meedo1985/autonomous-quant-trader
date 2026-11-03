# D-12 decision proposal, revision 3 (delta on revision 2)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per this session's metadata. I am an AI reviewer, not an authority.

**What it revises:** `PROPOSAL_REV2.md` (reviewed at `9022549`). It answers `SOL_REREVIEW_9022549.md` (gpt-6-sol, FIX, D12R2-S-1..4) and `ASTRA_REREVIEW_9022549.md` (gpt-6-astra, FIX; its report labels its findings `D12R2-S-n`, and the record header maps them to **D12R2-A-1..4**, used here). I read both in full.

**How to read it:** a delta. Every rev 2 section not restated below stands unchanged. Restated sections replace rev 2's in full.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `597d707`. The agent wrote only this one new file, at the caller's explicit instruction. (The agent definition in this worktree still lists `Write` as disallowed; the version on `main` after PR #79 allows one new report file by owner decision of 2026-10-25. I followed the caller's scope.) Nothing was staged or committed. No frozen file, hash or sidecar was touched. No simulation; no confirmation, lockbox, network or credential access.

**Status: INACTIVE PROPOSAL.** It needs an owner decision on Q1-Q5 and then the owner's signed C2 §4 amendment before it binds anything. Nothing frozen changed.
**Review status:** revision 3 is unreviewed. R19-2 requires a focused re-check by two model families before the owner decides.
**VERDICT: `AMENDMENT_REQUIRED`** (unchanged). R-b (Q4) is **not available under C2 as drafted**; §6' states the two extra bindings it would need.

## 0. Verification run

- **Citations, both ways (item 1).** Re-read: protocol l.74-76, l.87-91, l.296, l.300; Constitution §7 l.73-85, §13 l.122-124, §26 l.191, §27 l.194; DRAFT l.217-244 and l.325-326; `THREAT_MODEL_v1.md` l.9, l.13, l.17. Topic search added one uncited clause: **DRAFT l.221-222 sets `max_evaluations_per_family_per_cycle: 1`** ("no replacement"). Rev 2's R-b relied on v1.0 l.74 (value 2) and missed that C2 itself lowers it (self-finding D12-17).
- **Referents (item 2).** D-11's sealed artifact holds "(q, n, b, stream identity, artifact hash)" (`d11-proposal/PROPOSAL_REV3.md` l.41), adopted by `OWNER_DECISION_D11.md` l.16-24 (type-7 5th percentile, 2,000 attempts, l.19-20). D11-15 (which timing rule governs) is sent to the S4 draft (l.28); this revision uses DRAFT l.229-231 and l.244 as written.
- **Bytes (item 3).** `schemas/attestation.schema.json` SHA-256 `43e975bf…0ab9c2fa`, equal to its sidecar (re-run at `597d707`).
- **Exact arithmetic (item 8), computed with `fractions.Fraction`:** for n = 2,000, the type-7 position is h = 1999·p. For p = 1/20, h = 99 + 19/20; for p = 19/20, h = 1899 + 1/20 (0-based order statistics). IEEE check: `NaN <= x` and `NaN > x` are both false, so an unguarded rank gives `k = 0` and the flag `false` (Astra A-3 confirmed). Schedule arithmetic is in §6'.

## 1. Disposition of re-check findings

Overlaps: S-1 ≈ A-2 (release envelope); S-3 ≈ A-1 (audit schedule); S-4 ≈ A-4 (Q3 consequence); S-2 (crash recovery) and A-3 (upside unavailable) are single-reviewer.

| ID | Disposition | Evidence | Repaired in |
|---|---|---|---|
| S-1 / A-2 | **Accepted.** Rev 2's index mixed fields visible before and after release, let a crash before step 4 lack a commitment, and bound no certificate timestamp. A completion-dependent `cooling_off_start` would leak timing even with a fixed release. The pre-read reason code is not lockbox-derived (decided before any byte is read), but it is a disclosure, so it now goes to the owner explicitly. | rev 2 l.67, l.71, l.109; §13 l.124; §7 l.79 | §3', Q2 |
| S-2 | **Accepted.** Rev 2 step 6 named no recovery actor or transaction and did not fence a late worker. | rev 2 l.109 | §6' |
| S-3 / A-1 | **Accepted, with a stronger result.** Under C2 as drafted, R-b is infeasible on two grounds: the one-evaluation limit (DRAFT l.222), and the 30-day cooldown if it applies to every read (last release day 277+g > 255). A feasible schedule exists only with two further C2 bindings. Astra's points on concurrency, unconditional start and certificate IDs are bound. | protocol l.75; DRAFT l.222, l.229-231, l.243-244 | §6', Q4 |
| S-4 / A-4 | **Accepted.** "Every post-read FAIL is `LOCKBOX_FAIL`" is a proposed binding (P-3), not frozen. It can bar a descendant with no performance result. Q3 now says so, and says why the alternative leaks. | §7 l.85; protocol l.296 | §5', Q3 |
| A-3 | **Accepted.** Upside logging gets an availability guard, a sealed not-computed form and a same-vector rule. | protocol l.89; §0 NaN check | §7' |
| Sol side note (vector vs D-11) | **Accepted, with a self-correction.** Rev 2 l.119 said D-11's artifact "cannot reconstruct a rank". That overstates it: the replicates could be regenerated from the stream identity and the confirmation series. Storing them is the simpler checkable route. It extends D-11's adopted artifact list; it does not change q. | d11 REV3 l.41 | §7' |
| Sol side note (Q1 FAIL alternative) | **Accepted.** That alternative now has an unavailable-value rule and a stated consequence for Q2. | rev 2 l.129 | Q1 |
| Astra Q2 note | **Accepted.** "Technical" includes data-dependent unavailability. | rev 2 l.86 | Q2 |

Totals: 8 findings plus 3 side notes. 8 accepted, 0 in part, 0 rejected.

**D12R-A-1..8 (Astra's first round, not re-checked by Astra):** my self-check is that all eight remain resolved. A-1 (P-1 unchanged); A-2 (O-4 correction stands, and Q2 is extended); A-3 and A-4 (strengthened by §3' and §6'); A-5 (now with explicit P-3); A-6 (R-b now costed honestly); A-7 (Q1-Q5 restated); A-8 (§7' adds the unavailable case). This is a self-check, not a reviewer re-check.

## 3'. Who sees what, and when (replaces rev 2 §3)

**Working rule (unchanged):** whatever the owner sees counts as research-visible.

**Index: two entries per read, each with a fixed shape [AI default; D-20 implements].**

| Entry | Written | Visible from | Fields (the same for every outcome) |
|---|---|---|---|
| **Pre-read entry** | step 2, before any lockbox byte | immediately | evaluation ID; family; nominee ID; prediction-artifact hash; scheduled release time `T_r`; EXPOSED mark; under R-b, the linked audit evaluation ID |
| **Release entry** | once, by the publisher (§6'), at `T_r` | `T_r` | evaluation ID; `result ∈ {PASS, FAIL}`; `released_at = T_r` (the scheduled value, never a clock reading); `commitment` (always 32 bytes, §6'); `attestation_ref` (present on PASS only; this field *is* the PASS bit) |

- A post-read technical failure, a crash before step 4, a missed `T_r` and a performance FAIL all produce byte-for-byte the same release-entry shape, with a commitment present.
- Nothing else about a read is visible before `T_r`: no progress, heartbeat or partial entry.
- **Pre-read rejection** produces a separate entry, `PRE_READ_REJECTED`, with a fixed reason code and no EXPOSED mark. Its content is decided before any lockbox byte is read, so it carries no lockbox information. It is still a disclosure, and Q2 asks the owner to authorise it.
- **Certificate timestamps.** `cooling_off_start := T_r`, exactly as written at step 2. The attestation carries no other time. D-20 picks a **deterministic signature scheme with no embedded time**. Then every attestation field is fixed by step 2 except the signature, which reveals nothing about completion time. The 72-hour cooling-off (protocol l.300) runs from `T_r`.
- **No earlier certificate access.** A signed attestation lives in the sealed store, readable only by the `lockbox_eval` identity, until the release entry references it. The owner and promotion tooling get it only through that entry.
- **Commitment (unchanged rule):** `SHA-256(nonce ‖ canonical bundle bytes)`, with a 256-bit nonce kept only in the sealed store.

**Disclosure bound (restated precisely).** Lockbox-derived information reaching research is (i) PASS/FAIL per read, plus (ii) the D12-3 cycle-label bit (Q2), and (iii) under Q1's alternative, the FAIL fields. Publisher delays are independent of the outcome (§6'), and so are pre-read rejections.

## 5'. Cross-family descendants (replaces rev 2 §5, second bullet; rest unchanged)

**Proposed C2 binding P-3:** "For Constitution §7 l.85 and protocol l.296, every lockbox outcome released as FAIL is a `LOCKBOX_FAIL`, including a post-read technical failure and, under R-b, an audit disagreement. A pre-read rejection is not a read and is not a `LOCKBOX_FAIL`."

- **Consequence.** A crash or signing failure in the trend read bars a descendant volatility nominee (`BARRED_DESCENDANT`, no read), even though no performance failure was shown.
- **Why not the reverse.** If a technical failure did not count, the descendant would be read after a technical FAIL and barred after a performance FAIL. Research would see which happened, per read, and §7 l.79 would be broken.

## 6'. Accounting order, publication, recovery and reproduction (replaces rev 2 §6)

**Actors.** The *worker* (the read and compute) and the *publisher* (a separate scheduled job) both run under the `lockbox_eval` identity (THREAT_MODEL l.9). The publisher is the **only** writer of release entries. The index accepts at most one release entry per evaluation ID.

**State machine per evaluation, in the append-only store (§26), with compare-and-set transitions:** `OPEN → READY` (worker) or `OPEN → CLOSED` (publisher), then `→ RELEASED` (publisher).

1. Pre-read verification (D-11 REV3 item 3, plus §7' vector check). If it fails, write a pre-read rejection and stop.
2. Durably write and confirm: the evaluation ID(s), the budget decrement(s), EXPOSED, `T_r = read start + p` (p = 7 days [AI default]), state `OPEN`, and a **default failure bundle** with its commitment (cause class plus the step-2 record, with its own nonce). If the write fails, no read happens.
3. Read and compute; capture hashes, commit, image, seeds, streams and outputs; compute twice (a determinism check only).
4. Write the sealed bundle and its commitment.
5. Only if L-1..L-4 all PASS and P-2 holds: request a signature. The signing service signs only while the state is `OPEN`.
6. Worker: CAS `OPEN → READY`, referencing the bundle commitment and, on PASS, the attestation. This must land before `T_r`. If the CAS fails because the state is `CLOSED`, the worker's outputs are void. They are logged in the sealed store and never published. A signature not referenced by a `READY` record is void.
7. Publisher at `T_r`: CAS `OPEN → CLOSED` if still `OPEN`. It then appends the release entry: from `READY`, the worker's result and commitment; from `CLOSED`, `FAIL` with the default bundle's commitment (a post-read technical failure, never retried). Last, CAS to `RELEASED`.
   - Both branches do the same work: one CAS and one append, with everything prepared at step 2. So publisher timing does not depend on the outcome.
   - If the publisher itself fails, it restarts and repeats step 7 idempotently. The entry still says `released_at = T_r`, the actual time is logged only in the sealed operational log, and the delay is an incident (§26).

**Reproduction (owner choice, Q4).**
- **R-a (unchanged).** Full capture at step 3; independent re-execution after the segment rolls into confirmation (§7 l.81); a mismatch voids the promotion (§27 l.194).
- **R-b, schedule check.** Let the nomination look be day 180 (worst case, DRAFT l.229), g = days of pre-lockbox gate processing before the first read, p = 7, cooling-off = 3 days, cap = day 255 (DRAFT l.231, l.244). Four reads: trend primary and audit, then volatility primary and audit.
  - *Cooldown on every read (strict reading of l.75):* reads on days 180+g, 210+g, 240+g, 270+g. The last release is on day 277+g, which is after 255 for every g ≥ 0. **Infeasible.** It would need the window raised from 75 to at least 97+g days, which reopens owner decision O-2.
  - *Per-family cooldown, primaries 30 days apart, each audit with the other family's primary:* puts a trend read and a volatility read on the same day. That breaks C2's own cross-family cooldown (DRAFT l.243). **Infeasible as drafted.**
  - *Audit concurrent with its own primary, families 30 days apart:* trend pair on day 180+g, volatility pair on day 210+g. Releases on days 187+g and 217+g, cooling-off ending on day 220+g. **Feasible iff g ≤ 38** (g ≤ 35 if cooling-off must also end by day 255). That is the same calendar as R-a, so no extra delay.
  - **Extra C2 bindings this needs:**
    - (i) `max_evaluations_per_family_per_cycle: 2`, defined as one primary plus one audit of the same nominee and sealed artifact, with no replacement. This amends DRAFT l.221-222; the value equals v1.0 l.74's 2 but not its meaning.
    - (ii) "The l.75 cooldown does not apply between a primary and its own audit." This is an exception to a frozen anti-re-probing control that DRAFT §4 says stays in force, so only the signed amendment can grant it.
  - **R-b rules:**
    - Both reads are fixed at step 2, before any byte, and the audit runs unconditionally, whatever the primary shows.
    - There is one `T_r` for the pair.
    - If the two runs' scientific bytes differ, the result is a post-read technical failure (and a `LOCKBOX_FAIL` under P-3).
    - The attestation's single `lockbox_evaluation_id` is the primary's. The audit ID is linked in the pre-read entry and in the bundle.
  - **Cost:** two reads, budget charges and log entries per family; two extra amendment clauses; and one more component under §16 review. Without (i) and (ii), R-b is unavailable.

## 7'. Upside exceedance (replaces rev 2 §7)

Protocol l.89 says "logged, does not fail". **Proposed binding P-4 [AI default; D-20 implements]:**
- **Artifact.** D-11's sealed artifact (d11 REV3 l.41) also stores the 2,000 replicate values, sorted, and the artifact hash covers them. This extends D-11's adopted list; q is unchanged.
- **Pre-read vector check (step 1).** The check confirms that there are 2,000 values, all finite, in ascending order, and that D-11's reference type-7 function returns, bit for bit, the sealed q at p = 1/20 (h = 99 + 19/20). A failure is a pre-read rejection, with no lockbox byte read. This is how "same vector" is enforced.
- **Sealed record `upside`:** `{status: COMPUTED | NOT_COMPUTED, k: int | null, exceeds_p95: bool | null, reason: enum | null}`.
  - `COMPUTED` only if `T_L` is finite and available. Then `k = #{v_i ≤ T_L}` and `exceeds_p95 = T_L > type-7 p = 19/20` of the **same** vector (h = 1899 + 1/20).
  - Otherwise `NOT_COMPUTED`, both values `null`, and a reason class. NaN comparisons are never evaluated.
- **Readers:** the sealed bundle only. It is no gate, and it is never shown to research, the attestation or the index. The 95th percentile remains an [AI default].

## 8'. Owner questions (replace rev 2 Q1-Q5)

Choosing "keep blocked" on Q1-Q4 means C2 cannot be signed yet. Q5 can be deferred without blocking.

**Q1. What does a lockbox result tell you?**
- **"PASS or FAIL only (Recommended, if you accept Q2)."** The three items appear only on a PASS certificate, where they always read "positive / yes / yes". On a FAIL you learn nothing about which test failed.
- **"Also show me the three items on a FAIL."** Each item shows its value or "unavailable" when it could not be computed (a crash shows all three "unavailable"). You get a partial diagnosis: there is still no ETH item and no reason. Because you work with the research AI, research learns it too, and "unavailable" reveals a technical breakdown on every read, so Q2's "plain FAIL" option can no longer close that leak. It needs explicit C2 disclosure wording.
- **"Keep blocked."**

**Q2. Two things research may learn beyond PASS/FAIL. Allow them, written into C2?** (a) When the other family has no result, the end-of-cycle label shows whether a FAIL was a technical breakdown. "Technical" includes failures caused by the data itself, such as a zero-variance or non-numeric result on the real lockbox path, so this bit is not fully independent of the data. (b) A rejection *before* any lockbox data is read shows a fixed reason code; it says nothing about the lockbox.
- **"Allow both, stated openly in C2 (Recommended, conditionally)."** At most one data-linked fact per cycle, written down rather than hidden.
- **"Count a technical breakdown as a plain FAIL."** This closes (a). A broken run could then end the cycle as `NO_EDGE_FOUND` and open the baseline path, and draft l.82 changes.
- **"Keep blocked."**

**Q3. If one family's pick is built on the other's, and the earlier one's lockbox result is FAIL, what happens?**
- **"The later pick is not read, and any FAIL counts, including a technical breakdown (Recommended)."** This applies the frozen no-descendant rule, and C2 must state that a technical FAIL counts. Cost: a crash in the first read can stop the second pick even though nothing showed it was bad. The alternative would show research which kind of FAIL happened.
- **"Do not allow related picks at all."** A new C2 eligibility rule; the bar then never arises.
- **"Keep blocked."**

**Q4. How is the lockbox result checked for reproducibility?**
- **"Record everything; re-run later once the period becomes confirmation data (Recommended, conditionally)."** It uses no extra lockbox read. Cost: if the later re-run does not match, an already approved promotion is voided.
- **"A second, counted audit read at the same time as the first."** Catches problems before the certificate is signed, with no extra days. Cost: C2 must allow two reads per family and waive the 30-day wait between a read and its own audit (an exception to a frozen anti-probing rule), and every read counts. With the 30-day wait kept, it does not fit in the 75-day window.
- **"Keep blocked."**

**Q5. May anyone open the sealed details (the margin, the drawdowns) later?** Unchanged from rev 2:
- **"No, sealed and machine-checked only (Recommended)."** The details are not secret forever: prices are public, and the period becomes confirmation data.
- **"I may open them after C2 ends."** That reaches research through you, so it needs explicit wording.
- **"Decide later."** They stay sealed until you decide. C2 is not blocked.

## 9'. Additions to "what D-20 must bind" (rev 2 §9 stands)

- The two-entry index shapes.
- `cooling_off_start := T_r`, and a deterministic, timeless signature scheme.
- The state machine, its CAS fencing, the default failure bundle and the sole-publisher rule.
- P-3.
- P-4 with the vector check.
- Under R-b only, bindings (i) and (ii) and the audit link.
- Unchecked: whether THREAT_MODEL l.9 ("lockbox read + attestation signing only") covers the publisher job. D-20 and §16 must confirm that.

## 10'. New findings (numbering continues rev 2)

- **D12-12 NON-BLOCKING.** The uniform release envelope and timestamp binding (§3').
- **D12-13 NON-BLOCKING.** Publication fencing and recovery (§6').
- **D12-14 QUESTION (Q4).** R-b is infeasible under C2 as drafted; feasible only with bindings (i) and (ii).
- **D12-15 QUESTION (Q3).** P-3, technical FAIL as `LOCKBOX_FAIL`.
- **D12-16 NON-BLOCKING.** P-4 availability and same-vector rule, and the correction of rev 2's "cannot reconstruct".
- **D12-17 NON-BLOCKING (self-finding).** Rev 2's R-b reason ("within the frozen limit") ignored DRAFT l.222.

**Remaining:** the R19-2 re-check of this revision; owner Q1-Q5; signed C2 §4 wording for P-1 to P-4, §3', §4, §5' and §6'; D-20; §16. **Still unauthorized:** frozen edits, activation, code, simulation, confirmation or lockbox access, promotion and trading.
