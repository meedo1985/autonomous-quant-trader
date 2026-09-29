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
