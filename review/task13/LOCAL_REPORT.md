# Task 13 local implementation and gate report

Date: 2026-09-26
Base commit: `0f59c22` (`main`)
Branch: `task13-binance-public-download`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Task 13 is defined in `review/roadmap/ROADMAP_PROPOSAL.md`, which is still an
open, unapproved proposal (PR #13). The roadmap's approval clause is what would
authorize Task 13. This branch is written in advance of that approval and
**must not merge before it**. Owner questions Q3 and Q4 are unanswered; the code
takes the conservative reading of both (exploration window only; the owner runs
the network calls). Nothing here was run against the network.

## Scope

- `src/aqt/data/binance_public.py` (new): write-once, checksum-verified,
  credential-free download of monthly 1h kline archives and one `exchangeInfo`
  snapshot, over an injected transport.
- `scripts/download_market_data.py` (new): owner-run CLI; exploration months
  only; writes a new run summary per run; exit 1 if anything is unavailable.
- `tests/unit/test_binance_public.py` (new): 25 offline tests, sockets blocked.
- `README.md`: one status section.

No frozen artifact, no existing module, and no import contract changed. Size is
671 added lines against the roadmap's ~400 target; 224 of them are tests.

## Acceptance criteria (roadmap Task 13)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Exact bytes stored; SHA-256 matches an independent digest | `test_fetch_stores_exact_bytes_with_independent_hash` |
| 2 | Checksum mismatch raises and writes nothing | `test_checksum_mismatch_raises_and_writes_nothing`, `test_checksum_naming_another_file_is_rejected` |
| 3 | No request can carry an auth header, signature, or `apiKey` | `test_authenticated_or_unlisted_request_cannot_be_built` (7 cases, asserted on `PublicRequest`), `test_every_request_sent_is_unauthenticated` |
| 4 | Construction fails if Binance key variables are set | `test_client_refuses_to_start_with_credentials_in_environment` (3 names) |
| 5 | Missing archive is `unavailable(reason=...)`, not filled | `test_missing_archive_is_unavailable_not_filled`; CLI smoke run below |
| 6 | Re-run is a no-op and never rewrites bytes | `test_rerun_is_a_no_op_and_never_rewrites` (no request sent, same mtime); `test_tampered_artifact_is_refused` |
| 7 | Whole module runs with sockets blocked | autouse `_no_sockets` fixture patches `socket.socket`, `create_connection`, `getaddrinfo` |

Also covered: bounded retries on 5xx and transport errors
(`test_retries_are_bounded_on_server_errors`, `test_transient_error_then_success`),
stop without retry on 403/418/429 (`test_rate_limit_stops_without_retry`), symbol
allow-list, and `EXPLORATION_MONTHS` checked against the text of
`protocols/protocol_v1.yaml` (53 months, 2017-08 to 2021-12).

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Exit | Result |
|---|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 0 | 1178 passed, 4 pre-existing skips |
| `ruff check .` | 0 | all checks passed |
| `ruff format --check .` | 0 | 65 files already formatted |
| `mypy src scripts/download_market_data.py` | 0 | no issues in 32 source files |
| `lint-imports` | 0 | 5 kept, 0 broken |
| `git diff --check` | 0 | clean |

CLI smoke run, offline, with a transport answering 404 to everything: 54
`UNAVAILABLE` lines (1 `exchangeInfo` + 53 months), run summary written as
canonical JSON, exit 1.

## Frozen verification

`git diff main -- docs protocols schemas specs FROZEN_HASHES.json
FROZEN_HASHES.json.sha256` is empty. All 14 `.sha256` sidecars were recomputed
independently and match. `tests/integration/test_manifest_experiment_binding.py`
and `test_preregistration_schema_binding.py` pass (3 tests). The baseline is
`main` at `0f59c22`, the last merged state.

## Findings (self-review against task-gate, binance-quant, quant-code, and scientific-reproducibility checklists)

- **T13-01 NON-BLOCKING (carried to Task 14).** The `exchangeInfo` snapshot
  records the filters and symbol status **as of the download date**, not as of
  2017–2021. Section 6 asks for point-in-time filters "where available". Task 14
  must mark historical filters and status `UNAVAILABLE` for the exploration
  window, not bind this snapshot as if it were historical. Left unrepaired here
  because this task parses nothing.
- **T13-02 NON-BLOCKING.** If the sidecar write fails after the archive is
  written, the next run raises `artifact without sidecar` and a person must
  remove the file. This fails closed rather than guessing, so it is left as is.
- **T13-03 NON-BLOCKING.** Write-once means a later upstream re-publication of an
  archive is not picked up; the stored bytes and their hash stay as recorded.
  That is the intended section 6 behavior.
- **T13-04 NON-BLOCKING (external fact, unverified).** Binance changed Spot
  archive timestamps to microseconds for data from 2025-01-01. The exploration
  window ends in 2021, so this does not reach these archives, but Task 14's
  parser should reject rather than guess on an unexpected timestamp width. Not
  verified against Binance documentation in this session: network access is
  not used by the coding AI.
- **T13-05 NON-BLOCKING.** Size over the roadmap's ~400-line target (see Scope).
- **T13-06 QUESTION (owner).** Q3 and Q4 of the roadmap. The code assumes
  exploration only and owner-run downloads.

## Gate

LOCAL GATE: PASS, conditional on the roadmap being approved.

BLOCKER to merge: roadmap PR #13 is unapproved, so Task 13 is not yet
authorized. Independent review status: `NOT SENT`. This module is not one of
the section 16 enumerated components, so a different-model review is not
mandatory, but the AGENTS.md adversarial-review packet has not been prepared
and no independent reviewer has looked at this code.
