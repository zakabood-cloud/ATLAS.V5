# Observed local release checks

ATLAS 5.0.0. Run finished 2026-11-04T20:23:32.677161+00:00. Tests: 257/257 passed; 0 failed, 0 errors, 0 skipped. Local status: **QUALIFIED_LOCAL_RELEASE**.

The local gate executed the static structure check, the discovered test suite, the synthetic lifecycle, all 10 example calculations, the supplied-v3 paired controls, and a hash comparison of all 147 audited baseline files. This is not a research-quality or factual-accuracy score. No Copilot runtime, network request, model/provider, or paid API was used by the gate.

See [machine-readable results](test_results.json), [test log](unittest.log), and [upgrade comparison](v4_comparison.json). Packaging and independent ZIP extraction are separate steps. Unresolved: live Copilot behavior, authenticated integrations, independent post-implementation review, blinded research-quality evaluation, model-facing injection resistance, and other operating systems/Python versions.

Reproduce with `python3 scripts/validate_release.py`; run the local demo with `python3 scripts/demo.py`. These checks do not establish that sources support research claims or that real-world findings are correct.
