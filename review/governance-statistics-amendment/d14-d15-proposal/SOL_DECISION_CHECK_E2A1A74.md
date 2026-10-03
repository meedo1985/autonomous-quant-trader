# Sol High check of the owner's D-14/D-15/N-3/N-4 answers (`e2a1a74`, rev7 `411e1af`) — INCONSISTENT

Date: 2026-10-03. The owner asked for this check ("let the agent check the answers"). This is the OpenAI-family check for R19-2. It ran in parallel with the Fable check, without access to it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10323-5598-7770-b487-df4e8e7290d9`;
  tokens used 138,933; exit 0. (The reviewer's self-report names only "GPT-5 family". The CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_DECISION_CHECK.md` (committed `5df9c93`) with `{{PREFIX}}` = `SC7`
  (substituted file SHA-256 `aa6c62b62bb9841b60e7e6bb4cfc78d04bdb495d1917c2f166ece57a53e0b0f5`).
- The reviewer's final message follows verbatim:

---

Model: **Codex, OpenAI GPT-5 family**; exact runtime model ID is not exposed to me.  
Commits checked: **`411e1af`** (revision 7), **`e2a1a74`** (owner record), **`4c8648f`** and its FN6/SN6 context; earlier owner records were checked at HEAD **`5df9c93`**.  
Verdict: **INCONSISTENT**.

Revision 7 itself resolves FN6-1..FN6-8 and SN6-1..SN6-6 textually, and I found no new technical defect in its selected options. The inconsistency is between revision 7, the questions actually shown to the owner, and what the Effect section records as decided.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| **SC7-1** | **BLOCKER** | `OWNER_DECISION_D14_D15.md:27–34`; `PROPOSAL.md:132–146` | Q2b told the owner that under A his recorded rule “skips this check.” | Revision 7 says that outcome is conditional: fixed 10% sizing might not be registrable; without an entry signal the rule gets `N/A`, but with an entry signal G-11 runs and tests that signal. The Effect at lines 138–140 correctly restores the condition, contradicting the verbatim question. | Re-present Q2b with both conditional mappings and the unresolved registration issue; ask the owner to confirm or reconsider A. |
| **SC7-2** | **BLOCKER** | `OWNER_DECISION_D14_D15.md:77`; `PROPOSAL.md:308–319` | Q11 was summarized only as “each input’s value as of one clock hour earlier.” | The distinguishing consequence added to resolve SN6-4 was omitted: a daily input emitted at 00:00 receives no extra delay when read at 12:00, but receives a prior-day value at 00:00. The Effect at lines 119–120 records that phase dependence as accepted although it was not disclosed. | Re-present Q11 with the hourly-versus-immediately-preceding-emission alternatives and the daily-input example. |
| **SC7-3** | **BLOCKER** | `OWNER_DECISION_D14_D15.md:65–87`; `PROPOSAL.md:89–98, 150–158, 190–198, 342–346, 353–362` | The 18-item “Accept all” question listed recommendations but not the material alternatives or tradeoffs that revision 7 asks the owner to decide. | Omitted items include: `g11_class` and `CLASS_MISMATCH`; volatility timing can pass without directional information; the 30-day floor is an unsupported AI default that costs power; sampling is without replacement and depends on D-20; Q13 has a competing whole-ETH-at-1x reading; Q15/Q17 have baseline-ETH alternatives; and survival permits arbitrarily large degradation. | Re-present the affected items individually or in an option-complete matrix before treating “Accept all” as dispositive. |
| **SC7-4** | **BLOCKER** | `OWNER_DECISION_D14_D15.md:91–145` | The Effect accurately summarizes revision 7’s recommended package, but it records more than the verbatim answers establish. | In particular, lines 99–100 record the undeclared `g11_class` mechanism; lines 119–120 record Q11 phase behavior; and lines 136–144 call undisclosed consequences “accepted.” Lines 10–11 also say the owner added N-3, although the verbatim N-3 prompt merely labels it and never says that answering creates a new row; Q20 explicitly did so for N-4. | Relabel the excess material as “proposal consequences not yet explicitly confirmed,” then obtain explicit owner confirmation. |
| **SC7-5** | **NON-BLOCKING** | `OWNER_DECISION_D14_D15.md:53–59`; `PROPOSAL.md:274–290` | Q10 identifies fill time as frozen but does not state all consequences of the recommended amendment. | Revision 7 says decision-time anchoring amends four frozen clauses, permits an increase 23 hours after the actual fill, and makes the 24-hour clause inert for daily decisions. The Effect records the inertness. | Include those consequences when Q10 is re-presented; the timing arithmetic itself is correct. |
| **SC7-6** | **NON-BLOCKING** | `OWNER_DECISION_D14_D15.md:4–6, 18–20` | The provenance introduction says seven revisions were reviewed by two families. | The same record correctly states that revision 7 was applied without a further check. FN1–FN6 and SN1–SN6 constitute six checked rounds, not a check of revision 7. | Correct the provenance wording without changing any owner answer. |
| **SC7-7** | **NON-BLOCKING** | Revision 7 throughout; earlier owner records | The selected options were checked for internal and historical coherence. | They remain compatible with D-01..D-10, N-1/N-2, D-18 and B-1..B-7: E-IMPROV remains the filter estimand, PBO remains E-DIFF, the 476/500 convention matches N-2, filters do not replace the DSR error control, and B-7 supplies the D-19 `T_min` dependency. The prompt’s “5%” is only shorthand after B-5; later eligible-cycle allowances are smaller. | No substantive reconciliation is proposed. Use the applicable B-5 allowance rather than describing every cycle as having exactly 5%. |

Independent exact checks confirmed the factual Q20 and Q10 examples: after a 0.5% loss, held exposure is `199/1999 = 9.954977…%`, and 01:00 to the next 00:00 is 23 hours. No network, confirmation data, or lockbox data was accessed. The worktree remained clean and no files were edited.

Because editing and committing were prohibited, this review is not a committed repository review record and should not be cited as complete until an authorized person records it.

### Plain-language summary

The chosen rules fit the owner’s earlier decisions.  
Revision 7 fixed every FN6/SN6 issue I checked and introduced no new technical defect I found.  
But the owner was incorrectly told that his recorded rule would always skip G-11 under option A.  
The bundled question also omitted Q11’s phase behavior and several other important tradeoffs that the Effect later calls accepted.  
The affected questions should be presented again; nothing should be activated in the meantime.