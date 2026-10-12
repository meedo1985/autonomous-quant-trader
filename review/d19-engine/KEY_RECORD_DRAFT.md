# D-19 attempt keys: draft key record (O-6a channel, preregistration §4)

**Status:** DRAFT. The keys are recorded; the bound coins `F_Q1` and `F_Q2` and the deadline `D_Q1` are pending. The values become `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2>>` only in the owner's acceptance record. `D_Q2` is fixed later, in the attempt-2 record (DF5-3).
**Supplied by:** the owner, 2026-10-12. He generated each key offline in its own Electrum 4.8.2 wallet (installer signature verified, key fingerprint `6694 D8DE 7BE8 EE56 31BE D950 2BD5 824B 7F94 70E6`). Only public data is recorded here. No seed, private key or password has been shared, and none may ever be added to this repository.
**Checked by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-12.

| Attempt | Address `A_Qn` (P2WPKH) | Public key |
|---|---|---|
| 1 | `bc1qccn3q8ja6wq4cefuzzzdv3nckjuedqw95wmdws` | `0279da9408e066a8a5bc791b6e0c63a5a17e927b547617f39c9790a6f5bb477686` |
| 2 | `bc1qj9jzenczghkav85jyn82vnplch5wqtwahdqray` | `02670ee4336fe38e762fac1cc642ebf2a1f38d13634bff54ad96f790ffe70cb25c` |

**Checks (2026-10-12, chain tip 971106):**
- Each public key is a valid compressed secp256k1 point. Its `bech32(0, HASH160(pubkey))` equals the address given.
- Both addresses have no funding, spending or mempool transaction, on both mempool.space and blockstream.info (`tx_count: 0`).

**Pending:** the owner's funding payment to each address (`F_Qn`: outpoint, amount, height); the check, at acceptance, that each address has never been spent from and holds only its `F_Qn` (OF1-3); and `D_Q1`.
