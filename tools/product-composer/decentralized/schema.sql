PRAGMA foreign_keys = ON;

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    reuse_adapt TEXT,
    new_specific TEXT,
    architecture_thesis TEXT NOT NULL,
    sections_count INTEGER NOT NULL CHECK (sections_count = 23),
    reuse_weight_count INTEGER NOT NULL,
    new_sections_count INTEGER NOT NULL,
    compose_adapt_sections_count INTEGER NOT NULL
);

CREATE TABLE offer_tiers (
    tier_id INTEGER PRIMARY KEY,
    tier_name TEXT NOT NULL UNIQUE,
    stage_order INTEGER NOT NULL UNIQUE CHECK (stage_order BETWEEN 1 AND 5)
);

CREATE TABLE canonical_sections (
    section_id INTEGER PRIMARY KEY,
    canonical_order INTEGER NOT NULL UNIQUE CHECK (canonical_order BETWEEN 1 AND 23),
    token INTEGER NOT NULL UNIQUE,
    section_key TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    semantic_role TEXT NOT NULL
);

CREATE TABLE bricks (
    brick_id TEXT PRIMARY KEY,
    asset_class TEXT NOT NULL,
    name TEXT NOT NULL,
    source_expertise TEXT NOT NULL,
    source_asset TEXT,
    intended_function TEXT NOT NULL,
    reuse_mode TEXT NOT NULL CHECK (reuse_mode IN ('REUSE','ADAPT','NEW')),
    target_product_raw TEXT NOT NULL,
    canonical_tokens_raw TEXT NOT NULL,
    technical_object TEXT NOT NULL,
    evidence_requirement TEXT NOT NULL,
    composition_note TEXT,
    source_url TEXT
);

CREATE TABLE brick_products (
    brick_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    PRIMARY KEY (brick_id, product_id),
    FOREIGN KEY (brick_id) REFERENCES bricks(brick_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE brick_sections (
    brick_id TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    PRIMARY KEY (brick_id, section_id),
    FOREIGN KEY (brick_id) REFERENCES bricks(brick_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES canonical_sections(section_id) ON DELETE CASCADE
);

CREATE TABLE product_sections (
    product_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    primary_brick_id TEXT NOT NULL,
    build_strategy TEXT NOT NULL CHECK (build_strategy IN ('REUSE','ADAPT','NEW','COMPOSE')),
    thesis TEXT NOT NULL,
    composition_note TEXT,
    reuse_weight REAL NOT NULL CHECK (reuse_weight >= 0 AND reuse_weight <= 1),
    evidence_rule TEXT NOT NULL,
    PRIMARY KEY (product_id, section_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES canonical_sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (primary_brick_id) REFERENCES bricks(brick_id)
);

CREATE TABLE offers (
    config_id TEXT PRIMARY KEY,
    product_id INTEGER NOT NULL,
    tier_id INTEGER NOT NULL,
    offer_name TEXT NOT NULL,
    buyer_trigger TEXT NOT NULL,
    outcome TEXT NOT NULL,
    modules_raw TEXT NOT NULL,
    deliverables TEXT NOT NULL,
    typical_format TEXT NOT NULL,
    commercial_model TEXT NOT NULL,
    reusable_core TEXT NOT NULL,
    specific_core TEXT NOT NULL,
    entry_criteria TEXT NOT NULL,
    exit_acceptance TEXT NOT NULL,
    explicit_exclusions TEXT NOT NULL,
    evidence_contract TEXT NOT NULL,
    UNIQUE (product_id, tier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (tier_id) REFERENCES offer_tiers(tier_id)
);

CREATE TABLE offer_bricks (
    config_id TEXT NOT NULL,
    brick_id TEXT NOT NULL,
    sequence_no INTEGER NOT NULL CHECK (sequence_no >= 1),
    PRIMARY KEY (config_id, brick_id),
    UNIQUE (config_id, sequence_no),
    FOREIGN KEY (config_id) REFERENCES offers(config_id) ON DELETE CASCADE,
    FOREIGN KEY (brick_id) REFERENCES bricks(brick_id)
);

CREATE TABLE evidence_items (
    evidence_id TEXT PRIMARY KEY,
    evidence_type TEXT NOT NULL,
    status TEXT NOT NULL,
    epistemic_class TEXT NOT NULL,
    supported_use TEXT NOT NULL,
    boundary_non_claim TEXT NOT NULL,
    target_tokens_raw TEXT,
    source_url TEXT
);

CREATE TABLE evidence_products (
    evidence_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    PRIMARY KEY (evidence_id, product_id),
    FOREIGN KEY (evidence_id) REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE evidence_sections (
    evidence_id TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    PRIMARY KEY (evidence_id, section_id),
    FOREIGN KEY (evidence_id) REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES canonical_sections(section_id) ON DELETE CASCADE
);

CREATE TABLE canon_rules (
    rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL UNIQUE,
    implementation TEXT NOT NULL
);

CREATE TABLE source_assets (
    source_asset_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url_path TEXT NOT NULL
);

CREATE TABLE decision_layers (
    decision_id INTEGER PRIMARY KEY,
    label TEXT NOT NULL UNIQUE,
    question TEXT NOT NULL,
    desci_guidance TEXT NOT NULL,
    compute_guidance TEXT NOT NULL,
    default_action TEXT NOT NULL,
    rationale TEXT NOT NULL
);

CREATE TABLE composer_meta (
    meta_key TEXT PRIMARY KEY,
    meta_value TEXT NOT NULL
);

CREATE TABLE permutation_rules (
    rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL UNIQUE,
    rule_text TEXT NOT NULL
);

CREATE TABLE offer_permutations (
    permutation_id TEXT PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    scope TEXT NOT NULL CHECK (scope IN ('single_product','cross_product')),
    ds_start_stage INTEGER,
    ds_end_stage INTEGER,
    dc_start_stage INTEGER,
    dc_end_stage INTEGER,
    product_count INTEGER NOT NULL CHECK (product_count BETWEEN 1 AND 2),
    offer_count INTEGER NOT NULL CHECK (offer_count BETWEEN 1 AND 10),
    CHECK ((ds_start_stage IS NULL AND ds_end_stage IS NULL) OR
           (ds_start_stage BETWEEN 1 AND 5 AND ds_end_stage BETWEEN ds_start_stage AND 5)),
    CHECK ((dc_start_stage IS NULL AND dc_end_stage IS NULL) OR
           (dc_start_stage BETWEEN 1 AND 5 AND dc_end_stage BETWEEN dc_start_stage AND 5)),
    FOREIGN KEY (ds_start_stage) REFERENCES offer_tiers(stage_order),
    FOREIGN KEY (ds_end_stage) REFERENCES offer_tiers(stage_order),
    FOREIGN KEY (dc_start_stage) REFERENCES offer_tiers(stage_order),
    FOREIGN KEY (dc_end_stage) REFERENCES offer_tiers(stage_order)
);

CREATE TABLE permutation_offers (
    permutation_id TEXT NOT NULL,
    config_id TEXT NOT NULL,
    sequence_no INTEGER NOT NULL CHECK (sequence_no >= 1),
    PRIMARY KEY (permutation_id, config_id),
    UNIQUE (permutation_id, sequence_no),
    FOREIGN KEY (permutation_id) REFERENCES offer_permutations(permutation_id) ON DELETE CASCADE,
    FOREIGN KEY (config_id) REFERENCES offers(config_id)
);

CREATE INDEX idx_offers_product_tier ON offers(product_id, tier_id);
CREATE INDEX idx_offer_bricks_brick ON offer_bricks(brick_id);
CREATE INDEX idx_product_sections_brick ON product_sections(primary_brick_id);
CREATE INDEX idx_evidence_sections_section ON evidence_sections(section_id);
CREATE INDEX idx_perm_offers_config ON permutation_offers(config_id);
