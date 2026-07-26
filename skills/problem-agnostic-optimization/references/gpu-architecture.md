# GPU Optimization Reference

Use for CUDA, HIP/ROCm, Triton, device-library routes, and scored GPU kernels. Route end-to-end request services separately.

## Establish Shape, Target, And Lifecycle

Treat shapes, dtypes, layouts, and devices as separate lanes until evidence supports one route. Load the matching shape module for operation-specific candidates.

Discover only facts that can change a candidate: device and backend, compiler/library versions, subgroup and resource limits, memory behavior, supported matrix or async features, and placement topology. Record whether timing includes import, build, JIT, warmup, allocation, capture, replay, and teardown.

Moving work outside the timed path is valid only when the contract allows it and every invocation receives fresh correct state. For cached or captured routes, prove route execution, pointer lifetime, workspace isolation, alias safety, and input refresh.

## Choose From The Measured Owner

- Transfer or bandwidth: reduce bytes, conversions, materialization, and poorly coalesced traffic before tuning instruction count.
- Compute or primitive: compare the relevant library/generated baseline, representation, algorithm, and precision route before hand scheduling.
- Launch or setup: fuse, batch, persist, capture, or precompile only when lifecycle savings exceed added state and synchronization.
- Occupancy or latency: trade registers, shared memory/LDS, async staging, subgroup exchange, and independent work from measured reuse and stalls.
- Tail or imbalance: change work mapping, grid shape, routing, or decomposition rather than optimizing the already-fast majority.

When the remaining gap exceeds the plausible gain of local substitutions, reserve a bounded integrated phase-graph candidate instead of continuing micro-tuning.

## Preserve The Phase Contract

Model the dependency DAG, not source order or kernel count. Co-design algorithm, mapping, layout, precision, synchronization, metadata, ownership, and buffer lifetime; a component can regress alone while enabling a winning integrated route.

A failed concurrency API closes that representation, not every allowed form. Never disguise forbidden semantics. Before a multi-kernel rewrite, specify only boundaries that can fail and attest that the intended route ran.

## Budget Precision And Recovery

Storage, products, accumulation, critical scalars, output, certificate, and repair need not share one dtype. Scope a precision failure to the tested boundary. When justified, pair a cheaper carrier with scaling, a certificate, selective repair, refinement, or an accurate terminal phase, pricing its synchronization and worst-case fallback.

## Interpret And Transfer Evidence

Profiles and stage cuts diagnose; authoritative end-to-end time promotes. Use counters only to distinguish occupancy, bandwidth, compute, cache, synchronization, atomics, tail, and launch hypotheses. Never sum incompatible cuts or promote a stage-only result.

Retune after changing device, compiler, library, subgroup model, or lifecycle. Keep target-specific artifacts when trades conflict, and stop unchanged retries when local wins fail to transfer or added state, synchronization, register pressure, or tail cost consumes the predicted gain.
