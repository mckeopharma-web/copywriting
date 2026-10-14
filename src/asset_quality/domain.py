"""Domain model for cross-asset offer assurance.

The commercial surface owns offer semantics. This module does not edit pages and
it does not know ERPNext, Django or GitHub APIs. It only evaluates immutable
manifest data against deterministic invariants.

Variance is deliberate:

* ``AssetSource[T_co]`` is covariant because a source that returns a specialised
  manifest can be used wherever a base manifest source is expected.
* ``AssetRule[T_contra]`` is contravariant because a rule able to validate a
  base asset can validate any specialised asset.

That keeps extension open without weakening the closed invariants below.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar
from urllib.parse import urlparse

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class AssetSource(Protocol[T_co]):
    def load(self) -> T_co: ...


class AssetRule(Protocol[T_contra]):
    def validate(self, asset: T_contra) -> tuple["Finding", ...]: ...


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class OfferAsset:
    asset_id: str
    asset_kind: str
    source_path: str
    canonical_url: str
    manifest: dict[str, Any]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "OfferAsset":
        return cls(
            asset_id=str(payload.get("asset_id", "")).strip(),
            asset_kind=str(payload.get("asset_kind", "")).strip(),
            source_path=str(payload.get("source_path", "")).strip(),
            canonical_url=str(payload.get("canonical_url", "")).strip(),
            manifest=payload,
        )


class IdentityRule(Generic[T_contra]):
    """Primary-key and canonical-location invariants."""

    allowed_prefixes = ("offer.", "programme.", "expertise.", "page.")

    def validate(self, asset: OfferAsset) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        if not asset.asset_id.startswith(self.allowed_prefixes):
            findings.append(Finding("AQ-ID-001", "error", "asset_id is not a canonical commercial primary key"))
        if asset.asset_kind not in {"offer", "programme", "expertise", "page"}:
            findings.append(Finding("AQ-ID-002", "error", f"unsupported asset_kind={asset.asset_kind!r}"))
        parsed = urlparse(asset.canonical_url)
        if parsed.scheme != "https" or parsed.netloc != "mickael-umt.com":
            findings.append(Finding("AQ-ID-003", "error", "canonical_url must be on https://mickael-umt.com/"))
        if not asset.source_path:
            findings.append(Finding("AQ-ID-004", "error", "source_path is required"))
        return tuple(findings)


class ValueEquationRule(Generic[T_contra]):
    """Deterministic controls around the five offer-quality dimensions.

    The equation is used as a quality decomposition, not as a numeric claim. The
    gate therefore checks that each dimension is explicit and evidence-bounded.
    """

    def validate(self, asset: OfferAsset) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        value = asset.manifest.get("value_equation") or {}
        required = (
            "dream_outcome",
            "perceived_likelihood",
            "time_delay",
            "effort_sacrifice",
            "risk_reversal",
        )
        missing = [name for name in required if not isinstance(value.get(name), dict)]
        if missing:
            return (Finding("AQ-VAL-001", "error", f"missing offer-quality dimensions: {', '.join(missing)}"),)

        dream = value["dream_outcome"]
        if not str(dream.get("statement", "")).strip():
            findings.append(Finding("AQ-VAL-002", "error", "dream outcome must be stated explicitly"))
        if not dream.get("evidence_refs"):
            findings.append(Finding("AQ-VAL-003", "error", "dream outcome has no evidence reference"))

        likelihood = value["perceived_likelihood"]
        coverage = likelihood.get("evidence_coverage")
        target = (asset.manifest.get("quality_targets") or {}).get("evidence_coverage_min")
        if not isinstance(coverage, (int, float)):
            findings.append(Finding("AQ-VAL-004", "error", "evidence_coverage must be numeric"))
        elif isinstance(target, (int, float)) and coverage < target:
            findings.append(
                Finding(
                    "AQ-VAL-005",
                    "warning",
                    f"evidence coverage {coverage:.2f} is below target {target:.2f}; open/retain CAPA",
                )
            )
        if int(likelihood.get("evidence_unit_count", 0)) > 0 and not likelihood.get("evidence_refs"):
            findings.append(Finding("AQ-VAL-006", "error", "evidence units are counted but not referenced"))

        delay = value["time_delay"]
        if not str(delay.get("full_outcome", "")).strip():
            findings.append(Finding("AQ-VAL-007", "error", "full outcome delay must be explicit"))
        if not delay.get("first_verified_value"):
            findings.append(Finding("AQ-VAL-008", "warning", "first verified value is not yet defined"))

        effort = value["effort_sacrifice"]
        if not effort.get("client_inputs"):
            findings.append(Finding("AQ-VAL-009", "error", "client effort must list required inputs/dependencies"))
        if not effort.get("estimated_commitment"):
            findings.append(Finding("AQ-VAL-010", "warning", "client commitment is not yet measured"))

        reversal = value["risk_reversal"]
        controlled = tuple(str(v).lower() for v in reversal.get("controlled_commitments") or [])
        excluded = tuple(str(v).lower() for v in reversal.get("excluded_outcomes") or [])
        if reversal.get("guarantee_type") != "none" and not controlled:
            findings.append(Finding("AQ-VAL-011", "error", "a guarantee requires explicit controllable commitments"))
        forbidden = ("regulatory compliance", "revenue", "customer outcome", "production decision")
        for phrase in forbidden:
            if any(phrase in item for item in controlled) and not any(phrase in item for item in excluded):
                findings.append(
                    Finding(
                        "AQ-VAL-012",
                        "error",
                        f"uncontrolled outcome appears guaranteed without an explicit exclusion: {phrase}",
                    )
                )
        return tuple(findings)


class MeshRule(Generic[T_contra]):
    """Cross-domain references use canonical IDs; runtime IDs never enter the manifest."""

    def validate(self, asset: OfferAsset) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        mesh = asset.manifest.get("mesh") or {}
        for field in ("programme_ids", "learning_program_ids", "capability_ids", "app_tool_ids"):
            values = mesh.get(field)
            if not isinstance(values, list):
                findings.append(Finding("AQ-MESH-001", "error", f"mesh.{field} must be a list"))
                continue
            if len(values) != len(set(values)):
                findings.append(Finding("AQ-MESH-002", "error", f"mesh.{field} contains duplicate canonical IDs"))
            if any(str(value).startswith(("pk:", "db:", "runtime:")) for value in values):
                findings.append(Finding("AQ-MESH-003", "error", f"mesh.{field} contains a runtime identifier"))
        if mesh.get("mesh_status") == "complete" and asset.asset_kind == "programme" and not mesh.get("learning_program_ids"):
            findings.append(Finding("AQ-MESH-004", "error", "complete programme mesh requires a learning_program_id"))
        return tuple(findings)


DEFAULT_RULES: tuple[AssetRule[OfferAsset], ...] = (
    IdentityRule(),
    ValueEquationRule(),
    MeshRule(),
)


def validate_asset(asset: OfferAsset, *, repo_root: Path) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for rule in DEFAULT_RULES:
        findings.extend(rule.validate(asset))
    if asset.source_path and not (repo_root / asset.source_path).is_file():
        findings.append(Finding("AQ-ID-005", "error", f"source_path does not exist: {asset.source_path}"))
    return tuple(findings)
