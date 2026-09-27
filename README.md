# tPBM cognition and EEG reproducibility repository

The release package is in [`tpbm_reproducibility_release_v1.0/`](tpbm_reproducibility_release_v1.0/). Its README describes the 17-cohort cognitive models, non-pooled EEG audit, recorded outputs, and Windows rerun instructions.

This repository is a **private release candidate**. The numerical snapshot was frozen on 19 September 2026. The manuscript and supplementary materials are maintained separately; the package crosswalk must be checked against their final submission versions.

## Archival sequence

1. Resolve the license and redistribution questions identified in the package's `LICENSE_TO_SET_BEFORE_PUBLIC_DEPOSIT.md`.
2. Obtain the authors' approval of the exact public snapshot and confirm the final manuscript-to-output map.
3. Run `validate_release.py` and, on Windows with R and Python available, `RUN_ALL.ps1` from the package directory. The existing `Environment/final_QA.json` records the earlier verification; it does not substitute for a fresh release check.
4. Make this repository public and connect it to Zenodo under the repository owner's account.
5. Publish a tagged GitHub release from the reviewed commit. Verify the Zenodo record, archive, creator metadata, and assigned version DOI before adding the DOI to the manuscript.

Do not cite the mutable `main` branch as the permanent version. The GitHub release and its Zenodo DOI identify the frozen snapshot.
