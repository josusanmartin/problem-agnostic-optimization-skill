# Matrix Composition Kernels

Use this module for GEMM, GEMV, batched matrix multiplication, triangular or symmetric products, fused matrix epilogues, and matrix-based reformulations.

## First Candidates

- Flatten the math to GEMM, GEMV, or TRMM when possible.
- Establish vendor-library and generated-kernel baselines before writing a direct kernel.
- Cache descriptors, handles, workspaces, and algorithm choices only when the contract permits reuse.
- Fuse epilogues through library support or a vectorized post-pass.
- Choose compute precision from the correctness tolerance and validate residual or repair paths authoritatively.

## Typical Traps

- Structured BLAS calls can be semantically wrong when inputs only approximately satisfy the structure.
- A local-device win does not prove correctness or speed on the target device.
- Library heuristics can be shape-specific; preserve per-shape routing when needed.
