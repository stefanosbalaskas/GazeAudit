from __future__ import annotations

import hashlib
import json
from urllib.error import HTTPError

import pytest

import gazeaudit.pedrotti_fetch as pedrotti_fetch


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._chunk_read = False

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self._payload
        if self._chunk_read:
            return b""
        self._chunk_read = True
        return self._payload


def _md5_bytes(payload: bytes) -> str:
    return hashlib.md5(payload, usedforsecurity=False).hexdigest()


def _record_html(expected: dict[str, str]) -> bytes:
    rows = []
    for name, digest in expected.items():
        rows.append(
            "<tr>"
            f'<td><a href="/records/7962917/files/{name}?download=1">{name}</a> '
            f"md5:{digest}</td>"
            "</tr>"
        )
    return (
        "<html><body>"
        "<div>10.5281/zenodo.7962917</div>"
        "<table>"
        + "".join(rows)
        + "</table></body></html>"
    ).encode("utf-8")


def test_public_record_html_reconstructs_exact_verified_remote_contract():
    expected = {"01.txt": "a" * 32, "readme.txt": "b" * 32}
    metadata = pedrotti_fetch._metadata_from_record_html(_record_html(expected))

    assert metadata["id"] == 7962917
    remote = pedrotti_fetch._verified_remote_contract(metadata, expected)
    assert remote == {
        "01.txt": "https://zenodo.org/records/7962917/files/01.txt?download=1",
        "readme.txt": "https://zenodo.org/records/7962917/files/readme.txt?download=1",
    }


def test_metadata_fetch_falls_back_to_record_html_after_api_transport_error(monkeypatch):
    expected = {"01.txt": "a" * 32}
    calls: list[str] = []

    def fake_urlopen(request, timeout):
        del timeout
        calls.append(request.full_url)
        if request.full_url == pedrotti_fetch.PEDROTTI_ZENODO_API:
            raise HTTPError(request.full_url, 504, "Gateway Time-out", None, None)
        if request.full_url == pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE:
            return _Response(_record_html(expected))
        raise AssertionError(f"unexpected URL: {request.full_url}")

    monkeypatch.setattr(pedrotti_fetch, "urlopen", fake_urlopen)
    metadata, attempts, source = pedrotti_fetch._fetch_record_metadata(
        max_attempts=1,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
    )

    assert attempts == 1
    assert source == "record_html"
    assert calls == [
        pedrotti_fetch.PEDROTTI_ZENODO_API,
        pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE,
    ]
    assert pedrotti_fetch._verified_remote_contract(metadata, expected)


def test_transport_only_metadata_outage_uses_frozen_checksum_contract(tmp_path, monkeypatch):
    payloads = {"01.txt": b"one\n", "readme.txt": b"readme\n"}
    expected = {name: _md5_bytes(payload) for name, payload in payloads.items()}
    metadata_calls: list[str] = []
    download_calls: list[str] = []

    def fake_urlopen(request, timeout):
        assert timeout > 0
        url = request.full_url
        if url in {
            pedrotti_fetch.PEDROTTI_ZENODO_API,
            pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE,
        }:
            metadata_calls.append(url)
            raise HTTPError(url, 504, "Gateway Time-out", None, None)
        for name, payload in payloads.items():
            if url == pedrotti_fetch._canonical_pedrotti_download_url(name):
                download_calls.append(name)
                return _Response(payload)
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(pedrotti_fetch, "urlopen", fake_urlopen)
    monkeypatch.setattr(pedrotti_fetch, "expected_pedrotti_md5", lambda: dict(expected))
    monkeypatch.setattr(
        pedrotti_fetch,
        "build_pedrotti_source_manifest",
        lambda root: {
            "file_count": len(expected),
            "source_manifest_fingerprint": "f" * 64,
        },
    )

    summary = pedrotti_fetch.fetch_pedrotti_zenodo_source(
        tmp_path / "download",
        max_attempts=1,
        initial_backoff_seconds=0.0,
        timeout_seconds=1.0,
        metadata_max_attempts=2,
        metadata_timeout_seconds=0.1,
    )

    assert metadata_calls == [
        pedrotti_fetch.PEDROTTI_ZENODO_API,
        pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE,
        pedrotti_fetch.PEDROTTI_ZENODO_API,
        pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE,
    ]
    assert sorted(download_calls) == sorted(expected)
    assert summary["metadata_source"] == "frozen_contract_after_metadata_outage"
    assert summary["metadata_attempts"] == 2
    assert summary["file_count"] == 2
    assert summary["scientific_endpoint_evaluated"] is False
    for name, payload in payloads.items():
        assert (tmp_path / "download" / name).read_bytes() == payload


def test_api_structural_identity_failure_does_not_fall_back(monkeypatch):
    calls: list[str] = []

    def fake_urlopen(request, timeout):
        del timeout
        calls.append(request.full_url)
        return _Response(json.dumps({"id": 1, "files": []}).encode("utf-8"))

    monkeypatch.setattr(pedrotti_fetch, "urlopen", fake_urlopen)
    with pytest.raises(ValueError, match="unexpected record identity"):
        pedrotti_fetch._fetch_record_metadata(
            max_attempts=1,
            initial_backoff_seconds=0.0,
            timeout_seconds=1.0,
        )

    assert calls == [pedrotti_fetch.PEDROTTI_ZENODO_API]


def test_invalid_record_html_after_api_outage_remains_hard_failure(monkeypatch):
    def fake_urlopen(request, timeout):
        del timeout
        if request.full_url == pedrotti_fetch.PEDROTTI_ZENODO_API:
            raise HTTPError(request.full_url, 504, "Gateway Time-out", None, None)
        if request.full_url == pedrotti_fetch.PEDROTTI_ZENODO_RECORD_PAGE:
            return _Response(b"<html><body>not the frozen record</body></html>")
        raise AssertionError(f"unexpected URL: {request.full_url}")

    monkeypatch.setattr(pedrotti_fetch, "urlopen", fake_urlopen)
    with pytest.raises(ValueError, match="record-page metadata failed validation"):
        pedrotti_fetch._fetch_record_metadata(
            max_attempts=1,
            initial_backoff_seconds=0.0,
            timeout_seconds=1.0,
        )


def test_record_html_must_bind_frozen_doi_and_exact_md5():
    expected = {"01.txt": "a" * 32}
    missing_doi = _record_html(expected).replace(b"10.5281/zenodo.7962917", b"other")
    with pytest.raises(ValueError, match="frozen DOI identity"):
        pedrotti_fetch._metadata_from_record_html(missing_doi)

    wrong_md5 = _record_html({"01.txt": "c" * 32})
    metadata = pedrotti_fetch._metadata_from_record_html(wrong_md5)
    with pytest.raises(ValueError, match="MD5 metadata differs"):
        pedrotti_fetch._verified_remote_contract(metadata, expected)


def test_record_specific_download_boundary_is_fail_closed():
    assert (
        pedrotti_fetch._pedrotti_record_download_name(
            "https://zenodo.org/records/7962917/files/01.txt?download=1"
        )
        == "01.txt"
    )
    assert pedrotti_fetch._pedrotti_record_download_name(
        "https://zenodo.org/records/1/files/01.txt?download=1"
    ) is None
    assert pedrotti_fetch._pedrotti_record_download_name(
        "https://zenodo.org/records/7962917/files/01.txt"
    ) is None
    assert pedrotti_fetch._pedrotti_record_download_name(
        "https://example.com/records/7962917/files/01.txt?download=1"
    ) is None
    assert (
        pedrotti_fetch._canonical_pedrotti_download_url("01.txt")
        == "https://zenodo.org/records/7962917/files/01.txt?download=1"
    )


def test_record_html_rejects_ambiguous_download_links():
    html = b"""
    <html><body>
      <div>10.5281/zenodo.7962917</div>
      <table><tr><td>
        <a href="/records/7962917/files/01.txt?download=1">01.txt</a>
        <a href="/records/7962917/files/02.txt?download=1">02.txt</a>
        md5:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      </td></tr></table>
    </body></html>
    """
    with pytest.raises(ValueError, match="ambiguous download links"):
        pedrotti_fetch._metadata_from_record_html(html)
