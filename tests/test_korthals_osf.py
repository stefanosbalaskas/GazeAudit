from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from gazeaudit.korthals_osf import KorthalsRemoteFile, fetch_korthals_osf_resumable


def _remote(path: str, payload: bytes) -> KorthalsRemoteFile:
    return KorthalsRemoteFile(
        remote_path=f"/{path}",
        destination=f"data/{path}",
        md5=hashlib.md5(payload).hexdigest(),  # noqa: S324 - published transfer checksum
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def _write(path: str, payload: bytes) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)


def test_resumable_download_succeeds_without_retry(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    first = _remote("raw/a.bin", b"alpha")
    second = _remote("clean/b.bin", b"beta")
    inventory = (first, second)

    def download() -> None:
        _write(first.destination, b"alpha")
        _write(second.destination, b"beta")

    result = fetch_korthals_osf_resumable(
        inventory_fn=lambda: inventory,
        download_fn=download,
        sleep_fn=lambda _: None,
    )

    assert result == {
        "attempts": 1,
        "file_count": 2,
        "retained_verified_files": 0,
        "removed_partial_files": 0,
    }


def test_partial_file_is_removed_before_safe_retry(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    first = _remote("raw/a.bin", b"alpha")
    second = _remote("raw/b.bin", b"beta")
    inventory = (first, second)
    calls = 0
    sleeps: list[float] = []

    def download() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            _write(first.destination, b"alpha")
            _write(second.destination, b"partial")
            raise RuntimeError("Response has status code 403")
        assert Path(first.destination).read_bytes() == b"alpha"
        assert not Path(second.destination).exists()
        _write(second.destination, b"beta")

    result = fetch_korthals_osf_resumable(
        max_attempts=3,
        initial_backoff_seconds=2,
        inventory_fn=lambda: inventory,
        download_fn=download,
        sleep_fn=sleeps.append,
    )

    assert calls == 2
    assert sleeps == [2]
    assert result["attempts"] == 2
    assert result["retained_verified_files"] == 1
    assert result["removed_partial_files"] == 1


def test_preexisting_verified_file_is_retained(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    first = _remote("raw/a.bin", b"alpha")
    second = _remote("raw/b.bin", b"beta")
    inventory = (first, second)
    _write(first.destination, b"alpha")

    def download() -> None:
        assert Path(first.destination).read_bytes() == b"alpha"
        _write(second.destination, b"beta")

    result = fetch_korthals_osf_resumable(
        inventory_fn=lambda: inventory,
        download_fn=download,
        sleep_fn=lambda _: None,
    )

    assert result["retained_verified_files"] == 1
    assert result["removed_partial_files"] == 0


def test_remote_inventory_change_during_retry_fails_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    baseline = (_remote("raw/a.bin", b"alpha"),)
    changed = (_remote("raw/a.bin", b"changed"),)
    inventory_calls = 0

    def inventory() -> tuple[KorthalsRemoteFile, ...]:
        nonlocal inventory_calls
        inventory_calls += 1
        return baseline if inventory_calls == 1 else changed

    with pytest.raises(ValueError, match="source inventory changed"):
        fetch_korthals_osf_resumable(
            max_attempts=3,
            initial_backoff_seconds=0,
            inventory_fn=inventory,
            download_fn=lambda: (_ for _ in ()).throw(RuntimeError("403")),
            sleep_fn=lambda _: None,
        )


def test_successful_transport_with_bad_final_bytes_fails_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    remote = _remote("raw/a.bin", b"alpha")

    def download() -> None:
        _write(remote.destination, b"wrong")

    with pytest.raises(ValueError, match="checksum completeness validation"):
        fetch_korthals_osf_resumable(
            inventory_fn=lambda: (remote,),
            download_fn=download,
            sleep_fn=lambda _: None,
        )


def test_retry_exhaustion_preserves_transport_failure_boundary(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    remote = _remote("raw/a.bin", b"alpha")
    calls = 0

    def download() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("Response has status code 403")

    with pytest.raises(RuntimeError, match="failed after 3 attempts"):
        fetch_korthals_osf_resumable(
            max_attempts=3,
            initial_backoff_seconds=0,
            inventory_fn=lambda: (remote,),
            download_fn=download,
            sleep_fn=lambda _: None,
        )

    assert calls == 3


@pytest.mark.parametrize("max_attempts", [0, -1, True])
def test_invalid_attempt_count_rejected(max_attempts) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        fetch_korthals_osf_resumable(max_attempts=max_attempts)


def test_negative_backoff_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        fetch_korthals_osf_resumable(initial_backoff_seconds=-1)
