# Update Plan: expertise/ and programmes/ (v4 Source-First + Atomic Design)

**Date**: 2026-08-12
**Scope**: **`/expertises/`**, **`/expertises/<category>/`**, **`/programme/`**, **`/programme/<slug>/`**
**Mode**: Content refresh + template refactor (Option C), with atomic-design asset priority
**Source of truth**: **`tmp/mysite_landing_page_skills_v4_source_first.zip`** + **`assets/design/design-system/atomic-design/`**

---

## 1. Goal

Bring the **expertise** and **programme** page surfaces into alignment with the v4 source-first design canon (23 semantic sections, source-owner inheritance, design-DNA tokens) while consuming the existing **PrivyPulse atomic design system** as the visual asset layer.

Outcome:

- Every expertise/programme page renders a **complete 23-section buyer journey** (or a justified subset) instead of the current ad-hoc subset.
- Templates, CSS, and content data all reference the same section tokens so they cannot drift.
- Brand visuals come from **`assets/design/design-system/atomic-design/`** (t0–t3), not from ad-hoc inline SVGs or images.

---

## 2. Current State Audit

### 2.1 expertise/ pages

| **PageTemplateSections presentSections missing** |                               |                                                                                         |                                                                                                                                                                                                                                                                          |
| ------------------------------------------------ | ----------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`/expertises/`**                               | **`capabilities.html`**       | hero (0), category switch, cards, capability ranking, benchmark (6), CTA/engagement (7) | triggers(11), problems(20), audience(13), qualification(14), proposition(1), value(2), offers(10), product(15), transformation(3), before_after(12), results(19), proof(4), scope(16), phases(17), modules(18), intersection(21), guarantee(22), faq(23), lead_form(8) |
| **`/expertises/<cat>/`**                         | **`expertise_category.html`** | hero (0), category switch, filtered cards, related capabilities, CTA/engagement (7)     | same as above minus benchmark                                                                                                                                                                                                                                            |

### 2.2 programmes/ pages

| **PageTemplateSections presentSections missing**    |                                              |                                                                                                                                                                                                                                       |                                                                              |
| --------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **`/programme/`**                                   | **`programmes.html`**                        | hero (0), programme cards, fallback card, CTA/engagement (7)                                                                                                                                                                          | almost entire canon — this hub is currently a flat list, not a buyer journey |
| **`/programme/ai-production-assurance/`**           | **`production_assurance.html`**              | rich set (triggers, problems, audience, qualification, proposition, value, offers, product, transformation, before_after, results, proof, scope, phases, modules, capabilities, intersection, benchmark, guarantee, faq, engagement) | lead_form (8)                                                               |
| **`/programme/pharmaceutical-evidence-assurance/`** | **`pharmaceutical_evidence_assurance.html`** | same rich set as above                                                                                                                                                                                                                | lead_form (8)                                                               |

### 2.3 Atomic-design coverage

- **t0-token**: colours, typography, signature motifs (pulse-line, shield-orbit, proof-ring, data-stream, hex-grid, orbit-point) — all present.
- **t3-organism / web**: **`hero-sections-a`**, **`hero-sections-b`**, **`homepage`**, **`landing-brand-framework`**, **`landing-services`** — visual reference sheets exist but are **not yet wired into Django templates**.
- **t4-template**: identity / mediakit / pdf / presentation — not directly relevant.
- **Gap**: no organism-level CSS classes or template partials map these atoms to the 23 canonical sections. The site currently uses ad-hoc class names (**`.offer-hero`**, **`.assurance-hero`**, **`.card`**, etc.).

---

## 3. Design Decisions (resolved)

| **DecisionResolution**       |                                                                                                                                                                                                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Option**                   | **C** — content refresh + template refactor                                                                                                                                                                                                                                         |
| **Asset priority**           | Atomic design system (**`assets/design/design-system/atomic-design/`**) is the **visual source of truth**; templates must consume its tokens and motifs before inventing new visuals.                                                                                               |
| **Section canon**            | v4 **`canonical-order.json`** order is the **required sequence** for any page that can bear it: **`[0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8]`**.                                                                                                                |
| **Source-owner inheritance** | Expertise pages are **S-series** (offer pages). Programme pages are **P-series**. Regulated programme pages are **R-series**. COMMON sections (hero, proof, engagement) are shared.                                                                                                 |
| **Hard vs soft tokens**      | Hard (D0–D3: structure_family, topology, content_anatomy, primary_interaction_model) are inherited from the source owner and **must not change** without updating the owner source first. Soft (D5–D8: surface, spacing, motion, depth, accent, edges) can be adapted per page. |
| **Rhythm**                   | Pages are optimized as sequences, not isolated blocks. No two adjacent semantic-peak sections (proof, capabilities, benchmark) may sit next to each other without a transition section.                                                                                             |

---

## 4. Implementation Tasks

### Task 1 — Create the canonical section component library (CSS + DTL partials)

**Why**: Currently every page reinvents **`.card`**, **`.timeline`**, **`.faq-list`**, etc. The v4 system requires a single source of truth per section.

**Steps**: 1.1. Add **section-token CSS classes** in a new **`static/css/sections/v4-sections.css`** that map the 23 sections to atomic-design tokens: - **`.section-token-00-hero`** through **`.section-token-23-faq`** - Each class encodes: **`structure_family`**, **`topology`**, **`content_anatomy`**, **`primary_interaction`**, **`rhythm_target`** (energy, spacing, peak). - Pull all colours from **`tokens.css`** (violet, cyan, paper, surface, etc.). - Inject brand motifs as background layers: **`pulse-line`**, **`shield-orbit`**, **`proof-ring`** from t0-token.

1.2. Create **DTL section partials** under **`templates/partials/v4-sections/`**: - **`_hero.html`**, **`_triggers.html`**, **`_problems.html`**, **`_audience.html`**, **`_qualification.html`**, **`_proposition.html`**, **`_value.html`**, **`_offers.html`**, **`_product.html`**, **`_transformation.html`**, **`_before_after.html`**, **`_results.html`**, **`_proof.html`**, **`_scope.html`**, **`_phases.html`**, **`_modules.html`**, **`_capabilities.html`**, **`_intersection.html`**, **`_benchmark.html`**, **`_guarantee.html`**, **`_faq.html`**, **`_engagement.html`**, **`_lead_form.html`** - Each partial accepts a **context dict** keyed by section token and renders **`data-fr`**/**`data-en`** attributes. - Each partial includes its own **`<style>`** or class hook so QA can verify section DNA presence.

1.3. Wire the partials into **`base.html`** as available includes.

**Atomic-design assets used**:

- t0-token colours and motifs become CSS custom properties and background SVG layers.
- t3-organism **`web/hero-sections-a`** and **`web/landing-services`** inform the **`.section-token-00-hero`** and **`.section-token-05-capabilities`** layouts.

---

### Task 2 — Refactor `/expertises/` (`capabilities.html`)

**Why**: This is the S-series catalogue. It must present the full buyer journey, not just a grid of cards + benchmark.

**Steps**: 2.1. Replace the flat **`<section>`** soup with the v4 canonical order, omitting only sections that have no data: - **0-hero**: keep current hero, restructure to use **`_hero.html`** partial with **`structure_family=split-hero-blueprint`**. - **11-triggers**: new section. Data source: add **`TRIGGERS`** list to **`content.py`** (3–6 market signals relevant to AI/data/security/blockschain/training). - **20-problems**: new section. Data source: add **`PROBLEMS`** list (3–5 failure modes per category). - **13-audience**: already partially present as category chips; refactor into **`_audience.html`** with role-switcher layout. - **14-qualification**: new section. Data source: reuse existing **`AUDIENCES`** list, convert into fit-gates. - **1-proposition**: new section. Data source: add **`PROPOSITIONS`** dict (mechanism-diagram layout — input/output of the offer). - **2-value**: new section. Data source: reuse **`offer.result_fr/en`** as value-waterfall. - **10-offers**: replace current flat card grid with **`_offers.html`** using route-selector layout. - **15-product**: new section. Data source: add **`DELIVERABLES`** per offer (artifact-explorer layout). - **3-transformation**: new section. Data source: reuse **`offer.result_fr/en`** as state-morph. - **12-before_after**: new section. Data source: add **`BEFORE_AFTER`** pairs per offer. - **19-results**: new section. Data source: add **`RESULTS`** metrics per offer. - **4-proof**: already partially present; refactor into **`_proof.html`** with evidence-ledger layout. - **16-scope, 17-phases, 18-modules**: new sections for each offer. Data source: add **`SCOPE`**, **`PHASES`**, **`MODULES`** dicts. - **5-capabilities**: already present as CV ranking; keep but restyle to use **`_capabilities.html`** partial. - **21-intersection**: new section. Data source: derive from offer stack intersections (e.g., AI + security + data). - **6-benchmark**: already present; keep but move to v6 position in sequence. - **22-guarantee**: new section. Data source: reuse **`offer.format_fr/en`** + CGV references as control-boundary. - **23-faq**: new section. Data source: add **`FAQ`** list per offer/category. - **7-engagement**: already present as CTA buttons; restyle to **`_engagement.html`** with next-step-rail layout. - **8-lead_form**: new section. Data source: reuse existing **`contact`** form partial.

2.2. Update the view **`expertise_category()`** in **`views.py`** to pass a **section_context dict** containing all above data for the resolved category.

2.3. Update the view **`capabilities()`** to pass an **aggregated section_context** across all categories.

**Atomic-design assets used**:

- t3-organism **`web/landing-services`** → **`.section-token-10-offers`** layout.
- t3-organism **`web/landing-brand-framework`** → **`.section-token-01-proposition`** layout.
- t0-token **`pulse-line`**, **`shield-orbit`** → section dividers and background accents.

---

### Task 3 — Refactor `/programme/` (`programmes.html`)

**Why**: The programme hub is currently a flat list. As the P-series entry point, it must answer the buyer question "Which bounded mandate fits my decision?"

**Steps**: 3.1. Replace current template with v4 canonical order, using only sections that make sense at hub level: - **0-hero**: keep, restyle to **`_hero.html`**. - **11-triggers**: new. Show 3–4 signals that make a bounded mandate necessary (inspection, production readiness, AI promotion, etc.). - **20-problems**: new. Show 3–4 problems solved by a programme vs. ad-hoc engagement. - **13-audience**: new. Decision-unit roles (CDO, CTO, QP, etc.). - **14-qualification**: new. Fit-gates: "Do you have a sponsor? A technical lead? A named workflow?" - **10-offers**: replace flat cards with **`_offers.html`** using offer-ladder layout (already prototyped in **`programme.css`** as **`.assurance-offer-ladder`**). - **7-engagement**: restyle CTA to **`_engagement.html`** with commitment-preview layout. - **8-lead_form**: add inline qualification form.

3.2. Update **`programmes()`** view in **`views.py`** to build **`section_context`** from **`PROGRAMME_CATEGORIES`** and **`PROGRAMMES`**.

**Atomic-design assets used**:

- t3-organism **`web/hero-sections-a`** → **`.section-token-00-hero`** variant for programme hub.
- t3-organism **`web/landing-services`** → **`.section-token-10-offers`** offer-ladder.

---

### Task 4 — Refactor programme detail pages (production_assurance + pharma)

**Why**: These are already rich but hard-coded. They must inherit from the new canonical partials and consume atomic-design motifs.

**Steps**: 4.1. **production_assurance.html**: replace hand-written HTML blocks with v4 partials in canonical order: **`[0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8]`** - Map existing blocks to partials (e.g., existing **`.assurance-offer-ladder`** → **`_offers.html`**). - Add missing sections: intersection (21), guarantee (22), faq (23), lead_form (8). - Remove duplicate CSS by migrating **`.assurance-*`** classes to **`.section-token-*`** classes.

4.2. **pharmaceutical_evidence_assurance.html**: same migration, preserving R-series specific content (triggers, before_after, roles, decision chain).

4.3. Update both views to pass **`section_context`** and let partials render.

**Atomic-design assets used**:

- t0-token motifs as section backgrounds.
- t3-organism **`web/landing-brand-framework`** → **`.section-token-01-proposition`** and **`.section-token-03-transformation`**.

---

### Task 5 — Content data expansion (`content.py`, `programme_content.py`, `programme_pharma_content.py`, taxonomy)

**Why**: Templates are only as good as the data they receive. The v4 sections need structured data.

**Steps**: 5.1. In **`content.py`**, expand **`OFFERS`** dict to include: - **`triggers`**: list of 3–6 signal dicts - **`problems`**: list of 3–5 problem dicts - **`audiences`**: list of role dicts (already exists as **`AUDIENCES`**) - **`qualification`**: list of fit-gate dicts - **`proposition`**: mechanism-diagram dict (input/output/control loop) - **`value`**: value-waterfall dict (3 tiers) - **`offers`**: route-selector dict (already exists as offer_ladder in programmes) - **`product`**: artifact-explorer dict (deliverables list) - **`transformation`**: state-morph dict (before/after states) - **`before_after`**: comparison-slider dict (3 dimensions) - **`results`**: acceptance-ledger dict (metrics with units) - **`proof`**: evidence-ledger dict (reuse existing **`proof_fr/en`** + GitHub provenance) - **`scope`**: boundary-map dict (in/out/owned-by) - **`phases`**: sticky-timeline dict (5 phases with outcomes) - **`modules`**: module-lattice dict (8 modules with objectives) - **`intersection`**: convergence-node dict (skill braid) - **`guarantee`**: control-boundary dict (residual risk + controls) - **`faq`**: list of objection dicts

5.2. In **`programme_content.py`** and **`programme_pharma_content.py`**, add the same keys where missing.

5.3. In **`taxonomy.py`**, add **`EXPERTISE_TRIGGERS`**, **`EXPERTISE_PROBLEMS`** etc. as category-level metadata.

---

### Task 6 — CSS reconciliation

**Why**: Current CSS is page-scoped and ad-hoc. The v4 system needs a coherent section-layer cascade.

**Steps**: 6.1. Create **`static/css/sections/v4-sections.css`**: - Define **`.section-token-XX-<name>`** base classes. - Each class sets: **`--section-energy`** (1–3), **`--section-spacing`** (air/medium/dense), **`--section-peak`** (true/false), **`--section-motion`** (state/scroll/transition), **`--section-depth`** (flat/layered/spatial-2.5d). - Use **`color-mix(in srgb, ...)`** exclusively so light/dark themes stay in sync.

6.2. Refactor **`programme.css`**: - Replace **`.assurance-*`** classes with **`.section-token-*`** equivalents where 1:1. - Keep only page-specific overrides (e.g., **`.assurance-offer-ladder`** → **`.section-token-10-offers .offer-ladder`**). - Delete dead selectors after migration.

6.3. Add **`static/css/sections/capabilities.css`**: - Styles for S-series specific adaptations (category-chip grid, capability-rank-card, filterable-grid).

6.4. Add **`static/css/sections/programmes.css`**: - Styles for P-series hub (offer-ladder, fit-gates, qualification console).

6.5. Update **`base.html`** to load the new section CSS files via **`{% block styles %}`**.

---

### Task 7 — Atomic-design asset ingestion

**Why**: The visual system already exists; we need to surface it in the pages.

**Steps**: 7.1. Export or inline the relevant t3-organism **`web`** PNGs as **CSS background-image** references in **`v4-sections.css`**: - **`hero-sections-a`** → **`.section-token-00-hero`** background pattern - **`landing-services`** → **`.section-token-10-offers`** card background texture - **`landing-brand-framework`** → **`.section-token-01-proposition`** diagram background

7.2. Add a **brand-motif SVG sprite** (**`static/svg/brand-motifs.svg`**) containing: - **`pulse-line`**, **`shield-orbit`**, **`proof-ring`**, **`data-stream`**, **`hex-grid`**, **`orbit-point`** - Use these as decorative **`<svg><use href="#pulse-line"/></svg>`** in section partials.

7.3. Document the mapping in **`assets/design/design-system/atomic-design/web-to-section-map.md`** so future editors know which organism feeds which section token.

---

### Task 8 — Source-first inheritance enforcement

**Why**: The v4 system requires that hard structural changes happen at the owner source first.

**Steps**: 8.1. Add a **CI lint rule** (Python script) that checks: - Any template using **`.section-token-*`** must match the hard-inherited tokens declared in **`canonical-design-dna.json`**. - No template may invent a new **`.section-token-*`** class without a corresponding entry in **`section-origin-registry.json`**.

8.2. Add a **pre-commit hook** or management command **`validate_section_dna`** that runs the above.

8.3. Document the update protocol in **`content/docs/SECTION_UPDATE_PROTOCOL.md`**: > "To change a section's hard structure: edit the owner template first → bump DNA version → run **`promote_section_champion.py`** → verify propagation to S/P/R."

---

### Task 9 — Validation

**Steps**: 9.1. Run existing test suite: **`pytest apps/tests/`** — ensure no regressions in views, URLs, or templates. 9.2. Run **`ruff check`** and **`mypy`** on modified files. 9.3. Run **`python manage.py validate_section_dna`** (new command) — must pass. 9.4. Visual regression: capture screenshots of all 4 expertise + 4 programme pages before/after; diff with Playwright. 9.5. Accessibility: run **`axe-core`** or **`pa11y`** on the 4 pages; ensure no new violations. 9.6. Performance: run Lighthouse on each page; ensure no regression in LCP/CLS due to new SVGs or CSS.

---

## 5. Data Flow

```
content.py / programme_content.py / programme_pharma_content.py
    ↓ (section_context dict)
views.py (expertise_category, capabilities, programmes, production_assurance, pharmaceutical_evidence_assurance)
    ↓ (render context)
v4 section partials (templates/partials/v4-sections/_*.html)
    ↓ (CSS classes)
v4-sections.css + capabilities.css + programmes.css + programme.css
    ↓ (visual layer)
atomic-design tokens (t0) + motifs (t1) + organisms (t3)
    ↓
Browser
```

---

## 6. Rollout Order

1. **Task 1** — Section component library (unblocks all others).
2. **Task 5** — Content data expansion (unblocks templates).
3. **Task 2** — Refactor **`/expertises/`** and **`/expertises/<cat>/`**.
4. **Task 3** — Refactor **`/programme/`** hub.
5. **Task 4** — Refactor programme detail pages.
6. **Task 6** — CSS reconciliation (can run parallel to 3–5).
7. **Task 7** — Atomic-design asset ingestion (can run parallel to 3–5).
8. **Task 8** — Inheritance enforcement (after templates are stable).
9. **Task 9** — Validation (after all above).

---

## 7. Risks & Mitigations

| **RiskMitigation**                                                                     |                                                                                                                                                    |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Template bloat** — 23 partials × 4 pages = 92 includes per page                      | Use **`{% include %}`** with caching; lazy-load below-the-fold sections; keep partials under 60 lines each.                                        |
| **Content gaps** — not every offer has triggers, problems, etc.                        | Partial must degrade gracefully: if a list is empty, render nothing and do not leave an empty **`<section>`**. Add **`{% if triggers %}`** guards. |
| **CSS specificity wars** between old **`.assurance-*`** and new **`.section-token-*`** | Deprecate old classes in one sprint; use a codemod or search-replace to swap them.                                                                 |
| **Atomic-design assets not web-ready** — PNGs are mockup cuts, not production sprites  | Use them as **reference** for CSS shapes/gradients; recreate production SVGs from the tokens, not by slicing the PNGs directly.                    |
| **Rhythm violations** — two peak sections adjacent                                     | Add a CI check that parses the section order in each template and flags adjacent peaks (proof+capabilities, capabilities+benchmark, etc.).         |

---

## 8. Out of Scope

- Changing the URL structure (**`/expertises/`**, **`/programme/`** remain as-is).
- Modifying the mega-menu or navigation tree.
- Adding new programme entries (content expansion only).
- React/Babel front-end migration (this plan stays within Django + CSS).

---

## 9. Open Questions

None. All material decisions are resolved:

- Option C is selected.
- Atomic-design assets are the visual priority.
- v4 source-first canon is the structural priority.
- Rollout order is dependency-driven.
