# Task 23 owner behavioural review (Constitution section 16)

Date: 2026-09-28. Reviewed state: `c0e6051` on `task23-safety` (PR #29).

Conducted by Claude Opus 5.5 as a guided walkthrough with four yes/no
questions, the same form as Tasks 17, 21 and 22. The questions below are
quoted as asked; the answers are the owner's selections.

1. **HALT.** "When you press HALT, or the 20% loss stop fires, the system
   places no new orders at all. It keeps whatever coins it holds and waits
   for you. To restart, you must give a written reason, a fresh account check
   and an explicit 'resume'. Is that what you want?" — **Yes**
2. **FLATTEN.** "Emergency sell, only when you press it: it sells at most
   half of what's left each hour, never below 1% under the market price. If
   any alarm fires during FLATTEN, it stops selling and goes to HALT. Is that
   what you want?" — **Yes**
3. **FREEZE.** "If the system is unsure whether an order went through, or its
   account records don't match the exchange, it freezes and does nothing,
   even if prices move. It only unfreezes after a fresh account check that
   looks up every uncertain order, and then goes to HALT, not back to
   trading. Is that what you want?" — **Yes**
4. **Startup and alarms.** "The system refuses to start if its records don't
   match the exchange. Every alarm is logged and acted on, even if its clock
   stamp is a little late. Is that what you want?" — **Yes**

## Review substitution

When Codex was at its usage limit, the owner chose Claude Fable 5.1 instead
of the exact GPT-6 Astra review ("use Fable now", 2026-09-28), after being
told Fable is not an exact-Astra review. Fable reviewed `752f158` (FIX,
`FABLE_REVIEW_752F158.md`) and re-reviewed the repairs at `3b9237e`
(ACCEPT, `FABLE_REREVIEW_3B9237E.md`). The F23R-3 guard and documentation in
`c0e6051` were not re-reviewed.

This review covers behaviour, not code. It authorizes no trading, no
credentials and no deployment. Merge happens only on the owner's instruction.
