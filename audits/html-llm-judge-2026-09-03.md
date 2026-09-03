# HTML LLM-as-a-Judge audit — 2026-09-03

Repository: `mckeopharma-web/copywriting`
Baseline commit: `baf5f43ea7febc2a70cc81feaa5e0489e59acd5e`
Policy source of truth: NeoFort `current=true`
Execution posture: `FAIL_CLOSED`
HTML artifacts enumerated at baseline: **27**

## Formal gate used

`DeterministicPreflight → FactfulnessSemanticJudge → JudgeApplicability → ApplicableSpecialistJudges → SnapshotCoherence → AgentExploitability → EvidencePresentationDecision → PlacementJudge → PublicationGate`

Current thresholds and reducers resolved from NeoFort:

- Factfulness semantic: score ≥ 90 + every applicable hard gate PASS.
- Evidence placement presentation v1.2: score ≥ 85, 3 replicas, `MIN(score)`, `AND(boolean/hard-gates)`, disagreement blocks.
- Evidence graphic presentation: score ≥ 90 + quantitative mark binding/provenance/epistemic hard gates.
- Coverage: every assertive copy span that is in scope must have an explicit support/disposition decision.
- A previous PASS does not survive a material page edit unless the exact judged snapshot/claim span/locator still matches.

## Important distinction: two kinds of gap

NeoFort currently contains two materially different gap classes and they must not be conflated:

1. **Sequence-support gaps** — the gap has a `sequence_id` / claim span. These are direct copy-publication blockers.
2. **Unplaced-EU backlog** — the gap has an `eu_id` but no `sequence_id`, usually `NO_SEQUENCE_ADDRESSED_SITE_PLACEMENT`. This means an EvidenceUnit has not yet been assigned to an addressable page sequence. It can be a required evidence-placement backlog, but it is **not by itself proof that a specific copy sentence is unsupported**.

Current homepage gaps: **74 total = 71 sequence-support gaps + 3 unplaced-EU gaps**. For the main expertise/service pages, the 9/10-gap counts seen in the graph are currently **unplaced-EU backlog**, not sentence-level support gaps.

## Repository-wide result

**No HTML file is promoted to `FORMAL_PUBLICATION_PASS` by this audit.** This is deliberate. The graph contains strong current 3-replica placement PASS results for AI Security and two HealthTech Product placements, but there is no complete current file-level publication certificate for all 27 artifacts. Existing preview/review files remain preview/review.

Verdict vocabulary:

- `SEQUENCE_SUPPORT_BLOCKED`: current claim-span support gap(s) exist.
- `CURRENT_PLACEMENT_JUDGE_BLOCKED`: exact current placements still lack required 3-replica placement/presentation PASS.
- `STALE_JUDGE`: a previous PASS exists but its placement was superseded by a later page edit.
- `PLACEMENTS_PASS__FILE_CERT_PENDING`: current placements pass, but the complete current file/page publication decision is not materialized.
- `PREVIEW_BLOCKED`: HTML explicitly declares review/preview/fail-closed state.
- `READY_FOR_FORMAL_FILE_JUDGE`: no direct blocker was found in current graph/metadata, but file-level final judgement still has to be executed.
- `REVIEW_ARTIFACT`: derived/reconstruction/preview variant; it is not allowed to outrank its canonical page.

## Audit matrix — every HTML file

| # | HTML artifact | Semantic target | Verdict | Evidence/judge state |
|---:|---|---|---|---|
| 1 | `engagement/audiences/avatar-ai-security.html` | `/engagement/audiences/#avatar-ai-security` | `READY_FOR_FORMAL_FILE_JUDGE` | Artifact exposes 11 distributed EU / 4 EUG in its own validation footer, but a current file-level publication certificate is not materialized. |
| 2 | `expertises/agentic-ai/agentic-ai.html` | `/expertises/agentic-ai/` | `STALE_JUDGE + CURRENT_PLACEMENT_JUDGE_BLOCKED` | Ten earlier placements passed 87–96 with 3 replicas, but are `current=false / SUPERSEDED_BY_PAGE_EDIT`. Ten current placements are `BLOCKED_PENDING_3_REPLICA_PRESENTATION_JUDGE`. Separate backlog: 9 unplaced EU. |
| 3 | `expertises/agentic-ai/agentic-ai_night_mode_evidence_grounded_reconstruction_v1.html` | derived Agentic AI | `REVIEW_ARTIFACT` | Derived reconstruction; prior Agentic AI judge runs cannot be transferred to this distinct snapshot. |
| 4 | `expertises/ai-security/ai-security.html` | `/expertises/ai-security/` | `PLACEMENTS_PASS__FILE_CERT_PENDING` | **14/14 current placements** have current placement-judge v1.2 PASS, hard gates PASS, 3 replicas, scores **94–98**, XPath match count=1. Separate backlog: 9 unplaced EU, which is not a sentence-level gap. File is `noindex,nofollow`; final page/file publication gate not materialized. |
| 5 | `expertises/blockchain/blockchain.html` | `/expertises/blockchain/` | `CURRENT_PLACEMENT_JUDGE_BLOCKED` | 54 current placement records, **0 current formal placement PASS**; multiple states remain XPath-pending, upstream-judge-blocked, candidate or superseded. Separate backlog: 10 unplaced EU plus a current EUG/public-page mismatch gap. |
| 6 | `expertises/cdm-automation/cdm-automation.html` | `/expertises/cdm-automation/` | `CURRENT_PLACEMENT_JUDGE_BLOCKED` | 8 current placements; publication states include `BLOCKED_PENDING_PRESENTATION_JUDGE` and `BLOCKED_PENDING_EU_ADMISSION_AND_PRESENTATION_JUDGE`. Repo companion requires >8 distributed EU and >3 graph placements to pass the full chain. Separate backlog: 10 unplaced EU. |
| 7 | `expertises/data-engineering/data-engineering.html` | `/expertises/data-engineering/` | `PREVIEW_BLOCKED` | Explicit `REVIEW_ARTIFACT_NOT_LIVE`; 17 current proposed/review-only placements, 0 formal current placement PASS. HTML still contains evidence labels such as `PENDING`, `PENDING_MATERIALIZATION`, or `FACTFULNESS_PASS/PENDING_ADMISSION`. Separate backlog: 9 unplaced EU. |
| 8 | `expertises/healthtech-product/healthtech-product.html` | `/expertises/healthtech-product/` | `PARTIAL_PLACEMENT_PASS__FILE_BLOCKED` | 8 current placements; **2 current PASS at score 98** (EHDS EHR testing; EMA/FDA good-AI lifecycle). Remaining placements/presentation decisions are not publication-complete. Separate backlog: 10 unplaced EU. |
| 9 | `expertises/healthtech-product/healthtech-product_lossless-evidence-v1.2_2026-09-02.html` | derived HealthTech Product | `REVIEW_ARTIFACT` | Historical lossless-evidence variant; cannot substitute for a current judged canonical snapshot. |
| 10 | `expertises/healthtech-product/healthtech-product_lossless-evidence-v1.3-review_2026-09-02.html` | derived HealthTech Product | `REVIEW_ARTIFACT` | Explicit review variant. |
| 11 | `expertises/healthtech/healthtech.html` | `/expertises/healthtech/` | `CURRENT_PLACEMENT_JUDGE_BLOCKED` | 10 current placements are `CANDIDATE/PROPOSED`; 0 current placement PASS. |
| 12 | `expertises/it/it.html` | `/expertises/it/` | `PREVIEW_BLOCKED` | Explicit `REVIEW_ARTIFACT_NOT_LIVE` and `noindex,nofollow`; repo notes state new page-level EUG placement still requires current graph-presentation and placement judges. |
| 13 | `expertises/it/it_night_mode_evidence_grounded_reconstruction_v1.html` | derived IT | `REVIEW_ARTIFACT` | Reconstruction is not a canonical judged snapshot. |
| 14 | `expertises/marketing-engineering/marketing-engineering.html` | `/expertises/marketing-engineering/` | `PREVIEW_BLOCKED` | HTML explicitly declares `preview-blocked-pending-current-specialist-judge-replicas-and-exact-deployed-dom-xpath-consensus`; its manifest records 14 distributed placements and 4 selected EUG, but final current specialist/DOM consensus is not materialized. Separate backlog: 9 unplaced EU. |
| 15 | `expertises/pv-data-engineer/pv-data-engineer.html` | `/expertises/pv-data-engineer/` | `PREVIEW_BLOCKED` | HTML explicitly says existing EU placements use current judge runs while four new QGEUs remain preview graphics; it states no canonical 3-replica presentation PASS was fabricated. NeoFort has many agent-allowed PV EU, but current page placement/presentation completion is still missing. Separate backlog: 10 unplaced EU. |
| 16 | `expertises/reg-csv/reg-csv.html` | `/expertises/reg-csv/` | `CURRENT_PLACEMENT_JUDGE_BLOCKED` | Multiple strong agent-allowed Annex 11 / FDA CSA / GxP evidence objects exist, but current site placements are not fully presentation-judged. Separate backlog: 10 unplaced EU. |
| 17 | `expertises/training/training.html` | `/expertises/training/` | `PREVIEW_BLOCKED` | Explicit `x-evidence-status=BLOCKED_REVIEW`; distributed EU/EUG tables are review-blocked and do not claim a fabricated PASS. Separate backlog: 9 unplaced EU. |
| 18 | `pages/engagement/audiences.html` | `/engagement/audiences/` | `PREVIEW_BLOCKED` | Explicit `GITHUB_PREVIEW_ONLY_PENDING_PLACEMENT_JUDGE`. |
| 19 | `pages/engagement/audiences/mickael-umt.com.html` | derived `/engagement/audiences/` | `REVIEW_ARTIFACT` | Duplicate/derived target; choose one canonical source-of-truth snapshot before publication. |
| 20 | `pages/mickael-umt.com.html` | `/` | `SEQUENCE_SUPPORT_BLOCKED` | **71 current claim/sequence support gaps** + 3 unplaced-EU backlog gaps. Homepage is the only audited HTML target where the current graph directly exposes this large sentence-level coverage deficit. |
| 21 | `pages/programme/pharmaceutical-evidence-assurance.html` | `/programme/pharmaceutical-evidence-assurance/` | `CURRENT_PLACEMENT_JUDGE_BLOCKED` | HTML contains admitted evidence bubbles, but current programme-level placement/publication completion is not materialized. Separate backlog: 9 unplaced EU. |
| 22 | `pages/realisations/ia-agents.html` | `/realisations/ia-agents/` | `REVIEW_ARTIFACT / FAIL_CLOSED` | Explicit `artifact-status=REVIEW_FAIL_CLOSED`; keep public-project claims tied to repository provenance and maturity labels. |
| 23 | `publish/expertises/blockchain/index.html` | `/expertises/blockchain/` wrapper | `BLOCKED_BY_CANONICAL_PAGE` | Canonical Blockchain evidence/presentation state is still blocked; wrapper cannot outrank it. |
| 24 | `publish/expertises/growth/growth.html` | `/expertises/growth/` | `PREVIEW_BLOCKED` | Explicit `preview-blocked-pending-current-specialist-judges-and-live-dom-selectors`. |
| 25 | `publish/expertises/growth/index.html` | `/expertises/growth/` wrapper | `PREVIEW_BLOCKED` | Explicit `x-publication-status=blocked-pending-neofort-placement`. |
| 26 | `publish/expertises/pv-data-engineer/index.html` | `/expertises/pv-data-engineer/` wrapper | `BLOCKED_BY_CANONICAL_PAGE` | Canonical PV page is still fail-closed for new QGEU presentation/publication. |
| 27 | `publish/realisations/blockchain/blockchain.html` | `/realisations/blockchain/` | `READY_FOR_FORMAL_FILE_JUDGE` | Strong provenance-first structure; no sentence-level gap found in current graph. No current formal file-level certificate exists, so no final PASS is asserted. |

## Replacement policy

For any failing span, remediation order is:

1. **Reuse current admitted / agent-exploitable evidence** when it entails the exact subject, metric, population, period, modality and causal level.
2. **Replace the proposition, not the evidence**, when the source only supports a narrower statement.
3. If no admissible external support exists, use **bounded first-party capability, process or qualification copy** supported by repository/CV/offer artifacts.
4. Never convert `PENDING`, `REVIEW_ONLY`, `PLANNED`, `DERIVED`, `ASSOCIATIONAL`, or a superseded judge result into observed/publication PASS by wording alone.
5. Preserve section count/order/semantic role (`STRUCTURE_LOCK=true`).

## High-value replacements staged

A separate artifact, `audits/html-copy-replacements-2026-09-03.md`, stages bounded replacement copy for 18 semantic page targets. Examples:

- Homepage: `Trois situations reviennent le plus souvent.` → `Trois points d’entrée : production agentique, preuve réglementaire et transfert de capacité.`
- Homepage: `Ce qui vient de paraître.` → `Publications récentes sur causalité, preuve d’investigation et audit continu.` unless the exact count is snapshotted and judged.
- Homepage: `Ce qui s’achète sans me parler.` → `Produits et cadres accessibles sans qualification préalable.` unless catalogue count/price visibility is snapshotted and bound.
- Blockchain: `Start with the property an independent party must verify.` Then choose signatures, attestations, append-only commitments, selective disclosure, ZK or shared ledger only when the trust boundary requires them.
- Data Engineering: `Make a data decision reconstructible.` Keep publishable facts separate from any evidence bubble still marked `PENDING*`.
- PV: `Use data engineering and AI to prioritize pharmacovigilance evidence for accountable human review.` Do not present model output as clinical causality.

These are **staged proposals**, not fabricated judge PASSes.

## NeoFort mutation performed

A stale lifecycle inconsistency was corrected for **16 current placements** whose existing current placement-judge v1.2 run already had `decision=PASS`, hard gates PASS, 3 replicas and score ≥85. Their placement/presentation status was synchronized to PASS while page publication remains non-final.

This synchronization affected the current AI Security placements and current passing HealthTech Product placements. It did not reactivate superseded Agentic AI placements.

## Publication rule

A file may move to `FORMAL_PUBLICATION_PASS` only when the following are true for the **same immutable current snapshot**:

`preflight PASS ∧ factfulness PASS ∧ all applicable specialist judges PASS ∧ graph/presentation PASS when applicable ∧ exact placement PASS ∧ required support coverage/placement policy satisfied ∧ snapshot coherence PASS`.

Anything less remains fail-closed.