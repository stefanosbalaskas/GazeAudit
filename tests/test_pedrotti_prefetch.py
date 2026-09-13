from __future__ import annotations

import hashlib
from urllib.error import HTTPError

import pytest

import gazeaudit.pedrotti_prefetch as prefetch


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._read = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self._payload
        if self._read:
            return b""
        self._read = True
        return self._payload


def _md5(payload: bytes) -> str:
    return hashlib.md5(payload, usedforsecurity=False).hexdigest()


def test_prefetch_falls_back_from_api_content_to_public_record(tmp_path, monkeypatch):
    payload = b"frozen bytes\n"
    expected = {"01.txt": _md5(payload)}
    calls: list[str] = []

    def fake_urlopen(request, timeout):
        assert timeout > 0
        calls.append(request.full_url)
        if "/api/records/7962917/files/01.txt/content" in request.full_url:
            raise HTTPError(request.full_url, 504, "Gateway Time-out", None, None)
        if request.full_url == "https://zenodo.org/records/7962917/files/01.txt?download=1":
            return _Response(payload)
        raise AssertionError(request.full_url)

    monkeypatch.setattr(prefetch, "urlopen", fake_urlopen)
    monkeypatch.setattr(prefetch, "expected_pedrotti_md5", lambda: dict(expected))
    monkeypatch.setattr(prefetch.time, "sleep", lambda seconds: None)

    summary = prefetch.prefetch_pedrotti_source_bytes(
        tmp_path / "source",
        max_attempts=2,
        initial_backoff_seconds=0.01,
        timeout_seconds=1.0,
    )

    assert calls == [
        "https://zenodo.org/api/records/7962917/files/01.txt/content",
        "https://zenodo.org/records/7962917/files/01.txt?download=1",
    ]
    assert summary["request_attempts"] == 2
    assert summary["route_attempts"] == {"api_content": 1, "public_record": 1}
    assert summary["scientific_endpoint_evaluated"] is False
    assert (tmp_path / "source" / "01.txt").read_bytes() == payload


def test_prefetch_rejects_wrong_bytes_then_accepts_exact_fallback(tmp_path, monkeypatch):
    good = b"correct\n"
    expected = {"01.txt": _md5(good)}
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        assert timeout > 0
        calls += 1
        if calls == 1:
            return _Response(b"wrong\n")
        return _Response(good)

    monkeypatch.setattr(prefetch, "urlopen", fake_urlopen)
    monkeypatch.setattr(prefetch, "expected_pedrotti_md5", lambda: dict(expected))
    monkeypatch.setattr(prefetch.time, "sleep", lambda seconds: None)

    summary = prefetch.prefetch_pedrotti_source_bytes(
        tmp_path / "source",
        max_attempts=2,
        initial_backoff_seconds=0.01,
        timeout_seconds=1.0,
    )

    assert calls == 2
    assert summary["request_attempts"] == 2
    assert (tmp_path / "source" / "01.txt").read_bytes() == good
    assert not (tmp_path / "source" / "01.txt.part").exists()


def test_prefetch_fails_closed_when_all_routes_fail(tmp_path, monkeypatch):
    expected = {"01.txt": _md5(b"expected\n")}

    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, 504, "Gateway Time-out", None, None)

    monkeypatch.setattr(prefetch, "urlopen", fake_urlopen)
    monkeypatch.setattr(prefetch, "expected_pedrotti_md5", lambda: dict(expected))
    monkeypatch.setattr(prefetch.time, "sleep", lambda seconds: None)

    with pytest.raises(RuntimeError, match="via all routes"):
        prefetch.prefetch_pedrotti_source_bytes(
            tmp_path / "source",
            max_attempts=2,
            initial_backoff_seconds=0.01,
            timeout_seconds=1.0,
        )

    assert not (tmp_path / "source" / "01.txt").exists()
    assert not (tmp_path / "source" / "01.txt.part").exists()


def test_prefetch_retains_only_checksum_valid_existing_files(tmp_path, monkeypatch):
    payload = b"already here\n"
    expected = {"01.txt": _md5(payload)}
    root = tmp_path / "source"
    root.mkdir()
    (root / "01.txt").write_bytes(payload)

    monkeypatch.setattr(prefetch, "expected_pedrotti_md5", lambda: dict(expected))

    def forbidden_urlopen(request, timeout):
        raise AssertionError("network should not be used for verified retained files")

    monkeypatch.setattr(prefetch, "urlopen", forbidden_urlopen)
    summary = prefetch.prefetch_pedrotti_source_bytes(root, max_attempts=1)

    assert summary["retained_verified_files"] == 1
    assert summary["request_attempts"] == 0
    assert summary["route_attempts"] == {"api_content": 0, "public_record": 0}


def test_transfer_routes_are_exact_record_specific_and_safe():
    assert prefetch._transfer_routes("01.txt") == (
        (
            "api_content",
            "https://zenodo.org/api/records/7962917/files/01.txt/content",
        ),
        (
            "public_record",
            "https://zenodo.org/records/7962917/files/01.txt?download=1",
        ),
    )
    with pytest.raises(ValueError, match="unsafe frozen Pedrotti filename"):
        prefetch._transfer_routes("../01.txt")
