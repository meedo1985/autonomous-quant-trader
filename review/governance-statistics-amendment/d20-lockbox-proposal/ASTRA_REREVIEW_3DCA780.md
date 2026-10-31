# Codex Astra re-check of D-20 lockbox revision 2 (3dca780)

Prompt: `REREVIEW_PROMPT.md`, plus one appended line telling the reviewer not to read `SOL_REREVIEW_3DCA780.md` (it reports it did not). Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a1789a-0959-7653-9ab6-94f45ad82379`, 123,543 tokens. Ran at HEAD d65f4c6; PROPOSAL_REV2.md unchanged since 3dca780. The CLI's `-o` output file was empty (a model-list refresh timed out), so the report below is the final agent message copied verbatim from the CLI log.

Verdict: **FIX** (4 BLOCKER, 2 NON-BLOCKING). Findings D20LR2-A-1 .. A-6. First-round A-1, A-2, A-5, A-6, A-7, A-9 resolved; A-3, A-4, A-8 partly resolved. Overlaps with Sol's re-check: A-1 ~ S-2 (schemas/nulls), A-2 ~ S-1 (step-2 transaction), A-6 = S-3 + S-5 (cap). New: A-3 (replay vs whole-bundle commitment), A-4 (publisher auth, signer guard state, compromise review), A-5 (old-seed branch). Note: Astra judges the seed mapping resolved; Sol (S-4) says it is a new default for the owner.

## Report (verbatim)

**Verdict: FIX.** Revision 2 repairs the main statistical bindings, but its transaction, record and replay contracts remain incomplete.

I use the requested **Astra/A** identifiers. My visible metadata identifies Codex/GPT-6, without an exact variant; the caller must attach the CLI model metadata.

Reviewed [PROPOSAL_REV2.md](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md>) at HEAD `d65f4c65a763ac9b51bbe03ab406890b011cb68a`, raw SHA-256 `f84e7e444091f5b6cc8bb577515f0ceb9d2e02a0442e99e0a2d01d49cdaedea1`. I did not read `SOL_REREVIEW_3DCA780.md`.

Frozen v1.0 remains controlling. The owner decisions require signed C2 incorporation; this proposal and this review activate nothing.

**Disposition of my first-round findings**

| Finding | Status | Evidence |
|---|---|---|
| **A-1 — runner/metrics** | **Resolved at binding level** | A6 uses `screen.daily_returns` and `_max_drawdown((1.0,*equity))`, validates complete paths, and separates BTC E-DIFF from ETH E-IMPROV availability. Implementation must resolve the integer `EventResult.start` through its source `BarSeries` when checking UTC boundaries. |
| **A-2 — model seed** | **Resolved at binding level** | A1b preserves l.266, specifies the estimator mapping, records both seeds and requires identical confirmation/lockbox use. The seed-0 implementation remains an acknowledged build blocker. |
| **A-3 — custody** | **Partly resolved** | Public-key bytes, binding time, private-key custody and loss policy are supplied. Publisher authentication and trusted guard-state access remain unspecified; see A-4 below. |
| **A-4 — schemas/atomicity** | **Partly resolved** | Numeric ordering, nulls, vector serialization and upside ties are repaired. PASS/default schemas and transaction guarantees still fail; see A-1/A-2 below. |
| **A-5 — hidden choices** | **Resolved in substance** | Three labels replace “technical means no choice”; confirmation start state is separately presented in Q2. “DETAIL” still means a proposed convention requiring adoption, not a uniquely compelled value. |
| **A-6 — artifact kinds** | **Resolved** | A1a separates canonical JSON from raw source bytes and correctly describes existing hash-before-execution behavior. |
| **A-7 — R-14 placement** | **Resolved for the proposed layouts** | The recorded engine commit is fixed; later object files remain unfrozen. Both offered layouts keep the service separate. “Every route” should mean these layouts, not a theorem that R-14 prohibits service code in every existing object file. |
| **A-8 — seed assurances** | **Partly resolved** | §1.3 correctly narrows protection and removes the unsupported “small” claim. The old-seed alternative is named but contradicts A7’s unconditional verification; see A-5 below. |
| **A-9 — supporting claims** | **Resolved** | Source length includes the gap, handwritten cryptography is removed, and V’s checker is described as unnecessary. That reasoning applies to the statistical calculation; it does not waive pinned-runtime requirements for model fitting. |

**Remaining findings**

1. **D20LR2-A-1 — BLOCKER — B4, sealed-bundle schema and result rules.**  
   **Failure:** a successful result has no legal `cause_class`: `PERFORMANCE` requires a false condition, `TECHNICAL` requires a null, and `DEADLINE` is for the default. Conversely, the default’s null conditions satisfy the stated “TECHNICAL iff any is null” rule while its required class is `DEADLINE`. The default is committed before reading, but `read_start` is neither nullable nor defined as a logical authorization timestamp. Independent implementations cannot construct identical valid bundles.  
   **Minimal repair:** give explicit schemas/examples for PASS, performance FAIL, technical FAIL and DEFAULT. Define a PASS cause value or null, default precedence, timestamp semantics, and the computed-upside `reason` value. State float encodings for A7’s `q` and block fields explicitly.

2. **D20LR2-A-2 — BLOCKER — B4, step-2 atomicity and retry.**  
   **Failure:** two publishers both observe an unused budget and absent evaluation ID, then each appends a valid `1 → 0` entry. [`append_entry`](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/core/ledger.py:369>) serializes appends and verifies the chain; it does not enforce evaluation uniqueness or conditionally consume budget. Also, `verify_ledger` returns chain metadata, not an evaluation-ID lookup.  
   **Minimal repair:** require one serialized store transaction that checks evaluation absence and current budget, verifies the durable default-bundle reference, assigns its authoritative timestamp, and appends the entry. Reconciliation must inspect verified entries under the same concurrency contract. Add a duplicate-request/interleaving test; a general transaction framework is unnecessary.

3. **D20LR2-A-3 — BLOCKER — B4, later `verify_commitment` operation.**  
   **Failure:** the commitment covers the entire bundle, including original `read_start` and `finished`. A later replay with identical scientific outputs has different timestamps and therefore returns `MISMATCH`. The sole proposed operation neither supplies those original metadata nor defines an internal scientific comparison. This can falsely void a valid promotion under D-12 R-a.  
   **Minimal repair:** inside the sealed store, verify the original bundle against its commitment, then compare a precisely defined deterministic scientific projection against the replay. Preserve operational metadata separately and return only the permitted comparison result. Do not release the nonce or diagnostics.

4. **D20LR2-A-4 — BLOCKER — B1 permissions and Q5.**  
   **Failure:** naming “publisher” does not bind how the store authenticates that identity or restricts its writes. The signer is allowed to read its bundle and clock, but its inherited guard also needs trusted release state. Q5 additionally leaves unclear how compromised-key certificates already approved before discovery are validated during incident review. Approval before detection is not evidence that signing preceded compromise.  
   **Minimal repair:** specify a minimal publisher authentication/ACL binding and trusted state-query interface for signer guards. Make retained approvals conditional on successful incident reconciliation against trusted records. Keep replacement blocked unless C2 preauthorizes an exact replacement procedure; an ordinary signed incident record alone cannot silently replace the protocol-bound key.

5. **D20LR2-A-5 — NON-BLOCKING for the recommended route; blocks the alternative — A7 versus §1.3/Q3.**  
   **Failure:** the owner chooses `seed_l266`, but A7 always re-derives `seed_hex` from `family_seed_f` and `trial_id`; the valid alternative artifact is rejected.  
   **Minimal repair:** define a closed `seed_source` enum and dispatch verification according to the signed choice. Add one vector for each branch.

6. **D20LR2-A-6 — NON-BLOCKING — B3a/D20L-21.**  
   **Failure:** at `R_j = C − 72 h`, uninterrupted availability gives `E = C`; no decision satisfies `E ≤ t_dec < C`. The disclosure misses this equality case. The blanket “an action is valid only before C” also needs narrowing so it does not prohibit D-12’s explicitly permitted post-cap publication of an uncertified result.  
   **Minimal repair:** state `R_j ≥ C − 72 h` cannot promote under the strict cutoff, test equality, and distinguish promotion expiry from later result visibility.

**Statistical and source checks**

The affected consumer bindings remain correct:

| Consumer | Binding |
|---|---|
| L-1 | `T_L ≥ q`, with `T = √365 × mean(d)/sample_sd(d)`, daily `d = c − b`; 457-day bootstrap paths |
| L-2 | Same E-DIFF statistic, strictly `T_L > 0` |
| L-3 | Hourly BTC drawdown magnitude difference `≤ 0.05` |
| L-4 | ETH E-IMPROV `> 0`, plus the same ETH drawdown constraint |
| Attestation | PASS only; coarse fields consequently `positive/true/true` |
| Publication | D-12’s fixed releases, available-time cooling-off and cap remain controlling |

The estimator mapping is deterministic and compatible with l.266’s unspecified estimator conversion. It retains the low 31 bits; its range is exactly `0..2147483647`. Matching B4’s range does **not** mean using B4’s RNG derivation. No such equivalence is needed.

A7’s pre-look `d_sha256`, independent engine recomputation and sealing substantially repair provenance. They establish consistency with recorded inputs under the trusted-engine assumption, not prediction coverage.

Independent in-memory checks reproduced:

- Type-7 example: `q = 0.31900000000000006`.
- Drawdown on `(1.0, 0.8, 0.9, 0.6)`: `0.4`.
- E-DIFF available while E-IMPROV is unavailable, and the reverse.
- Identical scientific values with changed run timestamps produce different whole-bundle commitments.

For **D20L-15..21**: 15 correctly identifies the seed-0 conflict, but seed-invariance tests must cover supported configurations and have an explicit failure disposition; 16’s adapter direction is correct; 17’s verifier-mode distinction is supported by the cited local README; 18 appropriately leaves the calendar anchor for adoption/S4; 19’s recorded engine/object facts check out; 20 supplies the needed provenance field; 21 needs the equality correction above. The qualification-definition hash matches `FULL_RUN_START_EVIDENCE.md`. Freeze status was checked from repository evidence, not the server.

**Owner questions and simplification**

Q2 is clear and fair. Q1 should describe detail rows as proposed implementation conventions. Q3 needs its alternative made executable. Q4 is fair when its architectural assumptions are explicit. Q5 is useful but needs the operational rules in A-4 before adoption. The anchor must also govern day 180 consistently; D11-15 remains an S4 decision.

Drop the unfinished mid-cycle key-replacement option, a general artifact framework, and any second beacon. Replace whole-bundle replay comparison with the narrow sealed comparison above. Preserve D-12’s adopted publication controls.

Read-only checks found a clean worktree, unchanged bound engine sources, and **28/28 trusted frozen files, 14/14 sidecars, Constitution self-hash and manifest/protocol bindings passing**. Numerical probes used Python 3.14.7 with `-B`; direct preregistration import lacked `jsonschema`, so its seed formula was checked independently. Tests, lint, types and import-boundary suites were N/A because no implementation changed.

Nothing was written or committed. No simulation, restricted data or deployed custody system was tested. The caller must commit this complete record with verified model metadata before counting it as a completed repository review.
