# Quantized Kernels

Use this module for FP4/FP6/FP8, NVFP, MXFP, block-scaled operations, quantized decode, and quantized matrix or expert kernels.

## First Candidates

- Verify tensor layout, scale layout, swizzling, and packing before optimizing.
- Build exhaustive or CPU bit checks for decode and encode paths.
- Use vectorized byte or word loads and stores.
- Establish hardware-matrix and library baselines for quantized matrix work.

## Typical Traps

- Platform or reference failures can masquerade as candidate failures.
- Public documentation can differ from runner semantics; authoritative sample and checker evidence wins.
- Re-swizzling already-swizzled scale tensors breaks correctness.
