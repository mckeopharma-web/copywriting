#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
import xml.etree.ElementTree as ET

TARGET = Path('engagement/audiences/avatar-ai-security.html')
CANDIDATE = Path('engagement/audiences/avatar-ai-security-customer-avatar.html')
CONTRACT = Path('engagement/audiences/structure/avatar-ai-security-contract.xml')
LIVE_XML = Path('engagement/audiences/structure/avatar-ai-security-live.xml')
HTML_XML = Path('engagement/audiences/structure/avatar-ai-security-html.xml')
REPORT = Path('reports/ai-security-avatar-contract-validation.xml')
EXPECTED = ['triggers','consequences','buyer','qualification','proposition','offers','deliverables','before-after','results','evidence','scope','process','modules','intersection','commitments','questions','engagement']
POLICIES = {
    'deterministic_preflight':'policy:evidence-agent-exploitability:deterministic-preflight-v2',
    'factfulness':'judge:evidence:factfulness-epistemology-methodology-v2',
    'agent_exploitability':'policy:evidence-agent-exploitability:proof-carrying-v3',
    'placement':'policy:evidence-placement:claim-span-entailment-v2',
    'placement_judge':'judge:evidence-placement:presentation-v1.2',
    'copy_grounding_judge':'judge:copy-claim:external-capability-grounding-v1.1',
    'llm_determinism':'policy:llm-judge:deterministic-execution-v2',
}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def section_ids(s: str) -> list[str]:
    return re.findall(r'<section\s+id="([^"]+)"', s)


def anchor_ids(s: str) -> list[str]:
    m = re.search(r'<nav class="anchorbar".*?</nav>', s, flags=re.S)
    if not m:
        return []
    return re.findall(r'href="#([^"]+)"', m.group(0))


def manifest(s: str, element_id: str) -> dict:
    m = re.search(rf'<script type="application/json" id="{re.escape(element_id)}">(.*?)</script>', s, flags=re.S)
    if not m:
        raise ValueError(f'missing JSON manifest {element_id}')
    return json.loads(m.group(1))


def preflight_topology(label: str, s: str) -> list[str]:
    errors = []
    if s.count('id="avatar-ai-security"') != 1:
        errors.append(f'{label}: avatar-ai-security id must occur exactly once')
    ids = section_ids(s)
    if ids != EXPECTED:
        errors.append(f'{label}: section order mismatch: {ids}')
    anchors = anchor_ids(s)
    if anchors != EXPECTED:
        errors.append(f'{label}: anchor order mismatch: {anchors}')
    if s.count('class="hero"') < 1:
        errors.append(f'{label}: hero missing')
    if 'data-theme="dark"' not in s:
        errors.append(f'{label}: dark theme contract missing')
    return errors


def materialize() -> None:
    old = TARGET.read_text(encoding='utf-8')
    candidate = CANDIDATE.read_text(encoding='utf-8')
    errors = preflight_topology('target-before', old) + preflight_topology('candidate', candidate)
    if errors:
        raise SystemExit('\n'.join(errors))
    # Copy only after topology equality has been proven. Keep publication fail-closed.
    out = candidate.replace('"artifact":"engagement/audiences/avatar-ai-security-customer-avatar.html"', '"artifact":"engagement/audiences/avatar-ai-security.html"')
    out = out.replace('data-publication-status="PENDING_FORMAL_LLM_JUDGE"', 'data-publication-status="REVIEW_ONLY_PENDING_TARGET_PLACEMENT_REPLICA_JUDGE"')
    out = out.replace('data-judge="judge:copy-claim:external-capability-grounding-v1.2"', 'data-judge="judge:copy-claim:external-capability-grounding-v1.1"')
    TARGET.write_text(out, encoding='utf-8')


def validate() -> tuple[str, str]:
    errors = []
    for p in [TARGET, CANDIDATE, CONTRACT, LIVE_XML, HTML_XML]:
        if not p.exists(): errors.append(f'missing:{p}')
    if errors: raise SystemExit('\n'.join(errors))

    target = TARGET.read_text(encoding='utf-8')
    candidate = CANDIDATE.read_text(encoding='utf-8')
    errors += preflight_topology('target', target)

    root = ET.parse(CONTRACT).getroot()
    contract_ids = [n.attrib['id'] for n in root.find('sections').findall('section') if n.attrib['id'] != 'hero']
    if contract_ids != EXPECTED:
        errors.append(f'contract: section order mismatch: {contract_ids}')
    if root.find('sections').attrib.get('count') != '18':
        errors.append('contract: expected section count=18')

    required_tokens = [
        'DEMOGRAPHICS_INTERESTS','FRUSTRATIONS_FEARS','WANTS_ASPIRATIONS','KEY_PURCHASE_DRIVERS','BEFORE_AFTER',
        'HAVE','FEEL','AVERAGE DAY','STATUS','EVIL → GOOD','MISSING_NOT_INFERRED','TO_VALIDATE','SYNTHESIS_NOT_CUSTOMER_VERBATIM'
    ]
    for token in required_tokens:
        if token not in target:
            errors.append(f'target: missing customer-avatar token {token}')

    if 'data-publication-status="REVIEW_ONLY_PENDING_TARGET_PLACEMENT_REPLICA_JUDGE"' not in target:
        errors.append('target: publication must remain REVIEW_ONLY_PENDING_TARGET_PLACEMENT_REPLICA_JUDGE')
    if 'data-judge="judge:copy-claim:external-capability-grounding-v1.1"' not in target:
        errors.append('target: current NeoFort copy-grounding judge metadata missing')

    try:
        em = manifest(target, 'evidence-manifest')
        pm = em.get('policy_resolution', {})
        for key, expected in POLICIES.items():
            if pm.get(key) != expected:
                errors.append(f'evidence-manifest: {key}={pm.get(key)!r}, expected {expected!r}')
        if len(em.get('evidence_units', [])) != 9:
            errors.append('evidence-manifest: expected 9 EvidenceUnits')
        if len(em.get('evidence_graphs', [])) != 3:
            errors.append('evidence-manifest: expected 3 EvidenceGraphs')
        lock = em.get('structure_lock', {})
        if lock.get('content_sections') != 17 or lock.get('order') != EXPECTED:
            errors.append('evidence-manifest: structure_lock mismatch')
        if em.get('validation', {}).get('fresh_target_placement_3_replica_judge') != 'REQUIRED':
            errors.append('evidence-manifest: target placement replica judge must remain REQUIRED')
    except Exception as exc:
        errors.append(f'evidence-manifest:{exc}')

    # XPath-equivalent uniqueness gates: each public claim anchor must be unique.
    claim_ids = re.findall(r'id="(claim-eu-ca-[0-9]+)"', target)
    if len(claim_ids) != len(set(claim_ids)):
        errors.append('target: duplicate claim anchor id')
    for cid in claim_ids:
        if target.count(f'id="{cid}"') != 1:
            errors.append(f'target: claim anchor {cid} match_count != 1')

    if errors:
        raise SystemExit('\n'.join(errors))

    target_hash, candidate_hash = sha256(target), sha256(candidate)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<validationReport id="ai-security-avatar-contract" status="PASS" scope="deterministic-structure-and-manifest">\n'
        f'  <target path="{TARGET}" sha256="{target_hash}" sectionCount="18" anchorCount="17" xpathUniqueness="PASS" />\n'
        f'  <candidate path="{CANDIDATE}" sha256="{candidate_hash}" />\n'
        '  <customerAvatar contract="contract:customer-avatar:audiences:2026-09-03" status="PASS" />\n'
        '  <evidence units="9" graphs="3" upstreamAdmission="REUSED_CURRENT_ADMITTED" />\n'
        '  <publication deterministicPreflight="PASS" semanticPlacementReplicas="REQUIRED" finalPass="false" state="REVIEW_ONLY" />\n'
        '  <boundary>This CI validates deterministic topology, manifests and XPath-equivalent uniqueness. It does not fabricate the required three independent semantic placement-judge replicas.</boundary>\n'
        '</validationReport>\n', encoding='utf-8')
    return target_hash, candidate_hash


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if args.apply:
        materialize()
    th, ch = validate()
    print(f'PASS deterministic contract: target={th[:12]} candidate={ch[:12]} sections=18 EU=9 EUG=3; final publication remains REVIEW_ONLY pending 3-replica placement judge')

if __name__ == '__main__':
    main()
