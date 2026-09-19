"""Compare a fresh rerun with the frozen numerical outputs."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def numeric(value: str):
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def compare_csv(recorded: Path, rerun: Path, tolerance: float = 3e-6) -> None:
    expected = read_csv(recorded)
    observed = read_csv(rerun)
    if len(expected) != len(observed):
        raise AssertionError(f"Row-count mismatch for {recorded.name}: {len(expected)} != {len(observed)}")
    if expected and expected[0].keys() != observed[0].keys():
        raise AssertionError(f"Column mismatch for {recorded.name}")
    for row_number, (left, right) in enumerate(zip(expected, observed), start=2):
        for column in left:
            a, b = left[column], right[column]
            na, nb = numeric(a), numeric(b)
            if na is not None and nb is not None:
                if abs(na - nb) > tolerance:
                    raise AssertionError(
                        f"Numeric mismatch {recorded.name} row {row_number} {column}: {na} vs {nb}"
                    )
            elif a != b:
                raise AssertionError(
                    f"Text mismatch {recorded.name} row {row_number} {column}: {a!r} vs {b!r}"
                )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--rerun", required=True, type=Path)
    args = parser.parse_args()

    cognition_files = [
        "model_results.csv",
        "moderators.csv",
        "small_study.csv",
        "PET_PEESE.csv",
        "trimfill.csv",
        "selection.csv",
        "multilevel.csv",
        "LOO_Overall_cognition.csv",
        "LOO_Memory.csv",
        "LOO_Global_cognition.csv",
        "LOO_Executive_sustained_attention.csv",
    ]
    for name in cognition_files:
        compare_csv(
            args.release / "Cognition" / "Recorded_Outputs" / name,
            args.rerun / "Cognition" / "Outputs" / name,
        )

    eeg_files = [
        "EEG_cluster_inventory.csv",
        "EEG_compatibility_gates.csv",
        "EEG_effect_reconstruction_checks.csv",
        "EEG_exclusion_sensitivity_inventory.csv",
        "EEG_study_level_estimates.csv",
        "EEG_Chaudhari_sample_size_sensitivity.csv",
        "EEG_Chaudhari_sensitivity_intervals.csv",
        "EEG_independent_R_checks.csv",
    ]
    for name in eeg_files:
        compare_csv(
            args.release / "EEG" / "Recorded_Outputs" / name,
            args.rerun / "EEG" / "Outputs" / name,
            tolerance=1e-7,
        )

    expected_summary = json.loads(
        (args.release / "EEG" / "Recorded_Outputs" / "EEG_audit_summary.json").read_text(encoding="utf-8")
    )
    observed_summary = json.loads(
        (args.rerun / "EEG" / "Outputs" / "EEG_audit_summary.json").read_text(encoding="utf-8")
    )
    if expected_summary != observed_summary:
        raise AssertionError("EEG audit summary mismatch")

    model_rows = {row["model"]: row for row in read_csv(args.rerun / "Cognition" / "Outputs" / "model_results.csv")}
    expected = {
        "primary__Overall cognition": (17, 0.380327280084903),
        "primary__Memory": (7, 0.251222282609883),
        "primary__Global cognition": (5, 0.398711445334661),
        "primary__Executive / sustained attention": (3, 0.617307059781905),
    }
    for model, (k, estimate) in expected.items():
        row = model_rows[model]
        if int(row["k"]) != k or abs(float(row["g"]) - estimate) > 3e-6:
            raise AssertionError(f"Principal result mismatch: {model}")

    print("VALIDATION PASSED: cognition and EEG numerical outputs match the frozen release.")


if __name__ == "__main__":
    main()
