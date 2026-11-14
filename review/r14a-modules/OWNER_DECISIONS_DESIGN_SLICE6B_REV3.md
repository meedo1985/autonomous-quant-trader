# Owner decisions on slice 6b design rev 3 re-check items (B-1..B-5)

- Date: 2026-11-14. Asked by Claude Opus 5.5 in Claude Code (multiple-choice question); the
  owner's selections are recorded verbatim below. These are direction for design rev 4, not
  activation of any governance change; rows that touch P18 or S4 wording still follow the
  Constitution's amendment process.
- Source items: `ADJUDICATION_RECHECK_DESIGN_SLICE6B_5CD2A29.md` (R14D6B3-F-1..13).

| Item | Finding | Owner selection |
|---|---|---|
| B-1 | R14D6B3-F-1 capture record | "Offline checks (Recommended)": module checks body = frozen tip block hash, CDX timestamp form, link to the acceptance record; logs the record's SHA-256; truth and earliest-capture are a stated store/verifier obligation. |
| B-2 | R14D6B3-F-2 day 0 | "Block time (Recommended)": day 0 = header time of the block containing the post; acceptance record gains the 80-byte header, checked to hash to `block_hash`. |
| B-4 | R14D6B3-F-5 runner breaches | "Record family U_ops (Recommended)": the family is recorded failed with a U_ops reason naming the attempt; the cycle continues. Touches P18-1/P18-7 wording. |
| B-5 | R14D6B3-F-8 `DAYS_INCOMPLETE` | "U_proc (Recommended)": stays U_proc; `U_OPS_REASONS` unchanged. |

Not asked: B-3 (fixed outcome label for a look entry without an evaluation record). Rev 4
carries an AI-proposed label marked `[OWNER]`.
