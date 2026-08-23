#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
candidates = json.loads((ROOT / "data/candidate_register_15.json").read_text(encoding="utf-8"))
invariants = json.loads((ROOT / "data/publication_invariants.json").read_text(encoding="utf-8"))

lines = [
    "# Publication evidence summary",
    "",
    "Generated from machine-readable repository data.",
    "",
    "## Fixed publication counts",
    "",
]
for key, value in invariants.items():
    if isinstance(value, (str, int, bool)):
        lines.append(f"- **{key}**: `{value}`")

lines += [
    "",
    "## Candidate register",
    "",
    "| ID | Publication-facing title | Lane | Final disposition |",
    "|---|---|---|---|",
]
for row in candidates:
    lines.append(
        f"| {row['case_id']} | {row['publication_facing_title']} | "
        f"{row['lane']} | {row['final_disposition']} |"
    )

out = ROOT / "generated/PUBLICATION_EVIDENCE_SUMMARY.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out)
