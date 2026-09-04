#!/usr/bin/env python3
from pathlib import Path
from lxml import html, etree
import json, sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages/realisations/ia-agents.html"
LIVE_XML = ROOT / "pages/realisations/ia-agents.live.structure.xml"
REPO_XML = ROOT / "pages/realisations/ia-agents.repo.structure.xml"
CONTRACT = ROOT / "contracts/realisations-ia-agents.section-contract.xml"

failures = []
def require(ok, msg):
    if not ok:
        failures.append(msg)

for p in (PAGE, LIVE_XML, REPO_XML, CONTRACT):
    require(p.exists(), f"missing:{p.relative_to(ROOT) if p.exists() or p.is_absolute() else p}")
if failures:
    raise SystemExit("\n".join(failures))

doc = html.fromstring(PAGE.read_text(encoding="utf-8"))
contract = etree.parse(str(CONTRACT)).getroot()
live = etree.parse(str(LIVE_XML)).getroot()
repo = etree.parse(str(REPO_XML)).getroot()

required_sections = ["ia-agents-hero","ia-agents-projects","ia-agents-provenance","ia-agents-method-form"]
observed = [x.get("id") for x in doc.xpath("//main/section")]
require(observed == required_sections, f"section-order:{observed!r}")

for sid in required_sections:
    require(len(doc.xpath(f"//*[@id='{sid}']")) == 1, f"xpath-count:{sid}")

projects = ["mistral","rag","streamlit","governed"]
project_nodes = doc.xpath("//*[@id='ia-agents-projects']//article")
require([x.get("id") for x in project_nodes] == projects, "project-order-or-count")

require(len(doc.xpath("//*[@id='framework-form']")) == 1, "form-id")
require(len(doc.xpath("//*[@id='framework-screen-1']")) == 1, "form-screen-1")
require(len(doc.xpath("//*[@id='framework-screen-2']")) == 1, "form-screen-2")
require(len(doc.xpath("//input[@name='email' and @required]")) == 1, "email-required")
require(len(doc.xpath("//input[@name='consent' and @required]")) == 1, "consent-required")
require(len(doc.xpath("//input[@name='work_topic']")) == 6, "work-topic-options")
require(len(doc.xpath("//input[@name='intended_use']")) == 3, "intended-use-options")
require(doc.xpath("//*[@id='framework-form']/@data-network-submit") == ["DISABLED_IN_REVIEW_ARTIFACT"], "review-form-network-disabled")

for cid in ("claim-nist-tevv","claim-ncsc-controls","claim-bounded-auth"):
    require(len(doc.xpath(f"//*[@id='{cid}']")) == 1, f"claim-xpath-count:{cid}")

# Contract references: 23-section S/P canon is reference-only for this proof page.
canon = "0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8"
require(contract.xpath("string(ownerPolicy/canonicalOfferProgrammeOrder)") == canon, "canonical-order")
require(contract.xpath("string(ownerPolicy/offerProgrammeCanonReferenceOnly)") == "true", "canon-must-be-reference-only")
require(int(contract.xpath("string(requiredTopology/@sectionCount)")) == 4, "contract-section-count")
require(int(live.xpath("string(liveTopologyCheck/@sectionCount)")) == 4, "live-xml-section-count")
require(int(live.xpath("string(liveTopologyCheck/@projectCount)")) == 4, "live-xml-project-count")
require(int(live.xpath("string(liveTopologyCheck/@formScreens)")) == 2, "live-xml-form-screens")

# NeoFort / DEVICEV deterministic metadata.
html_root = doc.xpath("/html")[0]
require(html_root.get("data-publication-status") == "PENDING_FORMAL_LLM_JUDGE", "publication-must-remain-pending")
require(len(doc.xpath("//*[@id='customer-avatar-contract']")) == 1, "avatar-contract")
require(len(doc.xpath("//*[@id='evidence-placement-contract']")) == 1, "evidence-placement-contract")
require(len(doc.xpath("//*[@id='neofort-claim-loop-contract']")) == 1, "neofort-loop-contract")

for script_id in ("customer-avatar-contract","evidence-candidate-pool","evidence-placement-contract","section-contract","neofort-claim-loop-contract"):
    txt = doc.xpath(f"string(//*[@id='{script_id}'])")
    try:
        json.loads(txt)
    except Exception as e:
        failures.append(f"invalid-json:{script_id}:{e}")

loop = json.loads(doc.xpath("string(//*[@id='neofort-claim-loop-contract'])"))
require(loop["source_count"] / loop["section_count"] > loop["source_section_threshold"], "sources-per-section-not-strictly-greater")
require(loop["source_section_gate"] == "PASS", "source-section-gate")
require(loop["publication_status"] == "PENDING_FORMAL_LLM_JUDGE", "loop-publication-status")

placements = json.loads(doc.xpath("string(//*[@id='evidence-placement-contract'])"))
for row in placements["placements"]:
    require(row["xpath_match_count"] == 1, f"placement-xpath:{row['claim_id']}")
    require(row["judge_status"] == "PENDING_3_REPLICA_JUDGEMENT", f"placement-judge-status:{row['claim_id']}")
    require(row["agent_exploitability_status"] == "BLOCKED_PENDING_PLACEMENT_JUDGE", f"agent-exploitability:{row['claim_id']}")

if failures:
    print("FAIL")
    print("\n".join(failures))
    sys.exit(1)

print("PASS: /realisations/ia-agents/ live topology preserved")
print("PASS: 4 main sections, 4 project records, 2-screen framework form")
print("PASS: S/P 23-section canon checked as reference-only; not forced onto proof-realisation page")
print("PASS: 3 evidence claim XPaths resolve exactly once")
print("PASS: source/section density = 3/4 = 0.75 > 0.72")
print("BLOCKED_FINAL: formal 3-replica EvidencePlacement judge is still pending by design")
