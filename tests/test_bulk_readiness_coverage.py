from __future__ import annotations

import json
import runpy
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import gazeaudit.readiness as readiness
from gazeaudit.study_qc import build_study_qc_audit


ROOT = Path(__file__).resolve().parents[1]


def _demo() -> dict[str, object]:
    namespace = runpy.run_path(
        str(ROOT / "examples" / "analysis_readiness.py")
    )
    return namespace["run_demo"]()


def _rewrite_artifact(
    root: Path,
    mutate,
) -> dict[str, object]:
    path = root / "analysis_readiness_artifacts.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    core = dict(document)
    core.pop("artifact_fingerprint", None)
    document["artifact_fingerprint"] = readiness.fingerprint(core)
    path.write_text(
        readiness.canonical_json(document) + "\n",
        encoding="utf-8",
    )
    return document


def _write_artifacts(
    tmp_path: Path,
    *,
    with_repair: bool = True,
) -> tuple[Path, object, object]:
    demo = _demo()
    report = demo["readiness"]
    comparison = demo["repair_comparison"]
    root = tmp_path / "artifacts"
    readiness.write_analysis_readiness_artifacts(
        report,
        root,
        repair_comparison=comparison if with_repair else None,
    )
    return root, report, comparison


def test_readiness_properties_and_participant_summary_paths() -> None:
    demo = _demo()
    report = demo["readiness"]
    comparison = demo["repair_comparison"]

    assert report.manifest_fingerprint == report.manifest["manifest_fingerprint"]
    assert comparison.manifest_fingerprint == comparison.manifest["manifest_fingerprint"]

    summary = readiness.participant_qc_summary(demo["study"])
    assert len(summary) == 3
    assert summary["participant_unit_id"].tolist() == [
        "P000001",
        "P000002",
        "P000003",
    ]
    assert summary["n_rows"].sum() == len(demo["study"].data)


def test_evaluate_readiness_rejects_invalid_threshold_and_qc_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo = _demo()
    study = demo["study"]

    with pytest.raises(TypeError, match="thresholds"):
        readiness.evaluate_analysis_readiness(
            study,
            object(),  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="qc_audit"):
        readiness.evaluate_analysis_readiness(
            study,
            readiness.ReadinessThresholds(),
            qc_audit=object(),  # type: ignore[arg-type]
        )

    audit = build_study_qc_audit(study)
    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        lambda _audit: False,
    )
    with pytest.raises(ValueError, match="does not match its manifest"):
        readiness.evaluate_analysis_readiness(
            study,
            readiness.ReadinessThresholds(),
            qc_audit=audit,
        )


def test_evaluate_readiness_rejects_audit_from_other_study() -> None:
    demo = _demo()
    other = demo["repaired"]
    wrong_audit = build_study_qc_audit(other)

    with pytest.raises(ValueError, match="different canonical study"):
        readiness.evaluate_analysis_readiness(
            demo["study"],
            readiness.ReadinessThresholds(),
            qc_audit=wrong_audit,
        )


def test_cohort_preview_and_filter_guardrails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo = _demo()
    report = demo["readiness"]
    study = demo["study"]

    full = readiness.cohort_impact_preview(report)
    assert len(full) == 2

    with pytest.raises(ValueError, match="scope must be"):
        readiness.cohort_impact_preview(report, scope="bad")

    with pytest.raises(ValueError, match="scope must be"):
        readiness.filter_study_by_readiness(study, report, scope="bad")

    with pytest.raises(ValueError, match="different canonical study"):
        readiness.filter_study_by_readiness(
            demo["repaired"],
            report,
            scope="trial",
        )

    participant = readiness.filter_study_by_readiness(
        study,
        report,
        scope="participant",
    )
    assert 0 < len(participant.data) <= len(study.data)

    no_pass = report.participant_summary.copy()
    no_pass["passes_thresholds"] = False
    forced = replace(report, participant_summary=no_pass)
    monkeypatch.setattr(
        readiness,
        "_require_readiness_report",
        lambda *args, **kwargs: None,
    )
    with pytest.raises(ValueError, match="remove every row"):
        readiness.filter_study_by_readiness(
            study,
            forced,
            scope="participant",
        )


def test_readiness_policy_table_and_processor_guards() -> None:
    demo = _demo()
    study = demo["study"]
    policies = demo["policies"]

    with pytest.raises(ValueError, match="non-empty mapping"):
        readiness.readiness_policy_table(study, {})

    with pytest.raises(ValueError, match="non-empty mapping"):
        readiness.readiness_pipeline_processor({})

    with pytest.raises(TypeError, match="all policies"):
        readiness.readiness_pipeline_processor({"bad": object()})

    with pytest.raises(ValueError, match="scope must be"):
        readiness.readiness_pipeline_processor(
            policies,
            scope="bad",
        )

    processor = readiness.readiness_pipeline_processor(policies)

    with pytest.raises(ValueError, match="missing readiness choice"):
        processor(study, {})

    with pytest.raises(ValueError, match="unknown readiness policy"):
        processor(study, {"readiness_policy": "does-not-exist"})


@pytest.mark.parametrize(
    ("thresholds", "row", "expected"),
    [
        (
            readiness.ReadinessThresholds(min_rows_per_trial=10),
            {
                "coordinate_issue_fraction": 0.0,
                "timestamp_issue_fraction": 0.0,
                "identifier_issue_fraction": 0.0,
                "duplicate_timestamp_fraction": 0.0,
                "n_rows": 2,
                "decreasing_time": False,
            },
            "min_rows_per_trial",
        ),
        (
            readiness.ReadinessThresholds(min_trials_per_participant=3),
            {
                "coordinate_issue_fraction": 0.0,
                "timestamp_issue_fraction": 0.0,
                "identifier_issue_fraction": 0.0,
                "duplicate_timestamp_fraction": 0.0,
                "flagged_trial_fraction": 0.0,
                "n_trials": 1,
                "decreasing_time_trials": 0,
            },
            "min_trials_per_participant",
        ),
    ],
)
def test_minimum_count_failure_labels(
    thresholds: readiness.ReadinessThresholds,
    row: dict[str, object],
    expected: str,
) -> None:
    if "n_rows" in row:
        result = readiness._trial_failures(row, thresholds)
    else:
        result = readiness._participant_failures(row, thresholds)
    assert expected in result


def test_readiness_manifest_verifiers_fail_closed() -> None:
    demo = _demo()
    report = demo["readiness"]
    comparison = demo["repair_comparison"]

    bad = dict(comparison.manifest)
    bad["schema"] = "wrong"
    assert not readiness.verify_repair_comparison_manifest(bad)

    bad = dict(comparison.manifest)
    bad["comparison_fingerprint"] = "0" * 64
    assert not readiness.verify_repair_comparison_manifest(bad)

    assert not readiness.verify_repair_comparison_manifest({})

    bad = dict(report.manifest)
    bad["schema"] = "wrong"
    assert not readiness.verify_analysis_readiness_manifest(bad)

    bad = dict(report.manifest)
    bad["readiness_fingerprint"] = "0" * 64
    assert not readiness.verify_analysis_readiness_manifest(bad)

    assert not readiness.verify_analysis_readiness_manifest({})


def test_repair_comparison_verifier_guardrails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    comparison = _demo()["repair_comparison"]

    with pytest.raises(TypeError, match="RepairComparison"):
        readiness.verify_repair_comparison(object())  # type: ignore[arg-type]

    calls = 0

    def first_invalid(_audit) -> bool:
        nonlocal calls
        calls += 1
        return calls != 1

    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        first_invalid,
    )
    assert not readiness.verify_repair_comparison(comparison)

    calls = 0

    def second_invalid(_audit) -> bool:
        nonlocal calls
        calls += 1
        return calls != 2

    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        second_invalid,
    )
    assert not readiness.verify_repair_comparison(comparison)

    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        lambda _audit: True,
    )
    bad_manifest = dict(comparison.manifest)
    bad_manifest["software"] = "bad"
    assert not readiness.verify_repair_comparison(
        replace(comparison, manifest=bad_manifest)
    )

    assert not readiness.verify_repair_comparison(
        replace(comparison, metrics=None)  # type: ignore[arg-type]
    )


def test_readiness_report_verifier_guardrails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _demo()["readiness"]

    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        lambda _audit: False,
    )
    assert not readiness.verify_analysis_readiness_report(report)

    monkeypatch.setattr(
        readiness,
        "verify_study_qc_audit",
        lambda _audit: True,
    )
    bad_manifest = dict(report.manifest)
    bad_manifest["software"] = "bad"
    assert not readiness.verify_analysis_readiness_report(
        replace(report, manifest=bad_manifest)
    )

    assert not readiness.verify_analysis_readiness_report(
        replace(report, trial_summary=None)  # type: ignore[arg-type]
    )


def test_write_artifacts_rejects_invalid_repair(
    tmp_path: Path,
) -> None:
    demo = _demo()
    comparison = demo["repair_comparison"]
    bad = replace(
        comparison,
        manifest={
            **comparison.manifest,
            "comparison_fingerprint": "0" * 64,
        },
    )
    with pytest.raises(ValueError, match="repair_comparison"):
        readiness.write_analysis_readiness_artifacts(
            demo["readiness"],
            tmp_path,
            repair_comparison=bad,
        )


def test_artifact_verifier_requires_manifest_and_schema(
    tmp_path: Path,
) -> None:
    assert not readiness.verify_analysis_readiness_artifacts(tmp_path)

    root, _, _ = _write_artifacts(tmp_path)
    _rewrite_artifact(
        root,
        lambda document: document.__setitem__("schema", "wrong"),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root)


def test_artifact_verifier_checks_outer_fingerprint(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    path = root / "analysis_readiness_artifacts.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["artifact_fingerprint"] = "0" * 64
    path.write_text(json.dumps(document), encoding="utf-8")
    assert not readiness.verify_analysis_readiness_artifacts(root)


def test_artifact_verifier_checks_file_set_and_repair_pairing(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    _rewrite_artifact(
        root,
        lambda document: document["files"].pop("trial_readiness.csv"),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root)

    root2, _, _ = _write_artifacts(tmp_path / "second")
    _rewrite_artifact(
        root2,
        lambda document: document["files"].pop("repair_comparison.csv"),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root2)


def test_artifact_verifier_checks_file_existence_size_and_digest(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    (root / "trial_readiness.csv").unlink()
    assert not readiness.verify_analysis_readiness_artifacts(root)

    root2, _, _ = _write_artifacts(tmp_path / "size")
    _rewrite_artifact(
        root2,
        lambda document: document["files"]["trial_readiness.csv"].__setitem__(
            "bytes",
            document["files"]["trial_readiness.csv"]["bytes"] + 1,
        ),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root2)

    root3, _, _ = _write_artifacts(tmp_path / "digest")
    _rewrite_artifact(
        root3,
        lambda document: document["files"]["trial_readiness.csv"].__setitem__(
            "sha256",
            "0" * 64,
        ),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root3)


def _refresh_descriptor(
    root: Path,
    filename: str,
) -> None:
    payload = (root / filename).read_bytes()

    def mutate(document: dict[str, object]) -> None:
        document["files"][filename] = {
            "bytes": len(payload),
            "sha256": readiness.hashlib.sha256(payload).hexdigest(),
        }

    _rewrite_artifact(root, mutate)


def test_artifact_verifier_checks_embedded_readiness_manifest(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    path = root / "analysis_readiness.json"
    path.write_text("{}", encoding="utf-8")
    _refresh_descriptor(root, "analysis_readiness.json")
    assert not readiness.verify_analysis_readiness_artifacts(root)


def test_artifact_verifier_binds_readiness_fingerprint(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)

    _rewrite_artifact(
        root,
        lambda document: document.__setitem__(
            "readiness_fingerprint",
            "0" * 64,
        ),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root)


def test_artifact_verifier_checks_repair_manifest_and_fingerprint(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    repair_path = root / "repair_comparison.json"
    repair_path.write_text("{}", encoding="utf-8")
    _refresh_descriptor(root, "repair_comparison.json")
    assert not readiness.verify_analysis_readiness_artifacts(root)

    root2, _, _ = _write_artifacts(tmp_path / "fingerprint")
    _rewrite_artifact(
        root2,
        lambda document: document.__setitem__(
            "repair_comparison_fingerprint",
            "0" * 64,
        ),
    )
    assert not readiness.verify_analysis_readiness_artifacts(root2)


def test_artifact_verifier_fails_closed_on_invalid_json(
    tmp_path: Path,
) -> None:
    root, _, _ = _write_artifacts(tmp_path)
    (root / "analysis_readiness_artifacts.json").write_text(
        "{",
        encoding="utf-8",
    )
    assert not readiness.verify_analysis_readiness_artifacts(root)


def test_readiness_internal_guard_and_normalization_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo = _demo()
    report = demo["readiness"]

    with pytest.raises(ValueError, match="invalid readiness status"):
        readiness._build_readiness_manifest(
            policy_name="x",
            thresholds=report.thresholds,
            qc_audit=report.qc_audit,
            trial=report.trial_summary,
            participant=report.participant_summary,
            impact=report.cohort_impact,
            status="bad",
            software={},
        )

    with pytest.raises(TypeError, match="pandas DataFrame"):
        readiness._table_descriptor(object())  # type: ignore[arg-type]

    assert readiness._normalize(np.int64(2)) == 2
    assert readiness._normalize(float("nan")) is None
    assert readiness._normalize(float("inf")) == {
        "__gazeaudit_nonfinite__": "positive_infinity"
    }
    assert readiness._normalize(float("-inf")) == {
        "__gazeaudit_nonfinite__": "negative_infinity"
    }
    stamp = pd.Timestamp("2026-01-02")
    assert readiness._normalize(stamp) == stamp.isoformat()
    assert readiness._normalize({"x": np.array([1, 2])}) == {"x": [1, 2]}
    assert readiness._normalize((np.int64(1), 2)) == [1, 2]
    assert readiness._normalize(pd.NA) is None

    class Unsupported:
        pass

    original_isna = readiness.pd.isna
    monkeypatch.setattr(
        readiness.pd,
        "isna",
        lambda value: (
            False
            if isinstance(value, Unsupported)
            else original_isna(value)
        ),
    )
    with pytest.raises(TypeError, match="unsupported analysis-readiness"):
        readiness._normalize(Unsupported())


def test_participant_unit_labels_and_public_type_guards() -> None:
    demo = _demo()
    labels = readiness._participant_unit_labels(demo["study"])
    assert len(labels) == len(demo["study"].data)
    assert labels[0] == "P000001"
    assert labels[-1] == "P000003"

    with pytest.raises(TypeError, match="study must be"):
        readiness._require_study(object())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="AnalysisReadinessReport"):
        readiness._require_readiness_report(object())  # type: ignore[arg-type]

    tampered = replace(
        demo["readiness"],
        manifest={
            **demo["readiness"].manifest,
            "readiness_fingerprint": "0" * 64,
        },
    )
    with pytest.raises(ValueError, match="does not match its manifest"):
        readiness._require_readiness_report(tampered)

    with pytest.raises(ValueError, match="non-empty string"):
        readiness._nonempty_text(" ", "name")
