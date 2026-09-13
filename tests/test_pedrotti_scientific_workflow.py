from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "pedrotti-scientific-execution.yml"
)


def test_pedrotti_scientific_workflow_is_manual_main_only_and_frozen() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "push:" not in text
    assert "pull_request:" not in text
    assert "if: github.ref == 'refs/heads/main'" in text
    assert "python-version: '3.12.14'" in text
    assert '"numpy==2.5.3"' in text
    assert '"pandas==2.3.3"' in text


def test_pedrotti_scientific_workflow_locks_source_before_endpoint() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    lock_step = text.index(
        "- name: Verify locked endpoint-blind intake before scientific execution"
    )
    execute_step = text.index(
        "- name: Execute frozen protocol and build hidden scientific archive"
    )
    assert lock_step < execute_step
    assert "verify_pedrotti_locked_intake" in text[lock_step:execute_step]


def test_pedrotti_scientific_workflow_archives_before_reveal() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    execute_step = text.index(
        "- name: Execute frozen protocol and build hidden scientific archive"
    )
    verify_step = text.index("- name: Verify scientific archive before upload")
    archive_step = text.index("- name: Archive scientific result before reveal")
    reveal_step = text.index("- name: Reveal archived scientific result")
    assert execute_step < verify_step < archive_step < reveal_step
    hidden_section = text[execute_step:archive_step]
    assert "pedrotti_reveal_cli" not in hidden_section
    assert "cat " not in hidden_section
    assert "actions/upload-artifact@v7" in text[archive_step:reveal_step]
