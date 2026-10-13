# Adjudication of the Sol narrow re-check of the D-20/D-13 proposal rev 5 (d082318)

Record: `SOL_RECHECK4_D082318.md` (gpt-6-sol). Adjudicated by Claude Opus
5.5, the drafter. Revision 6 applies every disposition below. Each one
withdraws or narrows a claim. No binding, stream rule, option or
recommendation changes, except that option 2b (a) now includes re-running
the re-pilot.

| ID | Severity | Decision | Reasoning and evidence | Disposition in rev 6 |
|---|---|---|---|---|
| DC5-R1 | blocking | AGREE | "Every attempt whose declaration is fixed in advance" reopened DC4-R1. The *decision* to make a later attempt can depend on an earlier outcome, even if the declaration does not. | §4: (b) meets the transfer assumption for the first attempt on a window, declared before any outcome on it is seen. |
| DC5-R2 | blocking | AGREE | Declarations independent of earlier outcomes do not secure conditional error control, because the decision to retry can itself depend on those outcomes. | §4 retry paragraph: no probability bound across outcome-dependent retries is asserted. The allowance stands as the Constitution's multiplicity rule. The calibration bullet points to that paragraph. |
| DC5-R3 | blocking | AGREE | Identical canary and reference-vector outputs do not establish unchanged re-pilot rates, cost or speed. | §3a (a): the FE-7 re-pilot is re-run on the rebuilt image before the go-ahead, with the CPU probe and the resume test. The old measurements are planning estimates only. Q2b says so. |
| DC5-R4 | note | AGREE | "Only" ignored the conservative change in unavailability among retained cycles. | §4: both effects are named. |

Fable was not asked to re-check rev 5: its rev 4 verdicts carried no blocking
finding, and rev 5 only narrowed claims. Rev 6 again only narrows claims.

Nothing was left unrepaired.
