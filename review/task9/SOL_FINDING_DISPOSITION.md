# Sol High Finding Disposition

All five findings are **ACCEPTED AND FIXED**.

| Finding | Correction | Regression evidence |
|---|---|---|
| Semantic verification | Shared semantic validator now runs during build and verification and checks header, coverage, lineage, gaps, provenance, and supplied series metadata. | Rehashed invalid bar count is rejected. |
| Fixed interval | Partition manifests require the protocol's `1h` series and label. | A real two-hour series is rejected. |
| Sealed/composite validation | Only lockbox may be sealed; exploration and confirmation require full manifests; every symbol requires all three partitions; composite headers are revalidated. | Wrong sealed partition, mixed symbol coverage, and a rehashed invalid header are rejected. |
| Raw identity | `RawArtifact` accepts exact bytes and computes SHA-256 and byte count internally. Caller-asserted metadata is not an API. | Byte mutation changes identity; metadata arguments raise. |
| Git bypasses | The clean-tree check rejects index masking flags and ignored source files, then compares each clean-filtered working blob to the recorded commit blob. | Both index flags and an ignored Python source file are rejected. |

Post-fix focused suite: **55 passed**.
Post-fix full suite: **900 passed, 4 skipped**.
