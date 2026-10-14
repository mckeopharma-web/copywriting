"""CLI for deterministic offer-assurance validation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .domain import OfferAsset, validate_asset


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_tree(*, root: Path, manifests_dir: Path, report_path: Path | None = None) -> dict:
    manifests = sorted(manifests_dir.glob("*.json"))
    seen: dict[str, str] = {}
    assets: list[dict] = []
    errors = 0
    warnings = 0

    for path in manifests:
        try:
            payload = _load(path)
        except Exception as exc:  # fail closed on malformed governed data
            errors += 1
            assets.append({"manifest": str(path), "status": "FAIL", "findings": [{"code": "AQ-JSON-001", "severity": "error", "message": str(exc)}]})
            continue

        asset = OfferAsset.from_mapping(payload)
        findings = list(validate_asset(asset, repo_root=root))
        previous = seen.get(asset.asset_id)
        if previous:
            findings.append({"code": "AQ-ID-006", "severity": "error", "message": f"duplicate asset_id also declared by {previous}"})
        else:
            seen[asset.asset_id] = str(path)

        normalized = []
        for finding in findings:
            if isinstance(finding, dict):
                row = finding
            else:
                row = {"code": finding.code, "severity": finding.severity, "message": finding.message}
            normalized.append(row)
            if row["severity"] == "error":
                errors += 1
            elif row["severity"] == "warning":
                warnings += 1

        assets.append(
            {
                "asset_id": asset.asset_id,
                "manifest": str(path.relative_to(root)),
                "source_path": asset.source_path,
                "status": "FAIL" if any(row["severity"] == "error" for row in normalized) else "PASS_WITH_WARNINGS" if normalized else "PASS",
                "findings": normalized,
            }
        )

    report = {
        "contract": "offer-assurance-v1",
        "status": "FAIL" if errors else "PASS",
        "registered_asset_count": len(manifests),
        "error_count": errors,
        "warning_count": warnings,
        "assets": assets,
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifests", default="quality/assets")
    parser.add_argument("--report", default="reports/offer-assurance-gate.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = validate_tree(
        root=root,
        manifests_dir=(root / args.manifests),
        report_path=(root / args.report),
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
