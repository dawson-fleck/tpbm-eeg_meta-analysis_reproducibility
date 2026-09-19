# Reproducible EEG analysis package

Start with Analysis_Status_EEG_2026-09-16.md, then the Methods and Results drafts. All paths used by the scripts are relative to this folder; moving the whole EEG folder is supported.

Requirements: Python 3.10+ (standard library only), R 4.x (base R only). No Python/R add-on package or network access is required. Tested runtime versions are recorded in Outputs and run logs.

Run from any directory:

```text
python path/to/EEG/Scripts/run_eeg.py --rscript path/to/Rscript
```

If Rscript is on PATH, omit --rscript. The runner freezes source hashes, archives previous outputs, runs preparation, independent R verification/plots, and report generation, and writes PASS.txt only after all steps succeed and source hashes match. A successful run means the stated audit passed; it does not validate unresolved scientific assumptions.

- Reproducibility/Source_snapshots: frozen source records, never edited by the pipeline.
- Inputs: machine-readable original and audited effect tables.
- Outputs: study-level tables, compatibility gates, checks, sensitivity, figure panels and session information.
- Scripts: the complete workflow; both R and Python are intentional and reproducible together.
- Reproducibility/Runs: timestamped logs, prior-output archives and checksums.

No pooled model is fitted because no compatible family meets the protocol threshold. The numeric field eligible_for_new_pool is only a nonquarantine flag; always apply EEG_compatibility_gates.csv as well.

For a public GitHub repository, upload the scripts, README, environment/session record and suitable derived tables/figures. Review source snapshots for redistribution rights and private correspondence before publication; do not upload copyrighted full-text PDFs or private email records by default. If any input cannot be shared, provide a documented access/reconstruction route and clearly state that a public code-only repository cannot reproduce results without those inputs. Choose a license for your own code and cite the original studies/data separately. No GitHub upload has been performed.
