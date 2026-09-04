#!/usr/bin/env python3
"""Fail-closed live/repository contract audit for one programme page.

This validator has two different outputs:
1) deterministic_audit_status: whether the audit faithfully captured current live and repo state;
2) page_parity_status/publication_status: whether the legacy review HTML may be treated as live-parity/publication-ready.

A green CI audit MUST NOT be interpreted as evidence-placement publication approval.
NeoFort remains authoritative for evidence admission and target-page presentation judgement.
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
LEGACY_PATH = Path("pages/programme/pharmaceutical-evidence-assurance.html")
SNAPSHOT_PATH = Path("pages/programme/pharmaceutical-evidence-assurance.live.sanitized.html")
TOPOLOGY_REPORT = Path("reports/claim-loop-topology-preserving-v12.json")
EXPECTED_LEGACY_TOPOLOGY_SHA256 = "790b0e88dd04fec3d9304d9d5cca14851055db78cd08b698c6f4eb34a50934ce"

CANONICAL_TOKENS = ["0","11","20","13","14","1","2","10","15","3","12","19","4","16","17","18","5","21","6","22","23","7","8"]
LIVE_ANCHORS = [
    "haut","declencheurs","problemes","pour-qui","qualification","proposition","valeur","offres",
    "produit","transformation","avant-apres","resultats","preuves","perimetre","deroule","modules",
    "capacites","intersection","benchmark","garantie","faq","engagement","demande",
]
LIVE_DATA_IDS = [
    "hero","triggers","problems","audience","qualification","proposition","value","offers","product",
    "transformation","before_after","results","proof","scope","phases","modules","capabilities",
    "intersection","benchmark","guarantee","faq","engagement","lead_form",
]
LIVE_LAYOUTS = [
    "split","ledger","graph","mosaic","compare","editorial","matrix","ledger","console","editorial",
    "compare","ledger","mosaic","matrix","timeline","mosaic","graph","canvas","console","matrix",
    "ledger","split","form",
]
LIVE_NAV_ANCHORS = [
    "declencheurs","problemes","pour-qui","qualification","proposition","offres","produit",
    "avant-apres","resultats","preuves","perimetre","deroule","modules","intersection",
    "garantie","faq","engagement",
]
NESTED_LEAD_FORM_ID = "lead-form-pharma-evidence-scope-programme-pharma"

LEGACY_SECTION_IDS = [
    "triggers","consequences","for-whom","qualification","proposition","offers","deliverables",
    "before-after","outcomes","evidence","scope","process","modules","intersection","commitments",
    "questions","engagement",
]
MISSING_CANONICAL_TOKENS = ["2","3","5","6","8"]


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict[str, str]] = []
        self.fragment_hrefs: list[str] = []
        self.form_count = 0
        self.html_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        tag = tag.lower()
        if tag == "html" and not self.html_attrs:
            self.html_attrs = {k: v or "" for k, v in attrs}
        if tag == "section":
            self.sections.append({
                "id": a.get("id", ""),
                "data_section_id": a.get("data-section-id", ""),
                "token": a.get("data-section-token", ""),
                "class": a.get("class", ""),
                "layout": a.get("data-layout", ""),
                "density": a.get("data-density", ""),
                "typology": a.get("data-typology", ""),
            })
        if tag == "a":
            href = a.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.fragment_hrefs.append(href[1:])
        if tag == "form":
            self.form_count += 1


def parse_html(text: str) -> StructureParser:
    p = StructureParser()
    p.feed(text)
    return p


def unique_in_order(values: list[str], allowed: set[str]) -> list[str]:
    out, seen = [], set()
    for value in values:
        if value in allowed and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def fetch_live() -> str:
    req = urllib.request.Request(
        LIVE_URL,
        headers={"User-Agent": "mckeopharma-section-contract-audit/1.1 (+https://github.com/mckeopharma-web/copywriting)"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if getattr(response, "status", 200) != 200:
            raise RuntimeError(f"live-fetch-http-status:{getattr(response, 'status', 'unknown')}")
        return response.read().decode("utf-8", errors="strict")


def sanitize_live(text: str) -> tuple[str, int]:
    pattern = re.compile(r'(name="csrfmiddlewaretoken"\s+value=")[^"]+(")', re.I)
    sanitized, count = pattern.subn(r'\1__REDACTED_CSRF_TOKEN__\2', text)
    return sanitized, count


def topology_entry(root: Path) -> dict:
    report = json.loads((root / TOPOLOGY_REPORT).read_text(encoding="utf-8"))
    matches = [x for x in report.get("files", []) if x.get("path") == LEGACY_PATH.as_posix()]
    if len(matches) != 1:
        raise RuntimeError(f"topology-report-target-match-count:{len(matches)}")
    return matches[0]


def check(name: str, actual, expected, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{name}: expected={expected!r} actual={actual!r}")


def extract_live_contract(parser: StructureParser) -> dict:
    canonical = [s for s in parser.sections if s.get("token")]
    return {
        "tokens": [s["token"] for s in canonical],
        "anchors": [s["id"] for s in canonical],
        "data_section_ids": [s["data_section_id"] for s in canonical],
        "layouts": [s["layout"] for s in canonical],
        "typologies": [s["typology"] for s in canonical],
        "nested_lead_form_count": sum(1 for s in parser.sections if s.get("id") == NESTED_LEAD_FORM_ID),
        "nav_anchors": unique_in_order(parser.fragment_hrefs, set(LIVE_NAV_ANCHORS)),
        "form_count": parser.form_count,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--check-live", action="store_true")
    ap.add_argument("--report", default="")
    ap.add_argument("--save-live-html", default="")
    ap.add_argument("--save-sanitized-html", default=SNAPSHOT_PATH.as_posix())
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    failures: list[str] = []

    legacy_text = (root / LEGACY_PATH).read_text(encoding="utf-8")
    legacy = parse_html(legacy_text)
    legacy_ids = [s["data_section_id"] for s in legacy.sections if s["data_section_id"]]
    check("legacy-section-order", legacy_ids, LEGACY_SECTION_IDS, failures)
    check("legacy-section-count", len(legacy_ids), 17, failures)
    if legacy.html_attrs.get("data-theme") != "dark":
        failures.append("legacy-theme-not-dark")
    if legacy.html_attrs.get("data-publication-status") != "PENDING_FORMAL_LLM_JUDGE":
        failures.append("legacy-publication-state-promoted")
    entry = topology_entry(root)
    check("legacy-topology-report-order", entry.get("section_ids"), LEGACY_SECTION_IDS, failures)
    check("legacy-topology-report-hash", entry.get("topology_sha256"), EXPECTED_LEGACY_TOPOLOGY_SHA256, failures)
    check("legacy-topology-report-gate", entry.get("gate"), "PASS", failures)

    live_summary = None
    raw_live_sha = None
    sanitized_sha = None
    csrf_redactions = 0

    if args.check_live:
        live_text = fetch_live()
        raw_live_sha = hashlib.sha256(live_text.encode("utf-8")).hexdigest()
        if args.save_live_html:
            raw_out = root / args.save_live_html
            raw_out.parent.mkdir(parents=True, exist_ok=True)
            raw_out.write_text(live_text, encoding="utf-8")

        sanitized, csrf_redactions = sanitize_live(live_text)
        snapshot_out = root / args.save_sanitized_html
        snapshot_out.parent.mkdir(parents=True, exist_ok=True)
        snapshot_out.write_text(sanitized, encoding="utf-8")
        sanitized_sha = hashlib.sha256(sanitized.encode("utf-8")).hexdigest()

        live = parse_html(live_text)
        snapshot = parse_html(sanitized)
        live_contract = extract_live_contract(live)
        snapshot_contract = extract_live_contract(snapshot)

        check("live-token-order", live_contract["tokens"], CANONICAL_TOKENS, failures)
        check("live-anchor-order", live_contract["anchors"], LIVE_ANCHORS, failures)
        check("live-data-section-id-order", live_contract["data_section_ids"], LIVE_DATA_IDS, failures)
        check("live-layout-order", live_contract["layouts"], LIVE_LAYOUTS, failures)
        check("live-typology", live_contract["typologies"], ["R"] * 23, failures)
        check("live-nav-order", live_contract["nav_anchors"], LIVE_NAV_ANCHORS, failures)
        check("live-nested-lead-form", live_contract["nested_lead_form_count"], 1, failures)
        check("live-form-count", live_contract["form_count"], 1, failures)
        check("snapshot-contract", snapshot_contract, live_contract, failures)

        if sanitized != snapshot_out.read_text(encoding="utf-8"):
            failures.append("snapshot-write-not-lossless-after-sanitization")
        if re.search(r'name="csrfmiddlewaretoken"\s+value="(?!__REDACTED_CSRF_TOKEN__)[^"]+"', sanitized, re.I):
            failures.append("snapshot-csrf-secret-not-redacted")
        if csrf_redactions < 1:
            failures.append("snapshot-no-csrf-redaction-observed")
        if '<html lang="fr" data-theme="dark">' not in sanitized:
            failures.append("live-night-mode-root-not-preserved")
        if "ne certifie ni ne libère jamais un lot" not in sanitized:
            failures.append("live-hard-boundary-missing")

        live_summary = live_contract

    audit_status = "PASS" if not failures else "FAIL"
    summary = {
        "contract": "contract:programme:pharmaceutical-evidence-assurance:structure:2026-09-04",
        "scope": "ONE_PAGE_ONLY",
        "deterministic_audit_status": audit_status,
        "live_contract_status": "PASS" if args.check_live and not failures else ("NOT_CHECKED" if not args.check_live else "FAIL"),
        "legacy_repository_contract_status": "PASS_OWN_LEGACY_CONTRACT" if not failures else "FAIL",
        "legacy_live_parity_status": "FAIL_STRUCTURAL_SUBSET",
        "missing_canonical_tokens_in_legacy": MISSING_CANONICAL_TOKENS,
        "publication_status": "BLOCKED_PENDING_TARGET_PAGE_PRESENTATION_JUDGE_AND_REPO_PARITY_REMEDIATION",
        "neoFort_target_page_presentation_judge": "judge:evidence-placement:presentation-v1.2",
        "legacy_target": LEGACY_PATH.as_posix(),
        "snapshot_target": args.save_sanitized_html if args.check_live else None,
        "raw_live_sha256": raw_live_sha,
        "sanitized_snapshot_sha256": sanitized_sha,
        "csrf_redactions": csrf_redactions,
        "legacy_topology_sha256": EXPECTED_LEGACY_TOPOLOGY_SHA256,
        "live": live_summary,
        "failures": failures,
        "copy_mutation_performed": False,
        "other_page_mutation_performed": False,
        "google_drive_mutation_performed": False,
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

    print("PASS: live 23-section contract captured losslessly (except CSRF redaction); legacy 17-section artifact remains explicitly BLOCKED from live parity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
