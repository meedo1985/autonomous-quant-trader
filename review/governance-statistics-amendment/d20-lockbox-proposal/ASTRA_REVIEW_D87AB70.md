# Codex Astra review of the D-20 lockbox proposal (d87ab70)

Prompt: `REVIEW_PROMPT.md`, plus one appended line telling the reviewer not to read `SOL_REVIEW_D87AB70.md` (the log shows it did not). Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a17881-5093-7722-aef6-254b436a21a6`, 124,964 tokens. It ran at HEAD 17cc7e0; PROPOSAL.md is unchanged since d87ab70.

**ID mapping:** the model could not see its exact variant and labelled its findings `D20LR-Codex-n`. The CLI header verifies gpt-6-astra, so **D20LR-Codex-n is recorded as D20LR-A-n** (n = 1..9).

Verdict: **FIX** (5 BLOCKER: A-1..A-5; 3 NON-BLOCKING: A-6, A-8, A-9; 1 QUESTION: A-7). Overlaps with Sol: A-2 = S-1 (model seed); A-3 ~ S-4 (key custody); A-5 ~ S-3 (w0 start is a choice); A-7 = S-8 (R-14 route); A-9 and S's Q4 note (drop hand-written Ed25519). New: A-1 (runner/metric interface), A-4 (exact record schemas).

## Report (verbatim)

**Verdict: FIX.** The statistical construction largely follows D-11 correctly. The proposal is not yet exact enough to adopt as an implementation contract: code interfaces, failure records, signing custody, and several purportedly “technical” choices need correction.

**Model disclosure:** my supplied session metadata identifies me as **Codex, based on GPT-6**, but does not expose an exact Sol/Astra variant. I therefore use `D20LR-Codex-n`; assigning `S` or `A` would invent metadata. The caller should attach the observed runtime model ID before counting this toward R19-2.

Reviewed [PROPOSAL.md](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL.md) at HEAD `17cc7e0758a3adf7417ff7ff5b7549c8fefb175f`; raw SHA-256 `2ea756b2a4aa36c1816d6a2788ff38dc93f840949e027f0a7b5c08772880918c`. I did not read `SOL_REVIEW_D87AB70.md`.

The authority distinction is sound: frozen v1.0 remains controlling; D-11, D-12, and D20_D13 are owner decisions awaiting their signed amendment; this document supplies proposed bindings only. R19-2 changes the statistical review process, not §16’s later human and different-model code-review requirements.

**What checks out**

| Consumer | Required binding | Assessment |
|---|---|---|
| L-1 | Daily difference returns; E-DIFF; 457-day resamples; `T_L ≥ q` | A3–A5 preserve D-11 |
| L-2 | `sqrt(365) × mean(d)/sample_sd(d) > 0` | B2 correctly uses the difference-series field |
| L-3 | Hourly BTC MDD difference ≤ 0.05 | Formula correct; code interface incomplete |
| L-4 | ETH E-IMPROV > 0 and ETH drawdown condition | Inherited binding correct; needs the same execution-to-metric bridge |
| Attestation | PASS only; three fields necessarily `positive/true/true` | B1–B2 preserve D-12 |
| Publication | Fixed release schedule, available-hour cooling-off, day-255 cap | B3/B5 correctly incorporate D-12, subject to complete records and storage |

Independent, in-memory checks under Python 3.14.7 established:

- A4 reproduced `bootstrap_indices` for `m=n=32`, purpose `paired_sharpe_ci`, replicates 0, 1 and 1999. The seed material and draw ordering also establish the general equality. **Equality requires changing the purpose for this comparison**; production `lockbox_prediction` intentionally produces another stream.
- The 457-length generator returned exactly 457 indices within the source bounds.
- Exact type-7 position is `1999/20`. Float64 interpolation fraction is `0.9500000000000028`. With order statistics 0.30 and 0.32, the repository returns `0.31900000000000006`; `0.319` fails equality against that threshold.
- A deterministic synthetic example gave block lengths **6.074176969115878** for D-11, **6.19174116118544** for the DSR rule, and **6.996148498744724** for E-IMPROV. A5 correctly distinguishes them. These checks establish implementation differences, not prediction coverage.

**Findings**

1. **D20LR-Codex-1 — BLOCKER — A1/A6: the proposed runner and metric do not connect.**  
   **Failure scenario:** A2 reuses `run_event_contract`, which returns `EventResult`. A6 binds public `max_drawdown`, which explicitly requires `BacktestResult`. Passing the former raises `MetricsError`; I reproduced this. Existing `screen.leg_stats` instead calls `_max_drawdown((1.0, *r.equity))`, and also requires E-IMPROV availability—making that entire helper unsuitable for BTC’s independently available E-DIFF.  
   **Minimal repair:** bind an explicit, validated `EventResult` conversion for daily returns and hourly equity. Reuse the existing drawdown kernel or specify an adapter, with exact agreement tests. Preserve D-11’s timestamp/completeness checks and separate BTC E-DIFF availability from ETH E-IMPROV availability. See [screen.py:1010](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/calibration/screen.py:1010) and [descriptive.py:126](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/metrics/descriptive.py:126).

2. **D20LR-Codex-2 — BLOCKER — A1/D20L-7: model-seed identity remains unresolved.**  
   **Failure scenario:** an implementation adopts A1’s seed 0 while the accepted D20_D13 decision preserves protocol l.266 for the nominee’s own fit. “Whatever the reviewed `walk_forward` passes” lets code determine a governance binding. A subsequent code review alone cannot authorize that substitution.  
   **Minimal repair:** settle the binding explicitly before adopting A1: retain l.266 and define its mapping to estimator seeds, or obtain an explicit owner decision changing it. Store the actual seed and its derivation in the nominee identity. D20L-7 correctly detects the conflict but understates it as merely wording.

3. **D20LR-Codex-3 — BLOCKER — B1/B4/Q4: signing and publisher custody are incomplete.**  
   **Failure scenario:** the signer host is lost or its key compromised after sealing. The proposal specifies neither recovery nor revocation, replacement authorization, treatment of previously issued certificates, or publisher behavior. A public-key hash alone also does not give the publisher the public-key bytes needed to verify signatures. D-12 expressly leaves the publisher identity and key for D-20.  
   **Minimal repair:** specify the public-key retrieval/check, signer access permissions, publisher authentication/permissions and verification environment, plus a short loss/compromise policy. A simple policy forbidding mid-cycle replacement and stopping promotion is admissible if its cost is disclosed and accepted. A general rotation service is unnecessary. This is missing operational policy, not a claim that the Constitution’s exchange-key rotation rule automatically applies here.

4. **D20LR-Codex-4 — BLOCKER — B2–B4: the promised record schemas are still field lists.**  
   **Failure scenario:** the worker crashes before producing `T_L` or either MDD. B4 requires those fields but gives no unavailable-value encoding or exact default-failure bundle. Independent implementations produce different commitment bytes. Likewise, “ascending hex floats” can mean lexicographic ordering, which is not numeric ordering for signed IEEE-754 encodings. The inherited upside field `k` remains undefined here.  
   **Minimal repair:** provide exact shapes for successful, unavailable and default bundles; define nullable values, reason enums, numeric decoding/order, `k` and tie handling, and the byte serialization used for vector hashes. Specify how step 2 atomically includes budget, exposure, default bundle and pre-read record. `ledger.append_entry` supplies a chain, not that multi-object transaction.

5. **D20LR-Codex-5 — BLOCKER — §1/Q1: “TECHNICAL means no real choice” is inaccurate.**  
   **Failure scenario:** the owner believes Q1 only acknowledges consequences of earlier decisions, while adopting a new baseline initial condition, retry policy, artifact-storage design and signing deployment arrangement. D11-16 explicitly says the confirmation baseline state was **not decided**. Matching the lockbox start state is a reasonable recommendation, not a logical necessity.  
   **Minimal repair:** distinguish **already decided**, **necessary implementation detail**, and **recommended new default**. Ask plainly whether both confirmation legs should start flat at `w0`, paying entry costs, rather than carrying prior holdings. Other engineering defaults can remain bundled if their consequences are stated. Do not promise that Q1 alone makes every row build-ready.

6. **D20LR-Codex-6 — NON-BLOCKING — A1/D20L-13: artifact validation conflates JSON and source bytes.**  
   **Failure scenario:** the stated retrieval sequence applies `json.loads(bytes)` to “each item,” including Python source, rejecting valid nominees. Separately, D20L-13 implies the current loader can execute substituted unchecked bytes; it actually hashes the bytes and compiles those same bytes.  
   **Minimal repair:** branch by artifact kind: canonical-JSON validation for trial objects; raw-byte hash and `check_code` for source. Describe the byte loader as enabling immutable-store retrieval. Preserve the current hash-before-execution behavior.

7. **D20LR-Codex-7 — QUESTION — D20L-3/Q3: R-14 creates a conditional placement constraint, not a demonstrated universal build stop.**  
   **Failure scenario:** the owner approves an amendment or delays the freeze because the proposal says lockbox code “cannot load anywhere today,” without establishing whether the engine commit is already fixed. R-14 explicitly permits engine-commit code and later object files.  
   **Minimal repair:** establish the relevant freeze state and distinguish confirmation prediction construction from the separate lockbox service. Include “engine module before the engine commit is fixed” when still available. If using a separately hashed module, define the narrow R-14 exception and dependency checks. Do not put lockbox orchestration inside `screen.py` merely to avoid a wording amendment.

8. **D20LR-Codex-8 — NON-BLOCKING — §1.3/Q2: narrow the seed assurances.**  
   **Failure scenario:** “nobody can search” and “effect is small” are read as stronger guarantees than established. Protection depends on the inherited beacon/channel assumptions; strategy/model-seed searches and outcome-dependent cycle retries remain possible. No bound establishes that quantile noise has a small effect near a pass boundary.  
   **Minimal repair:** say it prevents selecting the **realized lockbox bootstrap seed through pre-post cosmetic edits**, under the existing commitment/beacon assumptions. Retain the accepted retry caveat and absence of an across-retry probability bound. Remove “small.” Also specify A4’s seed variable for Q2’s old-seed alternative.

9. **D20LR-Codex-9 — NON-BLOCKING — §0/D20L-14/Q4: correct three supporting claims.**  
   **Failure scenarios:** an implementer treats 1,247 as the eligible source length despite C2’s gap; rejects reuse of a runtime checker for an incorrect reason; or treats handwritten RFC cryptography as a routine dependency-saving option.  
   **Minimal repair:** state `n = 1247 − gap_embargo.value_days`; 1,247 describes the full original partition. Say V’s checker is unnecessary for this non-V calculation, rather than inherently unusable because its expected canaries came from a particular machine. Remove handwritten cryptography as an ordinary option: RFC 8032 expressly describes its Python implementation as unsuitable for production. Ed25519’s deterministic signature construction itself is verified. [RFC 8032 §§6, 8.1–8.2](https://www.rfc-editor.org/rfc/rfc8032.html)

**Disposition of D20L-1…14**

- **Supported:** 1–2, 4, 6, 8 and 11. I independently confirmed the CRLF/LF hash discrepancy in 6.
- **Supported with qualifications above:** 3, 5, 7, 9 and 13.
- **10:** retaining a precise cap binding is correct. D-12 already chooses completion by day 255; remaining work should identify the timestamp anchor and remove conflicting wording, not reopen that choice.
- **12:** retry after a *definitively uncommitted* step 2 is consistent with D-11. An ambiguous acknowledgement must first be reconciled against the same evaluation ID; it is not evidence of non-commit.
- **14:** avoiding the V-specific checker is reasonable; the stated justification is too categorical.

The seed extension does not itself read lockbox data, consume another evaluation, bypass eligibility or authorize a descendant retry. It therefore creates no identified conflict with frozen anti-probing rules. It **does require** extending R-13 beyond the three streams authorized by D20_D13. A second beacon is unnecessary for the narrowly stated protection.

**Owner questions and simplification**

Q1 needs rewriting as finding 5 describes. Q2’s beacon recommendation is reasonable after narrowing its promise. Q3 needs the actual freeze state and complete alternatives. Q4’s maintained-library recommendation is reasonable; the missing owner-facing decision is what happens after signing-key loss or compromise.

Drop the handwritten cryptography option, avoid a general artifact-store framework when immutable hash-addressed files suffice, and avoid adding lockbox orchestration to `screen.py`. Preserve D-12’s chosen publication controls; simplifying those would reopen an owner decision.

Validation used read-only source inspection and in-memory deterministic probes (`python -X utf8 -B`), with no simulation or restricted data. The working tree remained clean; all 14 frozen sidecars, manifest hashes and Constitution self-hash checked successfully. Tests, lint, type and import-boundary suites were N/A because no implementation changed.

Nothing was written or committed. This response must be recorded with verified model metadata before it becomes a completed repository review record. Prediction coverage and the deployed signing/storage system were not validated; this review authorizes no implementation or lockbox access.