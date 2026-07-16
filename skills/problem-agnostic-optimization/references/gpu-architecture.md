# GPU Optimization Reference

Use this reference for CUDA, HIP/ROCm, Triton, GPU challenge kernels, production GPU services, and leaderboard GPU work. Keep the guidance architecture-agnostic by default; discover hardware facts from the active target and prove them with measurements.

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

- Use packetized IO and exact grids for streaming kernels.
- Keep tail handling outside the hot path when the contract allows it.
- For reductions, compare atomics, partial reductions, subgroup/block reductions, vendor libraries, and graph wrappers empirically.
- For GEMM, convolution, FFT, scan, sort, and attention-like primitives, try vendor libraries and template kernels before hand-written direct kernels.
- Use graph capture only when repeated launch overhead is material and argument lifetime/statefulness is safe.
- Treat approximate math as a tolerance-gated candidate, not a default.
- Inspect generated code when register pressure, spills, instruction selection, or missed vectorization plausibly dominates.

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

## Profiling

Use the profiler available on the target system. Examples:

```bash
nsys profile ./my_kernel
ncu --set full ./my_kernel
rocprofv3 --hip-trace --hsa-trace --kernel-trace ./my_kernel
hipcc --save-temps my_kernel.cpp
```

Use counters to check occupancy, memory bandwidth, tensor/ALU utilization, shared-memory conflicts, cache behavior, atomics, stalls, and launch overhead. Counter wins do not override authoritative wall time.

## Attention And Decode Lessons

Transferable lessons from attention/decode-style kernels:

- Split exact shapes first. The winning route often differs by sequence length, batch, head count, page size, expert count, or routing mode.
- Page size, tile size, and split count can move the bottleneck between metadata, atomics, memory bandwidth, and compute.
- Persistent and non-persistent modes are different algorithms; validate each shape because one mode can be correct and fast on one case but invalid on another.
- Skipping large zero/fill initialization after warmup is valid only when the contract proves the kernel fully overwrites the buffer; otherwise treat it as statefulness risk and validate against ranked behavior.
- Very large page sizes can cause timeouts despite good microbenchmarks.
- Environment variables can be part of the measured system; record them with results.

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
