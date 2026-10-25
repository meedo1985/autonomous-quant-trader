# FP3: binding the drand chain — options for the owner

**Status: AI OPTIONS PAPER — NOT A DECISION — NOT AN AMENDMENT.** Prepared by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, for the owner. Revision 2, after the Codex review `SOL_FP3_OPTIONS_REVIEW.md` (FP3-R1..R7, all accepted). The owner decides. Facts were fetched on 2026-10-25; the raw responses are in `drand-info-2026-10-25/`.

## 1. What FP3 is, in plain words

The held-out test's random seed is built from a public random number that nobody can know in advance: one round of a **drand** beacon (League of Entropy). The preregistration (§8, `review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` line 397) says the round is "the first round of the C2 drand chain (DRAFT §2.0) whose scheduled time is at or after `T_Qn + 24h`". The C2 draft leaves that chain blank, `<<SIGNING: chain hash, public key>>`, and says it is fixed "in this protocol at signing" (`s4-amendment-draft/DRAFT_WORDING.md` §2.0). A blank binds nothing, so today the seed has no defined source. It must be bound **before step G**: a chain picked once beacon outputs are known could steer the result (`FREEZE_HELDOUT.md` FP3).

FP3 has three parts: **which chain**, **what happens if the round's output never appears**, and **which formal act makes both binding before G**. The third is the hard one (section 4).

## 2. Which chain

drand mainnet lists three chains (`chains.json`; drand's [developer page](https://docs.drand.love/developer/)). `default` and `quicknet` values were identical on `api.drand.sh`, `drand.cloudflare.com`, `api2.drand.sh` and `api3.drand.sh`. `evmnet` was read from `api.drand.sh` only.

| | `quicknet` | `default` | `evmnet` |
|---|---|---|---|
| Chain hash | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` | `8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce` | `04f1e9062b8a81f848fded9c12306733282b2727ecced50032187751166ec8c3` |
| Public key | `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a` | `868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31` | see `drand-info-2026-10-25/04f1e906….info.json` |
| Round every | 3 s | 30 s | 3 s |
| Genesis | 2023-08-23 (1692803367) | 2020-07-22 (1595431050) | 2024-09-28 (1727521075) |
| Scheme | `bls-unchained-g1-rfc9380` | `pedersen-bls-chained` | `bls-bn254-unchained-on-g1` |
| One round verifiable alone | yes | needs the previous round's signature too | yes |

History: drand retired `fastnet` (announced 2023; network shut down [2024-11-06](https://docs.drand.love/blog/fastnet-to-be-sunset/)). drand has in the past discussed a possible `default` deprecation; in 2025 it said it had no plan then to wind down `evmnet` ([2025 post](https://docs.drand.love/blog/2025/08/26/verifying-bls12-on-ethereum/)). No retirement notice for `quicknet` or `default` was found in 2024-2026 posts.

**This paper's recommendation (a reasoned choice, not drand's ruling): `quicknet`.** Each round verifies on its own with only the public key, which is simpler and leaves fewer ways to err. `default` (longest record, since 2020) is a sound alternative.

Whatever is chosen also pre-binds the C2 beacon line, because the preregistration names "the C2 drand chain".

## 3. If the round's output never appears

The C2 draft's rule is: "If no verifying output for the round **exists** within 7 days of its scheduled time, the cycle is INVALIDATED". For D-19 this is **not settled**: D-19's VOID boundary (prereg line 270) covers O-6a invalidations, not a missing drand output, and "C2 cycle INVALIDATED" cannot simply be copied to D-19. So this is a **new owner choice**, to be bound with the chain:

- **Criterion (existence, not retrieval):** the output counts as existing if a verifying output for the round is shown to have been published within 7 days of its scheduled time, by evidence fixed in advance. A failure of your laptop or of one relay is not a missing output.
- **Disposition, proposed:** if none exists within 7 days, attempt 1 is **void** before any held-out evaluation; the key is used up; there is never a fallback chain or source. The alternative is no time limit (the attempt stays open).
- **Retirement or halt** of the chosen chain never authorises a switch: the bound rule above applies. Any other chain would need a new, prospective formal binding, with prior exposure and attempt accounting preserved.

## 4. Which formal act makes it binding before G

| Route | Assessment |
|---|---|
| **R1. Constitution §4 amendment** | **The only presently established route among R1-R3.** §4 requires a version bump, written rationale, an owner-of-record signed and dated commit, cycle termination and pre-new-cycle activation (`docs/RESEARCH_CONSTITUTION.md` §4). Heavy, and you author it. |
| R2. The C2 signing | Too late: C2 is signed after D-19's results (`<<D19>>` markers, draft order). |
| R3. An owner decision on the accepted preregistration | **Not established.** The precedents differ: your acceptance record filled values the text reserved for acceptance and pinned the hash; the reading decisions interpreted rules already present. Neither shows authority to *add* a chain and a failure rule to an accepted preregistration (FP3-R1). Not recommended. |
| R4. A new, separately accepted D-19 preregistration | Conceivable, conditional: a replacement experiment with an explicit beacon rule and a new hash. It needs its own governance and scientific review, a decision on which development and qualification work must be repeated, and an update of the engine pin. Likely costly in time. |

**Signing, whichever route:** you author the text and make the dated, signed commit **yourself**. An AI-made commit under your account is not evidence that you authored or signed it (FP3-R4). The AI may explain and may propose wording, labelled as an AI proposal; it cannot author, merge or activate.

## 5. Also needed before G (AI work)

A pinned, tested signature-verification procedure, run on a known round, recording the chain hash, public key, scheme, genesis, period, round and signature, and the randomness, which drand's v2 relays omit and clients derive as SHA-256 of the signature ([drand-client](https://github.com/drand/drand-client/blob/master/README.md)). A successful fetch is not a verification. This goes into the H/I/M rewrite (FP3-R5).

## 6. What you decide

1. Route: R1 (amendment) or R4 (new preregistration); or ask for an independent governance opinion on R3 first.
2. Chain: `quicknet` or `default`.
3. Missing output: void within 7 days by existence, or no time limit.
