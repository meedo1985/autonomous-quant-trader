# Adjudication of the focused checks of D-14/D-15 rev4 (`83fc993`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_83FC993.md`: FN4, NOT READY, `f0f676a`.
- `SOL_REVIEW_83FC993.md`: SN4, NOT READY, `e5512a4`.

All findings are accepted and none is rejected. They are applied in revision 5.

| Finding(s) | Disposition in rev 5 |
|---|---|
| FN4-1, SN4-3 | §1.2 uses a three-layer declaration: signal, sizing, and overlay. Declared overlays are re-run on every draw. Q1b recommends that re-run. Its options say plainly that the `N/A` route lets a trial be promoted without G-11 evidence, and that a stop which never fires would be enough to opt out. Testability is checked mechanically against the hashed interface. |
| FN4-2 | §2.1 Q20 adds a proposed row N-4, which governs all runs. Option (i) drift traps positions below 0.10, shown exactly. Option (ii) uses the last filled target. Option (iii) drift with exits to 0 always allowed (amends l.60) is recommended. |
| FN4-3 | §2.1 states that under the recommended anchor the 24 h test never binds. It cites l.113, and C-3 records it. |
| FN4-4 | §1.2 restricts `σ̂` to l.115 and l.121, with the annualization from CANONICAL l.23. The gaming argument is applied to Q2 and Q3 as well. |
| FN4-5 | §2.1 uses the trial's declared band (l.97; l.112 default 0.10; CANONICAL l.10, l.26). |
| FN4-6, SN4-4 | §2.2: each input takes its last value emitted at or before `t − 1h` under its own declared emission schedule. No partial aggregate is built, and the rev 4 "recompute" option is removed. For FEATURE_FACTORY hourly features this is exactly a one-bar lag. |
| FN4-7, SN4-2 | §2.1 splits the question in two: Q10a asks what counts as an increase (recommendation: an actual rise at fill, per l.57), and Q10b asks what the clock is anchored to. |
| FN4-8, SN4-1 | §2.1: every fill, including the same-instant baseline fill, updates all state atomically. |
| FN4-9, SN4-7 | §3 is recounted per gate and per asset, as stressed runs only. |
| FN4-10, FN4-11, SN4-6 | §2.3: each gate's benchmark choice applies to BTC and ETH alike. The ETH candidate leg is a separate option, so candidate-only stress can be expressed. Every leg runs at 1x cost unless stated. Q13 is labelled a reading. |
| FN4-12 | `g` is fixed by the draft (§1.1) and is not an owner question. This corrects the line in `ADJUDICATION_540E773.md` that called `g` part of Q6; that committed record is left as it was. |
| FN4-13 | §1.1: `T` is the number of UTC days in the window. |
| FN4-14 | History restores both reviewers' qualifiers. |
| SN4-5 | Q19 asks the owner to accept the whole event contract, and C-3 lists all of its bindings. |

**Review cadence [AI default].** The revision 4 → 5 changes are bounded, and
the core construction is unchanged. One more focused check by both reviewers
follows before the owner is asked.
