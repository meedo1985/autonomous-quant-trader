# Sol narrow re-check DS6 of the D-19 preregistration rev 6 at `e1e4e7e`: READY

Date: 2026-10-04. This is an R19-2 independent narrow re-check by the different model family, scoped to `git diff 327aa3d e1e4e7e`. Fable stated in DF5 that these fixes need no further round.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10710-9f07-7d13-b0b7-73b9d9dc9710`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex, GPT-5 family; exact served identifier unavailable  
Commit: `e1e4e7e8c01954912d0dad7f30a8a90308d96d6f`  
Verdict: **READY**

| Finding | Status |
|---|---|
| DS5-1 / DF5-3 | RESOLVED — `D_Q2` is bound only before attempt 2’s post. |
| DS5-2 / DF5-5 | RESOLVED — Q2m assignments are deterministic; `K=2` confounding is disclosed. |
| DS5-3 | RESOLVED — 379 cells and `M_max ≈ 1,167`; stated thresholds remain unchanged. |
| DF5-1 | RESOLVED — voids consume keys; exhaustion requires new acceptance. |
| DF5-2 | RESOLVED — committed pre-run check and start record define the boundary. |
| DF5-4 | RESOLVED — opposites use the stated covariance without further negation. |

New findings: **None.**

All eight last-round findings are fixed on paper.  
You may accept rev 6 and decide Q-1.  
Authorize only the measured pilot; no full run, certification, or promotion is authorized.
