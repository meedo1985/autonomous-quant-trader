# Astra review prompt: slice 6b build B1 (read-free input checks) at 637a7b0

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, commit `637a7b0`. Do not modify any file.
Your findings are proposals; you are not an authority. This is the Constitution §16
different-model review of `calibration/c2_confirmation.py` changes; the builder was Claude
Opus 5.5.

Scope: `git diff 8d63b21 637a7b0` only (the B1 functions appended after the pinned 6a
section, their tests in `tests/unit/test_c2_confirmation_inputs.py`, and the two notes
files). Read first: `review/r14a-modules/BUILD_NOTES_SLICE6B_B1.md`,
`review/r14a-modules/VERIFY_CAPTURE_DIGEST_2026-11-15.md`, and in
`review/r14a-modules/DESIGN_SLICE6B.md` (rev 16) §1 (entry points, `sources`, declaration
layout), §2 (sources table: day 0 / tip row, classifier row), §2.1 (capture record) and §8.
Use code and the O-6a SPEC (`review/governance-statistics-amendment/o6a-channel/SPEC.md`
§5) only where needed. Do not reopen owner decisions B-1..B-5, C-1..C-3 or the rest of the
design.

Check:
1. Each B1 function against its rev 16 text: `headers_check`, `check_capture_record`,
   `qualification_report`, `classifier_bounds`, `parse_declaration`. Anything missing,
   extra, or in a different order of checks that matters; every refusal is read-free.
2. Deviation B1-D-1 (capture schema v2): is the evidence sound (CDX digest = SHA-1 of the
   stored payload; the known capture), does v2 close the gap without opening another (for
   example a payload that decodes to the tip hash but is not the archived bytes, gzip
   members/trailing data, base64 forms), and is anything in SPEC §5 now unchecked?
3. Deviation B1-D-2 (`protocol_hash` added to the declaration keys) and the extra value
   forms: correct, and do they conflict with `verify_chain`, `start` or the lockbox's
   `_check_declared`?
4. Byte order and hash conventions in `headers_check` (display vs internal), day 0 from
   bytes 68-71, and the tip hash used by the capture check.
5. `qualification_report` parity with `verify_code` (canonical manifest hash, raw-byte file
   hashes, the signed row name) and `classifier_bounds` parity with
   `scripts/d19_heldout.py` l.188-191 and `reduce.for_k`.
6. Test quality: would each test fail on a plausible regression? Name missing tests.
7. The pinned 6a section is unchanged (`tests/unit/test_c2_confirmation_start.py`).

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_inputs.py
tests/unit/test_c2_confirmation_start.py -q`.

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe
(say if not exposed); files and line ranges read; commands run with results; findings
B1-A-1.. with severity (blocker/major/minor/info), location, evidence, failure scenario,
proposed correction; a line on each of B1-D-1 and B1-D-2: ACCEPT / ACCEPT WITH CHANGES /
REJECT.
