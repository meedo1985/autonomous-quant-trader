# Sol focused re-check OS2 of the O-6a specification rev 2 at `9ffcb4a`: NOT READY

Date: 2026-10-04. This is an R19-2 independent re-check. The prompt was the same as Fable OF2's, with the ID prefix `OS2`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106b9-a479-7673-a9c3-01d9010b0779`. The final message is reproduced below unchanged, except that one local file link was shortened to its repository-relative form.

---

## R19-2 focused re-check

**Model:** OpenAI Codex, GPT-5 family; exact deployment identifier unavailable  
**Commit:** `9ffcb4aa032eabbf80fd00766c55bcc23d82a196`  
**Verdict:** **NOT READY**

The archive-based design is sound in principle, but rev 2 leaves one security-critical ambiguity. Capture timing alone gives the declarer no beacon-outcome choice: delaying `T` selects another still-unpublished drand round. However, the literal definition permits a capture made before six-confirmation acceptance. If acceptance takes over 24 hours, the beacon could become public while the transaction remains reorg/replacement-sensitive. The known post-outcome abort remains possible and costs one `m`.

A properly qualified static archive capture cannot predate the post’s inclusion: the archived response must itself contain the transaction ID and frozen block hash. Rev 2 does not specify that strongly enough for JavaScript-driven explorer pages.

### Earlier findings

| Finding | Status | Note |
|---|---|---|
| OF1-1 | **Partial** | Block/order freeze fixed; qualifying-capture and `T`/round freeze event remain ambiguous. |
| OF1-2 | Resolved | Exact six-confirmation formula. |
| OF1-3 | Resolved | Signing check and C2 interval defined. |
| OF1-4 | Resolved | Key destruction is specified, although procedural rather than publicly provable. |
| OF1-5 | Resolved | Exact 39-byte script and single OP_RETURN. |
| OF1-6 | **Partial** | Correct RPCs, but required node/index configuration is omitted. |
| OF1-7 | Resolved | Governing node, disagreement rule and substitute named. |
| OF1-8 | Resolved | Correct 90/93-byte counts. |
| OF1-9 | Resolved | Full release-note sentence. |
| OF1-10 | Resolved/superseded | Block time no longer determines `T`. |
| OF1-11 | Resolved | Practical Bitcoin risks are stated plainly. |
| OS1-1 | **Partial** | Independent timestamp adopted; pre-acceptance eligibility remains open. |
| OS1-2 | **Partial** | Bound outpoint works once `T` is necessarily post-acceptance. |
| OS1-3 | Resolved | Confirmation and reorganization outcomes are coherent. |
| OS1-4 | **Partial** | Archive named, but qualifying evidence and later unavailability are unspecified. |
| OS1-5 | **Partial** | Correct scan method, incomplete prerequisites. |
| OS1-6 | **Partial** | Funding/RBF/privacy improved; no terminal stuck-transaction outcome. |
| OS1-7 | Resolved | Options are substantially parallel and understandable. |

### New findings

| ID | Severity | Location | Problem, evidence and fix |
|---|---|---|---|
| **OS2-1** | **BLOCKER** | [§4–5, lines 51–75](review/governance-statistics-amendment/o6a-channel/SPEC.md) | §4 says capture “once accepted,” but §5 counts the earliest capture by anyone. A pre-acceptance capture can make the selected round public before six confirmations if blocks stall, reopening reorg/replacement choice. Require a qualifying Save Page Now capture initiated only after the recorded acceptance tip is observed; immediately freeze and record its `T`, round and receipt. Ignore all earlier captures. |
| **OS2-2** | **MAJOR** | §4–5 | Hashes of responses without retained response bytes do not preserve evidence. Internet Archive also warns that JavaScript-dependent pages may not archive their originating-host functionality. Define exact qualifying HTTP/archive content containing txid and frozen block hash; retain bytes, headers, status, capture URI and hash. If no valid capture occurs within seven days, invalidate; if the archive later cannot verify an existing capture, specify fail-closed handling rather than improvising a source. |
| **OS2-3** | **MAJOR** | §7 lines 98–101 | Fourteen-day rebroadcast is not a terminal deadline or failure rule; the post can remain pending indefinitely. Set a final confirmation deadline and explicit invalidation/block outcome, plus the permitted fee-rate/replacement procedure. |
| **OS2-4** | **MINOR** | §4 lines 43–45 | `scanblocks` requires `blockfilterindex`; descriptor activity also needs the relevant block data. Require `blockfilterindex=1` and retained/unpruned block data over the scan range. |
| **OS2-5** | **MINOR** | §8 | Plain and substantially neutral, with the recommendation visibly labelled. Replace “reveals nothing” with “does not disclose the declaration contents by itself,” avoid “anyone, permanently,” and say option B requires a separately reviewed receipt/archive procedure before signing. |

### Sources

Primary sources: [Bitcoin Core 30 release notes](https://bitcoincore.org/en/releases/30.0/), [`scanblocks`](https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/scanblocks/), [`getdescriptoractivity`](https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/getdescriptoractivity/), [Internet Archive Save Page Now](https://archivesupport.zendesk.com/hc/en-us/articles/360001513491-Save-Pages-in-the-Wayback-Machine), [Internet Archive dynamic-page limitations](https://archivesupport.zendesk.com/hc/en-us/articles/360004716091-Wayback-Machine-General-Information), [drand protocol timing](https://docs.drand.love/docs/specification/), and [drand unpredictability](https://github.com/drand/drand-docs/blob/master/docs/concepts/01-Cryptography.md).

Read-only review; no confirmation or lockbox data accessed. `git diff --check` passed; no code tests applied. No edits, commits or pushes were made. Repository governance therefore still requires this review record to be committed before it is treated as completed or cited.

The archive idea can work, but the first valid capture must be made only after six confirmations.  
Delaying that capture does not reveal the future random result; the remaining choice is only to abort afterward and pay the stated penalty.  
Keep O-6a blocked until archive evidence, outage handling and the stuck-transaction outcome are explicit.
