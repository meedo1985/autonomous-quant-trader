# Owner answers to the Task 27 design questions

Date: 2026-09-29. Asked by Claude Opus 5.5 from `DESIGN.md` section 4;
question and option texts as asked, answers the owner's.

- **Q27-1.** "You pressed HALT during a fall, and later you end the HALT
  while your equity is still more than 20% below its peak. What should the
  loss stop do?" — **"Wait for a new fall (Recommended)"**: "Ending a HALT
  means you have looked and decided. The stop does not fire again at once; it
  fires on the next 20% fall from the new level."
- **Q27-2.** "After the loss stop has sold everything, your account is almost
  all cash, so it may never climb back above 80% of the old peak. How should
  the stop re-arm?" — **"Reset when you restart (Recommended)"**: "When you
  restart trading, the peak is reset to your equity at that moment, so the
  20% stop protects from there."
- **Q27-3.** "If Binance itself is missing an hour of prices (it has happened
  during exchange outages), the live price store stops. What then?" — **"You
  acknowledge it (Recommended)"**: "You sign a short record saying the gap is
  real; the store then continues after it, with the gap recorded, never
  filled."

## Effect on Task 27

Q27-1 and Q27-2 together: when the owner ends a HALT (the §14 override), the
loss-stop peak is reset to equity at that moment and the stop re-arms from
there. Q27-3: a signed, committed gap record lets the live store continue
after a real Binance gap; the gap stays recorded and is never filled. None of
this changes the adopted `L-03` 20% bound.

## T27-01 (asked 2026-09-30, from `LOCAL_REPORT.md` part b1)

Asked by Claude Opus 5.5 in a Claude Code session: "after a crash, the app
can resume in HALT, FLATTEN or FREEZE while an incident is still open. None
of those modes can buy, and trading can only restart after you close every
incident and reconciliation passes (section 14). Should such a start be
allowed?" — **"Allow it (Recommended)"**: "The app restarts in
HALT/FLATTEN/FREEZE with the incident still open. A resumed FLATTEN keeps
selling, so protection continues after a crash. A start that would be
RUNNING with an open incident is still refused."

Effect: the part b1 behaviour of `startup_check(resuming=...)` stands. This
answer changes no frozen file and no loss bound.

## Q27-3 follow-up: how a gap record is signed (asked 2026-10-01, Astra A27-5)

Asked by Claude Opus 5.5: "when Binance has a real gap, you 'sign' a record
so the live price store can continue. Right now the signature is your name
and a statement saved in the store file, which anyone with access to the
file could edit. How strong should it be?" — **"Name + statement
(Recommended)"**: "Keep it as now: the app checks the record is complete and
in the right place, but the file itself can be edited. Simple, enough for
paper trading; can be strengthened before real money."

Effect: "signed" in Q27-3 means the owner's name and statement in the gap
record, checked in full on every read. The words "signed, committed" in the
"Effect on Task 27" section above were the AI's paraphrase; this answer
settles them. Tamper evidence for the store stays open (T27-10) and is to be
revisited before any real-money use.

## A27-23: the loss stop in a health-breach hour (asked 2026-10-01)

Asked by Claude Opus 5.5: "in an hour where a health check fails (clock
skew, slow loop, stale data), nothing is ever traded. But if that hour's
closed price shows a fall of more than 20% from the peak, what should the
20% loss stop do?" — **"Fire as usual (Recommended)"**: "Record the breach
and switch to FLATTEN now; the first selling step waits for a healthy hour.
Same answer whether or not the app restarts. Safer side: a fall is never
ignored."

Effect: the part b2 behaviour stands (L-03 valued and fired in a
health-breach hour; no order that hour). No loss bound changes.
