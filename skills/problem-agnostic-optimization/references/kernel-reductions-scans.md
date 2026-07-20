# Reductions And Scans

Use this module for sums, means, norms, losses, min/max, argmin/argmax, normalization, cumsum, cumprod, and prefix transforms.

## Reduction Candidates

- Use warp/block reductions with minimal synchronization.
- Prefer row-local one-block kernels when row size permits.
- Vectorize reads and writeback.
- Use multi-block partial reductions only when one block cannot expose enough parallelism.
- Stabilize the numerical formulation before cross-target fanout.

## Scan Candidates

- Establish a library baseline for correctness.
- Test cooperative single-grid scan for fixed sizes.
- Test a fixed-tile two-pass scan when official sizes are exact multiples.
- Use decoupled lookback only when its residency assumptions hold.
- Add graph reuse only when launch overhead is proven material.

## Typical Traps

- Fewer atomics can lose after adding a launch or temporary-buffer traffic.
- Grid caps can reduce atomic pressure but lose needed parallelism.
- Raw-sum variance formulas may fail tighter correctness lanes.
- Generic scans can lose to exact-size dispatch.
- Lookback can deadlock or transfer poorly when resident-block assumptions are wrong.
