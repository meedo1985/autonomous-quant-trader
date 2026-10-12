# Sol narrow re-check OS4 of the O-6a specification revs 4–5 at `84fca9c`: READY

Date: 2026-10-04. This is an R19-2 independent narrow re-check, scoped to `git diff 89ecead 84fca9c` (rev 4 and rev 5). An earlier attempt on rev 4 was stopped by the system for low memory and produced no output. This run was started on the owner's instruction ("rerun sol").

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106d0-971b-7630-8095-c09390e15538`. The final message is reproduced below unchanged.

---

**Model:** OpenAI Codex, GPT-5 family; exact deployment identifier unavailable  
**Commit:** `84fca9c3bf01dd80628a7e18d496c8882d6c1206`  
**Verdict:** **READY**

| Finding | Status | Basis |
|---|---|---|
| OF3-1 | Resolved | Earlier different-round captures invalidate; under the disclosed no-removal assumption, the declarer can only abort, not select a round. |
| OF3-2 | Resolved | `D` is fixed at signing, public, above signing height, and bounded before expected evaluation start. Inclusion by `D` is objectively verifiable. |
| OF3-3 | Resolved | `T` is explicitly the 14-digit UTC CDX timestamp; source/original-date metadata is retained. |
| OS3-1 | Resolved | Complete CDX evidence is retained and the `id_` response is bound to the exact row. |
| OS3-2 | Resolved | The text correctly distinguishes chain-state existence from the verifier’s later observation. |

**New findings:** None; no `OS4-*` finding opened.

`git diff --check` passed. Tests/lint/type checks are N/A for this documentation-only review. No network, confirmation/lockbox data, or untracked `data/` content was accessed.

The earlier-capture rule now prevents beacon-round selection; archive removal remains an explicit trust assumption.
The public block-height deadline is sound, although “about 30 days” remains an estimate rather than a calendar guarantee.
Record and commit this review before repository governance treats the R19-2 review as complete.
