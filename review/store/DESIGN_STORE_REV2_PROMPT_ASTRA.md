# Astra re-check prompt: store build design rev 2

You are an independent adversarial design reviewer (read-only), as in your rev 1 review
(`review/store/ASTRA_DESIGN_STORE_REV1_1633831.md`). Repository root is the current
directory, branch `store-design`, at the commit that adds this prompt. Do not modify any
file. Findings are proposals.

Read: `review/store/DESIGN_STORE.md` (rev 2), `review/store/ADJUDICATION_DESIGN_STORE_REV1.md`,
and `git diff 1633831 HEAD -- review/store/DESIGN_STORE.md`. Authority as in rev 1 (Annex D
and the d20-lockbox-proposal files at `3abcafb`; the two modules' `Store` docstrings; 6b §12).

Check:
1. Is each of ST1-A-1..5 repaired as the adjudication says? For ST1-A-2, is the stated limit
   honest and is anything more achievable store-side?
2. Did the repairs introduce a new problem: the lock order D-7 (deadlock, or a writer that
   does not take the look lock), the ledger-identity check, the preflight tool's placement,
   `promotion_evidence` against the reader projection's withholding rules (§D-2.8), the
   §5 slice split?
3. Anything still missing for the design to be built slice by slice.

Output (Markdown, concise): verdict ACCEPT / ACCEPT WITH NOTES / FIX; model ID you can
observe; files and line ranges read; findings ST2-A-1.. with severity, location, evidence,
failure scenario, proposed correction.
