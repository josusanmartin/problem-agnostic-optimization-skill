# Problem Families

Use this reference after the contract is known. Pick the target family before writing candidates.

## Stateful Stochastic Policy / Controller

Examples: simulation-scored strategies, controllers, agents, game bots, auction policies, routing policies, schedulers under random demand, online decision systems, and other stateful action functions.

Use this family before CPU/GPU primitive work when the submitted artifact is mainly judged by policy quality under randomized scenarios, hidden seeds, or latent regimes.

First candidates:

- Define matched `smoke`, `train`, `validation`, `holdout`, and `adversarial` scenario sets.
- Compare candidate and parent on common random inputs when possible.
- Record mean, median, SEM, `p05`/`p95`, worst decile, win rate versus parent, invalid-action rate, and constraint margins.
- Break score into reward, adversarial loss, opportunity cost, tail loss, resource cost, and accumulated-state risk when the simulator exposes enough data.
- Start from one small mechanism family: regime estimator, adaptive margin, event classifier, exposure controller, participation controller, competitor/outside-option tracker, cooldown/decay, or tail-risk guard.
- Run parameter search only after the mechanism and validation gate are defined.

Typical traps:

- Train-set wins that vanish on validation or holdout.
- Leaderboard wins from one noisy sample with no same-seed local support.
- Mean-score gains that hide catastrophic worst-decile or invalid-action regressions.
- Parameter sweeps that find a sharp spike instead of a broad plateau.
- Adding state and constants faster than ablations can justify them.

Read `stochastic-policy-search.md` before optimizing this family.

## Elementwise And Streaming

Examples: activations, scalar transforms, vector add/mul, quantized decode/store.

First candidates:

- Exact-shape dispatch for fixed benchmark sizes.
- Packetized IO: `float4`, `uint4`, `int4`, vector intrinsics, or natural SIMD width.
- Exact-grid launches with no grid-stride loop on official sizes.
- Separate full blocks from tail handling.
- Approximate math only after tolerance and edge-case checks.
- Graph or launch reuse only as an isolated candidate.

Typical traps:

- Streaming cache hints can win or lose; measure normal IO against streaming/non-temporal IO.
- Register-caching can reduce recompute but regress from register pressure.
- Same-file reruns can beat a leaderboard through variance; label them as variance.

## Reductions, Norms, And Losses

Examples: MSE, L1/L2/frobenius norms, sums, means, min/max, argmin/argmax, cosine similarity, batch/layer/RMS norm.

First candidates:

- Warp/block reductions with minimal synchronization.
- Row-local one-block kernels when row size permits.
- Vectorized read and writeback paths.
- Multi-block partial reductions only when one block cannot expose enough parallelism.
- Stable numerical formulation before cross-GPU fanout.

Typical traps:

- Fewer atomics can lose if it adds a kernel launch or temp-buffer traffic.
- Grid caps can reduce atomic pressure but lose needed parallelism.
- Raw-sum variance formulas may fail tighter lanes; centered variance may be needed.

## Scans

Examples: cumsum, cumprod, running sums, prefix transforms.

First candidates:

- Library/CUB baseline for correctness.
- Cooperative single-grid scan for fixed sizes.
- Fixed-tile two-pass scan when official sizes are exact multiples.
- Decoupled lookback when cooperative sync is the bottleneck.
- Graph wrapper only if launch overhead is proven material.

Typical traps:

- Generic scans often lose to exact-N dispatch.
- Lookback can deadlock or transfer poorly if resident block assumptions are wrong.
- Graph setup/source-layout can erase the intended launch win.

## Pooling, Stencils, And Convolution

Examples: avg/max pool 1D/2D/3D, blur, edge detect, conv1D/2D/3D.

First candidates:

- Split interior from boundary so the hot path has no bounds checks.
- Use shared memory/LDS only when reuse exceeds synchronization and bank-conflict cost.
- Route by exact kernel size, stride, padding, dimension, and layout.
- Consider separable, FFT, cuDNN, CK, AITER, or other library paths before direct convolution on large kernels.

Typical traps:

- Direct O(N*K) kernels are often noncompetitive for large filters.
- Shared-memory staging can lose when reuse is low or bank conflicts dominate.
- A path that wins one kernel size can lose the geomean if applied broadly.

## GEMM And Matrix Composition

Examples: GEMM, GEMV, matrix-vector, batched matmul, triangular/symmetric matmul, GEMM+activation, attention matmul, quantized GEMM.

First candidates:

- Flatten the math to GEMM/GEMV/TRMM when possible.
- Use cuBLASLt, cuBLAS, cuDNN, cuFFT, CUTLASS, CK, AITER, or Triton before hand-written direct code.
- Cache descriptors, handles, workspaces, and algorithm choices.
- Fuse epilogues through library support or vectorized post-pass.
- Choose compute precision from tolerance: exact FP32, residual TF32/BF16, or approximate routes.

Typical traps:

- Special BLAS calls like symmetric/triangular can be semantically wrong if the input only approximately satisfies the structure.
- Success on one local GPU or checker does not prove correctness or speed on another target device, especially when fast math modes differ.
- A library heuristic can be shape-specific; keep per-shape policy rather than a single global heuristic.

## Histogram And Atomic Aggregation

Examples: histograms, counting, sparse accumulation, binning, graph updates.

First candidates:

- Inspect input distribution and value representation.
- Replace expensive conversions when the input contract gives integer-valued floats or bounded ranges.
- Sweep per-CTA work, bin privatization, shared/global atomics, and partial-reduce layouts.
- Use exact grids when official sizes are fixed.

Typical traps:

- Removing final global atomics can lose from temp-buffer writes and a reduce kernel.
- CUB/library paths are strong baselines but not always first-place.
- Branches that skip zero bins can be wasted when every bin is effectively nonzero.

## Quantized Formats

Examples: FP4/FP6/FP8/NVFP/MXFP dequantize, block-scaled GEMM, quantized MoE.

First candidates:

- Verify tensor layout, scale layout, swizzling, and packing before optimizing.
- Build exhaustive or CPU bit-checks for decode.
- Use vectorized byte/word loads and stores.
- Use hardware matrix instructions or library paths for GEMM when available.

Typical traps:

- Platform/reference failures can masquerade as candidate failures.
- Public docs can disagree with runner semantics; sample/check evidence wins.
- Re-swizzling already-swizzled scale tensors breaks correctness.

## Attention, MLA, And MoE

Examples: decode attention, MLA, MoE routing, paged KV cache.

First candidates:

- Split by exact batch, sequence length, head count, page size, expert count, and route mode.
- Treat library/kernel modes as separate algorithms.
- Sweep page size, split count, persistence, queue count, and metadata overhead.
- Check whether initialization is required for every timed call or only for warmup under the contract.

Typical traps:

- A setting that is correct for long sequence can produce zeros or garbage for short sequence.
- Very large pages or tiles can trigger leaderboard timeouts even if microbench is fast.
- Benchmark geomean and ranked geomean can differ; promote on ranked/authoritative score.

## Runtime And System Overhead

Examples: process startup, allocation, graph setup, dynamic dispatch, I/O, framework calls, synchronization.

First candidates:

- Cache allocations, descriptors, handles, and graphs when same-pointer or same-shape calls repeat.
- Remove unnecessary copies and buffered IO.
- Use direct syscalls or lower-level APIs when runtime overhead is included in timing.
- Precompute legal metadata offline or during unscored setup if the contract allows.

Typical traps:

- Host caching can regress hot path timing if it adds branches or state checks.
- Framework routes can include hidden synchronization.
- Startup/exit overhead can dominate sub-10ms CPU challenges.

## VLIW, Schedulers, And Fixed-Resource Machines

Examples: VLIW cycle-count searches, packet schedulers, DSP kernels, compiler instruction scheduling, custom accelerators, software pipelined kernels.

First candidates:

- Build resource-floor models before schedule sweeps.
- Count constrained engines separately: vector, scalar, memory, branch/control, gather, shuffle, store, or special units.
- Compare actual schedule to the max resource floor.
- Audit final-tail resource usage, not just total counts.
- Use contract-aware omission only when output semantics prove state is unobserved.
- Try resource rebalance only when the destination resource has measured slack.
- Compose mechanisms only after each resource trade is characterized.

Typical traps:

- A lower slot floor can lose from dependencies, scratch lifetimes, or barriers.
- Moving work from a saturated engine to an already-full engine is not a speedup.
- Schedule-only search cannot beat a lower bound that already exceeds the target.
- Combining knobs before measuring component effects produces ambiguous data.
