# D-19 acceptance record: keys, coins and deadline (full-run precondition P2)

**Status: ACCEPTED by the owner, 2026-10-20.** Drafted 2026-10-19 before the coins existed; every value below is filled only from checked public data or the owner's recorded answer.
**Prepared by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI records; the owner decides. No seed, private key or password appears here, ever.

## Why this record exists

`OWNER_DECISION_D19_ACCEPT.md` (effect 1) and `OWNER_DECISION_S13_ACCEPT.md` ("Still required"): acceptance of the D-19 preregistration is complete only when `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2` are committed, before the development phase. Prereg §4 fixes them "at the preregistration's acceptance" as `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2>>`.

## 1. Values (P1)

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Address `A_Qn` | `bc1qccn3q8ja6wq4cefuzzzdv3nckjuedqw95wmdws` | `bc1qj9jzenczghkav85jyn82vnplch5wqtwahdqray` |
| Public key | `0279da9408e066a8a5bc791b6e0c63a5a17e927b547617f39c9790a6f5bb477686` | `02670ee4336fe38e762fac1cc642ebf2a1f38d13634bff54ad96f790ffe70cb25c` |
| Coin `F_Qn` outpoint | `00ceaef0e0f6348ff881177661cf45916696bf5674329e5fd2f3def03a2a7e7d:0` | `0aa682d2f10e6c139d6521299849d0fb9ff18d9349c3e4821887491ed3f330cc:0` |
| Amount (sat) | `5500` | `5709` |
| Block height | `972269` | `972270` |
| Deadline `D_Qn` | `1000000` (owner, 2026-10-19) | fixed later, in the attempt-2 record (DF5-3) |

Keys: `KEY_RECORD_DRAFT.md` (2026-10-12; each public key hashes to its address).

## 2. Checks at acceptance (OF1-3, OF4-2)

Done on `mempool.space` and `blockstream.info`, at acceptance height 972,271 (tip on both explorers), 2026-10-20 06:00 UTC, by Claude Opus 5.5 (`claude-opus-5-5`) through each explorer's `/api/address/<A>` and `/api/address/<A>/utxo`:

- [x] each address received exactly one payment, the `F_Qn` above, confirmed;
- [x] neither address has ever been spent from, and neither has a mempool transaction;
- [x] the two explorers agree (any disagreement is recorded and blocks acceptance); they agreed on every field;
- [x] `D_Q1` > acceptance height (1,000,000 > 972,271).

Result on both explorers: attempt-1 address funded 1, spent 0, mempool 0, one unspent output `00ceaef0...7e7d:0` of 5,500 sat at height 972,269; attempt-2 address funded 1, spent 0, mempool 0, one unspent output `0aa682d2...30cc:0` of 5,709 sat at height 972,270. Both coins were paid from the owner's Trust Wallet (fees 418 and 356 sat). Each coin pays the later post's fee and its change (SPEC §7): about 160 vB plus at least 294 sat of change, so it covers a post fee rate up to about 30 sat/vB. A coin cannot be topped up, so a post waits for fees below that.

## 3. Deadline `D_Q1` (owner's choice)

Rule (O-6a SPEC §3 by substitution, prereg §4): `D_Q1` ≈ the height at which the owner plans to post `AQTQ1`, plus 4,320 blocks (about 30 days). **If no post is in a block by `D_Q1`, attempt 1 is void and its key is used up**, so a deadline that is too early costs an attempt; a later one costs nothing.

Planning estimate (2026-10-19, tip 972,122, about 144 blocks a day): the full run starts about 2026-11 and takes about 2½ months (`OWNER_DECISION_FE7_GO_AHEAD.md`); choice, freeze and post follow. A conservative planned post is 2027-03-31, about height 995,600, so `D_Q1` ≈ 999,900.

**Proposed: `D_Q1 = 1,000,000`** (expected about the end of April 2027). The owner's answer is recorded verbatim in §5.

## 4. Pinned hash (P2 to P3)

The accepted preregistration is `PREREGISTRATION.md` with the `<<ACCEPTANCE: ...>>` placeholder replaced by the values in §1, committed together with this record. Its SHA-256 at that commit is `ffadd2b5cdc72fa663ba5a0661f47fcdc2615ad8f660122b7611eb57e8f09f71`. That commit is the one that adds this record; it cannot name itself, so `git log -- review/d19-engine/ACCEPTANCE_RECORD.md` gives it and the pin PR records it. A separate PR then sets `calibration/rundef.py` `ACCEPTED_PREREG_SHA256` to that value (Sol review and owner §16 review).

## 5. Owner's answers (verbatim, recorded at acceptance)

**Coins (2026-10-20, after both explorer checks).** Asked: "Are these the two coins you paid, from your own wallet? Attempt 1: 00ceaef0…7e7d:0, 5,500 sats, block 972,269, to bc1qccn3…mdws. Attempt 2: 0aa682d2…30cc:0, 5,709 sats, block 972,270, to bc1qj9jz…qray." Options: "Yes, these are my coins" (both payments were made by you, and only you hold the seed words for both Electrum wallets); "No / not sure" (stop). Owner's answer, verbatim (the option label chosen): "Yes, these are my coins".
**D_Q1 (2026-10-19, before funding).** Asked, with options: "Deadline D_Q1 for the attempt-1 Bitcoin post: if the post is not in a block by this height, attempt 1 is void and its key is used up. A late deadline costs nothing; an early one can cost an attempt. Which deadline?" Options: "1,000,000 (Recommended)" (expected about end of April 2027: the ~2½-month run from November, choice and freeze, planned post by 2027-03-31, plus the rule's 30-day margin); "1,010,000" (about 10 weeks later, ~mid July 2027). Owner's answer, verbatim (the option label chosen): "1,000,000 (Recommended)". The check `D_Q1` > acceptance height is made at acceptance.
**Acceptance (2026-10-20).** Asked: "Do you accept the D-19 preregistration with these values (both coins, deadline D_Q1 = 1,000,000)? This completes acceptance. After it, the values are fixed and both coins must never be spent except by the official post." Options: "Accept" (I commit the filled preregistration and this record together; its hash then goes to a separate PR, Sol review + your §16 review); "Not yet" (nothing is committed). Owner's answer, verbatim (the option label chosen): "Accept".
