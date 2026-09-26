# Task 21 fourth review adjudication

Review record: `REVIEW_4.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0dee9-4d3b-7c91-9c35-f15b749137dd`), run on 2026-09-26 at the owner's
request ("let astra review the task 21 fixes again"). Packet: `REVIEW_3.md`,
`ADJUDICATION_3.md`, the repair diff `fb84c36..e701b37` for code and tests, the
current governor modules and tests line-numbered, recorded checks (not rerun),
`bars.py` and `canonical.py` excerpts, `protocol_v1.yaml` lines 49-62,
Constitution sections 14, 20, 21 and 22, and roadmap Task 23. Verdict:
**ACCEPT**, no new findings. R3-1 deferral ACCEPTED; R3-2 REPAIRED.

The reviewer scoped the verdict: it does not resolve T21-Q1, complete Task 23's
safety behaviour, or supply the section 16 human approval.

## Corrections to the AI's own records

The reviewer found two inaccuracies in AI-written records. Both are corrected
here and at the places named; the original wording in `ADJUDICATION_3.md`
stays as written.

1. **HALT does not reduce holdings.** `ADJUDICATION_3.md` and `LOCAL_REPORT.md`
   said "HALT and FLATTEN must reduce exposure at once". Roadmap Task 23 has
   HALT place no order while exposure is held, and FREEZE permits no
   autonomous risk change. The requirement carried to Task 23 is: **FLATTEN**
   must reduce exposure at once, at any time, including while a governor
   reservation is outstanding, in coordination with that reservation.
   `LOCAL_REPORT.md` is corrected.
2. **Not every invalid `now` raises `ValueError`.** `ADJUDICATION_3.md` said an
   invalid `now` raises `ValueError`. A naive or non-zero-offset datetime does;
   a non-datetime value raises `AttributeError`. In every case this happens
   before the governor changes, which is the property that matters.

## Test gaps noted by the reviewer (not findings), closed

- Invalid `now` in `release`, a non-zero UTC offset, and a non-datetime `now`
  are now covered: `test_every_entry_point_rejects_a_bad_now_without_changing_state`.
- The late-release test now also asserts the 00:06 refusals.
