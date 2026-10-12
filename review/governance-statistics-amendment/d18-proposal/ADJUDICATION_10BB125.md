# Adjudication of the two D-18 re-reviews of `10bb125` (revision 4)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`), author of the
proposal, so not independent; decides nothing. Records:
`FABLE_REVIEW_10BB125.md` (FR4-1..FR4-15, SOUND WITH FIXES, no blocker),
`SOL_REVIEW_10BB125.md` (SR4-1..SR4-7, UNSOUND as written, SR4-1..SR4-6 BLOCKER).

## Agreement

Both accept the event `E_f` for top Sharpe, no fallback; the inclusion
`F ⊆ E_trend ∪ E_vol`; and that the bound is a statement over named
simulated classes, not a verified real-market guarantee (FR3-10, FR4-11,
SR4-7). Both find the "unseen data" test too narrow, the no-result target
mis-scoped, and the post-pick procedure undefined.

| Topic | Fable | Sol | Adjudication |
|---|---|---|---|
| "Unseen" must mean unavailable to selection, not just "no per-trial metric returned"; record eligibility at declaration | FR4-1, FR4-2, FR4-12 | SR4-3 | Accept. Fix: eligible confirmation data is data that did not yet exist at declaration (future data), assigned at ingest to a partition off the sandbox, with a purge/embargo gap at the boundary. |
| No-result target: gate unavailability omitted; exogenous cancellations not calibratable; denominator | FR4-8 | SR4-1, SR4-2 | Accept. Fix: no-result includes any mandatory gate `UNAVAILABLE`/technical-invalid; denominator = eligible authorised cycle attempts; calibration certifies method-generated no-results; operational cancellations monitored separately. |
| Post-pick window, nominee order, cycle outcome undefined; ineligible / no-result cycle outcome; budget trigger fires at start of 162nd trial | FR4-4, FR4-5 | SR4-6 | Accept as **amendment text** (owner-authored §4). Severity disagreement: Sol BLOCKER, Fable NON-BLOCKING. I side with Sol that calibration cannot run until this is bound, and with Fable that it does not change the D-18 event. |
| Broadened method does not exist | FR4-9, O18-2 status | SR4-4 | Agree on substance; severity disagreement. It blocks calibration (D-19), not the D-18 definition. It is the next design task already recorded (O18-2). |
| `A_f` not total (hash mismatch, run exactly once) | FR4-7 | — | Accept; fix in text. |

## One reviewer only

- **SR4-5 (BLOCKER) held-out firewall.** Accept: freeze the whole
  qualification object (method, generator, classifier, confidence family,
  acceptance rule) before held-out generation; any held-out access burns that
  namespace. D-19 text.
- **FR4-3 scale of waiting** (~27.6 months for a 168-hour strategy's fallback
  ESS), **FR4-13** (under P18-0 the lifetime count adds no safety, only cost),
  **FR4-10/FR4-11** (my option texts overstated): owner-facing; to be shown.
- **FR4-6 reruns, FR4-14 family opt-out:** owner questions.
- FR4-15 availability in power cells: D-19.

## Assessment of the process

Four rounds have converged on the D-18 event itself; both reviewers now
accept it. The remaining blockers are the method (O18-2), the amendment's
cycle mechanics, and the D-19 calibration contract, which cannot be settled
inside D-18. Further D-18-only review rounds are unlikely to change the
event.

No frozen file edited; promotion stays blocked.
