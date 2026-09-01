---
id: pv-data-engineer-positioning-evidence-v1
page: https://mickael-umt.com/expertises/pv-data-engineer/
page_id: page:source:11.1
status: evidence_snapshot
language: en
positioning_policy: lossless
canonical_buyer_role_id: buyer-role:pv-data-engineer
canonical_persona: Karim Benali
canonical_role: Responsable pharmacovigilance
evidence_scope_type: SERVICE
evidence_unit_target: 2
neofort_model: opn-1.4
gdrive_policy: read_only_until_explicit_user_validation_for_any_mutation
updated_from_sources: 2026-09-01
---

# Pharmacovigilance Data Engineering — positioning evidence

## Lossless positioning kernel

The page must preserve the distinction between **automation of detection / case-processing work** and **human accountability for safety judgment**.

Canonical page thesis:

> An automated signal is not a safety decision; it is the starting point for one.

Canonical value proposition:

> Accelerate signal detection and case processing without transferring safety judgment to a model or dashboard.

The mechanism is the page's existing **Signal-to-Judgment Chain™**:

`Signal → Context → Prioritization → Human review → Action`

Any rewrite that implies autonomous clinical or safety decision-making is positioning-lossy and should be rejected.

## Canonical inductive buyer avatar

Reuse the existing avatar rather than creating a new one.

- **Persona:** Karim Benali
- **Buyer role:** Responsable pharmacovigilance
- **Before:** late signal detection, manual E2B(R3) re-entry, and surveillance workload consuming team capacity.
- **After:** automated signal detection, NLP-assisted case processing, and a pharmacovigilance dashboard supervised by the team rather than treated as the decision-maker.
- **Structural pressure band:** `critical-model-band`
- **OPN pressure index:** `94.5` (model-derived; not a public market statistic)

The avatar is a decision-modeling device, not a claim about a named real customer. Public copy should retain the site's existing validation boundary: interview and observed-behavior validation are still required.

## Buyer decision pressures

### 1. Reporting clocks × safety-data volume

Buyer objective: keep in-scope ICSR/SUSAR processing and submission within applicable regulatory reporting clocks while maintaining internal safety margin.

Useful operational metrics:

- on-time submission rate
- late cases
- cases due within 24/48h
- backlog aging
- day-zero errors

Boundary: regulatory clocks are external constraints; productivity targets such as cases/FTE/day are organization-specific and must not be presented as normative benchmarks.

### 2. Signal sensitivity × scarce medical attention

More candidate signals can consume Medical Safety and Safety Science attention. The commercial value is therefore not “maximum automation” or “maximum sensitivity”; it is **prioritized evidence that protects expert review capacity**.

Useful metrics:

- signal evaluation cycle time
- signal backlog
- validated signal yield
- aggregate report timeliness
- expert review workload

Boundary: precision/recall is publishable only for a specific evaluated model with a labeled dataset; it is not a generic PV KPI.

### 3. Throughput × defensibility

Automation must preserve ownership, quality, exceptions, auditability and documented human decisions.

Useful metrics:

- PV deviations
- audit/inspection findings
- automation exceptions
- quality-review failures
- evidence completeness

Positioning rule: **autonomy is not the target; controlled throughput and defensible decision quality are.**

## Decision-unit map

| Rank | Counterpart | Shared decision object | F | C | D | E | T |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Global Head Drug Safety | safety backlog and exposure | 5 | 5 | 5 | 5 | 4 |
| 2 | Medical Safety Physician | expert attention allocation | 5 | 5 | 5 | 5 | 4 |
| 3 | Signal Management / Safety Science | signal detection quality | 5 | 5 | 5 | 5 | 4 |
| 4 | Safety Operations Lead | case processing capacity | 5 | 5 | 5 | 5 | 3 |
| 5 | Regulatory Safety Lead | regulatory safety reporting | 4 | 5 | 4 | 5 | 4 |
| 6 | PV Quality / Compliance | controlled automation | 4 | 5 | 4 | 5 | 4 |
| 7 | Safety Database Product Owner | touchless processing | 4 | 4 | 5 | 4 | 3 |
| 8 | Safety Data Science / NLP | model-assisted safety triage | 4 | 4 | 5 | 4 | 3 |

Legend: `F=frequency`, `C=decision criticality`, `D=operational dependency`, `E=evidence burden`, `T=negotiation tension`, all on the existing 1–5 model scale.

## Factfulness-passing evidence to use

### EU-CANON-EMA-PRAC-GOVERNANCE-2026 — PASS / 100

**Fact:** EMA publishes PRAC recommendations on safety signals. Recommendations for regulatory action are routed to CHMP for endorsement for centrally authorised medicines or to CMDh for information for nationally authorised medicines; marketing-authorisation holders are expected to act according to the recommendations.

**Source:** https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/signal-management/prac-recommendations-safety-signals

**Allowed inference:** signal management remains embedded in accountable regulatory governance.

**Forbidden inference:** this evidence does not quantify signal-detection accuracy, decision speed, or treatment outcomes.

### EU-CANON-EMA-AI-GUIDANCE-PV-2028 — PASS / 100

**Fact:** the HMA-EMA Network Data Steering Group 2026–2028 workplan plans AI guidance for clinical development and pharmacovigilance, alongside a roadmap aligned with the Biotech Act.

**Source:** https://www.ema.europa.eu/en/about-us/how-we-work/data-regulation-big-data-other-sources/network-data-steering-group-ndsg

**Allowed inference:** AI use in pharmacovigilance is an explicit regulatory-workplan topic.

**Forbidden inference:** planned guidance is not evidence that a particular AI system is compliant, clinically effective, or autonomous.

## Evidence exclusions

Do not reuse page-linked Evidence Units whose `factfulness_gate_status` is `FAIL_RETIRED_REPLACED`. In particular, older PV/EMA/MHRA and generic service EUs must resolve through their canonical factfulness-passing replacements before publication.

Do not use generic Gartner/Deloitte agentic-AI forecasts as primary proof for this page when a PV-specific EMA source can support the same decision boundary more directly.

## Copywriting invariants

1. Keep **Responsable pharmacovigilance / Karim Benali** as the primary buyer avatar unless new evidence proves a better buyer-role fit.
2. Keep the human safety-review boundary explicit in hero, mechanism and deliverables.
3. Describe NLP/automation as triage, extraction, prioritization, lineage and exception-handling infrastructure—not as the safety authority.
4. Tie technical outputs to the buyer's operating objects: due-date risk, signal backlog, expert attention, case-processing capacity and inspection-defensible evidence.
5. Preserve source/version/threshold/reviewer/decision/reason lineage in the “signal decision log” concept.
6. Reject unsupported client-performance quantification. The current page itself identifies detection-rate-by-therapeutic-domain and client production metrics as missing evidence.

## Provenance snapshot

- Public page: `https://mickael-umt.com/expertises/pv-data-engineer/`
- Neo4j page: `page:source:11.1`
- Neo4j buyer role: `buyer-role:pv-data-engineer`
- Google Drive chapter/folder inspected read-only: Chapter `11.1 — Détecter plus tôt sans automatiser la décision clinique`
- Google Drive mutation policy for this work: **no create/update/delete without explicit user validation**.

## Recommended next artifact

Create a separate `eu-placement-audit-v1.md` only after mapping the live page's claims to stable selectors/XPaths. Keep evidence admission separate from copy presentation so an evidence PASS cannot silently authorize a positioning-lossy rewrite.
