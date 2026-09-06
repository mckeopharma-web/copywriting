INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('CAP-RUST', 17);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('CAP-RUST', 18);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('CAP-ZK-ZKML', 17);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('CAP-ZK-ZKML', 18);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('EG-DC-EXECUTION-RECEIPT', 6);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('EG-DC-EXECUTION-RECEIPT', 13);
INSERT INTO evidence_sections (evidence_id, section_id) VALUES ('EG-DC-EXECUTION-RECEIPT', 16);

-- canon_rules
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (1, '23-section lock', 'Both new pages must preserve canonical token order: 0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (2, 'Source-first modularity', 'Reuse or adapt owner assets before inventing new copy/mechanisms; hard structural changes require owner-source update.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (3, 'Evidence posture', 'FAIL_CLOSED. External factual claims require current source, explicit epistemic status and claim boundary.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (4, 'LLM judge execution', 'temperature=0, top_p=1, replicas=3, unanimous hard gate when formal execution is available.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (5, 'Quantitative claims', 'Require variable + value + unit + population + period + source + boundary; no silent interpolation.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (6, 'Evidence Graphic', 'EUG requires metric contract, source closure and enough datapoints; label OBSERVED / DERIVED / PLANNED / FORECAST.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (7, 'Decentralization test', 'If a conventional database/cloud architecture satisfies the verifier/trust/workload requirement, prefer it.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (8, 'Sensitive health data', 'Do not place patient-level/raw sensitive health data on-chain by default; separate data plane from verification/provenance plane.');
INSERT INTO canon_rules (rule_id, rule_name, implementation) VALUES (9, 'Claim discipline', 'Attestation proves the attested property, not scientific truth, clinical validity, ROI, security efficacy or universal performance.');

-- source_assets
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (1, 'Source-first Atomic Design v4', 'https://github.com/mckeopharma-web/copywriting/blob/main/.skills/source-first-atomic-design-v4/SKILL.md');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (2, 'Data Engineering canonical copy', 'https://github.com/mckeopharma-web/copywriting/blob/main/expertises/data-engineering/data-engineering.copywriting.json');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (3, 'HealthTech Product canonical copy', 'https://github.com/mckeopharma-web/copywriting/blob/main/expertises/healthtech-product/healthtech-product.copywriting.json');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (4, 'AI Security canonical copy', 'https://github.com/mckeopharma-web/copywriting/blob/main/expertises/ai-security/ai-security.copywriting.json');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (5, 'Agentic AI assets', 'https://github.com/mckeopharma-web/copywriting/tree/main/expertises/agentic-ai');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (6, 'Blockchain assets', 'https://github.com/mckeopharma-web/copywriting/tree/main/expertises/blockchain');
INSERT INTO source_assets (source_asset_id, name, url_path) VALUES (7, 'Live expertise catalogue', 'https://mickael-umt.com/expertises/');

-- decision_layers
INSERT INTO decision_layers (decision_id, label, question, desci_guidance, compute_guidance, default_action, rationale) VALUES (1, '1. Need', 'What must another party verify?', 'Scientific claim / provenance / reproducibility', 'Execution / environment / result', 'Start here', 'Prevents technology-led solutioning');
INSERT INTO decision_layers (decision_id, label, question, desci_guidance, compute_guidance, default_action, rationale) VALUES (2, '2. Centralized sufficiency', 'Can one trusted operator satisfy it?', 'Often yes for raw data', 'Often yes for ordinary workloads', 'Prefer simpler system', 'Decentralization must earn its complexity');
INSERT INTO decision_layers (decision_id, label, question, desci_guidance, compute_guidance, default_action, rationale) VALUES (3, '3. Trust boundary', 'Which parties cannot simply trust each other?', 'Researchers / institutions / reviewers / funders', 'Providers / users / verifiers / schedulers', 'Map explicitly', 'Defines the minimum mechanism');
INSERT INTO decision_layers (decision_id, label, question, desci_guidance, compute_guidance, default_action, rationale) VALUES (4, '4. Evidence', 'What proves the property?', 'Evidence graph + reproducibility + attestations', 'Execution receipt + attestation + matched benchmark', 'Machine-readable', 'Supports independent inspection');
INSERT INTO decision_layers (decision_id, label, question, desci_guidance, compute_guidance, default_action, rationale) VALUES (5, '5. Acceptance', 'How do we know the service delivered?', 'Traversable claim path + reproducible bounded run', 'Matched workload + verifiable receipt + failure test', 'Pre-written', 'Avoids post-hoc success criteria');

-- composer_meta
INSERT INTO composer_meta (meta_key, meta_value) VALUES ('title', 'Product Composer — Decentralized Science + Decentralized Compute');
INSERT INTO composer_meta (meta_key, meta_value) VALUES ('purpose', 'Purpose: compose two new specialized expertise products from reusable assets + net-new domain modules before generating canonical 23-section JSON.');
INSERT INTO composer_meta (meta_key, meta_value) VALUES ('next_step', 'Next step: use this workbook to emit 2 canonical JSON page files (23 sections each) + 1 offer-config JSON file, then run @neofort admission/placement rules.');
INSERT INTO composer_meta (meta_key, meta_value) VALUES ('source_workbook', 'decentralized_product_composer.xlsx');

-- permutation_rules
INSERT INTO permutation_rules (rule_id, rule_name, rule_text) VALUES (1, 'Per-product ladder continuity', 'For each product, a configuration may select no offer or one contiguous interval of the 5-stage ladder; gaps are not generated.');
INSERT INTO permutation_rules (rule_id, rule_name, rule_text) VALUES (2, 'Cross-product composition', 'DeSci and Compute intervals are selected independently and may be combined in the same configuration.');
INSERT INTO permutation_rules (rule_id, rule_name, rule_text) VALUES (3, 'No invented module optionality', 'Each selected offer inherits its workbook-defined brick list exactly; brick-level optionality is not inferred.');
INSERT INTO permutation_rules (rule_id, rule_name, rule_text) VALUES (4, 'Canonical order preservation', 'Offer stages remain in workbook ladder order: Diagnostic, Architecture Sprint, PoC, Implementation, Assurance.');
