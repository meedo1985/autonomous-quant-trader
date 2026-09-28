# Owner answers to T23-Q1 and T23-Q2

Date: 2026-09-27.

## The question as asked (by Claude Opus 5.5)

"Should the AI also choose the two Task 23 settings (FLATTEN: sell at most
50% per step, accept down to 1% below the price; account check must match
exactly)?"

## The owner's answer

Selected: **"Yes, use them"**. The option read: "Adopt the proposed values;
they are recorded as your choice and can be changed later."

## Effect

- **T23-Q1:** `FlattenBounds(max_step_fraction=0.5, max_slippage_bps=100)`.
- **T23-Q2:** the reconciliation tolerance is 0 in every asset, on the
  simulator. To be revisited before shadow.
- Both are marked `[OWNER-SET]` in the deployment protocol draft (sections 3
  and 6). The draft as a whole is still not adopted. The code keeps no
  defaults; the loop (Task 24) passes these values in.
