from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "pages/parcours/parcours.html"
LIVE = ROOT / "pages/parcours/structure/live-page.xml"
REPO = ROOT / "pages/parcours/structure/repo-html.xml"
AUDIT = ROOT / "pages/parcours/parcours.contract-audit.xml"
FAMILY = ROOT / "pages/parcours/structure/family-contract-audit.xml"
EVIDENCE = ROOT / "pages/parcours/structure/copy-evidence.xml"

EXPECTED = [
    "hero", "intersection-profile", "domains", "capability-summary",
    "capability-ranking", "experience", "research-development",
    "advanced-programmes", "certificates", "engagement", "qualification-form",
]

def fail(msg):
    raise SystemExit("PARCOURS_SECTION_CONTRACT_FAIL: " + msg)

for path in [LIVE, REPO, AUDIT, FAMILY, EVIDENCE]:
    try:
        ET.parse(path)
    except Exception as exc:
        fail(f"{path}: invalid XML: {exc}")

live = ET.parse(LIVE).getroot()
repo = ET.parse(REPO).getroot()
audit = ET.parse(AUDIT).getroot()
family = ET.parse(FAMILY).getroot()
evidence = ET.parse(EVIDENCE).getroot()

if live.attrib.get("scope") != "ONLY /parcours/": fail("live scope drift")
if audit.attrib.get("scope") != "ONLY /parcours/": fail("audit scope drift")
if live.attrib.get("section_count") != "11": fail("live section count drift")
if repo.attrib.get("section_count") != "11": fail("repo section count drift")

live_ids = [x.attrib["section_id"] for x in live.findall("./sections/section")]
repo_ids = [x.attrib["section_id"] for x in repo.findall("./topology/section")]
if live_ids != EXPECTED: fail(f"live order drift: {live_ids}")
if repo_ids != EXPECTED: fail(f"repo order drift: {repo_ids}")

text = HTML.read_text(encoding="utf-8")
html_ids = re.findall(r'<section\b[^>]*data-section-id="([^"]+)"', text)
if html_ids != EXPECTED: fail(f"html section order drift: {html_ids}")

screens = [int(x) for x in re.findall(r'<fieldset\b[^>]*data-screen="(\d+)"', text)]
if screens != list(range(1, 9)): fail(f"qualification form drift: {screens}")

claim_ids = re.findall(r'\bid="(claim-[^"]+)"', text)
if len(claim_ids) != len(set(claim_ids)): fail("duplicate claim ids")
if 'data-publication-allowed="false"' not in text: fail("candidate must remain non-production under fail-closed")

scope_guard = family.find("./scope_guard")
if scope_guard is None or scope_guard.findtext("google_drive_mutation") != "false": fail("Google Drive mutation guard missing")
if evidence.attrib.get("publication_allowed") != "false": fail("DEVICEV fail-closed publication flag drift")

print("PARCOURS_SECTION_CONTRACT_PASS")
print("sections=11 qualification_screens=8 scope=/parcours/ publication_allowed=false")
