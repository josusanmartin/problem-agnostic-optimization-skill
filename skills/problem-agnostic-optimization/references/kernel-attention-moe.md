# Attention And Expert Kernels

Use this module for attention decode, MLA, MoE routing, paged KV caches, and expert dispatch or aggregation.

## First Candidates

- Split by exact batch, sequence length, head count, page size, expert count, and route mode.
- Treat library and kernel modes as separate algorithms.
- Treat persistent and non-persistent execution as different algorithms and validate each scored shape.
- Sweep page size, split count, persistence, queue count, and metadata overhead within a written budget.
- Model how page size, tile size, and split count move pressure among metadata, atomics, memory bandwidth, and compute.
- Verify whether initialization is required for every timed call or only for warmup under the contract.
- Record environment variables that alter the measured route.

## Typical Traps

- A route correct for long sequences can produce zeros or garbage for short sequences.
- Very large pages or tiles can trigger timeouts even when a microbenchmark is fast.
- Skipping zero/fill after warmup is valid only when the contract proves every relevant buffer is overwritten.
- Local and ranked aggregates can differ; promote only on the authoritative score.
