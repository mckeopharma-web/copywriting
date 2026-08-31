# EvidenceUnit Judge & Placement Skill

## Purpose

Turn public-site copy into evidence-governed copy. Every assertive `CopySequence` (claim, recommendation, CTA, mixed assertion) is evaluated against complete `EvidenceUnit` objects, verified source text, an LLM-as-a-judge quality gate, and a unique rendered XPath before it can be selected for publication.

## Formal contract

`x = {variable, value, unit, population, period, primary_source_url}` is one atomic external observation.

`u = {boundary, limitations, uncertainty, source_independence, conflict_of_interest}` contains the conditions that prevent over-generalization.

`F = f(x,u,b,s)` where `b` is the offer/page/section binding and `s` is the explicit separation of observed-effect support from recommendation/implementation support. `F` exists only when the source URL is fetched, the claimed numeric/text anchors are found, semantic entailment passes, and the EvidenceUnit Judge hard gates pass.

`Y = {copy text, assertion_class, buyer_question, nlp_role, CTA intent, target_xpath}`.

`G = g(Y,F)` is the publication/placement decision. `G.publish=true` only when every factual premise in `Y` is entailed by admitted `F`, the CTA target/binding is valid, the XPath matches exactly once, no effect/recommendation evidence is stitched, and the page-level EvidenceUnit cardinality invariant is preserved.

## Mandatory pipeline

1. Snapshot the target page and enumerate every visible `CopySequence`.
2. Classify each sequence: CLAIM, RECOMMENDATION, CTA, CLAIM_AND_RECOMMENDATION, or NON_ASSERTIVE.
3. For each assertive sequence, generate up to five candidate EUs. Prefer independent peer-reviewed/high-authority research. Reject vendor promotional evidence and direct competitive-product arguments.
4. Require the quantitative atom: variable + numeric value/range + unit + population + period + canonical source URL.
5. Fetch the canonical source. Verify that the numeric anchors occur in the fetched content. Then run an LLM entailment check against bounded snippets. `UNKNOWN` fails closed.
6. Run `judge:evidence-unit:champion-v2`. Score A–J on `EU-CHAMPION-100-v1`. Dominant candidates require score >95 plus all research, bibliometric, competition, source-independence and causal-boundary gates.
7. Select one EU per placement. A replacement is allowed only when the candidate passes all hard gates and either the incumbent fails a hard gate or the new score is strictly higher after incumbent calibration.
8. Preserve the homepage selected-EU count exactly. Never increase or decrease it as a side effect of substitution.
9. Create/update `EvidencePlacement` only after selection. Persist page URL, sequence ID, semantic component IDs, XPath, `xpath_match_count=1`, page snapshot SHA-256, source-verification run and judge run.
10. Audit every claim/recommendation/CTA again. Any unsupported sequence creates an `EvidencePlacementGap` and blocks publication.

## Source anti-hallucination rule

A URL is not proof. CI must fetch the URL and prove that the source text supports the `source_fact`. Numeric anchors are deterministic preconditions; LLM entailment is a second independent check. Redirect-to-homepage, empty content, inaccessible source, missing anchor, contradiction or uncertainty => hard failure.

## Support separation

`(EU)-[:EFFECT_SUPPORTED_BY]->(SourceDocument)` proves the observed external effect only.

`(EU)-[:RECOMMENDATION_SUPPORTED_BY]->(SourceDocument)` supports an implementation/recommendation separately. An OSS library, consulting method or implementation substrate must never be used as proof of the external effect.

## GitHub Actions modes

- `check`: PR/push mode. Read Neo4j, fetch sources/site, run judge and fail on any invariant. No graph mutation.
- `apply`: manual workflow dispatch. May persist judge reviews, EUs, gaps and selected placements after all gates pass.

GitHub only executes workflows located in `.github/workflows/`. The canonical workflow specification is maintained under `cicd/`; the small `.github/workflows/evidence-unit-quality-gate.yml` dispatcher executes the same `src/eu_pipeline.py` entrypoint to avoid duplicated business logic.