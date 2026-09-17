from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TROUBLESHOOTING = ROOT / "docs" / "guides" / "troubleshooting.md"
RECOVERY = ROOT / "docs" / "examples" / "failed-audit-recovery.md"
DOCS_INDEX = ROOT / "docs" / "index.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
COMMON_MISTAKES = ROOT / "docs" / "guides" / "common-audit-mistakes.md"
MULTIVERSE = ROOT / "src" / "gazeaudit" / "multiverse.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_troubleshooting_center_is_symptom_first_and_searchable() -> None:
    text = _read(TROUBLESHOOTING)
    assert "permalink: /docs/guides/troubleshooting/" in text
    assert "search_category: Troubleshooting" in text
    assert "Fast symptom router" in text
    for layer in (
        "environment",
        "source and schema",
        "structural preflight",
        "measurement layer",
        "specification execution",
        "endpoint",
        "interpretation",
        "revision/publication provenance",
    ):
        assert layer in text


def test_troubleshooting_preserves_valid_failure_denominators() -> None:
    text = _read(TROUBLESHOOTING)
    assert "valid but technical failure" in text
    assert "**in the valid denominator**" in text
    assert "6 successful / 7 valid" in text
    assert "Do not report `6 / 6`" in text
    assert "A non-finite endpoint is **not a null effect**" in text


def test_troubleshooting_uses_real_public_contracts() -> None:
    guide = _read(TROUBLESHOOTING)
    recovery = _read(RECOVERY)
    multiverse = _read(MULTIVERSE)
    assert "from gazeaudit import GazeStudy, audit_study_qc" in guide
    assert "valid_specs = space.enumerate_specs(valid_if=valid_if)" in guide
    assert "class PipelineSpace" in multiverse
    assert "def enumerate_specs(" in multiverse
    assert "if valid_if is not None:" in multiverse
    assert "estimate = float(endpoint(processed, spec))" in multiverse
    assert "PipelineSpace" in recovery
    assert "space.enumerate_specs(valid_if=valid_if)" in recovery


def test_failed_audit_recovery_preserves_history_and_same_branch_rerun() -> None:
    text = _read(RECOVERY)
    assert "fully synthetic teaching exercise" in text
    assert "8 declared combinations" in text
    assert "7 valid combinations" in text
    assert "6 successful / 7 valid" in text
    assert "S06 | 1 | technical failure" in text
    assert "S06 | 2 | success after technical repair" in text
    assert "The previous failure is not deleted" in text
    assert "same branch was rerun" in text


def test_recovery_separates_invalid_from_failed_and_nonfinite_from_zero() -> None:
    text = _read(RECOVERY)
    assert "invalid before execution" in text
    assert "valid | technical failure" in text
    assert "Removing S06 because it failed would silently change the denominator" in text
    assert "A non-finite estimate is not evidence of a null effect" in text
    assert 'math.isfinite(estimate)' in text


def test_static_site_discovery_exposes_troubleshooting_without_new_javascript() -> None:
    docs = _read(DOCS_INDEX)
    guides = _read(GUIDES_INDEX)
    examples = _read(EXAMPLES_INDEX)
    assert "[Troubleshooting GazeAudit](guides/troubleshooting/)" in docs
    assert "[Failed-audit recovery walkthrough](examples/failed-audit-recovery/)" in docs
    assert "[Troubleshooting GazeAudit](troubleshooting/)" in guides
    assert "[failed-audit recovery walkthrough](../examples/failed-audit-recovery/)" in guides
    assert "<a href=\"../guides/troubleshooting/\">Troubleshooting GazeAudit</a>" in examples
    assert "<a href=\"failed-audit-recovery/\">Failed-audit recovery →</a>" in examples


def test_troubleshooting_center_is_distinct_from_record_mistakes() -> None:
    troubleshooting = _read(TROUBLESHOOTING)
    mistakes = _read(COMMON_MISTAKES)
    guides = _read(GUIDES_INDEX)
    symptom_boundary = (
        "when a GazeAudit workflow is **blocked, errors, returns an unusable result"
    )
    assert symptom_boundary in troubleshooting
    assert "A technically reproducible analysis can still have a weak scientific record" in mistakes
    assert "The two troubleshooting routes are deliberately different" in guides


def test_documentation_hub_preserves_frozen_evidence_card_markup() -> None:
    text = _read(DOCS_INDEX)
    for state, heading in (
        ("Incomplete", "GazeBase"),
        ("Robust negative", "Korthals"),
        ("Materially fragile", "Pedrotti/de Chambrier"),
    ):
        assert f'<span class="evidence-state">{state}</span>\n    <h3>{heading}</h3>' in text


def test_new_troubleshooting_material_preserves_frozen_outcomes() -> None:
    for text in (_read(TROUBLESHOOTING), _read(RECOVERY)):
        assert "GazeBase" in text and "`incomplete`" in text
        assert "Korthals" in text and "`robust_negative`" in text
        assert "Pedrotti/de Chambrier" in text and "`materially_fragile`" in text
