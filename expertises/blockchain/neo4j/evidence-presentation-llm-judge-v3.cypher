// Applied NeoFort migration — blockchain EvidenceUnit -> Presentation LLM Judge pipeline v3
// Applied 2026-08-31. Idempotent MERGE-based migration.

MERGE (p:EvidencePresentationPolicy {id:'policy:evidence-presentation:progressive-disclosure-v1'})
SET p.version='1.1', p.current=true,
    p.scope='https://mickael-umt.com/expertises/blockchain/',
    p.objective='Preserve executive landing-page rhythm while keeping every factual claim traceable to an admitted EvidenceUnit and verified primary source.',
    p.level_1='L1_DECISION', p.level_2='L2_EVIDENCE',
    p.default_render_mode='SILENT_CITATION',
    p.render_modes=['SILENT_CITATION','METRIC_CHIP','INLINE_NUMBER','SOURCE_AUTHORITY'],
    p.internal_route_template='/evidence/{eu_id}/',
    p.visible_citation_style='NUMERIC_SUPERSCRIPT',
    p.hover_only_forbidden=true, p.keyboard_required=true, p.touch_required=true,
    p.updated_at=datetime();

MERGE (j:EvidencePlacementPresentationJudge:Judge {id:'judge:evidence-placement:presentation-v1'})
SET j.name='Evidence Placement Progressive Disclosure LLM Judge',
    j.version='1.1', j.current=true, j.judge_type='LLM_AS_JUDGE',
    j.execution_mode='PROMPT_DRIVEN_EXTERNAL_ORCHESTRATOR',
    j.fail_closed=true, j.auto_publish=false,
    j.category='EvidencePlacement', j.subcategory='PresentationJudge',
    j.score_version='EUP-PRESENTATION-100-v1',
    j.semantic_fit_weight=30,
    j.executive_readability_weight=25,
    j.rhythm_continuity_weight=20,
    j.traceability_weight=15,
    j.progressive_disclosure_accessibility_weight=10,
    j.pass_threshold=85, j.champion_threshold=95,
    j.hard_gates=[
      'upstream_evidence_unit_admitted',
      'l1_claim_entailed_by_eu',
      'no_bibliographic_apparatus_in_silent_citation_l1',
      'max_one_inline_numeric_datum_unless_data_explanation',
      'l2_has_metric_population_period_source_boundary',
      'citation_resolves_to_exactly_one_eu',
      'internal_evidence_href_resolves',
      'external_source_verified',
      'pointer_keyboard_touch_supported',
      'xpath_claim_anchor_match_count_equals_one',
      'alias_does_not_create_duplicate_public_citation'
    ],
    j.updated_at=datetime();

MERGE (pr:EvidencePresentationJudgePrompt {id:'prompt:evidence-placement:presentation-v1'})
SET pr.name='Evidence Placement Progressive Disclosure Judge Prompt v1',
    pr.version='1.1', pr.current=true,
    pr.input_contract='EvidencePresentationDecision + CopySequence + selected EvidenceUnit + upstream admission state + EvidenceMetric + SourceDocument + internal evidence route + external source URL + DOM/XPath verification + alias metadata.',
    pr.output_contract='{"decision_id":string,"score_total":number,"semantic_fit":number,"executive_readability":number,"rhythm_continuity":number,"traceability":number,"progressive_disclosure_accessibility":number,"hard_gate_pass":boolean,"status":string,"recommended_render_mode":string,"l1_copy_ok":boolean,"l2_evidence_ok":boolean,"citation_ok":boolean,"xpath_ok":boolean,"unsupported_inferences":[string],"rhythm_breaks":[string],"missing_fields":[string],"next_upgrade":string,"judge_rationale":string}',
    pr.updated_at=datetime();

MERGE (sp:EvidencePresentationJudgeScorePolicy {id:'policy:evidence-placement:presentation-100-v1'})
SET sp.version='1.1', sp.current=true, sp.fail_closed=true,
    sp.pass_threshold=85, sp.champion_threshold=95,
    sp.weight_semantic_fit=30,
    sp.weight_executive_readability=25,
    sp.weight_rhythm_continuity=20,
    sp.weight_traceability=15,
    sp.weight_progressive_disclosure_accessibility=10,
    sp.updated_at=datetime();

MERGE (rc:EvidencePresentationJudgeRunContract {id:'contract:evidence-placement-presentation-judge-run:v1'})
SET rc.version='1.1', rc.current=true,
    rc.statuses=['BLOCKED_UPSTREAM_EVIDENCE_JUDGE','EVIDENCE_GAP','PENDING_XPATH','PENDING_PROMPT','RUNNING','SCORED_PASS','SCORED_FAIL','STALE'],
    rc.rule='Immutable per decision snapshot + selected EU snapshot + judge version + prompt version. Publication is never automated from score alone.',
    rc.updated_at=datetime();

MERGE (orch:LLMJudgeOrchestrationPolicy {id:'policy:llm-judge:evidence-to-presentation-v1'})
SET orch.name='Evidence to Presentation LLM Judge Pipeline', orch.version='1.0',
    orch.current=true, orch.fail_closed=true,
    orch.pipeline=['EvidenceUnitJudge','EvidenceUnitAdmission','EvidencePresentationDecision','EvidencePlacementPresentationJudge','XPathVerification','PublicationGate'],
    orch.rule='Scientific evidence quality and commercial presentation quality are separate judgements. Presentation scoring cannot override a failed or pending EvidenceUnit admission.',
    orch.updated_at=datetime();

MERGE (j)-[:USES_PRESENTATION_POLICY]->(p)
MERGE (j)-[:USES_JUDGE_PROMPT]->(pr)
MERGE (j)-[:USES_SCORE_POLICY]->(sp)
MERGE (j)-[:PRODUCES_RUN_CONTRACT]->(rc)
MERGE (orch)-[:USES_PRESENTATION_JUDGE]->(j);

MATCH (j:EvidencePlacementPresentationJudge {id:'judge:evidence-placement:presentation-v1'})
MATCH (euj:EvidenceUnitJudge) WHERE euj.id IN ['judge:evidence-unit:champion-v2','judge:evidence-unit:macro-market-v1']
SET euj.downstream_presentation_gate=true,
    euj.presentation_rule='Passing EvidenceUnit quality does not authorize direct insertion of bibliographic apparatus into landing copy. A separate EvidencePlacementPresentationJudge must approve L1/L2 rendering and XPath anchoring.',
    euj.updated_at=datetime()
MERGE (euj)-[:FEEDS_PRESENTATION_JUDGE]->(j);

// Canonical presentation decisions are materialized under:
// run:blockchain:evidence-presentation:2026-08-31:v3
// Queue statuses intentionally fail closed:
// PENDING_XPATH | BLOCKED_UPSTREAM_EVIDENCE_JUDGE | EVIDENCE_GAP.
// See expertises/blockchain/llm-judge-graph-sync-v3.yaml for the exact current mapping.
