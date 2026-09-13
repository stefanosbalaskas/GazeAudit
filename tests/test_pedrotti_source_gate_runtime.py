from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from urllib.error import URLError

import pandas as pd

from gazeaudit import pedrotti_fetch as fetch_module
from gazeaudit import pedrotti_source as source_module
from gazeaudit.pedrotti_freeze_cli import main as freeze_cli_main
from gazeaudit.pedrotti_source import inspect_pedrotti_source, write_pedrotti_source_intake_artifacts
from gazeaudit.pedrotti_source_cli import main as source_cli_main


_COLUMNS = [
    "TRIAL_INDEX",
    "LEFT_GAZE_X",
    "LEFT_GAZE_Y",
    "LEFT_PUPIL_SIZE",
    "RIGHT_GAZE_X",
    "RIGHT_GAZE_Y",
    "RIGHT_PUPIL_SIZE",
    "TIMESTAMP",
    "TrialTextShown",
]


class _Response:
    def __init__(self, payload: bytes):
        self._stream = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)


def _md5_bytes(payload: bytes) -> str:
    return hashlib.md5(payload, usedforsecurity=False).hexdigest()


def _write_synthetic_source(root: Path) -> dict[str, str]:
    root.mkdir()
    for participant in range(1, 37):
        rows = []
        for trial in range(1, 97):
            stimulus = "1,234" if trial == 1 else "12,345,678" if trial == 2 else f"word-{trial}"
            rows.append(
                {
                    "TRIAL_INDEX": trial,
                    "LEFT_GAZE_X": float(trial),
                    "LEFT_GAZE_Y": float(trial + 1),
                    "LEFT_PUPIL_SIZE": 1000.0,
                    "RIGHT_GAZE_X": ".",
                    "RIGHT_GAZE_Y": ".",
                    "RIGHT_PUPIL_SIZE": ".",
                    "TIMESTAMP": float(trial * 1000),
                    "TrialTextShown": stimulus,
                }
            )
        pd.DataFrame(rows, columns=_COLUMNS).to_csv(root / f"{participant:02d}.txt", index=False)
    (root / "readme.txt").write_text("synthetic endpoint-blind source fixture\n", encoding="utf-8")
    return {
        path.name: hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()
        for path in root.iterdir()
        if path.is_file()
    }


def test_source_and_freeze_clis_execute_endpoint_blind(tmp_path, monkeypatch, capsys):
    source_dir = tmp_path / "source"
    expected = _write_synthetic_source(source_dir)
    monkeypatch.setattr(source_module, "expected_pedrotti_md5", lambda: dict(expected))

    cli_intake = tmp_path / "cli-intake"
    assert source_cli_main(
        ["--source-dir", str(source_dir), "--output-dir", str(cli_intake)]
    ) == 0
    source_status = json.loads(capsys.readouterr().out)
    assert source_status["status"] == "source_intake_archived"
    assert source_status["scientific_endpoint_evaluated"] is False

    intake = inspect_pedrotti_source(source_dir)
    intake_dir = tmp_path / "intake"
    write_pedrotti_source_intake_artifacts(intake, intake_dir)
    environment = tmp_path / "pip-freeze.txt"
    environment.write_text("gazeaudit==0.1.0.dev19\npandas==2.3.3\n", encoding="utf-8")

    freeze_dir = tmp_path / "freeze"
    assert freeze_cli_main(
        [
            "--intake-dir",
            str(intake_dir),
            "--output-dir",
            str(freeze_dir),
            "--environment-file",
            str(environment),
            "--execution-commit",
            "a" * 40,
            "--run-id",
            "123456",
            "--runner-os",
            "Linux",
            "--runner-arch",
            "X64",
        ]
    ) == 0
    freeze_status = json.loads(capsys.readouterr().out)
    assert freeze_status["status"] == "source_freeze_archived"
    assert freeze_status["scientific_endpoint_evaluated"] is False
    assert (freeze_dir / "freeze_manifest.json").is_file()


def test_fetch_transport_downloads_retains_and_repairs_files(tmp_path, monkeypatch):
    payloads = {
        "01.txt": b"one\n",
        "readme.txt": b"readme\n",
    }
    expected = {name: _md5_bytes(payload) for name, payload in payloads.items()}
    metadata = {
        "id": fetch_module.PEDROTTI_ZENODO_RECORD,
        "files": [
            {
                "key": name,
                "checksum": f"md5:{digest}",
                "links": {
                    "content": (
                        f"https://zenodo.org/api/records/7962917/files/{name}/content"
                    )
                },
            }
            for name, digest in expected.items()
        ],
    }
    metadata_bytes = json.dumps(metadata).encode("utf-8")
    content_calls: list[str] = []

    def fake_urlopen(request, timeout):
        assert timeout > 0
        url = request.full_url
        if url == fetch_module.PEDROTTI_ZENODO_API:
            return _Response(metadata_bytes)
        name = url.rsplit("/", 2)[-2]
        content_calls.append(name)
        return _Response(payloads[name])

    monkeypatch.setattr(fetch_module, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_module, "expected_pedrotti_md5", lambda: dict(expected))
    monkeypatch.setattr(
        fetch_module,
        "build_pedrotti_source_manifest",
        lambda root: {
            "file_count": len(expected),
            "source_manifest_fingerprint": "f" * 64,
        },
    )

    root = tmp_path / "download"
    first = fetch_module.fetch_pedrotti_zenodo_source(
        root,
        max_attempts=2,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )
    assert first["file_count"] == 2
    assert first["download_attempts"] == 2
    assert first["retained_verified_files"] == 0
    assert first["removed_mismatched_files"] == 0
    assert first["scientific_endpoint_evaluated"] is False
    assert sorted(content_calls) == ["01.txt", "readme.txt"]

    content_calls.clear()
    second = fetch_module.fetch_pedrotti_zenodo_source(
        root,
        max_attempts=2,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )
    assert second["retained_verified_files"] == 2
    assert second["download_attempts"] == 0
    assert content_calls == []

    (root / "01.txt").write_bytes(b"corrupt\n")
    third = fetch_module.fetch_pedrotti_zenodo_source(
        root,
        max_attempts=2,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )
    assert third["retained_verified_files"] == 1
    assert third["removed_mismatched_files"] == 1
    assert third["download_attempts"] == 1
    assert content_calls == ["01.txt"]
    assert (root / "01.txt").read_bytes() == payloads["01.txt"]


def test_fetch_metadata_retry_and_validation_fail_closed(monkeypatch):
    attempts = 0
    metadata = {
        "id": fetch_module.PEDROTTI_ZENODO_RECORD,
        "files": [],
    }

    def flaky_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise URLError("synthetic transient failure")
        return _Response(json.dumps(metadata).encode("utf-8"))

    monkeypatch.setattr(fetch_module, "urlopen", flaky_urlopen)
    monkeypatch.setattr(fetch_module.time, "sleep", lambda seconds: None)
    document, used_attempts = fetch_module._fetch_record_metadata(
        max_attempts=2,
        initial_backoff_seconds=0.01,
        timeout_seconds=1.0,
    )
    assert used_attempts == 2
    assert document["id"] == fetch_module.PEDROTTI_ZENODO_RECORD
