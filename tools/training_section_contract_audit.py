#!/usr/bin/env python3
"""Fail-closed structural audit for /expertises/training/.

Scope is deliberately narrow. It validates the current repository reconstruction,
the live-contract XML extraction, and the contract-aligned review candidate. It
does not claim evidentiary publication PASS and does not mutate Google Drive.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "expertises" / "training"
CURRENT = BASE / "training.html"
CANDIDATE = BASE / "training.contract-aligned.candidate.html"
CONTRACT = BASE / "training.section-contract.xml"
LIVE_XML = BASE / "training.live.structure.xml"
REPO_XML = BASE / "training.repo.structure.xml"
REPORT = ROOT / "reports" / "training-section-contract-audit.json"

EXPECTED_NAV = [
    "triggers", "consequences", "for-whom", "qualification", "proposition",
    "offers", "deliverables", "before-after", "results", "proof", "scope",
    "process", "modules", "intersection", "commitments", "questions", "engagement",
]
EXPECTED_CANDIDATE_SECTIONS = [
    "triggers", "consequences", "for-whom", "qualification", "proposition", "value",
    "offers", "deliverables", "transformation", "before-after", "results", "proof",
    "scope", "process", "modules", "capabilities", "intersection", "benchmark",
    "commitments", "questions", "engagement",
]
EXPECTED_REPO_SECTIONS = EXPECTED_NAV.copy()
EXPECTED_MISSING_FROM_REPO = ["value", "transformation", "capabilities", "benchmark"]
EXPECTED_TOKENS = [0, 11, 20, 13, 14, 1, 2, 10, 15, 3, 12, 19, 4, 16, 17, 18, 5, 21, 6, 22, 23, 7]

SECTION_TAG_RE = re.compile(r"<section\b([^>]*)>", re.I)
NAV_BLOCK_RE = re.compile(r"<nav\b[^>]*>(.*?)</nav\s*>", re.I | re.S)
HREF_RE = re.compile(r"href\s*=\s*(?:[\"']#([^\"']+)[\"']|#([^\s>]+))", re.I)
ATTR_RE = re.compile(r"\b([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.I)


def read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def attrs(fragment: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in ATTR_RE.finditer(fragment):
        out[m.group(1).lower()] = next(x for x in m.groups()[1:] if x is not None)
    return out


def section_ids(html: str) -> list[str]:
    ids: list[str] = []
    for m in SECTION_TAG_RE.finditer(html):
        sid = attrs(m.group(1)).get("id")
        if sid:
            ids.append(sid)
    return ids


def nav_ids(html: str) -> list[str]:
    m = NAV_BLOCK_RE.search(html)
    if not m:
        return []
    out: list[str] = []
    for x in HREF_RE.finditer(m.group(1)):
        out.append(x.group(1) or x.group(2))
    return out


def section_tokens(html: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for m in SECTION_TAG_RE.finditer(html):
        a = attrs(m.group(1))
        if "id" in a and "data-section-token" in a:
            out.append((int(a["data-section-token"]), a["id"]))
    return out


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    failures: list[str] = []
    checks: dict[str, object] = {}
    try:
        current = read(CURRENT)
        candidate = read(CANDIDATE)
        contract_root = ET.parse(CONTRACT).getroot()
        live_root = ET.parse(LIVE_XML).getroot()
        repo_root = ET.parse(REPO_XML).getroot()

        current_sections = section_ids(current)
        candidate_sections = section_ids(candidate)
        candidate_nav = nav_ids(candidate)
        token_pairs = section_tokens(candidate)
        token_values = [x[0] for x in token_pairs]
        token_ids = [x[1] for x in token_pairs]

        assert_equal(current_sections, EXPECTED_REPO_SECTIONS, "current repository 17-section subset")
        assert_equal(candidate_sections, EXPECTED_CANDIDATE_SECTIONS, "candidate semantic section order")
        assert_equal(candidate_nav, EXPECTED_NAV, "candidate navigation order")
        assert_equal(token_values, EXPECTED_TOKENS[1:], "candidate canonical tokens after hero")
        assert_equal(token_ids, EXPECTED_CANDIDATE_SECTIONS, "candidate token/id binding")

        if 'id="hero"' not in candidate or 'data-section-token="0"' not in candidate:
            raise AssertionError("candidate hero/token 0 missing")
        if 'data-publication-status="BLOCKED_REVIEW"' not in candidate:
            raise AssertionError("candidate must remain BLOCKED_REVIEW")
        if '<meta name="robots" content="noindex,nofollow">' not in candidate:
            raise AssertionError("candidate must remain noindex,nofollow")
        if '"agent_exploitable":false' not in candidate:
            raise AssertionError("candidate agent_exploitable must be false")
        if 'judge:evidence-placement:presentation-v1.2' not in candidate:
            raise AssertionError("current NeoFort placement judge id missing")
        if 'google_drive_mutation":false' not in candidate:
            raise AssertionError("Drive mutation invariant missing")

        slots = contract_root.find("slots")
        if slots is None:
            raise AssertionError("contract slots missing")
        contract_ids = [x.attrib["id"] for x in slots.findall("slot")]
        assert_equal(contract_ids, ["hero"] + EXPECTED_CANDIDATE_SECTIONS, "contract slot ids")
        if slots.attrib.get("expected-count") != "22":
            raise AssertionError("contract expected-count must be 22")
        if slots.attrib.get("omitted-token") != "8":
            raise AssertionError("lead_form token 8 omission must be explicit")

        live_sections = live_root.find("sections")
        if live_sections is None:
            raise AssertionError("live XML sections missing")
        live_ids = [x.attrib["id"] for x in live_sections.findall("section")]
        assert_equal(live_ids, ["hero"] + EXPECTED_CANDIDATE_SECTIONS, "live XML slot ids")

        repo_sections_node = repo_root.find("sections")
        if repo_sections_node is None:
            raise AssertionError("repo XML sections missing")
        repo_ids = [x.attrib["id"] for x in repo_sections_node.findall("section")]
        assert_equal(repo_ids, EXPECTED_REPO_SECTIONS, "repo XML ids")
        delta = repo_root.find("delta-against-live")
        if delta is None:
            raise AssertionError("repo XML delta missing")
        missing = [x.attrib["id"] for x in delta.findall("missing")]
        assert_equal(missing, EXPECTED_MISSING_FROM_REPO, "documented repo/live delta")

        # Section-form sentinels: structural anatomy, not visual styling.
        sentinels = {
            "for-whom": ["HYPOTHÈSE À VALIDER", "Unité de décision"],
            "value": ["Ce que ça change", "Décision", "Risque", "Transfert", "Preuve"],
            "deliverables": ["Matrice compétence/tâche", "Matrice humain/IA", "Protocole de transfert"],
            "transformation": ["L'état d'arrivée"],
            "results": ["critères d'acceptation", "Aucun taux de transfert"],
            "capabilities": ["82/100", "Première date défendable: 2021"],
            "benchmark": ["Repère marché", "pas un prix contractuel"],
            "commitments": ["Garantir le produit de travail", "Non garantis"],
            "engagement": ["Évaluer le mandat en 20 minutes", "BLOCKED_REVIEW"],
        }
        for sid, needles in sentinels.items():
            start = candidate.find(f'id="{sid}"')
            if start < 0:
                raise AssertionError(f"missing sentinel section {sid}")
            next_section = candidate.find('<section id="', start + 1)
            fragment = candidate[start:] if next_section < 0 else candidate[start:next_section]
            for needle in needles:
                if needle not in fragment:
                    raise AssertionError(f"section {sid}: missing form sentinel {needle!r}")

        checks = {
            "current_repo_sections": len(current_sections),
            "candidate_semantic_slots": 1 + len(candidate_sections),
            "candidate_nav_anchors": len(candidate_nav),
            "canonical_tokens_present": [0] + token_values,
            "documented_missing_repo_slots": EXPECTED_MISSING_FROM_REPO,
            "lead_form_token_8": "JUSTIFIED_OMISSION_LIVE_DETAIL_PAGE",
            "devicev_publication": "BLOCKED_REVIEW",
            "formal_llm_triplicate_judge": "NOT_EXECUTED_BY_THIS_WORKFLOW",
            "google_drive_mutation": False,
            "status": "PASS_STRUCTURE_CONTRACT_ONLY",
        }
    except Exception as exc:  # fail closed
        failures.append(str(exc))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "page": "https://mickael-umt.com/expertises/training/",
        "scope": "training-only",
        "checks": checks,
        "failures": failures,
        "final_pass": not failures,
        "publication_pass": False,
        "publication_note": "Structural PASS cannot substitute for DEVICEV/NeoFort evidence and placement judges.",
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failures:
        print("FAIL: training section contract")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: 22 semantic slots (17 nav anchors + 4 non-nav sections + hero); repo delta documented; publication remains BLOCKED_REVIEW")
    return 0


if __name__ == "__main__":
    sys.exit(main())
