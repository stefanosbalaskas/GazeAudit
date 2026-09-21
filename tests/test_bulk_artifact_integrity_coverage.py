from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import gazeaudit.aoi_artifacts as aoi_artifacts
import gazeaudit.gazebase_artifacts as gazebase_artifacts
from gazeaudit.aoi import RectangleAOI
from gazeaudit.aoi_propagation import audit_aoi_effect_uncertainty
from gazeaudit.aoi_protocol import build_aoi_uncertainty_protocol
from gazeaudit.gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    PreparedGazeBaseData,
    run_gazebase_multidetector_execution,
)
from gazeaudit.scientific_benchmark import condition_dwell_effect
from gazeaudit.study import GazeStudy
from gazeaudit.uncertainty import GaussianGazeErrorModel

COMMIT = "f" * 40


def _aoi_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant": [
                "p1",
                "p1",
                "p2",
                "p2",
            ],
            "condition": [
                "control",
                "treatment",
                "control",
                "treatment",
            ],
            "duration": [
                100.0,
                100.0,
                200.0,
                200.0,
            ],
            "observed_x": [
                -5.0,
                5.0,
                -5.0,
                5.0,
            ],
            "observed_y": [
                0.0,
                0.0,
                0.0,
                0.0,
            ],
        }
    )


def _aoi_protocol(
    *,
    draws: int = 16,
) -> dict[str, object]:
    return build_aoi_uncertainty_protocol(
        case_study_id="artifact-coverage-v1",
        dataset={
            "name": "synthetic",
            "identity": "fixture",
        },
        validation={
            "name": "synthetic-validation",
            "identity": "fixture-validation",
        },
        aoi={
            "name": "right",
            "geometry": "rectangle",
            "xmin": 0.0,
            "ymin": -10.0,
            "xmax": 10.0,
            "ymax": 10.0,
        },
        endpoint={
            "name": "condition dwell effect",
            "unit": "ms",
        },
        error_model={
            "name": "global-bivariate-gaussian",
        },
        monte_carlo={
            "draws": draws,
            "batch_size": 4,
            "interval": 0.95,
            "reference": 0.0,
            "rng_seed": 123,
        },
        interpretation={
            "name": "measurement uncertainty audit",
        },
    )


def _aoi_audit(
    *,
    draws: int = 16,
):
    model = GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.eye(2),
        n_validation=10,
    )
    return audit_aoi_effect_uncertainty(
        _aoi_data(),
        RectangleAOI(
            "right",
            0.0,
            -10.0,
            10.0,
            10.0,
        ),
        model,
        condition_dwell_effect,
        draws=draws,
        batch_size=4,
        interval=0.95,
        reference=0.0,
        rng=123,
    )


def _rewrite_aoi_manifest(
    root: Path,
    mutate,
) -> dict[str, object]:
    path = root / "artifact_manifest.json"
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    mutate(document)
    core = dict(document)
    core.pop(
        "artifact_manifest_fingerprint",
        None,
    )
    document[
        "artifact_manifest_fingerprint"
    ] = aoi_artifacts.fingerprint(
        core
    )
    path.write_text(
        aoi_artifacts.canonical_json(
            document
        )
        + "\n",
        encoding="utf-8",
    )
    return document


def _refresh_aoi_file_record(
    root: Path,
    filename: str,
) -> None:
    def mutate(
        document: dict[str, object],
    ) -> None:
        for record in document["files"]:
            if record["path"] == filename:
                path = root / filename
                record["size_bytes"] = path.stat().st_size
                record["sha256"] = aoi_artifacts._sha256_file(
                    path
                )
                return
        raise AssertionError(
            filename
        )

    _rewrite_aoi_manifest(
        root,
        mutate,
    )


def _write_valid_aoi(
    root: Path,
) -> None:
    aoi_artifacts.write_aoi_uncertainty_artifacts(
        _aoi_audit(),
        _aoi_protocol(),
        root,
    )


def test_aoi_writer_requires_audit_type(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="AOIEffectUncertaintyAudit",
    ):
        aoi_artifacts.write_aoi_uncertainty_artifacts(
            object(),  # type: ignore[arg-type]
            _aoi_protocol(),
            tmp_path / "out",
        )


def test_aoi_writer_requires_verified_protocol(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="verified AOI uncertainty protocol",
    ):
        aoi_artifacts.write_aoi_uncertainty_artifacts(
            _aoi_audit(),
            {
                "schema": "bad",
            },
            tmp_path / "out",
        )


def test_aoi_writer_fails_if_new_archive_verification_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        aoi_artifacts,
        "verify_aoi_uncertainty_artifacts",
        lambda _root: False,
    )

    with pytest.raises(
        RuntimeError,
        match="failed verification",
    ):
        aoi_artifacts.write_aoi_uncertainty_artifacts(
            _aoi_audit(),
            _aoi_protocol(),
            tmp_path / "out",
        )


def test_aoi_verifier_requires_manifest_and_checksums(
    tmp_path: Path,
) -> None:
    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        tmp_path
    )


def test_aoi_verifier_rejects_nonobject_manifest(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    root.mkdir()
    (root / "artifact_manifest.json").write_text(
        "[]",
        encoding="utf-8",
    )
    (root / "SHA256SUMS").write_text(
        "",
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_wrong_schema(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            "schema",
            "wrong",
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_manifest_fingerprint_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / "artifact_manifest.json"
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    document[
        "artifact_manifest_fingerprint"
    ] = "0" * 64
    path.write_text(
        json.dumps(
            document
        ),
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_nonempty_file_records(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            "files",
            [],
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_nonmapping_file_record(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            "files",
            [
                "bad",
            ],
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_unsafe_record_path(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)

    def mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["path"] = "../bad"

    _rewrite_aoi_manifest(
        root,
        mutate,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_duplicate_record_path(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)

    def mutate(
        document: dict[str, object],
    ) -> None:
        document["files"].append(
            dict(
                document["files"][0]
            )
        )

    _rewrite_aoi_manifest(
        root,
        mutate,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_declared_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    (root / "summary.json").unlink()

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_checks_record_size(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)

    def mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["size_bytes"] += 1

    _rewrite_aoi_manifest(
        root,
        mutate,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_checks_record_hash(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)

    def mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["sha256"] = "0" * 64

    _rewrite_aoi_manifest(
        root,
        mutate,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_exact_declared_file_set(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)

    def mutate(
        document: dict[str, object],
    ) -> None:
        document["files"] = document["files"][:-1]

    _rewrite_aoi_manifest(
        root,
        mutate,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_rejects_extra_unbound_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    (root / "extra.txt").write_text(
        "extra",
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_valid_protocol_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / "protocol.json"
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    document["schema"] = "wrong"
    path.write_text(
        aoi_artifacts.canonical_json(
            document
        )
        + "\n",
        encoding="utf-8",
    )
    _refresh_aoi_file_record(
        root,
        "protocol.json",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_binds_protocol_fingerprint(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            "protocol_fingerprint",
            "0" * 64,
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_summary_object_and_protocol_match(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / "summary.json"
    path.write_text(
        "[]\n",
        encoding="utf-8",
    )
    _refresh_aoi_file_record(
        root,
        "summary.json",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (
            "aoi",
            "left",
        ),
        (
            "n_observations",
            999,
        ),
        (
            "n_draws",
            999,
        ),
    ],
)
def test_aoi_verifier_binds_summary_identity_fields(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            field,
            value,
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


@pytest.mark.parametrize(
    ("filename", "text"),
    [
        (
            "draw_effects.csv",
            "wrong,estimate\n0,1\n",
        ),
        (
            "membership_probabilities.csv",
            "wrong,membership_probability\n0,1\n",
        ),
        (
            "draw_effects.csv",
            "draw,estimate\n0,1\n",
        ),
        (
            "membership_probabilities.csv",
            "observation,membership_probability\n0,1\n",
        ),
    ],
)
def test_aoi_verifier_checks_result_table_shape_and_columns(
    tmp_path: Path,
    filename: str,
    text: str,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / filename
    path.write_text(
        text,
        encoding="utf-8",
    )
    _refresh_aoi_file_record(
        root,
        filename,
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_binds_scientific_fingerprint(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    _rewrite_aoi_manifest(
        root,
        lambda document: document.__setitem__(
            "scientific_fingerprint",
            "0" * 64,
        ),
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_requires_exact_checksum_name_set(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / "SHA256SUMS"
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()
    path.write_text(
        "\n".join(
            lines[:-1]
        )
        + "\n",
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_checks_checksum_digest(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    path = root / "SHA256SUMS"
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()
    _, name = lines[0].split(
        "  ",
        1,
    )
    lines[0] = (
        "0" * 64
        + "  "
        + name
    )
    path.write_text(
        "\n".join(
            lines
        )
        + "\n",
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_verifier_fails_closed_on_invalid_json(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_aoi(root)
    (root / "artifact_manifest.json").write_text(
        "{",
        encoding="utf-8",
    )

    assert not aoi_artifacts.verify_aoi_uncertainty_artifacts(
        root
    )


def test_aoi_audit_protocol_binding_checks_aoi_and_table_lengths() -> None:
    audit = _aoi_audit()
    protocol = _aoi_protocol()

    with pytest.raises(
        ValueError,
        match="audit AOI",
    ):
        aoi_artifacts._verify_audit_matches_protocol(
            replace(
                audit,
                aoi="left",
            ),
            protocol,
        )

    with pytest.raises(
        ValueError,
        match="draw table",
    ):
        aoi_artifacts._verify_audit_matches_protocol(
            replace(
                audit,
                draw_effects=audit.draw_effects.iloc[
                    :-1
                ].copy(),
            ),
            protocol,
        )

    with pytest.raises(
        ValueError,
        match="membership table",
    ):
        aoi_artifacts._verify_audit_matches_protocol(
            replace(
                audit,
                membership_probabilities=(
                    audit.membership_probabilities.iloc[
                        :-1
                    ].copy()
                ),
            ),
            protocol,
        )


def test_aoi_summary_match_fails_closed_on_invalid_shape() -> None:
    assert not aoi_artifacts._summary_matches_protocol(
        {},
        {},
    )


def test_aoi_output_directory_and_csv_guards(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "not-a-directory"
    file_path.write_text(
        "x",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="directory path",
    ):
        aoi_artifacts._prepare_output_directory(
            file_path,
            overwrite=False,
        )

    root = tmp_path / "nested-root"
    root.mkdir()
    (root / "nested").mkdir()

    with pytest.raises(
        ValueError,
        match="nested directories",
    ):
        aoi_artifacts._prepare_output_directory(
            root,
            overwrite=True,
        )

    with pytest.raises(
        TypeError,
        match="pandas DataFrames",
    ):
        aoi_artifacts._write_csv(
            tmp_path / "bad.csv",
            object(),  # type: ignore[arg-type]
        )


def test_aoi_checksum_parser_guardrails(
    tmp_path: Path,
) -> None:
    blank = tmp_path / "blank.txt"
    blank.write_text(
        "\n"
        + (
            "a" * 64
        )
        + "  file.txt\n",
        encoding="utf-8",
    )
    assert aoi_artifacts._parse_checksums(
        blank
    ) == {
        "file.txt": "a" * 64,
    }

    malformed = tmp_path / "malformed.txt"
    malformed.write_text(
        "bad\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="invalid SHA256SUMS entry",
    ):
        aoi_artifacts._parse_checksums(
            malformed
        )

    duplicate = tmp_path / "duplicate.txt"
    duplicate.write_text(
        (
            "a" * 64
        )
        + "  file.txt\n"
        + (
            "b" * 64
        )
        + "  file.txt\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="invalid or duplicate",
    ):
        aoi_artifacts._parse_checksums(
            duplicate
        )


# ---------------------------------------------------------------------------
# GazeBase artifacts
# ---------------------------------------------------------------------------


class _FakeDetector:
    def __init__(
        self,
        algorithm: str,
    ) -> None:
        self.algorithm = algorithm

    def get_default_params(
        self,
    ) -> dict[str, str]:
        return {
            "frozen_default": (
                f"default-{self.algorithm}"
            )
        }


class _DetectionResult:
    def __init__(
        self,
        samples: pd.DataFrame,
    ) -> None:
        self.samples = samples


def _gazebase_prepared() -> PreparedGazeBaseData:
    rows: list[dict[str, object]] = []
    for participant in (
        1,
        2,
        3,
        4,
    ):
        for task in (
            "FXS",
            "TEX",
        ):
            labels = np.full(
                6,
                "fixation",
                dtype=object,
            )
            if task == "TEX":
                labels[4:] = "saccade"
            for index, label in enumerate(
                labels
            ):
                rows.append(
                    {
                        "x": float(index),
                        "y": float(participant),
                        "timestamp": float(
                            index
                            * 10
                        ),
                        "participant": participant,
                        "trial": task,
                        "reference_event_label": label,
                    }
                )

    identity = {
        "dataset": "GazeBase",
        "dataset_version": 3,
        "paper_doi": "10.1038/s41597-021-00959-y",
        "data_doi": "10.6084/m9.figshare.12912257",
        "catalog_archive_md5": GAZEBASE_ARCHIVE_MD5,
        "round": 1,
        "session": 1,
        "tasks": [
            "FXS",
            "TEX",
        ],
        "selected_file_count": 8,
        "selected_files_fingerprint": "artifact-coverage-source",
    }
    return PreparedGazeBaseData(
        GazeStudy(
            pd.DataFrame(
                rows
            )
        ),
        identity,
    )


def _gazebase_factory(
    algorithm: str,
    **_kwargs: object,
) -> _FakeDetector:
    return _FakeDetector(
        algorithm
    )


def _gazebase_runner(
    study: GazeStudy,
    detector: _FakeDetector,
    **_kwargs: object,
) -> _DetectionResult:
    del detector
    output = study.data.copy()
    output[
        "event_label"
    ] = output[
        "reference_event_label"
    ].copy()
    return _DetectionResult(
        output.reset_index(
            drop=True
        )
    )


def _gazebase_versions(
    name: str,
) -> str:
    return {
        "pymovements": "0.28.0",
        "pEYES": "0.2.2",
        "gazeaudit": "0.1.0.dev11",
    }[name]


def _gazebase_execution():
    return run_gazebase_multidetector_execution(
        _gazebase_prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=_gazebase_factory,
        detector_runner=_gazebase_runner,
        version_getter=_gazebase_versions,
    )


def _rewrite_gazebase_manifest(
    root: Path,
    mutate,
) -> dict[str, object]:
    path = root / "artifact_manifest.json"
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    mutate(document)
    core = dict(document)
    core.pop(
        "artifact_manifest_fingerprint",
        None,
    )
    document[
        "artifact_manifest_fingerprint"
    ] = gazebase_artifacts.fingerprint(
        core
    )
    path.write_text(
        gazebase_artifacts.canonical_json(
            document
        )
        + "\n",
        encoding="utf-8",
    )
    return document


def _refresh_gazebase_file_record(
    root: Path,
    filename: str,
) -> None:
    def mutate(
        document: dict[str, object],
    ) -> None:
        for record in document["files"]:
            if record["path"] == filename:
                path = root / filename
                record["size_bytes"] = path.stat().st_size
                record["sha256"] = gazebase_artifacts._sha256_file(
                    path
                )
                return
        raise AssertionError(
            filename
        )

    _rewrite_gazebase_manifest(
        root,
        mutate,
    )


def _write_valid_gazebase(
    root: Path,
) -> None:
    gazebase_artifacts.write_gazebase_execution_artifacts(
        _gazebase_execution(),
        root,
    )


def test_gazebase_writer_requires_execution_type(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="GazeBaseExecution",
    ):
        gazebase_artifacts.write_gazebase_execution_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path / "out",
        )


def test_gazebase_writer_fails_if_new_archive_verification_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gazebase_artifacts,
        "verify_gazebase_execution_artifacts",
        lambda _root: False,
    )

    with pytest.raises(
        RuntimeError,
        match="failed verification",
    ):
        gazebase_artifacts.write_gazebase_execution_artifacts(
            _gazebase_execution(),
            tmp_path / "out",
        )


def test_gazebase_verifier_requires_manifest_and_checksums(
    tmp_path: Path,
) -> None:
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        tmp_path
    )


def test_gazebase_verifier_rejects_wrong_manifest_shape_or_schema(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    root.mkdir()
    (root / "artifact_manifest.json").write_text(
        "[]",
        encoding="utf-8",
    )
    (root / "SHA256SUMS").write_text(
        "",
        encoding="utf-8",
    )
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_rejects_manifest_fingerprint_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    path = root / "artifact_manifest.json"
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    document[
        "artifact_manifest_fingerprint"
    ] = "0" * 64
    path.write_text(
        json.dumps(
            document
        ),
        encoding="utf-8",
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_requires_nonempty_file_records(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    _rewrite_gazebase_manifest(
        root,
        lambda document: document.__setitem__(
            "files",
            [],
        ),
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_rejects_nonmapping_file_record(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    _rewrite_gazebase_manifest(
        root,
        lambda document: document.__setitem__(
            "files",
            [
                "bad",
            ],
        ),
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_rejects_unsafe_or_duplicate_record_paths(
    tmp_path: Path,
) -> None:
    unsafe = tmp_path / "unsafe"
    _write_valid_gazebase(
        unsafe
    )

    def unsafe_mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["path"] = "../bad"

    _rewrite_gazebase_manifest(
        unsafe,
        unsafe_mutate,
    )
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        unsafe
    )

    duplicate = tmp_path / "duplicate"
    _write_valid_gazebase(
        duplicate
    )

    def duplicate_mutate(
        document: dict[str, object],
    ) -> None:
        document["files"].append(
            dict(
                document["files"][0]
            )
        )

    _rewrite_gazebase_manifest(
        duplicate,
        duplicate_mutate,
    )
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        duplicate
    )


def test_gazebase_verifier_requires_declared_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    (root / "summary.json").unlink()

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_checks_record_size_and_hash(
    tmp_path: Path,
) -> None:
    size_root = tmp_path / "size"
    _write_valid_gazebase(
        size_root
    )

    def size_mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["size_bytes"] += 1

    _rewrite_gazebase_manifest(
        size_root,
        size_mutate,
    )
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        size_root
    )

    hash_root = tmp_path / "hash"
    _write_valid_gazebase(
        hash_root
    )

    def hash_mutate(
        document: dict[str, object],
    ) -> None:
        document["files"][0]["sha256"] = "0" * 64

    _rewrite_gazebase_manifest(
        hash_root,
        hash_mutate,
    )
    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        hash_root
    )


def test_gazebase_verifier_rejects_extra_unbound_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    (root / "extra.txt").write_text(
        "extra",
        encoding="utf-8",
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


@pytest.mark.parametrize(
    ("filename", "replacement"),
    [
        (
            "execution_manifest.json",
            "[]\n",
        ),
        (
            "protocol.json",
            "[]\n",
        ),
        (
            "publication_manifest.json",
            "[]\n",
        ),
    ],
)
def test_gazebase_verifier_checks_embedded_manifests(
    tmp_path: Path,
    filename: str,
    replacement: str,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    path = root / filename
    path.write_text(
        replacement,
        encoding="utf-8",
    )
    _refresh_gazebase_file_record(
        root,
        filename,
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_requires_exact_checksum_names(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    path = root / "SHA256SUMS"
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()
    path.write_text(
        "\n".join(
            lines[:-1]
        )
        + "\n",
        encoding="utf-8",
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_checks_checksum_digest(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    path = root / "SHA256SUMS"
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()
    _, name = lines[0].split(
        "  ",
        1,
    )
    lines[0] = (
        "0" * 64
        + "  "
        + name
    )
    path.write_text(
        "\n".join(
            lines
        )
        + "\n",
        encoding="utf-8",
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_verifier_fails_closed_on_invalid_json(
    tmp_path: Path,
) -> None:
    root = tmp_path / "out"
    _write_valid_gazebase(
        root
    )
    (root / "artifact_manifest.json").write_text(
        "{",
        encoding="utf-8",
    )

    assert not gazebase_artifacts.verify_gazebase_execution_artifacts(
        root
    )


def test_gazebase_output_and_table_guards(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "not-dir"
    file_path.write_text(
        "x",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="directory path",
    ):
        gazebase_artifacts._prepare_output_directory(
            file_path,
            overwrite=False,
        )

    with pytest.raises(
        TypeError,
        match="pandas DataFrames",
    ):
        gazebase_artifacts._write_csv(
            tmp_path / "bad.csv",
            object(),  # type: ignore[arg-type]
        )

    with pytest.raises(
        TypeError,
        match="pandas Series",
    ):
        gazebase_artifacts._series_mapping(
            object()  # type: ignore[arg-type]
        )


def test_gazebase_json_scalar_paths() -> None:
    assert gazebase_artifacts._json_scalar(
        np.inf
    ) is None
    assert gazebase_artifacts._json_scalar(
        np.int64(
            7
        )
    ) == 7

    marker = object()
    assert gazebase_artifacts._json_scalar(
        marker
    ) is marker


@pytest.mark.parametrize(
    ("helper", "filename"),
    [
        (
            gazebase_artifacts._verify_execution_manifest,
            "execution.json",
        ),
        (
            gazebase_artifacts._verify_protocol_document,
            "protocol.json",
        ),
        (
            gazebase_artifacts._verify_publication_manifest,
            "publication.json",
        ),
    ],
)
def test_gazebase_internal_manifest_verifiers_reject_nonobjects(
    tmp_path: Path,
    helper,
    filename: str,
) -> None:
    path = tmp_path / filename
    path.write_text(
        "[]",
        encoding="utf-8",
    )
    assert helper(
        path
    ) is False


def test_gazebase_checksum_parser_guardrails(
    tmp_path: Path,
) -> None:
    blank = tmp_path / "blank.txt"
    blank.write_text(
        "\n"
        + (
            "a" * 64
        )
        + "  file.txt\n",
        encoding="utf-8",
    )
    assert gazebase_artifacts._parse_checksums(
        blank
    ) == {
        "file.txt": "a" * 64,
    }

    malformed = tmp_path / "malformed.txt"
    malformed.write_text(
        "bad\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="invalid SHA256SUMS entry",
    ):
        gazebase_artifacts._parse_checksums(
            malformed
        )

    duplicate = tmp_path / "duplicate.txt"
    duplicate.write_text(
        (
            "a" * 64
        )
        + "  file.txt\n"
        + (
            "b" * 64
        )
        + "  file.txt\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="invalid or duplicate",
    ):
        gazebase_artifacts._parse_checksums(
            duplicate
        )
