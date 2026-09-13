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
    assert set(remote) == set(expected)

    bad = _metadata(expected)
    bad["files"][0]["checksum"] = "md5:" + "c" * 32
    with pytest.raises(ValueError, match="MD5 metadata differs"):
        _verified_remote_contract(bad, expected)


def test_remote_contract_rejects_untrusted_content_links():
    expected = {"01.txt": "a" * 32}
    metadata = _metadata(expected)
    metadata["files"][0]["links"]["content"] = "https://example.com/01.txt"
    with pytest.raises(ValueError, match="not trusted"):
        _verified_remote_contract(metadata, expected)

    assert _trusted_zenodo_url("https://zenodo.org/record/1")
    assert _trusted_zenodo_url("https://www.zenodo.org/record/1")
    assert not _trusted_zenodo_url("http://zenodo.org/record/1")
    assert not _trusted_zenodo_url("https://zenodo.org.example.com/record/1")
