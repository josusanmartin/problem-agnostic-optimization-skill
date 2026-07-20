# Histogram And Atomic Aggregation

Use this module for histograms, counting, sparse accumulation, binning, and graph or index updates dominated by atomics.

## First Candidates

- Inspect input distribution, key range, and value representation.
- Replace expensive conversions only when the input contract proves a bounded or integer-valued representation.
- Sweep per-block work, bin privatization, shared/global atomics, and partial-reduce layouts.
- Use exact grids when official sizes are fixed.

## Typical Traps

- Removing final global atomics can lose through temporary-buffer writes and a reduction launch.
- Library paths are strong baselines but not automatically the frontier.
- Branches that skip zero bins waste work when nearly every bin is nonzero.
