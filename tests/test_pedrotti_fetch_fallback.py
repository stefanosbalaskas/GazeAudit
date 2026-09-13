from __future__ import annotations

import json
from urllib.error import HTTPError

import pytest

import gazeaudit.pedrotti_fetch as pedrotti_fetch


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


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


def test_record_html_must_bind_frozen_doi_and_exact_md5():
    expected = {"01.txt": "a" * 32}
    missing_doi = _record_html(expected).replace(b"10.5281/zenodo.7962917", b"other")
    with pytest.raises(ValueError, match="frozen DOI identity"):
        pedrotti_fetch._metadata_from_record_html(missing_doi)

    wrong_md5 = _record_html({"01.txt": "c" * 32})
    metadata = pedrotti_fetch._metadata_from_record_html(wrong_md5)
    with pytest.raises(ValueError, match="MD5 metadata differs"):
        pedrotti_fetch._verified_remote_contract(metadata, expected)


def test_record_specific_file_url_validation_is_fail_closed():
    assert pedrotti_fetch._trusted_pedrotti_file_url(
        "https://zenodo.org/api/records/7962917/files/01.txt/content", "01.txt"
    )
    assert pedrotti_fetch._trusted_pedrotti_file_url(
        "https://zenodo.org/records/7962917/files/01.txt?download=1", "01.txt"
    )
    assert not pedrotti_fetch._trusted_pedrotti_file_url(
        "https://zenodo.org/records/1/files/01.txt?download=1", "01.txt"
    )
    assert not pedrotti_fetch._trusted_pedrotti_file_url(
        "https://zenodo.org/records/7962917/files/02.txt?download=1", "01.txt"
    )
    assert not pedrotti_fetch._trusted_pedrotti_file_url(
        "https://zenodo.org/records/7962917/files/01.txt?download=1&other=1", "01.txt"
    )
    assert not pedrotti_fetch._trusted_pedrotti_file_url(
        "https://example.com/records/7962917/files/01.txt?download=1", "01.txt"
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
