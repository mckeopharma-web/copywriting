from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

BLOCKING_GATES = (
    "question_answered",
    "metric_contract_complete",
    "source_admissible",
    "source_provenance_complete",
    "definition_stable_or_harmonized",
    "unit_dimension_valid",
    "population_geography_compatible",
    "temporal_alignment_valid",
    "missingness_explicit",
    "deduction_reproducible",
    "no_hidden_model_or_forecast",
    "no_unsupported_causality",
    "chart_encoding_truthful",
    "observed_derived_distinguished",
    "uncertainty_not_invented",
    "conclusion_entailed_by_data",
    "provenance_manifest_complete",
)

ALLOWED_EPISTEMIC = {"OBSERVED", "DERIVED_DETERMINISTIC"}
ALLOWED_MODES = {"FETCH_SOURCE_GRAPH", "REBUILD_FROM_SOURCE_DATA", "DERIVE_ORIGINAL"}
REQUIRED_FORBIDDEN = {
    "unsupported_causality",
    "hidden_extrapolation",
    "undeclared_interpolation",
    "silent_imputation",
}


def _fail(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def validate(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if doc.get("schema_version") != "2.0":
        _fail(errors, "schema_version", "must be 2.0")
    if doc.get("reasoning_mode") != "DEDUCTIVE":
        _fail(errors, "reasoning_mode", "QG-EU v2 is deductive only")

    mode = doc.get("production", {}).get("mode")
    if mode not in ALLOWED_MODES:
        _fail(errors, "production.mode", f"unsupported mode: {mode}")

    question = doc.get("question", {})
    if question.get("causal_intent") is True:
        _fail(errors, "question.causal_intent", "causal questions must route out of deductive QG-EU")

    metric = doc.get("metric_contract", {})
    for key in (
        "subject",
        "variable",
        "statistic_type",
        "unit",
        "population",
        "geography",
        "frequency",
        "aggregation",
    ):
        if not metric.get(key):
            _fail(errors, f"metric_contract.{key}", "required")

    series_by_id: dict[str, dict[str, Any]] = {}
    for series in doc.get("series", []):
        sid = series.get("id")
        if not sid:
            _fail(errors, "series[].id", "required")
            continue
        series_by_id[sid] = series
        for obs in series.get("observations", []):
            status = obs.get("epistemic_status")
            if status not in ALLOWED_EPISTEMIC:
                _fail(errors, f"{sid}/{obs.get('id')}", f"invalid epistemic status {status}")
            if status == "OBSERVED" and not obs.get("source_ref"):
                _fail(errors, f"{sid}/{obs.get('id')}.source_ref", "observed point requires source_ref")
            if obs.get("unit") != series.get("unit"):
                _fail(errors, f"{sid}/{obs.get('id')}.unit", "must match parent series unit")
            if obs.get("population") != series.get("population"):
                _fail(errors, f"{sid}/{obs.get('id')}.population", "must match parent series population")
            if obs.get("geography") != series.get("geography"):
                _fail(errors, f"{sid}/{obs.get('id')}.geography", "must match parent series geography")

    deriv = doc.get("derivation", {})
    if deriv.get("reasoning_mode") != "DEDUCTIVE":
        _fail(errors, "derivation.reasoning_mode", "must be DEDUCTIVE")
    forbidden = set(deriv.get("forbidden_inferences", []))
    if not REQUIRED_FORBIDDEN.issubset(forbidden):
        missing = sorted(REQUIRED_FORBIDDEN - forbidden)
        _fail(errors, "derivation.forbidden_inferences", f"missing {missing}")
    for sid in deriv.get("input_series_ids", []):
        if sid not in series_by_id:
            _fail(errors, "derivation.input_series_ids", f"unknown series {sid}")

    answer = doc.get("answer", {})
    if answer.get("epistemic_status") not in ALLOWED_EPISTEMIC:
        _fail(errors, "answer.epistemic_status", "invalid for deductive QG-EU")
    if answer.get("causal_language_allowed") is not False:
        _fail(errors, "answer.causal_language_allowed", "must be false")

    graph = doc.get("graph", {})
    for sid in graph.get("series_ids", []):
        if sid not in series_by_id:
            _fail(errors, "graph.series_ids", f"unknown series {sid}")
    if graph.get("y_scale") == "log":
        for sid in graph.get("series_ids", []):
            for obs in series_by_id.get(sid, {}).get("observations", []):
                if obs.get("value", 0) <= 0:
                    _fail(errors, "graph.y_scale", "log scale requires strictly positive rendered values")
    if len(graph.get("series_ids", [])) == 1:
        sid = graph["series_ids"][0]
        n = len(series_by_id.get(sid, {}).get("observations", []))
        if n == 2 and graph.get("chart_type") == "line":
            _fail(errors, "graph.chart_type", "two points should not imply an unobserved continuous path; prefer slope")

    candidates = doc.get("retrieval", {}).get("candidates", [])
    selected = doc.get("retrieval", {}).get("selected_candidate_id")
    selected_rows = [c for c in candidates if c.get("id") == selected]
    if len(selected_rows) != 1:
        _fail(errors, "retrieval.selected_candidate_id", "must resolve to exactly one candidate")
    elif not selected_rows[0].get("hard_gate_pass"):
        _fail(errors, "retrieval.selected_candidate_id", "selected candidate failed a hard gate")
    for candidate in candidates:
        if not candidate.get("hard_gate_pass") and candidate.get("score") is not None:
            _fail(errors, f"candidate:{candidate.get('id')}.score", "scoring forbidden before hard gates pass")

    gate = doc.get("quality_gate", {})
    false_gates = [name for name in BLOCKING_GATES if gate.get(name) is not True]
    if false_gates:
        _fail(errors, "quality_gate", "blocking gates false: " + ", ".join(false_gates))
    expected_status = "PASS" if not false_gates else "FAIL"
    if gate.get("status") != expected_status:
        _fail(errors, "quality_gate.status", f"must be {expected_status}")

    scalar = deriv.get("scalar_outputs", {})
    if scalar and len(deriv.get("input_series_ids", [])) == 1:
        observations = series_by_id[deriv["input_series_ids"][0]].get("observations", [])
        if len(observations) >= 2:
            x0, x1 = observations[0]["value"], observations[-1]["value"]
            if x0 == 0:
                _fail(errors, "derivation", "baseline zero invalid for ratio/percentage change")
            else:
                ratio = x1 / x0
                pct = 100 * (x1 - x0) / x0
                if "ratio" in scalar and not math.isclose(float(scalar["ratio"]), ratio, rel_tol=1e-12):
                    _fail(errors, "derivation.scalar_outputs.ratio", "does not reproduce from observations")
                if "percent_change" in scalar and not math.isclose(float(scalar["percent_change"]), pct, rel_tol=1e-12):
                    _fail(errors, "derivation.scalar_outputs.percent_change", "does not reproduce from observations")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate QG-EU v2 JSON documents")
    parser.add_argument("--root", type=Path, default=Path("examples/qgeu"))
    args = parser.parse_args()

    files = sorted(args.root.rglob("*.qgeu.json"))
    if not files:
        print(f"FAIL: no *.qgeu.json under {args.root}")
        return 2

    failed = False
    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        errors = validate(doc)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
