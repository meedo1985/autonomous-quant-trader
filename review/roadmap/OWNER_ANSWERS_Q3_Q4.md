# Owner answers to roadmap questions Q3 and Q4

Date: 2026-09-26
Given by: the repository owner, by selecting options the coding AI (Claude Opus
5.5) presented in a Claude Code session. The option texts he selected are
quoted verbatim below. The coding AI wrote this record; it adds no assessment
on his behalf.

## Q3: which partitions to download in Task 13

**Answer: exploration only.** Selected option: "Exploration only
(Recommended)": Aug 2017 to Dec 2021, which is what the merged Task 13 code
does. The confirmation and lockbox periods stay unfetched.

Effect: none on the code. `EXPLORATION_MONTHS` and the client's
`_require_exploration_month` guard already implement this answer. **Q3 is
closed.**

## Q4: who executes the network calls

**Answer: the AI may run the downloader.** The owner first selected "The AI may
run it". Because that option's own description said it "arguably conflicts
with section 15, so it would need a governance reading from you first", the AI
asked for that reading, and the owner selected "Adopt the narrow reading",
whose text was:

> "Section 15's Cycle-1 network denial does not cover the coding AI downloading
> Binance's public, credential-free exploration archives before Cycle 1
> starts." Recorded as your reading, not an amendment. The AI may then run the
> downloader, subject to this session's own permission controls.

**Q4 is closed** on that reading.

### Limits of the reading

- It is the owner's **interpretation** of section 15, not an amendment. The
  Constitution and every frozen artifact are unchanged, and the reading cannot
  override them.
- It covers only: the coding AI; Binance's public, credential-free archives
  and `exchangeInfo`; the exploration months; and the period **before Cycle 1
  starts**. It ends when Cycle 1 starts.
- It does not cover the research AI, any credential, any order endpoint,
  confirmation or lockbox data, or any other network access.
- Running the downloader remains subject to the Claude Code session's own
  permission and sandbox controls, which this record does not change.
- The previous default, that the owner runs the downloader, stays valid; the
  owner may still run it himself.
