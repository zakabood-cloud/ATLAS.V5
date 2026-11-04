# Executable synthetic examples

These ten JSON inputs illustrate supported calculations; all values/probabilities are invented for testing and must not be used as business, investment or scientific estimates.

From the repository root run:

```sh
python3 -m atlas quant examples/unit_economics.json --output /tmp/atlas-unit-economics.json
python3 scripts/demo.py
```

The first command produces a reproducible input/result artifact with output units. The second creates a temporary synthetic project, advances every gate, validates it and cleans up. The fixture review identities are test labels, not independent people or model calls.

New outputs use `atlas.quant/4.0.0` and distinguish per-order, per-period and cash-balance units. Existing registered `atlas.quant/3.0.0` calculations are reproduced explicitly with their historical unit map, not silently relabeled. Normal clipping bounds are checked before simulation; clipped-normal correlations must not be interpreted as the requested latent correlation.

To learn artifact construction, inspect `atlas/demo.py` alongside `docs/SCHEMAS.md`. Do not copy its synthetic answers, source text, review attestations or readiness findings into a real investigation. A genuine project starts with its own inquiry and user interview.
