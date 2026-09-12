"""Source-lock-enforced archive/reveal wrappers for Korthals protocol-v2 execution."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .korthals_execution_v2 import (
    KorthalsAOIExecutionV2,
    reveal_korthals_execution_v2,
    verify_korthals_execution_artifacts_v2,
    write_korthals_execution_artifacts_v2,
)
from .korthals_source_lock import (
    verify_korthals_locked_prepared,
    verify_korthals_source_lock,
)


def write_korthals_locked_execution_artifacts_v2(
    execution: KorthalsAOIExecutionV2,
    output_dir: str | Path,
    *,
    execution_context: Mapping[str, Any],
    environment_text: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a scientific archive only for the exact endpoint-blind locked intake."""

    verify_korthals_locked_prepared(execution.prepared)
    manifest = write_korthals_execution_artifacts_v2(
        execution,
        output_dir,
        execution_context=execution_context,
        environment_text=environment_text,
        overwrite=overwrite,
    )
    if not verify_korthals_locked_execution_artifacts_v2(output_dir):
        raise RuntimeError("newly written locked Korthals protocol-v2 archive failed verification")
    return manifest


def verify_korthals_locked_execution_artifacts_v2(output_dir: str | Path) -> bool:
    """Verify archive integrity plus exact source-freeze intake facts."""

    root = Path(output_dir)
    try:
        if not verify_korthals_execution_artifacts_v2(root):
            return False
        lock = verify_korthals_source_lock()
        intake = lock["intake"]
        source = lock["source"]
        source_identity = json.loads(
            (root / "source_identity.json").read_text(encoding="utf-8")
        )
        execution = json.loads(
            (root / "execution_manifest.json").read_text(encoding="utf-8")
        )
        summary = execution["summary"]

        checks = {
            "source_fingerprint": (
                source_identity.get("source_manifest_fingerprint")
                == source["source_manifest_fingerprint"]
            ),
            "source_file_count": (
                int(source_identity.get("source_file_count", -1)) == int(source["file_count"])
            ),
            "participant_count": (
                int(source_identity.get("participant_count", -1))
                == int(source["participant_count"])
            ),
            "split_fingerprint": (
                source_identity.get("participant_split_fingerprint")
                == intake["participant_split_fingerprint"]
            ),
            "retained_trials": (
                int(source_identity.get("retained_trial_count", -1))
                == int(intake["retained_trial_count"])
            ),
            "missingness_policy": (
                source_identity.get("missingness_policy") == intake["missingness_policy"]
            ),
            "zero_finite_count": (
                int(source_identity.get("zero_finite_scheduled_trial_count", -1))
                == int(intake["zero_finite_scheduled_trial_count"])
            ),
            "zero_finite_trials": (
                source_identity.get("zero_finite_scheduled_trials")
                == intake["zero_finite_scheduled_trials"]
            ),
            "incomplete_cell_count": (
                int(source_identity.get("sampling_incomplete_matched_cell_count", -1))
                == int(intake["sampling_incomplete_matched_cell_count"])
            ),
            "incomplete_cells": (
                source_identity.get("sampling_incomplete_matched_cells")
                == intake["sampling_incomplete_matched_cells"]
            ),
            "prepared_rows": int(execution.get("n_rows", -1))
            == int(intake["prepared_row_count"]),
            "validation_groups": int(execution.get("n_validation_groups", -1))
            == int(intake["validation_group_count"]),
            "summary_rows": int(summary.get("n_observations", -1))
            == int(intake["prepared_row_count"]),
            "draws": int(summary.get("n_draws", -1)) == 2000,
            "classification": execution.get("classification")
            in {"robust_positive", "robust_negative", "measurement_sensitive"},
        }
        return all(checks.values())
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def reveal_korthals_locked_execution_v2(output_dir: str | Path) -> dict[str, Any]:
    """Reveal only an intact archive that also reproduces the locked source intake."""

    if not verify_korthals_locked_execution_artifacts_v2(output_dir):
        raise ValueError("locked Korthals protocol-v2 scientific archive failed verification")
    return reveal_korthals_execution_v2(output_dir)
