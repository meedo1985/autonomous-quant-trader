# Slice 6b build: every deviation from design rev 16 (Fable R14B6F-F-11)

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-17, at branch `confirmation-module`
  `867fcc6`. Design text: `DESIGN_SLICE6B.md` rev 16 (unchanged; this list replaces a rev 17
  for the owner's PR review).
- Sources: `BUILD_NOTES_SLICE6B_B1.md` .. `_B5BC.md`, the B1-B5 adjudications, the final
  Fable record `FABLE_FINAL_BUILD_SLICE6B_24F0C95.md` and its adjudication.
- Nothing here is approved by writing it down. "Owner accepted" cites the commit that
  records the owner's own words. Every other row is an owner decision at the §16 PR review.

## 1. Deviations from the rev 16 text

| ID | Rev 16 says | The build does | Why | Status |
|---|---|---|---|---|
| B1-D-1 | §2.1 item 3: `body` hashes to `digest`; schema `capture_record.v1` | Schema `aqt.c2.capture_record.v2`: adds `payload` (the exact archived `id_` bytes, base64) and `content_encoding` (`identity` or `gzip`); the CDX digest is the base32 SHA-1 of `payload`, which must decode to `body` | On a real Internet Archive capture the digest covers the stored, gzip-compressed bytes; rev 16 as written can never pass (`VERIFY_CAPTURE_DIGEST_2026-11-15.md`). The store must keep the archive bytes | Owner accepted 2026-11-17, `OWNER_DECISIONS_BUILD_SLICE6B.md` (S4/SPEC wording to follow) |
| B1-D-2 | §1: the declaration's top-level keys, unknown or missing ones refused; `protocol_hash` not listed | `protocol_hash` is in the key set; plus exact forms (64-hex hashes, non-negative int counts, `YYYY-MM-DDTHH:MM:SSZ` time, non-empty `cycle_id`, at least one trial, trial-object map exactly the declared ids) | Every real declaration carries `protocol_hash` (`verify_chain` reads it); literal rev 16 refuses all of them | Owner accepted 2026-11-17, `OWNER_DECISIONS_BUILD_SLICE6B.md` (S4/SPEC wording to follow) |
| B4-D-1 | §7: five drand rows | Two more signed rows, `drand_group_hash` and `drand_beacon_id`, which drand's chain hash covers | Needed to recompute `drand_chain_hash` (R14D6B2-F-12) | Owner accepted, `3ca103a` (S4/OD-4 row list) |
| B5B-D-1 | §7: `canonical_benchmark_sha256` feeds G-13 | G-13 compares it with the SHA-256 of `specs/CANONICAL_BENCHMARKS_v1.1.md` in the module's checkout; file absent gives G-13 UNAVAILABLE `BENCHMARK_SPEC_MISSING` | Rev 16 names no compared value | Owner accepted, `73bbc5f`. **The file is absent at this commit: every nominee is `NO_RESULT` until it lands through the Constitution process** |
| B5BC-O-1 | §5: the U_ops reason list (B-5, A-7) | `BENCHMARK_SPEC_MISSING` added to `U_OPS_REASONS` | A missing engine file is infrastructure (P18-7) | Owner accepted, `24f0c95` |
| B5BC-A-2 | §10 field list | Each family record also carries `breaches` (every breach) and `attempts` (the §3-rewritten history); each gate carries its `cause` | §3 rule 1: every breach listed, full attempt history kept; P18-7 cause per gate (B5BC-A-1) | Astra-required repair; **§10 wording for the owner** |
| B6F-D-1 (F-2) | §2: `z_crit`/`family_block_rule` equality and classifier bounds checked at the look only | `qualification_checks` also runs in `prepare`, so both entry points refuse before any read | A mismatch would otherwise let every trial read the data and then refuse every look. Also moved: `open_look` now computes the classifier bounds outside the look lock, before `look_allowed` (it takes them from `qualification_checks`); this supersedes reading B5A-R-2 (bounds under the lock after `look_allowed`). A missing `T=<T>` still refuses with nothing written (B6FR-A-3) | Owner accepted 2026-11-17, `OWNER_DECISIONS_BUILD_SLICE6B.md` |
| B6F-D-2 (F-6) | §9: C-14 is diagnostic; silent on its errors | An exception in `cpcv_report` is recorded as `{"role": "diagnostic_only", "status": "UNAVAILABLE", "reason": "C14_ERROR:<type>"}`; the look continues | Nothing may read C-14 (§9), so it must not abort the look | Owner accepted 2026-11-17, `OWNER_DECISIONS_BUILD_SLICE6B.md` |
| F-7 cap | §2.1: no size bound | `CAPTURE_PAYLOAD_MAX = 1024` bytes, checked before `gzip.decompress` | Bounds decompression of caller bytes | Fable's proposal, repaired; for the record |

## 2. Readings that narrow the text (recorded, Fable found them consistent)

| ID | Reading |
|---|---|
| B5B-R-1 | `read` is called once at the look, and only when some family has a nominee. With no nominee the look makes no manifest check. |
| B5C-R-5 | The closing entry is appended even after a termination entry; release still needs both a closing entry and no termination (§12). |
| B5A-R-2 | Superseded by B6F-D-1: the bounds are now computed before the look lock. |
| B4-A-1 consequence | `signed_c2` refuses a signed C2 in which any §7 row name occurs as a whole token on more than one line, comments included. |

The other readings (B1..B5 notes, `-R-` ids) are in each build note and were checked by
that slice's Astra review.

## 3. Open items that are not code

| ID | Item | Who |
|---|---|---|
| F-9 | The `dsr` block names nominees as column numbers in ascending trial-id order, and does not carry that order; `decision` is Task 12's while V governs. Either add the column order to §10 or bind it in the S4 text | **Owner: S4 wording or a §10 field** |
| F-10 | Status (d) `SEAL_FAILED:<reason>` has no P18-7 cause in either record (the evaluation record is hashed before sealing). How such a family counts, U_ops or U_proc | **Owner wording** |
| F-7 (a) | A known-answer capture from `mempool.space` (only `blockstream.info` was checked) | **Pre-signing step** |
| F-7 (b) | A SPEC rule for a genuine earliest capture the module cannot decode (`br`, `zstd`, trailing newline): today such a refusal is permanent | **Owner/SPEC rule, pre-signing** |
| F-11 | Run `signed_c2` on the candidate signed C2 bytes before signing (catches the B4-A-1 refusal and any malformed row) | **Pre-signing step** |
| F-8 | The launch route must call `start` in each process and pass that `Started` (now a `Store` obligation) | Store build |

Owner items carried from the design (rev 16 "Owner items after rev 16", unchanged by the
build): B-3 "no closing entry" reading and how a `LOOK_WITHOUT_RECORD` cycle counts; the
crash-whatever-the-outcome rule and the one-launch-per-attempt runner promise (P18-1); the
verifier's duty for a true `capture_before_tip_window` and the optional hard capture floor;
the S4/SPEC/P18 wording items listed there.

## 4. What the owner decides at the PR review

1. B1-D-1 and B1-D-2: accept or reject.
2. B6F-D-1 and B6F-D-2: accept or reject.
3. F-9 and F-10: the wording route (may wait for the S4 text).
4. The §16 review itself: the build has had different-model reviews (Astra per slice,
   Fable final, Astra short check of the Fable repairs `ASTRA_REVIEW_B6F_REPAIRS_2A02F45.md`).
   The merge needs both: the repairs of that short check accepted (F-1's merge block is
   lifted only then, `ADJUDICATION_FABLE_FINAL_6B_24F0C95.md`), and the owner's PR review
   (B6FR-A-3).
