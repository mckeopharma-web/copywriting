#!/usr/bin/env python3
"""Fail-closed structure validator for the Pharmaceutical Evidence Assurance page.

Scope is intentionally narrow: one live URL, one repository HTML file, one topology report.
It does not rewrite HTML and it does not validate evidence truth; NeoFort remains authoritative
for evidence admission and placement/presentation decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

LIVE_URL = "https://mickael-umt.com/programme/pharmaceutical-evidence-assurance/"
TARGET_PATH = Path("pages/programme/pharmaceutical-evidence-assurance.html")
TOPOLOGY_REPORT = Path("reports/claim-loop-topology-preserving-v12.json")
EXPECTED_TOPOLOGY_SHA256 = "790b0e88dd04fec3d9304d9d5cca14851055db78cd08b698c6f4eb34a50934ce"
EXPECTED_SECTIONS = [
    "triggers",
    "consequences",
    "for-whom",
    "qualification",
    "proposition",
    "offers",
    "deliverables",
    "before-after",
    "outcomes",
    "evidence",
    "scope",
    "process",
    "modules",
    "intersection",
    "commitments",
    "questions",
    "engagement",
]


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attrs: dict[str, str] = {}
        self.section_refs: list[str] = []
        self.section_data_ids: list[str] = []
        self.fragment_hrefs: list[str] = []
        self.forms = 0
        self.element_ids: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        tag = tag.lower()
        if tag == "html" and not self.html_attrs:
            self.html_attrs = {k: v or "" for k, v in attrs}
        if tag == "section":
            if a.get("data-section-id"):
                self.section_data_ids.append(a["data-section-id"])
            ref = a.get("id") or a.get("data-section-id")
            if ref:
                self.section_refs.append(ref)
        if tag == "a":
            href = a.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.fragment_hrefs.append(href[1:])
        if a.get("id"):
            self.element_ids.append({
                "tag": tag,
                "id": a["id"],
                "class": a.get("class", ""),
            })
        if tag == "form":
            self.forms += 1


def unique_expected_in_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in EXPECTED_SECTIONS and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def parse_html(text: str) -> StructureParser:
    parser = StructureParser()
    parser.feed(text)
    return parser


def load_repo(root: Path) -> tuple[str, StructureParser]:
    path = root / TARGET_PATH
    text = path.read_text(encoding="utf-8")
    return text, parse_html(text)


def fetch_live() -> tuple[str, StructureParser]:
    req = urllib.request.Request(
        LIVE_URL,
        headers={
            "User-Agent": "mckeopharma-section-contract-audit/1.0 (+https://github.com/mckeopharma-web/copywriting)"
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if getattr(response, "status", 200) != 200:
            raise RuntimeError(f"live-fetch-http-status:{getattr(response, 'status', 'unknown')}")
        raw = response.read()
    text = raw.decode("utf-8", errors="strict")
    return text, parse_html(text)


def topology_entry(root: Path) -> dict:
    report = json.loads((root / TOPOLOGY_REPORT).read_text(encoding="utf-8"))
    matches = [x for x in report.get("files", []) if x.get("path") == TARGET_PATH.as_posix()]
    if len(matches) != 1:
        raise RuntimeError(f"topology-report-target-match-count:{len(matches)}")
    return matches[0]


def check_exact(name: str, actual, expected, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{name}: expected={expected!r} actual={actual!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--check-live", action="store_true")
    ap.add_argument("--report", default="")
    ap.add_argument("--save-live-html", default="")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    failures: list[str] = []
    repo_text, repo = load_repo(root)

    repo_sections = repo.section_data_ids
    check_exact("repo-section-order", repo_sections, EXPECTED_SECTIONS, failures)
    check_exact("repo-section-count", len(repo_sections), len(EXPECTED_SECTIONS), failures)
    check_exact("repo-section-unique-count", len(set(repo_sections)), len(EXPECTED_SECTIONS), failures)
    repo_nav = unique_expected_in_order(repo.fragment_hrefs)
    check_exact("repo-nav-order", repo_nav, EXPECTED_SECTIONS, failures)

    html_tag = re.search(r"<html\b[^>]*>", repo_text, re.I)
    if not html_tag:
        failures.append("repo-html-root:missing")
    else:
        tag = html_tag.group(0)
        required_root_fragments = [
            'data-theme="dark"',
            'data-claim-loop-version="external-capability-v1.2-topology-preserving"',
            'data-publication-status="PENDING_FORMAL_LLM_JUDGE"',
        ]
        for fragment in required_root_fragments:
            if fragment not in tag:
                failures.append(f"repo-root-contract:missing:{fragment}")

    if "CLAIM_LOOP_UPGRADE_BEGIN" in repo_text or "claim-loop-seed-archive" in repo_text:
        failures.append("repo-destructive-upgrade-residue")
    if "never certifies or releases a batch" not in repo_text:
        failures.append("repo-statutory-boundary:missing-batch-release-boundary")
    if "never replaces the Qualified Person" not in repo_text:
        failures.append("repo-statutory-boundary:missing-qualified-person-boundary")

    entry = topology_entry(root)
    check_exact("report-section-order", entry.get("section_ids"), EXPECTED_SECTIONS, failures)
    check_exact("report-topology-sha256", entry.get("topology_sha256"), EXPECTED_TOPOLOGY_SHA256, failures)
    check_exact("report-gate", entry.get("gate"), "PASS", failures)

    live_summary = None
    if args.check_live:
        live_text, live = fetch_live()
        if args.save_live_html:
            live_out = root / args.save_live_html
            live_out.parent.mkdir(parents=True, exist_ok=True)
            live_out.write_text(live_text, encoding="utf-8")
        live_sections = unique_expected_in_order(live.section_refs)
        live_nav = unique_expected_in_order(live.fragment_hrefs)
        check_exact("live-section-order", live_sections, EXPECTED_SECTIONS, failures)
        check_exact("live-nav-order", live_nav, EXPECTED_SECTIONS, failures)
        if "Pharmaceutical AI Decision Assurance" not in live_text:
            failures.append("live-page-identity:missing")
        if "ne certifie ni ne libère jamais un lot" not in live_text:
            failures.append("live-statutory-boundary:missing-batch-release-boundary")
        live_summary = {
            "url": LIVE_URL,
            "sha256": hashlib.sha256(live_text.encode("utf-8")).hexdigest(),
            "section_order": live_sections,
            "nav_order": live_nav,
            "form_count": live.forms,
            "all_section_refs": live.section_refs,
            "all_fragment_hrefs": live.fragment_hrefs,
            "element_ids": live.element_ids,
        }

    summary = {
        "contract": "contract:programme:pharmaceutical-evidence-assurance:structure:2026-09-04",
        "target": TARGET_PATH.as_posix(),
        "repo_html_sha256": hashlib.sha256(repo_text.encode("utf-8")).hexdigest(),
        "expected_topology_sha256": EXPECTED_TOPOLOGY_SHA256,
        "repo_section_order": repo_sections,
        "repo_nav_order": repo_nav,
        "topology_report_gate": entry.get("gate"),
        "live": live_summary,
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "scope": "ONE_PAGE_ONLY",
        "mutation_performed": False,
    }

    if args.report:
        out = root / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS: live and repository section contracts match exactly for the 17 anchored sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
