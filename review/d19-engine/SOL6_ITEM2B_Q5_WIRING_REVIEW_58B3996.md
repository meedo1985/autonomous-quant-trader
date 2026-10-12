<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a1277b-9dbc-7a81-81a1-454d820d003c. Tokens used: 44,447. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM2B_Q5_WIRING_REVIEW_PROMPT.md, git diff 367c434..58b3996 -- calibration scripts tests, the HEAD text of scripts/d19_run.py, scripts/d19_run_definition.py, calibration/rules.py, calibration/semi.py, calibration/generator.py lines 1-100, the accepted preregistration §1-§3.5 and §8, and the rule-library proposal revision 3 at 52316cf. -->

# Independent review: D-19 engine item 2b, step 1 — Q5 cells wired into the run

**Reviewer model metadata:** Codex, GPT-6 family. The exact served model ID and reasoning effort are not exposed in this session.  
**Commit reviewed:** `58b3996` on `d19-calibration-engine`, parent `367c434`.  
**Basis:** Supplied attachments only. I did not inspect the repository or run commands. The drafter’s reported checks are unverified by this review.  
**Scope:** Q5 `semi-trend` and `semi-vol` in threshold and development. QJ and `d19_choose` are outside this change.  
**Commands run:** None; the command runner was unavailable.  
**Verdict for pilot use:** **FIX**. The threshold binding disagrees with accepted preregistration §3.5.

## Findings

### I2BW-1 — High — Thresholds are pooled by K instead of T

**Location:** `scripts/d19_run.py:174–193, 270–287`

**Failure scenario:** A manifest contains cells at two T levels with the same K, or cells with different K at the same T. `dev_bounds` uses the existing `reduce.pooled` per K, and jobs select `bounds.get(c.k)`. Section 3.5 requires the extreme over **all candidate cells per T level**. Development therefore uses thresholds different from the accepted method, including when agnostic and Q5 cells are pooled.

**Proposed repair:** Pool and select bounds by `cell.t`, across every agnostic and Q5 candidate cell at that T. Add a test with both multiple T values at one K and multiple K values at one T. Retaining per-K thresholds would change the accepted preregistration and requires an owner proposal, not an implementation choice.

### I2BW-2 — Medium — The separately supplied exploration manifest is not linked to the Q5 source

**Location:** `scripts/d19_run_definition.py:125–146`; `scripts/d19_run.py:220–227`

**Failure scenario:** Recording succeeds with an arbitrary `--exploration-manifest` file—the new end-to-end test uses `{}`—and archives from `--raw-root`. The top-level `exploration_manifest_sha256` can consequently describe a file unrelated to the returns used for Q5. Workers check the separately recorded `exploration_source` identity, but never reconcile the two records.

**Proposed repair:** At record time, establish and validate the intended relationship between the supplied exploration manifest and the two source manifest hashes; reject a mismatch. Cover a mismatched file in a test. If changing the meaning of the existing manifest field is necessary, take that change to the owner.

**Boundary assessment:** Given the attached worker path and absent a SHA-256 collision or in-process mutation, a new Q5 chunk cannot use returns different from the recorded `exploration_source` identity. It *can* use returns unrelated to the separately hashed `--exploration-manifest` file.

### I2BW-3 — Medium — Source validity and reference variance are deferred to every draw

**Location:** `calibration/semi.py:89–98`; `calibration/rules.py:59–65, 191–202`; `scripts/d19_run_definition.py:125–146`

**Failure scenario:** Demeaning otherwise valid positive-price returns can produce a BTC return at or below −100%. `record` accepts and writes that source identity; the first replication then raises in `reference_variance`. Revision 3 says to refuse such a source before any replication and to compute and freeze `v̄` once per source. The current code recomputes it from the whole source on every draw. With unchanged source bytes, that calculation is deterministic and gives the specified value; the timing and freezing requirement is unmet.

**Proposed repair:** Validate the source and calculate `v̄` during source preparation, then use that fixed value for every Q5 draw. Test record-time refusal of an invalid demeaned source.

### I2BW-4 — Low — Synthetic job tuples changed shape

**Location:** `scripts/d19_run.py:279–289`

**Failure scenario:** A Q1–Q4 threshold job previously had five arguments and a development job six; both now have seven. The worker defaults preserve the apparent execution behavior, but the requested claim that job tuples remain unchanged is false. A tuple-shape assertion or integration consuming those tuples would fail.

**Proposed repair:** Keep the prior tuple forms for synthetic cells and supply the additional arguments only to Q5 jobs, or explicitly accept and document the internal tuple change.

### I2BW-5 — Medium — The Q5 development integration test checks completion, not its result

**Location:** `tests/unit/test_calibration_rundef.py:1168` (new Q5 test block)

**Failure scenario:** The end-to-end test compares threshold diagnostics against a Q5 draw, but checks only the number of development results. The separate `family_seed` spy raises before Annex B. A development regression that emits incorrect Q5 diagnostics or downstream results could leave both tests passing.

**Proposed repair:** Compare at least one stored development diagnostic against an independently constructed `rules.draw` using the development outer seed, and verify a substantive development result. Keep the family-label spy for its narrower assertion.

## Other checks

- **Seeds:** The attached paths use `"market"` and `"sign"` for Q5, `"market"` and `"columns"` for synthetic cells, and the Q5 family label or `"agnostic"` for the inner family seed. No seed-routing defect is evident.
- **Source identity:** The run definition records both source manifest hashes, the SHA-256 of contiguous little-endian binary64 return bytes, row count, and left-out count. Each Q5 worker rebuilds and compares that identity before creating its chain. Missing `--raw-root` is refused at record and run time.
- **Q1–Q4:** Their draw call retains the same generator and stream construction in the attached diff. Reference-vector results were reported by the drafter, not independently reproduced here. The job-tuple exception is I2BW-4.
- **Warm-up:** `WARMUP = 250` is passed to `semi_empirical`, and `v̄` comes from the whole demeaned BTC source. The calculation is deterministic for a fixed source; see I2BW-3 for its repeated calculation.
- **Scope boundaries:** `cells_from_manifest` still refuses `semi-joint`. No `d19_choose` change appears in the supplied diff; its asserted refusal cannot be independently checked from the attached HEAD excerpts.
- **Tests:** The reported 177 calibration passes, broader suite, lint, types, import checks, and frozen verification are drafter reports. The Q5 tests exercise missing archives, differing returns, threshold outputs, direct draw streams, and family-label selection. They do not resolve I2BW-1, I2BW-2, I2BW-3, or I2BW-5.

This review makes no code or preregistration change. All five findings remain open.
