# Adjudication of BF3 (Fable) and BS3 (Sol) on the D-19 §13 rev 7d at `9762781`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_9762781.md` (`ff9eb3a`): SOUND WITH FIXES
- `SOL_REVIEW_9762781.md` (`564ebea`): SOUND WITH FIXES

**Result:** `PREREGISTRATION.md` §13 rev 7e. Both reviewers found the statistics valid, including the 40k escape. The remaining findings are about the runtime text and the disclosures.

Every finding is accepted.

| Findings | Disposition |
|---|---|
| BF3-1 | **Values recorded before the run.** The expected values of both canaries and the reference vectors are recorded on the server before the threshold run, as part of the run definition and its hash. **At the freeze,** they are carried unchanged into the qualification object, which is how they are "recorded at the D-19 freeze" (A-V1). **Changes.** Any later change to them voids every chunk bound to the run definition. |
| BF3-2, BS3-1 | **The identity is split into two parts.** <ul><li>The **gating identity** is what chunk acceptance and A-V1's "frozen runtime" compare. It is the decided A-V1 identity, plus the image digest and the results of the canaries and the reference vectors.</li><li>**Host provenance** is the CPU model and microcode. It is recorded and disclosed, never compared.</li></ul>The CPU model was never in the decided A-V1 identity; rev 7d had added it. So Sol's option of an owner-decided contract change is not needed: rev 7e returns to the decided identity. Any change in the gating identity stops the run. |
| BS3-2 | The demotion table is relabelled per `U_G` test. It now discloses the QJ range (one to two times the per-test value; 0.023–0.046 at p = 5·10⁻⁵) and the separate DSR-availability route. The re-pilot also measures DSR availability in the thin categories. |
| BF3-3, BS3-3 | **The estimate is now parametric.** It is a base of about 4,200 laptop-core-hours, plus fixed extras of about 300 (itemised), plus about 25 per ordinary escaped cell and 50 per QJ cell. Scenarios at p = 2·10⁻⁵, 5·10⁻⁵ and 10⁻⁴ give about 3½–5 months on 2 vCPU. The re-pilot's measured rates replace the assumptions before the full-run go-ahead. |
