from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

TARGET = Path("expertises/ai-security/ai-security.html")
EXPECTED_GIT_BLOB_SHA = "d93066839986e5f66be4e1f714a0416d307b56a9"
EXPECTED_SECTIONS = [
    "triggers", "consequences", "buyer", "qualification", "proposition",
    "offers", "deliverables", "before-after", "results", "evidence",
    "scope", "process", "modules", "intersection", "commitments",
    "questions", "engagement",
]
EXPECTED_EUG_COUNTS = {
    "QGEU-AISEC-FRAMING-GAP-2026": 16,
    "QGEU-AISEC-TOOLMIN-PCS-2026": 8,
    "QGEU-AISEC-BOUNDED-EXFIL-DETAIL-2026": 10,
    "QGEU-AISEC-PERMISSION-OVERREACH-2026": 21,
}
HOSTS = {
    "consequences": "eug-framing-gap",
    "deliverables": "eug-toolmin",
    "modules": "eug-bounded-exfil",
    "commitments": "eug-permission-overreach",
}


def fail(msg: str) -> None:
    raise SystemExit(f"DEVICEV deterministic preflight failed: {msg}")


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def extract_json_script(html: str, script_id: str) -> tuple[dict, tuple[int, int]]:
    pattern = re.compile(
        rf'<script type="application/json" id="{re.escape(script_id)}">(.*?)</script>',
        re.S,
    )
    m = pattern.search(html)
    if not m:
        fail(f"missing JSON script #{script_id}")
    try:
        obj = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON script #{script_id}: {exc}")
    return obj, (m.start(1), m.end(1))


def replace_json_script(html: str, script_id: str, obj: dict) -> str:
    pattern = re.compile(
        rf'(<script type="application/json" id="{re.escape(script_id)}">)(.*?)(</script>)',
        re.S,
    )
    if not pattern.search(html):
        fail(f"cannot replace missing JSON script #{script_id}")
    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return pattern.sub(lambda m: m.group(1) + payload + m.group(3), html, count=1)


def wrap_eug_as_sidecar(html: str, section_id: str, article_id: str) -> str:
    start_token = f'<section id="{section_id}">'
    section_start = html.find(start_token)
    if section_start < 0:
        fail(f"section #{section_id} not found")
    section_end = html.find("</section>", section_start)
    if section_end < 0:
        fail(f"section #{section_id} has no closing tag")
    section_end += len("</section>")
    section = html[section_start:section_end]

    article_token = f'<article class="eug-card" id="{article_id}"'
    article_start = section.find(article_token)
    if article_start < 0:
        fail(f"EUG article #{article_id} not found in #{section_id}")
    article_end = section.find("</article>", article_start)
    if article_end < 0:
        fail(f"EUG article #{article_id} has no closing tag")
    article_end += len("</article>")

    h2_start = section.find('<h2 class="section-title">')
    if h2_start < 0:
        fail(f"section #{section_id} has no section title")
    prefix_end = section.find("</h2>", h2_start)
    if prefix_end < 0:
        fail(f"section #{section_id} title is malformed")
    prefix_end += len("</h2>")

    prefix = section[:prefix_end]
    copy = section[prefix_end:article_start]
    article = section[article_start:article_end]
    suffix = section[article_end:]

    article = article.replace(
        '<article class="eug-card"',
        f'<article class="eug-card eug-sidecar-visual" data-layout-host-section="{section_id}" data-layout-mode="sidecar" data-illustrates-section="{section_id}" aria-describedby="{section_id}-eug-context"',
        1,
    )
    wrapped = (
        prefix
        + f'<div class="eug-sidecar" data-eug-host="{section_id}">'
        + f'<div class="eug-sidecar-copy" id="{section_id}-eug-context">'
        + copy
        + "</div>"
        + article
        + "</div>"
        + suffix
    )
    return html[:section_start] + wrapped + html[section_end:]


def add_css(html: str) -> str:
    marker = ".eug-card{margin-top:30px;"
    if marker not in html:
        fail("EUG CSS anchor not found")
    sidecar_css = (
        ".eug-sidecar{display:grid;grid-template-columns:minmax(0,1.06fr) minmax(360px,.94fr);gap:24px;align-items:start;margin-top:28px}"
        ".eug-sidecar-copy{min-width:0}.eug-sidecar .eug-card{margin-top:0;min-width:0}"
        ".eug-sidecar .eug-chart{overflow-x:auto}.eug-sidecar .eug-svg{min-width:520px}"
        ".lab-decision-gate{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;align-items:stretch;margin-top:18px}"
        ".lab-decision-node{border:1px solid var(--line);background:rgba(13,18,43,.74);border-radius:12px;padding:12px;font-size:12px;color:#dce4f7;display:flex;align-items:center;justify-content:center;text-align:center;position:relative}"
        ".lab-decision-node:not(:last-child)::after{content:'→';position:absolute;right:-13px;top:50%;transform:translateY(-50%);z-index:2;color:var(--cyan);font-weight:800}"
        "@media(max-width:980px){.eug-sidecar{grid-template-columns:1fr}.eug-sidecar .eug-svg{min-width:680px}.lab-decision-gate{grid-template-columns:1fr}.lab-decision-node:not(:last-child)::after{content:'↓';right:auto;left:50%;top:auto;bottom:-13px}}"
        "@media(max-width:600px){.eug-sidecar .eug-svg{min-width:600px}}"
    )
    return html.replace(marker, sidecar_css + marker, 1)


def add_lab_decision_gate(html: str) -> str:
    anchor = '<div class="method-note">Method map, not an evidence graphic: the arrows describe the consulting mechanism, not a measured causal effect.</div>'
    if anchor not in html:
        fail("method-map note anchor not found")
    gate = (
        '<div class="lab-decision-gate" role="img" aria-label="NeoFort data-analysis lab decision: decision question, data quality, metric contract, source-linked observations, then use or upgrade the lab only if the result can change a decision gate" '
        'data-neofort-concepts="CHAIN|semantic-anchor:data-quality-before-decision-automation|concept:it-production-transition">'
        '<div class="lab-decision-node">Decision question is bounded</div>'
        '<div class="lab-decision-node">Data quality is adequate</div>'
        '<div class="lab-decision-node">MetricContract is complete</div>'
        '<div class="lab-decision-node">Observed marks are source-linked</div>'
        '<div class="lab-decision-node">Result can change a gate → use / upgrade lab</div>'
        '</div>'
        '<div class="method-note">NeoFort lab gate: a “no” before the final node means no EUG is manufactured; keep the section narrative, collect evidence, or route the question out. This is a decision-policy map, not empirical evidence.</div>'
    )
    return html.replace(anchor, anchor + gate, 1)


def upgrade_toolmin_visual_contract(html: str) -> str:
    data, _ = extract_json_script(html, "eug-data")
    for qid in EXPECTED_EUG_COUNTS:
        if qid not in data:
            fail(f"missing EUG data {qid}")
        data[qid]["chart"] = "grouped_bar"
    toolmin = data["QGEU-AISEC-TOOLMIN-PCS-2026"]
    toolmin["chart"] = "paired_dot"
    toolmin["x_axis"] = "model_or_source_aggregate"
    toolmin["y_axis"] = "paper_specific_privacy_cost_score"
    toolmin["aggregate_category"] = "Average"
    html = replace_json_script(html, "eug-data", data)

    old_aria = 'aria-label="Grouped bar chart of privacy-cost score before and after minimization for three LLMs and the source-reported average"'
    new_aria = 'aria-label="Paired-dot plot of privacy-cost score before and after minimization, with model name on the x-axis and score on the y-axis; the final category is the source-reported aggregate"'
    if old_aria not in html:
        fail("ToolMin aria-label anchor not found")
    html = html.replace(old_aria, new_aria, 1)

    boundary_old = "EU [9] and G2 use different source-reported evaluation slices and must not be arithmetically conflated."
    boundary_new = boundary_old + " † Average is the source-reported aggregate, not a model identity."
    if boundary_old not in html:
        fail("ToolMin boundary anchor not found")
    html = html.replace(boundary_old, boundary_new, 1)

    old = "const groupW=plotW/cats.length,inner=Math.min(groupW*.76,76),barW=inner/series.length;cats.forEach((cat,ci)=>{const base=L+ci*groupW+(groupW-inner)/2;series.forEach((ser,si)=>{const d=spec.data.find(x=>x.category===cat&&x.series===ser);if(!d)return;const h=(d.value/spec.max)*plotH,y=T+plotH-h,x=base+si*barW;const rect=add(svg,'rect',{x:x+1,y,width:Math.max(1,barW-3),height:h,rx:2,fill:palette[si%palette.length]});const title=document.createElementNS(svgNS,'title');title.textContent=`${cat} · ${ser}: ${d.value}${spec.unit==='%'?'%':' '+spec.unit}`;rect.appendChild(title);if(d.value>0)add(svg,'text',{x:x+barW/2,y:Math.max(T+10,y-4),fill:'#dce4f7','font-size':9,'text-anchor':'middle'},String(d.value));});const tx=L+ci*groupW+groupW/2,ty=T+plotH+16;add(svg,'text',{x:tx,y:ty,fill:'#a9b4d0','font-size':10,'text-anchor':'end',transform:`rotate(-34 ${tx} ${ty})`},cat);});"
    new = "const groupW=plotW/cats.length;if(spec.chart==='paired_dot'){cats.forEach((cat,ci)=>{const cx=L+ci*groupW+groupW/2,pts=[];series.forEach((ser,si)=>{const d=spec.data.find(x=>x.category===cat&&x.series===ser);if(!d)return;const y=T+plotH-(d.value/spec.max)*plotH;pts.push({x:cx,y,d,si});});if(pts.length>1)add(svg,'line',{x1:pts[0].x,y1:pts[0].y,x2:pts[1].x,y2:pts[1].y,stroke:'#51618f','stroke-width':2});pts.forEach(p=>{const dot=add(svg,'circle',{cx:p.x,cy:p.y,r:5.5,fill:palette[p.si%palette.length],stroke:'#080c1d','stroke-width':2});const title=document.createElementNS(svgNS,'title');title.textContent=`${cat} · ${p.d.series}: ${p.d.value} ${spec.unit}`;dot.appendChild(title);add(svg,'text',{x:p.x+9,y:p.y+3,fill:'#dce4f7','font-size':9},String(p.d.value));});const label=cat==='Average'?'Source avg.†':cat;add(svg,'text',{x:cx,y:T+plotH+25,fill:'#a9b4d0','font-size':10,'text-anchor':'middle'},label);});}else{const inner=Math.min(groupW*.76,76),barW=inner/series.length;cats.forEach((cat,ci)=>{const base=L+ci*groupW+(groupW-inner)/2;series.forEach((ser,si)=>{const d=spec.data.find(x=>x.category===cat&&x.series===ser);if(!d)return;const h=(d.value/spec.max)*plotH,y=T+plotH-h,x=base+si*barW;const rect=add(svg,'rect',{x:x+1,y,width:Math.max(1,barW-3),height:h,rx:2,fill:palette[si%palette.length]});const title=document.createElementNS(svgNS,'title');title.textContent=`${cat} · ${ser}: ${d.value}${spec.unit==='%'?'%':' '+spec.unit}`;rect.appendChild(title);if(d.value>0)add(svg,'text',{x:x+barW/2,y:Math.max(T+10,y-4),fill:'#dce4f7','font-size':9,'text-anchor':'middle'},String(d.value));});const tx=L+ci*groupW+groupW/2,ty=T+plotH+16;add(svg,'text',{x:tx,y:ty,fill:'#a9b4d0','font-size':10,'text-anchor':'end',transform:`rotate(-34 ${tx} ${ty})`},cat);});}"
    if old not in html:
        fail("generic grouped-bar renderer anchor not found")
    html = html.replace(old, new, 1)
    html = html.replace("const W=Math.max(760,110+cats.length*96),H=390", "const W=Math.max(520,110+cats.length*84),H=360", 1)
    return html


def update_contracts(html: str) -> str:
    manifest, _ = extract_json_script(html, "evidence-manifest")
    manifest["eug_status"] = "4_ADMISSIBLE_EUG_SELECTED_SIDE_CAR_LAYOUT"
    manifest["eug_layout"] = {
        "mode": "SIDECAR_WITHIN_PREEXISTING_SECTION",
        "layout_mutation_only": True,
        "hosts": {
            "QGEU-AISEC-FRAMING-GAP-2026": "consequences",
            "QGEU-AISEC-TOOLMIN-PCS-2026": "deliverables",
            "QGEU-AISEC-BOUNDED-EXFIL-DETAIL-2026": "modules",
            "QGEU-AISEC-PERMISSION-OVERREACH-2026": "commitments",
        },
        "rule": "Each graph illustrates an existing semantic section and never creates a standalone evidence section.",
    }
    manifest["data_analysis_lab_decision"] = {
        "concepts": [
            "CHAIN",
            "semantic-anchor:data-quality-before-decision-automation",
            "concept:it-production-transition",
        ],
        "decision": "Use or upgrade a data-analysis lab only when the question is bounded, data quality is adequate, MetricContract is complete, every observed mark is source-linked, and the result can change a decision gate.",
        "else": "Do not manufacture an EUG; keep narrative, collect evidence, or route out.",
    }
    manifest["version_consolidation"] = {
        "canonical_file": "expertises/ai-security/ai-security.html",
        "versioned_ai_security_html_search": "NO ai-security-v* file found in repository search on 2026-09-04",
        "feature_layers_merged": ["EU", "EUG", "source closure", "claim-loop contract", "sidecar layout", "visual-policy-v3 renderer", "lab decision gate"],
    }
    manifest.setdefault("current_policy_snapshot", {})["data_visualization_policy"] = "policy:qgeu:data-visualization-analyst-v3"
    manifest["validation"]["post_edit_rendered_judge"] = "PENDING_EXTERNAL_3_REPLICA_AFTER_LAYOUT_MUTATION"
    manifest["validation"]["publication"] = "BLOCKED_PENDING_PRESENTATION_JUDGE"
    html = replace_json_script(html, "evidence-manifest", manifest)

    contract, _ = extract_json_script(html, "neofort-claim-loop-contract")
    contract["topology_contract"] = "PRESERVE_SECTION_ORDER_IDS_NAVIGATION_CTA; EUG_LAYOUT_MUTATION_ONLY"
    contract["publication_status"] = "REVIEW_REQUIRED_AFTER_EUG_LAYOUT_MUTATION"
    contract["eug_layout_rule"] = "EUGP integrates beside its pre-existing host section and illustrates that section; no standalone EUG section."
    contract["data_analysis_lab_decision"] = "CHAIN -> data quality -> MetricContract -> source-linked observed marks -> decision-gate utility; otherwise no lab/EUG."
    contract.setdefault("current_true_policy_resolution", {})["data_visualization"] = "policy:qgeu:data-visualization-analyst-v3"
    html = replace_json_script(html, "neofort-claim-loop-contract", contract)

    review = {
        "devicev_version": "1.0.0",
        "execution_posture": "FAIL_CLOSED",
        "scope": "https://mickael-umt.com/expertises/ai-security/ only",
        "source_git_blob_sha": EXPECTED_GIT_BLOB_SHA,
        "mutation": "EUG sidecar integration + ToolMin paired-dot rerender + NeoFort lab decision gate + single canonical HTML consolidation",
        "deterministic_preflight": "PASS",
        "factfulness_snapshot": "UNCHANGED_SOURCE_CLAIMS_AND_BOUNDARIES",
        "provenance_snapshot": "UNCHANGED_HASH_VERIFIED_SOURCE_CLOSURE",
        "formal_placement_and_presentation_judge": "PENDING_EXTERNAL_ORCHESTRATOR_3_REPLICAS",
        "publication_allowed": False,
        "google_drive_write": "NOT_PERFORMED_REQUIRES_EXPLICIT_USER_APPROVAL",
    }
    payload = json.dumps(review, ensure_ascii=False, separators=(",", ":"))
    insert = f'<script type="application/json" id="devicev-layout-review">{payload}</script>\n'
    if 'id="devicev-layout-review"' not in html:
        html = html.replace("</body></html>", insert + "</body></html>", 1)
    return html


def validate(before: str, after: str) -> None:
    before_sections = re.findall(r'<section id="([^"]+)"', before)
    after_sections = re.findall(r'<section id="([^"]+)"', after)
    if before_sections != EXPECTED_SECTIONS or after_sections != EXPECTED_SECTIONS:
        fail(f"section order changed: {after_sections}")

    if after.count('class="eug-card eug-sidecar-visual"') != 4:
        fail("expected exactly 4 sidecar EUG cards")
    if after.count('class="eug-sidecar"') != 4:
        fail("expected exactly 4 sidecar wrappers")

    for host, article_id in HOSTS.items():
        section_start = after.find(f'<section id="{host}">')
        section_end = after.find("</section>", section_start)
        section = after[section_start:section_end]
        if f'id="{article_id}"' not in section:
            fail(f"graph #{article_id} left its host #{host}")
        if f'data-layout-host-section="{host}"' not in section:
            fail(f"graph #{article_id} lacks host binding")

    before_data, _ = extract_json_script(before, "eug-data")
    after_data, _ = extract_json_script(after, "eug-data")
    for qid, count in EXPECTED_EUG_COUNTS.items():
        if len(before_data[qid]["data"]) != count or len(after_data[qid]["data"]) != count:
            fail(f"data-point count changed for {qid}")
        before_points = [(d["category"], d["series"], d["value"]) for d in before_data[qid]["data"]]
        after_points = [(d["category"], d["series"], d["value"]) for d in after_data[qid]["data"]]
        if before_points != after_points:
            fail(f"source-reported marks changed for {qid}")

    if after_data["QGEU-AISEC-TOOLMIN-PCS-2026"].get("chart") != "paired_dot":
        fail("ToolMin did not receive paired-dot renderer")

    before_sources = set(re.findall(r'href="(https?://[^"]+)"', before))
    after_sources = set(re.findall(r'href="(https?://[^"]+)"', after))
    if not before_sources.issubset(after_sources):
        fail("an existing external URL was removed")

    ids = re.findall(r'\bid="([^"]+)"', after)
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        fail(f"duplicate HTML ids: {duplicates}")

    for evidence_id in [f"evidence-eu-sg-{i:03d}" for i in range(1, 8)] + ["evidence-eu-sg-008", "evidence-eu-sg-009", "evidence-eu-sg-010"]:
        if f'id="{evidence_id}"' not in after:
            fail(f"lost evidence disclosure {evidence_id}")
    for evidence_id in ["evidence-eug-framing-gap", "evidence-eug-toolmin", "evidence-eug-bounded-exfil", "evidence-eug-permission-overreach"]:
        if f'id="{evidence_id}"' not in after:
            fail(f"lost graph evidence disclosure {evidence_id}")

    manifest, _ = extract_json_script(after, "evidence-manifest")
    if manifest["validation"].get("publication") != "BLOCKED_PENDING_PRESENTATION_JUDGE":
        fail("fail-closed publication state not recorded")
    if 'data-publication-status="REVIEW_REQUIRED_AFTER_LAYOUT_MUTATION"' not in after:
        fail("HTML publication status is not fail-closed")


def main() -> None:
    before = TARGET.read_text(encoding="utf-8")
    actual_blob = git_blob_sha(TARGET)
    if actual_blob != EXPECTED_GIT_BLOB_SHA:
        fail(f"source blob moved: expected {EXPECTED_GIT_BLOB_SHA}, got {actual_blob}")

    html = before
    html = html.replace(
        'data-publication-status="PASS_CURRENT_TRUE_ONLY"',
        'data-publication-status="REVIEW_REQUIRED_AFTER_LAYOUT_MUTATION"',
        1,
    )
    html = html.replace(
        'data-claim-loop-version="external-capability-v1.2-topology-preserving"',
        'data-claim-loop-version="external-capability-v1.3-eug-sidecar" data-eug-layout-version="sidecar-v1"',
        1,
    )
    html = add_css(html)
    for host, article_id in HOSTS.items():
        html = wrap_eug_as_sidecar(html, host, article_id)
    html = add_lab_decision_gate(html)
    html = upgrade_toolmin_visual_contract(html)
    html = update_contracts(html)
    html = html.replace(
        "10 EU · 4 EUG · 80→30 Loop · fail-closed evidence pipeline",
        "10 EU · 4 EUG · section-sidecar layout · fail-closed review",
        1,
    )

    validate(before, html)
    TARGET.write_text(html, encoding="utf-8")
    print(json.dumps({
        "status": "PASS_DETERMINISTIC_REVIEW_READY",
        "source_blob_sha": actual_blob,
        "output_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "sections": len(EXPECTED_SECTIONS),
        "eugs": 4,
        "host_sections": HOSTS,
        "toolmin_renderer": "paired_dot",
        "publication": "BLOCKED_PENDING_PRESENTATION_JUDGE",
    }, indent=2))


if __name__ == "__main__":
    main()
