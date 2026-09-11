import pandas as pd

from gazeaudit.report import render_markdown_audit


def test_report_includes_pairwise_interaction_section_for_two_factors():
    results = pd.DataFrame(
        {
            "detector": ["a", "a", "b", "b"],
            "qc": ["low", "high", "low", "high"],
            "estimate": [0.0, 1.0, 1.0, 0.0],
        }
    )
    report = render_markdown_audit(results, factors=["detector", "qc"])
    assert "Pairwise interaction sensitivity" in report
    assert "Interaction ratio" in report
    assert "not causal effects" in report
