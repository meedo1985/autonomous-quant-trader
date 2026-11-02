# Sol re-check 5 of the R-14a lockbox module (850d49b, prompt at 881880f)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-sol`; session 01a19d72-fb3f-7640-974a-b64c31d3b675; 89,547 tokens), 2026-11-02, on the owner's Mac.
- Prompt: review/r14a-modules/RECHECK5_LOCKBOX_PROMPT_SOL.md.
- Finding IDs: R14L5-S-1, R14L5-S-2 (BLOCKER). Verdict: **FIX**.
- Adjudication: to follow, with the repairs.

## Report (verbatim)

## Verdict: FIX

The snapshot and startup-ID repairs address the two earlier worker failures for ordinary inputs. The new tests would catch the earlier ledger swap and a different startup ID. Two contract issues remain.

1. **R14L5-S-1 — BLOCKER.** [c2_lockbox.py:1219](/Users/pmp/aqt/autonomous-quant-trader/calibration/c2_lockbox.py:1219): The `Store` contract says the read gate uses the manifest hash *the request carries*. A caller could supply the same wrong hash in `request.manifest_sha256` and `manifest_sha256`; the worker’s comparison would pass, and a store following this wording could serve bars from that manifest. The contract also omits Annex D §D-3.7’s full check-record identity match and its requirement that `startup_check_id` name the matching PASS record. **Impact:** the documented store boundary does not establish the cycle’s manifest or this start’s entitlement. **Minimal correction:** state that the store obtains and checks the authoritative cycle manifest, matches all check-record identity fields to the sealing record and request, and resolves the check’s startup ID to the matching PASS record. This finding concerns the written contract; the store build itself remains an open item.

2. **R14L5-S-2 — BLOCKER.** [c2_lockbox.py:115](/Users/pmp/aqt/autonomous-quant-trader/calibration/c2_lockbox.py:115): `trial_seed` reproduces the frozen preregistration function instead of calling it. Its validation and hashed JSON bytes match on source inspection, but DRAFT R-14a item 4 explicitly requires the module to call an existing engine-commit function that implements a rule. **Impact:** byte equality does not establish compliance with that code binding. **Minimal correction:** make the frozen function callable on the qualified runtime and call it, or obtain an explicitly reviewed owner-approved exception before signing C2.

The ledger and file snapshots are used for both checking and computation; `screen.load` hashes installed source again before execution. The startup-ID comparison rejects a different record. Deriving `image_digest` from `started.signed` is sound within the stated `start()` contract. The CI globs cover all five lockbox test files on Python 3.14; source inspection and the reported green CI support the numpy-only import claim.

I did **not** run Haswell-pinned tests on this Mac or independently inspect CI run 41493979111. Ruff check, Ruff format, and `git diff --check` passed; no frozen paths changed in the scoped comparison. The store implementation, qualified-image vectors, and the other listed pre-signing items remain unverified. This read-only review made no commit, so the repository’s required committed review record is still outstanding.