"""Endpoint-blind source intake for the Pedrotti/de Chambrier case study.

The intake verifies the exact Zenodo v1 files and only inspects source structure needed
by the frozen protocol. It deliberately does not compute gaze-path endpoints,
perturbation estimates, recovery fractions, or robustness classifications.
"""

from __future__ import annotations

import hashlib
import json
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .provenance import canonical_json, fingerprint

PEDROTTI_CASE_STUDY_ID = "pedrotti2023-reading-numerals-sampling-missingness-v1"
PEDROTTI_PROTOCOL_FINGERPRINT = (
    "efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5"
)
PEDROTTI_ZENODO_DOI = "10.5281/zenodo.7962917"
PEDROTTI_ZENODO_RECORD = 7962917
PEDROTTI_ZENODO_VERSION = "v1"
PEDROTTI_SOURCE_SCHEMA = "gazeaudit-pedrotti-source-manifest-v1"
PEDROTTI_SOURCE_INTAKE_SCHEMA = "gazeaudit-pedrotti-source-intake-artifacts-v1"
_PROTOCOL_FILE = "pedrotti2023_sampling_missingness_v1.json"


@dataclass(frozen=True)
class PedrottiSourceIntake:
    """Verified source identity and endpoint-blind compatibility summary."""

    source_manifest: dict[str, Any]
    intake_summary: dict[str, Any]


def load_pedrotti_protocol() -> dict[str, Any]:
    """Load the packaged frozen protocol and require its immutable fingerprint."""

    path = Path(__file__).resolve().parent / "data" / _PROTOCOL_FILE
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("packaged Pedrotti protocol must contain a JSON object")
    if document.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
        raise ValueError("packaged Pedrotti protocol fingerprint is not the frozen identity")
    return document


def expected_pedrotti_md5() -> dict[str, str]:
    """Return the exact Zenodo v1 filename-to-MD5 contract from the frozen protocol."""

    protocol = load_pedrotti_protocol()
    values = protocol["dataset"]["source_files"]["expected_md5"]
    if not isinstance(values, dict):
        raise ValueError("frozen Pedrotti expected_md5 contract must be an object")
    expected = {str(name): str(digest).lower() for name, digest in values.items()}
    participant_names = [f"{participant:02d}.txt" for participant in range(1, 37)]
    if sorted(expected) != sorted([*participant_names, "readme.txt"]):
        raise ValueError("frozen Pedrotti expected_md5 contract has an unexpected file set")
    if not all(_hex_digest(digest, 32) for digest in expected.values()):
        raise ValueError("frozen Pedrotti expected_md5 contract contains an invalid digest")
    return expected


def build_pedrotti_source_manifest(source_dir: str | Path) -> dict[str, Any]:
    """Verify exact public bytes and build a deterministic MD5+SHA256 source manifest."""

    root = Path(source_dir)
    if not root.is_dir():
        raise FileNotFoundError("Pedrotti source_dir must be an existing directory")
    expected = expected_pedrotti_md5()
    actual_names = sorted(path.name for path in root.iterdir() if path.is_file())
    if actual_names != sorted(expected):
        missing = sorted(set(expected).difference(actual_names))
        unexpected = sorted(set(actual_names).difference(expected))
        raise ValueError(
            f"Pedrotti source file set differs from frozen Zenodo v1 contract; "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    if any(path.is_dir() for path in root.iterdir()):
        raise ValueError("Pedrotti source_dir must not contain nested directories")

    files: list[dict[str, Any]] = []
    for name in sorted(expected):
        path = root / name
        md5 = _digest_file(path, "md5")
        if md5 != expected[name]:
            raise ValueError(
                f"Pedrotti source MD5 mismatch for {name!r}: {md5} != {expected[name]}"
            )
        files.append(
            {
                "path": name,
                "size_bytes": int(path.stat().st_size),
                "md5": md5,
                "sha256": _digest_file(path, "sha256"),
            }
        )

    core = {
        "schema": PEDROTTI_SOURCE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "zenodo_doi": PEDROTTI_ZENODO_DOI,
        "zenodo_record": PEDROTTI_ZENODO_RECORD,
        "zenodo_version": PEDROTTI_ZENODO_VERSION,
        "download_contract": _expected_download_contract(),
        "files": files,
        "file_count": len(files),
    }
    document = dict(core)
    document["source_manifest_fingerprint"] = fingerprint(core)
    return document


def verify_pedrotti_source_manifest(document: dict[str, Any]) -> bool:
    """Return whether a Pedrotti source manifest matches the frozen source contract."""

    try:
        normalized = json.loads(canonical_json(document))
        if not isinstance(normalized, dict):
            return False
        expected_keys = {
            "schema",
            "case_study_id",
            "protocol_fingerprint",
            "zenodo_doi",
            "zenodo_record",
            "zenodo_version",
            "download_contract",
            "files",
            "file_count",
            "source_manifest_fingerprint",
        }
        if set(normalized) != expected_keys:
            return False
        if normalized.get("schema") != PEDROTTI_SOURCE_SCHEMA:
            return False
        if normalized.get("case_study_id") != PEDROTTI_CASE_STUDY_ID:
            return False
        if normalized.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
            return False
        if normalized.get("zenodo_doi") != PEDROTTI_ZENODO_DOI:
            return False
        if normalized.get("zenodo_record") != PEDROTTI_ZENODO_RECORD:
            return False
        if normalized.get("zenodo_version") != PEDROTTI_ZENODO_VERSION:
            return False
        if normalized.get("download_contract") != _expected_download_contract():
            return False
        stored = normalized.pop("source_manifest_fingerprint")
        if stored != fingerprint(normalized):
            return False
        expected = expected_pedrotti_md5()
        files = normalized.get("files")
        if not isinstance(files, list) or len(files) != len(expected):
            return False
        if normalized.get("file_count") != len(expected):
            return False
        observed: dict[str, str] = {}
        for record in files:
            if not isinstance(record, dict) or set(record) != {
                "path",
                "size_bytes",
                "md5",
                "sha256",
            }:
                return False
            name = record["path"]
            if not isinstance(name, str) or name in observed or name not in expected:
                return False
            size_bytes = record["size_bytes"]
            if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes < 0:
                return False
            if record["md5"] != expected[name]:
                return False
            if not _hex_digest(record["sha256"], 64):
                return False
            observed[name] = record["md5"]
        return observed == expected
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def inspect_pedrotti_source(source_dir: str | Path) -> PedrottiSourceIntake:
    """Validate frozen structural compatibility without evaluating the endpoint."""

    root = Path(source_dir)
    manifest = build_pedrotti_source_manifest(root)
    if not verify_pedrotti_source_manifest(manifest):
        raise RuntimeError("newly built Pedrotti source manifest failed verification")

    protocol = load_pedrotti_protocol()
    required_columns = list(protocol["representation"]["required_columns"])
    participant_records: list[dict[str, Any]] = []
    for participant in range(1, 37):
        participant_id = f"{participant:02d}"
        participant_records.append(
            _inspect_participant_file(
                root / f"{participant_id}.txt", participant_id, required_columns
            )
        )

    total_rows = sum(record["row_count"] for record in participant_records)
    total_trials = sum(record["trial_count"] for record in participant_records)
    short_trials = sum(record["short_numeric_trial_count"] for record in participant_records)
    long_trials = sum(record["long_numeric_trial_count"] for record in participant_records)
    eye_counts = {
        eye: sum(record["eye"] == eye for record in participant_records)
        for eye in ("left", "right")
    }
    summary = {
        "schema": PEDROTTI_SOURCE_INTAKE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
        "participant_count": len(participant_records),
        "source_file_count": manifest["file_count"],
        "total_row_count": int(total_rows),
        "total_trial_count": int(total_trials),
        "short_numeric_trial_count": int(short_trials),
        "long_numeric_trial_count": int(long_trials),
        "eye_counts": eye_counts,
        "participants": participant_records,
        "scientific_endpoint_evaluated": False,
    }
    _validate_intake_summary(summary, manifest)
    return PedrottiSourceIntake(source_manifest=manifest, intake_summary=summary)


def write_pedrotti_source_intake_artifacts(
    intake: PedrottiSourceIntake,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write checksummed endpoint-blind source-intake artifacts."""

    if not isinstance(intake, PedrottiSourceIntake):
        raise TypeError("intake must be PedrottiSourceIntake")
    if not verify_pedrotti_source_manifest(intake.source_manifest):
        raise ValueError("intake source manifest is invalid")
    _validate_intake_summary(intake.intake_summary, intake.source_manifest)
    destination = _prepare_flat_destination(Path(output_dir), overwrite=overwrite)
    _write_json(destination / "source_manifest.json", intake.source_manifest)
    _write_json(destination / "intake_summary.json", intake.intake_summary)

    records = [
        _file_record(destination / "intake_summary.json", destination),
        _file_record(destination / "source_manifest.json", destination),
    ]
    core = {
        "schema": PEDROTTI_SOURCE_INTAKE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest["source_manifest_fingerprint"],
        "files": records,
    }
    artifact = dict(core)
    artifact["artifact_manifest_fingerprint"] = fingerprint(core)
    _write_json(destination / "artifact_manifest.json", artifact)
    targets = sorted(path for path in destination.iterdir() if path.is_file())
    (destination / "SHA256SUMS").write_text(
        "\n".join(f"{_digest_file(path, 'sha256')}  {path.name}" for path in targets) + "\n",
        encoding="utf-8",
    )
    if not verify_pedrotti_source_intake_artifacts(destination):
        raise RuntimeError("newly written Pedrotti intake artifact failed verification")
    return artifact


def verify_pedrotti_source_intake_artifacts(output_dir: str | Path) -> bool:
    """Return whether the endpoint-blind intake artifact set is complete and intact."""

    root = Path(output_dir)
    try:
        expected_names = {
            "source_manifest.json",
            "intake_summary.json",
            "artifact_manifest.json",
            "SHA256SUMS",
        }
        if not root.is_dir() or {path.name for path in root.iterdir()} != expected_names:
            return False
        source = _read_json(root / "source_manifest.json")
        summary = _read_json(root / "intake_summary.json")
        artifact = _read_json(root / "artifact_manifest.json")
        if not verify_pedrotti_source_manifest(source):
            return False
        _validate_intake_summary(summary, source)
        expected_artifact_keys = {
            "schema",
            "case_study_id",
            "protocol_fingerprint",
            "source_manifest_fingerprint",
            "files",
            "artifact_manifest_fingerprint",
        }
        if set(artifact) != expected_artifact_keys:
            return False
        stored = artifact.pop("artifact_manifest_fingerprint")
        if stored != fingerprint(artifact):
            return False
        if artifact.get("schema") != PEDROTTI_SOURCE_INTAKE_SCHEMA:
            return False
        if artifact.get("case_study_id") != PEDROTTI_CASE_STUDY_ID:
            return False
        if artifact.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
            return False
        if artifact.get("source_manifest_fingerprint") != source["source_manifest_fingerprint"]:
            return False
        expected_records = [
            _file_record(root / "intake_summary.json", root),
            _file_record(root / "source_manifest.json", root),
        ]
        if artifact.get("files") != expected_records:
            return False
        checksums = _parse_checksums(root / "SHA256SUMS")
        if set(checksums) != {
            "artifact_manifest.json",
            "intake_summary.json",
            "source_manifest.json",
        }:
            return False
        return all(
            _digest_file(root / name, "sha256") == digest for name, digest in checksums.items()
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _validate_intake_summary(summary: dict[str, Any], source: dict[str, Any]) -> None:
    expected_keys = {
        "schema",
        "case_study_id",
        "protocol_fingerprint",
        "source_manifest_fingerprint",
        "participant_count",
        "source_file_count",
        "total_row_count",
        "total_trial_count",
        "short_numeric_trial_count",
        "long_numeric_trial_count",
        "eye_counts",
        "participants",
        "scientific_endpoint_evaluated",
    }
    if set(summary) != expected_keys:
        raise ValueError("Pedrotti intake summary does not have the exact required field set")
    if summary["schema"] != PEDROTTI_SOURCE_INTAKE_SCHEMA:
        raise ValueError("unexpected Pedrotti intake summary schema")
    if summary["case_study_id"] != PEDROTTI_CASE_STUDY_ID:
        raise ValueError("unexpected Pedrotti case-study identity")
    if summary["protocol_fingerprint"] != PEDROTTI_PROTOCOL_FINGERPRINT:
        raise ValueError("unexpected Pedrotti protocol fingerprint")
    if summary["source_manifest_fingerprint"] != source["source_manifest_fingerprint"]:
        raise ValueError("Pedrotti intake/source fingerprint mismatch")
    if summary["scientific_endpoint_evaluated"] is not False:
        raise ValueError("Pedrotti source intake must remain endpoint-blind")
    if summary["participant_count"] != 36:
        raise ValueError("Pedrotti intake must contain exactly 36 participants")
    if summary["source_file_count"] != 37 or summary["source_file_count"] != source["file_count"]:
        raise ValueError("Pedrotti intake must contain exactly 37 frozen source files")
    if not _positive_int(summary["total_row_count"]):
        raise ValueError("Pedrotti intake total_row_count must be a positive integer")
    if summary["total_trial_count"] != 36 * 96:
        raise ValueError("Pedrotti intake must contain exactly 96 trials per participant")

    participants = summary["participants"]
    if not isinstance(participants, list) or len(participants) != 36:
        raise ValueError("Pedrotti intake participants must contain exactly 36 records")
    expected_ids = [f"{participant:02d}" for participant in range(1, 37)]
    participant_fields = {
        "participant_id",
        "row_count",
        "trial_count",
        "eye",
        "short_numeric_trial_count",
        "long_numeric_trial_count",
        "numeric_trial_count",
    }
    seen_ids: list[str] = []
    row_sum = 0
    trial_sum = 0
    short_sum = 0
    long_sum = 0
    computed_eye_counts = {"left": 0, "right": 0}
    for record in participants:
        if not isinstance(record, dict) or set(record) != participant_fields:
            raise ValueError("Pedrotti participant record has an unexpected field set")
        participant_id = record["participant_id"]
        if not isinstance(participant_id, str):
            raise ValueError("Pedrotti participant_id must be a string")
        seen_ids.append(participant_id)
        if not _positive_int(record["row_count"]):
            raise ValueError("Pedrotti participant row_count must be positive")
        if record["trial_count"] != 96:
            raise ValueError("Pedrotti participant must contain exactly 96 trials")
        if record["eye"] not in computed_eye_counts:
            raise ValueError("Pedrotti participant eye must be left or right")
        short_count = record["short_numeric_trial_count"]
        long_count = record["long_numeric_trial_count"]
        numeric_count = record["numeric_trial_count"]
        if not _positive_int(short_count) or not _positive_int(long_count):
            raise ValueError("Pedrotti participant must retain both numeric length conditions")
        if numeric_count != short_count + long_count or numeric_count > 96:
            raise ValueError("Pedrotti participant numeric-trial counts do not reconcile")
        row_sum += record["row_count"]
        trial_sum += record["trial_count"]
        short_sum += short_count
        long_sum += long_count
        computed_eye_counts[record["eye"]] += 1
    if seen_ids != expected_ids:
        raise ValueError("Pedrotti participant identities/order differ from 01 through 36")
    if row_sum != summary["total_row_count"]:
        raise ValueError("Pedrotti row totals do not reconcile")
    if trial_sum != summary["total_trial_count"]:
        raise ValueError("Pedrotti trial totals do not reconcile")
    if short_sum != summary["short_numeric_trial_count"]:
        raise ValueError("Pedrotti short-numeric totals do not reconcile")
    if long_sum != summary["long_numeric_trial_count"]:
        raise ValueError("Pedrotti long-numeric totals do not reconcile")
    if summary["eye_counts"] != computed_eye_counts:
        raise ValueError("Pedrotti eye counts do not reconcile")


def _inspect_participant_file(
    path: Path,
    participant_id: str,
    required_columns: list[str],
) -> dict[str, Any]:
    header = pd.read_csv(path, nrows=0)
    if header.columns.tolist() != required_columns:
        raise ValueError(f"participant {participant_id} columns differ from frozen contract")
    frame = pd.read_csv(
        path,
        usecols=required_columns,
        na_values=["."],
        dtype={"TrialTextShown": "string"},
        low_memory=False,
    )
    if frame.empty:
        raise ValueError(f"participant {participant_id} has no source rows")
    trial = pd.to_numeric(frame["TRIAL_INDEX"], errors="coerce")
    timestamp = pd.to_numeric(frame["TIMESTAMP"], errors="coerce")
    if trial.isna().any() or (trial != trial.astype(int)).any():
        raise ValueError(f"participant {participant_id} has invalid TRIAL_INDEX")
    if timestamp.isna().any() or not np.isfinite(timestamp.to_numpy(dtype=float)).all():
        raise ValueError(f"participant {participant_id} has invalid TIMESTAMP")
    frame["TRIAL_INDEX"] = trial.astype(int)
    frame["TIMESTAMP"] = timestamp.astype(float)
    observed_trials = sorted(frame["TRIAL_INDEX"].unique().tolist())
    if observed_trials != list(range(1, 97)):
        raise ValueError(f"participant {participant_id} does not contain exactly trials 1..96")
    increasing = frame.groupby("TRIAL_INDEX", sort=False)["TIMESTAMP"].apply(
        lambda values: values.diff().dropna().gt(0).all()
    )
    if not increasing.all():
        raise ValueError(f"participant {participant_id} timestamps are not strictly increasing")
    if frame["TrialTextShown"].isna().any():
        raise ValueError(f"participant {participant_id} has missing TrialTextShown")
    if not frame.groupby("TRIAL_INDEX")["TrialTextShown"].nunique(dropna=False).eq(1).all():
        raise ValueError(f"participant {participant_id} has unstable TrialTextShown within a trial")

    left_finite = _finite_xy(frame, "LEFT_GAZE_X", "LEFT_GAZE_Y")
    right_finite = _finite_xy(frame, "RIGHT_GAZE_X", "RIGHT_GAZE_Y")
    if bool(left_finite.any()) == bool(right_finite.any()):
        raise ValueError(
            f"participant {participant_id} does not expose exactly one finite eye side"
        )
    eye = "left" if left_finite.any() else "right"

    stimuli = frame.groupby("TRIAL_INDEX", sort=True)["TrialTextShown"].first()
    conditions = stimuli.map(_numeric_condition)
    short_count = int(conditions.eq("short").sum())
    long_count = int(conditions.eq("long").sum())
    if short_count < 1 or long_count < 1:
        raise ValueError(f"participant {participant_id} lacks a frozen numeric length condition")
    return {
        "participant_id": participant_id,
        "row_count": int(len(frame)),
        "trial_count": len(observed_trials),
        "eye": eye,
        "short_numeric_trial_count": short_count,
        "long_numeric_trial_count": long_count,
        "numeric_trial_count": short_count + long_count,
    }


def _expected_download_contract() -> dict[str, Any]:
    return {
        "participants": "all",
        "participant_files": [f"{participant:02d}.txt" for participant in range(1, 37)],
        "readme": "readme.txt",
        "bytes": "published_unchanged",
    }


def _numeric_condition(value: Any) -> str | None:
    text = str(value)
    removable = set(string.whitespace) | {",", ".", "'", "’", "\u00a0", "\u202f"}
    digits = "".join(character for character in text if character not in removable)
    if not digits or not digits.isascii() or not digits.isdigit():
        return None
    if len(digits) == 4:
        return "short"
    if 8 <= len(digits) <= 11:
        return "long"
    return None


def _finite_xy(frame: pd.DataFrame, x_column: str, y_column: str) -> pd.Series:
    x = pd.to_numeric(frame[x_column], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(frame[y_column], errors="coerce").to_numpy(dtype=float)
    return pd.Series(np.isfinite(x) & np.isfinite(y), index=frame.index)


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _prepare_flat_destination(destination: Path, *, overwrite: bool) -> Path:
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    destination.mkdir(parents=True, exist_ok=True)
    existing = list(destination.iterdir())
    if existing and not overwrite:
        raise FileExistsError("output_dir is not empty; pass overwrite=True to replace")
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise ValueError("overwrite=True refuses nested directories")
            path.unlink()
    return destination


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size_bytes": int(path.stat().st_size),
        "sha256": _digest_file(path, "sha256"),
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _digest_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hex_digest(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(
        character in "0123456789abcdef" for character in value
    )


def _parse_checksums(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, separator, name = line.partition("  ")
        candidate = Path(name)
        if not separator or not _hex_digest(digest, 64):
            raise ValueError("invalid SHA256SUMS entry")
        if not name or candidate.is_absolute() or ".." in candidate.parts or name in values:
            raise ValueError("invalid or duplicate SHA256SUMS path")
        values[name] = digest
    return values
