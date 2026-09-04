from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "expertises/agentic-ai/agentic-ai-live-devicev-v1.html"
CONTRACT = ROOT / "contracts/agentic-ai-offer-structure-lock.json"
LIVE_XML = ROOT / "expertises/agentic-ai/contracts/live-agentic-ai.structure.xml"
REPO_XML = ROOT / "expertises/agentic-ai/contracts/repository-agentic-ai.structure.xml"
PLACEMENT = ROOT / "expertises/agentic-ai/evidence/agentic-ai.devicev-placement-candidates.v1.json"


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict[str, str]] = []
        self.nav_hrefs: list[str] = []
        self.in_localnav = False
        self.element_ids: list[str] = []
        self.form_screens: list[dict[str, str]] = []
        self.html_attrs: dict[str, str] = {}
        self.scripts: dict[str, list[str]] = {}
        self.current_script_id: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_attrs = d
        if d.get("id"):
            self.element_ids.append(d["id"])
        if tag == "nav" and "localnav" in d.get("class", "").split():
            self.in_localnav = True
        if tag == "a" and self.in_localnav and d.get("href", "").startswith("#"):
            self.nav_hrefs.append(d["href"])
        if tag == "section":
            self.sections.append(d)
        if d.get("data-screen"):
            self.form_screens.append(d)
        if tag == "script" and d.get("id"):
            self.current_script_id = d["id"]
            self.scripts.setdefault(self.current_script_id, [])

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_localnav:
            self.in_localnav = False
        if tag == "script":
            self.current_script_id = None

    def handle_data(self, data: str) -> None:
        if self.current_script_id:
            self.scripts[self.current_script_id].append(data)


def block(message: str) -> None:
    raise SystemExit(f"BLOCK: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - CI diagnostic
        block(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        raise


def main() -> None:
    for path in (PAGE, CONTRACT, LIVE_XML, REPO_XML, PLACEMENT):
        if not path.exists():
            block(f"missing required artifact: {path.relative_to(ROOT)}")

    contract = load_json(CONTRACT)
    placement = load_json(PLACEMENT)
    html = PAGE.read_text(encoding="utf-8")
    parser = ContractParser()
    parser.feed(html)

    # Structured XML snapshots must remain parseable.
    try:
        live_root = ET.parse(LIVE_XML).getroot()
        repo_root = ET.parse(REPO_XML).getroot()
    except ET.ParseError as exc:
        block(f"XML snapshot parse failure: {exc}")

    expected = contract["sections"]
    expected_ids = [s["id"] for s in expected]
    actual_ids = [s.get("id", "") for s in parser.sections]

    if contract.get("fail_closed") is not True:
        block("contract must remain fail_closed=true")
    if contract.get("section_delta_allowed") != 0:
        block("section_delta_allowed must remain 0")
    if contract.get("reorder_allowed") is not False:
        block("reorder_allowed must remain false")
    if len(parser.sections) != contract["section_count"]:
        block(f"section count {len(parser.sections)} != {contract['section_count']}")
    if actual_ids != expected_ids:
        block(f"section order mismatch: {actual_ids} != {expected_ids}")

    for actual, spec in zip(parser.sections, expected, strict=True):
        if actual.get("data-section-kind") != spec["kind"]:
            block(f"{spec['id']}: data-section-kind mismatch")
        if actual.get("data-semantic-role") != spec["semantic_role"]:
            block(f"{spec['id']}: data-semantic-role mismatch")

    expected_nav = [f"#{s['id']}" for s in expected if s["id"] != "hero"]
    if parser.nav_hrefs != expected_nav:
        block(f"local navigation mismatch: {parser.nav_hrefs} != {expected_nav}")

    # Cross-family aliases are semantic mappings only; live ids must remain unchanged.
    aliases = [s["canonical_alias"] for s in expected]
    if len(set(aliases)) != len(aliases):
        block("canonical aliases must be unique")
    if contract["cross_family_contract"]["programme_reference"] != "/programme/ai-production-assurance/":
        block("programme reference drift")

    # Buyer role: preserve current live/NeoFort role-first avatar and do not regress to stale metadata.
    if "Claire Dumas" not in html or "CTO / Head of AI Platform" not in html:
        block("live buyer role/avatar missing")
    if "Claire Martin" in html:
        block("stale repository avatar Claire Martin must not appear in live candidate")
    if contract["buyer_contract"]["avatar_mode"] != "ROLE_FIRST_PARTIAL_EVIDENCE":
        block("buyer contract must remain role-first and evidence-bounded")

    # The post-engagement qualifier is part of the live page but NOT an extra offer section.
    form_contract = contract["post_engagement_form_contract"]
    if len(parser.form_screens) != form_contract["screen_count"]:
        block(f"qualification screen count {len(parser.form_screens)} != {form_contract['screen_count']}")
    actual_screen_numbers = [int(s["data-screen"]) for s in parser.form_screens]
    if actual_screen_numbers != list(range(1, form_contract["screen_count"] + 1)):
        block(f"qualification screen order mismatch: {actual_screen_numbers}")
    actual_topics = [s.get("data-topic") for s in parser.form_screens]
    if actual_topics != form_contract["screen_topics"]:
        block(f"qualification form topic drift: {actual_topics} != {form_contract['screen_topics']}")

    # Required navigation / conversion routes from the live page.
    for target in ("https://mickael-umt.com/qualification/", "https://mickael-umt.com/outils/"):
        if f'href="{target}"' not in html:
            block(f"required CTA target missing: {target}")

    # Evidence: upstream EU admission is not sufficient for placement. Claim anchors must be unique.
    if placement.get("resolved_judge") != contract["policy_resolution"]["resolved_current_judge"]:
        block("placement judge resolution mismatch")
    if placement.get("publication_status") != "BLOCKED_PENDING_FORMAL_PLACEMENT_JUDGE":
        block("placement manifest must remain fail-closed before formal 3-replica judge")
    for candidate in placement["candidates"]:
        cid = candidate["claim_element_id"]
        if parser.element_ids.count(cid) != 1:
            block(f"placement claim anchor {cid} occurs {parser.element_ids.count(cid)} times")
        eu_id = candidate["eu_id"]
        if html.count(f'data-eu-id="{eu_id}"') != 1:
            block(f"EvidenceUnit {eu_id} must bind to exactly one claim")
        if candidate["placement_status"] != "PENDING_FORMAL_3_REPLICA":
            block(f"{eu_id}: placement cannot be promoted without formal judge output")
        upstream = candidate["upstream"]
        required_upstream = {
            "deterministic_preflight": "PASS",
            "factfulness": "PASS",
            "admission": "ADMITTED",
            "agent_exploitability": "ALLOWED",
            "all_applicable_llm_judges": "PASS",
        }
        for key, value in required_upstream.items():
            if upstream.get(key) != value:
                block(f"{eu_id}: upstream gate {key}={upstream.get(key)!r}, expected {value!r}")

    # Embedded contract must agree with the external contract.
    script = "".join(parser.scripts.get("devicev-evidence-contract", []))
    if not script.strip():
        block("missing embedded DEVICEV contract")
    embedded = json.loads(script)
    if embedded.get("section_count") != contract["section_count"]:
        block("embedded section_count drift")
    if embedded.get("order") != expected_ids:
        block("embedded section order drift")
    if embedded.get("section_delta_allowed") != 0 or embedded.get("reorder_allowed") is not False:
        block("embedded structure lock weakened")
    if embedded.get("post_engagement_form", {}).get("screen_count") != form_contract["screen_count"]:
        block("embedded form screen count drift")
    if embedded.get("placement", {}).get("status") != "PENDING_FORMAL_3_REPLICA":
        block("embedded placement status must remain pending until formal judge results exist")

    # Root metadata and XML contract consistency.
    if parser.html_attrs.get("data-publication-status") != "BLOCKED_PENDING_FORMAL_PLACEMENT_JUDGE":
        block("HTML publication status must remain blocked")
    if parser.html_attrs.get("data-placement-judge") != contract["policy_resolution"]["resolved_current_judge"]:
        block("HTML placement judge drift")
    if live_root.attrib.get("source") != contract["source_of_truth"]:
        block("live XML source-of-truth drift")
    if live_root.find("./sectionContract").attrib.get("sectionCount") != str(contract["section_count"]):
        block("live XML section count drift")
    if repo_root.attrib.get("blobSha") != contract["existing_repository_blob_sha"]:
        block("repository XML blob lineage drift")

    print(
        "PASS: Agentic AI live structure locked — 18/18 sections, canonical semantic aliases, "
        "8-screen post-engagement qualifier, role-first avatar and exact EU claim anchors preserved."
    )
    print(
        "BLOCKED_FOR_PUBLICATION: formal evidence-placement/presentation judge v1.2 still requires "
        "3 deterministic replicas on the immutable page snapshot; structure PASS does not override this gate."
    )


if __name__ == "__main__":
    main()
