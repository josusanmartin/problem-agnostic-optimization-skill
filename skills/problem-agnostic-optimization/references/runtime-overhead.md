# Runtime And System Overhead

Use this module when process startup, allocation, graph setup, JIT, dynamic dispatch, I/O, framework calls, synchronization, or launch/setup cost dominates the measured result.

## First Candidates

- Cache allocations, descriptors, handles, compiled code, and graphs only when the contract permits reuse.
- Remove unnecessary copies and buffered I/O.
- Use lower-level runtime or syscall paths only when measured overhead and policy justify them.
- Precompute legal metadata during unscored setup only when the timed-boundary contract permits it.
- Separate cold-start and steady-state routes when both are scored differently.

## Typical Traps

- Host caching can regress the hot path through branches, state checks, or synchronization.
- Framework routes can include hidden synchronization or allocation.
- Setup moved outside timing without contract permission is invalid.
- Startup and exit can dominate sub-10ms process challenges.
