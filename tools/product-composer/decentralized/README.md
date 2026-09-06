# Decentralized Product Composer — relational database

Source of truth: `decentralized_product_composer.xlsx`.

This package normalizes the workbook into a SQLite-compatible relational model covering products, the five-stage offer ladder, offers, reusable/new bricks, canonical 23-section composition, evidence, rules, decision layers, and generated commercial configurations.

## Permutation policy

Each product has the ordered commercial ladder:

`Diagnostic → Architecture Sprint → PoC → Implementation → Assurance`

A valid selection for one product is either empty or one contiguous interval of that ladder. A five-stage ladder has 15 non-empty contiguous intervals; including the empty state yields 16 states per product. Across Decentralized Science and Decentralized Compute:

`16 × 16 − 1 = 255`

`generate_permutations.py` therefore materializes **255 commercially coherent configurations** and **1,120 configuration-to-offer relations**.

This is deliberately not the raw power set. It avoids inventing gaps such as Diagnostic + Implementation without the intermediate stages, and it does not invent brick-level optionality absent from the workbook.

## Relational coverage

- 2 products
- 5 offer tiers
- 10 base offers
- 36 bricks
- 43 offer ↔ brick relations
- 23 canonical sections
- 46 product ↔ section compositions
- 12 evidence objects
- 9 canonical rules
- 7 source assets
- 5 decision-layer records
- 255 generated offer permutations

Validation of the generated database: `PRAGMA foreign_key_check` = PASS; `PRAGMA integrity_check` = `ok`.

## Files

- `schema.sql` — tables, foreign keys, CHECK constraints and indexes.
- `seed/core_*.sql` — deterministic workbook-derived relational seed data.
- `generate_permutations.py` — deterministic 255-configuration generator.
- `views.sql` — offer/module, permutation and evidence traversal views.
- `queries.sql` — example decision queries.
- `erd.mmd` — Mermaid ER diagram.
- `build_db.py` — creates and validates `decentralized_product_composer.sqlite`.
- `manifest.json` — source hash, counts, permutation policy and validation status.

## Build

```bash
python build_db.py
```

## Design boundary

The workbook lists bricks per offer but does not identify brick cardinality, optional/mandatory status, substitution groups or incompatibility constraints. Every listed brick is therefore treated as required for that base offer. Add module-level permutations only after those constraints are explicitly modeled.
