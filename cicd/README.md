# CI/CD — EvidenceUnit evidence-governed copy

The executable reusable GitHub Action lives in `cicd/evidence-unit-quality-gate/action.yml`. GitHub requires workflow entrypoints under `.github/workflows/`, so `.github/workflows/evidence-unit-quality-gate.yml` is intentionally a thin dispatcher. Business rules stay in `src/eu_pipeline.py` and the contract in `.skills/evidence-unit-judge/SKILL.md`.

```mermaid
flowchart LR
  P[Public page + CopySequence] --> C[Classify claim / recommendation / CTA]
  C -->|assertive| R[Generate / retrieve up to 5 EU candidates]
  R --> X[x = variable + value + unit + population + period + source]
  X --> V[Fetch canonical URL + numeric-anchor verification]
  V --> E[LLM entailment: source actually supports source_fact]
  E --> J[LLM-as-a-Judge A-J / 100]
  J --> F[F = f(x,u,b,s) admitted EU]
  F --> S[Select / substitute with cardinality invariant]
  S --> XP[XPath must match exactly once]
  XP --> G[G = g(Y,F) publishable EvidencePlacement]
  G --> Q[Audit every claim / recommendation / CTA]
  Q -->|gap, hallucination, stitched support, bad XPath, count drift| FAIL[FAIL CLOSED]
```

## Required repository secrets

`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`. `NEO4J_DATABASE` is optional and defaults to `neo4j` in the Python entrypoint.

The default judge model is `gpt-5.6-sol`. It can be overridden by the composite-action `model` input.

## Modes

`check` is the default on pull requests and pushes. It never writes to Neo4j. It audits the selected homepage set, verifies every source fact against the fetched URL, re-runs the LLM judge, checks XPath uniqueness, and checks coverage of all assertive sequences.

`apply` is available only through manual workflow dispatch. For uncovered assertive sequences it asks the model, with web search enabled, for up to five independent quantitative research candidates. Every generated URL is then fetched and verified; only candidates passing deterministic anchor checks, LLM entailment and the judge hard gates can be persisted as `CANDIDATE` EvidenceUnits/EvidencePlacements. `apply` does **not** silently increase the selected homepage EU count; promotion/substitution must preserve the configured cardinality.

## Hard failures

The action returns a non-zero exit code when any of these is true: selected EU count drift; missing atomic quantitative fields; unreachable/empty source; source fact numeric anchors absent; semantic entailment FALSE/UNKNOWN; LLM Judge hard-gate failure; direct competitor/vendor evidence; missing effect/recommendation separation; XPath match count other than 1; claim/recommendation/CTA without a selected complete EU; CTA without a valid target route.

The machine-readable result is uploaded as `evidence-unit-quality-gate` from `artifacts/evidence-unit-quality-gate.json`.