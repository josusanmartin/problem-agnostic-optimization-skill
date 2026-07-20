# CPU Optimization Reference

Use this reference for CPU kernels, command/process benchmarks, cpu.mode-style single-shot submissions, SIMD code, intrinsics, generated assembly, and counter-driven diagnosis. Keep platform facts target-local: discover the active machine, runner, limits, and scoring contract before choosing tactics. This module deliberately excludes long-running request-service and load-test guidance.

## CPU Search Rules

- Start with the contract: input source, output format, target metric, correctness scope, warmup, concurrency, allowed languages, flags, syscalls, and resource limits.
- Classify the benchmark mode early: `single-shot process`, `batch/offline kernel`, or `mixed`.
- Run the baseline before claiming wins.
- Preserve the best artifact and command line.
- Compute a rough lower bound: bytes moved, operations, syscalls, requests, serialization, or unavoidable latency divided by realistic throughput.
- Keep per-system variants when CPUs, core counts, quotas, NUMA, or runner modes differ.
- If the gap is large, prefer algorithm, representation, parsing, allocation, I/O, or concurrency changes before instruction-level tuning.

## Target Discovery

Record only facts that are true for the active target:

- CPU model, core count, SMT, frequency behavior, caches, memory bandwidth, NUMA, cgroup/container quotas, and thermal/power limits when visible.
- Supported ISA features and whether the official runner permits binaries compiled for them.
- Compiler/runtime version, link mode, libc, allocator, kernel, filesystem, and network stack when relevant.
- Whether threads, fork/exec, mmap, huge pages, static linking, affinity, custom allocators, or direct syscalls are allowed.
- Whether timing includes process startup, parsing, I/O, warmup, network accept/connect, request generation, or only the hot function.

Do not assume local laptop facts transfer to the official runner.

## Build And Runtime Candidates

Use these as measured candidates, not defaults:

- Release builds with target-specific optimization only when the official runner supports the target CPU.
- LTO, PGO, link-time dead-code elimination, panic/exception removal, and static linking when allowed.
- Custom allocators, arena allocation, object pooling, mmap/read/write paths, buffered IO, direct syscalls, and fast exit paths when runtime overhead is included.
- Runtime CPU dispatch when one binary must support multiple machines.
- Intrinsics or assembly only after generated code or counters show the compiler cannot produce the needed instruction sequence.

Always verify that build flags do not silently change correctness, portability, startup time, or judge acceptance.

## Single-Shot Process Benchmarks

Examples: cpu.mode-like judges, command-line programs, offline stdin/stdout tasks, process startup included in timing.

High-signal candidates:

- Remove startup overhead: smaller runtime, fewer dynamic initializers, less allocator setup, simpler language/runtime paths.
- Reduce input and output cost: mmap or large reads, zero-copy parsing, custom scanners, batched writes, avoid formatting in hot paths.
- Avoid allocations in the measured path; pre-size or use arenas when the contract allows it.
- Specialize fixed input sizes, ranges, or output formats when the benchmark contract proves them.
- Use compile-time constants/templates/const generics to delete loop tails and branches.
- Exit directly only when the platform contract allows skipping destructors and buffered cleanup.

Typical traps:

- Static linking, custom entrypoints, direct syscalls, or mmap can be rejected or slower on some judges.
- Optimizing the hot loop is wasted when startup, parse, or output dominates.
- A local sample runner may not include the same startup, filesystem, or sandbox overhead as the official scorer.

## Memory-Bound Patterns

- Keep enough independent streams to expose memory-level parallelism without overflowing caches or hardware prefetchers.
- Sweep stream count, chunk size, prefetch distance, and data layout on the target machine.
- Keep hot working sets under the relevant cache level when possible.
- Pack data to reduce bytes moved before optimizing instruction count.
- Widen narrow accumulators before overflow.
- Treat prefetch as microarchitecture-specific and benchmark it; it often helps one target and hurts another.
- Avoid optimizing instruction count when counters show backend memory bound.

## Compute-Bound Patterns

- Use SIMD, vector libraries, or compiler auto-vectorization when the data layout supports it.
- Discover and guard ISA features; unsupported instructions should never reach unsupported targets.
- Unroll only when it reduces branch/bookkeeping or exposes ILP without frontend/register-pressure regressions.
- Move independent work earlier to overlap dependency chains.
- Prefer instruction forms that relieve the constrained port, critical path, or vector width on the measured CPU.
- Inspect assembly when a tiny loop matters.

## Primitive Choice Can Beat Width

Do not assume the widest or most semantic instruction is fastest. Some targets implement gathers, scatters, masked operations, cross-lane shuffles, atomics, conversions, crypto/math helpers, or library calls through microcode or low-throughput paths. A scalarized or decomposed version can retire many more instructions and still win by moving work off the saturated resource.

Use this probe when a compact vector/library/ISA primitive plateaus, especially with high frontend slots, low IPC, microcoded-assist symptoms, or a large target gap despite low instruction count:

- Check target-specific latency/throughput tables, uops databases, profiler samples, or a focused microbenchmark for the suspect primitive.
- Build the smallest A/B candidate that preserves the algorithm and replaces only that primitive family.
- Predict the resource transfer: saved frontend/uop/port/microcode pressure versus added scalar ALU, loads, stores, register pressure, or code size.
- Accept that instruction count may rise if wall time and the saturated-resource counters fall.
- Retune unroll, alignment, register constants, and tails after the primitive changes; old cadence choices may no longer apply.
- Keep per-microarchitecture variants when the decomposition wins on one core class and loses on another.

## Branch, Parse, And Format Patterns

- Replace branchy parsers with table-driven, vectorized, or delimiter-scan approaches when input format dominates.
- Exploit bounded ranges, sortedness, fixed field positions, ASCII-only input, or monotonicity only when the contract proves them.
- Avoid general formatting libraries in hot output paths; use specialized integer/float formatting when output cost matters.
- Validate edge cases before trusting a parser speedup.

## Counter And Trace Interpretation

Counters explain the result; wall time or official score decides promotion.

- High backend bound and cache misses: bandwidth/latency or layout likely dominates.
- High frontend bound: code size, branch density, decode pressure, or indirect calls may dominate.
- High branch misses: parsing, unpredictable conditionals, or data-dependent control flow may dominate.
- High context switches or scheduler time: thread count, blocking, load generator, or OS interaction may dominate.
- Better IPC with worse time: the program may be doing more work or losing locality.
- Fewer instructions with worse time: critical path, port pressure, memory behavior, or synchronization got worse.
- Lower instruction count with high frontend bound can indicate a toxic complex primitive. Test decomposition even if the replacement raises instruction count.

Useful tools when available:

```bash
perf stat ./target
perf record -g ./target
perf report
strace -c ./target
hyperfine './target < input'
taskset -c 0 ./target
```

## Public Clues And Harnesses

Mine public source, crate names, papers, benchmark writeups, leaderboard diffs, and flamegraphs for hypotheses, not conclusions. Treat a competitor's winning technique as a route-level evidence trigger; do not expand scope unless the router selects that add-on.

Clean examples:

- Sortedness or monotonicity enabling dynamic prefix stepping.
- Bounded ranges enabling smaller counters or lookup tables.
- Fixed loop bounds enabling compile-time specialization.
- Request distribution enabling route-specific fast paths.

Do not use leaked expected outputs, hidden fixed tests, stale validation pools, or harness bugs as clean wins.

## Low-Level Artifact Transfer

Use high-level code to explore algorithms. Move to intrinsics, custom runtime paths, or assembly only when it changes a measured resource:

- Instruction selection.
- Register allocation.
- Loop layout.
- ABI/startup overhead.
- Syscall or allocator overhead.
- Exact scheduling.

If low-level code wins and the user needs another language, first preserve or call the winning path. Rewrite only after wrapper overhead is gone or the high-level compiler can reproduce the behavior.

## CPU Dead-End Signals

Stop or change direction when:

- Threads, fork, mmap, static linking, or specific ISA flags are rejected by the runner.
- Startup, parsing, output, network, or load-generator overhead dominates the hot loop.
- More threads add contention, context switches, or worse tail latency.
- Prefetch, unroll, or vector width changes win locally but lose on the official runner.
- Assembly is structurally identical to compiler output.
- Proxy counter wins do not improve wall time, throughput, latency, or official score.
