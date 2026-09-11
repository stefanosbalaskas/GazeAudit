import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GazeStudy,
    canonical_json,
    fingerprint,
    inject_missingness,
    missingness_mask,
    missingness_sensitivity_curve,
    results_manifest,
    software_environment,
    specification_manifest,
    summarize_missingness,
)


def _study(n=20, *, index_offset=0):
    data = pd.DataFrame(
        {
            "participant": ["p1"] * (n // 2) + ["p2"] * (n - n // 2),
            "trial": [1] * n,
            "timestamp": np.arange(n, dtype=float),
            "x": np.arange(n, dtype=float),
            "y": np.arange(n, dtype=float) * 0.5,
        },
        index=np.arange(index_offset, index_offset + n),
    )
    return GazeStudy(data)


def test_missingness_mask_and_summary_detect_coordinate_loss():
    study = _study(10)
    data = study.data.copy()
    data.loc[data.index[2], "x"] = np.nan
    data.loc[data.index[5], "y"] = np.nan
    changed = study.copy_with(data)
    mask = missingness_mask(changed)
    assert mask.sum() == 2
    summary = summarize_missingness(changed)
    assert summary["n_missing"] == 2
    assert summary["n_complete"] == 8
    assert summary["missing_fraction"] == pytest.approx(0.2)


def test_mcar_injection_is_reproducible_and_preserves_original():
    study = _study(20, index_offset=100)
    first = inject_missingness(study, 0.25, mechanism="mcar", rng=123, reason="benchmark")
    second = inject_missingness(study, 0.25, mechanism="mcar", rng=123, reason="benchmark")
    pd.testing.assert_frame_equal(first.data, second.data)
    assert summarize_missingness(first)["n_missing"] == 5
    assert (first.data.loc[first.data["x"].isna(), "missing_reason"] == "benchmark").all()
    assert not study.data[["x", "y"]].isna().any().any()
    assert list(first.data.index) == list(range(20))


def test_block_injection_masks_requested_number_and_stays_reproducible():
    study = _study(20)
    first = inject_missingness(study, 0.30, mechanism="block", rng=77)
    second = inject_missingness(study, 0.30, mechanism="block", rng=77)
    pd.testing.assert_frame_equal(first.data, second.data)
    assert summarize_missingness(first)["n_missing"] == 6


def test_injection_respects_preexisting_missingness_and_zero_fraction():
    study = _study(10)
    data = study.data.copy()
    data.loc[0, ["x", "y"]] = np.nan
    study = study.copy_with(data)
    assert summarize_missingness(inject_missingness(study, 0.0, rng=1))["n_missing"] == 1
    assert summarize_missingness(inject_missingness(study, 0.5, rng=1))["n_missing"] == 5


def test_missingness_sensitivity_curve_reports_realized_loss_and_endpoint():
    study = _study(20)

    def endpoint(current):
        return float(current.data["x"].mean(skipna=True))

    first = missingness_sensitivity_curve(study, [0.0, 0.25, 0.5], endpoint, rng=11)
    second = missingness_sensitivity_curve(study, [0.0, 0.25, 0.5], endpoint, rng=11)
    pd.testing.assert_frame_equal(first, second)
    assert list(first["n_missing"]) == [0, 5, 10]
    assert np.isfinite(first["estimate"]).all()


def test_missingness_validation_guardrails():
    study = _study(10)
    with pytest.raises(ValueError, match="between 0 and 1"):
        inject_missingness(study, -0.1)
    with pytest.raises(ValueError, match="mechanism"):
        inject_missingness(study, 0.2, mechanism="informative")
    with pytest.raises(ValueError, match="at least one value"):
        missingness_sensitivity_curve(study, [], lambda _s: 1.0)
    with pytest.raises(ValueError, match="finite scalar"):
        missingness_sensitivity_curve(study, [0.1], lambda _s: np.inf)


def test_canonical_json_and_fingerprint_ignore_mapping_insertion_order():
    first = {"detector": "ivt", "qc": 0.2, "nested": {"a": 1, "b": [2, 3]}}
    second = {"nested": {"b": [2, 3], "a": 1}, "qc": 0.2, "detector": "ivt"}
    assert canonical_json(first) == canonical_json(second)
    assert fingerprint(first) == fingerprint(second)
    assert len(fingerprint(first)) == 64


def test_specification_manifest_is_stable_and_sensitive_to_decisions():
    spec = {"detector": "ivt", "qc": np.float64(0.2)}
    first = specification_manifest(spec, endpoint="dwell", metadata={"study": "demo"})
    second = specification_manifest(spec, endpoint="dwell", metadata={"study": "demo"})
    changed = specification_manifest({"detector": "idt", "qc": 0.2}, endpoint="dwell")
    assert first == second
    assert first["specification_fingerprint"] != changed["specification_fingerprint"]


def test_results_manifest_is_deterministic_and_sensitive_to_results():
    results = pd.DataFrame(
        {
            "spec_id": [0, 1],
            "detector": ["ivt", "idt"],
            "estimate": [1.2, 1.3],
        }
    )
    first = results_manifest(results, metadata={"endpoint": "dwell"})
    second = results_manifest(results, metadata={"endpoint": "dwell"})
    assert first == second
    assert first["n_rows"] == 2
    assert first["software"]["gazeaudit"].startswith("0.1.0.dev")
    changed = results.copy()
    changed.loc[1, "estimate"] = 2.0
    assert first["records_fingerprint"] != results_manifest(changed)["records_fingerprint"]


def test_provenance_validation_and_environment():
    with pytest.raises(ValueError, match="finite"):
        canonical_json({"bad": np.nan})
    with pytest.raises(TypeError, match="unsupported"):
        canonical_json({"bad": {1, 2}})
    with pytest.raises(ValueError, match="unsupported hash"):
        fingerprint({"x": 1}, algorithm="not-a-hash")
    with pytest.raises(ValueError, match="not present"):
        results_manifest(pd.DataFrame({"x": [1]}))
    with pytest.raises(ValueError, match="at least one row"):
        results_manifest(pd.DataFrame({"estimate": []}))
    required = {"gazeaudit", "python", "numpy", "pandas", "platform"}
    assert required.issubset(software_environment())
