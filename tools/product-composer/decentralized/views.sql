CREATE VIEW v_offer_module_counts AS
SELECT o.config_id, p.product_code, p.name AS product_name, t.stage_order, t.tier_name,
       o.offer_name, COUNT(ob.brick_id) AS brick_count
FROM offers o
JOIN products p ON p.product_id = o.product_id
JOIN offer_tiers t ON t.tier_id = o.tier_id
LEFT JOIN offer_bricks ob ON ob.config_id = o.config_id
GROUP BY o.config_id, p.product_code, p.name, t.stage_order, t.tier_name, o.offer_name;

CREATE VIEW v_permutation_summary AS
SELECT op.permutation_id, op.canonical_key, op.label, op.scope, op.product_count, op.offer_count,
       COUNT(DISTINCT ob.brick_id) AS distinct_brick_count,
       GROUP_CONCAT(DISTINCT po.config_id) AS offer_ids
FROM offer_permutations op
JOIN permutation_offers po ON po.permutation_id = op.permutation_id
LEFT JOIN offer_bricks ob ON ob.config_id = po.config_id
GROUP BY op.permutation_id, op.canonical_key, op.label, op.scope, op.product_count, op.offer_count;

CREATE VIEW v_permutation_bricks AS
SELECT DISTINCT po.permutation_id, ob.brick_id
FROM permutation_offers po
JOIN offer_bricks ob ON ob.config_id = po.config_id;

CREATE VIEW v_product_section_evidence AS
SELECT p.product_code, p.name AS product_name, cs.canonical_order, cs.token, cs.section_key,
       ps.primary_brick_id, ps.build_strategy, e.evidence_id, e.evidence_type, e.status, e.epistemic_class
FROM product_sections ps
JOIN products p ON p.product_id = ps.product_id
JOIN canonical_sections cs ON cs.section_id = ps.section_id
LEFT JOIN evidence_products ep ON ep.product_id = p.product_id
LEFT JOIN evidence_sections es ON es.evidence_id = ep.evidence_id AND es.section_id = cs.section_id
LEFT JOIN evidence_items e ON e.evidence_id = es.evidence_id;

CREATE VIEW v_permutation_evidence_candidates AS
SELECT DISTINCT po.permutation_id, ep.product_id, e.evidence_id, e.evidence_type, e.status,
       e.epistemic_class, e.supported_use, e.boundary_non_claim
FROM permutation_offers po
JOIN offers o ON o.config_id = po.config_id
JOIN evidence_products ep ON ep.product_id = o.product_id
JOIN evidence_items e ON e.evidence_id = ep.evidence_id;
