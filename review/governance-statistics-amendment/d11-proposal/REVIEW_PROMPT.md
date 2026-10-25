# Independent review: D-11 decision proposal (lockbox prediction and pass rule L-1..L-4)

You are an independent adversarial reviewer (read-only), not an authority; the owner (not a statistician,
own capital) decides. This is one of the two different-model AI reviews that owner decision R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`) requires in place of
a human statistician.

Review `review/governance-statistics-amendment/d11-proposal/PROPOSAL.md` (drafted by Claude Fable 5.1 under
`.agents/skills/statistical-binding-review/SKILL.md`; read that skill and follow its method). Verify against
the frozen `protocols/protocol_v1.yaml` (l.67, l.75-95, l.209, l.223-226, l.276-279, l.294-296),
`docs/RESEARCH_CONSTITUTION.md` §7, §7a, §13, the owner decisions it cites (D-01/D-02, D-18, D-20/D-13,
R19-2), the C2 draft `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md`
(§2, l.147, l.254, l.300-360), `review/governance-statistics-amendment/LOCKBOX_PREDICTION_PROPOSAL.md`,
the technical appendix and paired-Sharpe records it cites, and the code it names
(`paired_sharpe_statistics`, `difference_series_sharpe`, `type_seven_quantile`, `bootstrap_indices`,
`ReplicateStream`, `block_length`, `max_drawdown`, `daily_net_returns`). You may run read-only Python with
`D:\PMP-programs-for-sharawi\autonomous-quant-trader\.venv\Scripts\python.exe -B` importing this checkout's
`src` to check the worked numbers; write nothing.

Check:
1. Is Route A a faithful reading of the frozen text (l.84-91), and is the claim that l.85 cannot identify
   E-IMPROV (so Route B is an amendment) correct?
2. Are the definitions complete and unambiguous (m = 457, source, resampling identity, block length input,
   statistic, quantile and numerics, availability, identity boundary, L-1..L-4)?
3. Are the worked numbers right (type-7 position, boundary cases, float64 vs exact, the E-IMPROV/E-DIFF
   disagreement example, the approximate coverage 0.080 and power figures and their stated assumptions)?
4. Are the findings D11-1..D11-11 right, and is anything missing (dependence, selection, identity boundary,
   leakage, unavailable-cannot-pass, what D-12 and D-20 inherit)?
5. Are the owner questions Q1-Q3 fair, complete and answerable by a non-statistician, with an honest
   recommended option? Is any decision missing?
Findings: IDs `D11R-<reviewer>-n` (Codex Sol: `D11R-S-n`; Codex Astra: `D11R-A-n`) with severity, place,
failure scenario and minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
