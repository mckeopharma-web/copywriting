#!/usr/bin/env python3
from pathlib import Path
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
HTML = BASE / "publish/expertises/growth/growth.live-contract-candidate.html"
LIVE_XML = BASE / "expertises/growth/structure/live-page.xml"
CANON = [0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8]
GROWTH = [0,10,5,7,8]


def fail(msg):
    raise SystemExit(f"FAIL: {msg}")


def is_subsequence(sub, seq):
    it = iter(seq)
    return all(any(x == y for y in it) for x in sub)

if not HTML.exists():
    fail("candidate HTML missing")
if not LIVE_XML.exists():
    fail("live-page XML contract missing")

html = HTML.read_text(encoding="utf-8")
root = ET.parse(LIVE_XML).getroot()
contract = root.find("./section_contract")
canon = [int(x) for x in contract.attrib["canonical_full_order"].split(",")]
subset = [int(x) for x in contract.attrib["selected_justified_subset"].split(",")]
if canon != CANON or subset != GROWTH or not is_subsequence(subset, canon):
    fail("XML canonical/subset contract drift")

section_tokens = [int(x) for x in re.findall(r'<section\b[^>]*data-section-token="(\d+)"', html)]
if section_tokens != GROWTH:
    fail(f"HTML section-token sequence drift: {section_tokens}")

expected_ids = ["growth:hero","growth:offers","growth:capabilities","growth:next-step","growth:qualification"]
section_ids = re.findall(r'<section\b[^>]*data-section-id="([^"]+)"', html)
if section_ids != expected_ids:
    fail(f"HTML section-id topology drift: {section_ids}")

if len(re.findall(r'data-seq-id="growth:offer:', html)) != 2:
    fail("offer cardinality != 2")
if len(re.findall(r'data-seq-id="growth:capability:', html)) != 3:
    fail("capability cardinality != 3")
if sorted(int(x) for x in re.findall(r'data-screen="([1-8])"', html)) != list(range(1,9)):
    fail("qualification screen set != 1..8")

questions = [
    "Qu’est-ce qui doit avancer ?",
    "Dans quel cadre ?",
    "Comment souhaitez-vous avancer ?",
    "À quel rythme hebdomadaire ?",
    "Quelle est la taille de l’organisation ?",
    "Où en est le scope ?",
    "Y a-t-il un déclencheur d’inspection ou de contrôle ?",
    "Où envoyer la réponse ?",
]
for q in questions:
    if q not in html:
        fail(f"missing live-form semantic question: {q}")

for field in ["need","timeline","role","mode","cadence","org_size","maturity","inspection","consent"]:
    if f'name="{field}"' not in html:
        fail(f"missing interactive field group: {field}")
if 'type="email"' not in html:
    fail("professional email control missing")

required_current = [
    'data-neofort-copy-loop="loop:copy-claim:external-capability-v1.1"',
    'data-neofort-copy-judge="judge:copy-claim:external-capability-grounding-v1.1"',
    'data-neofort-placement-judge="judge:evidence-placement:presentation-v1.2"',
    'data-neofort-placement-policy="policy:evidence-placement:claim-span-entailment-v2@2.2"',
]
for marker in required_current:
    if marker not in html:
        fail(f"missing current NeoFort marker: {marker}")
if "external-capability-v1.2-topology-preserving" in html or "external-capability-grounding-v1.2" in html:
    fail("stale v1.2 copy-claim contract leaked into candidate")

if 'data-publication-status="BLOCKED_PENDING_DEVICEV_EU_PLACEMENT"' not in html:
    fail("candidate must remain publication-blocked")
if '"publication_authorized":false' not in html:
    fail("evidence candidate payload must remain not publication-authorized")
if html.count('"placement":"NOT_AUTHORIZED"') != 3:
    fail("all three external candidates must remain NOT_AUTHORIZED")

visitor_copy = html.split('<script type="application/json" id="devicev-evidence-candidates">', 1)[0]
for external in ["arxiv.org", "frontiersin.org", "digital-strategy.ec.europa.eu"]:
    if external in visitor_copy:
        fail(f"unadmitted external evidence leaked into visitor copy: {external}")

print("PASS: Growth HTML candidate preserves section tokens [0,10,5,7,8].")
print("PASS: cardinality = 2 offers + 3 capability cards + 8 qualification screens.")
print("PASS: qualification questions and interactive control groups match the live semantic contract.")
print("PASS: copy-claim policy markers resolve to NeoFort current=true v1.1; placement judge remains v1.2.")
print("PASS: external research remains metadata-only and NOT_AUTHORIZED for visitor placement.")
print("PUBLICATION: BLOCKED until EU admission, immutable snapshot, unique XPath and 3-replica judges PASS.")
