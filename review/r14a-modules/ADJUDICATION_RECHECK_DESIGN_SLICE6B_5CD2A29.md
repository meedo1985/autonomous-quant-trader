# Adjudication: Fable 5.2 re-check of slice 6b design rev 3 (R14D6B3-F-1..13)

- Record adjudicated: `FABLE_RECHECK_DESIGN_SLICE6B_5CD2A29.md` (commit `2a7e17a`), verdict FIX.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority;
  this file approves nothing and closes no owner item.
- Date: 2026-11-14.

## Evidence checked by the adjudicator

- Design rev 3 l.33-62, 104-122, 196-221: the quoted text is as the record says (capture hash
  in the declaration; `cycle_start` from the chain log; `now` from the step-7 entry; aborted
  look "is the P18-1 crash accounting's case"; U_ops by reason string; A-3 "decided").
- `c2_confirmation.py`: `ACCEPTANCE_FIELDS` l.2451-2454 and `Started` l.2661-2673 hold no time
  (F-2); `nominate` l.890-897 returns U_ops for not-completed, hash mismatch and misaligned
  days without a reason code (F-7); `baseline_d` raises `DAYS_INCOMPLETE` on a short run
  after bars were accepted (F-8).
- `dsr.family_block` l.100-105 returns the median for any rule other than `"largest"` (F-10).
- O-6a `SPEC.md` l.91-108: the qualifying capture is requested once the post is accepted, `T`
  is frozen at the freeze point 7 days later (F-1).

## Decisions

| ID | Decision | Action |
|---|---|---|
| F-1 | Accept. The declaration cannot bind the capture record. | Rev 4 states it. Choice (a) offline checks + logged hash + stated residual vs (b) second posted commitment goes to the owner (**OWNER B-1**, AI rec (a): no new channel rule). |
| F-2 | Accept. No verified time exists in `start`'s outputs. | Which instant is day 0, and its source, go to the owner (**OWNER B-2**). AI rec: day 0 = the inclusion block's header time, from an 80-byte header added to the acceptance record (a DESIGN schema) and checked to hash to `block_hash`. |
| F-3 | Accept as proposed. | Rev 4: one clock read before step 5, passed as `recorded_at_utc` at step 7; test: early look leaves no entry. |
| F-4 | Accept. | Rev 4: delete the P18-1 reference; a look entry without an evaluation record ends the cycle with no pick and no second look; step 7 tolerates intervening entries of other cycles, an intervening entry of this cycle is that case. The fixed outcome label and that the store records it go to the owner (**OWNER B-3**, cycle-outcome wording). |
| F-5 | Accept. | Rev 4 applies the module-side part: "completed" derived from exactly one valid result entry before any outcome; `evaluate_trial` calls `finish_attempt(completed)` after its append; the `trial_states` input change is named. Remaining breaches: record the family failed U_ops (touches P18-1/P18-7) vs keep refuse with the consequence written in §11 go to the owner (**OWNER B-4**, AI rec: record the family U_ops, so P18-7's "never dropped" holds). |
| F-6 | Accept as proposed. | Rev 4: `read` returns composite + series only; partition manifests taken from `composite.partitions`; `cycle_id` and protocol hash bound; step 3 removed; lockbox only as sealed hash. |
| F-7 | Accept as proposed. | Rev 4: full precedence (not completed, day mismatch → U_ops; then U_ops reasons; else U_proc); hash mismatch stays `CycleError` at §3 rule 5 and `nominate` keeps its check as defence. |
| F-8 | Accept. Rev 3 overstated the owner's A-3 answer. | Rev 4 marks the reason list as an owner item with both placements of `DAYS_INCOMPLETE` shown (**OWNER B-5**); `U_OPS_REASONS` unchanged until decided. AI rec: `DAYS_INCOMPLETE` stays U_proc (a short run on accepted bars is the trial's own failure). |
| F-9 | Accept. | Rev 4 adds the termination/invalidation row: record type, payload `{cycle_id, kind, reason}`, same anchored ledger, appended by the store on human action; both entry points refuse when one exists; residual stated. |
| F-10 | Accept. | Rev 4: `family_block_rule` must equal the qualification object's and be in `choices.RULES`; `drand_scheme == SCHEME`; `z_crit` compared as decimal strings. |
| F-11 | Accept. | Rev 4 names the 6a contract change (`start` keeps the qualification report), the `trial_states`/`look_allowed`/v2 key changes, the "every entry of this cycle lies after the anchor" rule; the anchor drops `path` (head hash + entry count). |
| F-12 | Accept. | Rev 4 states refuse-before-read as the chosen reading and adds a declaration-time check that `T=<T>` exists and `for_k` succeeds for each family's K. |
| F-13 | Accept. | Rev 4 wording fixes. |

No finding is left unrepaired. Five items (B-1..B-5) need the owner's choice before rev 4 is
final; rev 4 can be drafted with the AI recommendations marked `[OWNER]` meanwhile.
