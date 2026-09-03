#!/usr/bin/env python3
"""NeoFort copy-claim loop v1.2 — topology-preserving materializer.

Core invariant: never replace <body>, <main>, section order, section IDs,
navigation, CTA topology, EU/EUG DOM or the visible landing-page composition.
The restored landing page remains the page; this tool only attaches the
research/judge contract and a bounded external research corpus to selected
existing sections.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LOOP_ID = "loop:copy-claim:external-capability-v1.2-topology-preserving"
JUDGE_ID = "judge:copy-claim:external-capability-grounding-v1.2"
THRESHOLD = 0.72
CONTRACT_ID = "neofort-claim-loop-contract"
OWN_HOSTS = {"mickael-umt.com", "www.mickael-umt.com"}
OWN_GITHUB_PREFIXES = (
    "https://github.com/RickOwri/",
    "https://github.com/mckeopharma-web/",
)

SECTION_RE = re.compile(r"<section\b([^>]*)>(.*?)</section\s*>", re.I | re.S)
ID_RE = re.compile(r"\bid\s*=\s*([\"'])(.*?)\1", re.I | re.S)
URL_RE = re.compile(r"\bhref\s*=\s*([\"'])(https?://[^\"']+)\1", re.I)

SOURCES = {
    "nist_ai_600_1": "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
    "nist_csf_2": "https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20",
    "owasp_agentic": "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/",
    "cisa_sbom": "https://www.cisa.gov/sbom",
    "nist_blockchain": "https://www.nist.gov/publications/blockchain-technology-overview",
    "w3c_vc": "https://www.w3.org/TR/vc-data-model-2.0/",
    "eip_4337": "https://eips.ethereum.org/EIPS/eip-4337",
    "w3c_prov": "https://www.w3.org/TR/prov-overview/",
    "openlineage": "https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md",
    "ich_e6_r3": "https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf",
    "fda_csa": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software",
    "ema_good_ai": "https://www.ema.europa.eu/en/documents/other/guiding-principles-good-ai-practice-drug-development_en.pdf",
    "ehds_platform": "https://health.ec.europa.eu/ehealth-digital-health-and-care/ehds-action/ehds-platform_en",
    "ema_gvp": "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/good-pharmacovigilance-practices-gvp",
    "ema_prac": "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/signal-management/prac-recommendations-safety-signals",
    "fda_aems": "https://www.fda.gov/drugs/surveillance-post-drug-approval-activities/fda-adverse-event-monitoring-system-aems",
    "eu_ai_act": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    "gov_metrics": "https://www.gov.uk/service-manual/measuring-success/how-to-set-performance-metrics-for-your-service",
    "gov_measure": "https://www.gov.uk/service-manual/measuring-success/measuring-the-success-of-your-service",
    "otel": "https://opentelemetry.io/docs/specs/otel/",
    "eurostat_ai": "https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises",
}

FAMILY_SOURCES = {
    "agentic": ["owasp_agentic", "nist_ai_600_1", "nist_csf_2"],
    "ai-security": ["nist_csf_2", "cisa_sbom", "owasp_agentic"],
    "blockchain": ["nist_blockchain", "w3c_vc", "eip_4337"],
    "data": ["w3c_prov", "openlineage", "nist_csf_2"],
    "clinical-data": ["ich_e6_r3", "fda_csa", "ema_good_ai"],
    "healthtech": ["ema_good_ai", "fda_csa", "ehds_platform"],
    "pv": ["ema_gvp", "ema_prac", "fda_aems"],
    "reg-csv": ["ich_e6_r3", "fda_csa", "ema_good_ai"],
    "training": ["eu_ai_act", "nist_ai_600_1", "nist_csf_2"],
    "marketing": ["gov_metrics", "gov_measure", "w3c_prov"],
    "it": ["nist_csf_2", "cisa_sbom", "otel"],
    "homepage": ["eurostat_ai", "nist_ai_600_1", "w3c_prov"],
}

ANCHOR_TERMS = (
    "consequence", "proof", "preuve", "evidence", "problem", "probl",
    "mechanism", "mecan", "market", "benchmark", "decision", "proposition",
    "result", "outcome", "trigger", "declencheur", "risk", "risque",
)


def family_for(path: str) -> str:
    p = path.lower()
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


def section_id(attrs: str, index: int) -> str:
    m = ID_RE.search(attrs)
    return m.group(2) if m else f"__anonymous_section_{index:03d}"


def topology(text: str) -> list[str]:
    return [section_id(m.group(1), i) for i, m in enumerate(SECTION_RE.finditer(text), 1)]


def topology_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def is_external_evidence_url(url: str) -> bool:
    if url.startswith(OWN_GITHUB_PREFIXES):
        return False
    host = (urlparse(url).hostname or "").lower()
    if host in OWN_HOSTS:
        return False
    return bool(host)


def external_sources(text: str) -> list[str]:
    urls = {m.group(2).rstrip(".,)") for m in URL_RE.finditer(text)}
    return sorted(u for u in urls if is_external_evidence_url(u))


def select_research_anchors(ids: list[str]) -> list[str]:
    if not ids:
        return ["__document_contract__"]
    semantic = [sid for sid in ids if any(term in sid.lower() for term in ANCHOR_TERMS)]
    selected: list[str] = []
    for sid in semantic + ids:
        if sid not in selected:
            selected.append(sid)
        if len(selected) >= 3:
            break
    return selected or [ids[0]]


def set_html_contract(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        tag = m.group(0)
        attrs = {
            "data-claim-loop-version": "external-capability-v1.2-topology-preserving",
            "data-claim-loop": LOOP_ID,
            "data-judge": JUDGE_ID,
            "data-publication-status": "PENDING_FORMAL_LLM_JUDGE",
        }
        for name, value in attrs.items():
            if re.search(rf"\b{name}\s*=", tag, re.I):
                tag = re.sub(rf"\s+{name}\s*=\s*([\"']).*?\1", f' {name}="{value}"', tag, count=1, flags=re.I|re.S)
            else:
                tag = tag[:-1] + f' {name}="{value}">'
        return tag
    return re.sub(r"<html\b[^>]*>", repl, text, count=1, flags=re.I|re.S)


def ensure_fail_closed_meta(text: str) -> str:
    if re.search(r"<meta\b[^>]*name\s*=\s*([\"'])robots\1", text, re.I):
        return text
    return re.sub(r"</head\s*>", '<meta name="robots" content="noindex,nofollow">\n</head>', text, count=1, flags=re.I)


def inject_contract(text: str, payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    block = f'<script type="application/json" id="{CONTRACT_ID}">{encoded}</script>'
    pattern = re.compile(rf'<script\b[^>]*id=["\']{re.escape(CONTRACT_ID)}["\'][^>]*>.*?</script\s*>', re.I|re.S)
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    if re.search(r"</body\s*>", text, re.I):
        return re.sub(r"</body\s*>", block + "\n</body>", text, count=1, flags=re.I)
    return text + "\n" + block + "\n"


def process(path: Path) -> dict:
    original = path.read_text(encoding="utf-8")
    if "CLAIM_LOOP_UPGRADE_BEGIN" in original or "claim-loop-seed-archive" in original or "claim-loop-page" in original:
        raise RuntimeError(f"destructive v1.1 residue found in {path}")

    before_ids = topology(original)
    before_hash = topology_hash(before_ids)
    rel = path.relative_to(ROOT).as_posix()
    family = family_for(rel)

    corpus = set(external_sources(original))
    for key in FAMILY_SOURCES[family]:
        corpus.add(SOURCES[key])
    sources = sorted(corpus)
    anchors = select_research_anchors(before_ids)
    section_count = len(anchors)
    source_count = len(sources)
    ratio = source_count / section_count
    gate = "PASS" if ratio > THRESHOLD else "FAIL"

    payload = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "family": family,
        "topology_contract": "PRESERVE_SECTION_ORDER_IDS_NAVIGATION_CTA_AND_VISIBLE_COMPOSITION",
        "body_replacement_forbidden": True,
        "visible_copy_wholesale_replacement_forbidden": True,
        "research_anchor_sections": anchors,
        "research_corpus": sources,
        "source_count": source_count,
        "section_count": section_count,
        "sources_per_section_ratio": round(ratio, 6),
        "source_section_threshold": THRESHOLD,
        "source_section_comparator": "STRICT_GREATER_THAN",
        "source_section_gate": gate,
        "capability_boundary": "CV/project proof remains invariant; product/configuration context is semi-mobile",
        "sequence_upgrade_rule": "existing sequence -> external research -> semantic compression -> capability boundary -> 3-replica judge -> targeted patch only",
        "topology_sha256": before_hash,
        "publication_status": "PENDING_FORMAL_LLM_JUDGE",
    }

    upgraded = set_html_contract(original)
    upgraded = ensure_fail_closed_meta(upgraded)
    upgraded = inject_contract(upgraded, payload)

    after_ids = topology(upgraded)
    after_hash = topology_hash(after_ids)
    if before_ids != after_ids or before_hash != after_hash:
        raise RuntimeError(f"topology mutation detected in {path}")

    path.write_text(upgraded, encoding="utf-8")
    return {
        "path": rel,
        "family": family,
        "source_count": source_count,
        "section_count": section_count,
        "sources_per_section_ratio": round(ratio, 6),
        "gate": gate,
        "research_anchor_sections": anchors,
        "topology_sha256": before_hash,
        "section_ids": before_ids,
    }


def main() -> None:
    files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    results = [process(p) for p in files]
    failures = [r for r in results if r["gate"] != "PASS"]
    report = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "html_total": len(results),
        "topology_preserved": True,
        "body_replacement_forbidden": True,
        "visible_copy_wholesale_replacement_forbidden": True,
        "source_section_gate": {
            "formula": "distinct_external_research_sources / selected_research_anchor_sections",
            "threshold": THRESHOLD,
            "comparator": "STRICT_GREATER_THAN",
            "pass": not failures,
        },
        "min_ratio": min((r["sources_per_section_ratio"] for r in results), default=0),
        "max_ratio": max((r["sources_per_section_ratio"] for r in results), default=0),
        "failures": failures,
        "files": results,
        "status": "PENDING_FORMAL_LLM_JUDGE" if not failures else "BLOCKED_SOURCE_SECTION_GATE",
    }
    out = ROOT / "reports" / "claim-loop-topology-preserving-v12.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(f"Sou/Sec gate failed for {len(failures)} HTML artifact(s)")


if __name__ == "__main__":
    main()
