# O-6a: the public channel for the C2 declaration-hash post (specification, revision 2)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices to the agent on 2026-10-03 and again on 2026-10-04, so every choice below is an `[AI default]`. The channel itself stays `<<OWNER O-6a>>` until the owner answers §8.
**Scope:** the requirements in `../reg-o8-proposal/PROPOSAL.md` §4 (SR3-2, FR4-2) and DRAFT_WORDING §2.0. It changes no decided row and no frozen file.
**History:** rev 1 `8f0405f` was reviewed by Fable OF1 (READY WITH FIXES, `cc136ba`) and Sol OS1 (NOT READY, `a7dcd6b`). Rev 2 applies `ADJUDICATION_8F0405F.md`; it has not yet been re-reviewed.

## 1. What the channel must do (DRAFT_WORDING §2.0)

The channel must be one identity, named in the protocol and dedicated to C2. That identity must:
1. authenticate its poster;
2. be append-only;
3. carry a third-party timestamp;
4. be captured by an independent archive at posting time.

The declaration cannot choose the channel.

**What any channel can and cannot do (OS1-2).** A channel fixes the **one admissible commitment**. The declaration presented must match it, and it is fixed before the beacon is known. No channel can detect commitments made elsewhere: privately, under another key, or to another person. Such commitments can never be presented, so they cannot be used to choose a declaration after the beacon. The remaining abort route is disclosed in DRAFT §2.0 (FA5-3): a declarer who dislikes the computed outcome can abort, at the cost of one increment of `m`.

## 2. Choice: one dedicated Bitcoin key and one bound coin [AI default]

The post is a confirmed Bitcoin mainnet transaction that spends one bound coin of a dedicated key. Sigstore Rekor is rejected (PROPOSAL §4). The trusted-third-party option is §8 (B).

## 3. Definitions

- **Key `K` and address `A`.** One secp256k1 key, generated offline by the owner for C2 only. `A` is its P2WPKH address. Only `A` and the public key become public. `K` never enters the repository, a log, a prompt or an artifact.
- **Bound coin `F`.** Before signing, the owner pays one amount to `A`, and that payment confirms. Its outpoint `txid:vout`, amount and block height are fixed in the protocol at signing: `<<SIGNING: address A, outpoint F, amount, height>>`.
- **Check at signing (OF1-3).** At signing it is checked and recorded that `A` has never been spent from and holds only `F`.
- **Post.** A post is any main-chain transaction, confirmed after signing and before C2 ends, that spends any output locked to `A`. That includes `F`, and any payment someone else sends to `A`. An inbound payment is not a post.
- **Well-formed post (OF1-5).** A well-formed post spends `F` and has exactly one OP_RETURN output. That output has value 0 and scriptPubKey exactly:
  - `6a 25 41 51 54 43 32` followed by the 32-byte `declaration_sha256`;
  - that is 39 bytes: `OP_RETURN`, a push of 37 bytes, ASCII `AQTC2`, then the hash.

  Matching uses only this script. No other output may be an OP_RETURN. The text message in DRAFT §2.0 is replaced: it was 90 bytes, with a 93-byte script, which is over the pre-v30 relay default (OF1-8).
- **Order and first-post rule.** Posts are ordered by block height, then by position in the block. The first post governs. The cycle is invalidated if:
  - the first post is not well-formed;
  - its hash does not match the declaration presented;
  - any later post appears before C2 ends.

## 4. Finding every post, and the archive

- **Own node (OF1-6, OS1-5).** The verifier runs a fully validating Bitcoin Core node, version 30.0 or later. It lists every spend from `A` with:
  - `scanblocks` over descriptor `addr(A)`, from `F`'s block height to the current tip;
  - `getdescriptoractivity` over the blocks it returns, as a cross-check.

  `-txindex` is not used to find posts; it indexes transactions by id only.
- **Explorers (OF1-7).** The named explorers are `mempool.space` and `blockstream.info`, with `blockchair.com` as the substitute if one is unavailable. They list the address's spends independently.
  - The verifier's own node governs.
  - Any disagreement is recorded and blocks verification until it is resolved.
- **Independent archive (OS1-4).** The transaction's page on both named explorers is captured with Internet Archive Save Page Now, once the post is accepted (§5).
- **Record (Constitution §27).** For each post the record keeps:
  - the raw transaction;
  - the transaction of the previous output it spends, with that output's script and value;
  - the inclusion block hash and height;
  - the Merkle path;
  - the acceptance tip;
  - the capture URLs, their capture times, and SHA-256 hashes of the raw responses.

## 5. Acceptance, `T` and the beacon round

- **Confirmations (OS1-3, OF1-2).** A post's confirmations are `tip_height − inclusion_height + 1`. A post is **accepted** at 6 confirmations.
- **Before acceptance,** the posts are re-read from the current main chain, so a reorganization simply changes what is read.
- **At acceptance, these are frozen (OF1-1):**
  - the inclusion block hash;
  - the order of posts up to the accepted one;
  - the acceptance tip.
- **After acceptance,** any change to the inclusion block or that order invalidates the cycle. `T` is never recomputed.
- **`T` (OS1-1).** `T` is the earliest Internet Archive capture time, on either named explorer, of a page that shows the accepted post in its frozen inclusion block (§4). Whoever made the capture, it counts.
  - An independent party sets that wall-clock time, and the post demonstrably existed then.
  - Block timestamps are recorded, but they do not set the round: Bitcoin bounds them from above only, with no wall-clock lower bound against a miner.
  - If no capture exists within 7 days of acceptance, the cycle is invalidated before any evaluation, as in §2.0 `failure`.
- **Round.** The round is the first round of the fixed drand chain whose scheduled time is at least `T + 24h`, as in DRAFT §2.0.
  - That round is unpublished at `T`, and the post exists by `T`.
  - Delaying the capture only moves the round later, into a future that is equally unknown. It gives no choice of outcome.

## 6. Relay policy (checked 2026-10-04)

**Bitcoin Core 30.0** was released on 2025-10-10. Its release notes are at <https://bitcoincore.org/en/releases/30.0/>. They say:
- "`-datacarriersize` is increased to 100,000 by default, which effectively uncaps the limit";
- it "can be overridden with `-datacarriersize=83` to revert to the limit enforced in previous versions";
- "Multiple data carrier (OP_RETURN) outputs in a transaction are now permitted for relay and mining";
- "The `-datacarriersize` limit applies to the aggregate size of the scriptPubKeys across all such outputs in a transaction, not including the scriptPubKey size itself."

The post's 39-byte script fits the old 83-byte default and the new one.

The scan uses two Bitcoin Core 30.0 commands:
- `getdescriptoractivity`, which "Get[s] spend and receive activity associated with a set of descriptors for a set of blocks" (<https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/getdescriptoractivity/>);
- `scanblocks` (<https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/scanblocks/>).

## 7. Funding, fees, custody and privacy

- **Two transactions (OS1-6).** The owner pays for two transactions:
  - the funding payment that creates `F`;
  - the post, which spends `F`. Its OP_RETURN output has value 0, and its change goes to an address other than `A`.

  This costs two network fees, plus any withdrawal fee charged by the source of the funds. This is the owner's real money. It is separate from L-01, the trading capital, which stays 0. Fees vary with network demand, and no figure is promised here.
- **Fee bumps.**
  - A post that is slow to confirm may be replaced (RBF) only by a transaction carrying the **identical** OP_RETURN script.
  - If it has not confirmed 14 days after first broadcast, the owner may broadcast it again with the same script [AI default].
  - A replacement with a different payload is forbidden, but it cannot be detected unless it confirms. If it confirms, it is the first post, its hash will not match, and the cycle is invalidated. Unconfirmed variants all resolve before `T`, so before the beacon is known.
- **Custody (OF1-4).**
  - `K` is backed up offline and never shared until the post is accepted.
  - If `K` is lost before then, C2 cannot be declared, and a new channel needs a new amendment.
  - If `K` is stolen before then, the thief can post first and invalidate C2.
  - After acceptance, the owner **destroys `K`** [AI default]. No later spend is then possible, which closes the griefing route through payments others send to `A`.
- **Privacy (OS1-6).** The post is public and permanent. It reveals:
  - the hash;
  - `A` and its public key;
  - the amounts, the fee, and the change address.

  Funding from an exchange account can link `A` to the owner's identity there. Anyone who later sees the declaration can link the post to this project.
- **No automation.** The app, the repository and the AI never hold `K` or sign with it. The owner posts with a wallet of his choice. The repository only verifies the post, from public data.

## 8. Owner question (to be asked after review)

Where should the one public fingerprint of the C2 declaration be published? The fingerprint is the declaration's hash, and it reveals nothing about the strategies. It is published before the random draw, so that the declaration cannot be swapped after the draw is known. Both options fix which declaration is the official one. Neither can stop a copy being kept privately; such a copy can just never be used.

- **(A) One Bitcoin transaction from an address used only for this** [AI recommendation].
  - **Who can check it:** anyone, permanently, from public data.
  - **What you do:** create a Bitcoin wallet key and keep it safe offline; send a small payment to it; then send one transaction containing the fingerprint.
  - **Cost:** two Bitcoin network fees, plus any withdrawal fee.
  - **Risks:** a lost or stolen key, or a mistake in the transaction, cancels or blocks the cycle. The address may be linkable to you, depending on where the money comes from. The record is public forever.
- **(B) A trusted person named in the protocol.**
  - **Who can check it:** only that person's word and records. You email the fingerprint to that person, who confirms the date received, says it was the only message, and keeps it.
  - **What you do:** choose and ask the person.
  - **Cost:** none.
  - **Risks:** the cycle depends on that person's honesty and availability, and nobody else can check it. The earlier decision on how the random draw is disclosed (O-6) must be revisited.
- **Keep blocked.** The amendment cannot be signed until this is decided.

## 9. Changes to DRAFT_WORDING §2.0 if (A) is chosen

- `channel`: "the Bitcoin mainnet address and bound coin `<<SIGNING: address A, outpoint F, amount, height>>`, per O-6a SPEC §3–§5"
- `message`: "one zero-value OP_RETURN output with scriptPubKey exactly 6a25 4151544332 followed by the 32-byte declaration_sha256"
- `first_post_rule`: as in SPEC §3: posts are main-chain spends from `A` after signing and before C2 ends; a post is accepted at 6 confirmations, and the frozen record at acceptance governs (§5)
- `round`: "the first round whose scheduled time is at least T + 24h, where T is the earliest independent archive capture time of the accepted post (SPEC §5)"
- `failure` gains: "no archive capture within 7 days of acceptance, or a change to the accepted post's block, invalidates the cycle"
