# v1.1 method candidate — cover and human review request

**Status:** `NON-BINDING AI METHOD CANDIDATE — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**Prepared:** 2026-09-20
**Prepared by:** Claude, exact observed model ID `claude-opus-5`, read-only
documentation task, AI author. (Claude Opus 5.1 was the preferred author model;
the metadata actually observed in this session is `claude-opus-5`, recorded as
observed rather than as preferred.)
**Repository HEAD at preparation:** `a7f6a5cfdc1d2a3f77b6757201889fe4b49f06f2`
**Independent reviews received:** four AI checks, none of them authoritative.
(1) `../V1_1_CANDIDATE_REVIEW.md`
(Claude, observed model ID `claude-opus-5`, 2026-09-20, verdict
`REVISION_REQUIRED`, two defects corrected in place — see §6.3). (2)
`../V1_1_FABLE_ADVERSARIAL_REVIEW.md` (Claude, observed model ID
`claude-fable-5-1`, 2026-09-20, adversarial check of this directory and of
review (1); three further defects corrected in place — see §6.4 — and
substantive questions for the statistician recorded there, not here). (3) A third
read-only check by Claude (self-reported model ID `claude-fable-5-1`) of
everything changed after review (2), including the first commit; six write-up
defects corrected in place — see §6.5. (4) A fourth check after this branch was
pushed: an adversarial pass by Claude (observed model ID `claude-opus-5`) and an
independent adjudication of it by Claude (observed model ID `claude-fable-5-1`),
the first check by a model other than the one that authored this directory; six
write-up defects corrected in place, one blocker since closed by owner decision,
and one question left open — see §6.6. An AI
review confers no scientific or governance authority, and no human, owner, or
statistician review of this directory exists.

## 1. What "v1.1" means here, and what it does not

The directory name refers to a **candidate successor method set** for the
statistics the frozen v1.0 protocol requests but does not define. It does
**not** mean that a protocol version 1.1 exists, has been drafted, has been
proposed, or is planned. `protocols/protocol_v1.yaml` remains `status: "FROZEN"`
at `protocol_version: "1.0"`, cycle `C1`, and is untouched. No tracked file
**outside the eight this work added** has been modified, renamed, deleted, or
regenerated at any point in preparing, reviewing, committing, or revising this
directory. Exactly eight files were added: the six listed in §3, plus
`../V1_1_CANDIDATE_REVIEW.md` and `../V1_1_FABLE_ADVERSARIAL_REVIEW.md`; no
ninth file has been added since. Within this directory, the only post-review
changes are the corrections in §6.3, §6.4, §6.5, and §6.6, the `.gitattributes`
added on owner instruction at commit time (§6.2), and the resulting
`MANIFEST.sha256` regenerations. Every one of those changes is confined to
`README.md` and `MANIFEST.sha256`: `METHOD_CANDIDATE.md`,
`HUMAN_DECISION_MATRIX.md`, and `PREREGISTRATION_TEMPLATE.md` are each
byte-identical to their first committed revision.

## 2. Authority and non-authorization

This directory is written by an AI. Under `AGENTS.md` and
`docs/RESEARCH_CONSTITUTION.md` §4, research and coding AI may **propose** but
may not author, merge, activate, or self-approve an amendment. Accordingly, this
directory is explicitly **not**:

- a formal governance amendment, or any part of the §4 process (version bump,
  written rationale, owner-of-record signed and dated commit, cycle termination,
  pre-new-cycle activation, preserved history, no retroactive effect);
- an imitation of, or a draft for, such an amendment;
- human, owner, or statistician acceptance of any statistical method, and it
  neither creates nor substitutes for such acceptance;
- a claim that any DSR method is calibrated. Under `OWNER_DSR_DEFER_DECISION.md`
  (owner decision **DEFER**, 2026-09-18) DSR remains diagnostic-only, the
  mandatory `dsr_minimum: 0.95` gate remains unsatisfied, and promotion remains
  blocked regardless of anything decided here;
- authorization for Task 13, a calibration engine, any simulation or Monte Carlo
  run, any code change, confirmation-partition or lockbox data access, a
  governed trial, an eligibility decision, promotion, deployment, or trading;
- a resolution of Astra findings `B1`–`B5` or of `DEC-01` to `DEC-03`.

**No simulation was run, no data was accessed, no network or exchange call was
made, and no credential was used. At preparation and review time nothing was
committed or pushed; on owner instruction this directory was subsequently
committed as a non-binding proposal on branch `review/v1.1-method-candidate`
(PR #2 against `main`), which changes none of the above and confers no
authority.**

Constitution §16 requires different-model **and** human PR review before merging
its enumerated components: validation engine, promotion gate, governor, executor
state machine, lockbox ACL tooling, and protocol enforcement. This directory
contains none of them, so §16 is **not applicable** to it — that is not a claim
that §16 is satisfied, and it is untouched for the code it does govern. For that
later code, a review by a different AI model does not supply the human prong and
is no substitute for statistician acceptance.

**No universal binding is claimed.** The protocol requests a paired Sharpe-like
statistic in thirteen distinct clause groups, enumerated once as rows 1–13 of the
canonical decision object in
`../external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §5. Two are settled
by frozen text; the other eleven are treated strictly row by row. No sentence in
this directory asserts that one estimand binds "paired delta-Sharpe" everywhere,
and the prior recommendation of `KEEP_BLOCKED` for any such universal binding is
not disturbed.

## 3. Contents

| File | Contents |
| --- | --- |
| `README.md` | This cover: status, authority, non-authorization, review request, source inventory, checks |
| `METHOD_CANDIDATE.md` | Separate `E-IMPROV` and `E-DIFF` definitions; proposed consumer bindings row by row for rows 1–13; DSR candidate formula and trial-count construction; PBO scalar, ranking, tie, missing-trial and alignment rules; CPCV/ESS/bootstrap interaction; units, domains, failure behaviour, invariants; traceability table |
| `PREREGISTRATION_TEMPLATE.md` | Reviewable fields only, with an explicit `<<UNRESOLVED: D-xx>>` placeholder for every human decision not supported by current evidence. Nothing is pre-filled |
| `HUMAN_DECISION_MATRIX.md` | `D-01`–`D-20`: options, evidence, consequence, recommended candidate, falsifier, authority, and the required reviewer response code |
| `MANIFEST.sha256` | SHA-256 of the four Markdown files above, generated after they were final; it does not hash itself |
| `.gitattributes` | Packaging only: pins `eol=lf` so the manifest stays verifiable on every platform. Deliberately not listed in the manifest. No scientific content — see §6.2 |

Read `METHOD_CANDIDATE.md` first, then `HUMAN_DECISION_MATRIX.md`, then complete
a copy of `PREREGISTRATION_TEMPLATE.md` only for the rows actually decided.

## 4. Exact human review request

> **Q1.** For each of rows 3–7 (Queue I, interpretive), is the `PROPOSED`
> estimand in `METHOD_CANDIDATE.md` §2 the correct reading of the clause under
> frozen v1.0 wording — `ACCEPT`, `REVISE` (with substituted estimand and
> reason), or `REJECT` (leaving the row unbound)?
>
> **Q2.** For row 8 (PBO), which of the two mutually exclusive repairs in
> `HUMAN_DECISION_MATRIX.md` `D-08` should be carried into the §4 process, and
> is Lemma `L-1` — that under a shared benchmark, ranking by `E-IMPROV` is
> identical to ranking by the candidate's own Sharpe — a sufficient reason to
> prefer reading `ranking_metric` as `E-DIFF`?
>
> **Q3.** For rows 9–10 (lockbox) and rows 11–13 (undefined), are the scoped
> decision sets `D-11`, `D-12`, `D-13`, `D-14`, `D-15` complete, and is any of
> them closable by a statistician alone rather than by the §4 process?
>
> **Q4.** For DSR, are findings `F-1` to `F-3` in `METHOD_CANDIDATE.md` §3.3
> correct — in particular, that the existing candidate
> `aqt.dsr.iid_raw_count.proposal.v1` adopts the frozen **fallback**
> (`raw_trial_count`, `protocol_v1.yaml:233`) without the frozen **primary**
> eigenvalue method (line 232) ever being evaluated and without any
> protocol-stated fallback trigger (the only frozen trigger text is Constitution
> §9 line 106; see `METHOD_CANDIDATE.md` §3.3 `F-1`) — and is leaving `D-16`,
> `D-17`, `D-18` as blocking placeholders the right outcome?
>
> **Q5.** Is any placeholder in `PREREGISTRATION_TEMPLATE.md` in fact already
> determined by evidence in this repository, such that leaving it unresolved is
> an error rather than honest caution? Conversely, is any `PROPOSED` value in
> `METHOD_CANDIDATE.md` in fact unsupported and better demoted to a placeholder?

A reviewer who answers only "the evidence does not support these candidates" has
given a complete and useful answer. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain
valid scientific outcomes in this project, and rejecting every candidate here
requires no follow-up work.

**Required response form.** One code per row of `HUMAN_DECISION_MATRIX.md`
(`A` accept / `R` revise / `X` reject / `D` defer) plus a recorded rationale,
the reviewer's name, qualification, conflict disclosure, date, and the SHA-256
of the bytes reviewed. No decision-form file is supplied here, because inventing
a signature block that has not been agreed would itself be a governance act;
`../external-review-packet/REVIEWER_DECISION_FORM.md` is the existing precedent
for its structure.

## 5. Source inventory

SHA-256 of **raw working-tree bytes** at HEAD
`a7f6a5cfdc1d2a3f77b6757201889fe4b49f06f2`, not canonicalized. Paths are
repository-relative.

**Line endings, stated precisely (`C-1`).** These values were computed on a
Windows checkout with `core.autocrlf=true`. Twenty of the twenty-one files below
are LF in this working tree, and those twenty values equal the SHA-256 of each
file's **Git index blob**, so they reproduce anywhere via
`git show a7f6a5c:<path> | sha256sum`. They are **not** reproducible from a
working-tree file on every platform: **fourteen** of the twenty carry no `text`,
`eol`, or `-text` attribute (`git check-attr text eol -- <path>` reports
`unspecified`), so on a fresh Windows clone with `core.autocrlf=true` they
materialize as CRLF and the recorded value stops matching the file on disk.
**One file is the exact reverse:**
`DSR_METHOD_PREREGISTRATION_DRAFT.md` (§5.4) is **CRLF** in this working tree —
208 CRLF, zero bare LF — because no `eol=lf` attribute protects it
(`git ls-files --eol` reports `i/lf w/crlf attr/`). Its recorded value
`1391f81e…` is therefore the hash of **CRLF** bytes: it reproduces on a Windows
`autocrlf=true` checkout and **not** from its index blob. For that file only, both
values are given. A reviewer verifying on an arbitrary platform should hash index
blobs, not working-tree files:

| File | CRLF bytes (this Windows working tree, recorded in §5.4) | LF-normalized bytes |
| --- | --- | --- |
| `DSR_METHOD_PREREGISTRATION_DRAFT.md` | `1391f81edbcfdb2aaad2d49d8c0843688514b5c224dfc4e9f4d8332cdd00ce91` | `5c7119a56a35427b3a370e86cb9d2a46a46c2f0cf50891baeac92eadf606e899` |

The first revision of this section claimed "LF line endings" for all twenty-one
files, which was false for this one file. Attributing that miss precisely: the
adversarial review recomputed all twenty-one recorded hashes and found no
mismatch (`../V1_1_FABLE_ADVERSARIAL_REVIEW.md` §3, source-inventory check) —
correctly, because each did match the bytes on disk — but tested equality only,
never the stated *characterization* of those bytes. The first review
(`../V1_1_CANDIDATE_REVIEW.md` §4) did not recompute these twenty-one hashes at
all; it verified `MANIFEST.sha256` and the frozen inventory. **The defect is also
inherited, not new to this directory:** `../external-review-packet/README.md` §5
records the same `1391f81e…` value for the same file and characterizes its hashes
the same way, and that packet's own two reviews did not catch it either.
**Who found it, and how many passes carried it.** `C-1` was found by this
directory's author (`claude-opus-5`) while committing, not by either recorded
review; the token `C-1` appears in neither review file, and the attribution is
recorded here because it was previously stated nowhere. An earlier revision said
"five passes over two packets carried it" without stating the counting criterion,
which made the number unauditable. Stated precisely: **four** passes recorded the
value or verified it and did not catch the mischaracterization — the external
packet's authoring pass, the external `claude-fable-5-1` review (which verified
§5's hashes, its line 38), this directory's authoring pass, and the adversarial
review (which recomputed all twenty-one, its line 60). Two further passes had the
opportunity and made no §5 hash claim: the external closure review and review (1)
(which did not recompute them, as stated above). Six passes in total touched the
two packets; four carried the claim.
The file itself is **not** modified, normalized, or re-hashed here, for two
reasons stated plainly. It and its neighbours are committed artifacts of other
tasks, outside the owner instruction that produced this commit. And the same value
is recorded in `../external-review-packet/README.md`, which is manifest-covered
and `eol=lf`-pinned, so correcting the characterization at its source cannot be
done here without invalidating that packet's manifest. An earlier revision of this
paragraph gave a different and **incorrect** reason — that an `eol=lf` attribute
would invalidate the value §5.4 records. It would in fact make the published
LF value `5c7119a5…` the reproducible one; the obstacle is authority and blast
radius, not arithmetic. **Proposal for the owner, not applied:** decide whether the
`eol=lf` protection that `../external-review-packet/` and this directory now have
should be extended to the Markdown directly under
`review/governance-statistics-amendment/` — three files there are currently CRLF
in this working tree (`DSR_AGENT_REVIEW_ADDENDUM.md`, `DSR_DRAFT_REVIEW_PACKET.md`,
`DSR_METHOD_PREREGISTRATION_DRAFT.md`) — and if so, re-record every hash that
references them in the same change, including the one in the external packet.

### 5.1 Frozen governance (read-only; unchanged)

| SHA-256 | Path |
| --- | --- |
| `776396a25012276f22c4d7478166614e2f4f58e1a866e274ff8437e60cc09516` | `docs/RESEARCH_CONSTITUTION.md` |
| `d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26` | `protocols/protocol_v1.yaml` |

### 5.2 Instructions, skill, and implementation

| SHA-256 | Path |
| --- | --- |
| `ab4cb23eefec99207165c35e19727a12ca439e42741c01130b7db24d4dc0474b` | `AGENTS.md` |
| `627e27aaf531327c8e072bf361d72d6f287cbb6e3ec0fb4f8baab659450d97f6` | `.agents/skills/statistical-binding-review/SKILL.md` |
| `e8cd22385b978c49b2d0ba5b15f8760b179226b86fea70fdb027d9c382044bad` | `src/aqt/metrics/statistics.py` |
| `f3ba9362c5f1512fd24600775df2aa048a7e701c8f40c8cb00e97c2c644f515c` | `review/task12/IMPLEMENTATION_CONVENTIONS.md` |
| `1c686bcf61b4851f336b270c4e437d01e6a81459cbe3e6b86325c692e058d600` | `review/task12/OWNER_DECISION.md` |

### 5.3 External review packet (prefix `review/governance-statistics-amendment/external-review-packet/`)

| SHA-256 | Path |
| --- | --- |
| `b1d449f1e7f92e1a74853ce6f1143dc6abc3a7f2491372eb1306e0d8df43f45b` | `README.md` |
| `809ba3ea5d40a23f3d246653ed52ed249ffa8a8be9783502981dd853b10a2b4f` | `STATISTICAL_BINDING_CANDIDATE.md` |
| `915f804f10262d98b32849c2fa2454f7b8efb75d21d9fdeab7df6a831467ab1b` | `TECHNICAL_APPENDIX.md` |
| `7beae0fabbc44820ba34b08a8ec761f0dab949688a9788bcc7adff811b70fa11` | `REVIEWER_DECISION_FORM.md` |

### 5.4 Drafts, reconciliation, and decisions (prefix `review/governance-statistics-amendment/`)

| SHA-256 | Path |
| --- | --- |
| `6aaa2cab0e3da51dbede9e2ce11f7404d09cb6bf431b2c17e3df12a59cd03979` | `DRAFT_AMENDMENT_PROPOSAL.md` |
| `1391f81edbcfdb2aaad2d49d8c0843688514b5c224dfc4e9f4d8332cdd00ce91` | `DSR_METHOD_PREREGISTRATION_DRAFT.md` |
| `4017d27d784e81db18245aae233e5cfc025ccffcc2c5bcff3184b78f0da47da8` | `DSR_CALIBRATION_RECONCILIATION.md` |
| `c0120d23eea20f37ce951be5436cec19ce19538eb19f04decf4094c71e5c2c4b` | `DSR_CALIBRATION_PLAN.md` |
| `17c7945c3ed2b5ffb8c678bd2d03487bb8f49ef4f52257b5662ed4bccf1ebc17` | `LOCKBOX_PREDICTION_PROPOSAL.md` |
| `92be40273751c4f21bdb4cd067fba978b8c674cd7be515c259cbdabc1cebf2a0` | `ASTRA_REVIEW.md` |
| `dc0e77f9a6b85c68f7eb9de49520bb5660a6a590b38501513864a0c5403570d2` | `OWNER_DECISION.md` |
| `8aee76b499f8c3b3fc851e541da7622d649437c6da7ce01071a5a84515c35531` | `OWNER_DSR_DEFER_DECISION.md` |

### 5.5 Estimand disambiguation

| SHA-256 | Path |
| --- | --- |
| `05f771973a23c159c615a9e9dd5cc0e71e1cc1e196f740f79436f7df572b7621` | `review/estimand-disambiguation/PAIRED_SHARPE_USAGE_RECORD.md` |
| `d1426e3c667df8a887ef60fa6b7a6e00c47486daa25c2d198250217d425b10a3` | `review/estimand-disambiguation/REVIEW_ADJUDICATION.md` |

Every hash in §§5.1–5.5 that also appears in
`../external-review-packet/README.md` §5 reproduces that value exactly,
confirming those bytes are unchanged between HEAD `fad5564` and HEAD `a7f6a5c`.

## 6. Checks run while preparing this directory

| Check | Command (from repository root) | Result |
| --- | --- | --- |
| Source byte inventory | `sha256sum` over the 21 files in §5 | `PASS` — all 21 computed; every overlapping value matches the external packet's recorded hash |
| Frozen protected paths | `git status --short`, `git diff --stat` | `PASS` — `docs/`, `protocols/`, `schemas/`, `specs/`, `FROZEN_HASHES.json` and all sidecars unchanged; no tracked file modified, renamed, or deleted |
| Frozen protocol/constitution binding | `docs/RESEARCH_CONSTITUTION.md` and `protocols/protocol_v1.yaml` hashes compared to the values recorded in the external packet `README.md` §5.1 | `PASS` — 2/2 identical |
| Path and cross-reference resolution | every repository-relative path and intra-directory reference cited in these four files resolved against the working tree | `PASS` |
| Manifest generation and verification | `sha256sum` over the four Markdown files after they were final, written to `MANIFEST.sha256`, then recomputed and compared | `PASS` — 4/4 |
| Decision-ID resolution | `D-01`–`D-20` cross-checked between `METHOD_CANDIDATE.md` and `HUMAN_DECISION_MATRIX.md` | `PASS` — bidirectional; all 20 IDs appear in all three documents and each resolves to exactly one matrix row |
| Decision-ID *referent* correctness | each cross-reference re-read against the row it names, not merely resolved | `PASS after corrections` — one wrong referent found and fixed by the first review (§6.3, `R-1`); one wrong dependency-note referent found and fixed by the second (§6.4, `A-1`); resolution alone had detected neither |
| Invariant-ID resolution | `I-1`–`I-12` traced to their cited source | `PASS after correction` — `I-1`–`I-9` are introduced by this packet, not by the cited source; the mapping is now declared (§6.3, `R-2`) |
| Exact-arithmetic reverification | Lemma `L-1`, the `TECHNICAL_APPENDIX.md` §4 trial table, `C(16,8) = 12,870 = 2 × 6,435`, the `N = 2` PBO `omega`/`logit` branches including the `0.5` tie branch, and the negative-`v` plateau inversion, recomputed from exact rationals | `PASS` — every published value reproduced to full double precision; no discrepancy |
| Frozen citation audit | every `protocol_v1.yaml` and `RESEARCH_CONSTITUTION.md` line number cited in these four files re-read at HEAD | `PASS` — all resolve to the asserted clause; one incomplete citation noted as non-blocking (§6.3, `N-2`); one omitted frozen clause (Constitution §9 line 106) added to §3.3 `F-1` by the second review (§6.4, `A-3`) |
| Source line endings | every §5 source classified by raw bytes and by `git ls-files --eol` | `PASS after correction` — 21/21 recorded hashes match raw bytes, but 1/21 is CRLF, not LF as §5 originally claimed (`C-1`) |
| Whitespace | `git diff --check` | `PASS` — no output |
| Working tree | `git status --short --untracked-files=all` | `PASS` **at preparation time**: only untracked files — this directory, `../V1_1_CANDIDATE_REVIEW.md`, and `../V1_1_FABLE_ADVERSARIAL_REVIEW.md`; no tracked file modified, renamed, or deleted. The directory now holds six files (§3), and all eight are committed as described in §1 and §2 |
| Frozen verifier | `review/task6/verify_frozen.ps1` | **CANNOT RUN in this environment** — independently reproduced instead, `PASS`; see §6.1 |
| Tests, Ruff, mypy, import-linter | — | `N/A` — review Markdown only; no executable code, configuration, dependency, or import boundary is added or changed |

### 6.1 Frozen verifier, stated plainly

`review/task6/verify_frozen.ps1` **cannot execute in this environment.** Line 57
calls `[Convert]::ToHexString`, which exists only in .NET 5+ / PowerShell 7; the
only shell available here is Windows PowerShell 5.1.26100.9444 on .NET Framework,
and PowerShell 7 is not installed. The script carries no `#Requires -Version 7`,
so it fails at that line rather than refusing to start. An invocation was
attempted and returned exit code 1 with
`Method invocation failed because [System.Convert] does not contain a method
named 'ToHexString'`. This is a defect in the existing verifier's environment
assumptions, not a finding about this directory, and it is recorded as `N-3` in
`../V1_1_CANDIDATE_REVIEW.md` rather than repaired here — `review/task6/` is
another task's accepted artifact.

Because the script aborted only at that line, every assertion before it did run
without throwing: the 28-path protected inventory, the 28 baseline byte hashes,
and all 14 sidecars. To cover the remainder, the verifier's **entire** logic was
independently reimplemented and executed, reading `review/task1/protected-before.json`
and applying `schemas/HASH_CANONICALIZATION_v1.md` rules 1, 5, and 6:

| Verifier assertion | Result |
| --- | --- |
| Baseline entry count `= 28` | `PASS` |
| Protected inventory of `docs/`, `protocols/`, `schemas/`, `specs/` plus `FROZEN_HASHES.json{,.sha256}`, excluding `docs/README.md`, matches the baseline path set | `PASS` — no missing, no extra |
| Baseline byte hashes | `PASS` — 28/28 |
| Sidecar count `= 14` | `PASS` |
| Sidecar target hashes | `PASS` — 14/14 |
| Constitution content-hash field present | `PASS` |
| Constitution canonical self-hash recomputed with the hash value removed | `PASS` — `4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7` reproduced exactly |
| `FROZEN_HASHES.json` `release = v1.0`, `status = FROZEN` | `PASS` |
| `constitution_content_hash` binding | `PASS` |
| 7 embedded spec hash bindings | `PASS` — 7/7 |

The canonical self-hash step that the previous revision of this section recorded
as not re-executed is therefore now **independently verified**, not merely
inferred from byte-identity. The owner or reviewer should still run the verifier
itself, on PowerShell 7, to obtain its own `PASS` lines from the original script.

### 6.2 Packaging limitation — remedied at commit time

`MANIFEST.sha256` records SHA-256 over **LF** bytes. The first revision of this
directory had no `.gitattributes` pinning `eol=lf`, unlike
`../external-review-packet/`, because adding one was a packaging decision
reserved for a human: on a Windows checkout with `core.autocrlf=true`, a future
checkout could be rewritten with CRLF endings, invalidating every manifest entry
without any content change. Both AI reviews recorded it as an open limitation
rather than fixing it silently (`N-4`).

**Remedied.** On owner instruction, at the time this directory was first
committed, a `.gitattributes` was added here containing `*.md text eol=lf`,
`MANIFEST.sha256 text eol=lf`, and `.gitattributes text eol=lf`, mirroring the
external packet's existing file. The manifest was regenerated and re-verified
afterwards. The new file is packaging only: it changes no scientific content, no
recommendation, no review verdict, no source inventory, and no governance status,
and it is deliberately **not** listed in `MANIFEST.sha256`, whose contract covers
every Markdown file in this directory and nothing else.

Two qualifications are recorded rather than hidden. The `MANIFEST.sha256` rule is
redundant with the repository-root `*.sha256 -text` rule and is kept only for
parity with the precedent (`F-N4`). And a `.gitattributes` binds line endings
only from the commit that introduces it onward; it makes no retroactive claim
about bytes as they existed before that commit. The manifest values recorded here
were computed from LF bytes in the working tree and verified again after this
file was added.

The two review records **outside** this directory
(`../V1_1_CANDIDATE_REVIEW.md`, `../V1_1_FABLE_ADVERSARIAL_REVIEW.md`) are
deliberately left unprotected: no manifest covers them, so a CRLF checkout
changes nothing verifiable. Extending protection to that directory is the open
proposal recorded in §5 under `C-1`. Extending it there requires re-recording
every hash that references those files: three Markdown files directly under that
directory are currently CRLF in this working tree (`git ls-files --eol`), and one
of the affected values also appears in the manifest-covered external packet.

### 6.3 Corrections applied after independent AI review

`../V1_1_CANDIDATE_REVIEW.md` found two defects in the first revision of this
directory. Both were corrected in place before any human read it; the corrections
change no recommendation, no estimand, no decision, no threshold, and no
governance status, and `MANIFEST.sha256` was regenerated afterwards.

| ID | Defect in the first revision | Correction |
| --- | --- | --- |
| `R-1` | `HUMAN_DECISION_MATRIX.md` row `D-03` pointed a reviewer at `D-19` (the deferred `score >= 0.95` calibration question) for the consequence "forces a new block-length derivation". The bootstrap-migration decision is `D-20`, as `METHOD_CANDIDATE.md` §5 and this matrix's own dependency note both state | Reference corrected to `D-20` |
| `R-2` | `METHOD_CANDIDATE.md` §7 cited `I-1`–`I-9` as if the cited source used those labels. `../external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §6 is an unlabelled numbered list and contains no `I-n` token anywhere, so inline citations such as `I-7` were unresolvable in the source | §7 now declares that `I-n` denotes item `n` of that list and is introduced by this packet |

`R-1` is the reason the check table above now distinguishes decision-ID
*resolution* from decision-ID *referent correctness*. The original check verified
only that every cited ID matched some row, which `D-19` did; it could not detect
that the row named was the wrong one.

### 6.4 Corrections applied after independent adversarial review

`../V1_1_FABLE_ADVERSARIAL_REVIEW.md` (Claude, observed model ID
`claude-fable-5-1`) independently re-ran every check in §6 and §6.1, checked
`../V1_1_CANDIDATE_REVIEW.md` itself, and found three further defects. All three
were corrected in place; none changes a recommendation, an estimand, a
threshold, a decision, a frozen input, or a governance status, and
`MANIFEST.sha256` was regenerated afterwards. `PREREGISTRATION_TEMPLATE.md` is
still byte-identical to its first revision.

| ID | Defect | Correction |
| --- | --- | --- |
| `A-1` | `HUMAN_DECISION_MATRIX.md` §7 said `D-20` is triggered by the first acceptance among `D-03`, `D-08`, or `D-11`. `D-20` is scoped to bootstrap-backed clauses; PBO (`D-08`, `protocol_v1.yaml:234–241`, `METHOD_CANDIDATE.md` §4) uses no bootstrap. Only rows 5 (`D-03`) and 9 (`D-11`) are bootstrap-backed | Trigger list corrected to `D-03` or `D-11`, with the reason stated |
| `A-2` | This README's §6 "Working tree" row still described only the five-file directory after `../V1_1_CANDIDATE_REVIEW.md` had been added, contradicting §1 | Row and file-count statements updated. The accompanying claim that "every self-description re-verified true" did **not** hold: two were still false at the first commit, found later as `S2-3` (§6.5) |
| `A-3` | `METHOD_CANDIDATE.md` §3.3 `F-1` stated that the `raw_trial_count` fallback trigger "is undefined in frozen text". `docs/RESEARCH_CONSTITUTION.md` §9 line 106 is frozen trigger text: "If no frozen effective-count method exists, raw count is used." Neither the packet nor the first review cited it. Whether the method *named but not defined* at `protocol_v1.yaml:232` "exists" is undecided, so `D-16` stays `BLOCKING` | `F-1`, the §3.3 table, the §8 traceability row, `HUMAN_DECISION_MATRIX.md` `D-16`, and §4 `Q4` above now cite line 106 and state that its applicability is part of `D-16` |

Substantive questions raised by that review for the human statistician — in
particular the consequence of Lemma `L-1` for the row-12 pass event proposed in
`METHOD_CANDIDATE.md` §6.2 — are recorded in the review file and were
deliberately **not** written into the candidate, so that the candidate a
statistician judges is the one the reviews describe.

### 6.5 Third check, after the first commit

A third adversarial check (Claude, self-reported model ID `claude-fable-5-1`,
read-only) reviewed everything changed *after* the second review, including the
commit itself. It confirmed the mechanics — `C-1` is real, both published hashes
are correct, the `.gitattributes` works under a fresh `autocrlf=true` clone, the
manifest verifies against the committed blob bytes, and no frozen artifact was
touched — and found the write-up defective in six places. All six are repaired
above:

| ID | Defect | Repair |
| --- | --- | --- |
| `S1-2` | §5 claimed the other twenty values were "platform-independent" because they are LF on disk. False reasoning: fourteen of them carry no eol attribute, so they do **not** reproduce from a working-tree file on a fresh Windows clone — while the one labelled non-portable does | §5 now states what actually reproduces (index blobs) and what does not, with the attribute evidence |
| `S1-3` | `C-1` was presented as new to this directory when `../external-review-packet/README.md` carries the same value and the same characterization | §5 records the inheritance, the counting criterion, and which passes carried it |
| `S1-4` | §5 said *both* reviews had verified the twenty-one hashes. Only the adversarial review did | §5 attributes each check to the review that made it, with its section |
| `S1-5` | The stated reason for not normalizing the CRLF file was wrong, and "one file there is CRLF" undercounted — three are | §5 and §6.2 give the real reasons (authority and blast radius) and the correct count |
| `S2-3` | Two self-descriptions were false in the commit that contained them: §2 asserted "nothing was committed or pushed", and §6's working-tree row still said five files. §6.4 had declared every self-description re-verified | §2 and §6 corrected and time-scoped; a full sweep of every count and status claim was re-run afterwards |
| `S3-2` | §2 reported Constitution §16 as unsatisfied by this directory. §16 enumerates six code components (`RESEARCH_CONSTITUTION.md` lines 147–152); a Markdown-only directory contains none, so §16 is **not applicable** to it, and saying otherwise misreads the clause in the conservative direction | §2 now states non-applicability and preserves §16 for the code it does govern |

`S2-3` is the same defect class as `A-2`, recurring for the third time in this
document, and it is the reason the project's statistics agent carries an explicit
rule to re-sweep every self-description after *every* later edit, including edits
made at commit time. That rule was added on `main` in PR #3 (commit `1d716b3`,
merged as `4687c90`) **after** this branch was cut: the agent definition in this
branch's tree does not contain it. An earlier revision of this paragraph asserted
the rule as already present, which was true of `main` and false of the tree the
sentence sits in.

**The third check's report was not preserved, and its unrepaired findings are
lost (`V-01`).** An earlier revision of this paragraph said those findings "are
listed in that check's report". No such report exists in this repository. That
was verified, not assumed: no commit reachable from any ref adds such a file, and
the tokens `S1-1`, `S2-1`, `S2-2`, and `S3-1` appear in no blob in the entire
history except this README. Where the check's output went is not recorded
anywhere, and is not reconstructed here. The finding IDs
tabulated above are `S1-2` to `S1-5`, `S2-3`, and `S3-2`; the gaps at `S1-1`,
`S2-1`, `S2-2`, and `S3-1` are that check's remaining findings, which it chose
not to repair and whose content is now unrecoverable. They are not enumerated
here because no AI can reconstruct them without inventing them, and inventing
them would be worse than recording the loss.

What a reader should take from this: the six repairs above are the complete
record of that check, an unknown number of its findings — at least four, by the
numbering — were deliberately left unrepaired for reasons no longer available,
and the packet is therefore **not** accompanied by a full account of the known
defects in it. The remedy is preservation going forward, not reconstruction:
`§6.6` records its own check in full, in the repository, before the branch moved.
Owner decision, 2026-09-21, on the `V-01` blocker raised by the fourth check.

The first commit's message cannot be amended without a force-push, so its
repetition of the `S1-4` error is corrected here and in the follow-up commit
rather than rewritten.

### 6.6 Fourth check — independent different-model adjudication

A fourth read-only check was run after this branch was pushed: an adversarial
pass by Claude (observed model ID `claude-opus-5`), then an independent
adjudication of that pass by Claude (observed model ID `claude-fable-5-1`) under
the verification protocol added to the project's statistics agent in PR #3. The
adjudicating model is deliberately not the model that authored this directory or
wrote review (1), both of which observed `claude-opus-5`. Neither is human,
owner, or statistician acceptance, and neither moves any `D-nn`.

Repaired in this revision, all write-up only:

| ID | Defect | Repair |
| --- | --- | --- |
| `V-02` | §5 and the `S1-2` row said "fifteen of the twenty" carry no `text`, `eol`, or `-text` attribute. Fourteen do. Fifteen is the count across all twenty-one, which includes the one CRLF file §5 explicitly excludes from "the twenty": `20 − 2` (`-text`) `− 4` (`eol=lf`) `= 14`. Confirmed by `git check-attr` per path and by a fresh `core.autocrlf=true` clone materializing exactly fourteen as `w/crlf` | Both statements corrected |
| `V-04` | §6 subsections ran `6.1, 6.5, 6.2, 6.3, 6.4`; `§6.5` was inserted after `§6.1` in commit `e03b6fa` | `§6.5` moved after `§6.4`; its number and every cross-reference are unchanged |
| `V-05` | `C-1`'s discoverer was stated nowhere, and "five passes over two packets carried it" gave no counting criterion, so the number could not be audited | §5 now names the discoverer and states the criterion and the count |
| `N-A` | The header and §6.5 said the third check found five write-up defects; six were repaired, `S3-2` being recorded outside the table | Corrected to six; `S3-2` is now a table row |
| `N-B` | §6.5 said the statistics agent "now carries" the self-description rule. True of `main` after PR #3, false of this branch's tree, where the agent definition does not contain it | The sentence now states when the rule was added and that this branch predates it |
| `N-C` | `protocol_v1.yaml:27` — "One predeclared comparator is used for every eligibility, robustness, DSR/PBO, null, and lockbox comparison" — is the frozen clause that makes the benchmark leg common across trials and null draws. It underpins both the `L-1` argument in `D-08` and `F-Q1`/`D-14`, and is cited by no packet file and by neither review | Recorded here. The citation is **not** added to `METHOD_CANDIDATE.md` or the matrix: see the authority note below |

`V-01`, the blocker that check raised, was **closed by owner decision on
2026-09-21**: §6.5 pointed readers at a third-check report that exists nowhere in
this repository. The owner elected to record that the record was not preserved
rather than reconstruct it, and §6.5 now states the loss, identifies the missing
findings by their numbering gap, and says why they are not enumerated. The
underlying defect is not undone by this — an unknown number of that check's
findings remain unrepaired and unrecorded, and §6.5 says so plainly.

One item is recorded as **open, not repaired**:

- **`Q-SW` (QUESTION for the statistician).** `F-Q1`'s cancellation argument for
  row 12 additionally assumes the 500 null draws and the realized candidate are
  evaluated on the **same window**. Lines `134–140` do not state it. The
  adjudication verified the mathematics — type-7 quantiles are
  translation-equivariant, so under a shared `b` the event reduces exactly to a
  percentile gate on the candidate's own Sharpe, which is in effect what `I-12`
  forbids — and confirmed that rows 3–7 do **not** collapse.

**Authority note.** `V-03` in the adversarial pass — the `L-1` collapse of row 12
and the `D-14`/`D-08` asymmetry — is **not** a new finding: it is `F-Q1`
(`../V1_1_FABLE_ADVERSARIAL_REVIEW.md` lines 158–173), verified independently in
review (1) lines 246–250, and commit `4f65d2e` records the owner electing to
leave row 12 `PROPOSED` with the question standing so the statistician rules on
it. `V-06` — that the PBO `0.5` branch is reachable without ties for odd `N` — is
correct but already on record as `F-N3` (review (2), lines 205–209), and
`METHOD_CANDIDATE.md` §4.1's sentence is scoped to `N = 2`, where a tie is the
only route, so it is incomplete rather than wrong. Neither is carried into the
candidate, because the owner elected to freeze the candidate text as the reviews
describe it. For the same reason `N-C`'s citation is recorded here rather than
added to `METHOD_CANDIDATE.md` §2 or `HUMAN_DECISION_MATRIX.md` `D-08`/`D-14`,
although the `A-3` precedent would support a citation-only edit; whether to carry
it in is the owner's call, not an AI's.
