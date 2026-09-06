-- All 255 configurations
SELECT * FROM v_permutation_summary ORDER BY permutation_id;

-- Configurations containing a specific brick
SELECT DISTINCT p.permutation_id, p.label
FROM offer_permutations p
JOIN v_permutation_bricks pb ON pb.permutation_id = p.permutation_id
WHERE pb.brick_id = 'DS-CLAIM-GRAPH'
ORDER BY p.permutation_id;

-- Offers using the matched benchmark harness
SELECT o.config_id, o.offer_name, ob.sequence_no
FROM offer_bricks ob
JOIN offers o ON o.config_id = ob.config_id
WHERE ob.brick_id = 'DC-BENCH-HARNESS'
ORDER BY o.product_id, o.tier_id;

-- Section → primary brick → evidence
SELECT *
FROM v_product_section_evidence
WHERE product_code = 'DS' AND token = 4;

-- Evidence inherited by a commercial composition
SELECT *
FROM v_permutation_evidence_candidates
WHERE permutation_id = 'PERM-255'
ORDER BY product_id, evidence_id;

-- Compact cross-product bundles
SELECT *
FROM v_permutation_summary
WHERE scope = 'cross_product'
  AND offer_count <= 4
  AND distinct_brick_count <= 12
ORDER BY offer_count, distinct_brick_count, permutation_id;
