from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "expertises/blockchain/blockchain.html"
CONTRACT = ROOT / "contracts/blockchain-offer-structure-lock.json"


class SectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict[str, str]] = []
        self.nav_hrefs: list[str] = []
        self.in_localnav = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k: (v or "") for k, v in attrs}
        if tag == "nav" and d.get("class") == "localnav":
            self.in_localnav = True
        if tag == "section":
            self.sections.append(d)
        if tag == "a" and self.in_localnav and d.get("href", "").startswith("#"):
            self.nav_hrefs.append(d["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_localnav:
            self.in_localnav = False


def fail(message: str) -> None:
    raise SystemExit(f"BLOCK: {message}")


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    html = PAGE.read_text(encoding="utf-8")
    parser = SectionParser()
    parser.feed(html)

    expected = contract["sections"]
    if len(parser.sections) != contract["section_count"]:
        fail(f"section count {len(parser.sections)} != {contract['section_count']}")

    actual_ids = [s.get("id") for s in parser.sections]
    expected_ids = [s["id"] for s in expected]
    if actual_ids != expected_ids:
        fail(f"section order mismatch: {actual_ids} != {expected_ids}")

    for actual, spec in zip(parser.sections, expected, strict=True):
        if actual.get("data-section-kind") != spec["kind"]:
            fail(f"{spec['id']}: data-section-kind mismatch")
        if actual.get("data-semantic-role") != spec["semantic_role"]:
            fail(f"{spec['id']}: data-semantic-role mismatch")

    expected_nav = [f"#{sid}" for sid in expected_ids if sid != "top"]
    if parser.nav_hrefs != expected_nav:
        fail(f"local navigation order mismatch: {parser.nav_hrefs} != {expected_nav}")

    for claim_id in contract["preserve"]["evidence_claim_ids"]:
        count = len(re.findall(rf'\bid=["\']{re.escape(claim_id)}["\']', html))
        if count != 1:
            fail(f"evidence claim anchor {claim_id} occurs {count} times")

    for target in contract["preserve"]["required_cta_targets"]:
        if f'href="{target}"' not in html:
            fail(f"required CTA target missing: {target}")

    devicev_id = contract["preserve"]["devicev_contract_id"]
    m = re.search(
        rf'<script[^>]+id=["\']{re.escape(devicev_id)}["\'][^>]*>(.*?)</script>',
        html,
        flags=re.S,
    )
    if not m:
        fail(f"missing embedded contract {devicev_id}")
    embedded = json.loads(m.group(1))
    embedded_structure = embedded.get("structure_contract", {})
    if embedded_structure.get("section_count") != contract["section_count"]:
        fail("embedded structure section_count drift")
    if embedded_structure.get("order") != expected_ids:
        fail("embedded structure order drift")
    if embedded_structure.get("section_delta_allowed") != 0:
        fail("embedded structure must keep section_delta_allowed=0")
    if embedded_structure.get("reorder_allowed") is not False:
        fail("embedded structure must keep reorder_allowed=false")

    required_offer_codes = ["ZK-FIT", "ZK-XB", "ZK-ASSET", "ZK-RD", "ZK"]
    offers_match = re.search(
        r'<section[^>]+id=["\']offers["\'][^>]*>(.*?)</section>',
        html,
        flags=re.S,
    )
    if not offers_match:
        fail("offers section missing")
    offers_html = offers_match.group(1)
    for code in required_offer_codes:
        if code not in offers_html:
            fail(f"commercial offer code missing from offers section: {code}")
    if offers_html.count('href="#engagement"') < len(required_offer_codes):
        fail("each commercial configuration must route to engagement")

    if 'data-commercial-copy-version="blockchain-commercial-v1"' not in html:
        fail("commercial copy version marker missing")

    print(
        "PASS: blockchain offer structure locked — 18/18 sections, canonical order, "
        "semantic roles, evidence anchors, CTAs and commercial configurations preserved"
    )


if __name__ == "__main__":
    main()
