# tPBM cognition and EEG reproducibility repository

The release package is in [`tpbm_reproducibility_release_v1.0/`](tpbm_reproducibility_release_v1.0/). Its README describes the 17-cohort cognitive models, non-pooled EEG audit, recorded outputs, and Windows rerun instructions.

The numerical snapshot was frozen on 19 September 2026. The author team approved the release package, as confirmed by the corresponding author on 27 September 2026. The manuscript and supplementary materials are maintained separately; the package crosswalk must be checked against their final submission versions.

## Draft license scope

Original code: [MIT](LICENSE-CODE.md). Original tabular data and documentation: [CC BY 4.0](LICENSE-DATA.md). The author team approved these terms for the original material. Third-party rights are outside their scope.

## Archival sequence

1. Check the split-license scope in the package's `LICENSE_SCOPE.md` and the repository-root license files.
2. Confirm the release tag points to this approved snapshot and the final manuscript-to-output map.
3. The review team reports a successful prior run of `RUN_ALL.ps1`; `Environment/final_QA.json` records the archived numerical verification. If analysis inputs or scripts change beyond path portability, rerun before tagging.
4. Make this repository public and connect it to Zenodo under the repository owner's account.
5. Publish a tagged GitHub release from the reviewed commit. Verify the Zenodo record, archive, creator metadata, and assigned version DOI before adding the DOI to the manuscript.

Do not cite the mutable `main` branch as the permanent version. The GitHub release and its Zenodo DOI identify the frozen snapshot.
