// NeoFort migration — copy-claim loop v1.2 topology-preserving
// DDD / DRY / Open-Closed / PECS-compatible extension of v1.1.

MERGE (bc:BoundedContext {id:'BC-COPY-CLAIM-UPGRADE'})
SET bc.name='Copy Claim Upgrade', bc.current=true;

MATCH (old) WHERE old.id='loop:copy-claim:external-capability-v1.1'
SET old.current=false;
MATCH (oldj) WHERE oldj.id='judge:copy-claim:external-capability-grounding-v1.1'
SET oldj.current=false;

MERGE (loop:Loop {id:'loop:copy-claim:external-capability-v1.2-topology-preserving'})
SET loop.version='1.2',
    loop.current=true,
    loop.fail_closed=true,
    loop.topology_preserving=true,
    loop.body_replacement_forbidden=true,
    loop.visible_copy_wholesale_replacement_forbidden=true,
    loop.sequence_upgrade_rule='existing sequence -> external research -> semantic compression -> capability boundary -> 3-replica judge -> targeted patch only',
    loop.source_section_formula='distinct_external_research_sources / selected_research_anchor_sections',
    loop.source_section_threshold=0.72,
    loop.source_section_comparator='STRICT_GREATER_THAN',
    loop.updated_at=datetime();

MERGE (judge:LLMJudge {id:'judge:copy-claim:external-capability-grounding-v1.2'})
SET judge.version='1.2',
    judge.current=true,
    judge.fail_closed=true,
    judge.replica_count=3,
    judge.numeric_reducer='MIN',
    judge.boolean_reducer='AND',
    judge.score_threshold=92,
    judge.source_section_formula='source_count / section_count',
    judge.source_section_threshold=0.72,
    judge.source_section_comparator='STRICT_GREATER_THAN',
    judge.requires_topology_preservation=true,
    judge.requires_external_semantic_compression=true,
    judge.requires_capability_invariant_anchor=true,
    judge.requires_semi_mobile_product_consistency=true,
    judge.updated_at=datetime();

MERGE (inv:Invariant {id:'invariant:copy-topology-preservation-v1'})
SET inv.name='Landing-page topology preservation',
    inv.rule='Preserve section order, section IDs, navigation, CTA topology, EU/EUG DOM and visible composition; wholesale body/main replacement is forbidden',
    inv.fail_closed=true,
    inv.current=true;

MERGE (gate:ValidationGate {id:'gate:sources-per-section:strict-0.72-v1'})
SET gate.formula='source_count / section_count',
    gate.threshold=0.72,
    gate.comparator='STRICT_GREATER_THAN',
    gate.zero_section_policy='FAIL_CLOSED',
    gate.current=true;

MERGE (bc)-[:OWNS]->(loop)
MERGE (bc)-[:OWNS]->(judge)
MERGE (loop)-[:USES_JUDGE]->(judge)
MERGE (loop)-[:ENFORCES]->(inv)
MERGE (judge)-[:ENFORCES]->(inv)
MERGE (judge)-[:USES_GATE]->(gate);

MATCH (cap) WHERE cap.id='capability-invariant:cv-derived:2026-09-03'
MERGE (loop)-[:BOUNDED_BY]->(cap);
MATCH (commercial) WHERE commercial.id='commercial-context:catalogue:2026-09-03'
MERGE (loop)-[:SPECIALIZES_WITH]->(commercial);

MERGE (batch:Batch {id:'batch:copywriting:all-html:external-capability-v1.2:2026-09-03'})
SET batch.repo='mckeopharma-web/copywriting',
    batch.glob='**/*.html',
    batch.html_total=27,
    batch.topology_preserved=true,
    batch.source_section_gate_pass=true,
    batch.min_ratio=1.0,
    batch.status='MATERIALIZED_PENDING_FORMAL_LLM_JUDGE',
    batch.branch='recovery/topology-preserving-v1.2-2026-09-03',
    batch.updated_at=datetime()
MERGE (batch)-[:EXECUTES]->(loop);
