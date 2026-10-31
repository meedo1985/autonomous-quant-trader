# Codex Sol re-check of D-20 lockbox revision 4 (df28ee6)

Prompt: `REREVIEW3_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a17a05-78ad-7cb1-835a-0e663146ee8d`, 106,905 tokens. The report says the caller must verify the runtime variant; the CLI header is the verified source.

Verdict: **FIX** (2 BLOCKER, 1 NON-BLOCKING). Findings D20LR4-S-1 .. S-3. Dispositions: S-1, S-2, S-4, S-5, S-6 ACCEPT; S-3 ACCEPT WITH NOTES; Astra's FIX rows (S-4, A-1, A-2) and Sol's A-4 FIX repaired. E4-3 confirmed as unapplied repair (= D20LR4-S-1); E4-1, E4-2 = D20LR4-S-3.

## Report (verbatim)

## Verdict: FIX

Revision 4 is an **inactive binding proposal**, not an accepted C2 rule. Its statistical-binding status remains **REVISION_REQUIRED**. Most rev 3 repairs hold, but two release and cap guards still need explicit repair before this package goes to the owner. This was a read-only review; the worktree is clean. I use `D20LR4-S-*` for this Sol-lane report; the caller must verify the runtime model variant from the CLI header.

### Rev 3 dispositions

| Prior finding | Re-check | Evidence |
|---|---|---|
| S-1; Astra A-4 FIX | **ACCEPT** | Publisher `state` now has a uniform pre-deadline shape and exposes neither finished-record presence nor a commitment. |
| S-2 | **ACCEPT** | Admission now binds status (a), the matching pre-read check and startup record; an existing entry’s default is verified before return. |
| S-3 | **ACCEPT WITH NOTES** | The insert and signer guards now include the six-hour lower bound, integer day index and uniqueness. The PASS attestation requirement remains incomplete; see S-1 below. |
| S-4 | **ACCEPT** | A6 requires a one-hour series interval. |
| S-5 | **ACCEPT** | The hashes are typed, byte-exact examples; `k` is honestly labelled illustrative. |
| S-6 | **ACCEPT** | Q2(i) now says cost is paid at each leg’s first permitted entry. |

The other reviewer’s L4, seed-policy and cross-family cooldown FIX rows are also substantively repaired. `AND3(false, null) = false`; the two ETH rows demonstrate the distinct PERFORMANCE and TECHNICAL outcomes. Seed validity depends on the signed policy and derivation, so a legitimate numeric zero is accepted.

### Findings

| ID | Severity | Place, failure scenario, minimal repair |
|---|---|---|
| **D20LR4-S-1** | **BLOCKER** | [Rev 4 B1, B3a and B4.3](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:90>). `insert_release` refuses an attestation in the wrong circumstances, but does not explicitly refuse **null** for a PASS with `R_j < C`. Such a row would publish PASS without the certificate that [D-12 P-7](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV7.md:86>) requires; signer refusal must instead cause a missed release. Restore rev 3’s “attestation non-null iff PASS and `R_j < C`” and require the store to enforce both directions at insert, including certificate validation. This confirms E4-3 as an unapplied repair, rather than an established rev 4 guard. |
| **D20LR4-S-2** | **BLOCKER** | [Rev 4 B4.1 steps 3–5 and read gate](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:113>). At `t_s = C`, a failed check or exhausted budget reaches an index-writing rejection **before** the cap guard. A worker holding an earlier pre-read entry can also pass the three-condition bar gate after C. Both permit processing after [P-6’s day-255 stop](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV7.md:98>). Check the cap before any new admission or rejection write, while permitting read-only reconciliation of an existing entry; stop new bar service and worker completion at C. Add boundary tests for each path. D20L-50 is therefore only partially repaired. |
| **D20LR4-S-3** | **NON-BLOCKING** | [Rev 4 §0 and §4](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:11>). The self-check counts five notes where §1a has eight note rows (E4-1). The interval explanation should cite `event_contract.py` 151–156 and say its **default** volatility path rejects a two-hour series with `CostModelError`; supplied `sigma_bps` bypasses that path (E4-2). Correct both descriptions without changing the A6 guard. |

### Other checks

D20L-37–49 are real and appropriately repaired or routed, subject to S-1. In particular, **D20L-46** is repaired by a separate `L_store`: `append_entry` retains its own sidecar lock, while `read_entries` has none. Holding `L_store` through the append fsync and read-gate check closes the identified interleaving without nesting the same lock. The default-before-entry, orphan, torn-entry and lost-acknowledgement crash cases remain coherent. **D20L-48** is a real scheduling blocker under retained R-14: its wording covers the confirmation end-price adapter as well as the seed change. **D20L-36** is correctly reclassified: a result first published after C retains PASS/FAIL, while the nominee’s status is `U_ops` under P-6.

The disclosure sweep found no remaining FAIL-kind or finish-time discriminator in the pre-read entry, release commitment, no-read entry, publisher `state`, or `DEFERRED` answer. The cooldown `earliest` is derivable from the other family’s public `r0`; `CAP_REACHED` should become the uniform new-admission answer at C after S-2’s repair. Pre-read rejection reasons remain the separately permitted Q2b disclosure.

Using the actual `calibration/seeds.py` `cj` function with `python -I -B`, the displayed PASS fixture reproduces **1,053 bytes**, byte-for-byte, and SHA-256 `d64d228b84a1aaf6015a6860af7f69f2315cc77865e0afad4547822ab54ba520`. Its four label hashes and both added negative float encodings check out. This verifies serialization, not the illustrative `k = 1275` without its replicate vector.

A1b’s two policy branches, recorded-policy evidence rule and proposed Annex C wording are consistent. Q5 and Q2(ii) both require the reviewed `screen.py` bytes in the build selected **before step G**; [G0/G currently name a fixed commit](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/deploy/calibration/FREEZE_HELDOUT.md:27>), and [`qobj._reviewed`](<D:/PMP-programs-for-sharawi/aqt-freeze-sheet/calibration/qobj.py:199>) checks the file hash and committed review record. “Unavailable after freeze” is correctly limited to the retained R-14 route. I make no finding about this branch’s absence of the later main-branch freeze-review file.

Q2, Q3 and Q5 give a non-statistician understandable choices and costs. Q1 remains a large bundled adoption decision, and Q4 is mainly a code-placement decision; both would benefit from a short owner-facing summary of what accepting each changes. The derivable `DEFERRED {earliest}` field could be dropped, but the durable default, attempt number, audit bindings and shared lock have concrete purposes. No implementation, lint, type or import suite applies to this read-only document re-check; no files were written.