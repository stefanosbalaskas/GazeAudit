from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_workspace_exposes_four_task_first_launch_routes() -> None:
    page = _text("docs/workspace/index.md")
    assert 'class="workspace-launchpad"' in page
    assert page.count('class="workspace-launch-card"') == 4
    for route in (
        "/docs/guides/first-real-audit/",
        "/docs/planner/",
        "/docs/methods/",
        "/docs/workflows/reproducible-publication/",
    ):
        assert route in page
    for label in (
        "Start with my gaze CSV",
        "Plan an audit",
        "Answer one methodological question",
        "Prepare the publication record",
    ):
        assert label in page


def test_workspace_has_explicit_four_stage_first_audit_path() -> None:
    page = _text("docs/workspace/index.md")
    assert 'class="audit-path-strip"' in page
    assert page.count('class="audit-path-step"') == 4
    for marker in (
        "GazeStudy(frame)",
        "build_study_qc_audit()",
        "run_specs()",
        "analysis-output/",
    ):
        assert marker in page


def test_workspace_previews_complete_audit_bundle_not_preferred_result() -> None:
    page = _text("docs/workspace/index.md")
    assert 'class="audit-output-preview"' in page
    assert "The audit is a bundle, not one preferred result." in page
    for output in (
        "analysis-output/study-qc/",
        "analysis-output/specifications.csv",
        "analysis-output/specification-curve.csv",
        "analysis-output/effect-stability.csv",
        "analysis-output/marginal-sensitivity.csv",
        "analysis-output/pairwise-sensitivity.csv",
    ):
        assert output in page


def test_workspace_preserves_researcher_owned_scientific_boundaries() -> None:
    page = _text("docs/workspace/index.md")
    for statement in (
        "Navigation is not judgement.",
        "remain researcher-owned scientific decisions",
        "Empirical robustness summaries are not presented as confidence intervals.",
        "Do not transfer a case-study label to a new dataset",
    ):
        assert statement in page
    for outcome in ("incomplete", "robust_negative", "materially_fragile"):
        assert outcome in page


def test_practical_workspace_styles_are_loaded_and_responsive() -> None:
    gallery_css = _text("assets/css/gallery.css")
    css = _text("assets/css/practical-workspace.css")
    assert '@import url("./practical-workspace.css");' in gallery_css
    for selector in (
        ".workspace-launchpad",
        ".workspace-launch-card",
        ".audit-path-strip",
        ".audit-output-preview",
        ".audit-file-tree",
        ".audit-checklist",
        ".workspace-boundary-bar",
    ):
        assert selector in css
    assert "@media (max-width: 720px)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
