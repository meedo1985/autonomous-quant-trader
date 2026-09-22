# Task gate review — `LOSS_BOUND_DEFAULTS.md`

**Reviewer:** Claude, observed model ID `claude-opus-5` (Claude Code, Opus 5)
**Date:** 2026-09-22
**Skill:** `.agents/skills/task-gate-review/SKILL.md`, read directly (Skill-tool
discovery had not refreshed; AGENTS.md permits opening the file)
**Subject:** branch `docs/loss-bound-defaults`, base `8ba1a4b`

## 1. Scope

Two added files and one modified, no deletions:

- `review/pre-deployment/LOSS_BOUND_DEFAULTS.md` (new)
- `review/pre-deployment/LOSS_BOUND_DEFAULTS_GATE.md` (this record, new)
- `review/pre-deployment/LOSS_BOUNDS_AND_OPEN_DECISIONS.md` (modified: the
  `F-2` citation repair only, one paragraph rewrapped, nothing else)
- `review/pre-deployment/OWNER_ACKNOWLEDGMENT_S25.md` (new: the §25
  acknowledgment written out for signature, unsigned)

The §25 document was added after the first gate pass, so the validation in §2
and the frozen verification in §3 were **re-run** over the expanded change:
porcelain status over frozen paths still zero lines, Constitution canonical
self-hash still `4cb6c7d3…4fb8d7`, 1153 passed / 4 skipped, ruff clean, mypy
clean on 30 files. Its nine clauses were checked one by one against §25 lines
187–188 and map in order to `C-1`–`C-9`; §2 line 34, §12 lines 118–119 and §14
lines 128–135 were each read and verified as cited.

`git status --porcelain docs protocols schemas specs FROZEN_HASHES.json` returned
zero lines. No code, test, config, schema or spec file changed. No out-of-scope
edits found.

## 2. Validation

| Check | Command | Result |
| --- | --- | --- |
| Tests | `.venv/Scripts/python.exe -m pytest -q` | **1153 passed, 4 skipped**, 62.48s, exit 0 |
| Canaries | `... -m pytest tests/canaries -q` | **22 passed**, exit 0 |
| Lint | `.venv/Scripts/python.exe -m ruff check .` | **All checks passed!**, exit 0 |
| Types | `.venv/Scripts/python.exe -m mypy src` | **no issues in 30 source files**, exit 0 |
| Import boundaries | — | Covered by the suite; no import graph changed, as no `.py` file was touched |

The suite was run although the change is documentation-only, to establish that
the tree is green independently of this change rather than to claim the change
was exercised. **It was not: no test covers this document.**

## 3. Frozen artifact verification

Baseline is commit `8ba1a4b`, a clean merged state. Bytes under `docs/`,
`protocols/`, `schemas/`, `specs/` and `FROZEN_HASHES.json` are unchanged
against it, verified by porcelain status rather than by sidecar agreement alone.

Independently recomputed, not merely compared to freshly written sidecars:

- **14 single-file `.sha256` sidecars** — all match.
- **`external-review-packet/MANIFEST.sha256`** — 7 entries, all match.
- **`v1.1-method-candidate/MANIFEST.sha256`** — 4 entries, all match.
- **`review/task6/ACCEPTED_ORACLE_HASHES.sha256`** — 6 entries, all match
  (paths are repo-root-relative, not manifest-directory-relative).
- **`FROZEN_HASHES.json`** — 7 of 8 hash entries matched to on-disk frozen files
  by content: `protocol_v1.yaml`, `COST_MODEL_v1.md`, `FEATURE_FACTORY_v1.md`,
  `CANONICAL_BENCHMARKS_v1.md`, `BACKTESTER_SPEC_v1.md`, `THREAT_MODEL_v1.md`,
  `HASH_CANONICALIZATION_v1.md`.
- **`constitution_content_hash`** — the eighth entry, correctly not equal to the
  raw file hash. Recomputed per `HASH_CANONICALIZATION_v1.md` rules 1, 5 and 6
  (LF endings, self-hash value replaced with the empty string):
  `4cb6c7d3…4fb8d7`, matching both the embedded value at
  `RESEARCH_CONSTITUTION.md:8` and `FROZEN_HASHES.json`.

No hash was repaired or regenerated. Nothing frozen was touched.

## 4. Acceptance

The task was: choose defaults for `L-01`–`L-04`, which the owner delegated to the
AI after stating he has no background in the subject.

| Criterion | Evidence |
| --- | --- |
| Each row answered or explicitly declined with reason | §§2–5 of the document |
| Every line citation verified against the source | See §5 `F-2` — two were wrong and were corrected |
| Nothing frozen amended, no `D-nn` closed | §3 above; document §0 and §7 |
| AI authorship and non-adoption stated | Document status line and §6 |

## 5. Findings

**`F-1` — `NON-BLOCKING`, repaired.** The `L-02` figure of 240 effective
decisions has no frozen citation; only the floor of 120
(`protocol_v1.yaml:290`) does. Repaired by stating in the document that the
doubling is a judgment rather than a citation, and giving the argument for it.

**`F-2` — `NON-BLOCKING`, repaired.** Two line citations inherited from
`LOSS_BOUNDS_AND_OPEN_DECISIONS.md` were wrong. `btc_drawdown_constraint` spans
`276–278`, not `276–277`, and the clause reads *confirmation* OOS max drawdown,
which the draft had dropped. The cooling-off floors are at `303–304`; `305` is
`safety_amendment_activation_delay_hours`, which is not cited. Both corrected.
The `276-277` error also existed in the already-merged predecessor document and
**is repaired there by this change**, in the same branch. The cooling-off cite in
that document (`protocol_v1.yaml:303`, capital-increase only) was checked and is
correct, so it was left alone.

**`F-3` — `NON-BLOCKING`, repaired.** `protocol_v1.yaml:244` defines a fallback
effective-decisions method, `raw_decisions / ceil(horizon_hours/24)`, which is a
cruder discount than the Newey-West ESS at `242–243`. 240 under the fallback is
not the same quantity as 240 under the primary. A caveat was added requiring the
method actually used to be named when the row is applied.

**`F-4` — `NON-BLOCKING`, not repaired, stated instead.** The 20% figure in
`L-03` is a judgment with no citation and no calibration. It is likely to trigger
in an ordinary crypto bear market even if the strategy works as designed, because
exposure confined to `[0,1]` limits decoupling from the asset. Left unrepaired
because the alternative — a wider or absent stop — assumes the edge is real,
which is precisely what is not established. The cost is stated plainly in the
document rather than smoothed over.

**`F-5` — `NON-BLOCKING`, structural, not repairable here.** This project
designates Claude as its independent adversarial reviewer
(`.agents/skills/claude-adversarial-review/SKILL.md`). Claude authored the
document under review. **This gate is therefore not independent**, and no
adversarial packet prepared by the same model on its own output should be
recorded as an independent check. Stated rather than repaired; see §6.

**`F-6` — `QUESTION`, open, non-blocking for this task.** `L-01` is defaulted to
zero and left to the owner. The owner has stated he has no background in the
subject and asked the AI to choose. Zero is safe and blocks nothing today, but
the row is unanswered in substance and will have to be answered before any
deployment. It is not a question the AI can close.

**Sibling skills.** `quant-code-review` and `scientific-reproducibility-review`
are recorded **N/A** with reason: both scope to code, data, backtests,
benchmarks, models, determinism, provenance and reproducible artifacts. This
change contains none — no code, no computation, no data, no artifact, no seed,
no schema. The one part of `quant-code-review`'s remit that does bear on this
document, correctness of the promotion-gate citations, was discharged directly
and produced `F-2` and `F-3`.

## 6. Verdict

**`LOCAL GATE: PASS`** — for a documentation-only change that amends nothing.

Claude adversarial review status: **`NOT SENT`**, and per `F-5` it would not be
independent if sent to the same model. The independent review that would have
value here is by a different model family. Codex is installed but the owner
reported it **unavailable** on 2026-09-22, so no different-model review has been
run and this record does not claim one.

Outstanding before anything in this document takes effect:

1. **Owner adoption** of `L-02`, `L-03`, `L-04` in §6 of the document, and an
   owner-supplied figure for `L-01`. Not supplied. An AI cannot supply it.
2. The §25 acknowledgment remains **unsigned**, and is not satisfied by this.
3. `D-15`–`D-19` remain open; the statistical verdict remains `KEEP_BLOCKED`.

This gate authorizes no merge, no promotion, no deployment, and no next task.
Skills are instructions, not enforced CI: nothing here is mechanically enforced.
