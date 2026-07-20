# Service Throughput And Load

Use this reference for live HTTP/TCP/queue handlers, request/response workloads, production services, and service load competitions such as HighLoad. Do not load it for kernels, offline programs, simulators, or fixed-resource schedulers.

## Contract And Baseline

- Identify whether the authoritative metric is throughput, p50, p95/p99, tail latency under load, error rate, memory, cost, or a product of them.
- Record request shape and distribution, connection lifecycle, concurrency, warmup, duration, resource limits, language/runtime, and allowed system tuning.
- Verify the load generator is not saturated and the client path is comparable to the authoritative runner.
- Keep the protected best deployable and validate responses before interpreting throughput.

## High-Signal Candidates

- Keep the service warm and stable: avoid per-request initialization, descriptor churn, JIT/setup, and cold caches during measured load.
- Control concurrency explicitly: event loop, worker count, thread pool, async runtime, sharding, queues, and backpressure.
- Reduce per-request allocations, parsing, serialization, logging, locks, atomics, syscalls, and copies.
- Batch where it lowers overhead without violating latency targets.
- Pin or shard state only after measuring scheduler migration, lock contention, cache locality, or NUMA effects.
- Treat socket options, backlog, keep-alive, buffering, kernel/network tuning, and load-generator behavior as contract-governed candidates.
- Preserve per-language and per-runtime routes when compiler, startup, allocator, or framework behavior differs.

## Typical Traps

- A faster mean can hide worse p99 or a higher error rate.
- More threads can reduce throughput through contention, cache misses, queueing, or context switching.
- Async frameworks can lose to blocking or thread-per-core designs when work is CPU-bound and connections are simple.
- Client saturation can make server candidates appear tied.
- A locally valid socket, kernel, compiler, or runtime setting may be rejected or ignored by the authoritative runner.
- Checkpoint traffic, progress rendering, and logging can perturb the measured service; keep observability outside the hot path.
