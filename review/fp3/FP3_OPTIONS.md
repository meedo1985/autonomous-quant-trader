# FP3: binding the drand chain — options for the owner

**Status: AI OPTIONS PAPER — NOT A DECISION — NOT AN AMENDMENT.** Prepared by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, for the owner. The owner decides; the AI records. Facts below were fetched on 2026-10-25 and are cited.

## 1. What FP3 is, in plain words

The held-out test's random seed is built from a public random number that nobody can know in advance: one round of a **drand** beacon, published by the League of Entropy. The preregistration (§8, `review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` line 397) says the round is "the first round of the C2 drand chain (DRAFT §2.0) whose scheduled time is at or after `T_Qn + 24h`". But the C2 draft leaves that chain blank: `<<SIGNING: chain hash, public key>>` (`s4-amendment-draft/DRAFT_WORDING.md` §2.0). A blank binds nothing, so today the seed has no defined source.

It must be fixed **before step G** (the freeze): if the chain could be picked after beacon outputs are known, the pick could steer the result (`FREEZE_HELDOUT.md` FP3; Sol FH review: "A draft placeholder does not bind the chain").

FP3 is three decisions:

1. **Which chain** (its chain hash and public key).
2. **The missing-output rule**: what happens if no verifying output for the round can be found within 7 days of its scheduled time (DRAFT §2.0's rule; FH-3 left "whether it binds D-19" to FP3).
3. **The route**: which formal owner act makes 1 and 2 binding before G.

## 2. Decision 1 — which chain

drand mainnet currently lists three chains. Each was read on 2026-10-25 from `api.drand.sh`, and the hash and public key of the first two matched on `drand.cloudflare.com`, `api2.drand.sh` and `api3.drand.sh`.

| | `quicknet` | `default` | `evmnet` |
|---|---|---|---|
| Chain hash | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` | `8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce` | `04f1e9062b8a81f848fded9c12306733282b2727ecced50032187751166ec8c3` |
| Public key | `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a` | `868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31` | `07e1d1d335df83fa98462005690372c643340060d205306a9aa8106b6bd0b3820557ec32c2ad488e4d4f6008f89a346f18492092ccc0d594610de2732c8b808f0095685ae3a85ba243747b1b2f426049010f6b73a0cf1d389351d5aaaa1047f6297d3a4f9749b33eb2d904c9d9ebf17224150ddd7abd7567a9bec6c74480ee0b` (not cross-checked on other relays) |
| Round every | 3 s | 30 s | 3 s |
| Running since (genesis) | 2023-08-23 (1692803367) | 2020-07-22 (1595431050) | 2024-09-28 (1727521075) |
| Scheme | `bls-unchained-g1-rfc9380` | `pedersen-bls-chained` | `bls-bn254-unchained-on-g1` |
| One round verifiable alone | yes (unchained) | needs the previous round's signature too | yes |
| drand's own guidance | recommended for new applications ([quicknet is live](https://docs.drand.love/blog/2023/10/16/quicknet-is-live)) | the original chain | built for Ethereum contracts |

Notes:
- drand has retired a chain before (`fastnet`, 2023, replaced by `quicknet`). No retirement notice for `default` or `quicknet` was found in drand's blog posts for 2024-2026 (searched 2026-10-25). The one 2025 postmortem (v2.0, March 2025) was a fixed software vulnerability, not an outage.
- The C2 draft asks for "one drand League of Entropy mainnet chain". Whatever is chosen here must also be the C2 chain later, because the preregistration names "the C2 drand chain". FP3 therefore pre-binds the C2 beacon line.
- The engine does not check the signature (HO-4). The sheet's step K checks it on the laptop; the tool for that is chosen in the step H/I/M rewrite (both schemes are supported by drand's own clients).

**AI recommendation (yours to accept or not): `quicknet`.** It is drand's recommended chain for new uses, each round verifies on its own with only the public key (simpler, fewer ways to get it wrong), and it is newer than the chain drand retired. `default` is a sound alternative if you prefer the longest record (since 2020). `evmnet` has no advantage here.

## 3. Decision 2 — the missing-output rule

| Option | Meaning |
|---|---|
| **(a) Apply DRAFT §2.0's rule (AI recommendation)** | If no output for the round whose signature verifies against the fixed public key is retrieved within 7 days of its scheduled time, attempt 1 is **void** before any held-out evaluation: it is found before the run starts, so the namespace is not burned, and the same object may be posted again with key `A_Q2` (sheet "What can end it early"; §4 failure boundary). There is never a fallback chain or source. |
| (b) No time limit | Wait for the output however long it takes. Leaves the attempt open indefinitely; no other source is allowed either way. |

Why (a): it matches what the C2 draft already says for C2, gives a clear end, and voids rather than fails because nothing held-out has been seen.

## 4. Decision 3 — the route that makes it binding before G

| Route | Assessment |
|---|---|
| **R1. Constitution §4 amendment** | Certainly formal, but §4 requires a version bump, cycle termination and pre-new-cycle activation (`docs/RESEARCH_CONSTITUTION.md` §4). Heavy and slow for one value; it would also have to be authored and signed by you. |
| **R2. The C2 signing** | Too late: the C2 amendment waits for D-19's own results (`<<D19>>` markers), and D-19 needs the chain before G. (Negotiation record d2ea15a, CY-2.) |
| **R3. An owner binding decision on the accepted preregistration (AI recommendation, subject to review)** | You decide which chain "the C2 drand chain" in prereg §8 is, plus the missing-output rule, in a signed and dated owner decision committed before step G, which also states that the C2 signing must carry the same chain hash and public key. Precedent: the preregistration's `<<ACCEPTANCE>>` values were filled by your acceptance record (`review/d19-engine/ACCEPTANCE_RECORD.md`), and readings of the accepted text were fixed by your decisions (e.g. `OWNER_DECISION_GAP1_CUTOFF_READING.md`). It changes no frozen file and no preregistration text or hash. **Open question:** whether this counts as "the formal process" FP3 requires. The sheet names "Constitution amendment process or C2 signing". An independent review must answer this before you rely on R3. If the review rejects R3, R1 is what remains. |

## 5. What happens next

1. Independent review of this paper (facts and route validity), record committed.
2. You answer three questions (chain, rule, route), in your own words or by choosing options. If R3 stands, the AI records your answers in an owner decision file. How that decision must be signed and dated to count (an AI-made commit under your account, or a commit you make yourself) is part of the review question; the AI does not decide it.
3. The sheet's FP3 row is updated to point to that decision; steps K and L use its chain hash and public key.
