#!/usr/bin/env python3
"""Lossless, fail-closed sync/validator for /engagement/audiences/#avatar-training.

Only the Nadia Benali card may change. The script restores the public first-party
wording and target anchor, removes pending EvidenceUnit bindings from visible
copy, and proves that all other avatar cards and top-level page topology remain
byte-identical. It does not manufacture NeoFort semantic-judge PASS results.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "pages/engagement/audiences/mickael-umt.com.html"
LIVE_XML = ROOT / "engagement/audiences/audiences.live.structure.2026-09-04.xml"
REPO_XML = ROOT / "engagement/audiences/audiences.repo.structure.2026-09-04.xml"
PATCH_XML = ROOT / "engagement/audiences/avatar-training.patch.2026-09-04.xml"
CONTRACT_XML = ROOT / "contracts/expertises-programmes-section-contract-check-2026-09-04.xml"

EXPECTED_NAMES = [
    "Claire Dumas", "Marc Lefèvre", "Nadia Benali", "Dr. Antoine Moreau",
    "Sophie Lemercier", "Karim Benali", "Isabelle Fontaine", "Julien Rocher",
    "Élodie Marchand", "Camille Ferrand",
]
EXPECTED_MAIN_SECTIONS = ["decision-profiles", "audience-cards", "problem-before-profile", "qualifier"]
EXPECTED_LIVE_BEFORE = "L’usage de l’IA se diffuse déjà dans les équipes, mais elle ne peut ni démontrer les compétences acquises, ni prouver que les limites de confidentialité sont tenues."
EXPECTED_LIVE_AFTER = "Une capacité où les équipes savent quoi automatiser, quoi vérifier et quand escalader — avec la preuve par équipe qui rend la généralisation défendable devant la direction."
TARGET_CONTRACT = "contract:customer-avatar:audiences:2026-09-03"

CARD_RE = re.compile(r'<article class="card" id="([^"]+)"(?:\s+[^>]*)?>(.*?)</article>', re.S)
SECTION_RE = re.compile(r'<section\b[^>]*\bid="([^"]+)"[^>]*>', re.I)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def parse_xml(path: Path) -> ET.Element:
    if not path.exists():
        fail(f"missing contract artifact: {path.relative_to(ROOT)}")
    return ET.parse(path).getroot()


def card_map(html: str) -> dict[str, str]:
    return {cid: body for cid, body in CARD_RE.findall(html)}


def name_from_card(body: str) -> str:
    m = re.search(r"<h2>(.*?)</h2>", body, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def main_sections(html: str) -> list[str]:
    return SECTION_RE.findall(html)


def target_card() -> str:
    return (
        '<article class="card" id="avatar-training" '
        f'data-avatar-contract="{TARGET_CONTRACT}">'
        '<div class="head"><span class="no">03</span><div><h2>Nadia Benali</h2>'
        '<p class="role">Directrice transformation IA et formation · organisation régulée ou à fortes exigences de contrôle</p>'
        '</div></div><div class="states"><div class="st before"><span>Avant</span><p>'
        + EXPECTED_LIVE_BEFORE +
        '</p></div><div class="st after"><span>Après</span><p>' + EXPECTED_LIVE_AFTER +
        '</p></div></div><div class="offer"><div><a href="https://mickael-umt.com/ressources/produits/?role_key=training&amp;situation=adoption">Voir le parcours adapté →</a>'
        ' <a href="https://mickael-umt.com/expertises/training/">Voir la preuve utile à ce rôle →</a></div></div></article>'
    )


def replace_target(original: str) -> str:
    matches = list(CARD_RE.finditer(original))
    targets = [m for m in matches if name_from_card(m.group(2)) == "Nadia Benali"]
    if len(targets) != 1:
        fail(f"expected exactly one Nadia Benali card, got {len(targets)}")
    m = targets[0]
    return original[:m.start()] + target_card() + original[m.end():]


def validate_contract_artifacts() -> None:
    live = parse_xml(LIVE_XML)
    repo = parse_xml(REPO_XML)
    patch = parse_xml(PATCH_XML)
    canon = parse_xml(CONTRACT_XML)

    live_target = live.find("./AudienceCards/Avatar[@target='true']")
    if live_target is None or live_target.attrib.get("name") != "Nadia Benali":
        fail("live XML target avatar is not Nadia Benali")
    if live_target.attrib.get("id") != "avatar-training":
        fail("live XML target anchor must be avatar-training")
    if (live_target.findtext("Before") or "").strip() != EXPECTED_LIVE_BEFORE:
        fail("live XML target Before drifted")
    if (live_target.findtext("After") or "").strip() != EXPECTED_LIVE_AFTER:
        fail("live XML target After drifted")
    if live.find("TargetAvatarContract").attrib.get("id") != TARGET_CONTRACT:
        fail("live XML Customer Avatar contract drifted")

    repo_target = repo.find("./AudienceCards/Avatar[@target='true']")
    if repo_target is None or repo_target.attrib.get("name") != "Nadia Benali":
        fail("repository XML target avatar missing")
    if repo.findtext("./StandaloneTargetArtifact/CompatibilityWithLivePageTopology") != "NON_COMPLIANT_AS_PUBLIC_PAGE_REPLACEMENT":
        fail("standalone review-artifact boundary must remain explicit")

    selector = patch.find("Selector")
    if selector is None or selector.attrib.get("after") != "article#avatar-training":
        fail("patch selector does not resolve to avatar-training")
    if patch.find("AvatarContract").attrib.get("id") != TARGET_CONTRACT:
        fail("patch uses a non-current Customer Avatar contract")
    for eu in patch.findall("./EvidenceCandidates/EvidenceUnit"):
        if eu.attrib.get("publicationAllowed") == "true" or eu.attrib.get("action") != "DO_NOT_BIND_TO_VISIBLE_COPY":
            fail(f"pending evidence unexpectedly publishable: {eu.attrib.get('id')}")

    order = (canon.findtext("CanonicalSemanticOrder") or "").strip()
    if order != "0,11,20,13,14,1,2,10,15,3,12,19,4,16,17,18,5,21,6,22,23,7,8":
        fail("expertise/programme canonical semantic order drifted")
    observed = canon.findall("./ObservedDetailPages/Page")
    if len(observed) != 2 or any(p.find("LocalNavigation").attrib.get("anchorCount") != "17" for p in observed):
        fail("representative S/P detail-page 17-anchor contract missing")


def validate_html(original: str, updated: str) -> None:
    before_sections = main_sections(original)
    after_sections = main_sections(updated)
    if before_sections != after_sections:
        fail(f"top-level section topology changed: {before_sections} -> {after_sections}")
    if after_sections != EXPECTED_MAIN_SECTIONS:
        fail(f"unexpected audience section topology: {after_sections}")

    before_cards = card_map(original)
    after_cards = card_map(updated)
    if len(before_cards) != 10 or len(after_cards) != 10:
        fail(f"avatar-card count must stay 10: before={len(before_cards)} after={len(after_cards)}")

    before_names = [name_from_card(body) for _, body in CARD_RE.findall(original)]
    after_names = [name_from_card(body) for _, body in CARD_RE.findall(updated)]
    if before_names != EXPECTED_NAMES or after_names != EXPECTED_NAMES:
        fail(f"avatar order drifted: before={before_names}, after={after_names}")

    target_ids = [cid for cid, body in CARD_RE.findall(updated) if name_from_card(body) == "Nadia Benali"]
    if target_ids != ["avatar-training"]:
        fail(f"target anchor mismatch: {target_ids}")

    target_body = after_cards["avatar-training"]
    if EXPECTED_LIVE_BEFORE not in target_body or EXPECTED_LIVE_AFTER not in target_body:
        fail("target visible Before/After is not lossless with the live source")
    target_start = re.search(r'<article class="card" id="avatar-training"[^>]*>', updated)
    if target_start is None or TARGET_CONTRACT not in target_start.group(0):
        fail("target card does not carry current audiences Customer Avatar contract")
    if "data-eu=" in target_body or "popovertarget=" in target_body or "claim-eu-aud-004" in target_body or "claim-eu-aud-005" in target_body:
        fail("pending EvidenceUnit binding remains in target visible copy")
    if "ressources/produits/?role_key=training&amp;situation=adoption" not in target_body:
        fail("live path CTA missing from target card")
    if 'href="https://mickael-umt.com/expertises/training/"' not in target_body:
        fail("live proof CTA missing from target card")

    for name in EXPECTED_NAMES:
        if name == "Nadia Benali":
            continue
        before_id, before_body = next((cid, body) for cid, body in CARD_RE.findall(original) if name_from_card(body) == name)
        after_id, after_body = next((cid, body) for cid, body in CARD_RE.findall(updated) if name_from_card(body) == name)
        if before_id != after_id or sha256(before_body.encode()).digest() != sha256(after_body.encode()).digest():
            fail(f"non-target avatar mutated: {name}")

    for stable_fragment in ["problem-before-profile", 'id="qualifier"', "<footer"]:
        if stable_fragment not in updated:
            fail(f"required live structure fragment missing: {stable_fragment}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated target-only replacement")
    args = parser.parse_args()

    validate_contract_artifacts()
    if not HTML.exists():
        fail(f"missing target HTML: {HTML.relative_to(ROOT)}")
    original = HTML.read_text(encoding="utf-8")

    if 'id="avatar-training"' in original and EXPECTED_LIVE_BEFORE in original and EXPECTED_LIVE_AFTER in original:
        updated = original
    else:
        updated = replace_target(original)

    validate_html(original, updated)

    if args.apply and updated != original:
        HTML.write_text(updated, encoding="utf-8")
        print("APPLIED: lossless avatar-training sync; only Nadia Benali card changed.")
    else:
        print("VALIDATED: avatar-training contract; no write required." if updated == original else "VALIDATED: target-only patch is deterministic and ready to apply.")
    print("PASS: 4 top-level main sections, 10 ordered avatar cards, target anchor exactly once, non-target cards byte-stable.")
    print("PASS: visible target copy contains no draft/pending EvidenceUnit binding.")
    print("NOTE: semantic EvidencePlacement FINAL_PASS remains a separate NeoFort 3-replica gate for any future external evidence claim.")


if __name__ == "__main__":
    main()
