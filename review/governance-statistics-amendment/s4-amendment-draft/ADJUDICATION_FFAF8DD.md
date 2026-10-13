# Adjudication of the Sol fidelity review of the S4 D-20/D-13 fold-in (ffaf8dd)

Record: `SOL_FIDELITY_REVIEW_FFAF8DD.md` (gpt-6-sol, NOT FAITHFUL). Adjudicated
by Claude Opus 5.5, the drafter. Under Annex C's fidelity rule, each finding
is a drafting defect, corrected here. None is a new decision.

| ID | Severity | Decision | Disposition (Annex C rev 4, corrected) |
|---|---|---|---|
| SF-R1 | blocking | AGREE: the Task 12 reuse condition was dropped. | C-1: reuse of the Task 12 stream (row D-20 option (b)), on the condition that the Task 12 tests and the D-19 reference vectors pass at the bound commit on the pinned runtime. |
| SF-R2 | blocking | AGREE: the B6 screen-seed rules were dropped. | C-10 (3), new bullet "Inside the D-19 screen": the per-path trial-seed and `screen_seed` formulas, the C-0 window id, and the path streams bound by the reviewed `screen.py` and its vectors, as a clarification of prereg §7.2. |
| SF-R3 | blocking | AGREE: option (a)'s prerequisites were dropped. | C-12 (5): the §16-reviewed, hash-pinned image PR (NumPy 2.5.3 resolution, system libraries, binding through the image digest), byte-identical canary and reference-vector outputs, the FE-7 re-pilot re-run with the CPU probe and the resume test, and FE-4 reopened until merge. |
| SF-R4 | blocking | AGREE: the accepted modelling assumption was dropped. | C-13 "Seeds": the SHA-256 random-draw assumption, that no invariance bound proves the transfer, and that it is the calibration's own assumption. |
| SF-R5 | note | AGREE | C-12 (5): vectors at `d ∈ {0, 499}`, `w ∈ {0, 1}`, plus the full-grid hash for fixed `n_w`. |
| SF-R6 | note | AGREE | C-14 (2): the splits are in lexicographic order. |

Nothing was left unrepaired.
