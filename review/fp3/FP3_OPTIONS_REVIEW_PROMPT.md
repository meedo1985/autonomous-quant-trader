# Independent review: FP3 options paper

You are an independent adversarial reviewer (read-only), not an authority; the
owner decides. Review `review/fp3/FP3_OPTIONS.md` in this checkout.

Check:
1. Facts: the three drand mainnet chains (hashes, public keys, periods, genesis,
   schemes, guidance, retirement history). Verify against official drand sources
   (api.drand.sh, docs.drand.love, github.com/drand) with web search.
2. The central governance question: is route R3 (an owner binding decision on the
   accepted preregistration, committed before step G, pre-binding the C2 chain)
   a valid way to satisfy FP3 under `docs/RESEARCH_CONSTITUTION.md` (§3, §4),
   `AGENTS.md`, the accepted preregistration and its acceptance record
   (`review/d19-engine/ACCEPTANCE_RECORD.md`), `deploy/calibration/FREEZE_HELDOUT.md`
   FP3 ("Constitution amendment process or C2 signing"), and the project's prior
   owner decisions? If not, what minimal formal route is valid, and is R1 really
   the only remaining one? Also: how must such a decision be signed and dated
   (AI-made commit under the owner's account vs a commit the owner makes)?
3. Are the recommendations (quicknet; missing-output rule (a) with VOID; R3) sound
   and fairly presented, without steering the owner?
4. Any other defect, missing decision, or risk (for example: what if the chosen
   chain is retired between FP3 and the round; signature-verification tooling).
Findings: IDs `FP3-R1`, ... with severity, place, failure scenario, minimal
repair. Then a verdict: ACCEPT or FIX. Cite paths and URLs.
