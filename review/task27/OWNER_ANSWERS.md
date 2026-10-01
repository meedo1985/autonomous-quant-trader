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
