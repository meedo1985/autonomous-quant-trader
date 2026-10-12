<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12999-8615-7bc3-99d6-a9146715a912. Tokens used: 33,049. Made from a packet (Codex's command runner fails here: 'helper_unknown_error: setup refresh had errors'): the re-review prompt, SOL6_ITEM2B_Q5_WIRING_REREVIEW_B6EDC5C.md, ADJUDICATION_ITEM2BWR_B6EDC5C.md, OWNER_DECISION_I2BW1_THRESHOLD_POOLING.md, git diff b6edc5c..44c9859 -- calibration scripts tests, the text at 44c9859 of calibration/reduce.py, scripts/d19_run.py, scripts/d19_run_definition.py, scripts/d19_choose.py and calibration/classifier.py, build_exploration_manifest, canonical_json_bytes, and the accepted preregistration §3.5. Prompt: -->

> # Focused re-review: D-19 item 2b step 1 repairs (I2BW-1, I2BW-2, I2BW-5)
> 
> You are an independent adversarial reviewer (read-only). You are not an authority: findings are adjudicated with evidence. Review ONLY the repairs of the open findings of your previous re-review (attached: SOL6_ITEM2B_Q5_WIRING_REREVIEW_B6EDC5C.md), using the attached adjudication, owner decision, diff and HEAD files. Base yourself on the attachments; say so where you could not verify.
> 
> Questions:
> 1. I2BW-1: the owner bound §3.5 item 2 literally ("Pool over all K"). Do `reduce.pooled` / `reduce.for_k`, the driver's `dev_bounds`, and `d19_choose` implement "per T level, the extreme over all candidate cells" with K and T exact and correlation tails from K >= 2 cells only? Any path still keyed by (K, T)? Is the refusal when a K >= 2 cell lacks a pooled correlation tail correct and reachable only in that case?
> 2. I2BW-2: is the byte-equality check against the manifest rebuilt from `--raw-root` sufficient (forged-claims attack, canonical JSON form, the builder being the same one `scripts/build_manifests.py` uses)? Any way a Q5 record can be written with a manifest not built from the same archives?
> 3. I2BW-5: is the new test an adequate composition check, and is the stated limit (reuse of production `dsr.evaluate` / `gates.u_g`, covered elsewhere) acceptable for pilot use?
> 4. Any defect introduced by the repair.
> 
> Output: verdict for pilot use (ACCEPT or FIX); per prior finding: resolved / unresolved with reason; new findings with IDs I2BWR2-n, severity, file:line, failure scenario, and minimal fix. Put your model metadata at the top.

## Review (verbatim)

**Model metadata:** OpenAI Codex assistant. The exact served model ID and reasoning effort are not exposed in this session.

**Pilot verdict: FIX.** This is an attachments-only, read-only review. I did not rerun the reported tests or inspect files beyond the supplied excerpts.

| Prior finding | Status | Reason |
|---|---|---|
| **I2BW-1** | **Resolved** | `reduce.pooled` takes each tail’s extreme across all K at a given T. `reduce.for_k` restores exact K and T checks and selects only the tails required for that K. The driver supplies bounds by cell ID, and `d19_choose` uses the same T-level pool; neither development path remains keyed by `(K, T)`. With complete threshold chains, only K ≥ 2 cells contribute correlation tails. A missing-correlation refusal is correct if `for_k` is asked for K ≥ 2 from a pool containing only K = 1 cells; that situation cannot arise in the driver’s normal call for an enumerated K ≥ 2 cell. |
| **I2BW-2** | **Unresolved** | For files that stay fixed during `record`, byte comparison against the rebuilt canonical manifest defeats the forged-claims example. The builder and serializer shown are the ones used by `scripts/build_manifests.py`. Two reads and the separate source build still permit a mismatched Q5 definition to be written, as detailed below. |
| **I2BW-5** | **Resolved for the requested composition check** | The new test compares both block-rule results, the family-seeded draw, nominee, and `U_G` across Q5 families, and requires an Annex B result to reach `z_f*`. Reusing `dsr.evaluate` and `gates.u_g` is an acceptable limit for this wiring test given the reported separate numeric tests. It is not a standalone check of every record field or those components’ numerics; I could not independently verify the elsewhere-test bodies or their reported results. |

| New ID | Severity | Location | Failure scenario and minimal fix |
|---|---|---|---|
| **I2BWR2-1** | **High** | `scripts/d19_run_definition.py:132–164` | `record` loads the Q5 source, then separately rebuilds the BTC manifest. If archive bytes change between those operations, the accepted manifest can describe different bytes from the recorded source identity. Separately, it checks one read of the supplied manifest but hashes a later read; replacing that file between reads can record an arbitrary manifest hash. The repair also removed the earlier comparison with `source["manifest_sha256"]["BTCUSDT"]`. **Fix:** compare the rebuilt manifest’s self-hash with that recorded source hash, read the supplied manifest once, compare those captured bytes with the canonical build, and hash the same captured bytes. |
| **I2BWR2-2** | **Low** | `scripts/d19_run.py:18–20` | The driver’s opening description still says development pools “per K,” contradicting the repaired implementation and owner decision. **Fix:** describe pooling per T across all K. |

The provenance gap is the reason for **FIX**; the stale description is not a pilot blocker by itself.
