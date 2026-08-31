#!/usr/bin/env python3
"""EvidenceUnit generation, verification, judge and placement quality gate.

Formal invariants
-----------------
x = {variable, value, unit, population, period, source}
u = {boundary, limitations, uncertainty, independence, conflicts}
F = f(x,u,b,s) -> admitted EvidenceUnit
Y = {CopySequence semantics, assertion class, CTA intent, XPath}
G = g(Y,F) -> publishable EvidencePlacement

The pipeline is fail-closed. A URL is never treated as proof until its contents are
fetched and checked. Effect evidence and recommendation evidence are separate.
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import requests
from jsonschema import validate as jsonschema_validate
from lxml import etree, html
from neo4j import GraphDatabase
from openai import OpenAI

USER_AGENT = "copywriting-evidence-gate/1.0 (+https://github.com/mckeopharma-web/copywriting)"
TIMEOUT = int(os.getenv("SOURCE_HTTP_TIMEOUT", "25"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")
ARTIFACT = Path(os.getenv("EVIDENCE_GATE_ARTIFACT", "artifacts/evidence-unit-quality-gate.json"))
ASSERTIVE = {"CLAIM", "RECOMMENDATION", "CLAIM_AND_RECOMMENDATION", "CTA"}


class GateError(RuntimeError):
    pass


@dataclass
class SourceCheck:
    url: str
    ok: bool
    status_code: int | None
    content_sha256: str | None
    numeric_anchors: list[str]
    missing_numeric_anchors: list[str]
    entailment: str
    rationale: str
    snippets: list[str]


@dataclass
class XPathCheck:
    xpath: str
    count: int
    ok: bool


class Neo:
    def __init__(self) -> None:
        uri = required_env("NEO4J_URI")
        user = required_env("NEO4J_USERNAME")
        password = required_env("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def query(self, query: str, **params: Any) -> list[dict[str, Any]]:
        with self.driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as s:
            return [r.data() for r in s.run(query, **params)]

    def execute(self, query: str, **params: Any) -> list[dict[str, Any]]:
        return self.query(query, **params)

    def close(self) -> None:
        self.driver.close()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise GateError(f"missing required environment variable: {name}")
    return value


def llm() -> OpenAI:
    required_env("OPENAI_API_KEY")
    return OpenAI()


def llm_json(prompt: str, *, web_search: bool = False) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"model": MODEL, "input": prompt}
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    response = llm().responses.create(**kwargs)
    raw = response.output_text.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GateError(f"judge returned non-JSON output: {raw[:500]}") from exc


def fetch_url(url: str) -> tuple[int, str, str]:
    if urlparse(url).scheme not in {"http", "https"}:
        raise GateError(f"unsupported source URL scheme: {url}")
    r = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.1"},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    r.raise_for_status()
    body = r.text
    ctype = r.headers.get("content-type", "")
    if "html" in ctype or "xhtml" in ctype or "<html" in body[:500].lower():
        doc = html.fromstring(body)
        for bad in doc.xpath("//script|//style|//noscript|//svg"):
            bad.drop_tree()
        text = " ".join(doc.xpath("//text()"))
    else:
        text = body
    text = normalize_text(text)
    if len(text) < 200:
        raise GateError(f"source body too small to verify ({len(text)} chars): {url}")
    return r.status_code, text, r.url


def normalize_text(value: str) -> str:
    value = html_lib.unescape(value)
    value = value.replace("−", "-").replace("–", "-").replace("—", "-").replace("×", "x")
    value = value.replace("%", " percent ")
    value = re.sub(r"(?<=\d),(?=\d{3}\b)", "", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def extract_numeric_anchors(claim: str) -> list[str]:
    c = claim.replace("−", "-").replace("–", "-").replace("—", "-")
    anchors = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)?(?:\s*[-–]\s*\d+(?:[.,]\d+)?)?\s*(?:%|pp|x|×)?", c)
    cleaned: list[str] = []
    for a in anchors:
        a = a.strip().replace(",", "")
        if a and a not in cleaned:
            cleaned.append(a)
    return cleaned


def anchor_variants(anchor: str) -> list[str]:
    a = anchor.lower().replace("×", "x").strip()
    variants = {normalize_text(a)}
    if "%" in a:
        variants.add(normalize_text(a.replace("%", " percent")))
    if "pp" in a:
        variants.add(normalize_text(a.replace("pp", "percentage points")))
    if "x" in a and re.match(r"^[+-]?\d", a):
        variants.add(normalize_text(a.replace("x", " times")))
    return sorted(v for v in variants if v)


def snippets_for(text: str, anchors: Iterable[str], radius: int = 650) -> list[str]:
    out: list[str] = []
    for anchor in anchors:
        for variant in anchor_variants(anchor):
            pos = text.find(variant)
            if pos >= 0:
                s = text[max(0, pos - radius): min(len(text), pos + len(variant) + radius)]
                if s not in out:
                    out.append(s)
                break
    return out[:8]


def verify_source(source_url: str, source_fact: str) -> SourceCheck:
    if not source_url or not source_fact:
        return SourceCheck(source_url or "", False, None, None, [], [], "UNKNOWN", "missing source_url or source_fact", [])
    try:
        status, text, resolved = fetch_url(source_url)
    except Exception as exc:  # fail closed by design
        return SourceCheck(source_url, False, None, None, [], [], "UNKNOWN", f"fetch failed: {exc}", [])
    anchors = extract_numeric_anchors(source_fact)
    missing: list[str] = []
    for a in anchors:
        if not any(v in text for v in anchor_variants(a)):
            missing.append(a)
    snippets = snippets_for(text, anchors)
    if anchors and missing:
        return SourceCheck(resolved, False, status, hashlib.sha256(text.encode()).hexdigest(), anchors, missing, "FALSE", "one or more deterministic numeric anchors are absent from fetched source", snippets)
    if not snippets:
        snippets = [text[:4500]]
    entail_prompt = f"""You are a source-entailment verifier. Determine whether the bounded SOURCE EXCERPTS support CLAIM exactly as written.
Do not use outside knowledge. Do not infer a broader population, cause, recommendation or guarantee. Numbers, direction, population and period must agree.
Return JSON only: {{"entailment":"TRUE|FALSE|UNKNOWN","rationale":"..."}}.
CLAIM:\n{source_fact}\n\nSOURCE EXCERPTS:\n{json.dumps(snippets, ensure_ascii=False)}"""
    try:
        e = llm_json(entail_prompt)
        entailment = str(e.get("entailment", "UNKNOWN")).upper()
        rationale = str(e.get("rationale", ""))
    except Exception as exc:
        entailment, rationale = "UNKNOWN", f"entailment judge failed: {exc}"
    ok = not missing and entailment == "TRUE"
    return SourceCheck(resolved, ok, status, hashlib.sha256(text.encode()).hexdigest(), anchors, missing, entailment, rationale, snippets)


def xpath_check(page_html: str, xpath: str) -> XPathCheck:
    if not xpath:
        return XPathCheck("", 0, False)
    try:
        doc = html.fromstring(page_html)
        count = len(doc.xpath(xpath))
    except (etree.XPathError, ValueError):
        count = -1
    return XPathCheck(xpath, count, count == 1)


def page_snapshot(page_url: str) -> tuple[str, str]:
    r = requests.get(page_url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text, hashlib.sha256(r.content).hexdigest()


def get_judge_contract(neo: Neo) -> dict[str, Any]:
    rows = neo.query("""
        MATCH (j:EvidenceUnitJudge {id:'judge:evidence-unit:champion-v2'})
        WHERE j.current=true
        OPTIONAL MATCH (j)-[:USES_JUDGE_PROMPT]->(p:EvidenceJudgePrompt)
        WHERE p.current=true
        OPTIONAL MATCH (j)-[:USES_SCORE_POLICY]->(sp:EvidenceJudgeScorePolicy)
        WHERE sp.current=true
        RETURN properties(j) AS judge, properties(p) AS prompt, properties(sp) AS score_policy
        LIMIT 1
    """)
    if not rows:
        raise GateError("Neo4j current EvidenceUnit Judge v2 not found")
    return rows[0]


def selected_eus(neo: Neo, page_url: str) -> list[dict[str, Any]]:
    return neo.query("""
        MATCH (eu:EvidenceUnit)-[:HAS_SITE_PLACEMENT|HAS_EVIDENCE_PLACEMENT]->(pl:EvidencePlacement)
        WHERE pl.page_url=$page_url AND pl.selected_homepage=true
        OPTIONAL MATCH (eu)-[:HAS_EVIDENCE_METRIC]->(m:EvidenceMetric)
        OPTIONAL MATCH (eu)-[er:EFFECT_SUPPORTED_BY]->(es:SourceDocument)
        OPTIONAL MATCH (eu)-[rr:RECOMMENDATION_SUPPORTED_BY]->(rs:SourceDocument)
        RETURN properties(eu) AS eu,
               properties(pl) AS placement,
               collect(DISTINCT properties(m)) AS metrics,
               collect(DISTINCT {source:properties(es), rel:properties(er)}) AS effect_sources,
               collect(DISTINCT {source:properties(rs), rel:properties(rr)}) AS recommendation_sources
        ORDER BY pl.sequence_id
    """, page_url=page_url)


def visible_sequences(neo: Neo, page_url: str) -> list[dict[str, Any]]:
    return neo.query("""
        MATCH (cs:CopySequence)
        WHERE cs.page_url=$page_url AND coalesce(cs.current,true)=true AND coalesce(cs.visible,true)=true
        OPTIONAL MATCH (eu:EvidenceUnit)-[:HAS_SITE_PLACEMENT|HAS_EVIDENCE_PLACEMENT]->(pl:EvidencePlacement)
        WHERE pl.page_url=$page_url AND pl.sequence_id=cs.id AND pl.selected_homepage=true
        RETURN properties(cs) AS sequence, collect(DISTINCT eu.id) AS selected_eu_ids
        ORDER BY coalesce(cs.dom_order, cs.id)
    """, page_url=page_url)


def classify_sequence(seq: dict[str, Any]) -> dict[str, Any]:
    existing = str(seq.get("assertion_class") or seq.get("claim_or_recommendation") or "").upper()
    text = str(seq.get("text") or seq.get("raw_text") or "").strip()
    is_cta = bool(seq.get("is_cta") or seq.get("cta_target_url") or seq.get("href") or "CTA" in existing)
    if existing in ASSERTIVE:
        return {"class": existing, "factual_premise": existing != "CTA" or bool(seq.get("claim_id")), "text": text}
    if not text:
        return {"class": "NON_ASSERTIVE", "factual_premise": False, "text": text}
    prompt = f"""Classify one public-site copy sequence. Return JSON only:
{{"class":"CLAIM|RECOMMENDATION|CLAIM_AND_RECOMMENDATION|CTA|NON_ASSERTIVE","factual_premise":true|false,"reason":"..."}}.
A CTA is an instruction/link/action request. If the CTA embeds an outcome, statistic, superiority, risk or benefit premise, factual_premise=true.
TEXT: {text}\nKNOWN_CTA: {is_cta}"""
    c = llm_json(prompt)
    c["text"] = text
    return c


def candidate_graph_for_judge(row: dict[str, Any], source_check: SourceCheck) -> dict[str, Any]:
    return {
        "EvidenceUnit": row.get("eu", {}),
        "EvidenceMetric": row.get("metrics", []),
        "EffectSources": row.get("effect_sources", []),
        "RecommendationSources": row.get("recommendation_sources", []),
        "EvidencePlacement": row.get("placement", {}),
        "source_verification": asdict(source_check),
    }


def judge_eu(contract: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    prompt_template = contract.get("prompt", {}).get("prompt_template")
    if not prompt_template:
        raise GateError("Judge prompt_template missing from Neo4j")
    prompt = f"{prompt_template}\n\nINPUT_OBJECT:\n{json.dumps(graph, ensure_ascii=False, default=str)}"
    result = llm_json(prompt)
    if "score_total" not in result or "hard_gate_pass" not in result:
        raise GateError("judge output missing score_total/hard_gate_pass")
    return result


def atomic_gate(eu: dict[str, Any]) -> tuple[bool, list[str]]:
    required = ["quant_variable", "quant_value", "quant_unit", "population", "period", "primary_source_url"]
    missing = [k for k in required if eu.get(k) in (None, "", [])]
    qv = str(eu.get("quant_value") or "")
    if qv and not re.search(r"\d", qv):
        missing.append("quant_value:not_numeric")
    return not missing, missing


def generation_prompt(sequence: dict[str, Any], page_url: str) -> str:
    return f"""Find five independent high-quality evidence candidates for this exact public-site sequence.
Use web search. Prefer peer-reviewed randomized/controlled/field/longitudinal/meta-analytic research or highly authoritative public research. Avoid vendors, competitors and product-promotional studies.
Each candidate must contain ONE primary quantitative atom x: numeric value/range, unit, population, period and canonical source URL. Do not invent bibliometrics. Copy must not name a competing product.
Return JSON only: {{"candidates":[{{"title":"","source_url":"","doi_or_canonical_id":"","source_fact":"one bounded sentence","quant_variable":"","quant_value":"","quant_unit":"","population":"","period":"","study_design":"","boundary_short":"","why_fit":""}}]}}.
PAGE: {page_url}
SEQUENCE: {json.dumps(sequence, ensure_ascii=False, default=str)}"""


def generate_gap_candidates(sequence: dict[str, Any], page_url: str) -> list[dict[str, Any]]:
    data = llm_json(generation_prompt(sequence, page_url), web_search=True)
    candidates = data.get("candidates") or []
    return candidates[:5] if isinstance(candidates, list) else []


def candidate_id(sequence_id: str, candidate: dict[str, Any]) -> str:
    raw = f"{sequence_id}|{candidate.get('source_url')}|{candidate.get('source_fact')}".encode()
    return "EU-AUTO-" + hashlib.sha256(raw).hexdigest()[:16].upper()


def persist_gap_candidate(neo: Neo, page_url: str, sequence: dict[str, Any], candidate: dict[str, Any], source: SourceCheck, judge: dict[str, Any], snapshot_sha: str, xp: XPathCheck) -> None:
    eu_id = candidate_id(str(sequence.get("id")), candidate)
    source_id = "src:auto:" + hashlib.sha256(str(candidate["source_url"]).encode()).hexdigest()[:20]
    neo.execute("""
        MATCH (cs:CopySequence {id:$sequence_id})
        MERGE (eu:EvidenceUnit {id:$eu_id})
        SET eu += $candidate,
            eu.current=true,
            eu.schema_version='3.0',
            eu.admission_status='ADMITTED',
            eu.judge_hard_gate_pass=true,
            eu.champion_score=$score,
            eu.champion_status=CASE WHEN $score > 95 THEN 'DOMINANT_CANDIDATE' ELSE 'CHAMPION_CANDIDATE' END,
            eu.source_verification_status='VERIFIED_SOURCE_TEXT_ENTAILMENT',
            eu.source_content_sha256=$source_sha,
            eu.updated_at=datetime()
        MERGE (sd:SourceDocument {id:$source_id})
        SET sd.url=$source_url, sd.locator=$source_url, sd.title=$source_title, sd.current=true, sd.verified=true,
            sd.content_sha256=$source_sha, sd.verified_at=datetime(), sd.source_class='candidate_high_quality_research'
        MERGE (eu)-[es:EFFECT_SUPPORTED_BY]->(sd)
        SET es.verified=true, es.relationship_description='Supports only the bounded source_fact; downstream recommendations require separate support.'
        MERGE (m:EvidenceMetric {id:'metric:'+ $eu_id +':primary'})
        SET m.eu_id=$eu_id, m.current=true, m.metric_kind='ATOMIC_QUANTITATIVE_COPY_ANCHOR',
            m.target_value=$quant_value, m.unit=$quant_unit, m.population=$population, m.updated_at=datetime()
        MERGE (eu)-[:HAS_EVIDENCE_METRIC]->(m)
        MERGE (pl:EvidencePlacement {id:'placement:'+ $eu_id +':' + $sequence_id})
        SET pl.eu_id=$eu_id, pl.page_url=$page_url, pl.sequence_id=$sequence_id, pl.target_xpath=$xpath,
            pl.xpath_match_count=1, pl.xpath_verification_status='VERIFIED_UNIQUE', pl.page_snapshot_sha256=$snapshot_sha,
            pl.publication_status='CANDIDATE', pl.selected_homepage=false, pl.source_url=$source_url,
            pl.source_verification_status='VERIFIED_SOURCE_TEXT_ENTAILMENT', pl.rendered_or_proposed_copy=cs.text,
            pl.updated_at=datetime()
        MERGE (eu)-[:HAS_SITE_PLACEMENT]->(pl)
    """, sequence_id=sequence.get("id"), eu_id=eu_id, candidate=candidate, score=float(judge["score_total"]),
        source_id=source_id, source_url=candidate["source_url"], source_title=candidate.get("title"), source_sha=source.content_sha256,
        quant_value=str(candidate.get("quant_value", "")), quant_unit=candidate.get("quant_unit"), population=candidate.get("population"),
        page_url=page_url, xpath=xp.xpath, snapshot_sha=snapshot_sha)


def audit(page_url: str, expected_count: int, mode: str) -> dict[str, Any]:
    neo = Neo()
    try:
        contract = get_judge_contract(neo)
        html_body, snapshot_sha = page_snapshot(page_url)
        selected = selected_eus(neo, page_url)
        distinct_ids = {r["eu"].get("id") for r in selected}
        report: dict[str, Any] = {
            "page_url": page_url,
            "mode": mode,
            "model": MODEL,
            "formula": {
                "x": "{variable,value,unit,population,period,source}",
                "u": "{boundary,limitations,uncertainty,independence,conflicts}",
                "F": "f(x,u,b,s) -> admitted EvidenceUnit",
                "G": "g(Y,F) -> publishable placement iff entailment/support/xpath/cardinality gates pass",
            },
            "page_snapshot_sha256": snapshot_sha,
            "expected_selected_eu_count": expected_count,
            "selected_eu_count": len(distinct_ids),
            "selected_eus": [],
            "sequence_coverage": [],
            "generated_candidates": [],
            "failures": [],
        }
        if len(distinct_ids) != expected_count:
            report["failures"].append(f"selected EU cardinality {len(distinct_ids)} != expected {expected_count}")

        for row in selected:
            eu = row.get("eu", {})
            atomic_ok, atomic_missing = atomic_gate(eu)
            source_url = eu.get("primary_source_url") or eu.get("source_url")
            source_fact = eu.get("source_fact")
            sc = verify_source(str(source_url or ""), str(source_fact or ""))
            placement = row.get("placement") or {}
            xc = xpath_check(html_body, str(placement.get("target_xpath") or ""))
            try:
                jr = judge_eu(contract, candidate_graph_for_judge(row, sc)) if sc.ok and atomic_ok else {"hard_gate_pass": False, "score_total": eu.get("champion_score"), "status": "PRE_JUDGE_REJECT"}
            except Exception as exc:
                jr = {"hard_gate_pass": False, "score_total": eu.get("champion_score"), "status": "JUDGE_ERROR", "judge_rationale": str(exc)}
            entry = {"eu_id": eu.get("id"), "atomic_ok": atomic_ok, "atomic_missing": atomic_missing, "source_check": asdict(sc), "xpath_check": asdict(xc), "judge": jr}
            report["selected_eus"].append(entry)
            if not atomic_ok:
                report["failures"].append(f"{eu.get('id')}: incomplete atomic x: {atomic_missing}")
            if not sc.ok:
                report["failures"].append(f"{eu.get('id')}: source verification failed ({sc.rationale})")
            if not bool(jr.get("hard_gate_pass")):
                report["failures"].append(f"{eu.get('id')}: LLM Judge hard gate failed")
            if not xc.ok:
                report["failures"].append(f"{eu.get('id')}: XPath match count is {xc.count}, expected 1")

        sequences = visible_sequences(neo, page_url)
        for row in sequences:
            seq = row.get("sequence", {})
            try:
                cls = classify_sequence(seq)
            except Exception as exc:
                cls = {"class": "UNKNOWN", "factual_premise": True, "reason": str(exc), "text": seq.get("text")}
            c = str(cls.get("class", "UNKNOWN")).upper()
            selected_support = row.get("selected_eu_ids") or []
            target_xpath = str(seq.get("target_xpath") or seq.get("element_xpath") or "")
            xc = xpath_check(html_body, target_xpath) if target_xpath else XPathCheck("", 0, False)
            needs_eu = c in ASSERTIVE
            route = seq.get("cta_target_url") or seq.get("href") or seq.get("target_url")
            route_ok = c != "CTA" or bool(route)
            covered = (not needs_eu) or bool(selected_support)
            item = {"sequence_id": seq.get("id"), "class": c, "factual_premise": bool(cls.get("factual_premise")), "selected_eu_ids": selected_support, "covered": covered, "route_ok": route_ok, "xpath": asdict(xc)}
            report["sequence_coverage"].append(item)
            if needs_eu and not covered:
                report["failures"].append(f"{seq.get('id')}: {c} has no selected complete EU")
                if mode == "apply" and target_xpath and xc.ok:
                    candidates = generate_gap_candidates(seq, page_url)
                    candidate_results = []
                    for cand in candidates:
                        cand["id"] = candidate_id(str(seq.get("id")), cand)
                        sc = verify_source(str(cand.get("source_url") or ""), str(cand.get("source_fact") or ""))
                        atomic_ok, missing = atomic_gate(cand)
                        graph = {"EvidenceUnit": cand, "EvidencePlacement": {"page_url": page_url, "sequence_id": seq.get("id"), "target_xpath": target_xpath}, "source_verification": asdict(sc)}
                        jr = judge_eu(contract, graph) if sc.ok and atomic_ok else {"hard_gate_pass": False, "score_total": 0, "missing_fields": missing}
                        candidate_results.append({"candidate": cand, "source_check": asdict(sc), "judge": jr})
                        if sc.ok and atomic_ok and bool(jr.get("hard_gate_pass")):
                            persist_gap_candidate(neo, page_url, seq, cand, sc, jr, snapshot_sha, xc)
                    report["generated_candidates"].append({"sequence_id": seq.get("id"), "candidates": candidate_results})
            if c == "CTA" and not route_ok:
                report["failures"].append(f"{seq.get('id')}: CTA has no valid target route")
            if needs_eu and target_xpath and not xc.ok:
                report["failures"].append(f"{seq.get('id')}: assertive sequence XPath must match exactly once")

        report["passed"] = not report["failures"]
        return report
    finally:
        neo.close()


def write_report(report: dict[str, Any]) -> None:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report.get("passed"), "failures": len(report.get("failures", [])), "artifact": str(ARTIFACT)}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-url", default=os.getenv("EVIDENCE_PAGE_URL", "https://mickael-umt.com/"))
    parser.add_argument("--expected-count", type=int, default=int(os.getenv("HOMEPAGE_EU_COUNT", "20")))
    parser.add_argument("--mode", choices=["check", "apply"], default=os.getenv("EVIDENCE_PIPELINE_MODE", "check"))
    args = parser.parse_args()
    try:
        report = audit(args.page_url, args.expected_count, args.mode)
        write_report(report)
        return 0 if report.get("passed") else 2
    except Exception as exc:
        report = {"passed": False, "fatal": str(exc), "failures": [str(exc)]}
        write_report(report)
        return 3


if __name__ == "__main__":
    sys.exit(main())
