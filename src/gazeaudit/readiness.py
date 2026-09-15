"""Analysis-readiness governance for structural eye-tracking QC."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .provenance import canonical_json, fingerprint, software_environment
from .study import GazeStudy
from .study_qc import StudyQCAudit, audit_study_qc, build_study_qc_audit, verify_study_qc_audit

ANALYSIS_READINESS_SCHEMA = "gazeaudit-analysis-readiness-v1"
ANALYSIS_READINESS_ARTIFACT_SCHEMA = "gazeaudit-analysis-readiness-artifacts-v1"
ANALYSIS_READINESS_PUBLICATION_LINK_SCHEMA = "gazeaudit-analysis-readiness-publication-link-v1"
REPAIR_COMPARISON_SCHEMA = "gazeaudit-qc-repair-comparison-v1"

_TRIAL_METRICS = (
    "coordinate_issue_fraction",
    "timestamp_issue_fraction",
    "identifier_issue_fraction",
    "duplicate_timestamp_fraction",
)

_PARTICIPANT_METRICS = _TRIAL_METRICS + ("flagged_trial_fraction",)


@dataclass(frozen=True)
class ReadinessThresholds:
    """Researcher-declared structural-QC thresholds.

    Every field is optional. GazeAudit deliberately supplies no universal
    defaults: ``None`` means that a criterion is not part of the declared
    policy. Passing a policy means only that the data satisfy these declared
    structural thresholds; it is not a claim of scientific validity.
    """

    max_coordinate_issue_fraction: float | None = None
    max_timestamp_issue_fraction: float | None = None
    max_identifier_issue_fraction: float | None = None
    max_duplicate_timestamp_fraction: float | None = None
    max_flagged_trial_fraction: float | None = None
    min_rows_per_trial: int | None = None
    min_trials_per_participant: int | None = None
    require_monotonic_time: bool | None = None

    def __post_init__(self) -> None:
        for name in (
            "max_coordinate_issue_fraction",
            "max_timestamp_issue_fraction",
            "max_identifier_issue_fraction",
            "max_duplicate_timestamp_fraction",
            "max_flagged_trial_fraction",
        ):
            value = getattr(self, name)
            if value is None:
                continue
            number = float(value)
            if not np.isfinite(number) or not 0.0 <= number <= 1.0:
                raise ValueError(f"{name} must be finite and between 0 and 1")
            object.__setattr__(self, name, number)

        for name in ("min_rows_per_trial", "min_trials_per_participant"):
            value = getattr(self, name)
            if value is None:
                continue
            if isinstance(value, bool) or int(value) != value or int(value) < 1:
                raise ValueError(f"{name} must be a positive integer")
            object.__setattr__(self, name, int(value))

        if self.require_monotonic_time is not None and not isinstance(
            self.require_monotonic_time, bool
        ):
            raise TypeError("require_monotonic_time must be bool or None")

    @property
    def active_rules(self) -> tuple[str, ...]:
        """Names of criteria participating in this policy."""

        values = asdict(self)
        return tuple(
            name
            for name, value in values.items()
            if value is not None and not (name == "require_monotonic_time" and value is False)
        )

    @property
    def policy_fingerprint(self) -> str:
        """Deterministic fingerprint of the declared threshold policy."""

        return fingerprint(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic serialisable threshold mapping."""

        return asdict(self)


@dataclass(frozen=True)
class AnalysisReadinessReport:
    """Threshold evaluation, cohort impact, and provenance for one study."""

    policy_name: str
    thresholds: ReadinessThresholds
    qc_audit: StudyQCAudit
    trial_summary: pd.DataFrame
    participant_summary: pd.DataFrame
    cohort_impact: pd.DataFrame
    manifest: dict[str, Any]

    @property
    def status(self) -> str:
        """Policy status: ``unassessed``, ``ready_under_policy``, or ``review_under_policy``."""

        return str(self.manifest["status"])

    @property
    def policy_fingerprint(self) -> str:
        return str(self.manifest["thresholds"]["policy_fingerprint"])

    @property
    def readiness_fingerprint(self) -> str:
        return str(self.manifest["readiness_fingerprint"])

    @property
    def manifest_fingerprint(self) -> str:
        return str(self.manifest["manifest_fingerprint"])

    def manifest_json(self) -> str:
        return canonical_json(self.manifest)

    def trial_csv(self) -> str:
        return self.trial_summary.to_csv(index=False, lineterminator="\n")

    def participant_csv(self) -> str:
        return self.participant_summary.to_csv(index=False, lineterminator="\n")

    def cohort_impact_csv(self) -> str:
        return self.cohort_impact.to_csv(index=False, lineterminator="\n")


@dataclass(frozen=True)
class RepairComparison:
    """Before/after structural-QC comparison without assuming row correspondence."""

    before_audit: StudyQCAudit
    after_audit: StudyQCAudit
    metrics: pd.DataFrame
    manifest: dict[str, Any]

    @property
    def comparison_fingerprint(self) -> str:
        return str(self.manifest["comparison_fingerprint"])

    @property
    def manifest_fingerprint(self) -> str:
        return str(self.manifest["manifest_fingerprint"])

    def metrics_csv(self) -> str:
        return self.metrics.to_csv(index=False, lineterminator="\n")

    def manifest_json(self) -> str:
        return canonical_json(self.manifest)


def trial_qc_summary(study: GazeStudy) -> pd.DataFrame:
    """Return one deterministic structural-QC summary row per participant × trial unit."""

    _require_study(study)
    data = study.data.reset_index(drop=True)
    x = data[study.x].to_numpy(dtype=float, na_value=np.nan)
    y = data[study.y].to_numpy(dtype=float, na_value=np.nan)
    time = data[study.timestamp].to_numpy(dtype=float, na_value=np.nan)
    coordinate_issue = ~(np.isfinite(x) & np.isfinite(y))
    timestamp_issue = ~np.isfinite(time)
    identifier_issue = data[[study.participant, study.trial]].isna().any(axis=1).to_numpy()

    finite_time = np.isfinite(time)
    duplicate = np.zeros(len(data), dtype=bool)
    duplicate[finite_time] = (
        data.loc[finite_time]
        .duplicated(
            subset=[study.participant, study.trial, study.timestamp],
            keep=False,
        )
        .to_numpy()
    )

    rows: list[dict[str, Any]] = []
    grouped = data.groupby([study.participant, study.trial], sort=False, dropna=False)
    for number, (_, frame) in enumerate(grouped, start=1):
        positions = frame.index.to_numpy(dtype=int)
        finite_group_time = time[positions][np.isfinite(time[positions])]
        decreasing = bool(
            finite_group_time.size > 1 and np.any(np.diff(finite_group_time) < 0)
        )
        n_rows = int(len(positions))
        coord_n = int(coordinate_issue[positions].sum())
        time_n = int(timestamp_issue[positions].sum())
        ident_n = int(identifier_issue[positions].sum())
        duplicate_n = int(duplicate[positions].sum())
        row_issue = (
            coordinate_issue[positions]
            | timestamp_issue[positions]
            | identifier_issue[positions]
            | duplicate[positions]
        )
        rows.append(
            {
                "trial_unit_id": f"T{number:06d}",
                "participant": frame[study.participant].iloc[0],
                "trial": frame[study.trial].iloc[0],
                "n_rows": n_rows,
                "coordinate_issue_rows": coord_n,
                "coordinate_issue_fraction": coord_n / n_rows,
                "timestamp_issue_rows": time_n,
                "timestamp_issue_fraction": time_n / n_rows,
                "identifier_issue_rows": ident_n,
                "identifier_issue_fraction": ident_n / n_rows,
                "duplicate_timestamp_rows": duplicate_n,
                "duplicate_timestamp_fraction": duplicate_n / n_rows,
                "any_row_issue_rows": int(row_issue.sum()),
                "any_row_issue_fraction": float(row_issue.mean()),
                "decreasing_time": decreasing,
            }
        )
    return pd.DataFrame(rows)


def participant_qc_summary(study: GazeStudy) -> pd.DataFrame:
    """Return one deterministic structural-QC summary row per participant unit."""

    trial = trial_qc_summary(study)
    rows: list[dict[str, Any]] = []
    grouped = trial.groupby("participant", sort=False, dropna=False)
    for number, (_, frame) in enumerate(grouped, start=1):
        n_rows = int(frame["n_rows"].sum())
        n_trials = int(len(frame))
        rows.append(
            {
                "participant_unit_id": f"P{number:06d}",
                "participant": frame["participant"].iloc[0],
                "n_rows": n_rows,
                "n_trials": n_trials,
                "coordinate_issue_rows": int(frame["coordinate_issue_rows"].sum()),
                "coordinate_issue_fraction": float(
                    frame["coordinate_issue_rows"].sum() / n_rows
                ),
                "timestamp_issue_rows": int(frame["timestamp_issue_rows"].sum()),
                "timestamp_issue_fraction": float(
                    frame["timestamp_issue_rows"].sum() / n_rows
                ),
                "identifier_issue_rows": int(frame["identifier_issue_rows"].sum()),
                "identifier_issue_fraction": float(
                    frame["identifier_issue_rows"].sum() / n_rows
                ),
                "duplicate_timestamp_rows": int(frame["duplicate_timestamp_rows"].sum()),
                "duplicate_timestamp_fraction": float(
                    frame["duplicate_timestamp_rows"].sum() / n_rows
                ),
                "any_row_issue_rows": int(frame["any_row_issue_rows"].sum()),
                "any_row_issue_fraction": float(frame["any_row_issue_rows"].sum() / n_rows),
                "decreasing_time_trials": int(frame["decreasing_time"].sum()),
            }
        )
    return pd.DataFrame(rows)


def evaluate_analysis_readiness(
    study: GazeStudy,
    thresholds: ReadinessThresholds,
    *,
    policy_name: str = "declared_policy",
    qc_audit: StudyQCAudit | None = None,
) -> AnalysisReadinessReport:
    """Evaluate researcher-declared structural thresholds and preview cohort impact.

    No threshold is supplied by default and no flagged unit is automatically
    excluded. The resulting status is explicitly policy-relative.
    """

    _require_study(study)
    if not isinstance(thresholds, ReadinessThresholds):
        raise TypeError("thresholds must be ReadinessThresholds")
    policy_name = _nonempty_text(policy_name, "policy_name")

    if qc_audit is None:
        qc_audit = build_study_qc_audit(study)
    elif not isinstance(qc_audit, StudyQCAudit):
        raise TypeError("qc_audit must be StudyQCAudit or None")
    elif not verify_study_qc_audit(qc_audit):
        raise ValueError("qc_audit does not match its manifest")

    current_study_fingerprint = build_study_qc_audit(study).study_fingerprint
    if qc_audit.study_fingerprint != current_study_fingerprint:
        raise ValueError("qc_audit was built from a different canonical study view")

    trial = trial_qc_summary(study)
    trial_failures = [
        _trial_failures(row, thresholds) for row in trial.to_dict(orient="records")
    ]
    trial["failed_rules"] = ["|".join(values) for values in trial_failures]
    trial["n_failed_rules"] = [len(values) for values in trial_failures]
    trial["passes_thresholds"] = trial["n_failed_rules"].eq(0)

    participant = _participant_summary_from_trials(trial)
    participant_failures = [
        _participant_failures(row, thresholds)
        for row in participant.to_dict(orient="records")
    ]
    participant["failed_rules"] = ["|".join(values) for values in participant_failures]
    participant["n_failed_rules"] = [len(values) for values in participant_failures]
    participant["passes_thresholds"] = participant["n_failed_rules"].eq(0)

    impact = _cohort_impact_table(trial, participant)
    if not thresholds.active_rules:
        status = "unassessed"
    elif bool(trial["passes_thresholds"].all()) and bool(
        participant["passes_thresholds"].all()
    ):
        status = "ready_under_policy"
    else:
        status = "review_under_policy"

    manifest = _build_readiness_manifest(
        policy_name=policy_name,
        thresholds=thresholds,
        qc_audit=qc_audit,
        trial=trial,
        participant=participant,
        impact=impact,
        status=status,
        software=software_environment(),
    )
    return AnalysisReadinessReport(
        policy_name=policy_name,
        thresholds=thresholds,
        qc_audit=qc_audit,
        trial_summary=trial.copy(deep=True),
        participant_summary=participant.copy(deep=True),
        cohort_impact=impact.copy(deep=True),
        manifest=manifest,
    )


def cohort_impact_preview(
    report: AnalysisReadinessReport,
    *,
    scope: str | None = None,
) -> pd.DataFrame:
    """Return the no-mutation cohort impact preview for a declared policy."""

    _require_readiness_report(report)
    if scope is None:
        return report.cohort_impact.copy(deep=True)
    if scope not in {"trial", "participant"}:
        raise ValueError("scope must be 'trial', 'participant', or None")
    return report.cohort_impact.loc[report.cohort_impact["scope"] == scope].reset_index(
        drop=True
    )


def filter_study_by_readiness(
    study: GazeStudy,
    report: AnalysisReadinessReport,
    *,
    scope: str = "trial",
) -> GazeStudy:
    """Apply an already-declared readiness policy only when the caller explicitly asks.

    This function is intentionally separate from evaluation/preview so inspecting
    threshold impact never mutates or filters the study.
    """

    _require_study(study)
    _require_readiness_report(report)
    if scope not in {"trial", "participant"}:
        raise ValueError("scope must be 'trial' or 'participant'")
    if report.status == "unassessed":
        raise ValueError("cannot filter with a readiness policy that has no active rules")

    current = build_study_qc_audit(study)
    if current.study_fingerprint != report.qc_audit.study_fingerprint:
        raise ValueError("report was built from a different canonical study view")

    if scope == "trial":
        keep_ids = set(
            report.trial_summary.loc[
                report.trial_summary["passes_thresholds"], "trial_unit_id"
            ].astype(str)
        )
        unit_ids = _trial_unit_labels(study)
    else:
        keep_ids = set(
            report.participant_summary.loc[
                report.participant_summary["passes_thresholds"], "participant_unit_id"
            ].astype(str)
        )
        unit_ids = _participant_unit_labels(study)

    keep = np.array([unit_id in keep_ids for unit_id in unit_ids], dtype=bool)
    if not bool(keep.any()):
        raise ValueError("declared readiness policy would remove every row")
    return study.copy_with(study.data.reset_index(drop=True).loc[keep].reset_index(drop=True))


def readiness_policy_table(
    study: GazeStudy,
    policies: Mapping[str, ReadinessThresholds],
) -> pd.DataFrame:
    """Compare several declared policies without applying any exclusions."""

    _require_study(study)
    if not isinstance(policies, Mapping) or not policies:
        raise ValueError("policies must be a non-empty mapping")
    rows: list[dict[str, Any]] = []
    for name, thresholds in policies.items():
        name = _nonempty_text(str(name), "policy name")
        report = evaluate_analysis_readiness(study, thresholds, policy_name=name)
        trial_impact = cohort_impact_preview(report, scope="trial").iloc[0]
        participant_impact = cohort_impact_preview(report, scope="participant").iloc[0]
        rows.append(
            {
                "policy": name,
                "policy_fingerprint": report.policy_fingerprint,
                "status": report.status,
                "active_rules": "|".join(thresholds.active_rules),
                "trial_retained_row_fraction": float(
                    trial_impact["retained_row_fraction"]
                ),
                "trial_retained_trial_fraction": float(
                    trial_impact["retained_trial_unit_fraction"]
                ),
                "participant_retained_row_fraction": float(
                    participant_impact["retained_row_fraction"]
                ),
                "participant_retained_participant_fraction": float(
                    participant_impact["retained_participant_unit_fraction"]
                ),
            }
        )
    return pd.DataFrame(rows)


def readiness_pipeline_processor(
    policies: Mapping[str, ReadinessThresholds],
    *,
    choice_name: str = "readiness_policy",
    scope: str = "trial",
) -> Callable[[GazeStudy, Mapping[str, Any]], GazeStudy]:
    """Return a ``run_specs`` processor that makes the readiness policy explicit."""

    if not isinstance(policies, Mapping) or not policies:
        raise ValueError("policies must be a non-empty mapping")
    normalized = {
        _nonempty_text(str(name), "policy name"): value for name, value in policies.items()
    }
    if any(not isinstance(value, ReadinessThresholds) for value in normalized.values()):
        raise TypeError("all policies must be ReadinessThresholds")
    choice_name = _nonempty_text(choice_name, "choice_name")
    if scope not in {"trial", "participant"}:
        raise ValueError("scope must be 'trial' or 'participant'")

    def processor(study: GazeStudy, specification: Mapping[str, Any]) -> GazeStudy:
        if choice_name not in specification:
            raise ValueError(f"specification is missing readiness choice {choice_name!r}")
        policy_name = str(specification[choice_name])
        if policy_name not in normalized:
            raise ValueError(f"unknown readiness policy: {policy_name!r}")
        report = evaluate_analysis_readiness(
            study,
            normalized[policy_name],
            policy_name=policy_name,
        )
        return filter_study_by_readiness(study, report, scope=scope)

    return processor


def compare_qc_states(
    before: GazeStudy,
    after: GazeStudy,
) -> RepairComparison:
    """Compare structural QC before and after an explicitly performed repair.

    The function does not infer that changes were beneficial, valid, or caused by
    a particular repair. It records metric deltas and binds both canonical study
    views into deterministic provenance.
    """

    _require_study(before)
    _require_study(after)
    before_audit = build_study_qc_audit(before)
    after_audit = build_study_qc_audit(after)
    before_report = audit_study_qc(before).to_dict()
    after_report = audit_study_qc(after).to_dict()
    metric_names = (
        "n_rows",
        "n_participants",
        "n_trials",
        "missing_x_rows",
        "missing_y_rows",
        "missing_timestamp_rows",
        "infinite_x_rows",
        "infinite_y_rows",
        "infinite_timestamp_rows",
        "missing_identifier_rows",
        "duplicate_timestamp_rows",
        "decreasing_time_groups",
        "coordinate_issue_rows",
        "timestamp_issue_rows",
    )
    metrics = pd.DataFrame(
        [
            {
                "metric": metric,
                "before": int(before_report[metric]),
                "after": int(after_report[metric]),
                "delta": int(after_report[metric]) - int(before_report[metric]),
            }
            for metric in metric_names
        ]
    )
    scientific_core = {
        "schema": REPAIR_COMPARISON_SCHEMA,
        "before_study_fingerprint": before_audit.study_fingerprint,
        "before_qc_audit_fingerprint": before_audit.audit_fingerprint,
        "after_study_fingerprint": after_audit.study_fingerprint,
        "after_qc_audit_fingerprint": after_audit.audit_fingerprint,
        "metrics": _table_descriptor(metrics),
    }
    manifest = dict(scientific_core)
    manifest["comparison_fingerprint"] = fingerprint(scientific_core)
    manifest["software"] = _normalize(dict(software_environment()))
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return RepairComparison(
        before_audit=before_audit,
        after_audit=after_audit,
        metrics=metrics,
        manifest=manifest,
    )


def verify_repair_comparison_manifest(manifest: Mapping[str, Any]) -> bool:
    """Verify fingerprints carried by a serialized repair-comparison manifest."""

    try:
        if manifest.get("schema") != REPAIR_COMPARISON_SCHEMA:
            return False
        scientific_core = {
            "schema": manifest["schema"],
            "before_study_fingerprint": manifest["before_study_fingerprint"],
            "before_qc_audit_fingerprint": manifest["before_qc_audit_fingerprint"],
            "after_study_fingerprint": manifest["after_study_fingerprint"],
            "after_qc_audit_fingerprint": manifest["after_qc_audit_fingerprint"],
            "metrics": manifest["metrics"],
        }
        if fingerprint(scientific_core) != manifest["comparison_fingerprint"]:
            return False
        complete = dict(manifest)
        stored = str(complete.pop("manifest_fingerprint"))
        return fingerprint(complete) == stored
    except (KeyError, TypeError, ValueError):
        return False


def verify_repair_comparison(comparison: RepairComparison) -> bool:
    """Return whether a before/after comparison still matches its provenance."""

    if not isinstance(comparison, RepairComparison):
        raise TypeError("comparison must be RepairComparison")
    try:
        if not verify_study_qc_audit(comparison.before_audit):
            return False
        if not verify_study_qc_audit(comparison.after_audit):
            return False
        software = comparison.manifest.get("software")
        if not isinstance(software, Mapping):
            return False
        scientific_core = {
            "schema": REPAIR_COMPARISON_SCHEMA,
            "before_study_fingerprint": comparison.before_audit.study_fingerprint,
            "before_qc_audit_fingerprint": comparison.before_audit.audit_fingerprint,
            "after_study_fingerprint": comparison.after_audit.study_fingerprint,
            "after_qc_audit_fingerprint": comparison.after_audit.audit_fingerprint,
            "metrics": _table_descriptor(comparison.metrics),
        }
        expected = dict(scientific_core)
        expected["comparison_fingerprint"] = fingerprint(scientific_core)
        expected["software"] = _normalize(dict(software))
        expected["manifest_fingerprint"] = fingerprint(expected)
        return (
            canonical_json(expected) == canonical_json(comparison.manifest)
            and verify_repair_comparison_manifest(comparison.manifest)
        )
    except (KeyError, TypeError, ValueError):
        return False


def verify_analysis_readiness_manifest(manifest: Mapping[str, Any]) -> bool:
    """Verify fingerprints carried by a serialized readiness manifest."""

    try:
        if manifest.get("schema") != ANALYSIS_READINESS_SCHEMA:
            return False
        scientific_core = {
            "schema": manifest["schema"],
            "policy_name": manifest["policy_name"],
            "status": manifest["status"],
            "thresholds": manifest["thresholds"],
            "study_fingerprint": manifest["study_fingerprint"],
            "qc_audit_fingerprint": manifest["qc_audit_fingerprint"],
            "trial_summary": manifest["trial_summary"],
            "participant_summary": manifest["participant_summary"],
            "cohort_impact": manifest["cohort_impact"],
        }
        if fingerprint(scientific_core) != manifest["readiness_fingerprint"]:
            return False
        complete = dict(manifest)
        stored = str(complete.pop("manifest_fingerprint"))
        return fingerprint(complete) == stored
    except (KeyError, TypeError, ValueError):
        return False


def verify_analysis_readiness_report(report: AnalysisReadinessReport) -> bool:
    """Return whether a readiness report still matches its deterministic manifest."""

    _require_readiness_report(report, verify=False)
    try:
        if not verify_study_qc_audit(report.qc_audit):
            return False
        software = report.manifest.get("software")
        if not isinstance(software, Mapping):
            return False
        expected = _build_readiness_manifest(
            policy_name=report.policy_name,
            thresholds=report.thresholds,
            qc_audit=report.qc_audit,
            trial=report.trial_summary,
            participant=report.participant_summary,
            impact=report.cohort_impact,
            status=report.status,
            software=software,
        )
        return (
            canonical_json(expected) == canonical_json(report.manifest)
            and verify_analysis_readiness_manifest(report.manifest)
        )
    except (KeyError, TypeError, ValueError):
        return False


def analysis_readiness_publication_metadata(
    report: AnalysisReadinessReport,
) -> dict[str, Any]:
    """Return compact policy-relative readiness provenance for publication metadata."""

    _require_readiness_report(report)
    return {
        "schema": ANALYSIS_READINESS_PUBLICATION_LINK_SCHEMA,
        "policy_name": report.policy_name,
        "status": report.status,
        "active_rules": list(report.thresholds.active_rules),
        "policy_fingerprint": report.policy_fingerprint,
        "qc_audit_fingerprint": report.qc_audit.audit_fingerprint,
        "readiness_fingerprint": report.readiness_fingerprint,
        "n_trial_units": int(len(report.trial_summary)),
        "n_participant_units": int(len(report.participant_summary)),
    }


def write_analysis_readiness_artifacts(
    report: AnalysisReadinessReport,
    output_dir: str | Path,
    *,
    repair_comparison: RepairComparison | None = None,
) -> dict[str, Path]:
    """Write deterministic readiness CSV/JSON evidence and an integrity manifest."""

    _require_readiness_report(report)
    if repair_comparison is not None and not verify_repair_comparison(repair_comparison):
        raise ValueError("repair_comparison does not match its manifest")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    payloads: dict[str, str] = {
        "analysis_readiness.json": report.manifest_json() + "\n",
        "readiness_thresholds.json": canonical_json(report.thresholds.to_dict()) + "\n",
        "trial_readiness.csv": report.trial_csv(),
        "participant_readiness.csv": report.participant_csv(),
        "cohort_impact.csv": report.cohort_impact_csv(),
    }
    if repair_comparison is not None:
        payloads["repair_comparison.csv"] = repair_comparison.metrics_csv()
        payloads["repair_comparison.json"] = repair_comparison.manifest_json() + "\n"

    files = {
        name: {
            "sha256": _sha256_text(content),
            "bytes": len(content.encode("utf-8")),
        }
        for name, content in payloads.items()
    }
    artifact_manifest: dict[str, Any] = {
        "schema": ANALYSIS_READINESS_ARTIFACT_SCHEMA,
        "readiness_fingerprint": report.readiness_fingerprint,
        "repair_comparison_fingerprint": (
            repair_comparison.comparison_fingerprint if repair_comparison is not None else None
        ),
        "files": files,
    }
    artifact_manifest["artifact_fingerprint"] = fingerprint(artifact_manifest)
    payloads["analysis_readiness_artifacts.json"] = canonical_json(artifact_manifest) + "\n"

    paths: dict[str, Path] = {}
    for name, content in payloads.items():
        path = destination / name
        path.write_text(content, encoding="utf-8", newline="")
        paths[name] = path
    return paths


def verify_analysis_readiness_artifacts(output_dir: str | Path) -> bool:
    """Verify a written readiness evidence directory byte-for-byte."""

    destination = Path(output_dir)
    manifest_path = destination / "analysis_readiness_artifacts.json"
    if not manifest_path.is_file():
        return False
    try:
        artifact = json.loads(manifest_path.read_text(encoding="utf-8"))
        if artifact.get("schema") != ANALYSIS_READINESS_ARTIFACT_SCHEMA:
            return False
        complete = dict(artifact)
        stored = str(complete.pop("artifact_fingerprint"))
        if fingerprint(complete) != stored:
            return False
        files = artifact["files"]
        required = {
            "analysis_readiness.json",
            "readiness_thresholds.json",
            "trial_readiness.csv",
            "participant_readiness.csv",
            "cohort_impact.csv",
        }
        optional = {"repair_comparison.csv", "repair_comparison.json"}
        if not required <= set(files) or not set(files) <= required | optional:
            return False
        if ("repair_comparison.csv" in files) != ("repair_comparison.json" in files):
            return False
        for name, descriptor in files.items():
            path = destination / name
            if not path.is_file():
                return False
            payload = path.read_bytes()
            if len(payload) != int(descriptor["bytes"]):
                return False
            if hashlib.sha256(payload).hexdigest() != descriptor["sha256"]:
                return False
        readiness_manifest = json.loads(
            (destination / "analysis_readiness.json").read_text(encoding="utf-8")
        )
        if not verify_analysis_readiness_manifest(readiness_manifest):
            return False
        if readiness_manifest.get("readiness_fingerprint") != artifact[
            "readiness_fingerprint"
        ]:
            return False
        if "repair_comparison.json" in files:
            repair = json.loads(
                (destination / "repair_comparison.json").read_text(encoding="utf-8")
            )
            if not verify_repair_comparison_manifest(repair):
                return False
            if repair.get("comparison_fingerprint") != artifact[
                "repair_comparison_fingerprint"
            ]:
                return False
        return True
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return False


def _participant_summary_from_trials(trial: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = trial.groupby("participant", sort=False, dropna=False)
    for number, (_, frame) in enumerate(grouped, start=1):
        n_rows = int(frame["n_rows"].sum())
        n_trials = int(len(frame))
        rows.append(
            {
                "participant_unit_id": f"P{number:06d}",
                "participant": frame["participant"].iloc[0],
                "n_rows": n_rows,
                "n_trials": n_trials,
                "flagged_trials": int((~frame["passes_thresholds"]).sum()),
                "flagged_trial_fraction": float((~frame["passes_thresholds"]).mean()),
                "coordinate_issue_rows": int(frame["coordinate_issue_rows"].sum()),
                "coordinate_issue_fraction": float(
                    frame["coordinate_issue_rows"].sum() / n_rows
                ),
                "timestamp_issue_rows": int(frame["timestamp_issue_rows"].sum()),
                "timestamp_issue_fraction": float(
                    frame["timestamp_issue_rows"].sum() / n_rows
                ),
                "identifier_issue_rows": int(frame["identifier_issue_rows"].sum()),
                "identifier_issue_fraction": float(
                    frame["identifier_issue_rows"].sum() / n_rows
                ),
                "duplicate_timestamp_rows": int(frame["duplicate_timestamp_rows"].sum()),
                "duplicate_timestamp_fraction": float(
                    frame["duplicate_timestamp_rows"].sum() / n_rows
                ),
                "any_row_issue_rows": int(frame["any_row_issue_rows"].sum()),
                "any_row_issue_fraction": float(frame["any_row_issue_rows"].sum() / n_rows),
                "decreasing_time_trials": int(frame["decreasing_time"].sum()),
            }
        )
    return pd.DataFrame(rows)


def _trial_failures(row: Mapping[str, Any], thresholds: ReadinessThresholds) -> tuple[str, ...]:
    failures: list[str] = []
    threshold_map = {
        "max_coordinate_issue_fraction": "coordinate_issue_fraction",
        "max_timestamp_issue_fraction": "timestamp_issue_fraction",
        "max_identifier_issue_fraction": "identifier_issue_fraction",
        "max_duplicate_timestamp_fraction": "duplicate_timestamp_fraction",
    }
    for rule, metric in threshold_map.items():
        limit = getattr(thresholds, rule)
        if limit is not None and float(row[metric]) > float(limit):
            failures.append(rule)
    if (
        thresholds.min_rows_per_trial is not None
        and int(row["n_rows"]) < thresholds.min_rows_per_trial
    ):
        failures.append("min_rows_per_trial")
    if thresholds.require_monotonic_time is True and bool(row["decreasing_time"]):
        failures.append("require_monotonic_time")
    return tuple(failures)


def _participant_failures(
    row: Mapping[str, Any],
    thresholds: ReadinessThresholds,
) -> tuple[str, ...]:
    failures: list[str] = []
    threshold_map = {
        "max_coordinate_issue_fraction": "coordinate_issue_fraction",
        "max_timestamp_issue_fraction": "timestamp_issue_fraction",
        "max_identifier_issue_fraction": "identifier_issue_fraction",
        "max_duplicate_timestamp_fraction": "duplicate_timestamp_fraction",
        "max_flagged_trial_fraction": "flagged_trial_fraction",
    }
    for rule, metric in threshold_map.items():
        limit = getattr(thresholds, rule)
        if limit is not None and float(row[metric]) > float(limit):
            failures.append(rule)
    if (
        thresholds.min_trials_per_participant is not None
        and int(row["n_trials"]) < thresholds.min_trials_per_participant
    ):
        failures.append("min_trials_per_participant")
    if thresholds.require_monotonic_time is True and int(row["decreasing_time_trials"]) > 0:
        failures.append("require_monotonic_time")
    return tuple(failures)


def _cohort_impact_table(
    trial: pd.DataFrame,
    participant: pd.DataFrame,
) -> pd.DataFrame:
    baseline_rows = int(trial["n_rows"].sum())
    baseline_trials = int(len(trial))
    baseline_participants = int(len(participant))

    participant_lookup: dict[str, str] = {}
    for participant_row in participant.itertuples(index=False):
        participant_lookup[_unit_value_key(participant_row.participant)] = str(
            participant_row.participant_unit_id
        )
    trial_participant_units = trial["participant"].map(
        lambda value: participant_lookup[_unit_value_key(value)]
    )

    trial_keep = trial["passes_thresholds"].to_numpy(dtype=bool)
    retained_trial_rows = int(trial.loc[trial_keep, "n_rows"].sum())
    retained_trial_units = int(trial_keep.sum())
    retained_trial_participants = int(trial_participant_units.loc[trial_keep].nunique())

    participant_keep = participant["passes_thresholds"].to_numpy(dtype=bool)
    retained_participant_units = int(participant_keep.sum())
    retained_participant_rows = int(
        participant.loc[participant_keep, "n_rows"].sum()
    )
    retained_participant_ids = set(
        participant.loc[participant_keep, "participant_unit_id"].astype(str)
    )
    participant_scope_trial_keep = trial_participant_units.isin(retained_participant_ids)
    retained_participant_trials = int(participant_scope_trial_keep.sum())

    rows = [
        _impact_row(
            scope="trial",
            baseline_rows=baseline_rows,
            baseline_trials=baseline_trials,
            baseline_participants=baseline_participants,
            retained_rows=retained_trial_rows,
            retained_trials=retained_trial_units,
            retained_participants=retained_trial_participants,
        ),
        _impact_row(
            scope="participant",
            baseline_rows=baseline_rows,
            baseline_trials=baseline_trials,
            baseline_participants=baseline_participants,
            retained_rows=retained_participant_rows,
            retained_trials=retained_participant_trials,
            retained_participants=retained_participant_units,
        ),
    ]
    return pd.DataFrame(rows)


def _impact_row(
    *,
    scope: str,
    baseline_rows: int,
    baseline_trials: int,
    baseline_participants: int,
    retained_rows: int,
    retained_trials: int,
    retained_participants: int,
) -> dict[str, Any]:
    return {
        "scope": scope,
        "baseline_rows": baseline_rows,
        "retained_rows": retained_rows,
        "excluded_rows": baseline_rows - retained_rows,
        "retained_row_fraction": retained_rows / baseline_rows,
        "baseline_trial_units": baseline_trials,
        "retained_trial_units": retained_trials,
        "excluded_trial_units": baseline_trials - retained_trials,
        "retained_trial_unit_fraction": retained_trials / baseline_trials,
        "baseline_participant_units": baseline_participants,
        "retained_participant_units": retained_participants,
        "excluded_participant_units": baseline_participants - retained_participants,
        "retained_participant_unit_fraction": (
            retained_participants / baseline_participants
        ),
    }


def _build_readiness_manifest(
    *,
    policy_name: str,
    thresholds: ReadinessThresholds,
    qc_audit: StudyQCAudit,
    trial: pd.DataFrame,
    participant: pd.DataFrame,
    impact: pd.DataFrame,
    status: str,
    software: Mapping[str, Any],
) -> dict[str, Any]:
    if status not in {"unassessed", "ready_under_policy", "review_under_policy"}:
        raise ValueError("invalid readiness status")
    scientific_core = {
        "schema": ANALYSIS_READINESS_SCHEMA,
        "policy_name": policy_name,
        "status": status,
        "thresholds": {
            "values": _normalize(thresholds.to_dict()),
            "active_rules": list(thresholds.active_rules),
            "policy_fingerprint": thresholds.policy_fingerprint,
        },
        "study_fingerprint": qc_audit.study_fingerprint,
        "qc_audit_fingerprint": qc_audit.audit_fingerprint,
        "trial_summary": _table_descriptor(trial),
        "participant_summary": _table_descriptor(participant),
        "cohort_impact": _table_descriptor(impact),
    }
    manifest = dict(scientific_core)
    manifest["readiness_fingerprint"] = fingerprint(scientific_core)
    manifest["software"] = _normalize(dict(software))
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return manifest


def _table_descriptor(frame: pd.DataFrame) -> dict[str, Any]:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("readiness table must be a pandas DataFrame")
    records = [
        {str(key): _normalize(value) for key, value in record.items()}
        for record in frame.to_dict(orient="records")
    ]
    return {
        "columns": [str(column) for column in frame.columns],
        "n_rows": int(len(frame)),
        "records_fingerprint": fingerprint(records),
    }


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, np.generic):
        return _normalize(value.item())
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
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_normalize(item) for item in value.tolist()]
    missing = pd.isna(value)
    if isinstance(missing, (bool, np.bool_)) and bool(missing):
        return None
    raise TypeError(f"unsupported analysis-readiness provenance type: {type(value).__name__}")


def _trial_unit_labels(study: GazeStudy) -> list[str]:
    data = study.data.reset_index(drop=True)
    labels = [""] * len(data)
    grouped = data.groupby([study.participant, study.trial], sort=False, dropna=False)
    for number, (_, frame) in enumerate(grouped, start=1):
        label = f"T{number:06d}"
        for position in frame.index:
            labels[int(position)] = label
    return labels


def _participant_unit_labels(study: GazeStudy) -> list[str]:
    data = study.data.reset_index(drop=True)
    labels = [""] * len(data)
    grouped = data.groupby(study.participant, sort=False, dropna=False)
    for number, (_, frame) in enumerate(grouped, start=1):
        label = f"P{number:06d}"
        for position in frame.index:
            labels[int(position)] = label
    return labels


def _unit_value_key(value: Any) -> str:
    return canonical_json(_normalize(value))


def _require_study(study: GazeStudy) -> None:
    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")


def _require_readiness_report(
    report: AnalysisReadinessReport,
    *,
    verify: bool = True,
) -> None:
    if not isinstance(report, AnalysisReadinessReport):
        raise TypeError("report must be AnalysisReadinessReport")
    if verify and not verify_analysis_readiness_report(report):
        raise ValueError("analysis readiness report does not match its manifest")


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _nonempty_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()
