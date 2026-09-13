"""Resumable, checksum-locked Zenodo transfer for the Pedrotti source freeze.

This transport layer is endpoint-blind. It only acquires the exact frozen Zenodo v1
bytes and verifies their published MD5 identities before source intake begins.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from .pedrotti_source import (
    PEDROTTI_ZENODO_DOI,
    PEDROTTI_ZENODO_RECORD,
    build_pedrotti_source_manifest,
    expected_pedrotti_md5,
)

PEDROTTI_ZENODO_API = f"https://zenodo.org/api/records/{PEDROTTI_ZENODO_RECORD}"
PEDROTTI_ZENODO_RECORD_PAGE = f"https://zenodo.org/records/{PEDROTTI_ZENODO_RECORD}"
_USER_AGENT = "GazeAudit/0.1 Pedrotti source-freeze transport"
_MD5_RE = re.compile(r"\bmd5:([0-9a-fA-F]{32})\b")
_MD5_HEX_RE = re.compile(r"^[0-9a-f]{32}$")


class _ZenodoMetadataUnavailable(RuntimeError):
    """Signal a transport-only outage after all metadata paths are exhausted."""


class _ZenodoFileTableParser(HTMLParser):
    """Collect table-row text and links from the public Zenodo record page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._row_depth = 0
        self._text: list[str] = []
        self._links: list[str] = []
        self.rows: list[tuple[str, tuple[str, ...]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            if self._row_depth == 0:
                self._text = []
                self._links = []
            self._row_depth += 1
            return
        if tag == "a" and self._row_depth > 0:
            href = dict(attrs).get("href")
            if isinstance(href, str):
                self._links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag != "tr" or self._row_depth == 0:
            return
        self._row_depth -= 1
        if self._row_depth == 0:
            text = " ".join(part.strip() for part in self._text if part.strip())
            self.rows.append((text, tuple(self._links)))

    def handle_data(self, data: str) -> None:
        if self._row_depth > 0:
            self._text.append(data)


def fetch_pedrotti_zenodo_source(
    output_dir: str | Path,
    *,
    max_attempts: int = 5,
    initial_backoff_seconds: float = 2.0,
    timeout_seconds: float = 120.0,
    metadata_max_attempts: int = 2,
    metadata_timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Download and verify the exact frozen Pedrotti Zenodo v1 source set.

    Existing files are retained only when their MD5 digest already matches the frozen
    contract. Mismatched files are removed before retry. No source byte is modified.

    The canonical Zenodo REST record endpoint is the primary metadata source. If that
    endpoint fails with a transport-level error, the public record page is an allowed
    metadata fallback. If both metadata surfaces remain unavailable after bounded
    retries, acquisition may continue from the pre-frozen record/file/MD5 contract,
    because every downloaded byte must still match that contract before source intake.
    Any metadata response that is received but fails structural or identity validation
    remains a hard failure. Download URLs are reconstructed deterministically from the
    frozen record identity rather than trusting mutable metadata link representations.
    """

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer")
    if initial_backoff_seconds < 0:
        raise ValueError("initial_backoff_seconds must be non-negative")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if (
        not isinstance(metadata_max_attempts, int)
        or isinstance(metadata_max_attempts, bool)
        or metadata_max_attempts < 1
    ):
        raise ValueError("metadata_max_attempts must be a positive integer")
    if metadata_timeout_seconds <= 0:
        raise ValueError("metadata_timeout_seconds must be positive")

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

    try:
        metadata, metadata_attempts, metadata_source = _fetch_record_metadata(
            max_attempts=metadata_max_attempts,
            initial_backoff_seconds=initial_backoff_seconds,
            timeout_seconds=metadata_timeout_seconds,
        )
    except _ZenodoMetadataUnavailable:
        metadata_attempts = metadata_max_attempts
        metadata_source = "frozen_contract_after_metadata_outage"
        remote = _remote_contract_from_frozen_contract(expected)
    else:
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
        "metadata_source": metadata_source,
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
) -> tuple[dict[str, Any], int, str]:
    """Retrieve metadata; distinguish transport outage from identity failure."""

    error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            document = _fetch_json_record_once(timeout_seconds)
            return document, attempt, "api"
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            error = exc

        try:
            document = _fetch_record_page_metadata_once(timeout_seconds)
            return document, attempt, "record_html"
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            error = exc
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError(
                "Zenodo API was unavailable and public record-page metadata failed validation"
            ) from exc

        if attempt != max_attempts:
            time.sleep(initial_backoff_seconds * (2 ** (attempt - 1)))

    raise _ZenodoMetadataUnavailable(
        "failed to retrieve frozen Pedrotti Zenodo metadata from live transport surfaces"
    ) from error


def _fetch_json_record_once(timeout_seconds: float) -> dict[str, Any]:
    request = Request(
        PEDROTTI_ZENODO_API,
        headers={"User-Agent": _USER_AGENT, "Accept": "application/json"},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
    document = json.loads(payload.decode("utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Zenodo record metadata must be a JSON object")
    if document.get("id") != PEDROTTI_ZENODO_RECORD:
        raise ValueError("Zenodo record metadata returned an unexpected record identity")
    return document


def _fetch_record_page_metadata_once(timeout_seconds: float) -> dict[str, Any]:
    request = Request(
        PEDROTTI_ZENODO_RECORD_PAGE,
        headers={"User-Agent": _USER_AGENT, "Accept": "text/html"},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
    return _metadata_from_record_html(payload)


def _metadata_from_record_html(payload: bytes) -> dict[str, Any]:
    """Build a REST-compatible file contract from the public Zenodo record file table."""

    text = payload.decode("utf-8")
    if PEDROTTI_ZENODO_DOI not in text:
        raise ValueError("Zenodo record page does not contain the frozen DOI identity")

    parser = _ZenodoFileTableParser()
    parser.feed(text)
    files: list[dict[str, Any]] = []
    observed: set[str] = set()
    for row_text, links in parser.rows:
        checksum_match = _MD5_RE.search(row_text)
        if checksum_match is None:
            continue
        candidate_links: list[tuple[str, str]] = []
        for href in links:
            absolute = urljoin(PEDROTTI_ZENODO_RECORD_PAGE, href)
            name = _pedrotti_record_download_name(absolute)
            if name is not None:
                candidate_links.append((name, absolute))
        if not candidate_links:
            continue
        unique = {(name, url) for name, url in candidate_links}
        if len(unique) != 1:
            raise ValueError("Zenodo record page file row has ambiguous download links")
        name, url = unique.pop()
        if name in observed:
            raise ValueError(f"duplicate Zenodo filename in record page: {name!r}")
        observed.add(name)
        files.append(
            {
                "key": name,
                "checksum": f"md5:{checksum_match.group(1).lower()}",
                "links": {"content": url},
            }
        )

    if not files:
        raise ValueError("Zenodo record page does not expose a verifiable file table")
    return {"id": PEDROTTI_ZENODO_RECORD, "files": files}


def _pedrotti_record_download_name(url: str) -> str | None:
    """Return the filename only for the exact public-record download URL shape."""

    if not _trusted_zenodo_url(url):
        return None
    parsed = urlparse(url)
    prefix = f"/records/{PEDROTTI_ZENODO_RECORD}/files/"
    if not parsed.path.startswith(prefix):
        return None
    encoded_name = parsed.path[len(prefix) :]
    if not encoded_name or "/" in encoded_name:
        return None
    name = unquote(encoded_name)
    if not name or "/" in name or "\\" in name:
        return None
    query = parse_qs(parsed.query, keep_blank_values=True)
    if query.get("download") != ["1"]:
        return None
    return name


def _canonical_pedrotti_download_url(name: str) -> str:
    """Construct the immutable record-specific public download URL for a filename."""

    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError(f"unsafe Zenodo filename in metadata: {name!r}")
    encoded = quote(name, safe="")
    return f"{PEDROTTI_ZENODO_RECORD_PAGE}/files/{encoded}?download=1"


def _remote_contract_from_frozen_contract(expected: dict[str, str]) -> dict[str, str]:
    """Construct download URLs only from the pre-frozen filename/MD5 contract."""

    remote: dict[str, str] = {}
    for name, digest in expected.items():
        if not isinstance(name, str) or not isinstance(digest, str):
            raise ValueError("frozen Pedrotti file contract is structurally invalid")
        if _MD5_HEX_RE.fullmatch(digest) is None:
            raise ValueError(f"frozen Pedrotti MD5 is invalid for {name!r}")
        remote[name] = _canonical_pedrotti_download_url(name)
    if not remote:
        raise ValueError("frozen Pedrotti file contract is empty")
    return remote


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
        if not isinstance(name, str) or not isinstance(checksum, str):
            raise ValueError("Zenodo file metadata is structurally incomplete")
        if name in remote:
            raise ValueError(f"duplicate Zenodo filename in metadata: {name!r}")
        if not checksum.startswith("md5:"):
            raise ValueError(f"Zenodo checksum for {name!r} is not MD5")
        digest = checksum[4:].lower()
        remote[name] = _canonical_pedrotti_download_url(name)
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
