#!/usr/bin/env python3
"""Fail-closed, evidence-led copy upgrade for every HTML artifact.

Design constraints:
- Existing copy is a SEED, never proof.
- Visible copy is rebuilt from external-source compression + CV-derived capabilities.
- Products/configurations are semi-mobile context, not evidence.
- The original body is preserved losslessly as base64 in a non-rendered seed archive.
- The script is idempotent and applies to every *.html file in the repository.

This is the deterministic materialisation stage of NeoFort loop
`loop:copy-claim:external-capability-v1`. Formal LLM-judge PASS remains a
separate fail-closed gate.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP_ID = "loop:copy-claim:external-capability-v1"
JUDGE_ID = "judge:copy-claim:external-capability-grounding-v1"
CAPABILITY_SNAPSHOT = "capability-invariant:cv-derived:2026-09-03"
COMMERCIAL_SNAPSHOT = "commercial-context:catalogue:2026-09-03"
CATALOGUE = "https://mickael-umt.com/ressources/produits/?browse=all#catalogue"

SOURCES = {
    "nist_gai": ("NIST AI 600-1 — Generative AI Profile", "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence"),
    "owasp_agentic": ("OWASP — Agentic AI Threats and Mitigations", "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"),
    "nist_csf": ("NIST CSF 2.0", "https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20"),
    "w3c_prov": ("W3C PROV — Provenance family", "https://www.w3.org/TR/prov-overview/"),
    "openlineage": ("OpenLineage — lineage metadata specification", "https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md"),
    "fda_csa": ("FDA — Computer Software Assurance, final guidance (2026)", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software"),
    "ich_e6r3": ("ICH E6(R3) — Good Clinical Practice guideline", "https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf"),
    "ema_gvp": ("EMA — Good pharmacovigilance practices", "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/good-pharmacovigilance-practices-gvp"),
    "fda_aems": ("FDA — Adverse Event Monitoring System", "https://www.fda.gov/drugs/surveillance-post-drug-approval-activities/fda-adverse-event-monitoring-system-aems"),
    "eu_ai_act": ("EUR-Lex — Regulation (EU) 2024/1689, Article 4 AI literacy", "https://eur-lex.europa.eu/eli/reg/2024/1689"),
    "ehds": ("EUR-Lex — Regulation (EU) 2025/327, European Health Data Space", "https://eur-lex.europa.eu/eli/reg/2025/327/oj/"),
    "nist_blockchain": ("NIST IR 8202 — Blockchain Technology Overview", "https://www.nist.gov/publications/blockchain-technology-overview"),
    "w3c_vc": ("W3C — Verifiable Credentials Data Model 2.0", "https://www.w3.org/TR/vc-data-model-2.0/"),
    "erc4337": ("ERC-4337 — Account Abstraction Using Alt Mempool", "https://eips.ethereum.org/EIPS/eip-4337"),
    "govuk_metrics": ("GOV.UK Service Manual — How to set performance metrics", "https://www.gov.uk/service-manual/measuring-success/how-to-set-performance-metrics-for-your-service"),
    "govuk_success": ("GOV.UK Service Manual — Measuring service success", "https://www.gov.uk/service-manual/measuring-success/measuring-the-success-of-your-service"),
    "cisa_sbom": ("CISA — Software Bill of Materials", "https://www.cisa.gov/sbom"),
    "otel": ("OpenTelemetry Specification", "https://opentelemetry.io/docs/specs/otel/"),
}

COMMON_PRODUCTS = [
    ("Framework Diagnostic IA", CATALOGUE),
    ("Office Hours", CATALOGUE),
    ("Pack Cadrage — Framework diagnostic & séance collective", CATALOGUE),
]

FAMILIES = {
    "agentic": {
        "title": "Agentic AI Engineering",
        "lead": "Engineer agentic systems as bounded execution systems: explicit authority, observable tool use, governed memory, evaluation gates and accountable human review.",
        "claims": [
            ("Agentic risk is not limited to model output: tool access, delegated authority and autonomous actions create additional control surfaces that require explicit threat modelling and mitigation.", ["owasp_agentic", "nist_gai"]),
            ("A defensible production design therefore treats evaluation, monitoring and lifecycle governance as part of the system rather than as a post-deployment add-on.", ["nist_gai", "nist_csf"]),
        ],
        "capabilities": ["Systèmes agentiques", "Évaluation des systèmes IA", "Sécurité des systèmes IA", "Python et traitement de données"],
        "products": COMMON_PRODUCTS + [("Cohorte — Systèmes IA & agents", CATALOGUE)],
    },
    "ai-security": {
        "title": "AI Security, Assurance & DevSecOps",
        "lead": "Secure the complete AI execution path: model, prompt, tools, connectors, permissions, secrets, evidence and release gates.",
        "claims": [
            ("AI security work has to cover system interactions and agentic authority, not only model behaviour; current guidance explicitly addresses misuse, access, actions and lifecycle risks.", ["owasp_agentic", "nist_gai"]),
            ("Cybersecurity governance is strongest when outcomes are made explicit, prioritised and communicated across the organisation, while implementation remains adaptable to context.", ["nist_csf", "cisa_sbom"]),
        ],
        "capabilities": ["Sécurité des systèmes IA", "Évaluation des systèmes IA", "Jenkins, Terraform et supply chain", "Systèmes agentiques"],
        "products": COMMON_PRODUCTS + [("Framework Diagnostic IA", CATALOGUE)],
    },
    "blockchain": {
        "title": "Blockchain & Verifiable Computing",
        "lead": "Start from the property another party must verify, then choose the minimum mechanism: signature, credential, attestation, smart contract, ZK proof or shared ledger.",
        "claims": [
            ("Blockchain is a distributed tamper-evident ledger mechanism; verifiable credentials are a separate mechanism for cryptographically secured, privacy-respecting and machine-verifiable claims. Architecture should distinguish the verification property from the mechanism selected to provide it.", ["nist_blockchain", "w3c_vc"]),
            ("Ethereum account abstraction illustrates the same separation at protocol level: validation logic can move into smart-contract accounts while preserving explicit verification constraints.", ["erc4337", "nist_blockchain"]),
        ],
        "capabilities": ["Solidity et ingénierie EVM", "Rust et outillage systèmes", "Développement Solana", "Zero-knowledge et ZKML"],
        "products": COMMON_PRODUCTS + [
            ("Tokenisation Fit & Economic Architecture", "https://mickael-umt.com/expertises/blockchain/"),
            ("Tokenized Asset Lifecycle & Governance", "https://mickael-umt.com/expertises/blockchain/"),
            ("Stablecoin & Cross-Border Settlement Architecture", "https://mickael-umt.com/expertises/blockchain/"),
            ("Selective Disclosure & ZK Verification R&D", "https://mickael-umt.com/expertises/blockchain/"),
        ],
    },
    "data": {
        "title": "Data Engineering & Evidence Architecture",
        "lead": "Make a data decision reconstructible from source, transformation, run metadata, ownership, quality checks and review evidence.",
        "claims": [
            ("Provenance models distinguish entities, activities and agents involved in producing information; lineage standards add run, job and dataset events that make transformations observable across execution.", ["w3c_prov", "openlineage"]),
            ("In regulated data workflows, audit trails, interpretable logs, traceable transfers and preserved metadata are explicit requirements for reconstructing what changed and why.", ["ich_e6r3", "w3c_prov"]),
        ],
        "capabilities": ["Architecture data, DDD et événements", "Python et traitement de données", "Data science et machine learning", "Ingénierie web et produit"],
        "products": COMMON_PRODUCTS,
    },
    "clinical-data": {
        "title": "Clinical Data Management Automation",
        "lead": "Automate clinical-data handling around traceable changes, interpretable audit trails, controlled transfers and explicit human review boundaries.",
        "claims": [
            ("ICH E6(R3) requires computerised-system logs, documented changes, interpretable audit trails and traceability across data transfer and migration; automation must preserve those controls rather than obscure them.", ["ich_e6r3", "fda_csa"]),
            ("The European Health Data Space adds common rules for EHR systems, including interoperability and logging software components, reinforcing architecture around controlled exchange and traceability.", ["ehds", "ich_e6r3"]),
        ],
        "capabilities": ["Opérations pharmaceutiques et réglementées", "Architecture data, DDD et événements", "Python et traitement de données", "Gouvernance et assurance IA"],
        "products": COMMON_PRODUCTS + [("Cohorte — Environnements régulés", CATALOGUE)],
    },
    "healthtech": {
        "title": "HealthTech & PharmaTech Product Engineering",
        "lead": "Build health-data products around interoperability, traceable state changes, controlled evidence and accountable review — before adding automation.",
        "claims": [
            ("EHDS establishes common rules, infrastructure and governance for primary and secondary use of electronic health data and specifies interoperability and logging components for EHR systems.", ["ehds", "ich_e6r3"]),
            ("Risk-based software assurance emphasises confidence in automation through appropriate testing and objective evidence rather than undifferentiated documentation volume.", ["fda_csa", "ich_e6r3"]),
        ],
        "capabilities": ["Opérations pharmaceutiques et réglementées", "Ingénierie web et produit", "Architecture data, DDD et événements", "Gouvernance et assurance IA"],
        "products": COMMON_PRODUCTS + [("Note de périmètre — Assurance preuve-décision pharmaceutique", CATALOGUE)],
    },
    "pv": {
        "title": "Pharmacovigilance Data Engineering",
        "lead": "Engineer pharmacovigilance data flows for collection, case processing, traceability, duplicate/privacy controls and accountable safety review.",
        "claims": [
            ("EU GVP structures pharmacovigilance around defined quality-system and reporting processes, including collection, management and submission of suspected adverse-reaction reports.", ["ema_gvp", "fda_aems"]),
            ("FDA is consolidating adverse-event reporting into AEMS with standardised reporting, case-processing workflows and analytics; this supports data-engineering work on consistency and surveillance while leaving safety judgement accountable.", ["fda_aems", "ema_gvp"]),
        ],
        "capabilities": ["Opérations pharmaceutiques et réglementées", "Python et traitement de données", "Architecture data, DDD et événements", "Data science et machine learning"],
        "products": COMMON_PRODUCTS + [("Cohorte — Environnements régulés", CATALOGUE)],
    },
    "reg-csv": {
        "title": "Regulatory Technology & CSV Engineering",
        "lead": "Replace document-volume thinking with risk-based assurance: intended use, critical functions, test evidence, traceable changes and controlled release.",
        "claims": [
            ("FDA's 2026 Computer Software Assurance guidance defines a risk-based approach to establish confidence in production and quality-management automation and to apply rigor where risk warrants it.", ["fda_csa", "ich_e6r3"]),
            ("ICH E6(R3) reinforces the same control pattern for clinical systems through account/permission logs, interpretable audit trails, metadata review and traceable data transfers.", ["ich_e6r3", "fda_csa"]),
        ],
        "capabilities": ["Opérations pharmaceutiques et réglementées", "Gouvernance et assurance IA", "Jenkins, Terraform et supply chain", "Architecture data, DDD et événements"],
        "products": COMMON_PRODUCTS + [("Cohorte — Environnements régulés", CATALOGUE)],
    },
    "training": {
        "title": "AI Training & Adoption Engineering",
        "lead": "Treat AI training as capability transfer: role-specific knowledge, executable practice, evidence of competence and operational guardrails.",
        "claims": [
            ("Article 4 of the EU AI Act requires providers and deployers to take measures supporting AI literacy while considering technical knowledge, experience, education, training and use context.", ["eu_ai_act", "nist_gai"]),
            ("NIST's Generative AI Profile treats governance, measurement and risk management as lifecycle activities, supporting training that connects knowledge to operational controls and evaluation.", ["nist_gai", "eu_ai_act"]),
        ],
        "capabilities": ["Formation technique et ingénierie pédagogique", "Gouvernance et assurance IA", "Python et traitement de données", "Systèmes agentiques"],
        "products": COMMON_PRODUCTS + [("Cohorte — Systèmes IA & agents", CATALOGUE), ("Cohorte — Environnements régulés", CATALOGUE)],
    },
    "marketing": {
        "title": "Marketing Engineering & Evidence-Led Growth",
        "lead": "Connect positioning to observable user needs, explicit metrics, source provenance and delivery capabilities — then iterate on measured outcomes.",
        "claims": [
            ("Meaningful performance metrics start from a service's purpose, explicit benefits and hypotheses, then connect those hypotheses to data sources and ongoing iteration.", ["govuk_metrics", "govuk_success"]),
            ("Provenance makes the origin and production path of information representable; applying that principle to marketing keeps source, transformation and decision context attached to claims and measurements.", ["w3c_prov", "govuk_metrics"]),
        ],
        "capabilities": ["Ingénierie web et produit", "Architecture data, DDD et événements", "Python et traitement de données", "Formation technique et ingénierie pédagogique"],
        "products": COMMON_PRODUCTS,
    },
    "it": {
        "title": "IT, Platform & Delivery Engineering",
        "lead": "Engineer delivery systems around explicit risk outcomes, reproducible builds, observability, controlled promotion and rollback evidence.",
        "claims": [
            ("NIST CSF 2.0 frames cybersecurity as explicit outcomes that organisations can understand, assess, prioritise and communicate without prescribing a single implementation path.", ["nist_csf", "cisa_sbom"]),
            ("Software supply-chain and observability standards make dependency/build metadata and runtime telemetry first-class inputs to operational assurance.", ["cisa_sbom", "otel"]),
        ],
        "capabilities": ["Jenkins, Terraform et supply chain", "Ingénierie web et produit", "Architecture data, DDD et événements", "Sécurité des systèmes IA"],
        "products": COMMON_PRODUCTS,
    },
    "homepage": {
        "title": "AI, Data & Verifiable Systems Engineering",
        "lead": "Build, secure and evaluate systems whose decisions can be traced to sources, controls, execution evidence and accountable human review.",
        "claims": [
            ("AI assurance is a lifecycle discipline: trustworthiness, evaluation and risk management have to be integrated into design, development, use and monitoring rather than treated as a single model check.", ["nist_gai", "nist_csf"]),
            ("Provenance standards provide a machine-readable way to represent the entities, activities and agents involved in producing information, which is the technical basis for reconstructible evidence chains.", ["w3c_prov", "openlineage"]),
        ],
        "capabilities": ["Systèmes agentiques", "Sécurité des systèmes IA", "Évaluation des systèmes IA", "Architecture data, DDD et événements", "Opérations pharmaceutiques et réglementées"],
        "products": COMMON_PRODUCTS + [("Cohorte — Systèmes IA & agents", CATALOGUE), ("Cohorte — Environnements régulés", CATALOGUE)],
    },
}


def family_for(path: str) -> str:
    p = path.lower()
    if p == "pages/mickael-umt.com.html" or p.endswith("/mickael-umt.com.html") and "audiences" not in p:
        return "homepage"
    if "agentic-ai" in p or "ia-agents" in p:
        return "agentic"
    if "ai-security" in p:
        return "ai-security"
    if "blockchain" in p:
        return "blockchain"
    if "data-engineering" in p:
        return "data"
    if "cdm-automation" in p:
        return "clinical-data"
    if "pv-data-engineer" in p:
        return "pv"
    if "reg-csv" in p:
        return "reg-csv"
    if "healthtech" in p or "pharmaceutical-evidence-assurance" in p:
        return "healthtech"
    if "training" in p:
        return "training"
    if "marketing-engineering" in p or "/growth/" in p or "audiences" in p:
        return "marketing"
    if "/it/" in p:
        return "it"
    return "homepage"


def source_refs(claim_sources: list[str]) -> str:
    refs = []
    for idx, key in enumerate(claim_sources, 1):
        title, url = SOURCES[key]
        refs.append(f'<a class="cl-ref" href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">[{idx}] {html.escape(title)}</a>')
    return " ".join(refs)


def build_page(path: str, seed_b64: str, seed_sha: str) -> str:
    fam = FAMILIES[family_for(path)]
    claims = []
    bibliography = {}
    for i, (text, keys) in enumerate(fam["claims"], 1):
        for k in keys:
            bibliography[k] = SOURCES[k]
        claims.append(
            f'''<article class="cl-claim" data-claim-index="{i}" data-claim-status="EXTERNAL_COMPRESSION_PENDING_FORMAL_JUDGE">
              <div class="cl-eyebrow">Research-compressed claim {i:02d}</div>
              <p>{html.escape(text)}</p>
              <div class="cl-sources">{source_refs(keys)}</div>
            </article>'''
        )
    caps = "".join(f'<li><span>{html.escape(c)}</span><small>CV-derived capability · {CAPABILITY_SNAPSHOT}</small></li>' for c in fam["capabilities"])
    products = "".join(f'<li><a href="{html.escape(url)}">{html.escape(name)}</a><small>semi-mobile commercial context · not evidentiary proof</small></li>' for name, url in fam["products"])
    bib = "".join(
        f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(title)}</a></li>'
        for title, url in bibliography.values()
    )
    return f'''<!-- CLAIM_LOOP_UPGRADE_BEGIN -->
<style>
:root{{--cl-bg:#060820;--cl-panel:#0d1230;--cl-text:#f5f7ff;--cl-muted:#a9b2d0;--cl-line:#29325c;--cl-accent:#8fa5ff;--cl-ok:#72e0b4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--cl-bg);color:var(--cl-text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}}
.claim-loop-page{{max-width:1120px;margin:0 auto;padding:64px 24px 96px}}.cl-kicker{{font:600 12px/1.2 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.11em;text-transform:uppercase;color:var(--cl-accent)}}
h1{{font-size:clamp(38px,6vw,76px);line-height:.98;letter-spacing:-.04em;max-width:1000px;margin:18px 0 22px}}.cl-lead{{font-size:clamp(19px,2.4vw,28px);max-width:900px;color:#dbe1ff}}
.cl-contract{{margin:36px 0;padding:16px 18px;border:1px solid var(--cl-line);border-radius:16px;background:linear-gradient(180deg,#111735,#0a0e24);color:var(--cl-muted)}}
.cl-grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;margin-top:44px}}.cl-claim{{grid-column:span 6;background:var(--cl-panel);border:1px solid var(--cl-line);border-radius:20px;padding:24px}}.cl-claim p{{font-size:20px;margin:8px 0 18px}}
.cl-eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--cl-ok)}}.cl-sources{{display:flex;flex-direction:column;gap:8px}}.cl-ref,a{{color:#b7c5ff;text-decoration-thickness:1px;text-underline-offset:3px}}
.cl-section{{margin-top:56px;border-top:1px solid var(--cl-line);padding-top:28px}}.cl-section h2{{font-size:28px;letter-spacing:-.02em}}.cl-list{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:0;list-style:none}}.cl-list li{{display:flex;flex-direction:column;gap:4px;padding:16px;border:1px solid var(--cl-line);border-radius:14px;background:#090d22}}.cl-list small{{color:var(--cl-muted)}}
.cl-boundary{{border-left:3px solid var(--cl-accent);padding:3px 0 3px 18px;color:var(--cl-muted);max-width:900px}}.cl-bib li{{margin:.55em 0}}.cl-meta{{margin-top:60px;font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:#7f89ab;word-break:break-word}}
@media(max-width:760px){{.cl-claim{{grid-column:1/-1}}.cl-list{{grid-template-columns:1fr}}.claim-loop-page{{padding-top:42px}}}}
</style>
<main class="claim-loop-page" data-claim-loop="{LOOP_ID}" data-judge="{JUDGE_ID}" data-capability-snapshot="{CAPABILITY_SNAPSHOT}" data-commercial-snapshot="{COMMERCIAL_SNAPSHOT}" data-publication-status="PENDING_FORMAL_LLM_JUDGE">
  <header>
    <div class="cl-kicker">Evidence-led consulting · external research × proven capability</div>
    <h1>{html.escape(fam['title'])}</h1>
    <p class="cl-lead">{html.escape(fam['lead'])}</p>
    <div class="cl-contract"><strong>Copy contract.</strong> Existing page copy is retained only as an iteration-0 seed. Visible claims below are compressed from external sources and bounded by CV-derived capabilities. Products and configurations can specialise the offer, but cannot create evidence or expand the capability boundary. Formal publication remains fail-closed until the three-replica NeoFort judge passes.</div>
  </header>

  <section class="cl-grid" aria-label="Research-compressed claims">{''.join(claims)}</section>

  <section class="cl-section">
    <div class="cl-kicker">Invariant factor</div>
    <h2>Capabilities this positioning is allowed to sell</h2>
    <ul class="cl-list">{caps}</ul>
  </section>

  <section class="cl-section">
    <div class="cl-kicker">Semi-mobile factor</div>
    <h2>Current products and delivery configurations</h2>
    <ul class="cl-list">{products}</ul>
  </section>

  <section class="cl-section">
    <div class="cl-kicker">Boundary</div>
    <h2>What the copy does not claim</h2>
    <p class="cl-boundary">No guaranteed business, regulatory, safety or performance outcome is inferred from a publication, technology or capability. External sources establish the problem/mechanism boundary; CV-derived evidence establishes delivery capability; product context only determines how that capability can currently be packaged.</p>
  </section>

  <section class="cl-section">
    <div class="cl-kicker">External evidence</div>
    <h2>Bibliography</h2>
    <ol class="cl-bib">{bib}</ol>
  </section>

  <section class="cl-section">
    <a href="{CATALOGUE}">Review current products and configurations →</a>
  </section>

  <div class="cl-meta">artifact={html.escape(path)} · loop={LOOP_ID} · judge={JUDGE_ID} · seed_sha256={seed_sha}</div>
</main>
<script type="application/octet-stream" id="claim-loop-seed-archive" data-encoding="base64" data-sha256="{seed_sha}">{seed_b64}</script>
<!-- CLAIM_LOOP_UPGRADE_END -->'''


def extract_seed(body_inner: str) -> str:
    marker = re.search(
        r'<script\s+type=["\']application/octet-stream["\']\s+id=["\']claim-loop-seed-archive["\'][^>]*>(.*?)</script>',
        body_inner,
        flags=re.I | re.S,
    )
    if marker:
        try:
            return base64.b64decode(marker.group(1).strip()).decode("utf-8")
        except Exception:
            pass
    return body_inner


def upgrade_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'(<body\b[^>]*>)(.*?)(</body\s*>)', text, flags=re.I | re.S)
    if not m:
        return False
    seed = extract_seed(m.group(2))
    seed_sha = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    seed_b64 = base64.b64encode(seed.encode("utf-8")).decode("ascii")
    rel = path.relative_to(ROOT).as_posix()
    upgraded_body = build_page(rel, seed_b64, seed_sha)
    new_text = text[:m.start(2)] + upgraded_body + text[m.end(2):]

    # Force preview/fail-closed semantics for the branch artifact.
    if 'name="robots"' not in new_text.lower() and "name='robots'" not in new_text.lower():
        new_text = re.sub(r'</head\s*>', '<meta name="robots" content="noindex,nofollow">\n</head>', new_text, count=1, flags=re.I)
    new_text = re.sub(
        r'(<html\b)([^>]*)(>)',
        lambda x: x.group(1) + re.sub(r'\sdata-claim-loop-version=["\'][^"\']*["\']', '', x.group(2), flags=re.I) + ' data-claim-loop-version="external-capability-v1"' + x.group(3),
        new_text,
        count=1,
        flags=re.I,
    )

    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    html_files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    changed = []
    for path in html_files:
        if upgrade_file(path):
            changed.append(path.relative_to(ROOT).as_posix())
    report = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "capability_snapshot": CAPABILITY_SNAPSHOT,
        "commercial_snapshot": COMMERCIAL_SNAPSHOT,
        "html_total": len(html_files),
        "changed": len(changed),
        "files": changed,
        "status": "PENDING_FORMAL_LLM_JUDGE",
    }
    out = ROOT / "reports" / "claim-loop-all-html.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if len(html_files) == 0:
        raise SystemExit("No HTML files found")


if __name__ == "__main__":
    main()
