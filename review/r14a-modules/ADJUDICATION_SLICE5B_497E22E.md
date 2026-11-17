# Adjudication: Sol review of confirmation slice 5b at 497e22e

- Review record: `SOL_CONFIRMATION_SLICE5B_497E22E.md` (gpt-6-sol, high, verdict FIX).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09. The adjudication is the
  author's and approves nothing. The repairs are in the commit that adds this file.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S5B-S-1 | BLOCKER | **Accepted.** The single window-wide embargo let held-out labels change a split's training rows. LG5B-2's reading is withdrawn. | `cpcv_training_rows(times, ys, test, hours, w1)` now keeps the realised, purged candidates and computes the cutoff with `screen.embargo_days` over **those candidates' labels only**. They are laid out as a calendar-day sequence, with test and purged days as `None` gaps, exactly as `screen.training_rows` does. The embargo is then applied after each test group. Tests: the cutoff receives exactly the purged training labels, with gaps; with the real ACF rule, rewriting every label in the test groups and their purge zones leaves the kept rows unchanged. |
| R14S5B-S-2 | QUESTION | **Left open, no code change: owner/governance item.** A training row just after a test group can carry causal features (such as `ret_168h`) whose lookback reaches into that group. protocol_v1.yaml l.205-214 prescribes a label-horizon purge and a label-ACF embargo, not a feature-lookback embargo. Adding one would change the prescribed rule, which needs the governed process. | The module claims only what the text prescribes: no test-group **labels** reach a fit. It does not claim that no test-group feature history does. Recorded as LG5B-7 for the S4 binding. The report is `diagnostic_only` and nothing reads it. |
| R14S5B-S-3 | NON-BLOCKING | **Accepted.** | New test: each split's fit is replaced by a constant model, a different value per split. Every path's E-IMPROV and E-DIFF must equal a write-out that takes group g from split `{g, g XOR p}` (formula inline in the test). All 7 paths must differ. Mutation check: replacing the XOR assignment with another pairing fails this test (run locally, then reverted). |

LG5B-1, -3, -4 and -5 are unchanged; Sol found them consistent with the text. LG5B-3
(signal state continuous) is consistent with C-14 (3)'s explicit reset list, but whether
that was the intent is open, and it is listed for the owner with LG5B-7.

Validation: see `ADJUDICATION_SLICE5A_53B6BBC.md` (same run, 327 passed). Sol re-check:
one round, together with 5a's.
