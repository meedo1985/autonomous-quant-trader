# Sol narrow re-check of the D-20 (rest) and D-13 proposal, revision 4, at 4645e0a

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a13442-5cbe-75d0-b69e-a15e26ab847c)
- Date: 2026-10-13
- Reviewed: both rev 3 re-check records, `ADJUDICATION_DBA31FB.md`, the diff rev 3 -> rev 4 and the full rev 4 (packet)
- Limitation (the reviewer's own): its shell failed; it reviewed the packet only.
- Findings: DC4-R1, DC4-R2 (blocking); DC4-R3 (note). Verdicts: Q1, Q2, Q2b, Q4 READY; Q3 NOT READY.
- The reviewer's final output follows verbatim.

---

**Revision 4 is not ready to adopt as a whole.** The code-binding and CPCV repairs are sound in the supplied text. The calibration section still makes two claims that do not follow from the stated assumptions.

### Rev 3 findings and adjudication

| Rev 3 IDs | Re-check |
|---|---|
| DC3-R1 / DF3-R1 | **Repaired.** Engine files and object files now have disjoint byte checks, and the held-out entry point is named. |
| DC3-R2 / DF3-R2 / DF3-R3 | **Repaired at proposal level.** The image digest supplies the library binding; the image PR must pin dependencies and demonstrate unchanged numerical outputs before the run definition. That demonstration remains to be done. |
| DC3-R3 | **Partly repaired.** Revision 4 distinguishes a fresh attempt from a retained cycle, and the adjudication correctly restores the role of the `m` allowance. The remaining statistical claims are DC4-R1 and DC4-R2 below. |
| DF3-R4 | **Repaired.** Owner acceptance is presented as a decision sought. |
| DC3-R4 | **Repaired.** Enumeration confirms seven XOR paths, four splits per path, all 28 splits used once, and both test groups of each split kept together. |
| DF3-R5 | **Repaired at proposal level.** Group-start state and the benchmark series are specified. |

**The adjudication is right that an invalidated, posted cycle increments `m`**, and that the halving allowance is an across-cycle multiplicity budget for false promotion. It goes too far when it treats that budget alone as proof of a false-promotion probability bound.

### New findings in the rev 3 → 4 diff

- **DC4-R1 — blocking — §4, “claim is per attempt.”** A fresh seed independent of the data does not, by itself, transfer the D-19 `U_G` rate to *each adaptively reached attempt*. An attempt made only after a prior outcome is conditioned on that outcome and may have a different data distribution. For example, if unavailability is driven by a data feature and a second attempt is made only when the first is unavailable, unavailability conditional on the second attempt can be 1 even though the original ex ante rate is \(p\). Limit the claim to an attempt fixed ex ante, or supply a conditional, sequential argument. The narrower statement about **retaining an available result when retrying solely to escape unavailability** is sound; it does not establish the general per-attempt claim.

- **DC4-R2 — blocking — §4, false-promotion retries.** The supplied O-1 wording establishes the allowance and its sum. Converting that arithmetic into a probability bound across outcome-dependent retries also requires each cycle’s false-promotion test to control error at its assigned allowance **conditional on the history that led to that cycle**. Revision 4 does not state or establish that premise. Keep `m` described as the applicable multiplicity correction, but qualify the asserted probability bound until that conditional guarantee is identified.

- **DC4-R3 — note — §4, “total over all attempts stays below 0.10.”** This is exact for every *finite* number of eligible cycles. Over an unbounded sequence the sum approaches **0.10**; say “below 0.10 after any finite number of cycles, and at most 0.10 overall.”

### Verdict by owner question

| Question | Verdict |
|---|---|
| 1. Code bindings and R-7 | **READY** |
| 2. Null streams and `s_inputs` | **READY** |
| 2b. Model libraries | **READY** as a proposal choice; option (a) remains conditional on the specified image PR and its checks |
| 3. C2 seed source | **NOT READY** — DC4-R1 and DC4-R2 |
| 4. D-13 reporting | **READY** |

**Limits:** The local shell failed during process setup, and no computer surface exposed the checkout. I checked the supplied full revision and diff and enumerated the XOR paths, but could not verify HEAD at `4645e0a`, inspect exact repository bytes or skill instructions, run tests, or confirm library compatibility and image outputs. This is read-only feedback; I made no edits or commit, and it does not activate an owner or statistician decision.
