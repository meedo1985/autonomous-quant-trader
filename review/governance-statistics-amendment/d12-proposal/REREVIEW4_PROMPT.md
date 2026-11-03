# Independent re-check 4: D-12 proposal revision 5

You are an independent adversarial reviewer (read-only), not an authority. This is the fourth R19-2 re-check.
Revision 5 is `review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md`, a delta on `PROPOSAL_REV4.md`
(chain: PROPOSAL_REV2 -> REV3 -> REV4 -> REV5); its §11 "Current binding summary" states the bindings as they now stand.

Your own earlier record (check ONLY your own findings in (1)):
- If you are Codex Sol (gpt-6-sol): `SOL_REREVIEW3_DF9E0D0.md`, findings D12R4-S-1..5 (verbatim labels U-n; header maps to S-n).
- If you are Codex Astra (gpt-6-astra): `ASTRA_REREVIEW3_DF9E0D0.md`, findings D12R4-A-1..4.
The launcher states your model; use it.

Check: (1) is each of YOUR re-check-3 findings resolved as claimed; (2) are the new parts sound and consistent with the
frozen sources (Constitution §7/§13, protocol_v1.yaml l.67-95 and l.294-300, THREAT_MODEL_v1.md) and the C2 draft
(l.244-245): hourly publication slots V_k chosen at publisher restart and store-enforced visibility; timing tests
T-4..T-6; fractional bounds and slack; cooling_off_start := V_k via pre-signed per-slot attestations; the single
meaning of "attested" and the proposed l.244/l.245 wording; store-computed commitment and P-8 validation; the
disclosed residual channels (slot shift, signature nonce); does the §11 summary match the delta chain;
(3) are owner questions Q1, Q2a, Q2b, Q3-Q5, Q6(i), Q6(ii) fair, honest about costs, answerable by a
non-statistician, and complete; (4) any new defect, and whether anything is more complex than the problem needs.
Classify each finding BLOCKER or NON-BLOCKING (wording). Write nothing.
New IDs: Codex Sol `D12R5-S-n`; Codex Astra `D12R5-A-n`. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
