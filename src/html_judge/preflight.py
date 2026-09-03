from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCKING = (
    "PENDING",
    "BLOCKED",
    "REVIEW_ONLY",
    "REVIEW_ARTIFACT",
    "NOT_PUBLISHED",
    "DRAFT_NOT_AUTHORIZED",
    "REVIEW_FAIL_CLOSED",
)
PASS_MARKERS = ("FORMAL_PUBLICATION_PASS", "PUBLICATION_PASS")
STATUS_PATTERNS = (
    r'data-publication-status=["\']?([^"\' >]+)',
    r'x-publication-status["\']?\s+content=["\']([^"\']+)',
    r'artifact-status["\']?\s+content=["\']([^"\']+)',
    r'x-evidence-status["\']?\s+content=["\']([^"\']+)',
)


def status_values(text: str) -> list[str]:
    out: list[str] = []
    for pattern in STATUS_PATTERNS:
        out.extend(m.group(1) for m in re.finditer(pattern, text, re.I))
    return sorted(set(out))


def main() -> int:
    records = []
    contradictions = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        upper = text.upper()
        statuses = status_values(text)
        blocked_tokens = sorted({token for token in BLOCKING if token in upper})
        pass_asserted = any(marker in upper for marker in PASS_MARKERS)
        record = {
            "path": str(path.relative_to(ROOT)),
            "bytes": len(text.encode("utf-8")),
            "statuses": statuses,
            "noindex": "NOINDEX" in upper,
            "evidence_bubble_count": text.count("lp-evidence-bubble-scroll"),
            "blocking_tokens": blocked_tokens,
            "formal_pass_asserted": pass_asserted,
        }
        records.append(record)
        if pass_asserted and blocked_tokens:
            contradictions.append(
                {
                    "path": record["path"],
                    "reason": "formal publication PASS is asserted while fail-closed blocking tokens remain",
                    "blocking_tokens": blocked_tokens,
                }
            )

    report = {
        "html_count": len(records),
        "formal_pass_contradiction_count": len(contradictions),
        "records": records,
        "contradictions": contradictions,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Fail only on a logically impossible publication state. Review/blocked artifacts are valid
    # fail-closed states and therefore do not make the deterministic preflight itself fail.
    return 1 if contradictions else 0


if __name__ == "__main__":
    sys.exit(main())
