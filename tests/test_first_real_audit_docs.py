from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_first_real_audit_pages_and_script_exist() -> None:
    required = (
        "examples/first_real_audit.py",
        "docs/guides/first-real-audit.md",
        "docs/examples/first-real-audit.md",
        "docs/workflows/first-study-audit.md",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing


def test_first_real_audit_demo_executes_governed_public_path() -> None:
    namespace = runpy.run_path(str(ROOT / "examples/first_real_audit.py"))
    study = namespace["build_demo_study"]()
    audit = namespace["run_audit"](study)

    assert audit["space"].size == 12
    assert len(audit["results"]) == 12
    assert len(audit["curve"]) == 12
    assert int(audit["stability"]["n_specifications"]) == 12
    assert set(audit["marginal"]["factor"]) == {
        "min_quality",
        "sample_stride",
        "aoi_radius",
    }
    assert len(audit["pairwise"]) == 3
    assert audit["qc"].study_fingerprint
    assert audit["qc"].audit_fingerprint


def test_first_real_audit_documentation_keeps_scientific_judgement_researcher_owned() -> None:
    guide = _text("docs/guides/first-real-audit.md")
    example = _text("docs/examples/first-real-audit.md")
    workflow = _text("docs/workflows/first-study-audit.md")

    for route in (
        "/docs/guides/first-real-audit/",
        "/docs/examples/first-real-audit/",
        "/docs/workflows/first-study-audit/",
    ):
        assert route in guide + example + workflow

    for contract in (
        "not recommended universal cutoffs",
        "Structural QC is not scientific validity",
        "Do not expand the space after seeing",
        "Empirical specification quantiles are **not confidence intervals**",
    ):
        assert contract in guide

    assert "Supplying your own CSV does not turn the example into validation evidence" in example
    assert "The workflow governs traceability, not scientific judgement" in workflow


def test_first_real_audit_is_reachable_from_primary_docs_hubs() -> None:
    docs_hub = _text("docs/index.md")
    workspace = _text("docs/workspace/index.md")
    guides = _text("docs/guides/index.md")
    examples = _text("docs/examples/index.md")
    workflows = _text("docs/workflows/index.md")

    assert "guides/first-real-audit/" in docs_hub
    assert "/docs/guides/first-real-audit/" in workspace
    assert "first-real-audit/" in guides
    assert "first-real-audit/" in examples
    assert "first-study-audit/" in workflows


def test_first_real_audit_is_reachable_from_persistent_navigation() -> None:
    layout = _text("_layouts/default.html")
    assert layout.count("'/docs/guides/first-real-audit/' | relative_url") >= 3
    assert "First real audit example" in layout
    assert "'/docs/examples/first-real-audit/' | relative_url" in layout
    assert "First-study audit" in layout
    assert "'/docs/workflows/first-study-audit/' | relative_url" in layout
    assert "Use your own data" in layout
