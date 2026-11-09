# Adjudication: Sol design review of slice 6b at 1e6e672

- Review record: `SOL_DESIGN_SLICE6B_1E6E672.md` (gpt-6-sol, high, verdict FIX).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09. The adjudication is the
  author's and approves nothing. Every finding is accepted. The table gives the direction
  design rev 2 will take and marks what needs the owner. 6b part 1 (`cc197be`: read
  contract, pre-look record) stays; rev 2 extends it.

| ID | Decision | Direction for rev 2 | Owner? |
|---|---|---|---|
| R14D6B-S-1 | Accepted | Remove every caller-trusted input that has a verifiable source. **Trial records** are the verified declaration's entries (as the lockbox's `_check_declared`), not caller records. The **attempt history and look records** come from the hash-chained attempt ledger (`aqt.core.ledger.verify_ledger`), read by the module. The **ledger head** must be anchored by a governing record the module cannot forge; that anchor's source is an owner/store binding. **Manifest hash, `last_seen`, embargo:** taken from the signed C2 or declaration where they exist there; the rest are store obligations, listed field by field as the lockbox's `Store` docstring does. | Anchor and store obligations: yes |
| R14D6B-S-2 | Accepted | `evaluate_trial` appends its pre-look record to the **same attempt ledger**, between the attempt's start and outcome entries. The frozen `finish_attempt` has no result field, so the record is its own entry. At the look, each completed attempt must have exactly one such entry in that span, matching its cycle, trial, attempt id, declared configuration hash, window and estimator seed. Its `d` must hash to its `d_sha256`. | No (design) |
| R14D6B-S-3 | Accepted | The read gate also returns the data manifest it served under. The module recomputes the hash of the served bars (the repository's bar-series encoding) and requires it to equal the cycle's signed or declared data-manifest hash before use. Consumer-boundary test: bars of a valid shape from another manifest are refused. Who may call the gate, and under which identity, stays open. | Manifest format and access: yes |
| R14D6B-S-4 | Accepted | Order: ledger verification, then `family_attempts`, `trial_states`, the termination and look records, `look_allowed`, then `read`. | No |
| R14D6B-S-5 | Accepted | The classifier uses the **pooled** bounds for the window's T (`reduce.pooled`), then `reduce.for_k(pool, K_f)` for the exact K and T checks, from the D-19 bounds document certified with the signed `z_crit`. The document and its T are checked before any read. | Which document: yes (with `z_crit`, A-B7) |
| R14D6B-S-6 | Accepted | Per-trial S, T and D exist only at the look: D_j needs the family's bootstrap draws. DESIGN §5.2 step 4's "S, T, D" is corrected: the pre-look record keeps `d` and `d_sha256`, and the look record keeps each column's `S_j`, `T`, `D_j`, `z_j`. Two ways to get them: (a) change the protected `dsr.evaluate` to return the columns, which needs §16 review; (b) recompute with `dsr`'s own frozen functions and the same draws, with a test that the recomputed nominee z equals `evaluate`'s z bit for bit. **Recommendation: (b).** | (a) vs (b): owner may decide; (b) is recommended |
| R14D6B-S-7 | Accepted | Two records with a stated boundary. The evaluation record covers steps 1-6 and is hashed. `source.evaluation_record_sha256` means exactly that record. Every status (a)-(d) and every sealing failure lives only in the sealing record. DESIGN §5.2 and §7.2 wording is reconciled with this. | S4 output contract: yes |
| R14D6B-S-8 | Accepted | Add a signed `drand_chain_hash` row and verify the chain parameters against it (drand's chain-info hash). The capture time comes from its frozen record (seed_disclosure's capture source), never the caller. The seed-failure path stays read-free. | Capture-record source: yes |
| R14D6B-S-9 | Accepted (noted) | The module has no YAML parser (stdlib only, frozen image). The S4 binding should state the confirmation start and end **only** as the unique rows, or require them equal to the nested values when signing. Rev 2 records this. | Yes |

Next: design rev 2 (`DESIGN_SLICE6B.md`) with these directions, then a Sol re-review,
then the orchestration code.
