# Adjudication of BF2 (Fable) and BS2 (Sol) on the D-19 §13 rev 7c at `09b0fb9`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records** (both committed in `aa6caa7`):
- `FABLE_REVIEW_09B0FB9.md`: SOUND WITH FIXES
- `SOL_REVIEW_09B0FB9.md`: UNSOUND, blocker BS2-1

**Result:** `PREREGISTRATION.md` §13 rev 7d. The drafter recomputed τ_G(40k) = 0.000451 (critical count 32, at `M` = 322 and 340), the 12k UCBs at 0–2 events, and the demotion probabilities with the escape.

Every finding is accepted.

| Findings | Disposition |
|---|---|
| BS2-1 (BLOCKER) | Two hashes, in order. A **run-definition hash**, committed before the threshold run, binds the threshold and development chunks. The **qualification-object hash** binds the held-out chunks, and the object includes the final chain heads and the reduced results of threshold and development. Every chunk records its own content hash, and every chain's final head is recorded. |
| BF2-1 | Fable option (a): a held-out escape at 40k. A development `U_G` UCB at most τ_G(40k) allows 1–2 development events, and that cell then runs 40k held-out. This brings the chance demotion probability at p = 5·10⁻⁵ from 0.45 down to 0.023. The risk table is disclosed. The re-pilot measures `U_G` in the thin categories. Demoted cells are reported from development plus the §9 runs only. |
| BS2-2 | §1, §3.2 and §3.3 are now explicitly overridden: a challenge cell is a cap-demoted or availability-demoted cell. The "Unchanged" list is corrected. |
| BF2-3, BS2-3 | Fable option (a): the object certifies **C2 only**. Under decided A-B7's floor reading, C2's `T` cannot exceed `T_C2` (a `g` mismatch makes the declaration invalid), and a shorter window is already ineligible. So A-B7 is not changed, and `<<OWNER A-B7-EQ>>` is withdrawn. §12 is overridden: acceptance needs a separately recorded affirmative owner answer to `<<OWNER O18-4-T>>`. |
| BF2-2, BS2-4 | **Runtime.** A container image pinned by digest, holding the whole userland including libc and libm, with no updates inside it during the run. **Identity and checks.** The identity records the host CPU model and dispatch features. A `pow`/`exp`/`log` canary is added. On every start and resume, both canaries and the full frozen reference-vector suite run. **Canary.** Both canaries are re-recorded on the server at the freeze; the laptop's `V_CANARY` is not reused. This is an engine change for the build. **Wording.** "Rebuilt on another machine" becomes "rebuilt on a machine with the same CPU dispatch features". **Disclosed to the owner:** C2's evaluation must run on such a machine. **Host changes.** A change of CPU model with the same features is recorded and disclosed. A change of features stops the run. |
| BF2-4 | One chain per (namespace, cell). A corrupt chunk is deleted unread and recomputed. "Access" is defined, and the actions that are not access are listed. The chunk time is corrected to about 45 minutes, or about 90 in QJ. |
| BF2-5 | The workers run under `nice 19` with a systemd `MemoryMax` of 2.5 GB. The re-pilot is measured with forward paper running. |
| BF2-6 | §3.5, §3.6 and §10 are listed as overridden, with the new values. The ranks are bound in integer arithmetic (`n − q`, `q + 1`, `q = floor(n/100000)`). |
| BF2-7 | Power cells at Sharpe 0.5, 1.0 and 2.0 are restored, at 2k. The mixed-null resolution (standard error about 0.0035, so a detectable excess of about 0.007) is disclosed. |
| BS2-5 | Reworded: "marginal expected exceedance at most 4/300,001, with equality for continuous diagnostics". |
