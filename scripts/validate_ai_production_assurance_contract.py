#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "pages" / "programme" / "structure"
LIVE = BASE / "ai-production-assurance.live.xml"
REPO = BASE / "ai-production-assurance.repository.xml"
AUDIT = ROOT / "reports" / "ai-production-assurance.contract-audit.xml"

EXPECTED = [
    "triggers","consequences","for-whom","qualification","proposition","offers",
    "deliverables","before-after","results","proof","scope","process","modules",
    "intersection","commitments","questions","engagement"
]
CURRENT_NEOFORT_COPY_JUDGE = "judge:copy-claim:external-capability-grounding-v1.1"
CURRENT_NEOFORT_COPY_LOOP = "loop:copy-claim:external-capability-v1.1"

def parse(path):
    if not path.exists():
        raise SystemExit(f"BLOCKED_MISSING_FILE:{path}")
    return ET.parse(path).getroot()

live = parse(LIVE)
repo = parse(REPO)
audit = parse(AUDIT)
failures = []

def section_ids(root):
    return [s.attrib["id"] for s in root.findall("./topology/section")]

live_ids = section_ids(live)
repo_ids = section_ids(repo)
if live_ids != EXPECTED:
    failures.append(f"LIVE_TOPOLOGY_MISMATCH:{live_ids}")
if repo_ids != EXPECTED:
    failures.append(f"REPO_TOPOLOGY_MISMATCH:{repo_ids}")
if live_ids != repo_ids:
    failures.append("LIVE_REPO_SECTION_ORDER_MISMATCH")

live_form = live.find("./shared_qualification_form")
repo_form = repo.find("./shared_qualification_form")
if live_form is None or live_form.attrib.get("screen_count") != "8":
    failures.append("LIVE_SHARED_FORM_NOT_8_SCREENS")
if repo_form is None or repo_form.attrib.get("screen_count") != "8":
    failures.append("REPOSITORY_SHARED_FORM_MISMATCH")

live_forms = {s.attrib["id"]: s.attrib.get("semantic_form") for s in live.findall("./topology/section")}
repo_forms = {s.attrib["id"]: s.attrib.get("semantic_form") for s in repo.findall("./topology/section")}
for sid in EXPECTED:
    if live_forms.get(sid) != repo_forms.get(sid):
        failures.append(f"SECTION_FORM_MISMATCH:{sid}:{live_forms.get(sid)}!={repo_forms.get(sid)}")

attrs = {x.attrib.get("name"): x.attrib.get("value") for x in repo.findall("./html_contract/attribute")}
if attrs.get("judge") != CURRENT_NEOFORT_COPY_JUDGE:
    failures.append(f"NEOFORT_JUDGE_REFERENCE_DRIFT:{attrs.get('judge')}!={CURRENT_NEOFORT_COPY_JUDGE}")
if attrs.get("claim_loop") != CURRENT_NEOFORT_COPY_LOOP:
    failures.append(f"NEOFORT_LOOP_REFERENCE_DRIFT:{attrs.get('claim_loop')}!={CURRENT_NEOFORT_COPY_LOOP}")

source = live.find("./source")
if source is None or source.attrib.get("raw_dom_materialized") != "true":
    failures.append("RAW_LIVE_DOM_NOT_MATERIALIZED_EXACT_XPATH_UNPROVEN")

placement = audit.find("./placement_state/status")
if placement is None or placement.attrib.get("placement_judge_status") != "PASS":
    failures.append("PLACEMENT_PRESENTATION_JUDGE_NOT_PASS")

if failures:
    print("BLOCKED: AI Production Assurance live-structure publication contract failed closed.")
    for f in failures:
        print(" -", f)
    sys.exit(1)

print("PASS: exact live structure, section forms, shared qualifier, NeoFort policy refs and placement judge all validated.")
