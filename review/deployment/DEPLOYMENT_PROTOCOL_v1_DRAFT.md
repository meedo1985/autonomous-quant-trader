# Deployment protocol v1 — DRAFT for owner review

**Status:** `DRAFT — NOT ACTIVATED — NOT FROZEN — NOT A GOVERNANCE ARTIFACT`
**Prepared:** 2026-09-26 by Claude Opus 5.5 (`claude-opus-5-5`), coding AI, as
roadmap Task 20 (`review/roadmap/ROADMAP_PROPOSAL.md`, approved by the owner).
**Required by:** Constitution §19: "Separate deployment protocol required
before shadow."

## 0. What this is and what it is not

This is a **proposal**. Constitution §4 says research or coding AI "may propose
but not author/merge/activate/self-approve amendments", and activation needs an
owner-of-record signed, dated commit. Nothing here is in force until the owner
adopts it through that process. Merging this file into the repository does not
activate it.

It lives under `review/deployment/`, not `protocols/`, because `protocols/` is
a frozen path whose file inventory is verified exactly. (The roadmap said
`protocols/drafts/`; that location would have broken the frozen-inventory
check. See `review/task20/REVIEW_NOTES.md`, T20-01.)

It authorizes nothing: no key, no order, no shadow, no canary. Reaching any
stage below also requires every earlier gate in the Constitution, which this
document restates but cannot relax.

### How to read the markers

- **[FROZEN §<n>]** / **[FROZEN protocol:<line>]**: restates frozen text. The
  frozen text governs where they differ.
- **[ADOPTED L-<nn>]**: a loss bound the owner adopted in their own hand in
  section 6 of `review/pre-deployment/LOSS_BOUND_DEFAULTS.md` on 2026-09-26
  (record `review/pre-deployment/LOSS_BOUNDS_ADOPTION_RECORD.md`). It is the
  owner's self-imposed bound, not frozen text, and this draft is still not
  adopted as a whole.
- **[OPEN]**: a value or choice no frozen text or proposal supplies. The owner
  must decide it before activation. The AI has deliberately not proposed a
  number where none exists in the sources, so an invented default cannot pass
  as a considered one.

## 1. Inputs this draft cannot supply

Activation is blocked until each of these exists:

| Input | Status on 2026-09-26 | Source |
|---|---|---|
| Owner's §25 acknowledgment, signed and dated | Signed 2026-09-26 (`review/pre-deployment/S25_SIGNATURE_RECORD.md`) | [FROZEN §25]; `review/pre-deployment/OWNER_ACKNOWLEDGMENT_S25.md` |
| `L-01` deployable amount | `0` for now; to be revisited before canary | [ADOPTED L-01] |
| `L-02` forward paper period | ≥ 240 effective decisions, no real capital deployed | [ADOPTED L-02] |
| `L-03` absolute live stop | 20% from peak live equity | [ADOPTED L-03] |
| `L-04` risk-increase rule | Written record + no increase below peak | [ADOPTED L-04] |
| Different-model + human review of governor, executor state machine, protocol-enforcement logic | AI reviewer named: GPT-6 Astra (roadmap Q2, `review/roadmap/OWNER_ANSWER_Q2.md`); the human PR review is recorded separately before each protected merge | [FROZEN §16] |
| Governor, executor, HALT/FLATTEN/FREEZE, paper loop | Not written (roadmap Tasks 21-25) | roadmap |
| A promoted candidate, or the deployable baseline | No cycle has started; verdict `KEEP_BLOCKED` | [FROZEN §11, §13] |
| An external alert channel | None exists; each needs a credential and network path | §5 below |

## 2. Stages

The Constitution names paper, shadow, and canary gates ([FROZEN §11]: "all
live-safety, paper, reconciliation, canary, owner, and cooling-off gates still
apply") but does not define them. **Proposed definitions:**

| Stage | Market data | Orders | Capital at risk |
|---|---|---|---|
| **Replay** | Historical, already known | Sent to the simulated exchange (Task 18) only | None |
| **Forward paper** | Live, as it arrives | Sent to the simulated exchange (Task 18) only | None |
| **Shadow** | Live | Computed, authorized, and logged, but **never sent** | None |
| **Canary** | Live | Sent to Binance Spot | At most `L-01` [ADOPTED L-01] |

Replay is a test of the machinery only. **Only forward paper counts toward
`L-02`**: `L-02` is defined as forward evidence, data that did not exist when
the strategy was chosen, and a historical replay cannot supply that (review
finding R-2).

There is no stage beyond canary in this draft. Increasing capital beyond the
canary amount is a risk increase under §6.

### 2.1 Entry to replay or forward paper

1. The full path runs in the order [FROZEN §19] "predictor → governor →
   executor → exchange", with the simulator as the exchange.
2. Monitoring (Task 19) is configured with at least one sink [FROZEN §19
   "Alerting before shadow"; applied here one stage early].
3. §3 startup reconciliation passes and no §4 `REFUSE_START` condition holds.

### 2.2 Entry to shadow

1. Every §1 input except `L-01` exists and is adopted.
2. **Forward paper** (not replay) has run for the `L-02` period
   [ADOPTED L-02] and ended with no open incident.
3. An alert channel that reaches the owner outside the machine running the
   loop exists and has been tested end to end (§5) [OPEN: which channel].
4. This protocol has been activated by the owner under §4.

### 2.3 Entry to canary

1. Everything in 2.2, plus shadow has run for [OPEN: duration or decision
   count] with no open incident.
2. The key lifecycle rehearsal of §8 is complete [FROZEN §28:
   "Rotation/revocation rehearsal and permission/IP checks required before
   canary; withdrawals disabled"].
3. `L-01` is adopted and non-zero, and the owner has signed §25 clause C-8
   ("only fully-loss-acceptable capital may be deployed").
4. The Binance account holds no more than the `L-01` amount of quote asset
   plus fees [OPEN: fee headroom].

## 3. Startup reconciliation

Required at every start [FROZEN §19 "Startup reconciliation required"]:

1. Read the exchange's balances and open orders.
2. Read the local state: last known balances, every order the executor has
   recorded, and every unexpired authorization.
3. Every local order must resolve, by query on its `clientOrderId`, to a
   terminal exchange state that matches the local record. An order the
   exchange reports as unknown follows §7.
4. **In the other direction**, every open order on the exchange must match a
   local order record. An exchange order with no local record is an incident
   and a `REFUSE_START`, whatever the balances show: it can fill later outside
   the executor's tracked state (review finding R-1).
5. Free **and locked** balances must match the local record within
   [OPEN: tolerance, in base and quote units]; every locked amount must be
   explained by a matched open order. Any difference is an incident
   [FROZEN §0: "reconciliation mismatch ... unexplained exposure"].
6. The result, pass or fail with every difference, is written to the
   operational log (Task 19).

A failed reconciliation is `REFUSE_START` and opens an incident.

## 4. `REFUSE_START` conditions

The loop must not start if any of these holds. Each is logged.

1. Any configured hash differs from its frozen value: Constitution content
   hash, protocol file hash, cost model hash, and the deployed code identity
   [FROZEN §19: "Config/hash mismatch → REFUSE_START"].
2. Startup reconciliation fails (§3).
3. No alert sink is configured, or the external channel of §5 has not passed
   its test within [OPEN: interval] [FROZEN §19].
4. An incident is open [FROZEN §14: "Trading resumes only after incident
   closure plus successful reconciliation"].
5. The system is in FREEZE, or in HALT without a completed HALT exit (§6).
6. The exchange adapter is not the one the stage allows (simulator for paper;
   no order-sending adapter at all for shadow).
7. A production trading key is present anywhere other than the executor
   identity [FROZEN §28: "Production keys only under executor identity"].
   Other credentials, such as an alert channel's, are held as §8 describes
   and never in the repository, logs or reports [FROZEN §28: "No secrets in
   repo/artifacts/logs/reports/screenshots/LLM context/CI"].
8. The operational log fails hash-chain verification (Task 19 ledger).
9. A health check (Task 19) is in breach at startup: stale data, clock skew,
   or loop lag, at thresholds [OPEN: each threshold and its severity].

## 5. Alerting

[FROZEN §19: "Alerting before shadow."]

- **Local sinks** (built, Task 19): the standard output stream and the
  hash-chained operational log. Every CRITICAL event reaches every sink; a
  router with no sink refuses to start.
- **External channel** [OPEN]: at least one channel that reaches the owner
  when the machine running the loop is down or unattended (for example email,
  phone, or a messaging service). None is built: each needs a credential and
  an outbound network path, both forbidden in Milestone 0.1. Its credential
  falls under §8.
- **Must alert CRITICAL:** any entry to HALT, FLATTEN, or FREEZE; any
  `REFUSE_START`; any reconciliation mismatch; any ambiguous order reaching
  `UNKNOWN`; any credential anomaly; any `L-03` breach [ADOPTED L-03].
- **Channel test:** before shadow and then every [OPEN: interval], a test
  alert must be received and acknowledged by the owner, and the test recorded.

## 6. HALT, FLATTEN, FREEZE, and incidents

[FROZEN §22]: "HALT adds no risk. FLATTEN is bounded de-risking. FREEZE makes
no autonomous risk change. State transitions logged; exit FREEZE only after
reconciliation."

| State | Entered on | Allowed | Exit |
|---|---|---|---|
| **HALT** | Any incident (**proposed**; §0 defines an incident but does not say it causes HALT); `L-03` breach [ADOPTED L-03]; owner command | No new risk [FROZEN §22] | The HALT exit procedure below [FROZEN §14] |
| **FLATTEN** | Owner command, or [OPEN: automatic triggers] | Bounded de-risking [FROZEN §22], within [OPEN: bounds] | Zero exposure, then HALT (**proposed**) |
| **FREEZE** | An ambiguous order reaching `UNKNOWN` [FROZEN §21]; a reconciliation failure while running (**proposed**) | No autonomous risk change [FROZEN §22] | Successful reconciliation [FROZEN §22] |

Risk reductions are immediate and never gated [FROZEN §14: "Risk reductions
are immediate: reduce capital, tighten limits, kill, HALT, FREEZE";
FROZEN protocol:306 `risk_decrease_immediate: true`].

### HALT exit (override)

All five are required, and each is recorded in the incident record
[FROZEN §14]:

1. a written incident record;
2. an identified or bounded cause;
3. a successful reconciliation (§3);
4. explicit owner action;
5. a timestamp.

Trading resumes only after incident closure plus successful reconciliation
[FROZEN §14]. Safety-clause amendments cannot be proposed or activated during
an open incident or post-HALT cooling-off [FROZEN §4]; the length of that
cooling-off is [OPEN].

## 7. Ambiguous orders

[FROZEN §21]: "Timeout → query clientOrderId. NOT_FOUND → wait protocol delay
→ query again. Confirmed absence may resend only with same clientOrderId and
unexpired authorization; otherwise get new authorization. UNKNOWN →
reconcile/FREEZE."

- **The "protocol delay" is not set anywhere in the frozen protocol.** It is
  [OPEN: delay, and how many NOT_FOUND answers count as confirmed absence].
- Before relying on the venue to reject a repeated `clientOrderId`, verify
  Binance's current behavior against its official documentation (Task 18
  finding T18-04). The simulator never fills a repeated id twice; the real
  venue's rule must be confirmed, not assumed.

## 8. Key lifecycle

[FROZEN §28]: "No secrets in repo/artifacts/logs/reports/screenshots/LLM
context/CI. Production keys only under executor identity. Rotation/revocation
rehearsal and permission/IP checks required before canary; withdrawals
disabled." [FROZEN §2]: no withdrawals, margin, futures, or leverage.

Before canary, each of these is performed by the owner and recorded, with no
secret in the record:

1. Create a Binance API key with Spot trading only; withdrawals, margin, and
   futures disabled on the key.
2. Restrict the key to the executor's IP address(es) [OPEN: address].
3. Store the key only where the executor identity reads it [OPEN: mechanism].
   It never enters the repository, a log, a report, a screenshot, CI, or an
   AI's context.
4. **Rehearse rotation:** create a replacement key, switch the executor to it,
   confirm it works, revoke the old key, and confirm the old key is refused.
5. **Rehearse revocation:** revoke the active key and confirm the executor
   fails closed (`REFUSE_START` or HALT), not open.
6. Confirm from the account settings that the key cannot withdraw.

A key found anywhere else, or used from an unexpected address, is a credential
anomaly: an incident [FROZEN §0].

## 9. Change control and cooling-off

- Risk increases require formal review and cooling-off [FROZEN §14], at least
  72 hours [FROZEN §4; FROZEN protocol:303-304], and only at 00:00 UTC with 24
  hours since the last increase [FROZEN protocol:56-58].
- Safety-amendment activation delay: at least 72 hours [FROZEN §4; FROZEN
  protocol:305].
- `L-04` [ADOPTED L-04]: a written record for every increase, and no increase while
  equity is below its peak.
- Moving from shadow to canary, and any increase of the canary amount, is a
  risk increase.

## 10. Rollback

1. Returning from shadow to forward paper, or from paper to replay, is
   immediate: neither sends orders.
2. **Returning from canary** starts from HALT, because orders already sent to
   Binance can still fill after the order-sending adapter is removed (review
   finding R-3). In order: (a) enter HALT, which adds no risk
   [FROZEN §22]; (b) resolve every outstanding order through its
   `clientOrderId` (§7), cancelling any still open; (c) decide what happens
   to the live position that remains: hold it under HALT, or FLATTEN it
   [OPEN: which, or who decides at the time]; (d) reconcile (§3); (e) only
   then remove the order-sending adapter. Changing the stage label alone is
   not a risk reduction.
3. Rolling back deployed code or configuration is done from HALT: enter HALT,
   deploy the previous recorded code identity, run startup reconciliation, and
   pass every §4 condition before leaving HALT.
4. A rollback is recorded in the operational log with the code identities
   before and after.

## 11. Open values the owner must set before activation

| Where | Value |
|---|---|
| §2.2 | External alert channel |
| §2.3 | Shadow duration or decision count before canary; fee headroom |
| §3 | Reconciliation tolerance |
| §4, §5 | Channel test interval; health-check thresholds and severities |
| §6 | Automatic FLATTEN triggers and bounds; post-HALT cooling-off length |
| §10 | Hold or FLATTEN the remaining live position when leaving canary |
| §7 | NOT_FOUND delay and confirmed-absence rule |
| §8 | Executor IP address(es); key storage mechanism |

The §1 inputs `L-01`–`L-04`, the §25 signature and the §16 AI reviewer were
settled by the owner on 2026-09-26; `L-01` stays `0` until the owner revisits
it before canary.

## 12. Activation

Only the owner of record can activate this protocol, by the §4 process:
version bump, written rationale, a signed and dated commit, and preserved
history. The AI cannot activate, merge as activation, or self-approve it
[FROZEN §4].
