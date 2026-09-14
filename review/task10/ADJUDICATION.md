# Task 10 Fable finding adjudication

Date: 2026-09-14

| ID | Severity | Decision | Reason and disposition |
|---|---|---|---|
| T10-NB-01 | NON-BLOCKING | AGREE | Family is an asserted ledger fact. Before any trial is authorized, the later protected experiment engine must cross-check it with the registered hypothesis. Task 10 grants no permission and no budget decision. |
| T10-NB-02 | NON-BLOCKING | AGREE | The generic ledger deliberately accepts arbitrary canonical record types. The Task 10 preregistration write APIs validate their payloads. Typed read-hardening is a future maintenance improvement. |
| T10-NB-03 | NON-BLOCKING | PARTIAL | The frozen hypothesis schema intentionally permits broad field shapes. Task 10 provides a deterministic enumerator that rejects ambiguous grids before an experiment record can be constructed. Coupling extra constraints into schema-valid preregistration would strengthen frozen policy beyond its text. |
| T10-NB-04 | NON-BLOCKING | AGREE | JSON-native booleans and integers are distinguished. Non-JSON-native integer subclasses are outside the public input contract but should be rejected explicitly in a later hardening pass. |
| T10-NB-05 | NON-BLOCKING | AGREE | An unlocked reader can see a transient incomplete append. It fails closed and never edits data. Taking the lock would make a nominal read create/mutate a sidecar, so this safe behavior is documented rather than changed. |
| T10-Q-01 | QUESTION | AGREE | Clean suffix deletion needs an external head anchor. The future attestation layer is the correct governed location; Task 10 cannot create a protected acceptance anchor. |
| T10-Q-02 | QUESTION | RESOLVED | Independently recomputed with Python standard library only. Exact bytes were `["aqt.trial_seed.v1","a…a","c…c",7]`; SHA-256 was `a253b333a47d7aa201995a00ee4ee44bf0cd1ef6ea144cbef971ccea6d8cefa0`, matching the frozen test vector. |

Local blockers remaining: none.
External review: ADJUDICATED, final PASS.
