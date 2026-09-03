# IT & Data Platforms — evidence-grounded landing-page manifest

- Canonical page scope: `https://mickael-umt.com/expertises/it/`
- Artifact: `expertises/it/it.html`
- Language: English
- Theme: dark / night mode
- Scope lock: **only `/expertises/it/`**
- Structure lock: **4 core sections preserved** — hero/routing → capability proof → next step → 8-screen qualifier
- Policy source: NeoFort `current=true`
- Execution posture: `FAIL_CLOSED`
- Repository source: `mckeopharma-web/copywriting/.skills/landingpage.md` v3.0

## 1. Existing-state analysis

The live category page is a routing and production-readiness page, not a generic IT-services catalogue. Its invariant is the four-lane architecture:

1. Agentic AI Engineering
2. Data Engineering & Evidence Architecture
3. AI Security, Assurance & DevSecOps
4. Blockchain & Verifiable Computing

The page also exposes a capability matrix, a next-step CTA and an eight-screen mission qualifier. The update therefore improves evidence density and buyer decision utility **without adding, removing or reordering core sections**.

## 2. Positioning decision

**Buyer:** CTO / AI Platform / Data / Security leaders moving a critical system from prototype toward production.

**Job:** make execution observable, authority explicit, data reconstructible, release conditions testable and verification proportional to the trust boundary.

**Decision rule:** start from the production property that must hold, then choose the least-complex mechanism able to enforce or prove it. This explicitly allows a conventional database or ordinary control plane to be the correct answer.

## 3. Evidence candidate loop

NeoFort query snapshot on 2026-09-03:

- 82 current `EvidenceUnit` candidates screened.
- 7 candidates use arXiv as the primary source.
- 51 candidates use public/open institutional sources in the current public-source filter.
- Open/public loop therefore returned 58 candidates, exceeding the requested 30-candidate research loop.

Blocked current IT-page evidence was not silently retained. In particular, `EU-IT-NIST-DATA-LINEAGE-2026` and `EU-IT-NIST-SSDF-RELEASE-PROVENANCE-2026` have deterministic preflight PASS but remain `BLOCKED_PENDING_FACTFULNESS`; the HTML no longer depends on them for a publishable claim.

## 4. Selected distributed EvidenceUnit placements

| Marker | EU | Placement | Supported use |
|---|---|---|---|
| [1] | `EU-PV-NIST-MANAGE-1-1-PROCEED-DECISION` | hero | production proceed / do-not-proceed framing |
| [2] | `EU-AGENTIC-MEMSECBENCH-PERSIST-84_2-2026` | Agentic AI lane | governed-memory risk boundary |
| [3] | `EU-AGENTIC-PERMISSIONS-21-PROPOSALS-2026` | Agentic AI lane | permission architecture / enforcement taxonomy |
| [4] | first-party offer/capability evidence | Data Engineering lane | implementation scope; no external effect claim |
| [5] | `EU-SG-001` | AI Security lane | safeguards + oversight + response from the outset |
| [6] | `EU-SG-004` | AI Security lane | traces/transcripts + sandbox logs for oversight/investigation |
| [7] | `EU-CANON-WILEY-DB-VS-DLT-THROUGHPUT-2026` | Blockchain lane | negative architecture evidence: DB can be faster on bounded raw throughput |
| [8] | `EU-CANON-ECB-PROGRAMMABILITY-COORDINATION-2026` | Blockchain lane | coordination mechanism evidence; no quantified savings claim |
| [9] | `EU-SG-006` | capability proof | public contribution provenance only |
| [10] | `EU-AGENTIC-PERMISSIONS-21-PROPOSALS-2026` | EUG | enforcement-mechanism distribution |
| [11] | `EU-CANON-BOUNDED-AGENTS-EXFIL-2026` + `EU-AGENTIC-BOUNDED-INJEC-544-2026` | EUG | protocol-bounded attack-success comparison |
| [12] | `EU-AGENTIC-MEMSECBENCH-PERSIST-84_2-2026` | EUG | lifecycle checkpoint rates |
| [13] | `EU-AGENTIC-MEMSECBENCH-PERSIST-84_2-2026` | EUG | 24-configuration E2E-ASR distribution |
| [14] | `EU-PV-NIST-MAP-3-3-SCOPE-DOCUMENTED` | next step / qualifier | scope-before-control framing |

## 5. EUG placements

All four EUGs live **inside the existing capability-proof section**; no page-section topology is changed.

### EUG-A — permissions enforcement mechanisms

Source: arXiv:2607.13718. Population: 21 reviewed permission-system proposals. Seven enforcement categories are visualized from the paper taxonomy. Categories are not mutually exclusive. The chart is descriptive; it does not rank approaches or prove one mechanism is sufficient.

### EUG-B — bounded-agent compromised-model attacks

Source: arXiv:2608.15888, Table 8. Population: 609 AgentDojo task–injection pairs / 1,218 executions. The paired bars show observed attack-success rates for baseline versus APC across 12 domain/category rows. The graph is protocol-bounded and is **not** a production incident-rate claim.

### EUG-C — MemSecBench lifecycle checkpoints

Source: arXiv:2607.27080. Eight reported lifecycle rates are shown: W1, W2, E1, E2, E2E, F1, F2 and SRSR. Attack and repair checkpoints use different conditioning rules exactly as stated by the paper; they are not merged into one causal funnel.

### EUG-D — MemSecBench 24-configuration E2E-ASR

Source: arXiv:2607.27080, Table 2. Population: 310 cases per configuration across the 2×4×3 harness/memory/model matrix. All 24 observed E2E-ASR values are rendered individually; no missing values are imputed and no trend line is drawn.

## 6. Publication status

The HTML is a `REVIEW_ARTIFACT_NOT_LIVE` and is `noindex,nofollow`.

Reason: source-level evidence, deterministic preflight and the selected admitted EUs are available, but a new page-level EUG placement still requires current publication snapshots for the applicable NeoFort graph-presentation and placement judges. The artifact therefore does **not** claim `FINAL_PASS` and does not convert an unexecuted three-replica publication judge into a fabricated PASS.

This is intentional fail-closed behaviour.

## 7. GitHub / Google Drive rule

GitHub is the persistence target for this review artifact. Google Drive is not read/created/updated/deleted without a separate explicit user approval.
