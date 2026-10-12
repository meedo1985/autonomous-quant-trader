# Adjudication of FA5 and SA5 (rev 5 `ab9ad3f`) → revision 6

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter. This adjudication is
not an authority: owner items stay with the owner.
**Records:**
- `FABLE_REVIEW_AB9AD3F.md` (`883eec5`): SOUND WITH FIXES, 2 blockers, 15
  non-blocking findings.
- `SOL_REVIEW_AB9AD3F.md` (`404b8e5`): SOUND WITH FIXES, 4 blockers, 4
  non-blocking findings.

Both reviewers found every gate's pass rule, `N/A` case and availability
rule faithful to the owner records, except where noted below. Every finding
is listed. None is left unrepaired without a reason.

| Finding | Disposition | Where in rev 6 |
|---|---|---|
| FA5-1, SA5-3 (seed channel defeatable) | **Accepted.** The procedure now requires one authenticated, dedicated, append-only identity fixed in the protocol, a third-party timestamp and an independent archive. The message is canonical. Every post at that identity counts, and the first governs. The chain is fixed in the protocol at signing. The beacon output must verify against the chain's public key. There is no fallback. | DRAFT §2.0 `seed_disclosure` |
| FA5-2, SA5-1 (baseline application of the full Q19 contract never presented) | **Accepted. New owner item O-8.** N-4 (exits) and Q10 (clock) were presented as applying to all runs and stay decided. The rest of Q19, as applied to baseline and benchmark runs, is marked `<<OWNER O-8>>`. | Annex C C-6 (7); DRAFT §4, §7 |
| SA5-2 (the fixed 10% "cannot be expressed") | **Accepted. This was a drafting error against the addendum.** A fixed 10% is `s = 0.10·σ̂/τ`, which needs `s` to depend on `σ̂`. So REG-1 depends on REG-2. No re-ask is needed, because the owner was given the correct fact. | Annex C C-10 (1); DRAFT §7 |
| SA5-4, FA5-7 (l.113 leaf shape) | **Accepted.** l.113 stays a scalar. The anchor meaning goes in the l.57 value and the l.56–58 justification. | DRAFT §1a |
| FA5-3 (reroll by aborting after seeing the beacon) | **Partly accepted.** The cost is now stated: a cycle invalidated after its post increments `m` (O-1 already implies this). It is disclosed in §5. **Whether that invalidation also consumes the window is offered to the owner as O-9.** The recommendation is no, because C2's window is the only eligible one and consuming it ends promotion for both families. This is the reviewers' option, not a new decision. | DRAFT §2.0, §5, §7 |
| FA5-4 (declarer chooses the chain) | **Accepted.** The chain is fixed in the protocol at signing. | DRAFT §2.0 |
| FA5-5 (derivation ambiguous against Annex B) | **Accepted.** `family_seed_f = SHA256(annexB_family_seed_f ‖ round ‖ beacon_randomness)` **extends** Annex B §2.4. The declaration bytes are the Annex B canonical-JSON declaration. The round and the randomness are recorded for §27. The byte encoding stays `<<OPEN D-20>>`. | DRAFT §2.0 R-7, `derivation` |
| FA5-6 (trial-seed streams not beacon-protected) | **Accepted as a disclosure**, in C-13 and §5. Mixing the beacon into the G-1, G-11 and G-14 streams would change decided D-14 Q7 and N-2. It is not offered now; the owner may raise it. | Annex C C-13; DRAFT §5 |
| FA5-8 (§1a incomplete) | **Accepted.** Rows added: CANONICAL l.3 and l.38, BACKTESTER l.3, protocol l.8 and l.133 `benchmark_set_hash`, and a new FROZEN_HASHES key. The heading now names D-14 and D-08. `src/aqt/benchmarks/canonical.py` is added to the §16 list. | DRAFT §1a, §6 |
| FA5-9 (deleted §4 sentences) | **Accepted.** Both sentences are restored. | DRAFT §4 |
| FA5-10 (markers incomplete) | **Accepted.** D-20 rows added for C-0 Sharpe, C-0 `max_drawdown`, C-1 and C-11. G-1 status now carries D-20. `added_purposes` gains both null purposes. R-8 is extended to Annex C. | DRAFT §2.0, §2.4, §3, §4 |
| FA5-11 (normative line references) | **Accepted.** The `[...]` source tags are informative. In-text `l.n` references are normative, read against v1.0 at its frozen hash. | Annex C header |
| FA5-12 (`s` overloaded) | **Accepted.** The window start is renamed `w0` and the window end `w1`. | Annex C C-0, C-4, C-10 |
| FA5-13, SA5-5 (C-1 unavailability incomplete) | **Accepted** [derived]. | Annex C C-1 |
| FA5-14 (C-8 dimension rule) | **Accepted** [derived]. | Annex C C-8 |
| FA5-15 (model classes in a gate section) | **Accepted.** The rule is moved to DRAFT §2.5. | DRAFT §2.5; Annex C C-12 (8) |
| FA5-16 (unset clock; band value) | **Accepted** [AI default]. An unset clock permits the first increase. The declared band is the l.112 value, 0.10. | Annex C C-6 |
| FA5-17, SA5-8 (wording, legend, provenance) | **Accepted.** §6 step 1 says the rows were added by the owner's answers; the matrix file is unedited. The legend is expanded. "Done" is qualified. G-5 provenance adds D-15 Q18. | DRAFT header, §3, §6, §7 |
| SA5-6 (global float64 rule unmarked) | **Accepted.** It is marked `[AI default]` where it extends beyond D-05, D-07, D-10 and D-18. | Annex C C-0 |
| SA5-7 ("two annexes"; G-9/G-13 not in Annex C) | **Accepted.** | DRAFT §0, R-10 |

## Owner items after revision 6

REG-1, REG-2, O-6a, O-8 and O-9. REG-1 and REG-2 need a written proposal
first. O-6a, O-8 and O-9 can be asked as soon as that proposal exists, or
earlier if the owner wishes.

## Not re-reviewed

Revision 6 applies these dispositions without a further check, which is
weaker. The final-wording review in §6 step 2 covers it.
