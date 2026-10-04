# Sol fix-check BS4 of the D-19 preregistration §13 rev 7e at `9d811e6`: READY WITH FIXES

Date: 2026-10-04. R19-2 independent statistical fix-check, run with Codex CLI (`codex exec`, model requested `gpt-5.6-sol`, reasoning effort high), read-only. The drafter is Claude Opus 5.5. The reviewer's final report is reproduced below unchanged.

---

**Model identity:** OpenAI Codex, GPT-5 family; no finer serving-model identifier is exposed.  
**Commit reviewed:** `9d811e66aae18b757cba55b9b97402ba94bfaf28`  
**Verdict:** **READY WITH FIXES**

**Prior findings:** BF3-1, BF3-2, BS3-1, and BS3-2 are resolved. BF3-3 and BS3-3 are only partly resolved.

- **BS4-1 — MAJOR — PREREGISTRATION.md §13 item 3/6, lines 491, 570–572; ADJUDICATION_9762781.md.** The cost scenarios apply a one-test escape probability and 25-hour cost across all 104 cells, although QJ has two `U_G` tests and costs 50 hours when escaped. Also, a re-pilot limited to thin-category cells cannot replace assumptions for all cells. **Fix:** use `base + 25·E[ordinary escapes] + 50·E[QJ escapes]`, with the QJ union bounds, and either measure representative rates across all relevant strata or keep the scenarios explicitly conditional.

- **BS4-2 — MINOR — PREREGISTRATION.md history, line 23.** Rev 7e says the fixes were checked by narrow re-review before a committed review record exists, and BS4-1 remains. **Fix:** say “awaiting narrow re-review,” then cite the committed review and its actual verdict.

Owner: The runtime and demotion fixes are sound, but the server-time estimate still mishandles QJ cells and overstates what the limited re-pilot can establish.
