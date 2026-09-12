"""Resilient, endpoint-blind download of the frozen Korthals OSF source.

The companion repository writes directly to final paths and skips every existing
path when ``overwrite=False``. If a remote transfer fails after opening a file,
a partial file can therefore survive and be skipped by a naive in-process retry.
This module preserves the companion's exact public-source selection and path
contract while making retries safe: already-complete files are retained only
when their published OSF checksum matches, partial/mismatched files are removed,
and the remote inventory must remain unchanged throughout the download.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

KORTHALS_OSF_PROJECT_ID = "zx7hc"
KORTHALS_DATA_ROOT = Path("data")


@dataclass(frozen=True, order=True)
class KorthalsRemoteFile:
    """Immutable public-OSF identity needed for safe resumable transfer."""

    remote_path: str
    destination: str
    md5: str
    sha256: str | None


def _normalise_hash(value: Any, *, algorithm: str, remote_path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"OSF file {remote_path!r} is missing required {algorithm} checksum"
        )
    result = value.strip().lower()
    expected_length = 32 if algorithm == "md5" else 64
    if len(result) != expected_length or any(ch not in "0123456789abcdef" for ch in result):
        raise ValueError(
            f"OSF file {remote_path!r} has invalid {algorithm} checksum {value!r}"
        )
    return result


def _companion_destination(remote_file: Any) -> Path:
    """Reproduce the frozen companion's ``data{file_dir}/{file.name}`` mapping."""

    remote_path = str(remote_file.path)
    name = str(remote_file.name)
    if not remote_path.startswith("/") or not name or "/" in name or "\\" in name:
        raise ValueError(f"invalid OSF file identity: path={remote_path!r}, name={name!r}")
    file_dir = "/".join(remote_path.split("/")[:-1])
    destination = Path(f"data{file_dir}") / name
    if ".." in destination.parts:
        raise ValueError(f"OSF destination contains parent traversal: {destination}")
    try:
        destination.relative_to(KORTHALS_DATA_ROOT)
    except ValueError as exc:
        raise ValueError(f"OSF destination escapes data root: {destination}") from exc
    return destination


def _default_remote_inventory() -> tuple[KorthalsRemoteFile, ...]:
    """Read the current public OSF inventory without downloading scientific data."""

    from osfclient import OSF

    project = OSF().project(KORTHALS_OSF_PROJECT_ID)
    records: list[KorthalsRemoteFile] = []
    destinations: set[str] = set()
    remote_paths: set[str] = set()

    for storage in project.storages:
        for remote_file in list(storage.files):
            remote_path = str(remote_file.path)
            destination = _companion_destination(remote_file).as_posix()
            hashes = getattr(remote_file, "hashes", None)
            if not isinstance(hashes, dict):
                raise ValueError(f"OSF file {remote_path!r} has no checksum mapping")
            md5 = _normalise_hash(hashes.get("md5"), algorithm="md5", remote_path=remote_path)
            sha256_value = hashes.get("sha256")
            sha256 = (
                None
                if sha256_value in (None, "")
                else _normalise_hash(
                    sha256_value,
                    algorithm="sha256",
                    remote_path=remote_path,
                )
            )
            if remote_path in remote_paths:
                raise ValueError(f"duplicate OSF remote path: {remote_path!r}")
            if destination in destinations:
                raise ValueError(f"duplicate companion destination: {destination!r}")
            remote_paths.add(remote_path)
            destinations.add(destination)
            records.append(
                KorthalsRemoteFile(
                    remote_path=remote_path,
                    destination=destination,
                    md5=md5,
                    sha256=sha256,
                )
            )

    if not records:
        raise ValueError("OSF Korthals source inventory is empty")
    return tuple(sorted(records))


def _digest_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matches_remote(path: Path, remote: KorthalsRemoteFile) -> bool:
    if not path.is_file() or _digest_file(path, "md5") != remote.md5:
        return False
    return remote.sha256 is None or _digest_file(path, "sha256") == remote.sha256


def _scrub_unverified_local_files(
    inventory: Iterable[KorthalsRemoteFile],
) -> tuple[int, int]:
    """Keep checksum-matching files and delete partial/mismatched final-path files."""

    retained = 0
    removed = 0
    for remote in inventory:
        path = Path(remote.destination)
        if not path.exists():
            continue
        if _matches_remote(path, remote):
            retained += 1
            continue
        if not path.is_file():
            raise ValueError(f"expected file destination is not a regular file: {path}")
        path.unlink()
        removed += 1
    return retained, removed


def _verify_complete_local_source(inventory: Iterable[KorthalsRemoteFile]) -> None:
    missing: list[str] = []
    mismatched: list[str] = []
    for remote in inventory:
        path = Path(remote.destination)
        if not path.is_file():
            missing.append(remote.destination)
        elif not _matches_remote(path, remote):
            mismatched.append(remote.destination)
    if missing or mismatched:
        raise ValueError(
            "downloaded OSF source failed checksum completeness validation: "
            f"missing={missing[:5]!r}, mismatched={mismatched[:5]!r}"
        )


def _default_companion_download() -> None:
    from eyemovement_data.utils import download_osf_data

    download_osf_data(
        raw_clean="both",
        train_test="both",
        participants="all",
        overwrite=False,
    )


def _require_unchanged_inventory(
    baseline: tuple[KorthalsRemoteFile, ...],
    observed: tuple[KorthalsRemoteFile, ...],
) -> None:
    if observed != baseline:
        raise ValueError(
            "public OSF source inventory changed during download; refusing to mix revisions"
        )


def fetch_korthals_osf_resumable(
    *,
    max_attempts: int = 6,
    initial_backoff_seconds: float = 15.0,
    inventory_fn: Callable[[], tuple[KorthalsRemoteFile, ...]] | None = None,
    download_fn: Callable[[], None] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, int]:
    """Download the frozen public source with safe checksum-verified retries.

    Only the companion's transport ``RuntimeError`` is retried. Scientific,
    identity, filesystem, and checksum failures remain fail-closed. The
    companion's exact source selection is invoked on every attempt; verified
    completed files are retained so ``overwrite=False`` can resume without
    accepting partial files.
    """

    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer")
    if isinstance(initial_backoff_seconds, bool) or not isinstance(
        initial_backoff_seconds, (int, float)
    ):
        raise ValueError("initial_backoff_seconds must be a non-negative number")
    if initial_backoff_seconds < 0:
        raise ValueError("initial_backoff_seconds must be a non-negative number")

    inventory_loader = inventory_fn or _default_remote_inventory
    downloader = download_fn or _default_companion_download
    baseline = tuple(inventory_loader())
    if not baseline:
        raise ValueError("OSF Korthals source inventory is empty")

    retained, removed = _scrub_unverified_local_files(baseline)
    total_removed = removed

    for attempt in range(1, max_attempts + 1):
        try:
            downloader()
        except RuntimeError as exc:
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Korthals OSF download failed after {max_attempts} attempts"
                ) from exc
            current = tuple(inventory_loader())
            _require_unchanged_inventory(baseline, current)
            retry_retained, removed = _scrub_unverified_local_files(baseline)
            retained = max(retained, retry_retained)
            total_removed += removed
            sleep_fn(float(initial_backoff_seconds) * (2 ** (attempt - 1)))
            continue

        final_inventory = tuple(inventory_loader())
        _require_unchanged_inventory(baseline, final_inventory)
        _verify_complete_local_source(baseline)
        return {
            "attempts": attempt,
            "file_count": len(baseline),
            "retained_verified_files": retained,
            "removed_partial_files": total_removed,
        }

    raise AssertionError("unreachable")
