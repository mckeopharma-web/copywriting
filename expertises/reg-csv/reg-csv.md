# reg-csv.md — Evidence review manifest

Status: REVIEW_ONLY_PENDING_PRESENTATION_JUDGES  
Target page: https://mickael-umt.com/expertises/reg-csv/  
Repository target: mckeopharma-web/copywriting / expertises/reg-csv/  
Build date: 2026-09-03

## Candidate pool

NeoFort query contract:
- current = true
- deterministic_preflight_status = PASS
- factfulness_gate_status = PASS
- agent_exploitability_status = ALLOWED
- ranking: reg_csv first, then adjacent pharma/healthtech domains, then remaining proof-carrying objects
- cap: 80 EvidenceUnits

Pool result:
- 80 / 80 retained
- 9 arXiv-backed units
- 42 public-authority units (FDA, EMA, EC/Eur-Lex, MHRA/GOV.UK, NIST/openFDA)
- 51 / 80 therefore come from arXiv or public-authority/open public sources
- NeoFort currently contains 86 proof-carrying current EUs; the page-selection pool is deliberately capped at 80.

This pool count is a retrieval result, not a quality score. Every selected claim remains independently bounded.

## Distributed Level-1 / Level-2 placements

The HTML contains 11 citation placements resolving to 11 unique EvidenceUnits:

1. EU-REGCSV-ICH-Q9-QRM-2026 — pharmaceutical QRM scope.
2. EU-REGCSV-EC-ANNEX11-RISK-2026 — GMP computerised-system risk-based validation / traceability.
3. EU-REGCSV-FDA-CSA-RISK-2026 — medical-device CSA corroboration, explicitly separate scope.
4. EU-REGCSV-EC-ANNEX15-LIFECYCLE-2026 — lifecycle qualification/validation and change impact.
5. EU-REGCSV-FDA-DATA-INTEGRITY-CGMP-2026 — drug-CGMP data integrity.
6. EU-REGCSV-MHRA-GXP-DATA-INTEGRITY-2026 — cross-GxP data-governance scope.
7. EU-HT-EMA-FDA-GOOD-AI-2026 — good-AI lifecycle principles.
8. EU-CANON-EMA-NDSG-WORKPLAN-2026-2028 — planned regulatory data/AI work.
9. EU-REGCSV-PROOF-PHARMACY-STUDIES-2014-2020 — public education evidence.
10. EU-REGCSV-PROOF-PHARMACY-OPS-2015-2023 — public regulated-operations evidence.
11. EU-REGCSV-PROOF-RADIOPHARMACY-2018-2019 — public hospital-QC evidence.

The HTML uses `<div class="lp-evidence-bubble-scroll">` for every Level-2 disclosure. Each public citation maps to one unique EvidenceUnit; no FAQ alias duplicates are emitted.

## EUG / QGEU placements

Four question-driven graphs are embedded without adding or reordering page sections:

- QGEU-REGCSV-OFFICIAL-GUIDANCE-TIMELINE-2026
  - 7 source-date observations.
  - Direct timeline; no fitted trend.
  - Boundary: dates identify source revision/publication/effectivity, not hierarchy or deadlines.

- QGEU-REGCSV-EMA-NDSG-MINUTES-LAG-2026
  - 5 observed meeting/publication date pairs.
  - Derived values: 34, 30, 47, 32, 38 calendar days.
  - Formula: first_publication_date - meeting_date.
  - Boundary: document-publication cadence only.

- QGEU-REGCSV-PROFESSIONAL-EVIDENCE-TIMELINE-2026
  - 5 documented activity intervals.
  - No summing of overlapping periods.
  - Boundary: first-party public professional record; not CSV client outcomes.

- QGEU-REGCSV-PUBLIC-ENGINEERING-PROJECTS-TIMELINE-2026
  - 6 documented public-project intervals.
  - Boundary: public implementation history, not production or regulatory outcome evidence.

NeoFort deterministic graph-quality and Factfulness certificates are PASS for the four QGEUs. `judge:evidence-graphic:presentation-v1` has not yet produced the required independent 3-replica result, so `publication_status = REVIEW_ONLY_PENDING_PRESENTATION_JUDGE`.

## Current policy snapshot used

- policy:evidence-agent-exploitability:deterministic-preflight-v2
- policy:evidence-agent-exploitability:proof-carrying-v3
- policy:evidence:canonical-epistemic-classification-v2
- policy:evidence-judge:factfulness-semantic-100-v2
- policy:evidence-unit-judge:champion-100-v2
- evidence-placement-policy:site-v5
- policy:evidence-placement:claim-span-entailment-v2
- policy:llm-judge:deterministic-execution-v2
- policy:evidence-judge-verdict-normalization:v2
- policy:qgeu:data-visualization-analyst-v1

Applicable current judges:
- judge:evidence:factfulness-epistemology-methodology-v2
- judge:evidence-unit:champion-v2
- judge:evidence-placement:presentation-v1.2
- judge:evidence-graphic:presentation-v1

## Structural validation

Original top-level section topology retained exactly: 22 sections, same order and same `data-section-id` sequence.

Sequence:
hero → mandat → declencheurs → consequences → pour-qui → qualification → proposition → attributs → offres → livrables → avant-apres → resultats → preuves → perimetre → deroule → modules → capacites → intersection → pricing → engagements → questions → engagement.

Automated local checks:
- 22 sections: PASS
- section sequence equality: PASS
- `.lp-evidence-bubble-scroll`: 11
- citation buttons: 11
- unique cited EvidenceUnits: 11
- QGEU figures: 4
- static HTML IDs are unique: PASS
- runtime citation script assigns 11 unique `aria-controls` / bubble IDs deterministically: PASS BY CONSTRUCTION

## Publication gate

FAIL_CLOSED status:
- deterministic preflight: PASS for selected evidence objects and new QGEUs
- Factfulness / proof-carrying gate: PASS
- source provenance: recorded
- graph quality deterministic gate: PASS
- required 3-replica graph presentation judge: PENDING
- required final placement-presentation replica judgement for newly introduced placements: PENDING
- live/main publication: BLOCKED
- GitHub persistence: allowed only on a review branch; a commit is persistence, not evidence validity

No Google Drive create/update/delete operation has been performed.
