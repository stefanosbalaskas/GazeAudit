# GazeAudit 0.1.0

GazeAudit 0.1.0 is the first stable GitHub release of the package for auditing measurement uncertainty and inferential robustness in eye-tracking research.

## Scientific validation record

This release preserves the three canonical real-data validation outcomes established before release preparation:

- **GazeBase multi-detector audit:** `incomplete` under the frozen completeness gate;
- **Korthals target-tracking AOI audit:** `robust_negative` under the frozen measurement-error propagation protocol;
- **Pedrotti/de Chambrier sampling and missingness audit:** `materially_fragile` under the frozen recovery rule.

These labels are protocol-bound validation outcomes, not general claims about the datasets or every possible eye-tracking analysis.

## Distribution integrity

The attached files were rebuilt from the immutable `v0.1.0` tag and must match the previously qualified candidate exactly:

- `gazeaudit-0.1.0-py3-none-any.whl`  
  SHA-256: `51fa1f0a0388dfe337fad0d6564df802ae8464f01d5ce666cc96ce2e144271a1`
- `gazeaudit-0.1.0.tar.gz`  
  SHA-256: `8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173`

Source commit: `fdade23c12b3c2a2f26a1ca8398034b6f8d0213f`  
Source tree: `938007cda6051d50243fff27a892870f7128d407`  
Tag: `v0.1.0`

## Reproducibility

The repository contains publication-facing validation and reproducibility records under `docs/`, including the validation summary, reproducibility index, citation/reuse guidance, and release qualification documentation.

## Publication scope

This GitHub Release publishes the qualified source distribution and wheel only. It does **not** imply that GazeAudit has also been published to PyPI, assigned a DOI, or deposited in an archival registry. Those are separate publication actions with separate verification gates.
