# Astra calibration-preregistration proposal

**Model:** `gpt-6-astra`
**Mode:** read-only proposal
**Date:** 2026-09-15
**Verdict:** **SUPERSEDED AS AN EXECUTION PLAN — RECONCILIATION REQUIRED**

Astra proposed the concrete values recorded in
`CALIBRATION_PREREGISTRATION_DRAFT.md`. The design uses a per-family any-null-
clearance event, a 148-cell primary scenario manifest, 50,000 held-out family
replications per cell, one-sided exact binomial upper bounds with 99%
simultaneous Bonferroni coverage, and separate development, validation, and
power namespaces.

The proposal deliberately adds no error-rate slack, permits failed qualification,
and treats weak power as a reportable outcome. It distinguishes finite-grid
evidence from a universal guarantee and keeps adaptive searches, repeated looks,
and incomplete histories outside the initial qualifying domain.

No simulation was run, no DSR equation was selected, no restricted data was
accessed, and no governance artifact was activated. B1-B5 remain open.

After the 2026-09-17 GitHub work supplied a concrete narrow method candidate,
subsequent independent reconciliation found that the numerical proposal's
primary grid conflicts with that candidate's supported domain and event. The
proposal is retained as historical design evidence only. It is not a completed
preregistration and must not be executed.
