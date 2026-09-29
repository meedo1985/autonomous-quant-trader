# Owner answers to roadmap 2 questions Q-A to Q-D

Date: 2026-09-29. Given by the repository owner in a Claude Code session with
Claude Opus 5.5, which wrote this record. The owner's words are quoted
verbatim; the AI adds no assessment on his behalf.

The owner answered in one message:

> a: i dont know still dont rent or any servers
> b:it must be
> c:wait for resaerch but dont want it too long
> d:yes aproved

## Q-A: live public price data over the network

The first answer tied Q-A to renting a server. The AI explained that Q-A does
not depend on a server, and asked again: "May the app (on your PC for now, a
server later) read Binance's public live price feed? No account, no key,
read-only … The AI itself would never make these calls."

**Answer:** "Yes, allow it (Recommended)": "The app may read public live
prices. Needed for Task 26 and for any forward paper or shadow later."

Scope: the app, not the AI, reads Binance's public market-data API with no
credential. This does not change Constitution §15 for the research AI.

## Q-B: the Telegram bot token

**Answer:** "it must be". Read as approval: a Telegram bot token may exist as
a credential, stored only on the machine running the app, in the OS
credential store (D-8), never in the repository, a log, a report, CI, or an
AI's context (§28). The owner creates the bot and the token himself.

## Q-C: which strategy runs forward paper

**Answer:** "wait for resaerch but dont want it too long". Task 29 (forward
paper) therefore waits for a strategy from research cycle `C1`. The AI told
the owner that `C1` is blocked on `D-16` and `D-17`, which need a
statistician's review under the frozen rules, so "not too long" depends on
that review and cannot be promised by the AI.

## Q-D: order of work

**Answer:** "yes aproved". Tasks 26, 27, 28 and 30 are authorized, in that
order, under the conventions of roadmap 1 section 1 (section 16 review and
the owner's behavioural review before any protected merge; merge only on the
owner's instruction). Tasks 29, 31 and 32 are not authorized.

## Not authorized by these answers

Any real order, trading key, `L-01` increase, start of `C1`, statistical
binding, change to a frozen file, or renting a server on the owner's behalf.
Task 30 is written without a server; the owner rents one when he chooses.
