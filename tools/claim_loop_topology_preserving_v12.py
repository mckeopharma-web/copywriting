#!/usr/bin/env python3
"""NeoFort copy-claim loop v1.2 — topology-preserving materializer.

Invariant: never replace <body>, <main>, section order, section IDs, navigation,
CTA topology, EU/EUG DOM or existing visible copy wholesale.

This pass only materializes the loop contract around the already upgraded landing
pages, computes the strict Sou/Sec pre-gate, and records which sections still need
formal sequence-level research/judging.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LOOP_ID = "loop:copy-claim:external-capability-v1.2-topology-preserving"
JUDGE_ID = "judge:copy-claim:external-capability-grounding-v1.2"
THRESHOLD = 0.72
CONTRACT_ID = "neofort-claim-loop-contract"
OWN_HOSTS = {"mickael-umt.com", "www.mickael-umt.com"}
OWN_GITHUB_PREFIXES = (
    "https://github.com/RickOwri/",
    "https://github.com/mckeopharma-web/",
)

SECTION_RE = re.compile(r"<section\b([^>]*)>(.*?)</section\s*>", re.I | re.S)
ID_RE = re.compile(r"\bid\s*=\s*([\"'])(.*?)\1", re.I | re.S)
URL_RE = re.compile(r"\bhref\s*=\s*([\"'])(https?://[^\"']+)\1", re.I)


def section_id(attrs: str, index: int) -> str:
    m = ID_RE.search(attrs)
    return m.group(2) if m else f"__anonymous_section_{index:03d}"


def topology(text: str) -> list[str]:
    return [section_id(m.group(1), i) for i, m in enumerate(SECTION_RE.finditer(text), 1)]


def topology_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def is_external_evidence_url(url: str) -> bool:
    if url.startswith(OWN_GITHUB_PREFIXES):
        return False
    host = (urlparse(url).hostname or "").lower()
    if host in OWN_HOSTS:
        return False
    return bool(host)


def external_sources(text: str) -> list[str]:
    urls = {m.group(2).rstrip(".,)") for m in URL_RE.finditer(text)}
    return sorted(u for u in urls if is_external_evidence_url(u))


def claim_bearing_sections(text: str) -> list[str]:
    out: list[str] = []
    markers = (
        "data-eu-id=", "data-eug-id=", "lp-cite", "lp-evidence-ref",
        "lp-evidence-bubble-scroll", "supported proposition", "primary source",
    )
    for i, m in enumerate(SECTION_RE.finditer(text), 1):
        sid = section_id(m.group(1), i)
        body = m.group(2).lower()
        if any(marker in body for marker in markers):
            out.append(sid)
    return out


def set_html_contract(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        tag = m.group(0)
        attrs = {
            "data-claim-loop-version": "external-capability-v1.2-topology-preserving",
            "data-claim-loop": LOOP_ID,
            "data-judge": JUDGE_ID,
            "data-publication-status": "PENDING_FORMAL_LLM_JUDGE",
        }
        for name, value in attrs.items():
            if re.search(rf"\b{name}\s*=", tag, re.I):
                tag = re.sub(rf"\s+{name}\s*=\s*([\"']).*?\1", f' {name}="{value}"', tag, count=1, flags=re.I|re.S)
            else:
                tag = tag[:-1] + f' {name}="{value}">' 
        return tag
    return re.sub(r"<html\b[^>]*>", repl, text, count=1, flags=re.I|re.S)


def ensure_fail_closed_meta(text: str) -> str:
    if re.search(r"<meta\b[^>]*name\s*=\s*([\"'])robots\1", text, re.I):
        return text
    return re.sub(r"</head\s*>", '<meta name="robots" content="noindex,nofollow">\n</head>', text, count=1, flags=re.I)


def inject_contract(text: str, payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    block = f'<script type="application/json" id="{CONTRACT_ID}">{encoded}</script>'
    pattern = re.compile(rf'<script\b[^>]*id=["\']{re.escape(CONTRACT_ID)}["\'][^>]*>.*?</script\s*>', re.I|re.S)
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    return re.sub(r"</body\s*>", block + "\n</body>", text, count=1, flags=re.I)


def process(path: Path) -> dict:
    original = path.read_text(encoding="utf-8")
    if "CLAIM_LOOP_UPGRADE_BEGIN" in original or "claim-loop-seed-archive" in original or "claim-loop-page" in original:
        raise RuntimeError(f"destructive v1.1 residue found in {path}")

    before_ids = topology(original)
    before_hash = topology_hash(before_ids)
    sources = external_sources(original)
    claim_sections = claim_bearing_sections(original)
    section_count = len(claim_sections)
    source_count = len(sources)
    ratio = (source_count / section_count) if section_count else 0.0
    gate = "PASS" if section_count > 0 and ratio > THRESHOLD else "FAIL"

    payload = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "topology_contract": "PRESERVE_SECTION_ORDER_IDS_AND_VISIBLE_PAGE_STRUCTURE",
        "body_replacement_forbidden": True,
        "source_count": source_count,
        "section_count": section_count,
        "sources_per_section_ratio": round(ratio, 6),
        "source_section_threshold": THRESHOLD,
        "source_section_comparator": "STRICT_GREATER_THAN",
        "source_section_gate": gate,
        "claim_bearing_sections": claim_sections,
        "topology_sha256": before_hash,
        "publication_status": "PENDING_FORMAL_LLM_JUDGE",
    }

    upgraded = set_html_contract(original)
    upgraded = ensure_fail_closed_meta(upgraded)
    upgraded = inject_contract(upgraded, payload)

    after_ids = topology(upgraded)
    after_hash = topology_hash(after_ids)
    if before_ids != after_ids or before_hash != after_hash:
        raise RuntimeError(f"topology mutation detected in {path}")

    path.write_text(upgraded, encoding="utf-8")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "source_count": source_count,
        "section_count": section_count,
        "sources_per_section_ratio": round(ratio, 6),
        "gate": gate,
        "topology_sha256": before_hash,
        "section_ids": before_ids,
    }


def main() -> None:
    files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    results = [process(p) for p in files]
    failures = [r for r in results if r["gate"] != "PASS"]
    report = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "html_total": len(results),
        "topology_preserved": True,
        "body_replacement_forbidden": True,
        "source_section_gate": {
            "formula": "distinct_external_sources / claim_bearing_sections",
            "threshold": THRESHOLD,
            "comparator": "STRICT_GREATER_THAN",
            "pass": not failures,
        },
        "min_ratio": min((r["sources_per_section_ratio"] for r in results), default=0),
        "max_ratio": max((r["sources_per_section_ratio"] for r in results), default=0),
        "failures": failures,
        "files": results,
        "status": "PENDING_FORMAL_LLM_JUDGE" if not failures else "BLOCKED_SOURCE_SECTION_GATE",
    }
    out = ROOT / "reports" / "claim-loop-topology-preserving-v12.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(f"Sou/Sec gate failed for {len(failures)} HTML artifact(s)")


if __name__ == "__main__":
    main()
