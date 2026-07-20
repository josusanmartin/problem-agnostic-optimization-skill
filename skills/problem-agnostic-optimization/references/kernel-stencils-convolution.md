# Stencils And Convolution

Use this module for pooling, blur, edge detection, and 1D/2D/3D convolution or stencil kernels.

## First Candidates

- Split interior from boundary so the hot path avoids bounds checks.
- Use shared memory or LDS only when reuse exceeds synchronization and bank-conflict cost.
- Route by exact kernel size, stride, padding, dimension, and layout.
- Consider separable, FFT, vendor-library, or generated-kernel paths before direct convolution on large kernels.

## Typical Traps

- Direct O(N*K) kernels are often noncompetitive for large filters.
- Shared-memory staging can lose when reuse is low or bank conflicts dominate.
- A route that wins one kernel size can lose the aggregate metric when applied broadly.
