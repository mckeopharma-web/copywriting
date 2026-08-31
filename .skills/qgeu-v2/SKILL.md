# QG-EU v2 skill

Use this skill when a request asks for a quantitative graph that answers a bounded question from historical data.

## Procedure

1. Parse the question into subject, variable, population/universe, geography, period, comparator and answer type.
2. Build a `MetricContract` before searching.
3. Discover candidate source graphs, tables, datasets or series.
4. Apply hard gates before scoring. Reject incompatible definitions even when semantically similar.
5. Prefer the least-transformative admissible path: exact source graph, rebuild, deterministic derivation, otherwise route out.
6. Keep each observed point linked to an exact source locator.
7. Use only deterministic derivations under `reasoning_mode=DEDUCTIVE`.
8. Mark derived arithmetic as `DERIVED_DETERMINISTIC`; never call it source-observed data.
9. Select a chart type that does not imply observations that do not exist. Two points should normally use a slope/dot comparison, not a continuous trend line.
10. Produce a bounded answer and a provenance manifest.
11. Fail closed unless every `GraphQualityGate` field is true.

## Allowed deterministic transformations

Examples: difference, ratio, percentage change, index rebasing, share, per-capita normalization, spread, rolling mean, CAGR and deterministic decomposition when dimensions and assumptions are explicit.

## Forbidden in deductive QG-EU

- silent interpolation or imputation;
- fitted models hidden inside a derivation;
- forecast or scenario values represented as historical deductions;
- causal claims from descriptive correlation, ratios or trends alone;
- mixing incompatible units, populations, geographies or period semantics;
- truncated or transformed axes that materially exaggerate a comparison without explicit rationale;
- hiding source, period, population, formula or transformation notes.

## Output contract

A QG-EU must contain: question, metric contract, retrieval candidates, selected production mode, source series, derivation, graph spec, bounded answer, provenance manifest and fail-closed quality gate.
