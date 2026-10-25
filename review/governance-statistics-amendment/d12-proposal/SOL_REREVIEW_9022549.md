# Codex Sol re-check of D-12 revision 2 (9022549)

Prompt: `REREVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a174ef-24f8-70f1-88bf-a34d97a2dd39`, 65,034 tokens. (The report says model metadata was unavailable inside the session; the CLI header above is the verified source.)

Verdict: **FIX**. Findings D12R2-S-1 .. S-4.

## Report (verbatim)

## Verdict: FIX

Revision 2 resolves the PASS-only schema claim and the three-field lemma. It also separates pre-read rejection from post-read failure and correctly treats the cycle-label leak as a proposed C2 exception. The disclosure and audit procedures still need repair before the owner answers Q1–Q5.

| Prior Sol finding | Re-check |
|---|---|
| S-1 | Resolved: PASS-only issuance is proposed C2 wording, not a schema claim. |
| S-2 | Partial: the index still exposes distinguishable failure paths. |
| S-3 | Partial: the no-read precedence works, but technical failure is newly treated as `LOCKBOX_FAIL`. |
| S-4 | Partial: reads are counted, but the audit option has no viable schedule. |
| S-5 | Partial: failure paths are separated, but the stated disclosure bound is too narrow. |
| S-6 | Resolved: PASS fields have a value contract and require all four gates. |

**D12R2-S-1 — HIGH.** The research-readable index contains an EXPOSED mark and scheduled time before release. A normal FAIL can have a bundle commitment, while a crash before bundle creation cannot. A pre-read rejection also exposes a reason code. These channels distinguish paths beyond the claimed “at most one extra bit per cycle”; Q2 does not ask the owner to authorize them. Define exactly when each index field becomes visible and give every released outcome an indistinguishable record shape, or explicitly put the additional disclosures to the owner. [Proposal §§3–4, 6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:61>); [Constitution §7](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72>).

**D12R2-S-2 — HIGH.** Step 6 says a crash leaving only step 2’s durable record will produce a scheduled FAIL entry, but specifies no recovery actor or transaction that guarantees that entry and its commitment. It also does not fence a late worker from signing or publishing after the deadline. The proposed publication rule therefore does not yet establish its fixed-time, PASS-with-certificate promise. [Proposal §6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:101>).

**D12R2-S-3 — HIGH.** Q4’s extra audit read is described as fitting the frozen two-evaluation limit, but that limit alone does not settle the frozen 30-day cooldown or C2’s 75-day post-nomination window. Four sequential reads spaced 30 days apart span at least 90 days. The proposal needs an explicit feasible schedule or the additional timing amendments and costs stated in Q4. [Proposal §6 and Q4](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:111>); [protocol lines 73–76](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:73>); [C2 draft §2.3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:217>).

**D12R2-S-4 — MEDIUM.** Calling every post-read technical FAIL `LOCKBOX_FAIL` is a proposed binding, not an established frozen definition. Q3’s “frozen rule wins” wording obscures that choice. State it expressly in C2 and explain that it bars a descendant even when no performance result exists. [Proposal §5 and Q3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:88>); [Constitution §7](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:85>).

The upside-exceedance record is a reasonable *proposal*, with no new gate. Its extra replicate vector and chosen upper percentile should be reconciled explicitly with D-11’s adopted sealed-artifact contents before assigning them to D-20. Q1’s FAIL-field alternative also needs a rule for unavailable values. Q5 fairly states the later-access cost.

This was read-only: no files, restricted data, or tests were touched. Exact runtime Sol/Astra model metadata is unavailable in this interface, so the `D12R2-S` attribution requires external verification. Under the repository rule, this response is not yet a committed review record.
