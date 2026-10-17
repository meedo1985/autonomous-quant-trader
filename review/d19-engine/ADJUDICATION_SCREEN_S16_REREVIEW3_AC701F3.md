# Adjudication: Sol re-review 3 of the screen §16 repairs at ac701f3 (FIX, S16SR3-1..2)

Record: `SOL6_SCREEN_S16_REREVIEW3_AC701F3.md` (gpt-6-sol, effort high). Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. The reviewer found S16SR2-1 and S16SR2-2 resolved.

| ID | Sev. | Decision | Repair |
|---|---|---|---|
| S16SR3-1 | Medium | **Accept, repaired.** Confirmed by reading the code: `read` did not check the freeze's key set, and `datetime.fromisoformat` accepts a space separator, which `isoformat()` never writes. | New `qobj.FREEZE_KEYS` lists the six fields `build` writes. `read` refuses a freeze with any other key set, and a `threshold_started` that does not round-trip through `isoformat()`. Tests: a built freeze has exactly `FREEZE_KEYS`. The test refuses: each field missing, an extra field, an empty provenance map, a short commit, an unparsable time, a space-separated time, a non-int commit time, and a commit time after the start. |
| S16SR3-2 | Medium | **Accept; corrects the list in `ADJUDICATION_SCREEN_S16_REREVIEW2_9D5F3E9.md`.** | The complete list of what `read` cannot check, all checked once by `build` at the freeze, is below. |

**The checks left at the freeze, complete** (this replaces the list in the re-review 2 adjudication):

1. **Need the run's store.** Each threshold and dev chain verifies and has the recorded head (`_heads`). Each chain's host provenance has the recorded digest (`host_sha256`). `choices.json` is byte-identical to a fresh `choose` of those chains.
2. **Need the run's pinned checkout (`run_root`).** The engine files of the object (`ENGINE`: generator, binomial, choices rules, lock, Dockerfile) are that checkout's files, and its start gate passes for the fresh `choose`.
3. **Need the repository holding the later files (`root`) and its remote.** Each later file (`LATER`: preregistration, mapping, screen, held-out runner) equals the regular file committed at HEAD (`_committed`, `_reviewed`). The committed freeze-review record lists each reviewed file's SHA-256, with a committed review record. `definition_commit` holds the definition's bytes at its path. Its committer time is earlier than the threshold start and is the one recorded. The commit is on a branch of the remote.
4. **Outside all three.** Proof that the object's hash was posted publicly (QO-2 / HO-4, attempt procedure).

`screen.check_object` adds what a screen reader can check itself: the loaded engine modules equal the definition's engine commit, the object's `mapping.py` and `screen.py` are the ones loaded (`check_screen_code`), and the pinned runtime (`mapping.check_runtime`).
