#!/usr/bin/env python3
"""Fail-closed section-contract validator for expertises/reg-csv only.

This validator proves topology, navigation, form placement, canonical semantic-token
expansion and claim-anchor cardinality. It does not manufacture NeoFort LLM verdicts.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "expertises/reg-csv/reg-csv.html"
LIVE_XML = ROOT / "expertises/reg-csv/reg-csv.live.structure.2026-09-04.xml"
REPO_XML = ROOT / "expertises/reg-csv/reg-csv.repo.structure.2026-09-04.xml"

CANONICAL = [0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8]
PHYSICAL = [
    "hero","mandat","declencheurs","consequences","pour-qui","qualification",
    "proposition","attributs","offres","livrables","avant-apres","resultats",
    "preuves","perimetre","deroule","modules","capacites","intersection",
    "pricing","engagements","questions","engagement",
]
ANCHORS = [
    "declencheurs","consequences","pour-qui","qualification","proposition",
    "offres","livrables","avant-apres","resultats","preuves","perimetre",
    "deroule","modules","intersection","engagements","questions","engagement",
]
CLAIM_IDS = ["claim-annex11-risk", "claim-fda-csa-risk"]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.anchorbar_depth = 0
        self.sections: list[str] = []
        self.section_stack: list[str] = []
        self.anchors: list[str] = []
        self.forms: list[str | None] = []
        self.id_counts: Counter[str] = Counter()
        self.html_attrs: dict[str, str] = {}
        self.contract_payload_seen = False

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        if tag == "html":
            self.html_attrs = a
        if "id" in a:
            self.id_counts[a["id"]] += 1
            if a["id"] == "neofort-claim-loop-contract":
                self.contract_payload_seen = True
        if tag == "main":
            self.in_main = True
        if tag == "nav" and "anchorbar" in a.get("class", "").split():
            self.anchorbar_depth = 1
        elif self.anchorbar_depth:
            self.anchorbar_depth += 1
        if self.anchorbar_depth and tag == "a":
            href = a.get("href", "")
            if href.startswith("#"):
                self.anchors.append(href[1:])
        if self.in_main and tag == "section":
            sid = a.get("id") or a.get("data-section-id")
            if not sid:
                raise SystemExit("FAIL: every main section must expose id or data-section-id")
            self.sections.append(sid)
            self.section_stack.append(sid)
        if self.in_main and tag == "form":
            self.forms.append(self.section_stack[-1] if self.section_stack else None)

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.in_main and self.section_stack:
            self.section_stack.pop()
        if self.anchorbar_depth:
            self.anchorbar_depth -= 1
        if tag == "main":
            self.in_main = False


def xml_contract(path: Path) -> dict:
    root = ET.parse(path).getroot()
    canonical = [int(x.attrib["id"]) for x in root.find("CanonicalSemanticOrder").findall("Token")]
    physical, expansion = [], []
    for section in root.find("PhysicalSections").findall("Section"):
        physical.append(section.attrib["id"])
        expansion.extend(int(x.attrib["id"]) for x in section.findall("CanonicalToken"))
    anchors = [x.attrib["target"].lstrip("#") for x in root.find("LocalNavigation").findall("Anchor")]
    forms = [(x.attrib["parentSection"], int(x.attrib["canonicalToken"])) for x in root.find("Forms").findall("Form")]
    claims = [(x.attrib["claimId"], x.attrib["xpath"], int(x.attrib["expectedMatchCount"])) for x in root.find("EvidencePlacements").findall("Placement")]
    return {"canonical": canonical, "physical": physical, "expansion": expansion, "anchors": anchors, "forms": forms, "claims": claims}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for path in (HTML_PATH, LIVE_XML, REPO_XML):
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    live = xml_contract(LIVE_XML)
    repo = xml_contract(REPO_XML)
    if live != repo:
        fail("live XML and repository XML disagree on the structural contract")
    if live["canonical"] != CANONICAL:
        fail(f"canonical order mismatch: {live['canonical']}")
    if live["physical"] != PHYSICAL:
        fail(f"XML physical-section order mismatch: {live['physical']}")
    if live["expansion"] != CANONICAL:
        fail(f"physical-to-canonical expansion mismatch: {live['expansion']}")
    if live["anchors"] != ANCHORS:
        fail(f"XML local-navigation mismatch: {live['anchors']}")
    if live["forms"] != [("engagement", 8)]:
        fail(f"XML form contract mismatch: {live['forms']}")

    html = HTML_PATH.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)

    if parser.html_attrs.get("data-theme") not in {"dark", "night"}:
        fail("target HTML is not explicitly dark/night mode")
    if parser.sections != PHYSICAL:
        fail(f"HTML physical-section order drifted: {parser.sections}")
    if parser.anchors != ANCHORS:
        fail(f"HTML anchorbar drifted: {parser.anchors}")
    if parser.forms != ["engagement"]:
        fail(f"expected exactly one inline form under engagement; got {parser.forms}")
    if not parser.contract_payload_seen:
        fail("missing neofort-claim-loop-contract payload")
    for claim_id in CLAIM_IDS:
        if parser.id_counts[claim_id] != 1:
            fail(f"{claim_id} must resolve exactly once; got {parser.id_counts[claim_id]}")

    forbidden = ["CLAIM_LOOP_UPGRADE_BEGIN", "claim-loop-seed-archive", 'class="claim-loop-page"']
    residue = [item for item in forbidden if item in html]
    if residue:
        fail(f"destructive replacement residue detected: {residue}")

    print(
        "PASS reg-csv section contract: "
        f"{len(parser.sections)} physical sections / {len(CANONICAL)} canonical semantic tokens / "
        f"{len(parser.anchors)} anchors / {len(parser.forms)} inline form / "
        f"{len(CLAIM_IDS)} exact evidence claim anchors."
    )
    print("PASS scope: expertises/reg-csv only; visible structure and form topology preserved.")
    print("NOTE: semantic EvidencePlacement re-judgement remains a separate NeoFort fail-closed gate.")


if __name__ == "__main__":
    main()
