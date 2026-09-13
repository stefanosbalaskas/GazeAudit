"""Endpoint-blind redundant byte transport for the frozen Pedrotti source.

This helper exists only to improve source availability. It derives both transfer
routes locally from the frozen Zenodo record identity and accepts bytes only after
they match the published MD5 values already frozen in the protocol.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .pedrotti_source import PEDROTTI_ZENODO_RECORD, expected_pedrotti_md5

_USER_AGENT = "GazeAudit/0.1 Pedrotti source-freeze redundant transport"
_MD5_HEX_RE = re.compile(r"^[0-9a-f]{32}$")


def prefetch_pedrotti_source_bytes(
    output_dir: str | Path,
    *,
    max_attempts: int = 6,
    initial_backoff_seconds: float = 5.0,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Acquire the exact frozen files through redundant Zenodo byte routes.

    The REST file-content route and public record-file route are deterministic
    representations of the same frozen Zenodo record. They are alternated across
    bounded attempts. A response is never accepted merely because transport
    succeeded: its complete byte stream must match the frozen published MD5.
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
    if not expected:
        raise ValueError("frozen Pedrotti file contract is empty")
    for name, digest in expected.items():
        _validate_frozen_file_identity(name, digest)

    allowed = set(expected)
    unexpected = sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() or (path.is_file() and path.name not in allowed)
    )
    if unexpected:
        raise ValueError(f"Pedrotti prefetch directory contains unexpected entries: {unexpected!r}")

    retained = 0
    removed_mismatches = 0
    request_attempts = 0
    route_attempts = {"api_content": 0, "public_record": 0}

    for name in sorted(expected):
        destination = root / name
        if destination.is_file():
            if _md5_file(destination) == expected[name]:
                retained += 1
                continue
            destination.unlink()
            removed_mismatches += 1

        attempts, used_routes = _download_verified_file_redundant(
            name,
            destination,
            expected_md5=expected[name],
            max_attempts=max_attempts,
            initial_backoff_seconds=initial_backoff_seconds,
            timeout_seconds=timeout_seconds,
        )
        request_attempts += attempts
        for route in used_routes:
            route_attempts[route] += 1

    return {
        "record": PEDROTTI_ZENODO_RECORD,
        "file_count": len(expected),
        "request_attempts": request_attempts,
        "route_attempts": route_attempts,
        "retained_verified_files": retained,
        "removed_mismatched_files": removed_mismatches,
        "scientific_endpoint_evaluated": False,
    }


def _validate_frozen_file_identity(name: str, digest: str) -> None:
    if not isinstance(name, str) or not isinstance(digest, str):
        raise ValueError("frozen Pedrotti file contract is structurally invalid")
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError(f"unsafe frozen Pedrotti filename: {name!r}")
    if _MD5_HEX_RE.fullmatch(digest) is None:
        raise ValueError(f"frozen Pedrotti MD5 is invalid for {name!r}")


def _transfer_routes(name: str) -> tuple[tuple[str, str], tuple[str, str]]:
    _validate_frozen_file_identity(name, "0" * 32)
    encoded = quote(name, safe="")
    return (
        (
            "api_content",
            f"https://zenodo.org/api/records/{PEDROTTI_ZENODO_RECORD}/files/{encoded}/content",
        ),
        (
            "public_record",
            f"https://zenodo.org/records/{PEDROTTI_ZENODO_RECORD}/files/{encoded}?download=1",
        ),
    )


def _download_verified_file_redundant(
    name: str,
    destination: Path,
    *,
    expected_md5: str,
    max_attempts: int,
    initial_backoff_seconds: float,
    timeout_seconds: float,
) -> tuple[int, tuple[str, ...]]:
    routes = _transfer_routes(name)
    partial = destination.with_name(destination.name + ".part")
    error: Exception | None = None
    used_routes: list[str] = []

    for attempt in range(1, max_attempts + 1):
        route_name, url = routes[(attempt - 1) % len(routes)]
        used_routes.append(route_name)
        try:
            if partial.exists():
                partial.unlink()
            request = Request(
                url,
                headers={"User-Agent": _USER_AGENT, "Accept": "application/octet-stream"},
            )
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
                raise ValueError(f"downloaded MD5 mismatch for {name!r} via {route_name}")
            os.replace(partial, destination)
            return attempt, tuple(used_routes)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            error = exc
            if partial.exists():
                partial.unlink()
            if attempt == max_attempts:
                break
            time.sleep(initial_backoff_seconds * (2 ** (attempt - 1)))

    raise RuntimeError(
        f"failed to download frozen Pedrotti file {name!r} via all routes"
    ) from error


def _md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
