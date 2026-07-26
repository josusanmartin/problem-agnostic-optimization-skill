# CPU Optimization Reference

Use for offline CPU executables, command benchmarks, SIMD paths, generated code, and hot loops. Route end-to-end request services separately.

## Locate The Scored Boundary

Classify the run as `single-shot process`, `batch/offline kernel`, or `mixed`. Determine whether timing includes startup, parsing, allocation, I/O, warmup, and teardown before optimizing a hot loop.

Discover only target facts that can change a candidate: CPU and ISA support, core/NUMA or quota limits, compiler/runtime and link mode, relevant cache or bandwidth facts, and whether threads, mmap, affinity, custom allocation, or direct syscalls are allowed. Do not transfer local-machine assumptions to the authoritative runner.

## Choose From The Measured Owner

- Lifecycle or I/O: reduce startup, parsing, formatting, allocation, copying, syscalls, or teardown; load the runtime add-on when these dominate.
- Memory: reduce bytes, improve layout/locality, expose enough independent streams, and treat prefetch distance as target-specific.
- Compute: change algorithm or primitive first when its plausible gain exceeds local tuning; otherwise test vectorization, dependency overlap, instruction choice, and bounded unrolling.
- Frontend or branches: reduce code size, indirection, unpredictable control flow, or general parsing/formatting on the scored path.
- Contention or tails: change thread count, partitioning, synchronization, or straggler work rather than optimizing aggregate throughput alone.

Specialize fixed shapes, ranges, ordering, or formats only when the contract proves them. Build flags, static linking, custom entrypoints, and low-level runtime paths are candidates, not defaults; verify acceptance and end-to-end timing.

## Test Primitive Inversion

A compact or wide primitive can be slower when gather, shuffle, mask, conversion, atomic, helper, or library behavior is microcoded or serialized. When low instruction count still plateaus, replace only the suspect primitive family and predict the pressure moved to ALU, loads/stores, registers, frontend, or code size.

More instructions may win when they leave the true binder. Retune cadence after the primitive changes and keep per-microarchitecture variants when the trade does not transfer.

## Interpret And Transfer Evidence

Counters and generated code diagnose; authoritative wall time or score promotes. Treat better IPC, fewer instructions, or lower proxy counts as evidence only when end-to-end time follows. A local win that changes startup, filesystem, sandbox, ISA, or target topology may not transfer.

Move to intrinsics or assembly only when it can change instruction selection, register allocation, loop layout, ABI/startup cost, or exact scheduling. Stop unchanged retries when the runner rejects the mechanism, the compiler already emits the same path, or proxy improvements repeatedly fail to move authority.
