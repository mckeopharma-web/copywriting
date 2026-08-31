#!/usr/bin/env python3
"""Runtime adapter for the EvidenceUnit CI pipeline.

Keeps compatibility with legacy/generated EvidenceUnits that use `source_url` while
normalizing them to the canonical `primary_source_url`, and prevents duplicate
judge calls when a placement is reachable through both legacy placement relation
types. These normalizations are deliberately outside the evidence semantics.
"""
from __future__ import annotations

import sys
from typing import Any

import eu_pipeline as pipeline

_ORIGINAL_ATOMIC_GATE = pipeline.atomic_gate


def atomic_gate_with_source_normalization(eu: dict[str, Any]):
    if not eu.get("primary_source_url") and eu.get("source_url"):
        # Mutate the candidate map so apply-mode persistence also writes the
        # canonical field. A source alias never bypasses fetch/entailment gates.
        eu["primary_source_url"] = eu["source_url"]
    return _ORIGINAL_ATOMIC_GATE(eu)


def selected_eus_deduplicated(neo: pipeline.Neo, page_url: str):
    return neo.query(
        """
        MATCH (eu:EvidenceUnit)-[:HAS_SITE_PLACEMENT|HAS_EVIDENCE_PLACEMENT]->(pl:EvidencePlacement)
        WHERE pl.page_url=$page_url AND pl.selected_homepage=true
        WITH DISTINCT eu, pl
        OPTIONAL MATCH (eu)-[:HAS_EVIDENCE_METRIC]->(m:EvidenceMetric)
        OPTIONAL MATCH (eu)-[er:EFFECT_SUPPORTED_BY]->(es:SourceDocument)
        OPTIONAL MATCH (eu)-[rr:RECOMMENDATION_SUPPORTED_BY]->(rs:SourceDocument)
        RETURN properties(eu) AS eu,
               properties(pl) AS placement,
               collect(DISTINCT properties(m)) AS metrics,
               collect(DISTINCT {source:properties(es), rel:properties(er)}) AS effect_sources,
               collect(DISTINCT {source:properties(rs), rel:properties(rr)}) AS recommendation_sources
        ORDER BY pl.sequence_id
        """,
        page_url=page_url,
    )


pipeline.atomic_gate = atomic_gate_with_source_normalization
pipeline.selected_eus = selected_eus_deduplicated

if __name__ == "__main__":
    sys.exit(pipeline.main())
