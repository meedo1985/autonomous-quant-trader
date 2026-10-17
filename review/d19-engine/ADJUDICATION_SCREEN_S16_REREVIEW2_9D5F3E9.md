# Adjudication: Sol re-review 2 of the screen §16 repairs at 9d5f3e9 (FIX, S16SR2-1..2)

Record: `SOL6_SCREEN_S16_REREVIEW2_9D5F3E9.md` (gpt-6-sol, effort high). Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Both findings were reproduced as described before repair.

| ID | Sev. | Decision | Repair |
|---|---|---|---|
| S16SR2-1 | High | **Accept, repaired.** `read` checked only that `chain_heads` was present. | `read` derives the chain keys `{ns}/{cell_id}` for every manifest cell and both `NAMESPACES`, exactly as `build`'s `_chains` does. It requires `chain_heads` to have exactly those keys, each a 64-hex digest, none equal to `chunks.GENESIS`. Tests: `{}`, a non-digest, and genesis heads are refused. |
| S16SR2-2 | High | **Accept, repaired.** `read` accepted a freeze without the fields `build` always writes. | `read` requires: `host_provenance_sha256` with the same chain key set and 64-hex values; `definition_commit` as a full 40-hex id; `threshold_started` as a timezone-aware ISO time; and `definition_committed_unix` as an int earlier than that start, which is the order `committed_before` enforces. `build` now refuses a non-full `definition_commit`, so writer and reader agree. Tests: each field missing, a short commit, a commit time after the start, and `build` with a short commit. |

**The checks left at the freeze, stated correctly** (correcting the first re-review adjudication):

- **Need the run's store:** that each chain verifies and has the recorded head (`_heads`); that each chain's host provenance has the recorded digest (`host_sha256`), separately from the heads; and that `choices.json` is a fresh `choose` of those chains.
- **Need the repository and the remote:** that `definition_commit` holds the definition bytes at its path; that its committer time is the recorded `definition_committed_unix`; that it is on a remote branch; and that the freeze-review record lists the later files with existing review records.
- **Outside both:** proof that the object's hash was posted publicly (QO-2 / HO-4, attempt procedure).

The reviewer accepted the per-job `runtime` record as worker evidence. Its note stands: the record is an environment probe, not proof of the loaded BLAS state. The pinned runtime itself is proven by `mapping.check_runtime` (canaries and runtime identity) in the parent.
