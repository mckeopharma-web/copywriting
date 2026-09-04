#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'expertises/healthtech/healthtech.html'
XML=ROOT/'expertises/healthtech/contracts/healthtech-section-contract-2026-09-04.xml'
STRUCT=ROOT/'expertises/healthtech/contracts/healthtech-html-structure-2026-09-04.xml'
REVIEW=ROOT/'expertises/healthtech/healthtech_commercial-review-v3_2026-09-04.html'
EXPECTED=['healthtech-hero','healthtech-offers','healthtech-capabilities','healthtech-next-step','healthtech-qualifier']
EXPECTED_SCREENS=list(range(1,9))
fail=[]

def need(cond,msg):
    if not cond: fail.append(msg)

s=HTML.read_text(encoding='utf-8')
section_ids=re.findall(r'<section\b[^>]*\bid="([^"]+)"',s,re.I)
need(section_ids==EXPECTED,f'section-order:{section_ids!r}')
need(s.count('<section')==5,f'top-level-section-count-or-nested-section-drift:{s.count("<section")}')
need('<link rel="canonical" href="https://mickael-umt.com/expertises/healthtech/">' in s,'canonical-url-drift')
need('data-theme="dark"' in s,'dark-theme-contract-missing')
need(s.count('<article class="card">')==4,f'offer-route-count:{s.count("<article class=\"card\">")}')
need([int(x) for x in re.findall(r'data-screen="(\d+)"',s)]==EXPECTED_SCREENS,'qualifier-screen-order')
need(s.count('id="healthtech-form"')==1,'healthtech-form-id-count')
need(s.count('data-evidence-trigger=')==12,f'evidence-trigger-count:{s.count("data-evidence-trigger=")}')
eu_ids=set(re.findall(r'data-evidence-id="([^"]+)"',s))
expected_eu={'EU-REGCSV-EC-ANNEX11-RISK-2026','EU-REGCSV-FDA-CSA-RISK-2026','EU-CANON-EHDS-EHR-TESTING-2026','EU-HT-EMA-FDA-GOOD-AI-2026'}
need(eu_ids==expected_eu,f'evidence-id-set:{sorted(eu_ids)}')
need(s.count('data-qgeu-id=')==4,f'eug-candidate-count:{s.count("data-qgeu-id=")}')
need(s.count('data-eug-status="BLOCKED_PENDING_CURRENT_JUDGES"')==4,'eug-review-only-status-drift')

root=ET.parse(XML).getroot()
xml_ids=[x.attrib['id'] for x in root.findall('./healthtechArchetype/section')]
need(xml_ids==EXPECTED,f'xml-section-order:{xml_ids!r}')
seq=root.findtext('./orderingContract/sequence','').split(',')
need(seq==EXPECTED,f'xml-ordering-contract:{seq!r}')
need(root.find('./healthtechArchetype').attrib.get('exactSectionCount')=='5','xml-exact-section-count')

st=ET.parse(STRUCT).getroot()
st_ids=[x.attrib['id'] for x in st.findall('./document/main/section')]
need(st_ids==EXPECTED,f'structure-xml-section-order:{st_ids!r}')
need(st.find('./document/main').attrib.get('sectionCount')=='5','structure-xml-count')

r=REVIEW.read_text(encoding='utf-8')
need("const EXPECTED=['healthtech-hero','healthtech-offers','healthtech-capabilities','healthtech-next-step','healthtech-qualifier']" in r,'review-expected-sequence-drift')
need("new_external_effect_claims\":0" in r,'review-new-effect-claim-contract')
need("new_evidence_placements\":0" in r,'review-new-evidence-placement-contract')
need('<section class="sec"' not in r,'review-must-not-duplicate-base-topology')
need('REVIEW_ONLY_BLOCKED' in r,'review-publication-status')

contract_payload='|'.join(EXPECTED)+'|routes=4|screens=1,2,3,4,5,6,7,8|form=healthtech-form'
contract_sha=hashlib.sha256(contract_payload.encode()).hexdigest()
report={
 'validator':'healthtech-section-contract-v1',
 'status':'FAIL' if fail else 'PASS',
 'section_ids':section_ids,
 'section_count':len(section_ids),
 'offer_routes':s.count('<article class="card">'),
 'qualifier_screens':EXPECTED_SCREENS,
 'evidence_trigger_occurrences':s.count('data-evidence-trigger='),
 'unique_evidence_units':sorted(eu_ids),
 'eug_candidates':s.count('data-qgeu-id='),
 'contract_sha256':contract_sha,
 'failures':fail,
}
out=ROOT/'reports/healthtech-section-contract-validation.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
if fail:
    raise SystemExit(1)
