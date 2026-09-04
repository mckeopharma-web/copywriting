#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

TARGET_URL = "https://mickael-umt.com/engagement/audiences/#avatar-agentic-ai"
EXPECTED_ORDER = [
    "__anonymous_section_001",
    "identity",
    "tensions",
    "aspirations",
    "drivers",
    "before-after",
    "evidence",
    "capability",
    "qualification",
    "references",
]
CANONICAL = "0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8"

class ContractHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section_ids = []
        self.html_attrs = {}
        self.main_ids = []
        self.hrefs = []
        self._anonymous = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "html":
            self.html_attrs = d
        elif tag == "main" and d.get("id"):
            self.main_ids.append(d["id"])
        elif tag == "section":
            sid = d.get("id")
            if not sid:
                self._anonymous += 1
                sid = f"__anonymous_section_{self._anonymous:03d}"
            self.section_ids.append(sid)
        elif tag == "a" and d.get("href"):
            self.hrefs.append(d["href"])

def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

def main():
    if len(sys.argv) != 3:
        fail("usage: validate_avatar_agentic_ai_section_contract.py CONTRACT.xml TARGET.html")
    xml_path, html_path = map(Path, sys.argv[1:])
    root = ET.parse(xml_path).getroot()

    if root.attrib.get("scope") != f"ONLY {TARGET_URL}":
        fail("scope must remain target-only")
    if root.attrib.get("publication_allowed") != "false":
        fail("publication must remain blocked until formal judge materializes")
    if root.attrib.get("html_mutation_allowed") != "false":
        fail("audit commit must not silently mutate target HTML")

    canonical = root.findtext("./v4_reference_contract/canonical_full_order")
    if canonical != CANONICAL:
        fail("v4 canonical order drift")

    live = root.find("./live_page_xml")
    if live is None or live.attrib.get("target_fragment") != "avatar-agentic-ai":
        fail("live target fragment missing")
    qualifier = live.find("./section[@key='qualifier']")
    if qualifier is None or qualifier.attrib.get("screens") != "8":
        fail("live parent qualifier must remain 8 screens")

    repo = root.find("./repository_html_xml")
    if repo is None:
        fail("repository_html_xml missing")
    xml_ids = [s.attrib["id"] for s in repo.findall("./main/section")]
    if xml_ids != EXPECTED_ORDER:
        fail(f"XML repository section order drift: {xml_ids}")

    p = ContractHTMLParser()
    p.feed(html_path.read_text(encoding="utf-8"))
    if p.html_attrs.get("data-theme") != "dark":
        fail("target artifact must remain dark")
    if p.html_attrs.get("data-target") != TARGET_URL:
        fail("target URL drift")
    if p.html_attrs.get("data-publication-status") != "PENDING_FORMAL_LLM_JUDGE":
        fail("formal judge status must not be promoted by deterministic CI")
    if p.main_ids != ["avatar-agentic-ai"]:
        fail(f"main id drift: {p.main_ids}")
    if p.section_ids != EXPECTED_ORDER:
        fail(f"HTML section topology drift: {p.section_ids}")
    if "https://mickael-umt.com/qualification/" not in p.hrefs:
        fail("qualification CTA route drift")

    formal = root.find("./validation/formal_placement_judge")
    pub = root.find("./validation/publication")
    if formal is None or formal.attrib.get("status") != "PENDING_NOT_FABRICATED":
        fail("formal judge result must be explicit PENDING_NOT_FABRICATED")
    if pub is None or pub.attrib.get("status") != "BLOCKED_PENDING_3_REPLICA_PLACEMENT_JUDGE":
        fail("publication must remain fail-closed")

    print("PASS: avatar-agentic-ai section contract")
    print("PASS: /expertises/ and /programme/ v4 reference contract recorded")
    print("PASS: parent 8-screen qualifier preserved")
    print("PASS: target HTML topology preserved")
    print("BLOCKED: formal 3-replica evidence-placement judge not fabricated")

if __name__ == "__main__":
    main()
