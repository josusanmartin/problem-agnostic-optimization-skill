# Fixed-Resource Scheduling

Use this module for VLIW cycle searches, packet schedulers, DSP kernels, compiler instruction scheduling, custom accelerators, and software-pipelined fixed-resource machines.

## First Candidates

- Compute a rough per-engine floor (`required work / plausible throughput`) before schedule sweeps. Return to the core router for detailed resource modeling only when that floor, a tail, a transfer, or co-binders decide the next candidate.
- Count constrained engines separately: vector, scalar, memory, branch/control, gather, shuffle, store, and special units.
- Compare the actual schedule to the maximum resource floor.
- Audit final-tail resource use, not only total counts.
- Use contract-aware omission only when output semantics prove state is unobserved.
- Rebalance resources only when the destination has measured slack.
- Compose mechanisms only after each resource trade is characterized.

## Typical Traps

- A lower slot floor can lose through dependencies, scratch lifetimes, or barriers.
- Moving work to another saturated engine is not a speedup.
- Schedule-only search cannot beat a proven lower bound above the target.
- Combining knobs before measuring component effects produces ambiguous evidence.
