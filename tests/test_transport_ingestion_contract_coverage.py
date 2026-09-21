from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.error import URLError

import numpy as np
import pandas as pd
import pytest

import gazeaudit.bids_adapter as bids
import gazeaudit.pedrotti_prefetch as prefetch


# ======================================================================
# Eye-Tracking-BIDS helpers
# ======================================================================


def _metadata(**overrides: object) -> dict[str, object]:
    metadata: dict[str, object] = {
        "SamplingFrequency": 1000.0,
        "StartTime": 0.0,
        "Columns": [
            "timestamp",
            "x_coordinate",
            "y_coordinate",
            "pupil_size",
        ],
        "PhysioType": "eyetrack",
        "RecordedEye": "right",
        "SampleCoordinateSystem": "gaze-on-screen",
        "timestamp": {"Units": "ms"},
        "x_coordinate": {"Units": "pixel"},
        "y_coordinate": {"Units": "pixel"},
        "pupil_size": {"Units": "arbitrary"},
    }
    metadata.update(overrides)
    return metadata


def _write_record(
    root: Path,
    name: str,
    *,
    rows: list[list[object]] | None = None,
    metadata: dict[str, object] | None = None,
) -> tuple[Path, Path]:
    if rows is None:
        rows = [
            [0.0, 10.0, 20.0, 3.0],
            [10.0, 11.0, 21.0, 3.1],
        ]

    source = root / name

    pd.DataFrame(rows).to_csv(
        source,
        sep="\t",
        header=False,
        index=False,
        compression="gzip" if name.endswith(".gz") else None,
    )

    if name.endswith(".tsv.gz"):
        sidecar_name = name[: -len(".tsv.gz")] + ".json"
    else:
        sidecar_name = name[: -len(".tsv")] + ".json"

    sidecar = root / sidecar_name

    sidecar.write_text(
        json.dumps(metadata or _metadata()),
        encoding="utf-8",
    )

    return source, sidecar


def test_bids_sidecar_must_exist(tmp_path: Path) -> None:
    source = tmp_path / "sub-01_recording-eye1_physio.tsv"
    source.write_text("0\t1\t2\n", encoding="utf-8")

    with pytest.raises(
        FileNotFoundError,
        match="sidecar does not exist",
    ):
        bids.read_bids_eyetrack(source)


def test_bids_sidecar_must_be_json_object(tmp_path: Path) -> None:
    source, sidecar = _write_record(
        tmp_path,
        "sub-01_recording-eye1_physio.tsv",
    )

    sidecar.write_text(
        "[]",
        encoding="utf-8",
    )

    with pytest.raises(
        TypeError,
        match="JSON object",
    ):
        bids.read_bids_eyetrack(source)


@pytest.mark.parametrize(
    "columns",
    [
        None,
        [],
        ["timestamp", "", "y_coordinate"],
        ["timestamp", 123, "y_coordinate"],
    ],
)
def test_bids_columns_contract_validation(
    columns: object,
) -> None:
    metadata = _metadata()

    if columns is None:
        metadata.pop("Columns")
        with pytest.raises(
            ValueError,
            match="missing required fields",
        ):
            bids._validate_sidecar(metadata)
    else:
        metadata["Columns"] = columns
        with pytest.raises(
            TypeError,
            match="Columns",
        ):
            bids._validate_sidecar(metadata)


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_bids_sampling_frequency_requires_finite_number(
    value: float,
) -> None:
    metadata = _metadata(
        SamplingFrequency=value,
    )

    with pytest.raises(
        TypeError,
        match="SamplingFrequency",
    ):
        bids._validate_sidecar(metadata)


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_bids_start_time_requires_finite_number(
    value: float,
) -> None:
    metadata = _metadata(
        StartTime=value,
    )

    with pytest.raises(
        TypeError,
        match="StartTime",
    ):
        bids._validate_sidecar(metadata)


@pytest.mark.parametrize(
    "field",
    [
        "RecordedEye",
        "SampleCoordinateSystem",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_bids_text_metadata_must_be_nonempty(
    field: str,
    value: object,
) -> None:
    metadata = _metadata()
    metadata[field] = value

    with pytest.raises(
        TypeError,
        match=field,
    ):
        bids._validate_sidecar(metadata)


def test_bids_optional_column_units_helper() -> None:
    metadata = _metadata()

    assert bids._column_units(
        metadata,
        "not_present",
        required=False,
    ) == ""

    metadata["optional"] = {}

    assert bids._column_units(
        metadata,
        "optional",
        required=False,
    ) == ""

    metadata["optional"] = {
        "Units": "   ",
    }

    assert bids._column_units(
        metadata,
        "optional",
        required=False,
    ) == ""


def test_bids_required_column_metadata_must_be_mapping() -> None:
    metadata = _metadata(
        timestamp="ms",
    )

    with pytest.raises(
        ValueError,
        match="metadata for column",
    ):
        bids._column_units(
            metadata,
            "timestamp",
            required=True,
        )


@pytest.mark.parametrize(
    ("unit", "factor"),
    [
        ("s", 1000.0),
        ("sec", 1000.0),
        ("second", 1000.0),
        ("seconds", 1000.0),
        ("ms", 1.0),
        ("millisecond", 1.0),
        ("milliseconds", 1.0),
        ("us", 0.001),
        ("µs", 0.001),
        ("μs", 0.001),
        ("microsecond", 0.001),
        ("microseconds", 0.001),
        (" MS ", 1.0),
    ],
)
def test_bids_time_unit_aliases(
    unit: str,
    factor: float,
) -> None:
    assert bids._time_factor_to_ms(unit) == pytest.approx(factor)


def test_bids_sidecar_inference_for_plain_and_gzip() -> None:
    plain = Path("sub-01_recording-eye1_physio.tsv")
    zipped = Path("sub-01_recording-eye1_physio.tsv.gz")

    assert bids._infer_sidecar_path(plain).name.endswith(
        "_physio.json"
    )

    assert bids._infer_sidecar_path(zipped).name.endswith(
        "_physio.json"
    )

    with pytest.raises(
        ValueError,
        match="unsupported physio",
    ):
        bids._infer_sidecar_path(
            Path("invalid.txt")
        )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a_physio.tsv", True),
        ("a_physio.tsv.gz", True),
        ("a.tsv", False),
        ("a_physio.csv", False),
    ],
)
def test_bids_physio_filename_detection(
    name: str,
    expected: bool,
) -> None:
    assert bids._is_physio_tsv(
        Path(name)
    ) is expected


def test_bids_default_trial_id_all_entities_and_fallback() -> None:
    source = Path(
        "sub-01_ses-2_task-search_acq-fast_run-03_"
        "recording-eye1_physio.tsv"
    )

    entities = bids.parse_bids_entities(
        source.name
    )

    assert bids._default_trial_id(
        source,
        entities,
    ) == (
        "ses-2|task-search|acq-fast|run-03|recording-eye1"
    )

    fallback_plain = bids._default_trial_id(
        Path("plain_physio.tsv"),
        {},
    )

    fallback_gz = bids._default_trial_id(
        Path("plain_physio.tsv.gz"),
        {},
    )

    assert fallback_plain == "plain_physio"
    assert fallback_gz == "plain_physio"


def test_bids_optional_sequence_none_and_exact_length() -> None:
    assert bids._optional_sequence(
        None,
        2,
        "ids",
    ) is None

    assert bids._optional_sequence(
        ("a", "b"),
        2,
        "ids",
    ) == [
        "a",
        "b",
    ]


def test_bids_parse_entities_plain_tsv_and_ignores_invalid_tokens() -> None:
    assert bids.parse_bids_entities(
        "sub-01_badtoken_task-demo_recording-eye+right_physio.tsv"
    ) == {
        "sub": "01",
        "task": "demo",
        "recording": "eye+right",
    }


def test_bids_preserved_extra_column_collision_is_prefixed(
    tmp_path: Path,
) -> None:
    metadata = _metadata(
        Columns=[
            "timestamp",
            "x_coordinate",
            "y_coordinate",
            "participant",
        ],
        participant={
            "Units": "arbitrary",
        },
    )

    source, _ = _write_record(
        tmp_path,
        "sub-01_recording-eye1_physio.tsv",
        rows=[
            [0.0, 1.0, 2.0, "source-participant"],
            [1.0, 2.0, 3.0, "source-participant"],
        ],
        metadata=metadata,
    )

    record = bids.read_bids_eyetrack(
        source,
        participant_id="canonical",
    )

    assert set(
        record.study.data["participant"]
    ) == {
        "canonical",
    }

    assert list(
        record.study.data["bids_participant"]
    ) == [
        "source-participant",
        "source-participant",
    ]


def test_bids_microseconds_are_converted_to_milliseconds(
    tmp_path: Path,
) -> None:
    metadata = _metadata(
        timestamp={
            "Units": "us",
        }
    )

    source, _ = _write_record(
        tmp_path,
        "sub-01_recording-eye1_physio.tsv",
        rows=[
            [1000.0, 1.0, 2.0, 3.0],
            [2000.0, 2.0, 3.0, 3.0],
        ],
        metadata=metadata,
    )

    record = bids.read_bids_eyetrack(
        source
    )

    np.testing.assert_allclose(
        record.study.data["timestamp"],
        [
            1.0,
            2.0,
        ],
    )


def test_bids_decreasing_time_fails_canonical_validation(
    tmp_path: Path,
) -> None:
    source, _ = _write_record(
        tmp_path,
        "sub-01_recording-eye1_physio.tsv",
        rows=[
            [10.0, 1.0, 2.0, 3.0],
            [0.0, 2.0, 3.0, 3.0],
        ],
    )

    with pytest.raises(
        ValueError,
        match="timestamps decrease",
    ):
        bids.read_bids_eyetrack(
            source
        )


def test_bids_read_many_supports_explicit_ids_and_no_preservation(
    tmp_path: Path,
) -> None:
    first, _ = _write_record(
        tmp_path,
        "sub-01_recording-eye1_physio.tsv",
    )

    second, _ = _write_record(
        tmp_path,
        "sub-02_recording-eye1_physio.tsv",
    )

    study, records = bids.read_bids_eyetrack_many(
        [
            first,
            second,
        ],
        participant_ids=[
            "pA",
            "pB",
        ],
        trial_ids=[
            "trial-A",
            "trial-B",
        ],
        preserve_columns=False,
    )

    assert set(
        study.data["participant"]
    ) == {
        "pA",
        "pB",
    }

    assert set(
        study.data["trial"]
    ) == {
        "trial-A",
        "trial-B",
    }

    assert len(records) == 2
    assert "bids_timestamp" not in study.data


# ======================================================================
# Pedrotti redundant source transport
# ======================================================================


def _md5(payload: bytes) -> str:
    return hashlib.md5(
        payload,
        usedforsecurity=False,
    ).hexdigest()


class _Response:
    def __init__(
        self,
        chunks: list[bytes],
    ) -> None:
        self._chunks = list(chunks)

    def __enter__(self) -> "_Response":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> bool:
        return False

    def read(
        self,
        size: int = -1,
    ) -> bytes:
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        True,
        1.5,
    ],
)
def test_prefetch_max_attempts_requires_positive_integer(
    tmp_path: Path,
    value: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            tmp_path,
            max_attempts=value,  # type: ignore[arg-type]
        )


def test_prefetch_validates_backoff_and_timeout(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            tmp_path,
            initial_backoff_seconds=-0.01,
        )

    with pytest.raises(
        ValueError,
        match="timeout_seconds",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            tmp_path,
            timeout_seconds=0.0,
        )


def test_prefetch_rejects_existing_file_as_output_dir(
    tmp_path: Path,
) -> None:
    target = tmp_path / "not-a-directory"
    target.write_text(
        "x",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="directory path",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            target
        )


def test_prefetch_rejects_empty_frozen_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        prefetch,
        "expected_pedrotti_md5",
        lambda: {},
    )

    with pytest.raises(
        ValueError,
        match="contract is empty",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            tmp_path
        )


@pytest.mark.parametrize(
    ("name", "digest", "message"),
    [
        (123, "0" * 32, "structurally invalid"),
        ("01.txt", 123, "structurally invalid"),
        ("", "0" * 32, "unsafe"),
        (".", "0" * 32, "unsafe"),
        ("..", "0" * 32, "unsafe"),
        ("a/b.txt", "0" * 32, "unsafe"),
        ("a\\b.txt", "0" * 32, "unsafe"),
        ("01.txt", "xyz", "MD5 is invalid"),
        ("01.txt", "A" * 32, "MD5 is invalid"),
    ],
)
def test_frozen_pedrotti_identity_validation(
    name: object,
    digest: object,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        prefetch._validate_frozen_file_identity(
            name,  # type: ignore[arg-type]
            digest,  # type: ignore[arg-type]
        )


def test_prefetch_rejects_unexpected_existing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()

    (root / "unexpected.txt").write_text(
        "unexpected",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        prefetch,
        "expected_pedrotti_md5",
        lambda: {
            "01.txt": _md5(b"expected"),
        },
    )

    with pytest.raises(
        ValueError,
        match="unexpected entries",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            root
        )


def test_prefetch_rejects_unexpected_existing_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()

    (root / "nested").mkdir()

    monkeypatch.setattr(
        prefetch,
        "expected_pedrotti_md5",
        lambda: {
            "01.txt": _md5(b"expected"),
        },
    )

    with pytest.raises(
        ValueError,
        match="unexpected entries",
    ):
        prefetch.prefetch_pedrotti_source_bytes(
            root
        )


def test_prefetch_removes_bad_existing_file_and_downloads_exact_bytes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()

    destination = root / "01.txt"

    destination.write_bytes(
        b"wrong-existing"
    )

    correct = b"correct-new-payload"

    monkeypatch.setattr(
        prefetch,
        "expected_pedrotti_md5",
        lambda: {
            "01.txt": _md5(correct),
        },
    )

    monkeypatch.setattr(
        prefetch,
        "urlopen",
        lambda request, timeout: _Response(
            [
                correct[:5],
                correct[5:],
            ]
        ),
    )

    summary = prefetch.prefetch_pedrotti_source_bytes(
        root,
        max_attempts=1,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )

    assert destination.read_bytes() == correct
    assert summary["removed_mismatched_files"] == 1
    assert summary["retained_verified_files"] == 0
    assert summary["request_attempts"] == 1
    assert summary["route_attempts"] == {
        "api_content": 1,
        "public_record": 0,
    }


def test_download_first_attempt_success_returns_route_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = b"payload"
    target = tmp_path / "01.txt"

    monkeypatch.setattr(
        prefetch,
        "urlopen",
        lambda request, timeout: _Response(
            [
                payload,
            ]
        ),
    )

    attempts, routes = prefetch._download_verified_file_redundant(
        "01.txt",
        target,
        expected_md5=_md5(payload),
        max_attempts=3,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )

    assert attempts == 1
    assert routes == (
        "api_content",
    )

    assert target.read_bytes() == payload


def test_download_cleans_stale_partial_before_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = b"fresh"
    target = tmp_path / "01.txt"

    stale = tmp_path / "01.txt.part"
    stale.write_bytes(
        b"stale"
    )

    monkeypatch.setattr(
        prefetch,
        "urlopen",
        lambda request, timeout: _Response(
            [
                payload,
            ]
        ),
    )

    prefetch._download_verified_file_redundant(
        "01.txt",
        target,
        expected_md5=_md5(payload),
        max_attempts=1,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )

    assert not stale.exists()
    assert target.read_bytes() == payload


def test_download_retries_urlerror_with_exponential_backoff(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = b"eventual-success"
    calls = 0
    sleeps: list[float] = []

    def fake_open(
        request: object,
        timeout: float,
    ) -> _Response:
        nonlocal calls
        calls += 1

        if calls < 3:
            raise URLError(
                "temporary"
            )

        return _Response(
            [
                payload,
            ]
        )

    monkeypatch.setattr(
        prefetch,
        "urlopen",
        fake_open,
    )

    monkeypatch.setattr(
        prefetch.time,
        "sleep",
        sleeps.append,
    )

    attempts, routes = prefetch._download_verified_file_redundant(
        "01.txt",
        tmp_path / "01.txt",
        expected_md5=_md5(payload),
        max_attempts=3,
        initial_backoff_seconds=0.25,
        timeout_seconds=1.0,
    )

    assert attempts == 3

    assert routes == (
        "api_content",
        "public_record",
        "api_content",
    )

    assert sleeps == [
        0.25,
        0.5,
    ]


def test_md5_file_supports_multichunk_file(
    tmp_path: Path,
) -> None:
    payload = (
        b"a" * (1024 * 1024)
        + b"tail"
    )

    path = tmp_path / "payload.bin"
    path.write_bytes(payload)

    assert prefetch._md5_file(path) == _md5(
        payload
    )


def test_transfer_routes_url_encode_filename() -> None:
    routes = prefetch._transfer_routes(
        "file name.txt"
    )

    assert "file%20name.txt" in routes[0][1]
    assert "file%20name.txt" in routes[1][1]