// Blockchain Evidence Presentation / Progressive Disclosure v2
// Safe design intent: creates policy + proposed presentation decisions.
// It does NOT publish or replace current EvidencePlacements.

MERGE (p:EvidencePresentationPolicy {id:'policy:evidence-presentation:progressive-disclosure-v1'})
SET p.version = '1.0',
    p.current = true,
    p.scope = 'https://mickael-umt.com/expertises/blockchain/',
    p.objective = 'Preserve landing-page commercial rhythm while keeping every factual claim traceable to an admitted EvidenceUnit and verified primary source.',
    p.level_1 = 'L1_DECISION',
    p.level_2 = 'L2_EVIDENCE',
    p.default_render_mode = 'SILENT_CITATION',
    p.render_modes = ['SILENT_CITATION','METRIC_CHIP','INLINE_NUMBER','SOURCE_AUTHORITY'],
    p.internal_route_template = '/evidence/{eu_id}/',
    p.visible_citation_style = 'NUMERIC_SUPERSCRIPT',
    p.hover_only_forbidden = true,
    p.keyboard_required = true,
    p.touch_required = true,
    p.updated_at = datetime();

MERGE (j:EvidencePlacementPresentationJudge {id:'judge:evidence-placement:presentation-v1'})
SET j.current = true,
    j.fail_closed = true,
    j.semantic_fit_weight = 0.30,
    j.executive_readability_weight = 0.25,
    j.rhythm_continuity_weight = 0.20,
    j.traceability_weight = 0.15,
    j.progressive_disclosure_accessibility_weight = 0.10,
    j.hard_gates = [
      'l1_claim_entailed_by_admitted_eu',
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
    j.updated_at = datetime();

MERGE (run:EvidencePresentationRun {id:'run:blockchain:evidence-presentation:2026-08-31:v2'})
SET run.current = true,
    run.status = 'PROPOSED_NOT_PUBLISHED',
    run.page_url = 'https://mickael-umt.com/expertises/blockchain/',
    run.updated_at = datetime()
MERGE (run)-[:USES_PRESENTATION_POLICY]->(p)
MERGE (run)-[:REQUIRES_PRESENTATION_JUDGEMENT_BY]->(j);

WITH run
UNWIND [
  {seq:'seq:blockchain:hero:h1', mode:'METRIC_CHIP', eu:'EU-MACRO-TOKENIZED-ASSETS-GROWTH-5X-2025-2026', copy:'Rendez les décisions et transactions vérifiables sans sur-construire l’infrastructure.'},
  {seq:'seq:blockchain:proposition:mechanism', mode:'METRIC_CHIP', eu:'EU-MACRO-TOKENIZED-ASSETS-23.3B-2026Q1', copy:'Le cadrage peut conclure à une blockchain, une attestation, une preuve ZK — ou à aucune blockchain. Je pars de la propriété à prouver, puis du mécanisme le plus simple qui la rend vérifiable.'},
  {seq:'seq:blockchain:consequences:platform-first', mode:'SILENT_CITATION', eu:'EU-MACRO-STABLECOIN-PAYMENT-390B-2025', copy:'Le choix de plateforme vient après le flux économique, les contreparties et la propriété à vérifier.'},
  {seq:'seq:blockchain:consequence:key-governance', mode:'SILENT_CITATION', eu:'EU-AFT-KEY-RECOVERY-CORPUS-2026', copy:'Les droits de signature, de révocation et de reprise sont spécifiés avant le déploiement — pas après l’incident.'},
  {seq:'seq:blockchain:consequences:multisig-governance', mode:'SILENT_CITATION', eu:'EU-BC-EIP7702-MALICIOUS-AUTH-2026', copy:'Un multisig fixe un seuil. La gouvernance définit l’autorité, l’exception et la reprise.'},
  {seq:'seq:blockchain:consequence:history', mode:'SILENT_CITATION', eu:'EU-CROSBY-PROOF-VERIFY-2009', copy:'Signer un fichier ne prouve pas la continuité de son historique.'},
  {seq:'seq:blockchain:engagements:crypto-not-audit', mode:'SILENT_CITATION', eu:null, copy:'Une preuve cryptographique démontre une propriété ; elle ne remplace ni audit, ni gouvernance, ni contrôle.'},
  {seq:'seq:blockchain:functional:selective-disclosure', mode:'METRIC_CHIP', eu:'EU-JISA-BBS-VERIFY-2024', copy:'Rendez la propriété nécessaire vérifiable sans publier les données qui n’ont pas à l’être.'},
  {seq:'seq:blockchain:trigger:privacy', mode:'SILENT_CITATION', eu:'EU-ZKSA-VERIFY-2021', copy:'Un partenaire peut vérifier l’affirmation sans recevoir le secret qui la fonde.'},
  {seq:'seq:blockchain:resultats:independent-verifier', mode:'SILENT_CITATION', eu:'EU-MACRO-APPIA-PARTICIPANTS-61-2026', copy:'Le résultat reste vérifiable sans dépendre de l’opérateur qui l’a produit.'}
] AS row
MATCH (cs:CopySequence {id:row.seq})
MERGE (d:EvidencePresentationDecision {id:'presentation:blockchain:v2:' + row.seq})
SET d.sequence_id = row.seq,
    d.render_mode = row.mode,
    d.eu_id = row.eu,
    d.l1_copy = row.copy,
    d.presentation_level = 'L1_DECISION',
    d.source_visibility = 'ON_DEMAND',
    d.status = 'PROPOSED_NOT_PUBLISHED',
    d.updated_at = datetime()
MERGE (run)-[:HAS_PRESENTATION_DECISION]->(d)
MERGE (d)-[:FOR_COPY_SEQUENCE]->(cs)
WITH d,row
OPTIONAL MATCH (eu:EvidenceUnit {id:row.eu})
FOREACH (_ IN CASE WHEN eu IS NULL THEN [] ELSE [1] END |
  MERGE (d)-[:DISCLOSES_EVIDENCE_UNIT]->(eu)
);

// Aliases must not create public citation markers.
UNWIND [
  {seq:'seq:blockchain:consequences:history-integrity', canonical:'seq:blockchain:consequence:history'},
  {seq:'seq:blockchain:proposition:onchain-offchain', canonical:'seq:blockchain:functional:selective-disclosure'}
] AS a
MATCH (cs:CopySequence {id:a.seq})
MERGE (d:EvidencePresentationDecision {id:'presentation:blockchain:v2:' + a.seq})
SET d.sequence_id = a.seq,
    d.render_mode = 'ALIAS_NO_PUBLIC_CITATION',
    d.canonical_sequence_id = a.canonical,
    d.status = 'PROPOSED_NOT_PUBLISHED',
    d.updated_at = datetime()
WITH d,a
MATCH (canonical:CopySequence {id:a.canonical})
MERGE (d)-[:ALIASES_PRESENTATION_OF]->(canonical);
