# O-6a: the public channel for the C2 declaration-hash post (specification, revision 5)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices to the agent on 2026-10-03 and again on 2026-10-04. Every choice here is therefore an `[AI default]`. The channel itself stays `<<OWNER O-6a>>` until the owner answers §8.
**Scope:** the requirements in `../reg-o8-proposal/PROPOSAL.md` §4 (SR3-2, FR4-2) and DRAFT_WORDING §2.0. It changes no decided row and no frozen file.

**History:**
- Rev 1 `8f0405f`: Fable OF1 READY WITH FIXES (`cc136ba`); Sol OS1 NOT READY (`a7dcd6b`).
- Rev 2 `9ffcb4a`: Fable OF2 READY WITH FIXES (`0cc0f8e`); Sol OS2 NOT READY (`bb10c3a`).
- Rev 3 `89ecead`: Fable OF3 NOT READY (`f7d32ff`); Sol OS3 READY WITH FIXES (`784516d`).
- Rev 4 `c8c0721`: Fable OF4 READY WITH FIXES (`aed61ba`); Sol narrow re-check stopped by the system for low memory, with no output.
- Rev 5 applies OF4-1 and OF4-2 as the reviewer proposed (two wording additions, §3 and §5, plus §8). It is not yet re-checked.

## 1. What the channel must do (DRAFT_WORDING §2.0)

The channel is one identity, named in the protocol and dedicated to C2. It must:
1. authenticate its poster;
2. be append-only;
3. carry a third-party timestamp;
4. be captured by an independent archive at posting time.

The declaration cannot choose the channel.

**What any channel can and cannot do (OS1-2).** A channel fixes the **one admissible commitment**: the declaration presented must match it, and it is fixed before the beacon is known. No channel can detect commitments made elsewhere: privately, under another key, or to another person. Such commitments can never be presented, so they cannot be used to choose a declaration after the beacon. The remaining abort route is disclosed in DRAFT §2.0 (FA5-3). A declarer who dislikes the computed outcome can abort, at the cost of one increment of `m`.

## 2. Choice: one dedicated Bitcoin key and one bound coin [AI default]

The post is a confirmed Bitcoin mainnet transaction that spends one bound coin of a dedicated key. Sigstore Rekor is rejected (PROPOSAL §4). The trusted-third-party option is §8 (B).

## 3. Definitions

- **Key `K` and address `A`.** `K` is one secp256k1 key, generated offline by the owner for C2 only. `A` is its P2WPKH address. Only `A` and the public key become public. `K` never enters the repository, a log, a prompt or an artifact.
- **Bound coin `F`.** Before signing, the owner pays one amount to `A`, and the payment confirms. Its outpoint `txid:vout`, amount and block height are fixed in the protocol at signing: `<<SIGNING: address A, outpoint F, amount, height>>`.
- **Check at signing (OF1-3).** At signing it is checked and recorded that `A` has never been spent from and holds only `F`.
- **Post deadline height `D` (OF3-2).** `D` is a block height fixed in the protocol at signing (`<<SIGNING: D>>`). The owner chooses it to fall roughly when he plans to post, plus 4,320 blocks, which is about 30 days. `D` must be above the signing height, and block `D` must be expected before C2's evaluation starts. Both are checked and recorded at signing (OF4-2).
- **Post.** A post is any main-chain transaction, confirmed after signing and before C2 ends, that spends any output locked to `A`. That includes `F`, and any payment someone else sends to `A`. An inbound payment is not a post.
- **Well-formed post (OF1-5).** A well-formed post:
  - spends `F`;
  - has exactly one OP_RETURN output, with value 0;
  - that output's scriptPubKey is exactly `6a 25 41 51 54 43 32` followed by the 32-byte `declaration_sha256`. That is 39 bytes: `OP_RETURN`, a push of 37 bytes, ASCII `AQTC2`, then the hash.

  Matching uses only this script. No other output may be an OP_RETURN.

  This replaces the text message in DRAFT §2.0, which was 90 bytes with a 93-byte script, over the pre-v30 relay default (OF1-8).
- **Order and first-post rule.** Posts are ordered by block height, then by position in the block. The first post governs. The cycle is invalidated if:
  - the first post is not well-formed;
  - its hash does not match the declaration presented;
  - any later post appears before C2 ends.

## 4. Finding every post, and the record

- **Own node (OF1-6, OS1-5, OF2-4, OS2-4).** The verifier runs a fully validating Bitcoin Core node, version 30.0 or later. It runs with `-blockfilterindex=1` and is not pruned below `F`'s height. It lists every spend from `A` in two steps:
  - `scanblocks` over descriptor `addr(A)` with `filter_false_positives=true`, from `F`'s height to the current tip;
  - then `getdescriptoractivity` over the blocks found, with `include_mempool=false`, to remove the filters' false positives. BIP158 filters have no false negatives.
- **Explorers (OF1-7).** The named explorers are `mempool.space` and `blockstream.info`. `blockchair.com` is the substitute if one is unavailable. The explorers list the address's spends independently.
  - The verifier's own node governs.
  - Any disagreement is recorded, and it blocks verification until it is resolved.
- **Record (Constitution §27).** For each post, the record holds:
  - the raw transaction;
  - the transaction of the previous output it spends, with that output's script and value;
  - the inclusion block hash and height, and the Merkle path;
  - the acceptance tip.

  For the qualifying capture (§5), the record also holds:
  - its URI and Wayback timestamp;
  - the original body bytes, fetched with the Wayback `id_` modifier;
  - the response headers and status, including `x-archive-src` and `x-archive-orig-date` (OF3-3);
  - the SHA-256 of the body (OS2-2).

  At the freeze point, the record also holds the CDX evidence (OS3-1), for each of the two URLs:
  - the exact CDX query URI (exact URL match, with no collapsing, and every page);
  - the complete raw response bytes;
  - the response headers and status;
  - the retrieval time;
  - the SHA-256 of the response.

  It also holds the time at which the verifier's node first saw the post accepted.

## 5. Acceptance, `T` and the beacon round

- **Acceptance (OS1-3, OF1-2).** A post's confirmations are `tip_height − inclusion_height + 1`. A post is **accepted** at 6 confirmations.
  - The **acceptance tip** is the block at height `h + 5`, where `h` is the inclusion height.
  - Before acceptance, the posts are re-read from the current main chain.
- **What is frozen at acceptance (OF1-1):**
  - the inclusion block hash;
  - the order of posts up to the accepted post;
  - the acceptance-tip block hash.

  Any later change to any of these invalidates the cycle.
- **Qualifying capture (OS2-1, OF2-1).** A qualifying capture is an Internet Archive capture of one of these URLs:
  - `https://mempool.space/api/block-height/<h+5>`;
  - `https://blockstream.info/api/block-height/<h+5>`.

  Its original body, fetched with `id_`, must equal the frozen acceptance-tip block hash. These endpoints return the hash of the block at that height as plain text (mempool.space REST API documentation).
  - That block did not exist before the chain reached 6 confirmations, so **no qualifying capture can predate the frozen 6-confirmation chain state**, whoever made it. It may predate the moment the verifier's own node saw that state; that does not weaken anything (OS3-2).
  - Rendered or replayed pages never count.
  - The owner requests one Save Page Now capture of each URL once the post is accepted. Anyone else's qualifying capture counts too.
- **`T` (OS1-1, OF2-2, OF3-1, OF3-3).**
  - **Definition.** `T` is the 14-digit UTC CDX timestamp of the earliest qualifying capture of the two URLs. The capture's CDX row must:
    - match the URL exactly;
    - show archived status `200`.

    Its `id_` fetch must be bound to that exact row: the same original URL, the same timestamp and the same digest. A replay redirect, or a fetch that resolves to any other timestamp, does not count (OS3-1).
  - **Freeze point.** The index is read once, at the **freeze point**: 7 days after the verifier's node first saw the post accepted. The read is recorded as §4 sets out. `T` and the round are then frozen.
  - **An earlier capture invalidates (OF3-1).** If anyone, at any time before C2's evaluation is final, shows a qualifying capture with a CDX timestamp earlier than the recorded `T`, and the earlier timestamp gives a different round, the cycle is invalidated. It then costs one increment of `m`, as the FA5-3 abort does.
    - So reporting a later capture as the earliest, after the beacons are public, can only invalidate the cycle. It never chooses a round.
    - The rule applies equally to an honest late addition to the index, for example from a partner archive.
  - **A capture that disappears never changes `T`.** The retained record governs.
- **No capture (OS2-2, OF2-3).** If no qualifying capture is listed at the freeze point, the cycle is invalidated before any evaluation, as in §2.0 `failure`. An outage of the Internet Archive lasting 7 days or more therefore costs one increment of `m`, with no fault by anyone.
- **Later unavailability (OS2-2).** If the archive later cannot serve a recorded capture, the retained record governs. Anyone can check its bytes against the chain.
- **Round.** The round is the first round of the fixed drand chain whose scheduled time is at least `T + 24h`, as in DRAFT §2.0.
  - Every qualifying capture is made in real time after acceptance. The round that follows it is unpublished at that time.
  - The declarer cannot remove other parties' earlier captures. Making later captures does not change the earliest one.
  - **Trust assumption (OF4-1).** This rests on the Internet Archive not removing captures at the declarer's request before the freeze read. Procedurally, the owner requests no removal, and makes exactly one Save Page Now request per URL. Closing the gap entirely would need a freeze read within 24 hours of the first capture, which would give up the 7-day tolerance for archive outages; it is not taken [AI default].
  - So no capture timing gives a choice of beacon outcome.

## 6. Relay policy and node commands (checked 2026-10-04)

The release notes for **Bitcoin Core 30.0**, released 2025-10-10, are at <https://bitcoincore.org/en/releases/30.0/>. They say:
- "`-datacarriersize` is increased to 100,000 by default, which effectively uncaps the limit";
- it "can be overridden with `-datacarriersize=83` to revert to the limit enforced in previous versions";
- "Multiple data carrier (OP_RETURN) outputs in a transaction are now permitted for relay and mining";
- "The `-datacarriersize` limit applies to the aggregate size of the scriptPubKeys across all such outputs in a transaction, not including the scriptPubKey size itself."

**The post fits.** Its script is 39 bytes, which fits both the old 83-byte default and the new one.

**Node commands.** The scan uses two Bitcoin Core 30.0 commands:
- `getdescriptoractivity`, which "Get[s] spend and receive activity associated with a set of descriptors for a set of blocks" (<https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/getdescriptoractivity/>);
- `scanblocks`, which requires the block filter index (<https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/scanblocks/>).

## 7. Funding, fees, deadline, custody and privacy

- **Two transactions (OS1-6).**
  - The funding payment creates `F`.
  - The post spends `F`. Its OP_RETURN output has value 0, and its change goes to an address other than `A`.
  - The cost is two network fees, plus any withdrawal fee charged by the source of the funds. This is the owner's real money, separate from L-01 (the trading capital), which stays 0. Fees vary with network demand; no figure is promised here.
- **Fees and deadline (OS2-3).**
  - The post is broadcast at a fee rate at least the node's `estimatesmartfee` for 6 blocks. This is procedural: it cannot be verified publicly (OF3-2).
  - Until the deadline, the post may be replaced (RBF) only by a transaction carrying the identical OP_RETURN script.
  - **Deadline (OF3-2).** The deadline is public: the post must be included in a block at height at most `D` (§3). If no post is included by then, the cycle is invalidated. The owner then spends `F` back to himself with a higher fee [AI default]. That spend is itself a post, which closes the record.
  - A replacement with a different payload is forbidden, but it cannot be detected unless it confirms. If it confirms, it is the first post, its hash does not match, and the cycle is invalidated. Unconfirmed variants all resolve before acceptance, and so before `T` and the beacon.
- **Custody (OF1-4).**
  - `K` is backed up offline and never shared until the post is accepted.
  - If `K` is lost before then, C2 cannot be declared, and a new channel needs a new amendment.
  - If `K` is stolen before then, the thief can post first and invalidate C2.
  - After acceptance, the owner destroys `K` [AI default]. This is a procedural step: it cannot be proven publicly. Once `K` is destroyed, no later spend from `A` is possible.
- **Privacy (OS1-6).** The post is public and permanent. It shows the hash, `A` and its public key, the amounts, the fee and the change address.
  - Funding from an exchange account can link `A` to the owner's identity there.
  - Anyone who later sees the declaration can link the post to this project.
- **No automation.** The app, the repository and the AI never hold `K` or sign with it. The owner posts with a wallet of his choice. The repository only verifies, from public data.

## 8. Owner question (to be asked after review)

**The question.** Where should the one public fingerprint of the C2 declaration be published?

**What the fingerprint is.** It is the declaration's hash. It does not disclose the declaration's contents by itself. It is published before the random draw, so that the declaration cannot be swapped after the draw is known.

**What both options share.** Both fix which declaration is the official one. Neither can stop a copy being kept privately, but such a copy can never be used.

- **(A) One Bitcoin transaction from an address used only for this** [AI recommendation].
  - **Who can check it:** anyone with access to public Bitcoin data, plus the Internet Archive's saved copy.
  - **What you do:**
    1. Create a Bitcoin wallet key and keep it safe offline.
    2. Send a small payment to it.
    3. Send one transaction that contains the fingerprint.
    4. About an hour later, once it has 6 confirmations, ask the Internet Archive to save two given web addresses.
    5. Destroy the key.
  - **Cost:** two Bitcoin network fees, plus any withdrawal fee.
  - **Risks:**
    - A lost or stolen key, or a mistake in the transaction, cancels or blocks the cycle.
    - If the Internet Archive is unreachable for a week after the post, the cycle is cancelled.
    - If an earlier archive copy than the recorded one turns up later and changes the draw, the cycle is cancelled.
    - The design trusts the Internet Archive not to delete archive copies on request; you must never ask it to.
    - The post must be in a block by a deadline set when you sign (about 30 days after your planned posting date).
    - The address may be linkable to you, depending on where the money comes from.
    - The record is public forever.
- **(B) A trusted person named in the protocol.**
  - **Who can check it:** only that person's word and records. You email the fingerprint to them. They confirm the date it was received, confirm it was the only message, and keep it.
  - **What you do:** choose and ask the person. This route needs its own receipt-and-record procedure, written and reviewed before signing.
  - **Cost:** none.
  - **Risks:**
    - The cycle depends on that person's honesty and availability, and nobody else can check it.
    - The earlier decision on how the random draw is disclosed (O-6) must be revisited.
- **Keep blocked.** The amendment cannot be signed until this is decided.

## 9. Changes to DRAFT_WORDING §2.0 if (A) is chosen

| Key | New wording |
|---|---|
| `channel` | "the Bitcoin mainnet address, bound coin and deadline height `<<SIGNING: address A, outpoint F, amount, height, D>>`, per O-6a SPEC §3–§5" |
| `message` | "one zero-value OP_RETURN output with scriptPubKey exactly 6a25 4151544332 followed by the 32-byte declaration_sha256" |
| `first_post_rule` | "as in SPEC §3: posts are main-chain spends from `A` after signing and before C2 ends; a post is accepted at 6 confirmations, and the record frozen at acceptance governs (SPEC §5)" |
| `round` | "the first round whose scheduled time is at least T + 24h, where T is the Wayback timestamp of the earliest qualifying capture listed at the freeze point (SPEC §5)" |

`failure` gains four conditions. Each invalidates the cycle:
- no qualifying capture at the freeze point;
- a change to the frozen acceptance record;
- no post included by block height `D`;
- an earlier qualifying capture giving a different round (SPEC §5).
