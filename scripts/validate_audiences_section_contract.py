#!/usr/bin/env python3
from pathlib import Path
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
LIVE = BASE / "pages/engagement/audiences/structure/live-page.xml"
REPO = BASE / "pages/engagement/audiences/structure/repo-html.xml"
AUDIT = BASE / "reports/audiences-section-contract-audit-2026-09-04.xml"
HTML = BASE / "pages/engagement/audiences/mickael-umt.com.html"

CANON = [0, 11, 20, 13, 14, 1, 2, 10, 15, 3, 12, 19, 4, 16, 17, 18, 5, 21, 6, 22, 23, 7, 8]
PROGRAMME_HUB = [0, 11, 20, 13, 14, 10, 7, 8]
TARGET_SURFACES = ["decision-profiles", "audience-cards", "problem-before-profile", "decision-roles", "qualifier", "footer"]
AVATARS = [
    "Claire Dumas", "Marc Lefèvre", "Nadia Benali", "Dr. Antoine Moreau", "Sophie Lemercier",
    "Karim Benali", "Isabelle Fontaine", "Julien Rocher", "Élodie Marchand", "Camille Ferrand",
]
CURRENT_COPY_LOOP = "loop:copy-claim:external-capability-v1.1"
CURRENT_COPY_JUDGE = "judge:copy-claim:external-capability-grounding-v1.1"
CURRENT_PLACEMENT_JUDGE = "judge:evidence-placement:presentation-v1.2"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ints(csv: str):
    return [int(x) for x in csv.split(",") if x.strip()]


def gate_map(root):
    return {g.attrib["name"]: g.attrib["status"] for g in root.findall("./gates/gate")}


for p in (LIVE, REPO, AUDIT, HTML):
    if not p.exists():
        fail(f"missing artifact: {p.relative_to(BASE)}")

live = ET.parse(LIVE).getroot()
repo = ET.parse(REPO).getroot()
audit = ET.parse(AUDIT).getroot()
html = HTML.read_text(encoding="utf-8")

# Scope and authority checks.
if live.attrib.get("scope") != "ONLY /engagement/audiences/":
    fail("live snapshot scope drift")
if repo.attrib.get("scope") != "ONLY /engagement/audiences/":
    fail("repo snapshot scope drift")
if audit.attrib.get("scope") != "ONLY /engagement/audiences/":
    fail("audit scope drift")
if audit.attrib.get("execution_posture") != "FAIL_CLOSED":
    fail("DEVICEV fail-closed posture drift")

# v4 reference contracts are checked without authorizing cross-page mutation.
v4 = audit.find("./v4_contract")
if v4 is None:
    fail("v4_contract missing")
if ints(v4.findtext("canonical_full_order")) != CANON:
    fail("canonical v4 order drift")
if ints(v4.findtext("programme_hub_reference_subset")) != PROGRAMME_HUB:
    fail("programme hub reference subset drift")
refs = audit.findall("./reference_contract_checks/page")
if [x.attrib.get("url") for x in refs] != ["https://mickael-umt.com/expertises/", "https://mickael-umt.com/programme/"]:
    fail("reference pages drift")
for x in refs:
    if x.findtext("mutation_decision") != "OBSERVE_ONLY":
        fail(f"cross-page mutation is not observe-only: {x.attrib.get('url')}")

# Live target topology is immutable for this audit.
contract = live.find("./page_contract")
if contract is None:
    fail("live page_contract missing")
if int(contract.attrib.get("avatar_count", "0")) != 10:
    fail("live avatar count != 10")
if int(contract.attrib.get("decision_role_count", "0")) != 3:
    fail("live decision-role count != 3")
if int(contract.attrib.get("qualification_screen_count", "0")) != 8:
    fail("live qualification screen count != 8")
sections = live.findall("./sections/section")
if [x.attrib.get("id") for x in sections] != TARGET_SURFACES:
    fail("live target surface order drift")

live_avatars = live.findall("./sections/section[@id='audience-cards']/avatar")
if len(live_avatars) != 10:
    fail("live avatar objects != 10")
if [x.attrib.get("name") for x in live_avatars] != AVATARS:
    fail("live avatar identity/order drift")

live_roles = live.findall("./sections/section[@id='decision-roles']/role")
if [x.attrib.get("id") for x in live_roles] != ["DECISION_MAKER", "ADVOCATE", "CHAMPION"]:
    fail("decision-role triad drift")

live_screens = live.findall("./sections/section[@id='qualifier']/screen")
if len(live_screens) != 8:
    fail("live qualifier screen objects != 8")
if live_screens[1].attrib.get("semantic") != "timing_and_decision_role":
    fail("live screen 2 must group timing + decision role")
if live_screens[5].attrib.get("semantic") != "scope_maturity":
    fail("live screen 6 scope maturity drift")
if live_screens[6].attrib.get("semantic") != "inspection_or_validation_trigger":
    fail("live screen 7 trigger drift")

# Repository target HTML: cardinality/top-level order pass, but known lossless-fidelity defects must remain explicit.
if '<html lang="fr" data-theme="dark"' not in html:
    fail("repository review HTML must remain French dark mode")
if 'data-publication-status="PENDING_FORMAL_LLM_JUDGE"' not in html:
    fail("repository review HTML must not self-authorize publication")
for i, name in enumerate(AVATARS, start=1):
    avatar_id = f'avatar-{i:02d}'
    if html.count(f'id="{avatar_id}"') != 1:
        fail(f"{avatar_id} must resolve exactly once")
    if name not in html:
        fail(f"avatar name missing from HTML: {name}")
if len(re.findall(r'<fieldset\b', html, flags=re.I)) != 8:
    fail("repository HTML fieldset count != 8")
if len(re.findall(r'<figure class="eug"', html)) != 4:
    fail("audit expected exactly four review-only inline EUG figures")
if "https://mickael-umt.com/programmes/" not in html:
    fail("audit expected plural programme route drift, but it is absent")
if CURRENT_COPY_LOOP in html or CURRENT_COPY_JUDGE in html:
    fail("audit expected stale v1.2 repo copy-contract metadata; current v1.1 metadata is unexpectedly present")
if "loop:copy-claim:external-capability-v1.2-topology-preserving" not in html:
    fail("expected repo v1.2 loop metadata missing")

repo_form = repo.find("./qualification_form")
if repo_form is None or repo_form.attrib.get("screen_count") != "8":
    fail("repo qualification_form snapshot invalid")
if repo_form.attrib.get("semantic_fidelity") != "FAIL":
    fail("repo qualifier semantic drift must remain fail-closed")
if repo.findtext("./avatar_grid/visible_eug_total") != "4":
    fail("repo avatar-grid EUG count snapshot drift")
if repo.find("./navigation_fidelity").attrib.get("status") != "FAIL":
    fail("repo navigation drift must remain explicit")

# NeoFort current=true policy resolution must be exact.
policies = {p.attrib["role"]: p.attrib["id"] for p in audit.findall("./neofort_current_policy_resolution/policy")}
if policies.get("copy_claim_loop") != CURRENT_COPY_LOOP:
    fail("current NeoFort copy loop mismatch")
if policies.get("copy_claim_judge") != CURRENT_COPY_JUDGE:
    fail("current NeoFort copy judge mismatch")
if policies.get("placement_judge") != CURRENT_PLACEMENT_JUDGE:
    fail("current NeoFort placement judge mismatch")
note = audit.findtext("./neofort_current_policy_resolution/resolution_note") or ""
if "judge:eu:placementv1" not in note or CURRENT_PLACEMENT_JUDGE not in note:
    fail("requested-vs-current placement judge resolution is not recorded")

# Evidence status is not allowed to be promoted by structural CI.
placements = audit.findall("./evidence_and_copy_state/target_placement_examples/evidence")
if not placements:
    fail("target placement examples missing")
for e in placements:
    if e.attrib.get("target_placement_status") != "PENDING_TARGET_PAGE_PRESENTATION_JUDGE":
        fail(f"premature target placement authorization: {e.attrib.get('id')}")
    if e.attrib.get("xpath_match_count") != "1":
        fail(f"xpath match count drift: {e.attrib.get('id')}")
for e in audit.findall("./evidence_and_copy_state/graph_evidence_examples/evidence"):
    if not e.attrib.get("id"):
        fail("graph evidence id missing")

# Gate truth table: CI validates the audit, not publication.
gates = gate_map(audit)
expected = {
    "live_target_topology": "PASS",
    "live_customer_avatar_contract": "PASS",
    "live_raw_html_materialization": "BLOCKED",
    "expertises_v4_full_journey": "FAIL_PARTIAL_HUB",
    "programme_v4_reference_subset": "FAIL_PARTIAL_HUB",
    "expertises_repo_hub_html": "MISSING",
    "programme_repo_hub_html": "MISSING",
    "repo_target_top_level_topology": "PASS",
    "repo_avatar_card_form_fidelity": "FAIL",
    "repo_qualification_screen_count": "PASS",
    "repo_qualification_semantic_fidelity": "FAIL",
    "repo_navigation_fidelity": "FAIL",
    "repo_current_copy_policy_alignment": "FAIL_STALE_REPO_METADATA",
    "target_evidence_admission": "BLOCKED_MIXED",
    "target_placement_three_replica_judge": "BLOCKED",
    "xpath_unique_binding": "PARTIAL_PASS",
    "publication": "BLOCKED",
}
for name, status in expected.items():
    if gates.get(name) != status:
        fail(f"gate {name} expected {status}, got {gates.get(name)}")

# C/U/D protections and final fail-closed publication state.
gdrive = audit.find("./google_drive_execution")
if gdrive is None or gdrive.attrib.get("read_only") != "true" or gdrive.attrib.get("write_performed") != "false":
    fail("Google Drive must remain read-only until explicit approval")
if audit.attrib.get("publication_allowed") != "false" or audit.attrib.get("html_mutation_allowed") != "false":
    fail("publication/html mutation must remain blocked in this run")
mutation = audit.find("./mutation_decision")
if mutation is None or mutation.findtext("decision") != "DO_NOT_MUTATE_HTML_IN_THIS_RUN":
    fail("target HTML mutation decision drift")
final = audit.find("./final_decision")
if final is None or final.attrib.get("final_pass") != "false" or final.attrib.get("status") != "BLOCKED":
    fail("final DEVICEV decision must remain BLOCKED")

print("PASS: audiences section-contract audit artifacts are internally consistent.")
print("PASS: live target topology = hero + 10 avatars + problem fallback + 3 decision roles + 8-screen qualifier + footer.")
print("PASS: /expertises/ and /programme/ reference contracts were checked read-only and no cross-page mutation is authorized.")
print("EXPECTED BLOCK: repo avatar-card form differs from live because four inline EUG panels are injected.")
print("EXPECTED BLOCK: repo qualifier has 8 screens but does not preserve live screen semantics.")
print("EXPECTED BLOCK: repo copy metadata is stale versus NeoFort current=true v1.1.")
print("EXPECTED BLOCK: target EvidencePlacement v1.2 3-replica verdicts are pending.")
print("PASS: Google Drive write_performed=false.")
print("PUBLICATION: BLOCKED (correct DEVICEV fail-closed state).")
