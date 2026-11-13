from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_csv(recorded: Path, rerun: Path, tolerance: float = 1e-9):
    expected, observed = rows(recorded), rows(rerun)
    if len(expected) != len(observed):
        raise AssertionError(f"Row-count mismatch: {recorded.name}: {len(expected)} != {len(observed)}")
    if expected and expected[0].keys() != observed[0].keys():
        raise AssertionError(f"Column mismatch: {recorded.name}")
    for index, (left, right) in enumerate(zip(expected, observed), start=2):
        for key in left:
            a, b = left[key], right[key]
            if a == b:
                continue
            try:
                fa, fb = float(a), float(b)
            except ValueError:
                raise AssertionError(f"Text mismatch {recorded.name}:{index}:{key}: {a!r} != {b!r}")
            if not (math.isfinite(fa) and math.isfinite(fb) and abs(fa - fb) <= tolerance * max(1.0, abs(fa), abs(fb))):
                raise AssertionError(f"Numeric mismatch {recorded.name}:{index}:{key}: {fa} != {fb}")


parser = argparse.ArgumentParser()
parser.add_argument("--release", type=Path, required=True)
parser.add_argument("--rerun", type=Path, required=True)
args = parser.parse_args()
release, rerun = args.release.resolve(), args.rerun.resolve()

manifest = rows(release / "LOCKED_DATASET_SHA256.csv")
for item in manifest:
    path = release / item["path"]
    if sha(path) != item["sha256"]:
        raise AssertionError(f"Locked input hash mismatch: {item['path']}")

recorded = release / "Cognition" / "Recorded_Outputs"
regenerated = rerun / "Cognition" / "Outputs"
for name in [
    "all_model_results.csv", "model_membership.csv", "moderators_Holm.csv",
    "multilevel_CR2.csv", "multilevel_grid_CR2.csv", "multilevel_variants_CR2.csv",
    "small_study_tests.csv", "trimfill_exploratory.csv", "MMSE_raw_MD.csv",
]:
    compare_csv(recorded / name, regenerated / name)

independent = json.loads((rerun / "Cognition" / "Logs" / "independent_validation.json").read_text(encoding="utf-8"))
if independent.get("status") != "PASS" or len(independent.get("effect_checks", [])) != 54 or len(independent.get("independent_REML_HK", [])) != 5:
    raise AssertionError("Independent v3 verification did not report 54 effect checks and five model checks")

result = {
    "status": "PASS",
    "locked_input_files": len(manifest),
    "cognition_csvs_compared": 9,
    "independent_effect_checks": 54,
    "independent_models": 5,
    "eeg_scope": "Unchanged public v1.0 audit; intentionally not rerun in the v2.0 cognition release",
}
(rerun / "validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("VALIDATION PASSED")
