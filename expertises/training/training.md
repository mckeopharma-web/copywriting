# training.md — Evidence selection & validation ledger

Target: https://mickael-umt.com/expertises/training/
Artifact: `expertises/training/training.html`
Status: **BLOCKED_REVIEW — triplicate LLM judge execution not available in connected tool surface**

## Structure contract

The live source exposes 17 content sections in this order: Triggers → Consequences → For whom → Qualification → Proposition → Offers → Deliverables → Before/after → Results → Proof → Scope → Process → Modules → Intersection → Commitments → Questions → Engagement. The HTML preview preserves that sequence and semantic role. Raw origin HTML/CSS was not materialised in the local runtime, so this is a faithful static reconstruction of visible structure/content, not an assertion of byte- or DOM-identical reproduction.

## Candidate loop

NeoFort current-EU screening executed before copy: **80 candidates** retained from the current AI-related pool. Source mix in the screened 80: **37 arXiv · 15 EU-public · 8 NIST · 20 other**. **74/80** had quantitative fields or numeric source facts suitable for graph screening. A **30-candidate graphability shortlist** was then treated as the upper selection set; four EUGs were selected for exact-data availability, buyer relevance and placement fit. This ledger does not represent the 30 as formally judge-passed.

### Selected EUGs

| EUG | Placement | Question | Observations | Source | Epistemic status | Publication |
|---|---|---|---:|---|---|---|
| EUG-TR-01 | Triggers | Where is AI used inside EU enterprises? | 7 | Eurostat 2025 purpose shares | OBSERVED | BLOCKED_REVIEW |
| EUG-TR-02 | Proposition | Which skills do SMEs say GenAI made more important? | 7 | OECD 2025 SME survey / 2026 synthesis | OBSERVED self-report | BLOCKED_REVIEW |
| EUG-TR-03 | Consequences | Where do SMEs say GenAI helps shortages/gaps? | 14 | OECD 2025 SME survey | OBSERVED self-report | BLOCKED_REVIEW |
| EUG-TR-04 | Intersection | How do AI purposes differ by small vs large enterprises? | 14 | Eurostat 2025 | OBSERVED | BLOCKED_REVIEW |

Every mark in the HTML SVGs is bound to a disclosed datapoint. No interpolation, fitted model, forecast, invented uncertainty or decorative architecture diagram is counted as EUG.

## Distributed EvidenceUnit placements

| EU | Section | Target XPath | Supports | Preflight | Factfulness/agent status | Placement publication |
|---|---|---|---|---|---|---|
| EU-TR-01 | hero | `//*[@id="claim-eu-tr-01"]` | EC Article 4 current implementation / enforcement | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-02 | triggers | `//*[@id="claim-eu-tr-02"]` | Eurostat AI adoption by enterprise size | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-03 | consequences | `//*[@id="claim-eu-tr-03"]` | Eurostat expertise/legal/privacy barriers among non-users who considered AI | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-04 | for-whom | `//*[@id="claim-eu-tr-04"]` | NIST role-bound AI risk-management training | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-05 | qualification | `//*[@id="claim-eu-tr-05"]` | EC differentiated AI-literacy learning approaches | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-06 | proposition | `//*[@id="claim-eu-tr-06"]` | OECD advanced vs broader AI-relevant skill needs | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-07 | offers | `//*[@id="claim-eu-tr-07"]` | EC documentation: internal records, no specific certificate | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-08 | before-after | `//*[@id="claim-eu-tr-08"]` | OECD observational training/outcomes association | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-09 | results | `//*[@id="claim-eu-tr-09"]` | arXiv controlled user study of permission-policy overreach | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-10 | scope | `//*[@id="claim-eu-tr-10"]` | EMA/FDA medicines-lifecycle AI good-practice principles | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-11 | proof | `//*[@id="claim-eu-tr-11"]` | First-party training record since 2021 | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-12 | proof | `//*[@id="claim-eu-tr-12"]` | Public engineering portfolio | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-13 | proof | `//*[@id="claim-eu-tr-13"]` | Public persona/bias evaluation artefact | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |
| EU-TR-14 | intersection | `//*[@id="claim-eu-tr-14"]` | Eurostat AI-purpose heterogeneity by enterprise size | source fields complete in artefact | no fabricated new judge PASS | BLOCKED_REVIEW |

## Source boundaries

- Eurostat data are descriptive enterprise survey statistics. Adoption/use shares do not prove competence, productivity, safety or training effectiveness.
- OECD SME/worker evidence is survey evidence and is used as association/perception evidence unless the cited study design supports stronger inference.
- NIST AI RMF is voluntary risk-management guidance. It is not treated as EU law or certification.
- European Commission AI-literacy Q&A is used for Article 4 implementation statements and current timing; it does not prescribe this consulting offer.
- EMA/FDA principles are bounded to medicines lifecycle contexts; no cross-domain legal transfer is asserted.
- The arXiv 2608.27443 result is a single simulated-agent study. It supports a narrow warning about approval/policy design, not a universal enterprise effect.
- First-party CV/GitHub proof is used only for capability provenance, never as external outcome proof.

## NeoFort gate state

Resolved current policies include deterministic preflight v2, proof-carrying agent exploitability v3, factfulness semantic entailment v2, champion EU judge v2, EUG presentation judge v1, EvidencePlacement claim-span entailment v2.2, placement presentation judge v1.2, applicability v2, deterministic LLM execution v2 and verdict normalization v2.

The connected NeoFort surface does not expose an isolated triplicate semantic judge executor. Under the fail-closed rule, no new EU/EUG/placement is labelled FINAL_PASS. Required next gate: run the applicable judges on immutable source/claim snapshots with `temperature=0`, `top_p=1`, `replicas=3`; reduce booleans by AND, scores by MIN, and block categorical disagreement.

## Design / accessibility checks

- Night-mode static representation.
- Citation trigger is a real button, keyboard/pointer/touch equivalent.
- Evidence bubble uses the required `.lp-evidence-bubble-scroll` class.
- Escape and explicit close return focus.
- Every EUG has SVG `title`, `desc`, source note and a data table disclosure.
- Bibliography is placed inside the existing Engagement section; no 18th content section is added.
- Citation claim spans have unique IDs so each proposed XPath resolves exactly once in this artefact.

## GitHub persistence invariant

A commit proves persistence only. It does **not** convert `BLOCKED_REVIEW` into evidentiary PASS.
