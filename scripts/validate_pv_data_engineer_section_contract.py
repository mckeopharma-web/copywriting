#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

CANON = [0, 11, 20, 13, 14, 1, 2, 10, 15, 3, 12, 19, 4, 16, 17, 18, 5, 21, 6, 22, 23, 7, 8]
REPO_TOKENS = [0, 11, 20, 13, 14, 1, 15, 12, 4, 16, 17, 22, 23, 7, 8]
REPO_SECTION_IDS = [
    "hero",
    "declencheurs",
    "consequences",
    "pourqui",
    "qualification",
    "proposition",
    "livrables",
    "avantapres",
    "preuves",
    "perimetre",
    "deroule",
    "engagements",
    "faq",
    "mission",
    "qualification-form",
]
PROGRAMME_HUB = [0, 11, 20, 13, 14, 10, 7, 8]
CURRENT_COPY_LOOP = "loop:copy-claim:external-capability-v1.1"
CURRENT_COPY_JUDGE = "judge:copy-claim:external-capability-grounding-v1.1"
CURRENT_PLACEMENT_JUDGE = "judge:evidence-placement:presentation-v1.2"

BASE = Path(__file__).resolve().parents[1]
LIVE = BASE / "expertises/pv-data-engineer/structure/live-page.xml"
REPO = BASE / "expertises/pv-data-engineer/structure/repo-html.xml"
AUDIT = BASE / "reports/pv-data-engineer-contract-audit-2026-09-04.xml"
HTML = BASE / "expertises/pv-data-engineer/pv-data-engineer.html"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ints(csv: str | None) -> list[int]:
    if not csv:
        return []
    return [int(x) for x in csv.split(",") if x.strip()]


def is_subsequence(sub: list[int], seq: list[int]) -> bool:
    it = iter(seq)
    return all(any(x == y for y in it) for x in sub)


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class SectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "section":
            return
        data = {k: v for k, v in attrs}
        anchor = data.get("id") or data.get("data-section-id")
        if anchor:
            self.sections.append(anchor)


def gate_map(root: ET.Element, parent: str) -> dict[str, str]:
    return {
        gate.attrib["name"]: gate.attrib["status"]
        for gate in root.findall(f"./{parent}/gate")
    }


for artifact in (LIVE, REPO, AUDIT, HTML):
    if not artifact.exists():
        fail(f"missing artifact: {artifact.relative_to(BASE)}")

live = ET.parse(LIVE).getroot()
repo = ET.parse(REPO).getroot()
audit = ET.parse(AUDIT).getroot()

# Scope isolation: this task is forbidden from broadening to other pages.
expected_scope = "ONLY /expertises/pv-data-engineer/"
for label, root in (("live", live), ("repo", repo), ("audit", audit)):
    if root.attrib.get("scope") != expected_scope:
        fail(f"{label} scope drift: {root.attrib.get('scope')}")

# v4 contract: live PV detail is currently the full 23-section S-series journey.
live_contract = live.find("./section_contract")
if live_contract is None:
    fail("live section_contract missing")
if ints(live_contract.attrib.get("canonical_full_order")) != CANON:
    fail("live canonical order drift")
if ints(live_contract.attrib.get("selected_live_order")) != CANON:
    fail("live selected order is no longer the full canonical order")
if live_contract.attrib.get("live_matches_full_canon") != "true":
    fail("live full-canon assertion changed")
live_tokens = [int(x.attrib["token"]) for x in live.findall("./sections/section")]
if live_tokens != CANON:
    fail(f"live token sequence drift: {live_tokens}")
if len(live_tokens) != 23:
    fail(f"live semantic section count != 23: {len(live_tokens)}")

# Programme contracts are reference-only but must remain coherent with the v4 owner contract.
v4 = audit.find("./v4_contract")
if v4 is None:
    fail("audit v4_contract missing")
if ints(v4.findtext("canonical_full_order")) != CANON:
    fail("audit canonical order drift")
if ints(v4.findtext("programme_hub_reference_subset")) != PROGRAMME_HUB:
    fail("programme-hub reference contract drift")
if ints(v4.findtext("programme_detail_reference_order")) != CANON:
    fail("programme-detail reference contract drift")

# Repository snapshot must describe the actual HTML currently committed.
repo_tokens = [int(x.attrib["token"]) for x in repo.findall("./sections/section")]
if repo_tokens != REPO_TOKENS:
    fail(f"repo XML token sequence drift: {repo_tokens}")
if not is_subsequence(repo_tokens, CANON):
    fail("repo token sequence does not preserve canonical relative order")
if repo_tokens == CANON:
    fail("audit expects repo/live topology mismatch, but repo snapshot now claims full canon; regenerate audit")

repo_section_ids = [x.attrib["data_section_id"] for x in repo.findall("./sections/section")]
if repo_section_ids != REPO_SECTION_IDS:
    fail(f"repo XML section-id sequence drift: {repo_section_ids}")

html_bytes = HTML.read_bytes()
actual_blob = git_blob_sha(html_bytes)
recorded_blob = repo.attrib.get("blob_sha")
if actual_blob != recorded_blob:
    fail(
        "repository HTML changed after repo-html.xml snapshot: "
        f"actual blob {actual_blob}, recorded {recorded_blob}; recapture before judging"
    )

parser = SectionParser()
parser.feed(html_bytes.decode("utf-8"))
if parser.sections != REPO_SECTION_IDS:
    fail(f"actual HTML section topology drift: {parser.sections}")

# Forms: same cardinality is necessary but not sufficient; semantics are deliberately blocked.
live_form = live.find("./sections/section[@semantic='lead_form']/qualification_form")
repo_form = repo.find("./qualification_form")
if live_form is None or live_form.attrib.get("screen_count") != "8":
    fail("live qualification screen count != 8")
if repo_form is None or repo_form.attrib.get("screen_count") != "8":
    fail("repo qualification screen count != 8")
if len(live_form.findall("./screen")) != 8 or len(repo_form.findall("./screen")) != 8:
    fail("qualification screen object count != 8")
if live_form.find("./screen[@index='7']/question").text != "Ce que l’inspection devra pouvoir suivre":
    fail("live inspection-trigger screen semantics drift")
if repo_form.find("./screen[@index='7']/question").text == "Ce que l’inspection devra pouvoir suivre":
    fail("audit expected repo form semantic mismatch but screen 7 now matches; regenerate audit")

# Current NeoFort authority. The historical/user-supplied label is not allowed to override current=true.
policies = {
    p.attrib["role"]: p.attrib["id"]
    for p in audit.findall("./neofort_current_policy_resolution/policy")
}
if policies.get("copy_claim_loop") != CURRENT_COPY_LOOP:
    fail("current NeoFort copy loop mismatch")
if policies.get("copy_claim_judge") != CURRENT_COPY_JUDGE:
    fail("current NeoFort copy judge mismatch")
if policies.get("placement_judge") != CURRENT_PLACEMENT_JUDGE:
    fail("current NeoFort placement judge mismatch")

repo_loop = repo.findtext("./embedded_contract_metadata/claim_loop")
repo_judge = repo.findtext("./embedded_contract_metadata/claim_judge")
if repo_loop == CURRENT_COPY_LOOP or repo_judge == CURRENT_COPY_JUDGE:
    fail("audit expected stale repo copy-contract metadata, but mismatch has been resolved; regenerate audit")

# Fail-closed status is part of the contract. Passing this script means the audit is internally coherent,
# not that the page is publishable.
structure = gate_map(audit, "structure_gates")
expected_structure = {
    "live_full_canonical_order": "PASS",
    "live_section_forms_preserved_in_xml": "PASS",
    "repo_dark_theme": "PASS",
    "repo_topology_relative_order": "PASS_WITH_MISSING_SURFACES",
    "repo_live_topology_equivalence": "FAIL",
    "qualification_screen_count": "PASS",
    "qualification_semantic_fidelity": "FAIL",
    "qualification_control_fidelity": "FAIL",
    "raw_live_html_materialization": "BLOCKED",
}
for name, status in expected_structure.items():
    if structure.get(name) != status:
        fail(f"structure gate {name} expected {status}, got {structure.get(name)}")

evidence = gate_map(audit, "evidence_gates")
expected_evidence = {
    "current_evidence_deterministic_preflight": "PASS_FOR_LISTED_EUS",
    "current_evidence_factfulness": "PASS_FOR_LISTED_EUS",
    "evidence_agent_exploitability": "PASS_AT_EU_LEVEL_ONLY",
    "current_evidence_unit_publication_admission": "BLOCKED_OR_PENDING",
    "source_section_density": "PASS_SUPPLEMENTAL_ONLY",
    "placement_current_judge_version": "FAIL_STALE",
    "xpath_unique_claim_binding": "BLOCKED_LIVE_REBIND_REQUIRED",
    "formal_three_replica_current_presentation_judge": "BLOCKED",
}
for name, status in expected_evidence.items():
    if evidence.get(name) != status:
        fail(f"evidence gate {name} expected {status}, got {evidence.get(name)}")

copy_avatar = gate_map(audit, "copy_and_avatar_gates")
if copy_avatar.get("neofort_current_copy_contract") != "FAIL_STALE_REPO_METADATA":
    fail("stale copy-contract gate must remain explicit")
if copy_avatar.get("avatar_contract") != "PASS_BOUNDED":
    fail("avatar contract must remain bounded")
if copy_avatar.get("public_faers_biolearn_repo_resolution") != "NOT_INDEPENDENTLY_RESOLVED":
    fail("public FAERS/Biolearn provenance status drift")

# Evidence may be usable by agents at EU level while still being barred from new placement/publication.
register = audit.find("./current_evidence_register")
if register is None:
    fail("current_evidence_register missing")
for eu in register.findall("./evidence_unit"):
    placement = eu.findtext("placement_status") or ""
    if not placement.startswith("NOT_AUTHORIZED"):
        fail(f"{eu.attrib.get('id')} is prematurely placement-authorized: {placement}")

corpus = repo.find("./evidence_surfaces/research_corpus")
if corpus is None:
    fail("repo research corpus missing")
source_count = int(corpus.attrib["declared_source_count"])
section_count = int(corpus.attrib["declared_anchor_section_count"])
ratio = source_count / section_count
if not ratio > 0.72:
    fail(f"source/section density gate failed: {ratio}")

mutation = audit.find("./mutation_decision")
if mutation is None or mutation.findtext("decision") != "DO_NOT_MUTATE_HTML_IN_THIS_RUN":
    fail("HTML mutation decision must remain fail-closed for this snapshot")
if audit.attrib.get("publication_allowed") != "false":
    fail("publication must remain blocked")
if audit.attrib.get("html_mutation_allowed") != "false":
    fail("HTML mutation must remain blocked for this snapshot")

final = audit.find("./final_decision")
if final is None or final.attrib.get("final_pass") != "false" or final.attrib.get("status") != "BLOCKED":
    fail("final decision must remain BLOCKED")

print("PASS: PV contract artifacts are internally coherent and scope-isolated.")
print(f"PASS: live PV semantic topology = full v4 canon ({len(CANON)}/23 sections).")
print(f"PASS: current repo HTML blob is pinned and matches its 15-section XML snapshot: {actual_blob}.")
print("PASS: live/repo qualification cardinality = 8 screens.")
print("EXPECTED BLOCK: repo preview is missing 8 live canonical surfaces.")
print("EXPECTED BLOCK: repo qualification semantics/controls do not match live.")
print("EXPECTED BLOCK: repo copy-contract metadata is stale versus NeoFort current=true.")
print("EXPECTED BLOCK: current EU admission, placement v1.2, XPath rebind and 3-replica presentation gates are unresolved.")
print(f"PASS: supplemental source-density check = {source_count}/{section_count} = {ratio:.3f} > 0.72.")
print("PUBLICATION: BLOCKED (correct DEVICEV fail-closed state).")
