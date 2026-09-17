from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guides" / "what-next.md"
EXAMPLE = ROOT / "docs" / "examples" / "project-lifecycle-walkthrough.md"
DOCS_INDEX = ROOT / "docs" / "index.md"
NAVIGATION = ROOT / "assets" / "js" / "navigation.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_next_step_guide_covers_the_five_project_stages() -> None:
    text = _read(GUIDE)
    for stage in (
        "Stage 1 — plan before analysis",
        "Stage 2 — audit the canonical data",
        "Stage 3 — interpret before writing",
        "Stage 4 — revise after peer review",
        "Stage 5 — resubmission and durable handoff",
    ):
        assert stage in text

    assert "Stop rather than guess" in text
    assert "Fast decision map" in text
    assert "same project-stage logic in a stable, searchable, linkable document" in text


def test_next_step_guide_routes_to_existing_governed_workflows() -> None:
    text = _read(GUIDE)
    for label, destination in (
        ("Audit planner", "/docs/planner/"),
        ("First real audit", "/docs/guides/first-real-audit/"),
        ("Interpret an audit result", "/docs/guides/interpret-audit-result/"),
        ("Revision toolkit", "/docs/workspace/revision-toolkit/"),
        ("Resubmission readiness", "/docs/guides/resubmission-readiness/"),
        ("Reproducible publication", "/docs/workflows/reproducible-publication/"),
    ):
        assert f"[{label}]" in text
        assert destination in text


def test_next_step_guide_preserves_scientific_judgement_boundary() -> None:
    text = _read(GUIDE)
    assert "It is a navigation guide, not a scientific decision engine." in text
    assert "it does not decide scientific validity" in text
    assert "Do not inherit the frozen outcome label" in text


def test_lifecycle_walkthrough_preserves_temporal_denominators() -> None:
    text = _read(EXAMPLE)
    assert "fully synthetic teaching project" in text
    assert "E1 submitted: 8 successful / 8 valid" in text
    assert "E1 submitted: 8 / 8" in text
    assert "E1 post-review sensitivity amendment: 3 successful / 4 valid" in text
    assert "E2 post-review endpoint amendment: separate endpoint record" in text
    assert "11 / 11 analyses" in text
    assert "3 / 3 post-review analyses" in text


def test_lifecycle_walkthrough_uses_real_revision_package_cli() -> None:
    text = _read(EXAMPLE)
    assert "gazeaudit-revision-package init --root revision-package" in text
    assert "gazeaudit-revision-package validate --root revision-package" in text
    assert "structural provenance only" in text


def test_documentation_hub_exposes_static_onboarding_routes() -> None:
    text = _read(DOCS_INDEX)
    assert "[What should I do next?](guides/what-next/)" in text
    assert "[Project lifecycle walkthrough](examples/project-lifecycle-walkthrough/)" in text
    assert "ordinary semantic documentation that remains useful without JavaScript" in text


def test_navigation_enhancement_surfaces_next_step_routes_without_replacing_fallback() -> None:
    text = _read(NAVIGATION)
    assert "const whatNextUrl" in text
    assert "const lifecycleUrl" in text
    assert "data.nextStepNav" not in text
    assert "link.dataset.nextStepNav" in text
    assert "What should I do next?" in text
    assert "Project lifecycle walkthrough" in text
    assert "Not sure which stage fits? Use the static decision map" in text


def test_new_onboarding_material_preserves_frozen_outcomes() -> None:
    for text in (_read(GUIDE), _read(EXAMPLE)):
        assert "GazeBase `incomplete`" in text
        assert "Korthals `robust_negative`" in text
        assert "Pedrotti/de Chambrier `materially_fragile`" in text
