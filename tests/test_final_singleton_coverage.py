from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_execution as ke
import gazeaudit.korthals_execution_v2 as kev2
import gazeaudit.korthals_freeze as kfreeze
import gazeaudit.korthals_freeze_v2 as kfreeze2
import gazeaudit.korthals_osf as kosf
import gazeaudit.korthals_source as ks
import gazeaudit.korthals_v2 as kv2
import gazeaudit.pedrotti_execution as pe
import gazeaudit.pedrotti_freeze as pfreeze
import gazeaudit.pedrotti_source as ps

ROOT = Path(__file__).resolve().parents[1]

KEXEC = runpy.run_path(
    str(ROOT / "tests" / "test_bulk_korthals_execution_coverage.py")
)
KEV2 = runpy.run_path(
    str(ROOT / "tests" / "test_korthals_execution_v2.py")
)
FREEZE = runpy.run_path(
    str(ROOT / "tests" / "test_bulk_freeze_network_coverage.py")
)
KV2_FINAL = runpy.run_path(
    str(ROOT / "tests" / "test_final_korthals_v2_closure.py")
)
KS_FINAL = runpy.run_path(
    str(ROOT / "tests" / "test_final_source_last_lines.py")
)
SOURCE_FINAL = runpy.run_path(
    str(ROOT / "tests" / "test_final_source_closure.py")
)

_k_prepared = KEXEC["_prepared"]
_k_execution = KEXEC["_execution"]
_k_aligned = KEXEC["_aligned_fixture"]
_k_validation = KEXEC["_validation_fixture"]

_kv2_prepared = KEV2["_synthetic_prepared"]
_kv2_context = KEV2["_execution_context"]
_kv2_environment = KEV2["_environment_text"]

_write_fake_korthals_freeze = FREEZE["_write_fake_korthals_freeze"]
_write_fake_korthals_freeze_v2 = FREEZE["_write_fake_korthals_freeze_v2"]
_write_fake_pedrotti_freeze = FREEZE["_write_fake_pedrotti_freeze"]

_valid_kv2_intake = KV2_FINAL["_valid_intake"]
_valid_k_intake = KS_FINAL["_valid_k_intake"]
_valid_summary_and_source = SOURCE_FINAL["_valid_summary_and_source"]


def test_korthals_downsample_negative_grid_hits_empty_and_right_boundary() -> None:
    trial = pd.DataFrame(
        {
            "trial_time": [-0.03, -0.02],
            "x": [1, 2],
        }
    )
    sampled = ke._downsample_trial_50hz(trial)
    assert sampled["x"].tolist() == [2]
    assert sampled["scheduled_trial_time"].tolist() == [0.0]


def test_korthals_endpoint_rejects_metadata_trial_without_samples(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _k_prepared()
    frame = prepared.data.copy()
    metadata = ke._trial_metadata(frame)
    jumping = metadata["target_type"] == "jumping_circle"
    metadata.loc[jumping, "trial_number"] = 999999

    monkeypatch.setattr(
        ke,
        "_trial_metadata",
        lambda _frame: metadata.copy(),
    )

    with pytest.raises(ValueError, match="must contain retained samples"):
        ke._endpoint_weights(frame)


def test_korthals_v2_writer_overwrite_and_verifier_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _kv2_prepared()
    execution = kev2.run_korthals_aoi_execution_v2(prepared)
    output = tmp_path / "archive"
    output.mkdir()
    old = output / "old.txt"
    old.write_text("old", encoding="utf-8")

    kev2.write_korthals_execution_artifacts_v2(
        execution,
        output,
        execution_context=_kv2_context(prepared),
        environment_text=_kv2_environment(),
        overwrite=True,
    )
    assert not old.exists()

    monkeypatch.setattr(
        kev2,
        "_parse_checksums",
        lambda _path: (_ for _ in ()).throw(ValueError("forced")),
    )
    assert not kev2.verify_korthals_execution_artifacts_v2(output)


def test_korthals_v2_context_rejects_source_lock_fingerprint_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _kv2_prepared()
    context = _kv2_context(prepared)
    lock = kev2.verify_korthals_source_lock()
    bad_lock = copy.deepcopy(lock)
    bad_lock["source"]["source_manifest_fingerprint"] = "0" * 64

    monkeypatch.setattr(
        kev2,
        "verify_korthals_source_lock",
        lambda: bad_lock,
    )

    with pytest.raises(ValueError, match="differs from source lock"):
        kev2._validated_execution_context_v2(
            context,
            prepared,
        )


@pytest.mark.parametrize(
    ("builder", "module", "verifier", "intake_verifier"),
    [
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "verify_korthals_source_intake_artifacts_v2",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "verify_pedrotti_source_intake_artifacts",
        ),
    ],
)
def test_freeze_verifier_hits_invalid_intake_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder,
    module,
    verifier,
    intake_verifier: str,
) -> None:
    root = builder(tmp_path, monkeypatch)
    monkeypatch.setattr(
        module,
        intake_verifier,
        lambda _path: False,
    )
    assert verifier(root) is False


@pytest.mark.parametrize(
    ("builder", "module", "verifier"),
    [
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
        ),
    ],
)
def test_freeze_verifier_hits_forbidden_scientific_token_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder,
    module,
    verifier,
) -> None:
    root = builder(tmp_path, monkeypatch)
    token = (
        '"classification"'
        if module is pfreeze
        else '"hard_effect"'
    )
    monkeypatch.setattr(
        module,
        "canonical_json",
        lambda _value: token,
    )
    assert verifier(root) is False


def test_pedrotti_freeze_rejects_extra_manifest_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _write_fake_pedrotti_freeze(tmp_path, monkeypatch)
    path = root / "freeze_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["unexpected"] = True
    pfreeze._write_json(path, manifest)
    assert not pfreeze.verify_pedrotti_source_freeze_artifacts(root)


def test_korthals_source_intake_rejects_unexpected_top_level_file(
    tmp_path: Path,
) -> None:
    _intake, root = _valid_k_intake(tmp_path)
    (root / "unexpected.txt").write_text("x", encoding="utf-8")
    assert not ks.verify_korthals_source_intake_artifacts(root)


def test_korthals_source_intake_rejects_invalid_source_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _intake, root = _valid_k_intake(tmp_path)
    monkeypatch.setattr(
        ks,
        "verify_korthals_source_manifest",
        lambda _document: False,
    )
    assert not ks.verify_korthals_source_intake_artifacts(root)


def test_korthals_v2_protocol_frozen_guardrail_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = kv2.load_korthals_protocol_v2()
    bad = copy.deepcopy(protocol)
    bad["case_study_id"] = "wrong"

    monkeypatch.setattr(
        kv2,
        "verify_aoi_uncertainty_protocol",
        lambda _document: True,
    )

    with pytest.raises(ValueError, match="failed frozen guardrails"):
        kv2.verify_korthals_protocol_v2(bad)


def test_korthals_v2_zero_trial_ambiguous_metadata_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins

    aligned = _k_aligned(participants=("p1",))
    validations = _k_validation(participants=("p1",))
    original_zip = builtins.zip
    calls = 0

    def injected_zip(*args, **kwargs):
        nonlocal calls
        calls += 1
        values = list(original_zip(*args, **kwargs))
        if calls == 1:
            values.append(("ghost-participant", 999))
        return iter(values)

    monkeypatch.setattr(
        kv2,
        "zip",
        injected_zip,
        raising=False,
    )

    with pytest.raises(ValueError, match="ambiguous metadata"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
        )


def test_korthals_v2_zero_finite_incomplete_cell_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aligned = _k_aligned(participants=("p1",))
    validations = _k_validation(participants=("p1",))
    protocol = kv2.load_korthals_protocol_v2()
    custom = copy.deepcopy(protocol)
    custom["dataset"]["author_directed_exclusion"] = {
        "participant_id": "p1",
        "trial_number_start": 2,
        "trial_number_end": 2,
    }

    monkeypatch.setattr(
        kv2,
        "verify_korthals_protocol_v2",
        lambda _document=None: custom,
    )

    original = kv2._downsample_trial_50hz

    def zero_first(trial: pd.DataFrame) -> pd.DataFrame:
        result = original(trial)
        if int(trial["trial_number"].iloc[0]) == 1:
            result[["gaze_x", "gaze_y"]] = np.nan
        return result

    monkeypatch.setattr(
        kv2,
        "_downsample_trial_50hz",
        zero_first,
    )

    with pytest.raises(ValueError, match="complete frozen matched cell"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
        )


def test_korthals_v2_companion_participant_count_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root = KV2_FINAL["_source_tree"](tmp_path)
    KV2_FINAL["_configure_fakes"]()

    baseline = kv2.prepare_korthals_from_companion_v2(
        source_root,
        participant_factory=KV2_FINAL["_FakeParticipant"],
        preprocessor_factory=KV2_FINAL["_FakePreprocessor"],
    )
    bad_identity = dict(baseline.prepared.source_identity)
    bad_identity["participant_count"] = 999
    bad_prepared = type(baseline.prepared)(
        data=baseline.prepared.data,
        validation_groups=baseline.prepared.validation_groups,
        source_identity=bad_identity,
    )

    monkeypatch.setattr(
        kv2,
        "prepare_korthals_aligned_data_v2",
        lambda *args, **kwargs: bad_prepared,
    )

    with pytest.raises(ValueError, match="participant count differs"):
        kv2.prepare_korthals_from_companion_v2(
            source_root,
            participant_factory=KV2_FINAL["_FakeParticipant"],
            preprocessor_factory=KV2_FINAL["_FakePreprocessor"],
        )


def test_korthals_v2_intake_overwrite_unlinks_existing_file(
    tmp_path: Path,
) -> None:
    intake = _valid_kv2_intake(tmp_path / "source")
    output = tmp_path / "out"
    output.mkdir()
    old = output / "old.txt"
    old.write_text("old", encoding="utf-8")

    kv2.write_korthals_source_intake_artifacts_v2(
        intake,
        output,
        overwrite=True,
    )
    assert not old.exists()


def test_korthals_v2_intake_verifier_remaining_integrity_branches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    intake = _valid_kv2_intake(tmp_path / "source")
    output = tmp_path / "out"
    kv2.write_korthals_source_intake_artifacts_v2(
        intake,
        output,
    )

    monkeypatch.setattr(
        kv2,
        "verify_korthals_source_manifest_v2",
        lambda _document: False,
    )
    assert not kv2.verify_korthals_source_intake_artifacts_v2(output)
    monkeypatch.undo()

    def clone(name: str) -> Path:
        import shutil

        target = tmp_path / name
        shutil.copytree(output, target)
        return target

    root = clone("bad-fingerprint")
    path = root / "artifact_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["artifact_manifest_fingerprint"] = "0" * 64
    kv2._write_json(path, manifest)
    assert not kv2.verify_korthals_source_intake_artifacts_v2(root)

    root = clone("bad-manifest-source")
    path = root / "artifact_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["source_manifest_fingerprint"] = "0" * 64
    core = dict(manifest)
    core.pop("artifact_manifest_fingerprint", None)
    manifest["artifact_manifest_fingerprint"] = kv2.fingerprint(core)
    kv2._write_json(path, manifest)
    assert not kv2.verify_korthals_source_intake_artifacts_v2(root)

    root = clone("bad-summary-source")
    summary_path = root / "intake_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["source_manifest_fingerprint"] = "0" * 64
    kv2._write_json(summary_path, summary)

    artifact_path = root / "artifact_manifest.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["files"] = [
        kv2._file_record(root / "intake_summary.json", root),
        kv2._file_record(root / "source_manifest.json", root),
    ]
    core = dict(artifact)
    core.pop("artifact_manifest_fingerprint", None)
    artifact["artifact_manifest_fingerprint"] = kv2.fingerprint(core)
    kv2._write_json(artifact_path, artifact)
    assert not kv2.verify_korthals_source_intake_artifacts_v2(root)

    root = clone("bad-declared")
    path = root / "artifact_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["files"] = []
    core = dict(manifest)
    core.pop("artifact_manifest_fingerprint", None)
    manifest["artifact_manifest_fingerprint"] = kv2.fingerprint(core)
    kv2._write_json(path, manifest)
    assert not kv2.verify_korthals_source_intake_artifacts_v2(root)

    root = clone("bad-checksum-set")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert not kv2.verify_korthals_source_intake_artifacts_v2(root)


def test_pedrotti_summary_trial_total_reconciliation_guard() -> None:
    class DefensiveTrialCount:
        def __ne__(self, other: object) -> bool:
            return other != 96

        def __radd__(self, other: int) -> int:
            return other + 95

    summary, source = _valid_summary_and_source()
    summary["participants"][0]["trial_count"] = DefensiveTrialCount()

    with pytest.raises(ValueError, match="trial totals do not reconcile"):
        ps._validate_intake_summary(summary, source)


def test_korthals_osf_explicit_unreachable_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    item = kosf.KorthalsRemoteFile(
        remote_path="/raw/a.bin",
        destination=str(tmp_path / "a.bin"),
        md5="0" * 32,
        sha256=None,
    )

    monkeypatch.setattr(
        kosf,
        "_scrub_unverified_local_files",
        lambda _items: (0, 0),
    )
    monkeypatch.setattr(
        kosf,
        "range",
        lambda *_args: [],
        raising=False,
    )

    with pytest.raises(AssertionError, match="unreachable"):
        kosf.fetch_korthals_osf_resumable(
            max_attempts=1,
            initial_backoff_seconds=0,
            inventory_fn=lambda: (item,),
            download_fn=lambda: None,
            sleep_fn=lambda _seconds: None,
        )


def test_pedrotti_verifier_fails_closed_on_caught_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "archive"
    root.mkdir()
    for name in (
        "SHA256SUMS",
        "artifact_manifest.json",
        "execution_context.json",
        "execution_manifest.json",
        "family_recovery.json",
        "missingness_results.json",
        "pip_freeze.txt",
        "reference.json",
        "sampling_results.json",
        "source_identity.json",
    ):
        (root / name).write_text("", encoding="utf-8")

    monkeypatch.setattr(
        pe,
        "_parse_checksums",
        lambda _path: (_ for _ in ()).throw(ValueError("forced")),
    )
    assert not pe.verify_pedrotti_locked_execution_artifacts(root)


def test_pedrotti_verified_protocol_fail_closed_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packaged = pe.load_pedrotti_protocol()

    monkeypatch.setattr(
        pe,
        "canonical_json",
        lambda _value: "[]",
    )
    with pytest.raises(TypeError, match="normalize to an object"):
        pe._verified_protocol({"x": 1})

    monkeypatch.undo()
    packaged = pe.load_pedrotti_protocol()

    bad_fingerprint = copy.deepcopy(packaged)
    bad_fingerprint["protocol_fingerprint"] = "wrong"
    with pytest.raises(ValueError, match="fingerprint differs"):
        pe._verified_protocol(bad_fingerprint)

    changed = copy.deepcopy(packaged)
    changed["coverage_probe"] = True
    with pytest.raises(ValueError, match="content differs"):
        pe._verified_protocol(changed)


def test_pedrotti_tiny_negative_path_numerator_normalizes_to_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial = pe.make_pedrotti_trial(
        "01",
        1,
        "short",
        [0.0, 1.0, 2.0, 3.0],
        [0.0, 1.0, 2.0, 3.0],
        [0.0, 0.0, 0.0, 0.0],
    )
    object.__setattr__(
        trial,
        "edge_distance",
        np.array([1.0, 0.0, -5.0e-11]),
    )
    monkeypatch.setattr(
        pe,
        "_added_missingness_positions",
        lambda *args, **kwargs: np.array([1], dtype=int),
    )

    observed = pe._trial_rate_missingness(
        trial,
        mechanism="mcar_within_trial",
        fraction=0.25,
        replicate=1,
        root_seed=1,
    )
    assert observed == 0.0


def test_pedrotti_added_missingness_defensive_oversize_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial = pe.make_pedrotti_trial(
        "01",
        1,
        "short",
        [0.0, 1.0, 2.0],
        [0.0, 1.0, 2.0],
        [0.0, 0.0, 0.0],
    )
    monkeypatch.setattr(
        pe,
        "round",
        lambda _value: trial.finite_positions.size + 1,
        raising=False,
    )

    with pytest.raises(ValueError, match="exceeds finite trial rows"):
        pe._added_missingness_positions(
            trial,
            mechanism="mcar_within_trial",
            fraction=0.5,
            replicate=1,
            root_seed=1,
        )


def _pedrotti_prepared_for_aggregation(
    participant_count: int,
) -> pe.PreparedPedrottiData:
    participant_ids = tuple(
        f"{index:02d}"
        for index in range(1, participant_count + 1)
    )
    trials = []
    for participant_id in participant_ids:
        trials.extend(
            [
                pe.make_pedrotti_trial(
                    participant_id,
                    1,
                    "short",
                    [0.0, 1.0],
                    [0.0, 1.0],
                    [0.0, 0.0],
                ),
                pe.make_pedrotti_trial(
                    participant_id,
                    2,
                    "long",
                    [0.0, 1.0],
                    [0.0, 1.0],
                    [0.0, 0.0],
                ),
            ]
        )
    return pe.PreparedPedrottiData(
        source_identity={},
        trials=tuple(trials),
        participant_ids=participant_ids,
    )


def test_pedrotti_participant_contrast_nonfinite_guard() -> None:
    prepared = _pedrotti_prepared_for_aggregation(1)

    def estimator(trial: pe.PedrottiTrial) -> float:
        return 1.0e308 if trial.condition == "long" else -1.0e308

    with np.errstate(over="ignore", invalid="ignore"):
        with pytest.raises(ValueError, match="participant contrast is non-finite"):
            pe._study_estimate(prepared, estimator)


def test_pedrotti_study_endpoint_nonfinite_guard() -> None:
    prepared = _pedrotti_prepared_for_aggregation(2)

    def estimator(trial: pe.PedrottiTrial) -> float:
        return 1.0e308 if trial.condition == "long" else 0.0

    with np.errstate(over="ignore", invalid="ignore"):
        with pytest.raises(ValueError, match="study endpoint is non-finite"):
            pe._study_estimate(prepared, estimator)
