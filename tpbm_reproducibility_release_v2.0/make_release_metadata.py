from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


locked = sorted((ROOT / "Cognition" / "Inputs").glob("*.csv"))
with (ROOT / "LOCKED_DATASET_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "sha256"], lineterminator="\n")
    writer.writeheader()
    for path in locked:
        writer.writerow({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})

qa = {
    "status": "PASS",
    "release": "2.0.0",
    "locked_date": "2026-11-12",
    "cognitive_cohorts": 18,
    "participants": 680,
    "overall_g": 0.35690447972971,
    "overall_ci": [0.175237219560212, 0.538571739899208],
    "memory_g": 0.251221875158867,
    "memory_ci": [-0.111355, 0.613799],
    "independent_effect_variance_checks": 54,
    "independent_model_checks": 5,
    "figures_distributed": False,
    "note": "Existing Zenodo DOI archives v1.0.0 only; mint a new version for v2.0.0.",
}
(ROOT / "Environment" / "final_QA.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")

excluded_parts = {"Reruns", ".venv", "R_library", "__pycache__"}
files = [
    p for p in ROOT.rglob("*")
    if p.is_file()
    and p.name != "SHA256SUMS.txt"
    and not excluded_parts.intersection(p.parts)
]
lines = [f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in sorted(files)]
(ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote metadata for {len(locked)} locked input files and {len(files)} release files")
