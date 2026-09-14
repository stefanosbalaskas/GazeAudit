"""Conservative structural preflight checks and provenance for gaze studies."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .provenance import canonical_json, fingerprint, software_environment
from .study import GazeStudy

STUDY_QC_SCHEMA = "gazeaudit-study-qc-v1"
STUDY_QC_ARTIFACT_SCHEMA = "gazeaudit-study-qc-artifacts-v1"
STUDY_QC_PUBLICATION_LINK_SCHEMA = "gazeaudit-study-qc-publication-link-v1"

STUDY_QC_ISSUE_CODES = (
    "coordinate_nonfinite",
    "timestamp_nonfinite",
    "identifier_missing",
    "timestamp_duplicate",
    "timestamp_decreasing",
)

_DIAGNOSTIC_COLUMNS = [
    "diagnostic_id",
    "scope",
    "issue_code",
    "detail_code",
    "row_position",
    "participant",
    "trial",
    "timestamp",
    "message",
]

_DECISION_COLUMNS = [
    "decision_id",
    "issue_code",
    "action",
    "rationale",
    "diagnostic_ids",
]


@dataclass(frozen=True)
class StudyQCReport:
    """Machine-readable structural QC summary for a :class:`GazeStudy`.

    The report is intentionally descriptive. It flags conditions that deserve
    inspection before downstream analysis but does not impose universal
    exclusion thresholds or infer scientific validity from structural checks.
    """

    n_rows: int
    n_participants: int
    n_trials: int
    missing_x_rows: int
    missing_y_rows: int
    missing_timestamp_rows: int
    infinite_x_rows: int
    infinite_y_rows: int
    infinite_timestamp_rows: int
    missing_identifier_rows: int
    duplicate_timestamp_rows: int
    decreasing_time_groups: int
    coordinate_issue_rows: int
    timestamp_issue_rows: int

    @property
    def has_structural_issues(self) -> bool:
        """Whether at least one structural condition requires review."""

        return any(
            value > 0
            for value in (
                self.coordinate_issue_rows,
                self.timestamp_issue_rows,
                self.missing_identifier_rows,
                self.duplicate_timestamp_rows,
                self.decreasing_time_groups,
            )
        )

    @property
    def status(self) -> str:
        """Return ``"pass"`` when no flagged condition is present, else ``"review"``."""

        return "review" if self.has_structural_issues else "pass"

    @property
    def issue_codes(self) -> tuple[str, ...]:
        """Stable symbolic labels for the flagged structural conditions."""

        issues: list[str] = []
        if self.coordinate_issue_rows:
            issues.append("coordinate_nonfinite")
        if self.timestamp_issue_rows:
            issues.append("timestamp_nonfinite")
        if self.missing_identifier_rows:
            issues.append("identifier_missing")
        if self.duplicate_timestamp_rows:
            issues.append("timestamp_duplicate")
        if self.decreasing_time_groups:
            issues.append("timestamp_decreasing")
        return tuple(issues)

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable mapping with derived QC fields included."""

        payload: dict[str, Any] = asdict(self)
        payload["status"] = self.status
        payload["has_structural_issues"] = self.has_structural_issues
        payload["issue_codes"] = self.issue_codes
        return payload

    def to_frame(self) -> pd.DataFrame:
        """Return one row per QC metric for compact reporting or export."""

        return pd.DataFrame(
            [
                {"metric": key, "value": value}
                for key, value in self.to_dict().items()
                if key != "issue_codes"
            ]
        )


@dataclass(frozen=True)
class StudyQCDecision:
    """Researcher-supplied response to one flagged structural issue family.

    ``action`` and ``rationale`` are deliberately free text. GazeAudit records
    the decision but does not prescribe whether a flagged condition should be
    retained, repaired, combined, excluded, or handled in another defensible way.
    """

    issue_code: str
    action: str
    rationale: str
    diagnostic_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        issue_code = _nonempty_text(self.issue_code, "issue_code")
        if issue_code not in STUDY_QC_ISSUE_CODES:
            raise ValueError(f"unsupported study QC issue code: {issue_code!r}")
        action = _nonempty_text(self.action, "action")
        rationale = _nonempty_text(self.rationale, "rationale")
        diagnostic_ids = tuple(
            _nonempty_text(value, "diagnostic_id") for value in self.diagnostic_ids
        )
        if len(set(diagnostic_ids)) != len(diagnostic_ids):
            raise ValueError("diagnostic_ids must not contain duplicates")
        object.__setattr__(self, "issue_code", issue_code)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "rationale", rationale)
        object.__setattr__(self, "diagnostic_ids", diagnostic_ids)

    def to_dict(self) -> dict[str, Any]:
        """Return the deterministic decision payload used for provenance."""

        return {
            "issue_code": self.issue_code,
            "action": self.action,
            "rationale": self.rationale,
            "diagnostic_ids": list(self.diagnostic_ids),
        }


@dataclass(frozen=True)
class StudyQCAudit:
    """Deterministic structural QC record bound to one canonical study view."""

    report: StudyQCReport
    diagnostics: pd.DataFrame
    decisions: tuple[StudyQCDecision, ...]
    study_descriptor: dict[str, Any]
    manifest: dict[str, Any]

    @property
    def study_fingerprint(self) -> str:
        """Fingerprint of the five mapped columns inspected by structural QC."""

        return str(self.study_descriptor["study_fingerprint"])

    @property
    def audit_fingerprint(self) -> str:
        """Fingerprint of study identity, QC output, and recorded decisions."""

        return str(self.manifest["audit_fingerprint"])

    @property
    def manifest_fingerprint(self) -> str:
        """Fingerprint that additionally binds the recorded software environment."""

        return str(self.manifest["manifest_fingerprint"])

    def report_json(self) -> str:
        """Return the QC summary as canonical JSON."""

        return canonical_json(_qc_normalize(self.report.to_dict()))

    def diagnostics_csv(self) -> str:
        """Return row/group diagnostics as deterministic CSV."""

        return self.diagnostics.to_csv(index=False, lineterminator="\n")

    def decisions_frame(self) -> pd.DataFrame:
        """Return recorded decisions as a deterministic tabular log."""

        return _decisions_frame(self.decisions)

    def decisions_csv(self) -> str:
        """Return recorded decisions as deterministic CSV."""

        return self.decisions_frame().to_csv(index=False, lineterminator="\n")

    def manifest_json(self) -> str:
        """Return the complete QC manifest as canonical JSON."""

        return canonical_json(self.manifest)


def _float_values(series: pd.Series) -> np.ndarray:
    return series.to_numpy(dtype=float, na_value=np.nan)


def _count_decreasing_time_groups(study: GazeStudy) -> int:
    grouped = study.data.groupby(
        [study.participant, study.trial],
        sort=False,
        dropna=False,
    )
    count = 0
    for _, frame in grouped:
        values = _float_values(frame[study.timestamp])
        finite = values[np.isfinite(values)]
        if finite.size > 1 and np.any(np.diff(finite) < 0):
            count += 1
    return count


def audit_study_qc(study: GazeStudy) -> StudyQCReport:
    """Audit structural properties of a canonical eye-tracking study.

    Checks cover missing and infinite coordinates/timestamps, missing
    participant or trial identifiers, duplicate timestamps within a
    participant-by-trial unit, and decreasing finite timestamps within such
    units. Duplicate timestamps are flagged for review rather than treated as
    automatically invalid because their meaning can depend on acquisition and
    representation choices.
    """

    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")

    data = study.data
    x = data[study.x]
    y = data[study.y]
    timestamp = data[study.timestamp]

    x_values = _float_values(x)
    y_values = _float_values(y)
    timestamp_values = _float_values(timestamp)

    missing_x = x.isna().to_numpy()
    missing_y = y.isna().to_numpy()
    missing_timestamp = timestamp.isna().to_numpy()

    infinite_x = np.isinf(x_values)
    infinite_y = np.isinf(y_values)
    infinite_timestamp = np.isinf(timestamp_values)

    coordinate_issue = ~np.isfinite(x_values) | ~np.isfinite(y_values)
    timestamp_issue = ~np.isfinite(timestamp_values)
    missing_identifier = data[[study.participant, study.trial]].isna().any(axis=1).to_numpy()

    finite_time = np.isfinite(timestamp_values)
    duplicate_timestamp_rows = int(
        data.loc[finite_time]
        .duplicated(subset=[study.participant, study.trial, study.timestamp], keep=False)
        .sum()
    )

    return StudyQCReport(
        n_rows=int(len(data)),
        n_participants=study.n_participants,
        n_trials=study.n_trials,
        missing_x_rows=int(missing_x.sum()),
        missing_y_rows=int(missing_y.sum()),
        missing_timestamp_rows=int(missing_timestamp.sum()),
        infinite_x_rows=int(infinite_x.sum()),
        infinite_y_rows=int(infinite_y.sum()),
        infinite_timestamp_rows=int(infinite_timestamp.sum()),
        missing_identifier_rows=int(missing_identifier.sum()),
        duplicate_timestamp_rows=duplicate_timestamp_rows,
        decreasing_time_groups=_count_decreasing_time_groups(study),
        coordinate_issue_rows=int(coordinate_issue.sum()),
        timestamp_issue_rows=int(timestamp_issue.sum()),
    )


def study_qc_diagnostics(study: GazeStudy) -> pd.DataFrame:
    """Return deterministic row/group diagnostics for structural QC conditions."""

    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")

    data = study.data
    x = data[study.x]
    y = data[study.y]
    timestamp = data[study.timestamp]
    x_values = _float_values(x)
    y_values = _float_values(y)
    timestamp_values = _float_values(timestamp)

    missing_x = x.isna().to_numpy()
    missing_y = y.isna().to_numpy()
    missing_timestamp = timestamp.isna().to_numpy()
    infinite_x = np.isinf(x_values)
    infinite_y = np.isinf(y_values)
    infinite_timestamp = np.isinf(timestamp_values)
    missing_participant = data[study.participant].isna().to_numpy()
    missing_trial = data[study.trial].isna().to_numpy()

    finite_time = np.isfinite(timestamp_values)
    duplicate_timestamp = np.zeros(len(data), dtype=bool)
    duplicate_timestamp[finite_time] = (
        data.loc[finite_time]
        .duplicated(subset=[study.participant, study.trial, study.timestamp], keep=False)
        .to_numpy()
    )

    rows: list[dict[str, Any]] = []

    def add_row(
        position: int,
        issue_code: str,
        detail_code: str,
        message: str,
    ) -> None:
        rows.append(
            {
                "scope": "row",
                "issue_code": issue_code,
                "detail_code": detail_code,
                "row_position": int(position),
                "participant": data[study.participant].iloc[position],
                "trial": data[study.trial].iloc[position],
                "timestamp": timestamp.iloc[position],
                "message": message,
            }
        )

    for position in range(len(data)):
        if missing_x[position]:
            add_row(position, "coordinate_nonfinite", "x_missing", "x coordinate is missing")
        elif infinite_x[position]:
            add_row(
                position,
                "coordinate_nonfinite",
                "x_infinite",
                "x coordinate is infinite",
            )
        if missing_y[position]:
            add_row(position, "coordinate_nonfinite", "y_missing", "y coordinate is missing")
        elif infinite_y[position]:
            add_row(
                position,
                "coordinate_nonfinite",
                "y_infinite",
                "y coordinate is infinite",
            )
        if missing_timestamp[position]:
            add_row(
                position,
                "timestamp_nonfinite",
                "timestamp_missing",
                "timestamp is missing",
            )
        elif infinite_timestamp[position]:
            add_row(
                position,
                "timestamp_nonfinite",
                "timestamp_infinite",
                "timestamp is infinite",
            )
        if missing_participant[position]:
            add_row(
                position,
                "identifier_missing",
                "participant_missing",
                "participant identifier is missing",
            )
        if missing_trial[position]:
            add_row(
                position,
                "identifier_missing",
                "trial_missing",
                "trial identifier is missing",
            )
        if duplicate_timestamp[position]:
            add_row(
                position,
                "timestamp_duplicate",
                "timestamp_duplicate",
                "participant × trial timestamp is duplicated",
            )

    grouped = data.groupby(
        [study.participant, study.trial],
        sort=False,
        dropna=False,
    )
    for _, frame in grouped:
        values = _float_values(frame[study.timestamp])
        finite = values[np.isfinite(values)]
        if finite.size > 1 and np.any(np.diff(finite) < 0):
            rows.append(
                {
                    "scope": "group",
                    "issue_code": "timestamp_decreasing",
                    "detail_code": "timestamp_decreasing",
                    "row_position": pd.NA,
                    "participant": frame[study.participant].iloc[0],
                    "trial": frame[study.trial].iloc[0],
                    "timestamp": pd.NA,
                    "message": "finite timestamps decrease in observed row order",
                }
            )

    if not rows:
        return pd.DataFrame(columns=_DIAGNOSTIC_COLUMNS)

    for number, row in enumerate(rows, start=1):
        row["diagnostic_id"] = f"D{number:06d}"
    return pd.DataFrame(rows, columns=_DIAGNOSTIC_COLUMNS)


def build_study_qc_audit(
    study: GazeStudy,
    *,
    decisions: Sequence[StudyQCDecision] = (),
) -> StudyQCAudit:
    """Build a deterministic QC record for one canonical study representation."""

    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")
    normalized_decisions = tuple(decisions)
    report = audit_study_qc(study)
    diagnostics = study_qc_diagnostics(study)
    _validate_decisions(report, diagnostics, normalized_decisions)
    study_descriptor = _study_descriptor(study)
    manifest = _build_qc_manifest(
        report=report,
        diagnostics=diagnostics,
        decisions=normalized_decisions,
        study_descriptor=study_descriptor,
        software=software_environment(),
    )
    return StudyQCAudit(
        report=report,
        diagnostics=diagnostics.copy(deep=True),
        decisions=normalized_decisions,
        study_descriptor=study_descriptor,
        manifest=manifest,
    )


def verify_study_qc_manifest(manifest: Mapping[str, Any]) -> bool:
    """Verify deterministic fingerprints carried by a QC manifest."""

    try:
        if manifest.get("schema") != STUDY_QC_SCHEMA:
            return False
        study = dict(manifest["study"])
        stored_study_fingerprint = str(study.pop("study_fingerprint"))
        if fingerprint(study) != stored_study_fingerprint:
            return False
        scientific_core = {
            "schema": manifest["schema"],
            "study": manifest["study"],
            "report": manifest["report"],
            "diagnostics": manifest["diagnostics"],
            "decisions": manifest["decisions"],
        }
        if fingerprint(scientific_core) != manifest["audit_fingerprint"]:
            return False
        complete = dict(manifest)
        stored_manifest_fingerprint = str(complete.pop("manifest_fingerprint"))
        return fingerprint(complete) == stored_manifest_fingerprint
    except (KeyError, TypeError, ValueError):
        return False


def verify_study_qc_audit(audit: StudyQCAudit) -> bool:
    """Return whether a QC audit still matches its deterministic manifest."""

    if not isinstance(audit, StudyQCAudit):
        raise TypeError("audit must be a StudyQCAudit")
    try:
        _validate_decisions(audit.report, audit.diagnostics, audit.decisions)
        software = audit.manifest.get("software")
        if not isinstance(software, Mapping):
            return False
        expected = _build_qc_manifest(
            report=audit.report,
            diagnostics=audit.diagnostics,
            decisions=audit.decisions,
            study_descriptor=audit.study_descriptor,
            software=software,
        )
        return canonical_json(expected) == canonical_json(audit.manifest) and (
            verify_study_qc_manifest(audit.manifest)
        )
    except (KeyError, TypeError, ValueError):
        return False


def study_qc_publication_metadata(audit: StudyQCAudit) -> dict[str, Any]:
    """Return compact QC provenance suitable for publication-bundle metadata.

    The descriptor intentionally uses the substantive ``audit_fingerprint`` rather
    than the software-bound manifest fingerprint. Passing this mapping in the
    ``metadata`` argument of :func:`build_conclusion_audit_bundle` binds structural
    QC provenance into that bundle's scientific fingerprint without changing the
    publication schema.
    """

    if not isinstance(audit, StudyQCAudit):
        raise TypeError("audit must be a StudyQCAudit")
    if not verify_study_qc_audit(audit):
        raise ValueError("study QC audit does not match its manifest")
    return {
        "schema": STUDY_QC_PUBLICATION_LINK_SCHEMA,
        "status": audit.report.status,
        "issue_codes": list(audit.report.issue_codes),
        "study_fingerprint": audit.study_fingerprint,
        "audit_fingerprint": audit.audit_fingerprint,
        "n_diagnostics": int(len(audit.diagnostics)),
        "n_decisions": int(len(audit.decisions)),
    }


def write_study_qc_artifacts(
    audit: StudyQCAudit,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write deterministic JSON/CSV QC evidence and an integrity manifest."""

    if not isinstance(audit, StudyQCAudit):
        raise TypeError("audit must be a StudyQCAudit")
    if not verify_study_qc_audit(audit):
        raise ValueError("study QC audit does not match its manifest")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    payloads = {
        "study_qc_report.json": audit.report_json() + "\n",
        "study_qc_diagnostics.csv": audit.diagnostics_csv(),
        "study_qc_decisions.csv": audit.decisions_csv(),
        "study_qc_audit.json": audit.manifest_json() + "\n",
    }
    files = {
        name: {
            "sha256": _sha256_text(content),
            "bytes": len(content.encode("utf-8")),
        }
        for name, content in payloads.items()
    }
    artifact_manifest: dict[str, Any] = {
        "schema": STUDY_QC_ARTIFACT_SCHEMA,
        "audit_fingerprint": audit.audit_fingerprint,
        "files": files,
    }
    artifact_manifest["artifact_fingerprint"] = fingerprint(artifact_manifest)
    payloads["study_qc_artifacts.json"] = canonical_json(artifact_manifest) + "\n"

    paths: dict[str, Path] = {}
    for name, content in payloads.items():
        path = destination / name
        path.write_text(content, encoding="utf-8", newline="")
        paths[name] = path
    return paths


def verify_study_qc_artifacts(output_dir: str | Path) -> bool:
    """Verify a written structural-QC evidence directory byte-for-byte."""

    destination = Path(output_dir)
    manifest_path = destination / "study_qc_artifacts.json"
    if not manifest_path.is_file():
        return False
    try:
        artifact_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if artifact_manifest.get("schema") != STUDY_QC_ARTIFACT_SCHEMA:
            return False
        complete = dict(artifact_manifest)
        stored_fingerprint = str(complete.pop("artifact_fingerprint"))
        if fingerprint(complete) != stored_fingerprint:
            return False
        files = artifact_manifest["files"]
        expected_names = {
            "study_qc_report.json",
            "study_qc_diagnostics.csv",
            "study_qc_decisions.csv",
            "study_qc_audit.json",
        }
        if set(files) != expected_names:
            return False
        for name in sorted(expected_names):
            path = destination / name
            if not path.is_file():
                return False
            payload = path.read_bytes()
            if len(payload) != int(files[name]["bytes"]):
                return False
            if hashlib.sha256(payload).hexdigest() != files[name]["sha256"]:
                return False
        audit_manifest = json.loads(
            (destination / "study_qc_audit.json").read_text(encoding="utf-8")
        )
        return verify_study_qc_manifest(audit_manifest) and (
            audit_manifest["audit_fingerprint"] == artifact_manifest["audit_fingerprint"]
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return False


def _study_descriptor(study: GazeStudy) -> dict[str, Any]:
    semantic_columns = {
        "participant": study.participant,
        "trial": study.trial,
        "timestamp": study.timestamp,
        "x": study.x,
        "y": study.y,
    }
    dtypes = {
        semantic: str(study.data[column].dtype)
        for semantic, column in semantic_columns.items()
    }
    records = []
    for position in range(len(study.data)):
        records.append(
            {
                semantic: _qc_normalize(study.data[column].iloc[position])
                for semantic, column in semantic_columns.items()
            }
        )
    core: dict[str, Any] = {
        "semantic_columns": semantic_columns,
        "dtypes": dtypes,
        "n_rows": int(len(study.data)),
        "records_fingerprint": fingerprint(records),
    }
    descriptor = dict(core)
    descriptor["study_fingerprint"] = fingerprint(core)
    return descriptor


def _build_qc_manifest(
    *,
    report: StudyQCReport,
    diagnostics: pd.DataFrame,
    decisions: tuple[StudyQCDecision, ...],
    study_descriptor: Mapping[str, Any],
    software: Mapping[str, Any],
) -> dict[str, Any]:
    decision_payloads = [decision.to_dict() for decision in decisions]
    scientific_core: dict[str, Any] = {
        "schema": STUDY_QC_SCHEMA,
        "study": _qc_normalize(dict(study_descriptor)),
        "report": _qc_normalize(report.to_dict()),
        "diagnostics": _qc_table_descriptor(diagnostics),
        "decisions": {
            "n_decisions": int(len(decisions)),
            "records_fingerprint": fingerprint(decision_payloads),
        },
    }
    manifest = dict(scientific_core)
    manifest["audit_fingerprint"] = fingerprint(scientific_core)
    manifest["software"] = _qc_normalize(dict(software))
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return manifest


def _qc_table_descriptor(frame: pd.DataFrame) -> dict[str, Any]:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("QC diagnostics must be a pandas DataFrame")
    records = [
        {str(key): _qc_normalize(value) for key, value in record.items()}
        for record in frame.to_dict(orient="records")
    ]
    return {
        "columns": [str(column) for column in frame.columns],
        "n_rows": int(len(frame)),
        "records_fingerprint": fingerprint(records),
    }


def _validate_decisions(
    report: StudyQCReport,
    diagnostics: pd.DataFrame,
    decisions: tuple[StudyQCDecision, ...],
) -> None:
    if any(not isinstance(decision, StudyQCDecision) for decision in decisions):
        raise TypeError("decisions must contain only StudyQCDecision values")
    available_issues = set(report.issue_codes)
    diagnostic_issues = {
        str(row.diagnostic_id): str(row.issue_code)
        for row in diagnostics.itertuples(index=False)
    }
    for decision in decisions:
        if decision.issue_code not in available_issues:
            raise ValueError(
                f"decision references unflagged issue code: {decision.issue_code!r}"
            )
        for diagnostic_id in decision.diagnostic_ids:
            if diagnostic_id not in diagnostic_issues:
                raise ValueError(f"unknown diagnostic_id in decision: {diagnostic_id!r}")
            if diagnostic_issues[diagnostic_id] != decision.issue_code:
                raise ValueError(
                    "decision diagnostic_ids must belong to the same issue_code"
                )


def _decisions_frame(decisions: tuple[StudyQCDecision, ...]) -> pd.DataFrame:
    rows = []
    for number, decision in enumerate(decisions, start=1):
        rows.append(
            {
                "decision_id": f"Q{number:06d}",
                "issue_code": decision.issue_code,
                "action": decision.action,
                "rationale": decision.rationale,
                "diagnostic_ids": "|".join(decision.diagnostic_ids),
            }
        )
    return pd.DataFrame(rows, columns=_DECISION_COLUMNS)


def _qc_normalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, np.generic):
        return _qc_normalize(value.item())
    if isinstance(value, float):
        if np.isnan(value):
            return None
        if np.isposinf(value):
            return {"__gazeaudit_nonfinite__": "positive_infinity"}
        if np.isneginf(value):
            return {"__gazeaudit_nonfinite__": "negative_infinity"}
        return value
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _qc_normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_qc_normalize(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_qc_normalize(item) for item in value.tolist()]
    missing = pd.isna(value)
    if isinstance(missing, (bool, np.bool_)) and bool(missing):
        return None
    raise TypeError(f"unsupported study QC provenance type: {type(value).__name__}")


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _nonempty_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()
