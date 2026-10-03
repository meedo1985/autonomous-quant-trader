# Owner choice: raw lifetime count stays the candidate (D-16/D-17)

**Date:** 2026-10-03
**Authority:** the owner's selection in a Claude Code session, asked by
Claude Opus 5.5 (`claude-opus-5-5`) after the Astra review
`ASTRA_REVIEW_597DDC8.md` (AS-1..AS-3 BLOCKER).

Question as asked: "D-16/D-17: Should the 'count every attempt ever made'
number stay as the candidate that the calibration will test? (Nothing is
activated; promotion stays blocked either way.)"

Answer: **"Yes, keep as candidate"** — "Lifetime count of all attempts
(failures, aborts, reruns included) is the candidate to test. The claim that
it is 'provably correct' is dropped. Calibration decides if it works."

Other options offered: "No, look for another count"; "Decide later".

## Effect

- The raw lifetime family attempt count is the **candidate** input to `A(N)`
  for the calibration design (option C). The universal "mean-correct" and
  "double counting" claims of `PROPOSAL_PACKET.md` (AS-1, AS-2) are
  withdrawn as justification.
- AS-3 (small-N, `K=1`, zero/missing dispersion branches) remains open and
  must be resolved in the calibration design.

## Not changed

D-16 and D-17 are **not closed**; no method is accepted or activated; this is
not a Constitution section 4 amendment. The 2026-09-15 promotion block stands.
No frozen file is edited; no cycle, trial, confirmation or lockbox access,
promotion, deployment or trading is authorized.
