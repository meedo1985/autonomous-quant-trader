# Sol fidelity review of S4 draft rev 9 and Annex C rev 4 at ffaf8dd (D-20 rest, D-13 fold-in)

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a13492-9cd0-7081-bdde-07a5cb743fe7)
- Date: 2026-10-13
- Reviewed: the owner decision record, the decided proposal rev 6 and the S4 diff main..ffaf8dd (packet)
- Limitation (the reviewer's own): its shell failed; it reviewed the packet only.
- Findings: SF-R1..SF-R4 (blocking), SF-R5, SF-R6 (notes). Verdict: NOT FAITHFUL.
- The reviewer's final output follows verbatim.

---

## Verdict: NOT FAITHFUL

The supplied diff closes the shown D-13 and non-lockbox D-20 markers, but it drops several conditions the owner adopted. These are drafting defects under Annex C’s fidelity rule, not new decisions.

| ID | Severity | Evidence and minimal repair |
|---|---|---|
| **SF-R1** | **Blocking** | [DRAFT_WORDING.md:147](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:147>) binds the G-1 code, but omits the owner’s express condition for reusing the Task 12 stream: the Task 12 tests **and** D-19 reference vectors must pass at the bound commit on the pinned runtime. Add that condition to R-8 or C-1. |
| **SF-R2** | **Blocking** | [ANNEX_C_GATE_DEFINITIONS.md:299](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:299>) defines the G-11 stream, while C-13 only discloses a screen-seed weakness. The adopted B6 rule is absent: the exact `screen_seed` and per-path trial-seed formulas, C-0 window ID, and binding of the screen’s bootstrap and sign streams to reviewed `screen.py` code and vectors. Add those rules where the screen streams are defined. The G-11 gate-list status currently overstates closure. |
| **SF-R3** | **Blocking** | [ANNEX_C_GATE_DEFINITIONS.md:405](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:405>) says the model libraries enter the image before the run definition, but drops option (a)’s prerequisites: one §16-reviewed, hash-pinned image PR; byte-identical canaries and full reference vectors on both images; a new FE-7 re-pilot with CPU probe and resume test before go-ahead; and FE-4 “image done” reopening until merge. State these as prerequisites, rather than leaving the installation as an unqualified future event. |
| **SF-R4** | **Blocking** | [ANNEX_C_GATE_DEFINITIONS.md:449](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:449>) limits the `U_G` claim to the first attempt, but omits the accepted modelling assumption that its SHA-256 seed behaves as a fresh unpredictable draw independent of the data, and that no invariance bound proves the transfer. Add the assumption and its scope beside the `U_G` statement. |
| **SF-R5** | **Note** | [ANNEX_C_GATE_DEFINITIONS.md:408](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:408>) weakens B4’s vector specification. Rev 6 fixes examples at `d ∈ {0,499}`, `w ∈ {0,1}` and a full-grid hash for fixed `n_w`; the annex names only generic vectors and a grid hash. Restore the fixed coordinates and inputs. |
| **SF-R6** | **Note** | [ANNEX_C_GATE_DEFINITIONS.md:415](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:415>) defines the 28 CPCV pairs but drops rev 6’s *lexicographic order*. Add it to the split rule. |

**Markers and consistency.** In the supplied diff, the non-lockbox `<<OPEN D-20>>` markers and `<<OPEN D-13>>` are removed. The remaining D-20 marker is the expressly reserved lockbox row. `<<D19 values>>`, D-11, D-12 and signing placeholders remain intentionally open. The R-rows and gate statuses otherwise point to the intended annex sections; SF-R2 is the material gap behind a status that says D-20 is settled.

**Annex B.** Leaving its hash-cited §2.4 text untouched is sound **for this draft**: R-12 expressly supersedes that one stream-extension sentence and points to the bound `dsr.py` construction and D-19 vectors. The draft remains inactive, so this does not itself amend Annex B.

**Limits.** The local command runner failed before starting `git` or file reads. I could review the supplied owner record, rev 6 text and diff, but could not independently verify the `ffaf8dd` tree, unchanged surrounding text, full-tree marker counts, hashes, or repository skill files. No edits or committed review record were made; the repository’s committed-review requirement remains outstanding.
