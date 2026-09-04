from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "pages" / "ressources" / "produits" / "frameworks"
HTML = BASE / "diagnostic-framework.html"
LIVE = BASE / "diagnostic-framework.live.xml"
REPO = BASE / "diagnostic-framework.repo-html.xml"
AUDIT = BASE / "diagnostic-framework.contract-audit.xml"
TARGET = "https://mickael-umt.com/ressources/produits/frameworks/diagnostic-framework/"
CANON = [0, 11, 20, 13, 14, 1, 2, 10, 15, 3, 12, 19, 4, 16, 17, 18, 5, 21, 6, 22, 23, 7, 8]
EXPECTED_BLOCKERS = {
    "LIVE_RAW_HTML_NOT_MATERIALIZED",
    "EXACT_LIVE_SECTION_COUNT_UNKNOWN",
    "TARGET_WEBPAGE_NOT_REGISTERED_CURRENT_IN_NEOFORT",
    "NO_CURRENT_TARGET_EVIDENCE_PLACEMENT",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def csv_ints(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(x.strip()) for x in value.split(",") if x.strip()]


class ContractHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.main_depth = 0
        self.section_depth_in_main = 0
        self.top_level_main_sections = 0
        self.inputs: dict[str, dict[str, str | bool]] = {}
        self.review_form_seen = False

    @staticmethod
    def attrs_dict(attrs):
        return {k: (v if v is not None else True) for k, v in attrs}

    def handle_starttag(self, tag: str, attrs) -> None:
        a = self.attrs_dict(attrs)
        if tag == "main":
            self.main_depth += 1
            return
        if self.main_depth:
            if tag == "section":
                if self.section_depth_in_main == 0:
                    self.top_level_main_sections += 1
                self.section_depth_in_main += 1
            elif tag == "form" and a.get("data-review-only") == "true":
                self.review_form_seen = True
            elif tag == "input" and a.get("name"):
                self.inputs[str(a["name"])] = {
                    "type": str(a.get("type", "text")),
                    "required": "required" in a,
                }

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.main_depth and self.section_depth_in_main:
            self.section_depth_in_main -= 1
        elif tag == "main" and self.main_depth:
            self.main_depth -= 1


def parse_xml(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except Exception as exc:
        fail(f"cannot parse {path.relative_to(ROOT)}: {exc}")


def required_text(root: ET.Element, xpath: str) -> str:
    node = root.find(xpath)
    if node is None or not (node.text or "").strip():
        fail(f"missing text at {xpath}")
    return (node.text or "").strip()


def main() -> int:
    for path in (HTML, LIVE, REPO, AUDIT):
        if not path.exists():
            fail(f"missing required artifact: {path.relative_to(ROOT)}")

    html = HTML.read_text(encoding="utf-8")
    live = parse_xml(LIVE)
    repo = parse_xml(REPO)
    audit = parse_xml(AUDIT)

    # Scope and authority are immutable for this audit.
    if live.attrib.get("source_url") != TARGET:
        fail("live XML target URL drift")
    if repo.attrib.get("target_url") != TARGET:
        fail("repo HTML XML target URL drift")
    if audit.attrib.get("targetPage") != TARGET:
        fail("audit target URL drift")
    if required_text(audit, "./scope/pageOnly") != "/ressources/produits/frameworks/diagnostic-framework/":
        fail("audit scope drift")
    if required_text(audit, "./scope/otherPageCUD") != "FORBIDDEN":
        fail("other-page CUD must remain forbidden")
    if required_text(audit, "./scope/googleDriveCUD") != "NOT_PERFORMED_REQUIRES_EXPLICIT_USER_APPROVAL":
        fail("Google Drive write policy drift")

    # The S/P v4 canon is checked as a reference contract, not forced onto a product page.
    if csv_ints(required_text(audit, "./section_contract_review/expertises/canonicalFullOrder")) != CANON:
        fail("expertises canonical order drift")
    if csv_ints(required_text(audit, "./section_contract_review/programmes/canonicalFullOrder")) != CANON:
        fail("programme canonical order drift")
    if required_text(audit, "./section_contract_review/expertises/targetApplicability") != "REFERENCE_ONLY":
        fail("expertises contract must be reference-only for target")
    if required_text(audit, "./section_contract_review/programmes/targetApplicability") != "REFERENCE_ONLY":
        fail("programme contract must be reference-only for target")
    if required_text(audit, "./section_contract_review/target/forcedCanonical23Sections") != "false":
        fail("target must not be forced into 23-section monolith")

    # Fail-closed means missing live DOM parity is represented as a blocker, never silently repaired.
    if live.attrib.get("raw_html_materialized") != "false":
        fail("live raw HTML state must remain explicitly false until materialized")
    if live.attrib.get("exact_live_section_count_known") != "false":
        fail("exact live section count must remain unknown until materialized")
    if live.attrib.get("publication_allowed") != "false":
        fail("live snapshot cannot authorize publication")
    if audit.attrib.get("executionPosture") != "FAIL_CLOSED":
        fail("execution posture drift")
    if audit.attrib.get("copyReviewDecision") != "PASS":
        fail("bounded copy review should pass")
    if audit.attrib.get("publicationDecision") != "BLOCKED" or audit.attrib.get("publicationAllowed") != "false":
        fail("publication must remain blocked")
    blockers = {n.text.strip() for n in audit.findall("./publication_gate/blockers/blocker") if n.text}
    if blockers != EXPECTED_BLOCKERS:
        fail(f"publication blocker set drift: {sorted(blockers)}")

    # Resolve the user's legacy placement label to the current NeoFort judge snapshot recorded by the audit.
    judge = audit.find("./policy_resolution/judge")
    if judge is None:
        fail("placement judge resolution missing")
    if judge.attrib.get("resolvedCurrent") != "judge:evidence-placement:presentation-v1.2":
        fail("current placement judge drift")
    if (judge.attrib.get("temperature"), judge.attrib.get("topP"), judge.attrib.get("replicas")) != ("0", "1", "3"):
        fail("judge determinism contract drift")

    # Parse review HTML structure and form semantics without external dependencies.
    parser = ContractHTMLParser()
    parser.feed(html)
    repo_count = int(required_text(repo, "./topology/top_level_main_section_count"))
    if parser.top_level_main_sections != repo_count:
        fail(f"repo HTML top-level section count mismatch: html={parser.top_level_main_sections}, xml={repo_count}")
    if repo_count != 1:
        fail("review artifact intentionally uses one top-level product section")
    if not parser.review_form_seen:
        fail("review-only checkout form missing")
    expected_inputs = {
        "email": ("email", True),
        "name": ("text", False),
        "organisation": ("text", False),
        "accept_terms": ("checkbox", True),
    }
    for name, (typ, required) in expected_inputs.items():
        got = parser.inputs.get(name)
        if not got:
            fail(f"checkout field missing: {name}")
        if got["type"] != typ or got["required"] is not required:
            fail(f"checkout field contract drift: {name} -> {got}")

    # Copy/product truth gates.
    required_fragments = [
        "49 € HT",
        "Achat unique",
        "Accès permanent",
        "Maturité",
        "Impact",
        "Périmètre",
        "Proposition",
        "heuristique interne",
        "Le framework ne certifie pas une conformité ISO, NIST ou réglementaire.",
        "Il ne garantit ni ROI, ni réduction du risque projet, ni gain de temps, ni résultat de production.",
    ]
    for fragment in required_fragments:
        if fragment not in html:
            fail(f"required bounded copy fragment missing: {fragment}")

    forbidden_affirmative_fragments = [
        "49 € réduit le risque",
        "49€ réduit le risque",
        "économise une demi-journée",
        "évite l’approbation achat",
        "score validé",
        "conforme NIST",
        "certifié NIST",
        "ROI garanti",
        "conversion garantie",
    ]
    lowered = html.lower()
    for fragment in forbidden_affirmative_fragments:
        if fragment.lower() in lowered:
            fail(f"unsupported affirmative claim present: {fragment}")
    if "Télécharger le framework PDF" in html:
        fail("pre-purchase generated-PDF self-loop CTA must not appear in review artifact")

    # No external placement is published while target NeoFort page/selector objects are absent.
    if required_text(repo, "./evidence_binding/public_external_placement_count") != "0":
        fail("public external placement count must stay zero")
    candidate = repo.find("./evidence_binding/candidate_external_eu")
    if candidate is None or candidate.attrib.get("status") != "NOT_PLACED_TARGET_PAGE_BINDING_MISMATCH":
        fail("external EU target-binding rejection missing")

    # DeviceV manifest must tell downstream agents the same blocked state.
    m = re.search(r'<script type="application/json" id="devicev-manifest">\s*(\{.*?\})\s*</script>', html, re.S)
    if not m:
        fail("devicev manifest missing")
    manifest = json.loads(m.group(1))
    if manifest.get("source_page") != TARGET or manifest.get("publication_allowed") is not False:
        fail("devicev manifest scope/publication drift")
    if set(manifest.get("blocking_reasons", [])) != EXPECTED_BLOCKERS:
        fail("devicev manifest blocker drift")
    if manifest.get("public_external_citations") != 0:
        fail("devicev manifest cannot authorize public citations")

    print("PASS: diagnostic-framework review contract is internally coherent and fail-closed.")
    print("PASS: /expertises and /programme v4 canonical orders are preserved as reference-only contracts.")
    print("PASS: review HTML form/product semantics match the extracted repo XML.")
    print("BLOCKED_FOR_PUBLICATION: exact live DOM/XPath and current target NeoFort placement are unavailable.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
