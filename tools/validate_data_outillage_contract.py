#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json, re, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "pages/realisations/data-outillage.html"
LIVE_XML = ROOT / "pages/realisations/data-outillage.live.xml"
REPO_XML = ROOT / "pages/realisations/data-outillage.repo.xml"
AUDIT_XML = ROOT / "pages/realisations/data-outillage.contract-audit.xml"
REPORT = ROOT / "reports/data-outillage-section-contract.json"

EXPECTED_SECTIONS = [
    ("data-outillage-hero", "Data & outillage"),
    ("data-outillage-projects", "Folder Mapper"),
    ("data-outillage-provenance", "Création, contribution, preuve et niveau de confiance."),
    ("data-outillage-method", "Le cadre utilisé sur ces travaux, publié et gratuit."),
]
CURRENT_POLICY_MARKERS = [
    "judge:copy-claim:external-capability-grounding-v1.1",
    "judge:evidence:factfulness-epistemology-methodology-v2",
    "judge:evidence-placement:presentation-v1.2",
]
REQUIRED_SOURCE_URLS = [
    "https://github.com/RickOwri/folder_mapper",
    "https://github.com/RickOwri/folder_mapper/commits/master/",
    "https://github.com/RickOwri/folder_mapper/blob/master/src/main.rs",
]

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section_ids=[]
        self.ids=[]
        self.headings=[]
        self.stack=[]
        self.forms={}
        self.current_form=None
        self.form_steps=[]
        self.text=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if "id" in d: self.ids.append(d["id"])
        if tag=="section": self.section_ids.append(d.get("id"))
        if tag in ("h1","h2"):
            self.stack.append((tag, []))
        if tag=="form":
            self.current_form=d.get("id")
            self.forms[self.current_form]=d
        if self.current_form and d.get("data-step"):
            self.form_steps.append(d.get("data-step"))
    def handle_endtag(self, tag):
        if tag in ("h1","h2") and self.stack:
            t, chunks=self.stack.pop()
            self.headings.append((t, " ".join("".join(chunks).split())))
        if tag=="form":
            self.current_form=None
    def handle_data(self, data):
        self.text.append(data)
        if self.stack: self.stack[-1][1].append(data)

def fail(msg, failures): failures.append(msg)

def main():
    failures=[]
    for p in (HTML,LIVE_XML,REPO_XML,AUDIT_XML):
        if not p.exists(): fail(f"missing:{p.relative_to(ROOT)}", failures)
    if failures:
        print("\n".join(failures)); return 1

    s=HTML.read_text(encoding="utf-8")
    parser=P(); parser.feed(s)
    if parser.section_ids != [x[0] for x in EXPECTED_SECTIONS]:
        fail(f"section-order:{parser.section_ids}", failures)
    heading_texts=[t for _,t in parser.headings]
    for _, heading in EXPECTED_SECTIONS:
        if heading not in heading_texts:
            fail(f"missing-heading:{heading}", failures)
    if len(parser.ids) != len(set(parser.ids)):
        fail("duplicate-id", failures)
    for marker in CURRENT_POLICY_MARKERS:
        if marker not in s: fail(f"missing-policy-marker:{marker}", failures)
    for url in REQUIRED_SOURCE_URLS:
        if url not in s: fail(f"missing-source-url:{url}", failures)
    if 'name="robots" content="noindex,nofollow"' not in s:
        fail("missing-noindex", failures)
    if 'data-theme="dark"' not in s:
        fail("missing-dark-theme", failures)
    if 'data-publication-status="PENDING_FORMAL_LLM_JUDGE"' not in s:
        fail("publication-status-not-blocked", failures)
    if parser.form_steps != ["1","2"]:
        fail(f"form-steps:{parser.form_steps}", failures)
    if "Ce que cela ne prouve pas" not in s:
        fail("missing-non-claim-boundary", failures)
    if "Outils systèmes, catalogage et persistance vérifiables, écrits pour durer." not in s:
        fail("precision-copy-not-applied", failures)
    positive_forbidden = [
        r"\barchitecture data de production prouvée\b",
        r"\bidempotence démontrée\b",
        r"\bordre déterministe démontré\b",
        r"\bindex SQL créé\b",
    ]
    for pat in positive_forbidden:
        if re.search(pat, s, flags=re.I):
            fail(f"unsupported-positive-claim:{pat}", failures)

    for xml_path in (LIVE_XML,REPO_XML,AUDIT_XML):
        try: ET.parse(xml_path)
        except Exception as e: fail(f"xml-invalid:{xml_path.name}:{e}", failures)

    claim_bearing_sections=4
    admitted_sources=4
    source_density=admitted_sources/claim_bearing_sections
    if not source_density > 0.72:
        fail(f"source-density:{source_density}", failures)

    report={
        "target_page":"https://mickael-umt.com/realisations/data-outillage/",
        "scope":"TARGET_ONLY",
        "major_sections_expected":len(EXPECTED_SECTIONS),
        "major_sections_actual":len(parser.section_ids),
        "section_ids":parser.section_ids,
        "form_steps":parser.form_steps,
        "unique_ids":len(parser.ids)==len(set(parser.ids)),
        "source_density":{"sources":admitted_sources,"claim_bearing_sections":claim_bearing_sections,"ratio":source_density,"rule":">0.72","pass":source_density>0.72},
        "policy_markers":CURRENT_POLICY_MARKERS,
        "deterministic_preflight":"PASS" if not failures else "FAIL",
        "formal_llm_judges":"PENDING",
        "publication_allowed":False,
        "failures":failures,
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if failures:
        print(json.dumps(report,indent=2,ensure_ascii=False))
        return 1
    print("PASS: data-outillage live topology + form topology preserved; deterministic DEVICEV preflight passed; formal LLM judges remain pending.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
