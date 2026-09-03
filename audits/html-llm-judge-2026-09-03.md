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
- Coverage: every `CLAIM`, `RECOMMENDATION`, `CLAIM_AND_RECOMMENDATION`, and factual CTA premise requires a current support assessment; unsupported assertive copy opens an `EvidencePlacementGap` and blocks publication.
- A previous PASS does not survive a material page edit unless the exact judged snapshot/claim span/locator still matches.

## Repository-wide result

**No HTML file is promoted to `FORMAL_PUBLICATION_PASS` by this audit.** This is deliberate, not a quality guess. The current graph contains good passing evidence/placement runs for several pages, but there is no complete, current, file-level publication certificate satisfying the whole chain for all 27 artifacts. Existing review/preview files remain review/preview.

This audit therefore distinguishes:

- `BLOCKED_COVERAGE`: current page has open evidence-placement gaps.
- `BLOCKED_STALE_JUDGE`: a previous 3-replica PASS exists but the judged placement was superseded by a later page edit.
- `BLOCKED_PENDING_PRESENTATION`: evidence may be usable, but current placement/presentation judgement or exact locator proof is incomplete.
- `READY_FOR_FORMAL_JUDGE`: no current page-level placement gap was found, but the formal current 3-replica file/page judgement has not been materialized.
- `REVIEW_ARTIFACT`: derived/reconstruction/preview file; must remain non-live until its canonical page passes.

## Audit matrix — every HTML file

| # | HTML artifact | Canonical semantic target | Verdict | Current blocker / required remediation |
|---:|---|---|---|---|
| 1 | `engagement/audiences/avatar-ai-security.html` | `/engagement/audiences/#avatar-ai-security` | `READY_FOR_FORMAL_JUDGE` | No current page gap found for the fragment, but no current file-level 3-replica publication certificate. Keep bounded avatar language and judge exact snapshot before publish. |
| 2 | `expertises/agentic-ai/agentic-ai.html` | `/expertises/agentic-ai/` | `BLOCKED_STALE_JUDGE + BLOCKED_COVERAGE` | 9 current gaps. Ten placement runs previously passed 87–96 with 3 replicas, but their placements are now `current=false / SUPERSEDED_BY_PAGE_EDIT`. Rebind evidence to the edited copy and re-run exact placement judge. |
| 3 | `expertises/agentic-ai/agentic-ai_night_mode_evidence_grounded_reconstruction_v1.html` | derived Agentic AI artifact | `REVIEW_ARTIFACT` | Derived reconstruction is not a current judged page snapshot. Do not treat prior Agentic AI judge scores as transferable. |
| 4 | `expertises/ai-security/ai-security.html` | `/expertises/ai-security/` | `BLOCKED_COVERAGE` | 9 current page gaps remain. NeoFort contains multiple current placement PASS runs (3 replicas, scores 94–98); preserve those claims, remediate only uncovered spans, then run page publication gate. |
| 5 | `expertises/blockchain/blockchain.html` | `/expertises/blockchain/` | `BLOCKED_COVERAGE + BLOCKED_XPATH` | 11 current gaps; older selected placements include retired evidence and DOM/XPath-pending decisions. Replace market/performance claims only with current agent-exploitable EU/EUG and verify exact locator count=1. |
| 6 | `expertises/cdm-automation/cdm-automation.html` | `/expertises/cdm-automation/` | `BLOCKED_COVERAGE + BLOCKED_PENDING_PRESENTATION` | 10 current gaps. Several underlying EU are agent-allowed, but presentation/admission lifecycle is incomplete. Keep HTML fail-closed until current placements + graph presentations pass. |
| 7 | `expertises/data-engineering/data-engineering.html` | `/expertises/data-engineering/` | `BLOCKED_COVERAGE` | 9 current gaps; HTML explicitly contains `PENDING`, `PENDING_MATERIALIZATION`, or `FACTFULNESS_PASS/PENDING_ADMISSION` evidence. Replace those claim spans with admitted evidence or bounded capability/process copy; do not relabel pending evidence as passed. |
| 8 | `expertises/healthtech-product/healthtech-product.html` | `/expertises/healthtech-product/` | `BLOCKED_COVERAGE` | 10 current gaps. Two placement runs are strong current PASS (98) for EHDS EHR testing and EMA/FDA good-AI lifecycle; retain them and replace unsupported neighboring claims. |
| 9 | `expertises/healthtech-product/healthtech-product_lossless-evidence-v1.2_2026-09-02.html` | derived HealthTech Product artifact | `REVIEW_ARTIFACT` | Historical lossless-evidence variant; canonical page coverage still blocks publication. |
| 10 | `expertises/healthtech-product/healthtech-product_lossless-evidence-v1.3-review_2026-09-02.html` | derived HealthTech Product artifact | `REVIEW_ARTIFACT` | Explicit review variant; do not publish as a substitute for a canonical current judged snapshot. |
| 11 | `expertises/healthtech/healthtech.html` | `/expertises/healthtech/` | `READY_FOR_FORMAL_JUDGE` | No current page-level placement gap found, but no complete current file-level 3-replica publication certificate is materialized. Run current exact snapshot judges. |
| 12 | `expertises/it/it.html` | `/expertises/it/` | `BLOCKED_PENDING_PRESENTATION` | HTML is `REVIEW_ARTIFACT_NOT_LIVE`; current repo notes state page-level EUG renderings remain review-only pending current 3-replica graph-presentation and placement gates. |
| 13 | `expertises/it/it_night_mode_evidence_grounded_reconstruction_v1.html` | derived IT artifact | `REVIEW_ARTIFACT` | Reconstruction is not a canonical judged snapshot. Keep noindex/review semantics. |
| 14 | `expertises/marketing-engineering/marketing-engineering.html` | `/expertises/marketing-engineering/` | `BLOCKED_COVERAGE` | 9 current gaps. Rewrite market-effect claims from current evidence; keep first-party process/method claims explicitly bounded as offer design rather than observed market outcomes. |
| 15 | `expertises/pv-data-engineer/pv-data-engineer.html` | `/expertises/pv-data-engineer/` | `BLOCKED_COVERAGE + BLOCKED_PENDING_PRESENTATION` | 10 current gaps. NeoFort has 30 linked EvidenceUnits with agent exploitability `ALLOWED`; placement/presentation coverage remains incomplete. Bind the strongest EU to exact copy spans instead of adding more facts. |
| 16 | `expertises/reg-csv/reg-csv.html` | `/expertises/reg-csv/` | `BLOCKED_COVERAGE + REVIEW_ONLY_PLACEMENTS` | 10 current gaps. 11 linked EU are agent-allowed (including Annex 11/FDA CSA/GxP data integrity evidence), but placements are review-only. Rebind to exact claims and run presentation judge. |
| 17 | `expertises/training/training.html` | `/expertises/training/` | `BLOCKED_COVERAGE + BLOCKED_GRAPH_REVIEW` | 9 current gaps; repo companion audit marks EUGs `BLOCKED_REVIEW`. Replace unsupported transfer/adoption outcome claims with observed training-system capability or newly admitted outcome evidence. |
| 18 | `pages/engagement/audiences.html` | `/engagement/audiences/` | `BLOCKED_PENDING_PRESENTATION` | HTML self-identifies as `GITHUB_PREVIEW_ONLY_PENDING_PLACEMENT_JUDGE`. Keep preview-only until exact current placement judgement is materialized. |
| 19 | `pages/engagement/audiences/mickael-umt.com.html` | `/engagement/audiences/` derived page artifact | `REVIEW_ARTIFACT` | Same semantic target as audiences page; duplicate/derived HTML needs one canonical source-of-truth and an exact snapshot judge before publication. |
| 20 | `pages/mickael-umt.com.html` | `/` | `BLOCKED_COVERAGE` | 74 current gaps. Existing homepage audit has 90 assertive sequences; unsupported frequency, outcome, capability, catalogue-count and proof wording must be replaced or supported. Use cardinality-preserving substitutions; do not add sections. |
| 21 | `pages/programme/pharmaceutical-evidence-assurance.html` | `/programme/pharmaceutical-evidence-assurance/` | `BLOCKED_COVERAGE` | 9 current gaps. Replace unsupported regulatory/outcome language with current admitted pharma evidence + bounded programme deliverables; then rerun placement and page gates. |
| 22 | `pages/realisations/ia-agents.html` | `/realisations/ia-agents/` | `REVIEW_ARTIFACT / FAIL_CLOSED` | HTML explicitly declares `artifact-status=REVIEW_FAIL_CLOSED`. Keep public-project claims tied to repository provenance; do not elevate experimental/R&D statements to production outcomes. |
| 23 | `publish/expertises/blockchain/index.html` | `/expertises/blockchain/` publication wrapper | `BLOCKED_BY_CANONICAL_PAGE` | Canonical Blockchain page has 11 gaps + XPath/state issues. Publish wrapper cannot outrank its canonical evidence state. |
| 24 | `publish/expertises/growth/growth.html` | `/expertises/growth/` | `READY_FOR_FORMAL_JUDGE / PREVIEW` | No current page-level gap found, but repo status remains pending/review. Run exact current evidence/presentation judges before publication. |
| 25 | `publish/expertises/growth/index.html` | `/expertises/growth/` publication wrapper | `BLOCKED_PENDING_NEOFORT_PLACEMENT` | HTML explicitly declares `x-publication-status=blocked-pending-neofort-placement`. Do not flip status without current judge evidence. |
| 26 | `publish/expertises/pv-data-engineer/index.html` | `/expertises/pv-data-engineer/` publication wrapper | `BLOCKED_BY_CANONICAL_PAGE` | Canonical PV Data Engineer page has 10 gaps and incomplete placement presentation coverage. |
| 27 | `publish/realisations/blockchain/blockchain.html` | `/realisations/blockchain/` | `READY_FOR_FORMAL_JUDGE` | Strong provenance-first structure and no current page gap found. Still requires current formal 3-replica file/snapshot judgement before `FORMAL_PUBLICATION_PASS` can be asserted. |

## Copy replacement policy used

For each failing claim span, remediation must follow this order:

1. **Reuse current admitted/agent-exploitable evidence** when it entails the exact subject, metric, population, period, modality and causal level.
2. **Replace the proposition, not the evidence**, when the source only supports a narrower statement.
3. If no admissible external support exists, replace the slot with **bounded first-party capability / process / qualification copy** that is directly evidenced by the repository, contract, public implementation, or explicit offer definition.
4. Never convert `PENDING`, `REVIEW_ONLY`, `PLANNED`, `DERIVED`, `ASSOCIATIONAL`, or a previous superseded judge PASS into an observed/publication PASS by wording alone.
5. Preserve existing section count/order/semantic role (`STRUCTURE_LOCK=true`).

## High-value replacements already indicated by the graph

These are cardinality-preserving examples from current NeoFort copy-audit logic; they reduce unsupported implication without weakening positioning:

- Homepage frequency claim: `Trois situations reviennent le plus souvent.` → `Trois points d’entrée : production agentique, preuve réglementaire et transfert de capacité.`
- Homepage editorial recency: `Ce qui vient de paraître.` → `4 publications récentes sur causalité, preuve d’investigation et audit continu.` **only if the four linked publication objects remain current in the judged snapshot**.
- Homepage catalogue heading: `Ce qui s’achète sans me parler.` → `Produits et cadres accessibles sans qualification préalable.` (avoid numeric catalogue claims unless the repository/site inventory is snapshotted and bound).
- Homepage proof framing: replace success-language with repository-provenance language, e.g. `Dépôts publics avec contribution, historique et limites vérifiables; travaux confidentiels bornés au niveau de divulgation autorisé.`
- Agentic AI: previous evidence-placement PASS is not reused after page edit; copy must be rebound to the current edited span, then re-judged.
- Data Engineering: any citation bubble that says `PENDING*` must not carry a marketing fact in a publishable build. Either bind an admitted replacement EU or rewrite the sentence as a clearly bounded design/capability statement.

## What was changed in NeoFort during this audit

A stale lifecycle inconsistency was corrected for **16 current placements** whose current evidence-placement judge run already had: `decision=PASS`, hard gates PASS, 3 replicas and score ≥85. Their placement/presentation status is now synchronized to PASS while their page publication state remains `JUDGED_PASS_PENDING_PAGE_COVERAGE`; this does **not** bypass open page gaps.

No superseded Agentic AI placement was reactivated: its prior PASS placements are correctly `current=false / SUPERSEDED_BY_PAGE_EDIT`.

## Publication rule

A file may move to `FORMAL_PUBLICATION_PASS` only when all of the following are true for the **same immutable current snapshot**:

`preflight PASS ∧ factfulness PASS ∧ all applicable specialist judges PASS ∧ graph/presentation PASS when applicable ∧ exact placement PASS ∧ zero blocking coverage gaps ∧ current snapshot coherence PASS`.

Anything less remains fail-closed.