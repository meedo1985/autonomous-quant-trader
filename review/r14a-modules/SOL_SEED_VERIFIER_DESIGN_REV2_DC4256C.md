# Sol re-review: seed verifier design rev 2, at dc4256c

- Reviewer: Codex CLI v0.164.0, model `gpt-6-sol` (command line and session header),
  reasoning effort high, sandbox read-only, session `01a1bfc3-e969-75e2-a5ac-189228ac37c7`,
  2026-11-09. Exact deployment ID not exposed by the reviewer. Tokens: 109,837.
- Prompt: `review/r14a-modules/SEED_VERIFIER_DESIGN_REV2_PROMPT_SOL.md`. Author: Claude Opus 5.5.
- Independent feedback, not approval. Adjudication: `ADJUDICATION_SEED_VERIFIER_REV2_DC4256C.md`.

## Reviewer output (verbatim)

**Verdict: FIX.** This is independent design feedback, not approval. Rev 2 improves the line-266 route and reuses an accepted FP3 verifier, but the proposed record still does not provide an unambiguous, independently checked authority for the BLS result.

### Findings

**SV2-S-1 — BLOCKER — §§4–5, ledger authority.** Two valid `beacon_verification` entries could name different record hashes; the loader could choose either. [`aqt.core.ledger`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/ledger.py:282) verifies a chain’s internal integrity, but does not select a governing entry or prevent a different intact chain from being presented. Naming the entry *type* in signed C2 therefore does not remove caller choice. R-14a item 7 requires governing records, never caller values. **Correction:** bind the ledger identity and a deterministic entry-selection rule in signed C2, tie the selected entry to this post, protocol and round, and have the loader verify that binding before any gate.

**SV2-S-2 — BLOCKER — §§3.4–3.5, 5, verifier evidence.** A fabricated record can claim the pinned script and lock hashes, a CI identity and `ok: true` without those bytes having run. The ledger preserves that claim; it does not attest execution. Reinstalling dependencies from the lock also does not establish which `verify.mjs` bytes CI executed. R-14a item 7 and Constitution §27 require a verified signature and reproducible provenance. **Correction:** retain independently authenticated CI run evidence binding the actual script bytes, lock, runtime, input hashes, exit code and output; require the consumer to verify that evidence. OD-1 cannot be accepted on the present record alone.

**SV2-S-3 — BLOCKER — §2, lazy import.** The import-time claim is supported by the inspected frozen code: `preregistration.py` imports [`ledger.py`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/ledger.py:46), [`paths.py`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/paths.py:1) and [`manifest.py`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/data/manifest.py:47), which imports `bars.py`; none uses a `jsonschema` name at import time. Those names are used in `_validate_against_schema`, not [`trial_seed`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/preregistration.py:253). The gap is sequencing: if the R-14 code scan runs at startup and `derive_seeds` imports `preregistration` later, its bytes and transitive imports evade that scan. The “if `jsonschema` is importable, import normally” branch could also admit an unpinned library on an altered search path. R-14 and R-14a items 2–3 require the allowed bytes and imports to be verified before protected-data access. **Correction:** perform and byte-check this import before that access, use the placeholder only on the qualified image, and restore `sys.modules` on every exit path. Test the actual qualified-image path. The temporary placeholder appears feasible for `trial_seed`; its admissibility under “nothing else is loaded” remains an owner interpretation, not an established pass.

**SV2-S-4 — BLOCKER — §§3.5, 4, failure timing.** “Either fails, errors, round not available” is mapped to `seed_disclosure.failure`. A bad relay response or temporary CI failure on day one could therefore invalidate C2 while a valid copy is obtainable before day seven. FP3 permits copies from any source and imposes **no time limit for D-19**; C2’s draft instead invalidates if no verifying output exists within seven days. Those rules must not be merged. **Correction:** distinguish a failed fetch or verifier attempt from the C2 deadline outcome, permit verification of valid copies through that deadline, and specify the evidence used to establish the deadline outcome. A pushed valid record can demonstrate timely existence; absence of that record alone does not prove nonexistence.

**SV2-S-5 — BLOCKER — §§3.5, 5, 7, consumer checks.** The proposed §5 checks do not bind `responses[*].sha256` to the committed raw files, identify which response each verifier used, check the chain-info file bytes, establish two distinct relays, recompute `scheduled_time`, or validate an authenticated CI job and its actual exit status. A record with invented response provenance and two copied success objects can satisfy the listed comparisons. R-14a items 5 and 7 require an exact input-to-record contract and verification against governing records. **Correction:** define and test those links and strict field types at the consumer boundary, including the full verifier result rather than `ok` alone.

**SV2-S-6 — NON-BLOCKING — §§3, 5 versus the parent design.** [`DESIGN.md` §5.1](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:203) still describes BLS verification inside the confirmation module, whereas rev 2 uses an external record. A builder following the parent design could implement the wrong route. R-14a item 5 requires one exact module contract. **Correction:** reconcile the parent design and signed contract before implementation.

### Rev 1 disposition

| Finding | Status at design level |
|---|---|
| SV1-S-1, authoritative hash | **OPEN** — entry selection is still unbound. |
| SV1-S-2, self-asserted verification | **PARTIAL** — FP3 reuse helps; execution evidence remains self-asserted. |
| SV1-S-3, qualified-image line 266 | **PARTIAL** — the real function moves inside; import ordering and OD-2 remain. |
| SV1-S-4, authenticated inputs | **PARTIAL** — sources are named; response and ledger bindings remain incomplete. |
| SV1-S-5, BLS message | **CLOSED** — rev 2 specifies the bytes and uses the FP3 verifier. |
| SV1-S-6, lockbox handoff | **CLOSED as a design route** — §6 specifies sealing-to-request provenance; it is unimplemented. |
| SV1-S-7, NumPy and mixed check | **CLOSED as a design route** — verifier reuse removes the new Python environment and §5 splits the local check. |
| SV1-S-8, seven-day evidence | **PARTIAL** — a dated push is proposed, but its verification and failure meaning are unresolved. |

### Owner items

- **OD-1:** Defer acceptance until SV2-S-1, S-2 and S-5 are repaired and signed C2 explicitly states how authenticated external verification satisfies item 7.
- **OD-2:** Consider conditional acceptance of the placeholder after the pre-read import and byte checks in SV2-S-3 pass on the qualified image.
- **OD-3:** Do not accept the entry-type and GitHub-push wording as written; resolve SV2-S-1 and S-4, including durable, independently checkable push-time evidence.
- **OD-4:** Accept adding genesis and period alongside the exact FP3 hash, key and scheme, subject to checking the final signed C2 bytes and FP3 binding. FP3’s owner acceptance applies to D-19; it does not itself decide C2’s deadline.

**Review limits and gate:** I reviewed commit `dc4256cd`, the local frozen import and ledger code, and the FP3 files on `origin/freeze-sheet`. The working tree and index were clean; `git diff --check HEAD^ HEAD` passed; this commit changes only two review documents; all 14 current protected sidecars matched their files. Code tests, lint, types and import-boundary runs are N/A to this document-only change. I did not run the verifier or qualified image, authenticate a future CI run or GitHub push, inspect restricted data, or verify future signed C2 bytes. This read-only workspace prevented writing and committing this review record, so the repository’s recorded-review gate remains open.
