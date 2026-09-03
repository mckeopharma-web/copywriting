#!/usr/bin/env python3
"""Materialise NeoFort v1.1 source/section density contract on every HTML artifact.

This stage runs after tools/claim_loop_apply.py. It does not fabricate LLM-judge PASS.
It only verifies and materialises the deterministic publication pre-gate:

    distinct admitted external sources / claim-bearing sections > 0.72

Scope rules mirror NeoFort judge:copy-claim:external-capability-grounding-v1.1:
- section_count = visible research-compressed claim articles (.cl-claim).
- source_count = distinct external source URLs cited by those claim articles (.cl-ref).
- the comparator is STRICT_GREATER_THAN; 0.72 exactly fails.
- zero/missing counts fail closed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP_ID = "loop:copy-claim:external-capability-v1.1"
JUDGE_ID = "judge:copy-claim:external-capability-grounding-v1.1"
VERSION = "external-capability-v1.1"
THRESHOLD = 0.72


def upsert_attr(tag: str, name: str, value: str) -> str:
    pat = rf"\s{name}\s*=\s*([\"']).*?\1"
    clean = re.sub(pat, "", tag, flags=re.I | re.S)
    return clean[:-1] + f' {name}="{value}">' if clean.endswith(">") else clean


def claim_blocks(text: str) -> list[str]:
    return re.findall(
        r'<article\b[^>]*class=["\'][^"\']*\bcl-claim\b[^"\']*["\'][^>]*>.*?</article>',
        text,
        flags=re.I | re.S,
    )


def source_urls(blocks: list[str]) -> list[str]:
    urls: set[str] = set()
    for block in blocks:
        for m in re.finditer(
            r'<a\b[^>]*class=["\'][^"\']*\bcl-ref\b[^"\']*["\'][^>]*href=["\'](https?://[^"\']+)["\']',
            block,
            flags=re.I | re.S,
        ):
            urls.add(m.group(1).strip())
    return sorted(urls)


def patch_contract(text: str, source_count: int, section_count: int, ratio: float) -> str:
    gate = (
        '<div class="cl-contract">'
        '<strong>Copy contract.</strong> Existing page copy is retained only as an iteration-0 seed. '
        'Visible claims are compressed from external sources and bounded by CV-derived capabilities. '
        'Products and configurations may specialise the offer, but cannot create evidence or expand the capability boundary. '
        '<div class="cl-density" data-gate="sources-per-section" data-result="PASS">'
        f'<strong>Evidence-density pre-gate:</strong> {source_count} distinct external sources / '
        f'{section_count} claim-bearing sections = {ratio:.4f} &gt; {THRESHOLD:.2f} — PASS.'
        '</div>'
        ' Formal publication remains fail-closed until the three-replica NeoFort LLM judge passes all semantic and capability gates.'
        '</div>'
    )
    return re.sub(
        r'<div\s+class=["\']cl-contract["\']>.*?</div>',
        gate,
        text,
        count=1,
        flags=re.I | re.S,
    )


def patch_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    blocks = claim_blocks(text)
    urls = source_urls(blocks)
    section_count = len(blocks)
    source_count = len(urls)
    ratio = source_count / section_count if section_count else 0.0
    gate_pass = section_count > 0 and source_count > 0 and ratio > THRESHOLD

    # O/C: extend v1 output into v1.1 without mutating the archived seed.
    text = text.replace("loop:copy-claim:external-capability-v1", LOOP_ID)
    text = text.replace("judge:copy-claim:external-capability-grounding-v1", JUDGE_ID)
    text = re.sub(
        r'data-claim-loop-version=["\'][^"\']*["\']',
        f'data-claim-loop-version="{VERSION}"',
        text,
        count=1,
        flags=re.I,
    )

    def main_open(m: re.Match[str]) -> str:
        tag = m.group(0)
        tag = upsert_attr(tag, "data-claim-loop", LOOP_ID)
        tag = upsert_attr(tag, "data-judge", JUDGE_ID)
        tag = upsert_attr(tag, "data-source-count", str(source_count))
        tag = upsert_attr(tag, "data-section-count", str(section_count))
        tag = upsert_attr(tag, "data-sources-per-section-ratio", f"{ratio:.6f}")
        tag = upsert_attr(tag, "data-source-section-threshold", f"{THRESHOLD:.2f}")
        tag = upsert_attr(tag, "data-source-section-comparator", "STRICT_GREATER_THAN")
        tag = upsert_attr(tag, "data-source-section-gate", "PASS" if gate_pass else "FAIL")
        return tag

    text = re.sub(
        r'<main\b[^>]*class=["\'][^"\']*\bclaim-loop-page\b[^"\']*["\'][^>]*>',
        main_open,
        text,
        count=1,
        flags=re.I | re.S,
    )
    if gate_pass:
        text = patch_contract(text, source_count, section_count, ratio)
    else:
        text = re.sub(
            r'data-publication-status=["\'][^"\']*["\']',
            'data-publication-status="BLOCKED_SOURCE_SECTION_DENSITY"',
            text,
            count=1,
            flags=re.I,
        )

    path.write_text(text, encoding="utf-8")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "source_count": source_count,
        "section_count": section_count,
        "sources_per_section_ratio": round(ratio, 6),
        "threshold": THRESHOLD,
        "comparator": "STRICT_GREATER_THAN",
        "gate": "PASS" if gate_pass else "FAIL",
        "sources": urls,
    }


def main() -> None:
    files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    metrics = [patch_file(p) for p in files]
    failures = [m for m in metrics if m["gate"] != "PASS"]
    report = {
        "loop": LOOP_ID,
        "judge": JUDGE_ID,
        "html_total": len(files),
        "source_section_gate": {
            "formula": "source_count / section_count",
            "threshold": THRESHOLD,
            "comparator": "STRICT_GREATER_THAN",
            "pass": not failures,
        },
        "files": metrics,
        "status": "PENDING_FORMAL_LLM_JUDGE" if not failures else "BLOCKED_SOURCE_SECTION_DENSITY",
    }
    out = ROOT / "reports" / "claim-loop-all-html.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not files:
        raise SystemExit("No HTML files found")
    if failures:
        raise SystemExit("Source/section gate failed:\n" + "\n".join(
            f"{m['path']}: {m['source_count']}/{m['section_count']}={m['sources_per_section_ratio']}" for m in failures
        ))


if __name__ == "__main__":
    main()
