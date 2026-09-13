from __future__ import annotations

import pytest

from gazeaudit.pedrotti_fetch import _trusted_zenodo_url, _verified_remote_contract


def _metadata(expected: dict[str, str]) -> dict[str, object]:
    return {
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
        ]
    }


def test_remote_contract_requires_exact_file_and_md5_identity():
    expected = {"01.txt": "a" * 32, "readme.txt": "b" * 32}
    remote = _verified_remote_contract(_metadata(expected), expected)
    assert remote == {
        "01.txt": "https://zenodo.org/records/7962917/files/01.txt?download=1",
        "readme.txt": "https://zenodo.org/records/7962917/files/readme.txt?download=1",
    }

    bad = _metadata(expected)
    bad["files"][0]["checksum"] = "md5:" + "c" * 32
    with pytest.raises(ValueError, match="MD5 metadata differs"):
        _verified_remote_contract(bad, expected)


def test_remote_contract_does_not_trust_mutable_metadata_content_links():
    expected = {"01.txt": "a" * 32}
    metadata = _metadata(expected)
    metadata["files"][0]["links"]["content"] = "https://example.com/01.txt"

    remote = _verified_remote_contract(metadata, expected)
    assert remote == {
        "01.txt": "https://zenodo.org/records/7962917/files/01.txt?download=1"
    }

    metadata["files"][0].pop("links")
    assert _verified_remote_contract(metadata, expected) == remote

    assert _trusted_zenodo_url("https://zenodo.org/record/1")
    assert _trusted_zenodo_url("https://www.zenodo.org/record/1")
    assert not _trusted_zenodo_url("http://zenodo.org/record/1")
    assert not _trusted_zenodo_url("https://zenodo.org.example.com/record/1")


def test_remote_contract_rejects_unsafe_filename_even_with_matching_md5():
    expected = {"../01.txt": "a" * 32}
    with pytest.raises(ValueError, match="unsafe Zenodo filename"):
        _verified_remote_contract(_metadata(expected), expected)
