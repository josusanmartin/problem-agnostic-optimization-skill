# Elementwise And Streaming Kernels

Use this module for activations, scalar transforms, vector add/multiply, streaming decode, and simple load-transform-store kernels.

## First Candidates

- Dispatch exact shapes when the contract fixes benchmark sizes.
- Match packetized IO to natural alignment and vector width.
- Use exact-grid launches when official sizes do not need a grid-stride loop.
- Separate full blocks from tail handling.
- Test approximate math only after tolerance and edge-case checks.
- Treat graph or launch reuse as an isolated candidate.

## Typical Traps

- Streaming or non-temporal cache hints can win or lose; measure against normal IO.
- Register caching can reduce recompute but regress from register pressure.
- Same-artifact reruns are variance, not code improvement.
