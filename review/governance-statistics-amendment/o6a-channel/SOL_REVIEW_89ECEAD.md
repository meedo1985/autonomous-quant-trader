# Sol focused re-check OS3 of the O-6a specification rev 3 at `89ecead`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent re-check. The prompt was the same as Fable OF3's, with the ID prefix `OS3`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106c1-80ef-7f43-b163-8a6c1334f7b0`. The final message is reproduced below unchanged, except that local file links were shortened to repository-relative form.

---

**Model:** OpenAI Codex, GPT-5 family; exact deployment identifier unavailable  
**Commit:** `89ecead2cfbee56a689c854290237a062789c36e`  
**Verdict:** **READY WITH FIXES**

The security construction is sound. A matching archived response for height `h+5` proves that the frozen six-confirmation chain state existed before `T`. It cannot predate that chain state, although it can precede the verifier’s local observation by propagation delay. Capture timing gives the declarer no beacon-outcome choice: the selected drand round is at least 24 hours later and remains unpredictable when the capture is made. The disclosed post-outcome abort remains possible.

The endpoints behave as assumed: both return the block currently at the requested height. CDX supports exact-URL capture rows and exposes timestamps, status, digest, and original URL; `id_` retrieves the unrewritten capture. The remaining defect is evidentiary rather than cryptographic.

### OF2/OS2 status

| Finding | Status | Note |
|---|---|---|
| OF2-1 | Resolved | Static API response replaces rendered explorer pages. |
| OF2-2 | **Partial** | Freeze point and immutable `T`/round are defined, but the one-time CDX observation is not retained. |
| OF2-3 | Resolved | Seven-day archive outage consequence disclosed. |
| OF2-4 | Resolved | Index, pruning, mempool and false-positive settings supplied. |
| OF2-5 | Resolved | Owner wording and §9 reference corrected. |
| OS2-1 | Resolved | `h+5` response establishes the required six-confirmation chain state; see OS3-2 for wording. |
| OS2-2 | Resolved | Capture bytes, metadata, hash, no-capture outcome and later unavailability covered. |
| OS2-3 | Resolved | Thirty-day terminal deadline and replacement procedure supplied. |
| OS2-4 | Resolved | Required node configuration supplied. |
| OS2-5 | Resolved | Owner comparison corrected. |

### New findings

| ID | Severity | Location | Problem, evidence and fix |
|---|---|---|---|
| **OS3-1** | **MAJOR** | [SPEC.md:62](review/governance-statistics-amendment/o6a-channel/SPEC.md), [line 87](review/governance-statistics-amendment/o6a-channel/SPEC.md) | The one-time CDX view is the only evidence that the selected capture was the earliest qualifying capture at the freeze point, but the record retains only the selected capture—not the CDX request and complete response. Later index changes therefore make the selection unauditable. The `id_` fetch is also not explicitly bound to the exact CDX row. **Fix:** retain the acceptance-observation time, exact CDX query URI, complete uncollapsed/paginated response bytes, headers/status, retrieval time and SHA-256. Require exact URL and archived status `200`; bind `original`, timestamp and digest to the selected row; reject replay redirection or any resolved timestamp different from that row. |
| **OS3-2** | **MINOR** | [SPEC.md:84](review/governance-statistics-amendment/o6a-channel/SPEC.md), [line 91](review/governance-statistics-amendment/o6a-channel/SPEC.md) | “No qualifying capture can predate acceptance” is too absolute because §5 later measures acceptance as observed by the verifier’s node. An explorer and Wayback can observe `h+5` first. This does not weaken security: the matching hash still proves the six-confirmation chain state existed. **Fix:** say it cannot predate existence of the frozen `h+5` chain state, but may predate the verifier’s local observation; record that observation time because it starts the seven-day window. |

### Sources

- [mempool.space REST API](https://mempool.space/docs/api/rest) and [Blockstream Esplora API](https://github.com/Blockstream/esplora/blob/master/API.md) document `/block-height/:height`.
- [Internet Archive CDX documentation](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md) documents exact matching and the timestamp/original/status/digest fields.
- [Internet Archive `id_` documentation](https://github.com/internetarchive/wayback/pull/146/files) describes retrieval without Wayback rewriting.
- [Internet Archive capture metadata](https://github.com/internetarchive/warcprox/blob/master/api.rst) defines the timestamp as the resource-fetch start time.
- [drand scheduling](https://docs.drand.love/docs/specification/) and [drand cryptography](https://github.com/drand/drand-docs/blob/master/docs/concepts/01-Cryptography.md) support deterministic round selection and future-round unpredictability.

Read-only review. `git diff --check` passed; code tests, lint, typing and import checks are N/A. No confirmation/lockbox data or untracked `data/` content was accessed. No edits, commits or pushes were made. This must be committed separately before repository governance treats it as a completed review record.

Rev 3 fixes the last round’s security issues; the h+5 anchor prevents choosing a known drand outcome.  
Before approval, preserve the complete CDX freeze evidence and bind every id_ body to its exact indexed row.  
A capture may precede your node’s observation, but not the six-confirmation chain state that makes it qualify.
