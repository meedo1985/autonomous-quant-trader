# Owner decision: O-6a, the public channel for the C2 declaration-hash post

**Date:** 2026-10-04
**Authority:** The owner decided this in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the question and recorded the answer. Before the question was asked, the decided text went through two different-model families under R19-2.

**Fable (Claude Fable 5.1):**

| Review | Commit | Verdict |
|---|---|---|
| OF1 | `cc136ba` | READY WITH FIXES |
| OF2 | `0cc0f8e` | READY WITH FIXES |
| OF3 | `f7d32ff` | NOT READY |
| OF4 | `aed61ba` | READY WITH FIXES (rev 5 applies its fixes as proposed) |

**Sol (Codex `gpt-5.6-sol`):**

| Review | Commit | Verdict |
|---|---|---|
| OS1 | `a7dcd6b` | NOT READY |
| OS2 | `bb10c3a` | NOT READY |
| OS3 | `784516d` | READY WITH FIXES |
| OS4 | `73d744b` | **READY**, on rev 5 |

One earlier Sol attempt on rev 4 was stopped by the system for low memory and produced no output.

**Adjudications:**
- `ADJUDICATION_8F0405F.md`
- `ADJUDICATION_9FFCB4A.md`
- `ADJUDICATION_89ECEAD.md`

## Decided object

`SPEC.md` revision 5, commit `84fca9c`.

## Exchange (verbatim)

**Question:**

> "Before cycle C2's random draw, one public fingerprint of the C2 declaration is published. The fingerprint is a hash: it does not reveal what the strategies are, but it stops anyone swapping the declaration after the draw is known. Where should it be published? Both options fix which declaration is official; neither can stop a private copy being kept, but such a copy can never be used. Note: C2 cannot start until the other open items (D-19 and others) are also done, so nothing happens yet."

**Options as shown:**

- **"(A) Bitcoin post (Recommended)":**

  > "Anyone can check it from public Bitcoin data and the Internet Archive. You: make a Bitcoin key and keep it offline, send it a small payment, send one transaction with the fingerprint, have the Internet Archive save two web addresses about an hour later, then destroy the key. Cost: two Bitcoin network fees plus any withdrawal fee (your real money, separate from trading capital). Risks: a lost or stolen key, a transaction mistake, a week-long archive outage, or an earlier archive copy turning up later cancels the cycle; the address may be linkable to you; the record is public forever. Assumes the archive never deletes copies on request."

- **"(B) Trusted person":**

  > "You email the fingerprint to a person named in the protocol, who confirms the date, that it was the only message, and keeps it. Free. Only that person's word can verify it; the cycle depends on their honesty and availability. Needs its own receipt procedure written and reviewed, and the earlier decision on how the random draw is disclosed (O-6) must be revisited."

- **"Keep blocked":**

  > "Decide later. The amendment cannot be signed until this is decided."

**Answer:** **"(A) Bitcoin post (Recommended)"**

## Effect

- DRAFT_WORDING §2.0 `seed_disclosure` takes the SPEC §9 wording. The `channel` marker `<<OWNER O-6a>>` is replaced by the specification. The `<<SIGNING: ...>>` values remain: address A, outpoint F, amount, funding height, and deadline height D.
- **No money is spent and no key is made now.** The owner takes the §8 (A) steps only when C2 is declared, after the amendment is signed and active.

## Not changed by this decision

- D-19, D-11..D-13 and D-20 remain open.
- Nothing is activated.
- No frozen file and no `HUMAN_DECISION_MATRIX.md` is edited.
- No cycle, trial, data access, deployment or trading is authorized.
