# Adjudication of the two D-18 re-reviews of `8ff7316` (revision 3)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`), author of the
proposal, so not independent; decides nothing. Records:
`FABLE_REVIEW_8FF7316.md` (FR3-1..FR3-10, UNSOUND as written),
`SOL_REVIEW_8FF7316.md` (SR3-1..SR3-6, UNSOUND as written).

## Agreement

Both resolve FR2-1 (within a cycle), FR2-5, FR2-6, FR2-8, FR2-11, FR2-12,
FR2-13, SR2-2, SR2-5, SR2-6, SR2-7. Both accept the inclusion `F ⊆ E` and
top-Sharpe-no-fallback as defensible.

| Topic | Fable | Sol | Adjudication |
|---|---|---|---|
| `z_crit` chosen on the same replications that certify it | FR3-3 | SR3-4 | Accept; one global decimal `z_crit` fixed from development replications (or analytically) before held-out qualification; no re-tuning. D-19 detail. |
| Availability test must be on finite `z`, `D > 0`, not on Φ | FR3-5 | SR3-6 | Accept; fix in text. |
| Post-pick processing and amendment of `cycle_termination` | FR3-6 | SR3-1 (part) | Accept; amendment text. |

## Found by one reviewer, accepted

- **FR3-1 (BLOCKER) later cycles reuse seen confirmation data.** Re-declaring
  cycle 1's luckiest trials in cycle 2 gives a null pass of 34%–87% in
  Fable's model; the lifetime count does not prevent it. Owner question.
- **FR3-2 (BLOCKER, decision framing) 1% availability is infeasible on the
  O18-4 grid**, because the current method refuses duplicates, dependence,
  heavy tails and lifetime mismatch (DEC-02 lines 88–91, 113–115). My
  description to the owner ("the limit already proposed in earlier records")
  omitted that DEC-02 proposed it only for 16 Gaussian equal-count cells.
  Owner question.
- **SR3-1 (BLOCKER) pick trigger mismatch.** The owner was shown "when both
  budgets are used up or day 180"; revision 3 wrote "every declared trial has
  finished". My error in transcription. Owner question.
- **SR3-2 (BLOCKER) no-pick cycles as non-events** reopen the vacuous pass.
  Accept: a cycle that ends before the pick counts as no-result against the
  availability ceiling.
- **SR3-3 (BLOCKER) declared-set admissibility.** Accept: `1 <= |J_f| <= 81`,
  unique ids, hashes, validation before the cycle starts.
- **SR3-5 (BLOCKER) 1% per family or per cycle.** Owner question.
- FR3-4 (worst cell is N=2 high ρ; a 2.5% cap needs z_crit ≥ ~1.972 before
  margins; my round-3 option text "~4.25%" understated), FR3-7 (reruns),
  FR3-8, FR3-9 (referents), FR3-10 (bound is over qualifying cells).

## Not repaired here

All findings stay open until revision 4 and the owner's decisions. No frozen
file edited; promotion stays blocked.
