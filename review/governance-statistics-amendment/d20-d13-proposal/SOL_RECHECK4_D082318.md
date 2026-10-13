# Sol narrow re-check of the D-20 (rest) and D-13 proposal, revision 5, at d082318

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a13447-e041-7862-8a1b-4e7b1f5ad00e)
- Date: 2026-10-13
- Reviewed: both rev 4 re-check records, `ADJUDICATION_4645E0A.md`, the diff rev 4 -> rev 5 and the full rev 5 (packet)
- Limitation (the reviewer's own): its shell failed; it reviewed the packet only.
- Fable was not asked to re-check rev 5 (its rev 4 verdicts had no blocking finding); this record is Sol's only.
- Findings: DC5-R1, DC5-R2, DC5-R3 (blocking); DC5-R4 (note). Verdicts: Q1, Q2, Q4 READY; Q2b NOT READY for (a) as worded; Q3 NOT READY.
- The reviewer's final output follows verbatim.

---

## Narrow re-check of revision 5

**Revision 5 is not ready to adopt as a whole.** DC4-R3 and DF4-R1 are repaired. DC4-R1, DC4-R2 and DF4-R3 are only partly repaired: §4 states the needed limits, then makes claims those limits do not support. DF4-R2 is also only partly repaired.

### Findings in the revision 4 → 5 diff

- **DC5-R1 — blocking — §4, “(b) meets it for every attempt whose declaration is fixed in advance.”** This reintroduces DC4-R1. A later declaration can be fixed before any result is seen while the *decision to make that attempt* depends on an earlier result from the same window. Its conditional data distribution can therefore differ. Limit the `U_G` transfer claim to the first pre-outcome attempt, as the preceding paragraph does, unless a sequential argument is supplied.

- **DC5-R2 — blocking — §4, false-promotion allowance.** The text correctly states that a probability bound needs error control given the history leading to each cycle. It then says this holds when re-declarations are independent of earlier outcomes. That is insufficient: retrying can itself depend on those outcomes. For example, an earlier result can reveal a data feature, and a fixed second test can be run only when that feature is present. The second test may meet its *marginal* allowance yet fail conditional control. Keep the allowance arithmetic, but do not assert the probability bound without establishing the conditional guarantee. This leaves DC4-R2 and DF4-R3 open.

- **DC5-R3 — blocking for option 2b(a) as worded — §3a, re-pilot carry-over.** Byte-identical canaries and reference vectors check those outputs; they do not establish unchanged re-pilot rates, elapsed cost, or speed across its runs. Repeating a CPU probe and resume test does not, by itself, validate the old go-ahead estimate. Re-measure the relevant re-pilot quantities on the rebuilt image, or state what evidence and acceptance rule permits their use as planning estimates. DF4-R2 is only partly repaired.

- **DC5-R4 — note — §4, “Retries change only the uncertified pass frequencies.”** The preceding bullets also say retries can change unavailability among retained cycles, though retrying solely to escape unavailability changes it in a conservative direction. Remove “only” or name that effect.

DC4-R3’s finite-versus-overall sum wording is correct. DF4-R1’s build-order consequence is stated. I found no other issue in the supplied diff.

| Owner question | Verdict |
|---|---|
| 1. Code bindings and R-7 | **READY** |
| 2. Null streams and `s_inputs` | **READY** |
| 2b. Model libraries | **NOT READY** for option (a) as worded — DC5-R3 |
| 3. C2 seed source | **NOT READY** — DC5-R1 and DC5-R2 |
| 4. D-13 reporting | **READY** |

**Limits:** I reviewed the supplied full text and diff. The local shell failed during process setup, no computer surface was available, and the connected GitHub repository did not expose commit `d082318`. I therefore could not verify HEAD, the exact committed bytes or complete commit diff, local skill versions, image outputs, re-pilot evidence, or tests. I made no edits or commit. Under the repository’s rule, this feedback is not a completed project review record until it is committed through the authorized workflow; it does not make or activate an owner or statistician decision.
