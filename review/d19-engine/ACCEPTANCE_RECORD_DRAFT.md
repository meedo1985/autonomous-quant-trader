# D-19 acceptance record: keys, coins and deadline (DRAFT, full-run precondition P2)

**Status: DRAFT, prepared 2026-10-19 before the coins exist.** Every `<<...>>` is filled only from checked public data or the owner's recorded answer. Not valid until the owner answers and the record is committed.
**Prepared by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI records; the owner decides. No seed, private key or password appears here, ever.

## Why this record exists

`OWNER_DECISION_D19_ACCEPT.md` (effect 1) and `OWNER_DECISION_S13_ACCEPT.md` ("Still required"): acceptance of the D-19 preregistration is complete only when `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2` are committed, before the development phase. Prereg §4 fixes them "at the preregistration's acceptance" as `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2>>`.

## 1. Values (P1)

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Address `A_Qn` | `bc1qccn3q8ja6wq4cefuzzzdv3nckjuedqw95wmdws` | `bc1qj9jzenczghkav85jyn82vnplch5wqtwahdqray` |
| Public key | `0279da9408e066a8a5bc791b6e0c63a5a17e927b547617f39c9790a6f5bb477686` | `02670ee4336fe38e762fac1cc642ebf2a1f38d13634bff54ad96f790ffe70cb25c` |
| Coin `F_Qn` outpoint | `<<F_Q1 txid:vout>>` | `<<F_Q2 txid:vout>>` |
| Amount (sat) | `<<F_Q1 amount>>` | `<<F_Q2 amount>>` |
| Block height | `<<F_Q1 height>>` | `<<F_Q2 height>>` |
| Deadline `D_Qn` | `1000000` (owner, 2026-10-19) | fixed later, in the attempt-2 record (DF5-3) |

Keys: `KEY_RECORD_DRAFT.md` (2026-10-12; each public key hashes to its address).

## 2. Checks at acceptance (OF1-3, OF4-2)

Done on `mempool.space` and `blockstream.info`, at acceptance height `<<ACCEPTANCE HEIGHT>>`, `<<UTC time>>`:

- [ ] each address received exactly one payment, the `F_Qn` above, confirmed;
- [ ] neither address has ever been spent from, and neither has a mempool transaction;
- [ ] the two explorers agree (any disagreement is recorded and blocks acceptance);
- [ ] `D_Q1` > acceptance height.

## 3. Deadline `D_Q1` (owner's choice)

Rule (O-6a SPEC §3 by substitution, prereg §4): `D_Q1` ≈ the height at which the owner plans to post `AQTQ1`, plus 4,320 blocks (about 30 days). **If no post is in a block by `D_Q1`, attempt 1 is void and its key is used up**, so a deadline that is too early costs an attempt; a later one costs nothing.

Planning estimate (2026-10-19, tip 972,122, about 144 blocks a day): the full run starts about 2026-11 and takes about 2½ months (`OWNER_DECISION_FE7_GO_AHEAD.md`); choice, freeze and post follow. A conservative planned post is 2027-03-31, about height 995,600, so `D_Q1` ≈ 999,900.

**Proposed: `D_Q1 = 1,000,000`** (expected about the end of April 2027). The owner's answer is recorded verbatim in §5.

## 4. Pinned hash (P2 to P3)

The accepted preregistration is `PREREGISTRATION.md` with the `<<ACCEPTANCE: ...>>` placeholder replaced by the values in §1, committed together with this record. Its SHA-256 at that commit is `<<PREREG_SHA256>>`, and that commit is `<<PREREG_COMMIT>>`. A separate PR then sets `calibration/rundef.py` `ACCEPTED_PREREG_SHA256` to that value (Sol review and owner §16 review).

## 5. Owner's answers (verbatim, recorded at acceptance)

`<<question and answer: the values in §1 are your coins>>`
**D_Q1 (2026-10-19, before funding).** Asked, with options: "Deadline D_Q1 for the attempt-1 Bitcoin post: if the post is not in a block by this height, attempt 1 is void and its key is used up. A late deadline costs nothing; an early one can cost an attempt. Which deadline?" Options: "1,000,000 (Recommended)" (expected about end of April 2027: the ~2½-month run from November, choice and freeze, planned post by 2027-03-31, plus the rule's 30-day margin); "1,010,000" (about 10 weeks later, ~mid July 2027). Owner's answer, verbatim (the option label chosen): "1,000,000 (Recommended)". The check `D_Q1` > acceptance height is made at acceptance.
`<<question and answer: accept, completing the acceptance of D-19>>`
