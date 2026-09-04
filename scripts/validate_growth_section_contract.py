#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET

CANON = [0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8]
GROWTH = [0,10,5,7,8]
PROGRAMME_HUB = [0,11,20,13,14,10,7,8]
CURRENT_COPY_LOOP = "loop:copy-claim:external-capability-v1.1"
CURRENT_COPY_JUDGE = "judge:copy-claim:external-capability-grounding-v1.1"
CURRENT_PLACEMENT_JUDGE = "judge:evidence-placement:presentation-v1.2"

BASE = Path(__file__).resolve().parents[1]
LIVE = BASE / "expertises/growth/structure/live-page.xml"
REPO = BASE / "expertises/growth/structure/repo-html.xml"
AUDIT = BASE / "reports/growth-contract-audit-2026-09-04.xml"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ints(csv: str):
    return [int(x) for x in csv.split(",") if x.strip()]


def is_subsequence(sub, seq):
    it = iter(seq)
    return all(any(x == y for y in it) for x in sub)


def gate_map(root):
    return {g.attrib["name"]: g.attrib["status"] for g in root.findall("./growth_gates/gate")}

for p in (LIVE, REPO, AUDIT):
    if not p.exists():
        fail(f"missing artifact: {p.relative_to(BASE)}")

live = ET.parse(LIVE).getroot()
repo = ET.parse(REPO).getroot()
audit = ET.parse(AUDIT).getroot()

if live.attrib.get("scope") != "ONLY /expertises/growth/":
    fail("live snapshot scope drift")
if repo.attrib.get("scope") != "ONLY /expertises/growth/":
    fail("repo snapshot scope drift")
if audit.attrib.get("scope") != "ONLY /expertises/growth/":
    fail("audit scope drift")

canon = ints(live.find("./section_contract").attrib["canonical_full_order"])
subset = ints(live.find("./section_contract").attrib["selected_justified_subset"])
if canon != CANON:
    fail(f"canonical order drift: {canon}")
if subset != GROWTH or not is_subsequence(subset, canon):
    fail(f"Growth subset is not canonical-order preserving: {subset}")

live_tokens = [int(x.attrib["token"]) for x in live.findall("./sections/section")]
repo_tokens = [int(x.attrib["token"]) for x in repo.findall("./sections/section")]
if live_tokens != GROWTH:
    fail(f"live token sequence drift: {live_tokens}")
if repo_tokens != GROWTH:
    fail(f"repo token sequence drift: {repo_tokens}")

live_offers = live.find("./sections/section[@semantic='offers']")
live_caps = live.find("./sections/section[@semantic='capabilities']")
live_form = live.find("./sections/section[@semantic='lead_form']/qualification_form")
repo_form = repo.find("./qualification_form")
if live_offers is None or live_offers.attrib.get("cardinality") != "2":
    fail("live offer cardinality != 2")
if live_caps is None or live_caps.attrib.get("cardinality") != "3":
    fail("live capability cardinality != 3")
if live_form is None or live_form.attrib.get("screen_count") != "8":
    fail("live qualification screen count != 8")
if repo_form is None or repo_form.attrib.get("screen_count") != "8":
    fail("repo qualification screen count != 8")
if len(live_form.findall("./screen")) != 8 or len(repo_form.findall("./screen")) != 8:
    fail("qualification screen objects != 8")

v4 = audit.find("./v4_contract")
if ints(v4.findtext("canonical_full_order")) != CANON:
    fail("audit canonical order drift")
if ints(v4.findtext("growth_justified_subset")) != GROWTH:
    fail("audit Growth subset drift")
if ints(v4.findtext("programme_hub_reference_subset")) != PROGRAMME_HUB:
    fail("programme-hub reference contract drift")
if ints(v4.findtext("programme_detail_reference_order")) != CANON:
    fail("programme-detail reference contract drift")

policies = {p.attrib["role"]: p.attrib["id"] for p in audit.findall("./neofort_current_policy_resolution/policy")}
if policies.get("copy_claim_loop") != CURRENT_COPY_LOOP:
    fail("current NeoFort copy loop mismatch")
if policies.get("copy_claim_judge") != CURRENT_COPY_JUDGE:
    fail("current NeoFort copy judge mismatch")
if policies.get("placement_judge") != CURRENT_PLACEMENT_JUDGE:
    fail("current NeoFort placement judge mismatch")

repo_loop = repo.findtext("./embedded_contract_metadata/claim_loop")
repo_judge = repo.findtext("./embedded_contract_metadata/claim_judge")
if repo_loop == CURRENT_COPY_LOOP or repo_judge == CURRENT_COPY_JUDGE:
    fail("audit expected a stale repo copy-contract mismatch but none is present")

gates = gate_map(audit)
expected = {
    "live_topology_cardinality": "PASS",
    "repo_topology_cardinality": "PASS",
    "canonical_relative_order": "PASS",
    "live_structure_preservation": "PASS",
    "qualification_screen_count": "PASS",
    "qualification_semantic_fidelity": "FAIL",
    "qualification_control_fidelity": "FAIL",
    "neofort_current_copy_contract": "FAIL",
    "neofort_page_section_graph": "BLOCKED",
    "neofort_evidence_unit_graph": "BLOCKED",
    "xpath_unique_claim_binding": "BLOCKED",
    "formal_three_replica_judges": "BLOCKED",
    "publication": "BLOCKED",
}
for name, status in expected.items():
    if gates.get(name) != status:
        fail(f"gate {name} expected {status}, got {gates.get(name)}")

if audit.attrib.get("publication_allowed") != "false":
    fail("publication must remain blocked until all mandatory DEVICEV gates pass")
final = audit.find("./final_decision")
if final is None or final.attrib.get("final_pass") != "false" or final.attrib.get("status") != "BLOCKED":
    fail("final decision must remain BLOCKED")

ce = audit.find("./candidate_evidence")
source_count = int(ce.attrib["declared_source_count"])
section_count = int(ce.attrib["claim_bearing_anchor_sections"])
ratio = source_count / section_count
if not ratio > 0.72:
    fail(f"source/section density gate failed: {ratio}")
for candidate in ce.findall("./candidate"):
    if candidate.findtext("placement_status") != "NOT_AUTHORIZED":
        fail(f"candidate {candidate.attrib['id']} is prematurely placement-authorized")
    if candidate.findtext("source_hash") != "MISSING_NOT_MATERIALIZED":
        fail(f"candidate {candidate.attrib['id']} unexpectedly claims a materialized source hash")

print("PASS: Growth audit integrity is valid.")
print(f"PASS: canonical Growth subset {GROWTH} preserves v4 relative order.")
print("PASS: live/repo topological cardinality = hero + 2 offers + 3 capabilities + CTA + 8 screens.")
print("EXPECTED BLOCK: qualification semantic/control fidelity is unresolved.")
print("EXPECTED BLOCK: repo copy-claim contract is stale versus NeoFort current=true v1.1.")
print("EXPECTED BLOCK: EU/placement/XPath/3-replica publication gates are not materialized.")
print(f"PASS: supplemental source-density check = {source_count}/{section_count} = {ratio:.3f} > 0.72.")
print("PUBLICATION: BLOCKED (correct fail-closed state).")
