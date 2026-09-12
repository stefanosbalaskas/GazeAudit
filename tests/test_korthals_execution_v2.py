from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import pandas as pd
import pytest

from gazeaudit.korthals_execution_archive_v2 import (
    write_korthals_locked_execution_artifacts_v2,
)
from gazeaudit.korthals_execution_v2 import (
    KORTHALS_V2_EXECUTION_WORKFLOW,
    reveal_korthals_execution_v2,
    run_korthals_aoi_execution_v2,
    run_korthals_locked_aoi_execution_v2,
    verify_korthals_execution_artifacts_v2,
    write_korthals_execution_artifacts_v2,
)
from gazeaudit.korthals_source_lock import (
    KORTHALS_SOURCE_LOCK_FINGERPRINT,
    load_korthals_source_lock,
)
from gazeaudit.korthals_v2 import (
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    prepare_korthals_aligned_data_v2,
)


def _aligned_fixture() -> pd.DataFrame:
    rows = []
    specs = [
        (1, "moving_circle", 4.0, "east", 2.0),
        (2, "jumping_circle", 4.0, "east", 0.0),
        (73, "moving_circle", 6.0, "north", 2.0),
        (74, "jumping_circle", 6.0, "north", 0.0),
    ]
    for trial_number, target_type, speed, trajectory, gaze_x in specs:
        for trial_time in (0.0, 0.02, 0.04):
            rows.append(
                {
                    "participant_id": "p1",
                    "trial_number": trial_number,
                    "trial_time": trial_time,
                    "gaze_x": gaze_x,
                    "gaze_y": 0.0,
                    "target_x": 0.0,
                    "target_y": 0.0,
                    "target_type": target_type,
                    "target_speed": speed,
                    "target_trajectory": trajectory,
                }
            )
    return pd.DataFrame(rows)


def _validation_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "validation_nr": 1,
                "error_avg": 0.0,
                "first_trial": 1,
                "last_trial": 72,
            },
            {
                "participant_id": "p1",
                "validation_nr": 2,
                "error_avg": 0.0,
                "first_trial": 73,
                "last_trial": 144,
            },
        ]
    )


def _synthetic_prepared():
    lock = load_korthals_source_lock()
    return prepare_korthals_aligned_data_v2(
        _aligned_fixture(),
        _validation_fixture(),
        source_identity={
            "source_manifest_fingerprint": lock["source"]["source_manifest_fingerprint"],
            "source_file_count": lock["source"]["file_count"],
            "fixture": "synthetic-execution-contract-only",
        },
    )


def _execution_context(prepared) -> dict:
    return {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": KORTHALS_V2_EXECUTION_WORKFLOW,
        "github_run_id": "123",
        "companion_repository": "lukekorthals/pursuing-smooth-pursuits-data",
        "companion_commit": prepared.source_identity["companion_commit"],
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": KORTHALS_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": prepared.source_identity["source_manifest_fingerprint"],
        "package_version": version("gazeaudit"),
        "python_version": "3.12.14",
        "platform": "synthetic-test-platform",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }


def _environment_text() -> str:
    return "numpy==2.5.3\npandas==2.3.3\nscipy==1.18.1\n"


def test_protocol_v2_execution_preserves_frozen_endpoint_and_mc_semantics():
    execution = run_korthals_aoi_execution_v2(_synthetic_prepared())

    assert execution.classification == "robust_positive"
    assert execution.protocol["protocol_fingerprint"] == KORTHALS_V2_PROTOCOL_FINGERPRINT
    assert execution.audit.summary["n_draws"] == 2000
    assert execution.audit.summary["hard_effect"] == pytest.approx(1.0)
    assert execution.audit.summary["probability_above_reference"] == pytest.approx(1.0)
    assert execution.execution_manifest["case_study_id"].endswith("-v2")


def test_real_data_entrypoint_fails_closed_when_synthetic_intake_is_not_source_locked():
    with pytest.raises(ValueError, match="differs from locked source freeze"):
        run_korthals_locked_aoi_execution_v2(_synthetic_prepared())


def test_generic_v2_archive_is_tamper_evident_without_weakening_locked_writer(tmp_path):
    prepared = _synthetic_prepared()
    execution = run_korthals_aoi_execution_v2(prepared)
    output = tmp_path / "generic-v2"
    manifest = write_korthals_execution_artifacts_v2(
        execution,
        output,
        execution_context=_execution_context(prepared),
        environment_text=_environment_text(),
    )

    assert manifest["classification"] == "robust_positive"
    assert verify_korthals_execution_artifacts_v2(output)
    revealed = reveal_korthals_execution_v2(output)
    assert revealed["classification"] == "robust_positive"

    with pytest.raises(ValueError, match="differs from locked source freeze"):
        write_korthals_locked_execution_artifacts_v2(
            execution,
            tmp_path / "must-not-write",
            execution_context=_execution_context(prepared),
            environment_text=_environment_text(),
        )

    summary = output / "audit" / "summary.json"
    summary.write_text(summary.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert not verify_korthals_execution_artifacts_v2(output)


def test_scientific_workflow_is_manual_main_only_source_locked_and_archive_before_reveal():
    text = Path(".github/workflows/korthals-scientific-execution.yml").read_text(
        encoding="utf-8"
    )

    assert "workflow_dispatch:" in text
    assert "pull_request:" not in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "python-version: '3.12.14'" in text
    for pin in ("numpy==2.5.3", "pandas==2.3.3", "scipy==1.18.1"):
        assert pin in text
    assert "verify_korthals_locked_source_manifest" in text
    assert "verify_korthals_locked_execution_artifacts_v2" in text

    execute = text.index("Execute locked protocol v2 without revealing scientific results")
    verify = text.index("Verify locked scientific archive before upload")
    archive = text.index("Archive scientific execution before reveal")
    reveal = text.index("Reveal archived scientific result")
    assert execute < verify < archive < reveal
