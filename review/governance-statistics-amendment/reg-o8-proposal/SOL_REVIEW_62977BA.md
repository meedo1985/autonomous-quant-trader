# Sol focused check of the REG-1/REG-2/O-8 proposal rev 3 at `62977ba` — NOT READY

Date: 2026-10-04. This is the OpenAI-family focused check for R19-2, run from prompt `REVIEW_PROMPT_R2.md` with prefix SR3. The prompt carried a preamble saying that SR2 (on rev 2) was killed by the system for low memory with no output, and that SR3 also covers rev 2's changes.

It ran under `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10589-246e-7c42-b6e3-9c8336b2f66a`. The final message below is verbatim.

---

Model: GPT-5 (OpenAI GPT family, Codex; exact serving variant is not exposed)  
Commit checked: `62977ba6f96300846161a60ea946d3e13bf20e7c`  
Verdict: **NOT READY**

Earlier-review resolution: SR1-2 through SR1-5 are resolved. SR1-1 is corrected in the body but not carried accurately into the owner question; therefore SR1-6 remains unresolved. SR1-7 also remains unresolved. Against the FR2 addendum, FR2-1 and FR2-9 remain unresolved.

| ID | Severity | Location | Evidence | Proposed disposition |
|---|---|---|---|---|
| SR3-1 | BLOCKER | `PROPOSAL.md` §6 Q1(A), versus §1 lines 37–62 | Q1(A) says “Your exact 10% rule cannot be registered,” but §1 correctly admits that a declared model with return-history access can reconstruct `σ̂` exactly. The declared-input ban prevents direct/honest use; it does not make exact fixed-size reconstruction impossible. Mentioning only “near-copies” understates the bypass and leaves SR1-6 unresolved. | Say that option A bars direct registration and accidental cancellation, but a deliberate model may reconstruct the exact number and proxies may approximate it. Present `KEEP_BLOCKED` explicitly if that residual is unacceptable. |
| SR3-2 | BLOCKER | §4 O-6a candidate; §6 Q3 | The proposed Bitcoin channel is explicitly unverified, so it does not resolve SR1-7/FR2-1. Its current description is also insufficient: Bitcoin has UTXO spends rather than a protocol-level “from address”; inbound transactions can involve the address without authenticating the poster; reorganizations require a finality rule; miner block time is only a bounded timestamp; pruned full nodes do not provide a permanent independent archive; and funding can link the supposedly pseudonymous identity. | Before asking the owner, verify and specify the fixed key/script, qualifying spend/message rule, enumeration procedure, confirmation depth, canonical timestamp, independent archive evidence, fee/funding lifecycle, and privacy disclosure. Otherwise omit Bitcoin and offer only trusted-third-party or `KEEP_BLOCKED`. |
| SR3-3 | MAJOR | §2 lines 103–110 and option (b); §6 Q1(C) | “Very unlikely unless the benchmark had a poor window” is an unsupported probability claim. Candidate timing covariance can materially change `E-DIFF`; size alone does not imply `C−B≈−B`. Exact synthetic counterexample: with benchmark exposure 0.6, a causal perfectly predictive 10% signal, 625 `+1%` and 623 `−1%` days gives benchmark Sharpe `+0.0306` and `E-DIFF=+1.7055`. This does not prove likely promotion, but proves poor benchmark performance is not the only route. Moreover, C2’s `z_crit` remains `<<D19>>`, so no pass probability is presently identifiable. | Retain “the DSR may mostly measure the benchmark and be poorly informative about the 10% rule.” Replace the likelihood claim with “pass probability is unknown until the signal, family, window, and D-19 critical value are fixed; poor benchmark performance and genuine timing edge are distinct routes.” |
| SR3-4 | MAJOR | `ADJUDICATION_370C50C.md` lines 29–31 and addendum line 53 | FR2-9 says the Annex C follow-up “now” covers the identity mapping and combined REG answer, but the actual follow-up still records only `s_inputs` if REG-2(a) is selected. The promised retention repair was not made. | Expand the follow-up entry to preserve the combined REG decision, `s_inputs`, the `ewma_vol_168h`/sizing-estimator identity mapping, and the consequences of the selected option. |

O-8 remains supported by the cited code and its owner question is sufficiently accurate. Checks were read-only: no network or restricted data; the commit changes only the two proposal records; `git diff --check` and independent frozen-artifact verification passed. Tests, lint, typing, and import-boundary checks are N/A for this Markdown-only review.

The sizing/estimand correction and O-8 analysis are substantially sound, but the owner questions still overstate what REG-2(A) prevents and what can be inferred about DSR passage.  
Do not ask O-6a yet: the Bitcoin candidate is unverified and lacks authentication, finality, timestamp, archive, enumeration, and privacy contracts.  
Repair SR3-1 through SR3-4, preserve the Annex C follow-up explicitly, and run the required focused different-model check again.
