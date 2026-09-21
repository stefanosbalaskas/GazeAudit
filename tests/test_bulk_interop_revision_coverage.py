from __future__ import annotations

import json
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import gazeaudit.gazebase_pymovements as gazebase_pm
import gazeaudit.peyes_adapter as peyes_adapter
import gazeaudit.pymovements_adapter as pymovements_adapter
import gazeaudit.revision_package as revision_package
from gazeaudit.study import GazeStudy


class _Detector:
    name = "demo-detector"
    algorithm_name = "demo"

    def detect(
        self,
        t: np.ndarray,
        x: np.ndarray,
        y: np.ndarray,
        viewer_distance_cm: float,
        pixel_size_cm: float,
    ) -> tuple[list[object], object]:
        del x, y, viewer_distance_cm, pixel_size_cm
        return list(range(1, len(t) + 1)), None


class _FakeStudy:
    participant = "participant"
    trial = "trial"
    timestamp = "timestamp"
    x = "x"
    y = "y"

    def __init__(self, frame: pd.DataFrame) -> None:
        self.data = frame

    def validate_time_order(self) -> None:
        return None


class _BadToPandas:
    def to_pandas(self) -> list[int]:
        return [1, 2, 3]


class _DictRows:
    def __init__(self, rows: object) -> None:
        self.rows = rows

    def to_dicts(self) -> object:
        return self.rows


def _simple_study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["p1", "p1"],
                "trial": [1, 1],
                "timestamp": [0.0, 10.0],
                "x": [100.0, 101.0],
                "y": [50.0, 51.0],
            }
        )
    )


# ---------------------------------------------------------------------------
# Revision-package validation
# ---------------------------------------------------------------------------


def test_revision_manifest_rejects_empty_project_slug() -> None:
    with pytest.raises(
        ValueError,
        match="project_slug",
    ):
        revision_package.build_revision_package_manifest("   ")


def test_revision_manifest_rejects_nonpositive_review_round() -> None:
    with pytest.raises(
        ValueError,
        match="review_round",
    ):
        revision_package.build_revision_package_manifest(
            "study",
            review_round=0,
        )


def test_revision_validator_reports_missing_manifest(tmp_path) -> None:
    validation = revision_package.validate_revision_package(
        tmp_path
    )

    assert validation["valid"] is False
    assert "missing package-manifest.json" in validation["problems"]
    assert validation["review_round"] is None


def test_revision_validator_reports_unreadable_manifest(tmp_path) -> None:
    path = tmp_path / "package-manifest.json"
    path.write_text("{", encoding="utf-8")

    validation = revision_package.validate_revision_package(
        tmp_path
    )

    assert validation["valid"] is False
    assert any(
        problem.startswith("unreadable package manifest:")
        for problem in validation["problems"]
    )


def test_revision_validator_requires_json_object(tmp_path) -> None:
    path = tmp_path / "package-manifest.json"
    path.write_text("[]", encoding="utf-8")

    validation = revision_package.validate_revision_package(
        tmp_path
    )

    assert validation["valid"] is False
    assert "package manifest must be a JSON object" in validation["problems"]


def test_revision_validator_reports_schema_round_and_fingerprint_errors(
    tmp_path,
) -> None:
    manifest = revision_package.build_revision_package_manifest(
        "study",
        review_round=2,
    )
    manifest["schema"] = "wrong-schema"
    manifest["review_round"] = True

    (tmp_path / "package-manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    validation = revision_package.validate_revision_package(
        tmp_path
    )

    assert validation["valid"] is False
    assert "unexpected package manifest schema" in validation["problems"]
    assert "review_round must be an integer >= 1" in validation["problems"]
    assert "package manifest fingerprint mismatch" in validation["problems"]
    assert validation["review_round"] is None


def test_revision_validator_rejects_nonstring_fingerprint(tmp_path) -> None:
    manifest = revision_package.build_revision_package_manifest(
        "study"
    )
    manifest["manifest_fingerprint"] = None

    (tmp_path / "package-manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    validation = revision_package.validate_revision_package(
        tmp_path
    )

    assert validation["manifest_fingerprint_valid"] is False
    assert "package manifest fingerprint mismatch" in validation["problems"]


# ---------------------------------------------------------------------------
# pEYES interoperability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "error", "message"),
    [
        (
            {
                "detector": object(),
                "viewer_distance_cm": 60.0,
                "pixel_size_cm": 0.03,
            },
            TypeError,
            "callable detect",
        ),
        (
            {
                "detector": _Detector(),
                "viewer_distance_cm": 0.0,
                "pixel_size_cm": 0.03,
            },
            ValueError,
            "viewer_distance_cm",
        ),
        (
            {
                "detector": _Detector(),
                "viewer_distance_cm": 60.0,
                "pixel_size_cm": np.nan,
            },
            ValueError,
            "pixel_size_cm",
        ),
        (
            {
                "detector": _Detector(),
                "viewer_distance_cm": 60.0,
                "pixel_size_cm": 0.03,
                "label_column": "",
            },
            ValueError,
            "label_column",
        ),
        (
            {
                "detector": _Detector(),
                "viewer_distance_cm": 60.0,
                "pixel_size_cm": 0.03,
                "code_column": "",
            },
            ValueError,
            "code_column",
        ),
    ],
)
def test_peyes_adapter_constructor_guardrails(
    kwargs: dict[str, object],
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error,
        match=message,
    ):
        peyes_adapter.PeyesDetectorAdapter(**kwargs)  # type: ignore[arg-type]


def test_peyes_adapter_rejects_nonfinite_timestamp_before_detector_call() -> None:
    frame = pd.DataFrame(
        {
            "participant": ["p1"],
            "trial": [1],
            "timestamp": [np.nan],
            "x": [1.0],
            "y": [2.0],
        }
    )

    adapter = peyes_adapter.PeyesDetectorAdapter(
        detector=_Detector(),
        viewer_distance_cm=60.0,
        pixel_size_cm=0.03,
    )

    with pytest.raises(
        ValueError,
        match="timestamps must be finite",
    ):
        adapter.detect(
            _FakeStudy(frame)  # type: ignore[arg-type]
        )


def test_peyes_custom_code_column_is_normalized_to_event_code() -> None:
    adapter = peyes_adapter.PeyesDetectorAdapter(
        detector=_Detector(),
        viewer_distance_cm=60.0,
        pixel_size_cm=0.03,
        code_column="raw_code",
    )

    result = adapter.detect(_simple_study())

    assert "event_code" in result.samples.columns
    assert "raw_code" not in result.samples.columns
    assert result.metadata.iloc[0]["metadata"] == {}


def test_make_peyes_detector_uses_public_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def create_detector(**kwargs: object) -> dict[str, object]:
        calls.append(dict(kwargs))
        return dict(kwargs)

    monkeypatch.setitem(
        sys.modules,
        "peyes",
        SimpleNamespace(
            create_detector=create_detector
        ),
    )

    result = peyes_adapter.make_peyes_detector(
        "ivt",
        missing_value=-1.0,
        min_event_duration=80.0,
        pad_blinks_time=50.0,
        name="ivt",
        extra=7,
    )

    assert result["algorithm"] == "ivt"
    assert result["extra"] == 7
    assert calls == [result]


def test_peyes_helper_fallbacks_are_explicit() -> None:
    class FallbackDetector:
        pass

    assert peyes_adapter._group_key("p1") == ("p1", None)
    assert peyes_adapter._label_name(" Fixation ") == "fixation"
    assert peyes_adapter._label_code("not-an-int") is None
    assert (
        peyes_adapter._detector_name(FallbackDetector())
        == "FallbackDetector"
    )
    assert (
        peyes_adapter._detector_algorithm(FallbackDetector())
        == "fallback"
    )
    assert peyes_adapter._metadata_mapping(None) == {}

    with pytest.raises(
        TypeError,
        match="metadata must be a dictionary",
    ):
        peyes_adapter._metadata_mapping(["bad"])


# ---------------------------------------------------------------------------
# pymovements interoperability
# ---------------------------------------------------------------------------


def test_pymovements_gaze_requires_time_column() -> None:
    source = SimpleNamespace(
        samples=pd.DataFrame(
            {
                "pixel": [[1.0, 2.0]],
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="canonical 'time' column",
    ):
        pymovements_adapter.from_pymovements_gaze(
            source
        )


def test_pymovements_gaze_requires_declared_participant_column() -> None:
    source = SimpleNamespace(
        samples=pd.DataFrame(
            {
                "time": [0.0],
                "pixel": [[1.0, 2.0]],
            }
        )
    )

    adapter = pymovements_adapter.PymovementsGazeAdapter(
        participant_column="subject",
    )

    with pytest.raises(
        ValueError,
        match="participant column",
    ):
        adapter.to_study(source)


def test_pymovements_dataset_requires_gaze_sequence() -> None:
    with pytest.raises(
        TypeError,
        match="expose a 'gaze' sequence",
    ):
        pymovements_adapter.from_pymovements_dataset(
            object()
        )


def test_pymovements_dataset_rejects_empty_recordings() -> None:
    with pytest.raises(
        ValueError,
        match="at least one loaded recording",
    ):
        pymovements_adapter.from_pymovements_dataset(
            SimpleNamespace(gaze=[])
        )


def test_pymovements_dataset_requires_matching_participant_ids() -> None:
    recording = SimpleNamespace(
        samples=pd.DataFrame(
            {
                "time": [0.0],
                "pixel": [[1.0, 2.0]],
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="participant_ids",
    ):
        pymovements_adapter.from_pymovements_dataset(
            SimpleNamespace(
                gaze=[recording, recording]
            ),
            participant_ids=["p1"],
        )


def test_samples_to_pandas_requires_callable_converter() -> None:
    with pytest.raises(
        TypeError,
        match="expose to_pandas",
    ):
        pymovements_adapter._samples_to_pandas(
            SimpleNamespace(samples=object())
        )


def test_samples_to_pandas_requires_dataframe_result() -> None:
    with pytest.raises(
        TypeError,
        match="must return a pandas DataFrame",
    ):
        pymovements_adapter._samples_to_pandas(
            SimpleNamespace(
                samples=_BadToPandas()
            )
        )


def test_coordinate_parser_preserves_missing_sample_positions() -> None:
    x, y = pymovements_adapter._extract_coordinate_components(
        pd.Series(
            [
                None,
                [3.0, 4.0],
            ],
            dtype="object",
        ),
        "auto",
    )

    assert np.isnan(x[0])
    assert np.isnan(y[0])
    assert x[1] == pytest.approx(3.0)
    assert y[1] == pytest.approx(4.0)


def test_coordinate_parser_rejects_all_missing_vectors() -> None:
    with pytest.raises(
        ValueError,
        match="no usable coordinate vectors",
    ):
        pymovements_adapter._extract_coordinate_components(
            pd.Series(
                [None, np.nan],
                dtype="object",
            ),
            "auto",
        )


def test_coordinate_parser_rejects_unknown_component() -> None:
    with pytest.raises(
        ValueError,
        match="component must be",
    ):
        pymovements_adapter._extract_coordinate_components(
            pd.Series(
                [[1.0, 2.0]],
                dtype="object",
            ),
            "unknown",
        )


def test_coordinate_parser_rejects_component_that_exceeds_vector_width() -> None:
    with pytest.raises(
        ValueError,
        match="requires at least",
    ):
        pymovements_adapter._extract_coordinate_components(
            pd.Series(
                [[1.0, 2.0]],
                dtype="object",
            ),
            "right",
        )


def test_time_conversion_rejects_nonduration_objects() -> None:
    with pytest.raises(
        TypeError,
        match="duration-like or numeric",
    ):
        pymovements_adapter._time_to_milliseconds(
            pd.Series(
                [object()],
                dtype="object",
            ),
            "ms",
        )


def test_time_conversion_rejects_nonfinite_numeric_values() -> None:
    with pytest.raises(
        ValueError,
        match="must be finite",
    ):
        pymovements_adapter._time_to_milliseconds(
            pd.Series(
                [0.0, np.nan],
                dtype=float,
            ),
            "ms",
        )


# ---------------------------------------------------------------------------
# GazeBase pymovements bridge
# ---------------------------------------------------------------------------


def test_gazebase_view_requires_live_deg2pix_when_requested() -> None:
    view = gazebase_pm._GazeFileinfoDatasetView(
        SimpleNamespace(
            gaze=[],
        ),
        pd.DataFrame(),
    )

    with pytest.raises(
        TypeError,
        match="expose deg2pix",
    ):
        view.deg2pix()


def test_gazebase_prepare_supports_direct_nonmapping_fileinfo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = object()
    dataset = SimpleNamespace(
        fileinfo=pd.DataFrame(
            {
                "filepath": [],
            }
        ),
        gaze=[],
    )

    monkeypatch.setattr(
        gazebase_pm,
        "_prepare_table_contract",
        lambda value: sentinel,
    )
    monkeypatch.setattr(
        gazebase_pm,
        "_selected_file_content_identity",
        lambda dataset, gaze_fileinfo, required: {},
    )

    result = gazebase_pm.prepare_gazebase_pymovements_dataset(
        dataset
    )

    assert result is sentinel


def test_content_identity_requires_fileinfo_rows_when_strict(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="requires gaze fileinfo rows",
    ):
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(),
            required=True,
        )


def test_content_identity_returns_empty_for_missing_rows_when_optional(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    assert (
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(),
            required=False,
        )
        == {}
    )


def test_content_identity_requires_filepath_values_when_strict(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="contain filepath values",
    ):
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(
                {
                    "other": [1],
                }
            ),
            required=True,
        )


def test_content_identity_returns_empty_for_missing_filepath_when_optional(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    assert (
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(
                {
                    "other": [1],
                }
            ),
            required=False,
        )
        == {}
    )


def test_content_identity_requires_selected_file_when_strict(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    with pytest.raises(
        FileNotFoundError,
        match="not readable",
    ):
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(
                {
                    "filepath": [
                        "missing.csv"
                    ],
                }
            ),
            required=True,
        )


def test_content_identity_returns_empty_for_missing_file_when_optional(
    tmp_path,
) -> None:
    dataset = SimpleNamespace(
        paths=SimpleNamespace(
            raw=tmp_path
        )
    )

    assert (
        gazebase_pm._selected_file_content_identity(
            dataset,
            pd.DataFrame(
                {
                    "filepath": [
                        "missing.csv"
                    ],
                }
            ),
            required=False,
        )
        == {}
    )


def test_fileinfo_records_supports_polars_like_to_dicts() -> None:
    rows = [
        {
            "filepath": "a.csv",
        },
        {
            "filepath": "b.csv",
        },
    ]

    assert gazebase_pm._fileinfo_records(
        _DictRows(rows)
    ) == rows


def test_fileinfo_records_rejects_nonlist_converter_result() -> None:
    assert gazebase_pm._fileinfo_records(
        _DictRows(
            {
                "filepath": "a.csv",
            }
        )
    ) == []
