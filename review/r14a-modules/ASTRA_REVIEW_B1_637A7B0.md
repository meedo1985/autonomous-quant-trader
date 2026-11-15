# Astra review of slice 6b build B1 at 637a7b0

- Reviewer: Codex CLI 0.164.0, requested model `gpt-6-astra` (`-c model_reasoning_effort=high`, `-s read-only`); the Codex run log header shows `model: gpt-6-astra`. The reviewer itself reports the runtime model ID is not exposed to it.
- Prompt: `B1_REVIEW_PROMPT_ASTRA.md` (`b9196fa`). Run by Claude Opus 5.5 on 2026-11-15; output recorded verbatim below.

---

**Verdict: FIX.** B1’s hash bindings and consumer parity are sound, but refusal handling and timestamp validation need corrections. Full test validation remains blocked by the read-only environment.

**Model:** exact runtime model ID is not exposed; I cannot attest that this response ran on Astra. Builder metadata identifies `claude-opus-5-5`.

Reviewed `8d63b21..637a7b0`. Actual HEAD is `b9196fa`, which adds only the review prompt; affected code and tests match the target.

**Findings — all proposals, unapplied**

- **B1-A-1 — major: some input failures escape the `CycleError` contract.**  
  Locations: [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2997), lines 2997, 3047–3058, 3070–3079, 3139–3153.  
  Read-only probes reproduced: capture `url=[]` → `TypeError`; declaration `trial_id=[]` or `hypothesis_hash=[]` → `TypeError`; classifier upper bounds missing `T` → `KeyError`; threshold `"x"` → ordinary `ValueError`; missing qualification directory → `FileNotFoundError`. Canonical declaration bytes can pass `verify_chain` without these fields being validated. These cases stop execution but bypass the promised refusal type.  
  **Correction:** validate types before set operations; translate expected file, parsing, threshold-conversion and `for_k` failures into `CycleError`, with specific regression tests.

- **B1-A-2 — minor: timestamp checks accept forms outside their stated formats.**  
  Locations: `c2_confirmation.py:3000–3005, 3165–3170`.  
  Confirmed acceptance of `last_seen="2024-1-1T0:0:0Z"` and full-width Unicode year digits in both timestamps. `strptime` permits unpadded fields; `isdigit()` permits Unicode digits. This admits multiple textual representations and a timestamp that cannot literally match an ASCII CDX row.  
  **Correction:** require exact ASCII shapes and valid calendar values; enforce canonical round-trip equality.

- **B1-A-3 — minor: several important regressions would survive the tests.**  
  Locations: [test_c2_confirmation_inputs.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_inputs.py:281), lines 281–395; capture tests 94–204.  
  The declaration fixture’s object-map order equals declaration order, so replacing ordered lookup with `trial_objects.values()` would still pass. The 21-trial test uses one family, so it does not distinguish a global limit from a per-family limit.  
  **Correction:** reverse object-map insertion order; test 11+10 trials across families with valid objects; isolate the own-`trial_id` mismatch after updating its configuration hash. Add A1/A2 cases, gzip mutation/member/padding cases with the original digest held fixed, noncanonical base64 pad bits, and classifier `K=1` behavior.

**Deviation decisions**

- **B1-D-1: ACCEPT** the payload-based v2 digest design. Independently recomputed the fixture: 69 bytes → `NNVZIO5QLFHVIRULV75YOBX7EKNQDJMI`, decompressing to exactly the genesis hash. Internet Archive’s CDX writer uses `WARC-Payload-Digest`, consistent with this approach. [Primary source](https://github.com/internetarchive/CDX-Writer/blob/master/cdx_writer.py#L409-L425)  
  Recompression, appended empty gzip members and zero padding all fail against the original digest. Nonempty additional decoded content and noncanonical base64 pad bits are refused. Empty members/padding pass only with a correspondingly changed digest, which remains subject to archive-provenance verification. Live CDX/capture retrieval was unavailable, so the fixture’s historical provenance was not independently authenticated. SPEC §5’s exact fetch URL/timestamp, redirect exclusion, freeze timing, earliest capture and later invalidation remain external obligations; v2 does not prove them.

- **B1-D-2: ACCEPT WITH CHANGES** for A2’s exact timestamp enforcement. Adding `protocol_hash` is necessary for `verify_chain`; `start` preserves those declaration bytes, and `_check_declared` accepts the additional top-level fields. The other added value restrictions do not conflict with these consumers.

**Checks satisfied**

- Header display/internal byte order, little-endian day-zero timestamp, sixth-header tip and concatenated-header SHA-256 match rev 16.
- Qualification hashing matches `verify_code`: canonical manifest hash, raw file hashes, correct signed row.
- Classifier conversion and delegation match `d19_heldout.py:188–192` and `reduce.for_k`.
- No protected-data reads or writes occur in these helpers. Qualification-file reads are intentional. Entry-point ordering awaits later slices.
- Pinned chain and 6a bytes are unchanged; their source-equality tests passed. The existing tests generally target plausible regressions, subject to A3.

**Commands and results**

All shell commands used `rtk proxy` after reading RTK instructions.

- `git status`, target diff, working/staged diffs, `git rev-parse HEAD`, `git log -3`: clean tree; four target files; prompt-only successor.
- `git diff --exit-code 8d63b21 637a7b0 -- docs protocols schemas specs FROZEN_HASHES.json '*.sha256' tests/unit/test_c2_confirmation_start.py calibration/c2_lockbox.py`: exit 0.
- Requested pytest command, with bytecode/cache writes disabled: exit 1 before collection; no usable temporary directory.
- Same command with `PYTEST_ADDOPTS="-p no:cacheprovider --capture=sys --tb=no"`: **72 passed, 27 setup errors**, exit 1.
- Diagnostic retry with `--capture=sys --tb=short -x`: **32 passed, 1 setup error**, confirming temporary-directory failure.
- Two in-memory `python -B -` probe scripts: exit 0; reproduced findings, capture behavior and unchanged pinned bytes.

**Files/ranges read:** both notes in full (1–43, 1–46); design §§1–2.1 and §8 (approximately 40–188, 396–409), failure contract; SPEC 51–116; confirmation 630–730, 1077–1084, 2369–2742, 2820–3184; inputs tests 1–395; start tests 1–320 plus test inventory; lockbox 719–756; screen 370–502; reduce 1–80; heldout 180–192; qobj 215–307; seeds 1–63; repository governance and review skills.

No files changed. Lint/type/full import-boundary checks and a full frozen-hash audit were outside this bounded review. This report remains uncommitted, so it does **not** yet satisfy the repository’s committed-review-record requirement.