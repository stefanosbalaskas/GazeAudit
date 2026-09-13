"""Resumable, checksum-locked Zenodo transfer for the Pedrotti source freeze.

This transport layer is endpoint-blind. It only acquires the exact frozen Zenodo v1
bytes and verifies their published MD5 identities before source intake begins.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .pedrotti_source import (
    PEDROTTI_ZENODO_RECORD,
    build_pedrotti_source_manifest,
    expected_pedrotti_md5,
)

PEDROTTI_ZENODO_API = f"https://zenodo.org/api/records/{PEDROTTI_ZENODO_RECORD}"
_USER_AGENT = "GazeAudit/0.1 Pedrotti source-freeze transport"


def fetch_pedrotti_zenodo_source(
    output_dir: str | Path,
    *,
    max_attempts: int = 5,
    initial_backoff_seconds: float = 2.0,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Download and verify the exact frozen Pedrotti Zenodo v1 source set.

    Existing files are retained only when their MD5 digest already matches the frozen
    contract. Mismatched files are removed before retry. No source byte is modified.
    """

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer")
    if initial_backoff_seconds < 0:
        raise ValueError("initial_backoff_seconds must be non-negative")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    root = Path(output_dir)
    if root.exists() and not root.is_dir():
        raise ValueError("output_dir must be a directory path")
    root.mkdir(parents=True, exist_ok=True)

    expected = expected_pedrotti_md5()
    allowed_names = set(expected)
    unexpected = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() or (path.is_file() and path.name not in allowed_names)
    )
    if unexpected:
        raise ValueError(f"Pedrotti download directory contains unexpected entries: {unexpected!r}")

    metadata, metadata_attempts = _fetch_record_metadata(
        max_attempts=max_attempts,
        initial_backoff_seconds=initial_backoff_seconds,
        timeout_seconds=timeout_seconds,
    )
    remote = _verified_remote_contract(metadata, expected)

    retained = 0
    removed_mismatches = 0
    download_attempts = 0
    for name in sorted(expected):
        destination = root / name
        if destination.is_file():
            if _md5_file(destination) == expected[name]:
                retained += 1
                continue
            destination.unlink()
            removed_mismatches += 1
        attempts = _download_verified_file(
            remote[name],
            destination,
            expected_md5=expected[name],
            max_attempts=max_attempts,
            initial_backoff_seconds=initial_backoff_seconds,
            timeout_seconds=timeout_seconds,
        )
        download_attempts += attempts

    manifest = build_pedrotti_source_manifest(root)
    return {
        "record": PEDROTTI_ZENODO_RECORD,
        "file_count": manifest["file_count"],
        "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
        "metadata_attempts": metadata_attempts,
        "download_attempts": download_attempts,
        "retained_verified_files": retained,
        "removed_mismatched_files": removed_mismatches,
        "scientific_endpoint_evaluated": False,
    }


def _fetch_record_metadata(
    *,
    max_attempts: int,
    initial_backoff_seconds: float,
    timeout_seconds: float,
) -> tuple[dict[str, Any], int]:
    error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            request = Request(PEDROTTI_ZENODO_API, headers={"User-Agent": _USER_AGENT})
            with urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read()
            document = json.loads(payload.decode("utf-8"))
            if not isinstance(document, dict):
                raise ValueError("Zenodo record metadata must be a JSON object")
            if document.get("id") != PEDROTTI_ZENODO_RECORD:
                raise ValueError("Zenodo record metadata returned an unexpected record identity")
            return document, attempt
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            error = exc
            if attempt == max_attempts:
                break
            time.sleep(initial_backoff_seconds * (2 ** (attempt - 1)))
    raise RuntimeError("failed to retrieve frozen Pedrotti Zenodo metadata") from error


def _verified_remote_contract(
    metadata: dict[str, Any],
    expected: dict[str, str],
) -> dict[str, str]:
    files = metadata.get("files")
    if not isinstance(files, list):
        raise ValueError("Zenodo metadata does not contain a files list")
    remote: dict[str, str] = {}
    observed_md5: dict[str, str] = {}
    for record in files:
        if not isinstance(record, dict):
            raise ValueError("Zenodo file metadata must contain objects")
        name = record.get("key")
        checksum = record.get("checksum")
        links = record.get("links")
        if (
            not isinstance(name, str)
            or not isinstance(checksum, str)
            or not isinstance(links, dict)
        ):
            raise ValueError("Zenodo file metadata is structurally incomplete")
        if name in remote:
            raise ValueError(f"duplicate Zenodo filename in metadata: {name!r}")
        if not checksum.startswith("md5:"):
            raise ValueError(f"Zenodo checksum for {name!r} is not MD5")
        digest = checksum[4:].lower()
        url = links.get("content")
        if not isinstance(url, str) or not _trusted_zenodo_url(url):
            raise ValueError(f"Zenodo content link for {name!r} is not trusted")
        remote[name] = url
        observed_md5[name] = digest
    if set(remote) != set(expected):
        missing = sorted(set(expected).difference(remote))
        unexpected = sorted(set(remote).difference(expected))
        raise ValueError(
            f"Zenodo record file set differs from frozen contract; "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    if observed_md5 != expected:
        mismatched = sorted(name for name in expected if observed_md5.get(name) != expected[name])
        raise ValueError(f"Zenodo record MD5 metadata differs from frozen contract: {mismatched!r}")
    return remote


def _download_verified_file(
    url: str,
    destination: Path,
    *,
    expected_md5: str,
    max_attempts: int,
    initial_backoff_seconds: float,
    timeout_seconds: float,
) -> int:
    partial = destination.with_name(destination.name + ".part")
    error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            if partial.exists():
                partial.unlink()
            request = Request(url, headers={"User-Agent": _USER_AGENT})
            digest = hashlib.md5(usedforsecurity=False)
            with (
                urlopen(request, timeout=timeout_seconds) as response,
                partial.open("wb") as handle,
            ):
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
                    handle.write(chunk)
            if digest.hexdigest() != expected_md5:
                raise ValueError(f"downloaded MD5 mismatch for {destination.name!r}")
            os.replace(partial, destination)
            return attempt
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            error = exc
            if partial.exists():
                partial.unlink()
            if attempt == max_attempts:
                break
            time.sleep(initial_backoff_seconds * (2 ** (attempt - 1)))
    raise RuntimeError(f"failed to download frozen Pedrotti file {destination.name!r}") from error


def _trusted_zenodo_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in {"zenodo.org", "www.zenodo.org"}


def _md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
