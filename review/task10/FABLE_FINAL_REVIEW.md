# Claude Fable 5.1 final adversarial review

Date: 2026-09-14
Observed canonical model: `claude-fable-5-1`
Verdict: **PASS**
Blockers: none

Fable verified the packet snapshot hashes and found no excluded policy,
confirmation/lockbox, promotion, execution, or network behavior.

## Non-blocking findings

- **T10-NB-01 — caller-asserted family:** `record_trial` accepts a family
  supplied by its caller, so a later experiment layer must cross-check it
  against the registered hypothesis before relying on lifetime counts.
- **T10-NB-02 — generic typed payloads:** callers can use the generic ledger
  primitive with a reserved record type and malformed payload; read-side
  helpers may then raise a raw shape error. The preregistration write APIs
  themselves validate correctly.
- **T10-NB-03 — grid validation time:** frozen-schema-valid hypothesis content
  can be registered even if its grid is rejected later by
  `enumerate_trials`.
- **T10-NB-04 — Python subclasses:** distinctness uses Python type names, so a
  non-JSON-native integer subclass and an integer could serialize identically.
- **T10-NB-05 — unlocked readers:** a reader racing an in-flight append can
  transiently report a torn final line. Writers remain serialized and never
  overwrite or repair damaged bytes.

## Questions

- **T10-Q-01 — clean tail truncation:** a self-contained hash chain cannot
  detect removal of complete trailing entries without an external head anchor.
  A later attestation layer should anchor the ledger head.
- **T10-Q-02 — independent seed digest:** Fable did not independently recompute
  the fixed test vector during its run and relied on the recorded focused test.

Fable found the concurrency, tamper detection, canonical bytes, schema
validation, seed framing, scope boundary, and acceptance evidence sufficient
for Task 10 and returned final **PASS**.
