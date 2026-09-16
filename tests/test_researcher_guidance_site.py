from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_researcher_checklist_has_before_during_after_governance() -> None:
    page = _text("docs/guides/researcher-audit-checklist.md")

    for contract in (
        "permalink: /docs/guides/researcher-audit-checklist/",
        "Before execution",
        "During execution",
        "Before interpretation",
        "Before publication",
        "The canonical source table or immutable source reference is identified.",
        "The scientific endpoint is defined",
        "Technical failures remain identifiable",
        "Descriptive robustness outputs are not described as confidence intervals",
        "What was fixed? What varied? What failed? What claim followed?",
    ):
        assert contract in page

    assert "This checklist records decisions; it does not make them." in page
    assert "Do not repair the specification space by outcome." in page


def test_decision_log_template_preserves_timing_and_boundaries() -> None:
    page = _text("docs/guides/audit-decision-log-template.md")

    for heading in (
        "## Study identity",
        "## Scientific endpoint",
        "## Structural-QC policy",
        "## Exclusions",
        "## Declared specification space",
        "## Perturbation / sensitivity plan",
        "## Technical failure policy",
        "## Interpretation rule",
        "## Deviations and amendments",
        "## Reporting boundary",
        "## Publication/archive handoff",
    ):
        assert heading in page

    assert "A decision log is not a preregistration by itself." in page
    assert "Results already inspected?" in page
    assert "Supported by this audit" in page
    assert "Not established by this audit" in page


def test_decision_to_report_example_is_synthetic_and_complete() -> None:
    page = _text("docs/examples/decision-to-report.md")

    for contract in (
        "examples/end_to_end_robustness.py",
        "All values on this page are synthetic.",
        "12 specifications",
        "**4 positive** estimates",
        "**4 negative** estimates",
        "**4 zero** estimates",
        "-0.0404 to +0.0210",
        "median of **0.0000**",
        "No single row represents the robustness result.",
        "descriptive property of this synthetic specification table",
        "It does not establish that AOI radius is a causal mechanism",
    ):
        assert contract in page

    assert "The treatment effect was robust across analytical choices." in page
    assert "AOI radius caused the instability in the treatment effect." in page
    assert "These numbers are demonstration choices" in page


def test_guides_and_examples_hubs_surface_new_learning_path() -> None:
    guides = _text("docs/guides/index.md")
    examples = _text("docs/examples/index.md")

    for route in (
        "researcher-audit-checklist/",
        "audit-decision-log-template/",
        "../examples/decision-to-report/",
    ):
        assert route in guides

    for route in (
        "decision-to-report/",
        "../guides/researcher-audit-checklist/",
        "../guides/audit-decision-log-template/",
    ):
        assert route in examples

    assert guides.count('class="card"') >= 4
    assert examples.count('class="card"') >= 4
    assert "Choose by task" in guides
    assert "Choose by task" in examples


def test_workspace_hands_researchers_into_decision_governance_and_reporting() -> None:
    workspace = _text("docs/workspace/index.md")

    for route in (
        "/docs/guides/researcher-audit-checklist/",
        "/docs/guides/audit-decision-log-template/",
        "/docs/examples/decision-to-report/",
        "/docs/guides/reporting-robustness/",
    ):
        assert route in workspace

    for contract in (
        "Before execution, preserve the decisions that GazeAudit cannot make for you.",
        "Declare researcher-owned decisions",
        "Interpret a robustness pattern",
        "Record later amendments instead of rewriting the original declaration",
        "I need to practise bounded reporting",
    ):
        assert contract in workspace
