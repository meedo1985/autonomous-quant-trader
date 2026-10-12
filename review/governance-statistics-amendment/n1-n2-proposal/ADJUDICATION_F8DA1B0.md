# Adjudication of the reviews of the N-1/N-2 proposal rev1 (`f8da1b0`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Reviews:
`FABLE_REVIEW_F8DA1B0.md` (FQ1, SOUND WITH FIXES, `8f046e9`) and
`SOL_REVIEW_F8DA1B0.md` (SQ1, SOUND WITH FIXES, `4e125c9`). All findings are
accepted; none is rejected. They are applied in revision 2 without a further
check [AI default].

| Finding(s) | Disposition in rev 2 |
|---|---|
| FQ1-1, SQ1-2 | §1 states the proven bound `ESS >= n/(L+1)`. G-12 cannot fail in C2, and can fail only for n ≤ 839. The relation to `T_min` and the CPCV consumer are stated, and Q1 is rewritten. |
| SQ1-1, FQ1-8 | §1 adds the caller duties (H set, valid days, exceptions mapped to `UNAVAILABLE`). The rounding-only `γ0 = 0` route is `UNAVAILABLE`, and the `Ω` branch is a numerical guard. |
| FQ1-2, SQ1-4 | §2 gives the full recipe: rows, BTC, purge then shift, the refitted pipeline, per-draw and per-window seeds, alignment, and availability. |
| FQ1-3, SQ1-4 | The i.i.d. permutation is replaced by a circular label shift within each window, which keeps the overlapping-label dependence. No error-rate claim is made. |
| SQ1-3, FQ1-6 | Option (a) is labelled one interpretation. Its `N/A` must be frozen and fixed at preregistration. The avoidance asymmetry is disclosed, and the gate precedents (G-8, G-10) are cited. |
| FQ1-4, SQ1-5 | §3 gives the per-gate input table and the two D-19 routes, (i) full computation or (ii) a route authorised by amendment. A deterministic assertion is not computation. |
| FQ1-5 | §1 corrects the gate outcomes for an all-cash nominee. |
| FQ1-7 | §23, §18 and l.97 are cited, and "decisions equals days" is labelled an interpretation. |
| FQ1-9 | §1 says the definition also feeds the CPCV switch. The CPCV role is left to D-13. |
| FQ1-10, SQ1-6 | §4 questions use parallel options with consequences, including keep-blocked and the lifting of packet R3. |
| FQ1-11 | The pass rule is stated independently as "at least 476" (FN1-4: 25/501), with no dependence on the undecided D-14. The citation is fixed to l.154–155, with the carry-over noted. Ties are handled. |
