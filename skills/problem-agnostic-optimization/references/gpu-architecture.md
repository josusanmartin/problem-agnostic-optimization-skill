# GPU Optimization Reference

Use this reference for CUDA, HIP/ROCm, Triton, GPU challenge kernels, GPU library paths, and leaderboard GPU work. Keep guidance architecture-agnostic by default; discover target facts and prove them with measurements. Route end-to-end request services separately.

## Contents

- GPU search and execution topology
- Device discovery and backend portability
- Precision, profiling, and cross-GPU transfer

## GPU Search Rules

- Start with the contract, not the kernel.
- Preserve the best like a production baseline.
- Make one candidate for one hypothesis.
- Treat shapes, dtypes, layouts, and target devices as separate problems until evidence says they share a bottleneck.
- Prefer exact-shape dispatch for fixed hidden cases.
- If the gap is 2x or more, stop micro-optimizing and change primitive, representation, route, or specialization level.
- Classify every speedup before trusting it.
- Use competitor clues as hypotheses, not truth.
- Separate speed from stability: benchmark, ranked, secret, rerun variance, and statefulness can differ.
- Keep only enough active state to avoid duplicate candidates and protect the best; persistent logging is optional.
- After every win, rewrite the bottleneck map.

## General GPU Patterns

- Test naturally aligned packetized IO such as `float4`, `uint4`, or `int4`, plus exact grids for streaming kernels.
- Keep tail handling outside the hot path when the contract allows it.
- For reductions, compare atomics, partial reductions, subgroup/block reductions, vendor libraries, and graph wrappers empirically.
- For GEMM, convolution, FFT, scan, sort, and attention-like primitives, establish relevant vendor-library or generated-kernel baselines before hand-written direct kernels.
- Use graph capture only when repeated launch overhead is material and argument lifetime/statefulness is safe.
- Treat approximate math as a tolerance-gated candidate, not a default.
- Inspect generated code when register pressure, spills, instruction selection, or missed vectorization plausibly dominates.

## Execution Topology And Lifecycle

- Model the dependency DAG, not just source order or kernel count. Independent graph nodes, batch chunks, producer-consumer phases, cooperative clusters, and fused kernels expose different overlap.
- Treat concurrency as a mechanism class, not one API. A ban or failure of extra streams, threads, workers, or processes closes that form only when the broader contract still permits concurrency.
- Separate written policy from lexical scanners and runtime enforcement. Never disguise forbidden work; when semantics are allowed but one representation is overblocked, test a transparent contract-valid form.
- Record import, build, JIT, warmup, allocation, graph capture, replay, and teardown boundaries. Moving work outside the timed path is valid only when the contract permits it and every invocation receives fresh correct state.
- For captured or cached routes, prove pointer lifetime, workspace isolation, output alias safety, input refresh, and route execution.
- Treat code generation, fixed-shape instantiation, offline compilation, and prelinked device code as optimization axes when source and deployment rules allow them.
- Co-design the algorithm and schedule. A new decomposition can lose when attached to an old reduction, materialization, or backtransform even if the integrated architecture wins.
- Write the phase contract before a multi-kernel rewrite: representation, layout, precision, metadata, ownership, synchronization, buffer lifetime, certificate, and repair at every boundary.
- If repeated wrapper or isolated primitive swaps do not move end-to-end time and the gap exceeds their plausible gain, protect the best and reserve a bounded branch for the integrated phase graph.

## Device Discovery

Do not bake device facts into the skill. Discover them for the active run before relying on them:

- Accelerator model, driver/runtime, compiler, library versions, clocks if available.
- Compute-unit or multiprocessor count, subgroup width, max threads, shared memory/LDS, register limits, and occupancy constraints.
- Memory bandwidth, cache/shared-memory behavior, memory transaction sizes, and alignment requirements.
- Supported matrix/tensor instructions, low-precision formats, async copy features, graph support, and atomic capabilities.
- Multi-die, NUMA, partitioning, or placement behavior when locality or launch placement plausibly matters.

Treat every discovered fact as a hypothesis until measured on the authoritative runner.

## Backend Portability

- Retune subgroup assumptions when moving between warp, wavefront, SIMD group, or tile abstractions.
- Keep backend-specific fast paths separate when library heuristics, compiler lowering, or matrix instructions differ.
- For shared memory/LDS staging, prove enough reuse exists to pay for synchronization, bank conflicts, and occupancy loss.
- Use double buffering or async copies only when memory latency is exposed and extra state does not reduce occupancy below the useful threshold.
- Try register caps, launch bounds, and occupancy controls only as measured candidates; they can hide one bottleneck while creating another.
- Prefer cross-lane shuffles, permutes, or subgroup reductions before shared-memory roundtrips when the operation fits.
- Use block swizzling, persistent kernels, or work reordering only when cache locality, load balance, or launch overhead is the measured problem.
- Keep enough blocks/workgroups to fill the target device, but do not increase grid size past the point where overhead, atomics, or tail imbalance dominate.

## Precision And Recovery

- Budget precision by state: storage, products, accumulation, critical scalar solves, final output, and verifier need not share one dtype.
- Keep a precision ledger per phase: carrier/storage, products/accumulation, critical scalars, output conversion, certificate, and repair/fallback.
- Normalize or scale before low-precision storage when range is the blocker.
- Pair approximate carriers with a mathematically justified repair such as residual correction, refinement, reorthogonalization, purification, or accurate terminal solve.
- Prefer per-item certificates and selective repair when failures are sparse and independently routable. Include certificate cost, synchronization, compaction, and worst-case fallback in the model.
- Do not infer that a low-precision family is invalid from an unscaled or unrepaired prototype; scope the verdict to the tested precision boundary.

## Profiling

Use the profiler available on the target system. Examples:

```bash
nsys profile ./my_kernel
ncu --set full ./my_kernel
rocprofv3 --hip-trace --hsa-trace --kernel-trace ./my_kernel
hipcc --save-temps my_kernel.cpp
```

Use counters to check occupancy, memory bandwidth, tensor/ALU utilization, shared-memory conflicts, cache behavior, atomics, stalls, and launch overhead. Counter wins do not override authoritative wall time.

When target profiling is unavailable, use route-attested stage cuts or controlled prefix/suffix variants to estimate phase ownership. Keep setup and warmup comparable, and never promote from a stage-only result.

## Cross-GPU Transfer

Do not assume a win on one GPU transfers to another:

- Re-check target hardware, memory hierarchy, compiler/runtime, library versions, and supported fast paths.
- Keep target-specific artifacts when policies conflict.
- Submit/fan out only when the expected margin is wide or a lane fill is explicitly valuable.
- If a target regresses, record the transfer failure and avoid unchanged retries.

## GPU Dead-End Signals

Stop or change direction when:

- A graph wrapper adds state checks or setup that exceeds launch savings.
- Shared memory/LDS staging adds synchronization or bank conflicts without enough reuse.
- Wider vectorization increases register pressure or hurts small cases.
- A library path is correct but dominated by one shape; route only that shape differently.
- Local/private timing wins do not survive the authoritative runner.
