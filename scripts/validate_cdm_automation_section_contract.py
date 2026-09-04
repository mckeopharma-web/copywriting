#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'expertises/cdm-automation/structure/cdm-automation.live.2026-09-04.xml'
REVIEW=ROOT/'expertises/cdm-automation/cdm-automation.live-visible-review_2026-09-04.html'
EXPECTED=['triggers','consequences','audience','qualification','proposition','offers','deliverables','before-after','results','proofs','scope','process','modules','intersection','commitments','questions','engagement']
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.sections=[]; self.steps=[]; self.consent=False; self.form_contract=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='section' and 'id' in a: self.sections.append(a['id'])
        if tag=='form' and a.get('id')=='qualifier': self.form_contract=a.get('data-live-form-contract')
        if tag=='fieldset' and 'data-step' in a: self.steps.append(a['data-step'])
        if tag=='input' and a.get('name')=='consent' and 'required' in a: self.consent=True
fail=[]
xml=ET.parse(LIVE).getroot()
xml_ids=[x.attrib['id'] for x in xml.findall('./sections/section')]
if xml_ids!=EXPECTED: fail.append(f'live-xml-section-order:{xml_ids}')
p=P(); p.feed(REVIEW.read_text(encoding='utf-8'))
if p.sections!=EXPECTED: fail.append(f'review-html-section-order:{p.sections}')
if p.form_contract!='8-screen-qualifier': fail.append('form-contract-not-8-screen')
if p.steps!=[str(i) for i in range(1,9)]: fail.append(f'form-steps:{p.steps}')
if not p.consent: fail.append('consent-required-missing')
text=REVIEW.read_text(encoding='utf-8')
for token in ['data-fidelity="VISIBLE_STRUCTURE_RECONSTRUCTED_NOT_RAW_DOM"','data-section-contract="LIVE_SHARED_17_SECTION_CONTRACT"','data-publication-status="REVIEW_ONLY_FAIL_CLOSED"']:
    if token not in text: fail.append('missing:'+token)
if fail:
    print('FAIL'); print('\n'.join(fail)); sys.exit(1)
print('PASS: 17/17 section order + 8/8 qualifier screens + consent + fail-closed review metadata')
