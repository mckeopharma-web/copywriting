// /expertises/blockchain/ — programmability EUP/EUGP triage v3
// Revision: 2026-09-01
// Purpose: materialise COPYWRITING TRIAGE only. This does not assert that the live DOM has changed.

MATCH (p:WebPage {id:'page:source:8.1'})
MERGE (s:PageSection {id:'section:blockchain:delivery-performance'})
SET s.title='Delivery performance — what programmability changes',
    s.order=6,
    s.current=false,
    s.page_id=p.id,
    s.page_url=p.url,
    s.source_of_truth='COPYWRITING_TRIAGE_PROPOSED',
    s.render_condition='SITE_NOT_YET_MODIFIED',
    s.provenance='programmability-eu-eug-triage-v3'
MERGE (p)-[:PAGE_CONTAINS_SECTION]->(s);

// Proposed trigger sequences. token_count intentionally remains null until tokenizer materialisation.
MATCH (s:PageSection {id:'section:blockchain:triggers'})
UNWIND [
  {component_id:'component:blockchain:triggers:coordination', subcomponent_id:'subcomponent:blockchain:triggers:coordination:copy', sequence_id:'seq:blockchain:trigger:coordination', order:1, role:'COORDINATION_TRIGGER', buyer:'Quand la coordination multi-organisations justifie-t-elle un mécanisme programmable partagé ?', text:'Plusieurs organisations maintiennent le même état ou doivent se transmettre des décisions interdépendantes : la friction se déplace vers le messaging, la reconciliation, les exceptions et l’autorité de mise à jour.'},
  {component_id:'component:blockchain:triggers:conditional-execution', subcomponent_id:'subcomponent:blockchain:triggers:conditional-execution:copy', sequence_id:'seq:blockchain:trigger:conditional-execution', order:2, role:'EXECUTION_TRIGGER', buyer:'Quand des conditions vérifiables et des transitions interdépendantes justifient-elles une exécution programmable ?', text:'Une transaction dépend de conditions vérifiables et plusieurs transitions doivent rester cohérentes : formalisez les conditions, les états autorisés et les voies d’exception avant de choisir le rail d’exécution.'}
] AS row
MERGE (c:UIComponent {id:row.component_id})
SET c.component_type='programmability-trigger', c.current=false, c.section_id=s.id, c.order=row.order, c.provenance='programmability-eu-eug-triage-v3'
MERGE (s)-[:SECTION_CONTAINS_COMPONENT]->(c)
MERGE (sc:CopySubcomponent {id:row.subcomponent_id})
SET sc.name='copy', sc.current=false, sc.component_id=c.id, sc.provenance='programmability-eu-eug-triage-v3'
MERGE (c)-[:COMPONENT_CONTAINS_SUBCOMPONENT]->(sc)
MERGE (seq:CopySequence {id:row.sequence_id})
SET seq.page_id='page:source:8.1', seq.page_url='https://mickael-umt.com/expertises/blockchain/',
    seq.section_id=s.id, seq.component_id=c.id, seq.subcomponent_id=sc.id,
    seq.current=false, seq.sequence_order=row.order, seq.semantic_role=row.role,
    seq.buyer_question=row.buyer, seq.text=row.text,
    seq.target_xpath='//*[@data-copy-seq="'+row.sequence_id+'"]',
    seq.xpath_status='PROPOSED_DOM_CONTRACT__NOT_IN_CURRENT_SITE',
    seq.token_count=null, seq.provenance='programmability-eu-eug-triage-v3'
MERGE (sc)-[:SUBCOMPONENT_EMITS_SEQUENCE]->(seq);

// Proposed delivery-performance sequences.
MATCH (s:PageSection {id:'section:blockchain:delivery-performance'})
UNWIND [
  {component_id:'component:blockchain:delivery:settlement', subcomponent_id:'subcomponent:blockchain:delivery:settlement:copy', sequence_id:'seq:blockchain:delivery-performance:settlement', order:1, role:'DELIVERY_SPEED_EVIDENCE', buyer:'Quelle vitesse de settlement a été observée dans un test institutionnel programmable ?', text:'Settlement speed — observed real-value test.'},
  {component_id:'component:blockchain:delivery:cost', subcomponent_id:'subcomponent:blockchain:delivery:cost:copy', sequence_id:'seq:blockchain:delivery-performance:cost', order:2, role:'DELIVERY_COST_EVIDENCE', buyer:'Quelle structure de frais de delivery est publiée pour le lancement de Pontes ?', text:'Delivery cost — Initial Launch fee structure.'},
  {component_id:'component:blockchain:delivery:availability', subcomponent_id:'subcomponent:blockchain:delivery:availability:copy', sequence_id:'seq:blockchain:delivery-performance:availability', order:3, role:'OPERATING_MODEL_EVIDENCE', buyer:'Comment la fenêtre opératoire planifiée évolue-t-elle ?', text:'Operating model — planned service availability.'}
] AS row
MERGE (c:UIComponent {id:row.component_id})
SET c.component_type='delivery-performance-eug', c.current=false, c.section_id=s.id, c.order=row.order, c.provenance='programmability-eu-eug-triage-v3'
MERGE (s)-[:SECTION_CONTAINS_COMPONENT]->(c)
MERGE (sc:CopySubcomponent {id:row.subcomponent_id})
SET sc.name='copy', sc.current=false, sc.component_id=c.id, sc.provenance='programmability-eu-eug-triage-v3'
MERGE (c)-[:COMPONENT_CONTAINS_SUBCOMPONENT]->(sc)
MERGE (seq:CopySequence {id:row.sequence_id})
SET seq.page_id='page:source:8.1', seq.page_url='https://mickael-umt.com/expertises/blockchain/',
    seq.section_id=s.id, seq.component_id=c.id, seq.subcomponent_id=sc.id,
    seq.current=false, seq.sequence_order=row.order, seq.semantic_role=row.role,
    seq.buyer_question=row.buyer, seq.text=row.text,
    seq.target_xpath='//*[@data-copy-seq="'+row.sequence_id+'"]',
    seq.xpath_status='PROPOSED_DOM_CONTRACT__NOT_IN_CURRENT_SITE',
    seq.token_count=null, seq.provenance='programmability-eu-eug-triage-v3'
MERGE (sc)-[:SUBCOMPONENT_EMITS_SEQUENCE]->(seq);

// Proposed second Results component: assurance coverage.
MATCH (s:PageSection {id:'section:blockchain:resultats'})
MERGE (c:UIComponent {id:'component:blockchain:resultats:assurance-coverage'})
SET c.component_type='assurance-coverage', c.current=false, c.section_id=s.id, c.order=2, c.provenance='programmability-eu-eug-triage-v3'
MERGE (s)-[:SECTION_CONTAINS_COMPONENT]->(c)
MERGE (sc:CopySubcomponent {id:'subcomponent:blockchain:resultats:assurance-coverage:copy'})
SET sc.name='copy', sc.current=false, sc.component_id=c.id, sc.provenance='programmability-eu-eug-triage-v3'
MERGE (c)-[:COMPONENT_CONTAINS_SUBCOMPONENT]->(sc)
MERGE (seq:CopySequence {id:'seq:blockchain:resultats:assurance-coverage'})
SET seq.page_id='page:source:8.1', seq.page_url='https://mickael-umt.com/expertises/blockchain/',
    seq.section_id=s.id, seq.component_id=c.id, seq.subcomponent_id=sc.id,
    seq.current=false, seq.sequence_order=2, seq.semantic_role='ASSURANCE_COVERAGE',
    seq.buyer_question='Comment démontrer une assurance reproductible sans prétendre qu’un outil unique couvre toute la surface de vulnérabilité ?',
    seq.text='L’assurance n’est pas un outil unique : le résultat attendu est une chaîne de vérification documentée, reproductible et bornée.',
    seq.target_xpath='//*[@data-copy-seq="seq:blockchain:resultats:assurance-coverage"]',
    seq.xpath_status='PROPOSED_DOM_CONTRACT__NOT_IN_CURRENT_SITE',
    seq.token_count=null, seq.provenance='programmability-eu-eug-triage-v3'
MERGE (sc)-[:SUBCOMPONENT_EMITS_SEQUENCE]->(seq);

// New EUG placements.
MATCH (p:WebPage {id:'page:source:8.1'})
UNWIND [
  {id:'eugp:blockchain:consequences:db-vs-dlt-throughput:2026-09-01', section_id:'section:blockchain:consequences', sequence_id:'seq:blockchain:consequences:platform-first', eug_id:'QGEU-DB-VS-DLT-THROUGHPUT-2026', xpath:'//*[contains(normalize-space(.),"Le projet démarre par une plateforme")][not(.//*[contains(normalize-space(.),"Le projet démarre par une plateforme")])]', l1:'Le ledger a un coût. Sous la même charge cible du prototype étudié, le chemin database-backed délivrait 924,79 TPS contre 219,23 TPS ledger-backed. La DLT doit donc être justifiée par coordination, vérification, autorité partagée ou exécution conditionnelle — pas par le stockage seul.'},
  {id:'eugp:blockchain:delivery:settlement-80s:2026-09-01', section_id:'section:blockchain:delivery-performance', sequence_id:'seq:blockchain:delivery-performance:settlement', eug_id:'QGEU-BIS-AGORA-SETTLEMENT-80S-2026', xpath:'//*[@data-copy-seq="seq:blockchain:delivery-performance:settlement"]', l1:'Project Agorá real-value testing reported approximately 80 seconds average initiation-to-settlement across 30 transactions. No matched conventional-payment control is available, so no legacy speedup factor is claimed.'},
  {id:'eugp:blockchain:delivery:pontes-cost:2026-09-01', section_id:'section:blockchain:delivery-performance', sequence_id:'seq:blockchain:delivery-performance:cost', eug_id:'QGEU-ECB-PONTES-DELIVERY-COST-STRUCTURE-2026', xpath:'//*[@data-copy-seq="seq:blockchain:delivery-performance:cost"]', l1:'Pontes Initial Launch pricing publishes €2,500 one-off connection for a market participant, €15,000 for a Market DLT Operator, €0 fixed monthly fee and €0 settlement fee. Initial Launch pricing is not total cost of ownership.'},
  {id:'eugp:blockchain:delivery:pontes-availability:2026-09-01', section_id:'section:blockchain:delivery-performance', sequence_id:'seq:blockchain:delivery-performance:availability', eug_id:'QGEU-ECB-PONTES-AVAILABILITY-ROADMAP-2026-2028', xpath:'//*[@data-copy-seq="seq:blockchain:delivery-performance:availability"]', l1:'ECB plans Pontes operating availability at 22.5 hours per business day and then 24/7 by mid-2028. This is a planned official roadmap, not observed uptime or an SLA.'}
] AS row
MATCH (seq:CopySequence {id:row.sequence_id})
MATCH (q:QuestionDrivenGraphEvidenceUnit {id:row.eug_id})
OPTIONAL MATCH (q)-[:RENDERS_WITH]->(g:GraphSpec)
MERGE (ep:EvidencePlacement {id:row.id})
SET ep.page_id=p.id, ep.page_url=p.url, ep.section_id=row.section_id,
    ep.sequence_id=row.sequence_id, ep.eug_id=row.eug_id, ep.qgeu_id=row.eug_id,
    ep.placement_kind='GRAPH_EVIDENCE_UNIT', ep.target_xpath=row.xpath,
    ep.l1_copy=row.l1, ep.publication_status='PROPOSED_TRIAGE__SITE_NOT_MODIFIED',
    ep.xpath_verification_status=CASE WHEN seq.current=false THEN 'PROPOSED_DOM_CONTRACT__NOT_IN_CURRENT_SITE' ELSE 'TEXT_ANCHORED__DOM_ASSERT_PENDING' END,
    ep.selection_trigger='programmability-eu-eug-triage-v3', ep.updated_at='2026-09-01'
MERGE (ep)-[:TARGETS_COPY_SEQUENCE]->(seq)
MERGE (ep)-[:PLACED_ON_PAGE]->(p)
MERGE (ep)-[:PLACES_QGEU]->(q)
FOREACH (_ IN CASE WHEN g IS NULL THEN [] ELSE [1] END | MERGE (ep)-[:USES_GRAPH_SPEC]->(g));

// New / upgraded atomic EU placements.
UNWIND [
  {id:'eup:blockchain:triggers:coordination-mechanism:2026-09-01', section_id:'section:blockchain:triggers', sequence_id:'seq:blockchain:trigger:coordination', eu_id:'EU-ECB-PROGRAMMABILITY-COORDINATION-MECHANISM-2026', kind:'MECHANISM_SUPPORT_EUP', xpath:'//*[@data-copy-seq="seq:blockchain:trigger:coordination"]', copy:'ECB mechanism evidence supports the coordination trigger: programmable repo workflows can automate collateral substitution, margin management and collateral return, reducing messaging, reconciliation and manual intervention. No numeric saving is claimed.'},
  {id:'eup:blockchain:consequences:history-merkle:2026-09-01', section_id:'section:blockchain:consequences', sequence_id:'seq:blockchain:consequence:history', eu_id:'EU-BC-MERKLE-LOG-VERIFY-2026', kind:'EVIDENCE_UNIT', xpath:'//main//*[self::p or self::div][contains(normalize-space(.),"Signer les exports ne suffit pas") and contains(normalize-space(.),"réécriture de l’historique")]', copy:'Une signature atteste un objet ; elle ne prouve pas, à elle seule, la continuité d’un historique. Dans l’évaluation 2026 étudiée, une vérification d’inclusion a été mesurée à 0,000035 s par enregistrement sur des jeux de 10³ à 10⁵ logs, avec 50 répétitions.'},
  {id:'eup:blockchain:resultats:irondict-independent-verification:2026-09-01', section_id:'section:blockchain:resultats', sequence_id:'seq:blockchain:resultats:independent-verifier', eu_id:'EU-BC-IRONDICT-VERIFY-2026', kind:'EVIDENCE_UNIT', xpath:'//*[contains(normalize-space(.),"Un tiers recalcule la preuve sans accès à vos systèmes")][not(.//*[contains(normalize-space(.),"Un tiers recalcule la preuve sans accès à vos systèmes")])]', copy:'IRONDICT rapporte environ 35 ms pour vérifier un dictionnaire transparent configuré pour 1 milliard d’entrées sur laptop grand public, avec des preuves de moins de 8 kB dans le papier.'},
  {id:'eup:blockchain:resultats:solidity-assurance-coverage:2026-09-01', section_id:'section:blockchain:resultats', sequence_id:'seq:blockchain:resultats:assurance-coverage', eu_id:'EU-BC-SOLIDITY-TOOLS-COVERAGE-2026', kind:'EVIDENCE_UNIT', xpath:'//*[@data-copy-seq="seq:blockchain:resultats:assurance-coverage"]', copy:'Sur 2 182 instances Solidity annotées ligne par ligne, trois outils complémentaires détectaient jusqu’à 76,78 % des vulnérabilités du dataset étudié ; aucun outil seul ne couvrait toutes les classes.'}
] AS row
MATCH (seq:CopySequence {id:row.sequence_id})
MATCH (eu:EvidenceUnit {id:row.eu_id})
MERGE (ep:EvidencePlacement {id:row.id})
SET ep.page_id='page:source:8.1', ep.page_url='https://mickael-umt.com/expertises/blockchain/',
    ep.section_id=row.section_id, ep.sequence_id=row.sequence_id, ep.eu_id=row.eu_id,
    ep.placement_kind=row.kind, ep.target_xpath=row.xpath,
    ep.rendered_or_proposed_copy=row.copy,
    ep.publication_status='PROPOSED_TRIAGE__SITE_NOT_MODIFIED',
    ep.xpath_verification_status=CASE WHEN seq.current=false THEN 'PROPOSED_DOM_CONTRACT__NOT_IN_CURRENT_SITE' ELSE 'TEXT_ANCHORED__DOM_ASSERT_PENDING' END,
    ep.selection_trigger='programmability-eu-eug-triage-v3', ep.updated_at='2026-09-01'
MERGE (ep)-[:TARGETS_COPY_SEQUENCE]->(seq)
MERGE (eu)-[:HAS_EVIDENCE_PLACEMENT]->(ep);

// De-prioritise the former generic macro-market layer without deleting its provenance.
MATCH (ep:EvidencePlacement)
WHERE ep.id STARTS WITH 'placement:macro-market:' AND ep.page_id='page:source:8.1'
SET ep.publication_status='SUPERSEDED_BY_PROGRAMMABILITY_TRIAGE_V3',
    ep.selection_trigger='programmability-eu-eug-triage-v3',
    ep.superseded_at='2026-09-01';

MATCH (alias:EvidencePlacement {id:'eup:blockchain:history-integrity:2026-08-31'})
SET alias.publication_status='SUPERSEDED_ALIAS_BY_PROGRAMMABILITY_TRIAGE_V3',
    alias.selection_trigger='programmability-eu-eug-triage-v3',
    alias.alias_of_placement_id='eup:blockchain:consequences:history-merkle:2026-09-01';

MATCH (oldResult:EvidencePlacement {id:'eup:blockchain:independent-verifier:2026-08-31'})
SET oldResult.publication_status='RETAINED_AS_ASSURANCE_SUPPORT__PRIMARY_SUPERSEDED_BY_IRONDICT',
    oldResult.selection_trigger='programmability-eu-eug-triage-v3',
    oldResult.superseded_by_placement_id='eup:blockchain:resultats:irondict-independent-verification:2026-09-01';
