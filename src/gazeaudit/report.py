"""Human-readable audit reporting."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from .robustness import (
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
)


def render_markdown_audit(
    results: pd.DataFrame,
    *,
    factors: Sequence[str] = (),
    estimate_col: str = "estimate",
    null: float = 0.0,
    title: str = "GazeAudit robustness report",
) -> str:
    """Render a deterministic Markdown summary of a specification analysis."""

    stability = effect_stability(results, estimate_col=estimate_col, null=null)
    lines = [
        f"# {title}",
        "",
        "## Effect stability",
        "",
        f"- Specifications evaluated: {int(stability['n_specifications'])}",
        f"- Median estimate: {stability['median_estimate']:.6g}",
        f"- 2.5%–97.5% specification range: "
        f"{stability['q025']:.6g} to {stability['q975']:.6g}",
        f"- Positive-effect specifications: {stability['positive_fraction']:.1%}",
        f"- Negative-effect specifications: {stability['negative_fraction']:.1%}",
        f"- Sign stability: {stability['sign_stability']:.1%}",
    ]

    factor_list = list(factors)
    if factor_list:
        sensitivity = marginal_sensitivity(
            results, factor_list, estimate_col=estimate_col
        )
        lines.extend(
            [
                "",
                "## Marginal specification sensitivity",
                "",
                "| Factor | Levels | Marginal eta² | Level-mean range |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in sensitivity.itertuples(index=False):
            lines.append(
                f"| {row.factor} | {row.n_levels} | {row.marginal_eta2:.4f} | "
                f"{row.level_mean_range:.6g} |"
            )
        lines.extend(
            [
                "",
                "> Marginal eta² values are descriptive sensitivity diagnostics. "
                "They can overlap and should not be interpreted as a causal or additive "
                "variance decomposition.",
            ]
        )

    if len(factor_list) >= 2:
        interactions = pairwise_interaction_sensitivity(
            results,
            factor_list,
            estimate_col=estimate_col,
        )
        lines.extend(
            [
                "",
                "## Pairwise interaction sensitivity",
                "",
                "| Factor A | Factor B | Cells | Interaction ratio | Max absolute interaction |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for row in interactions.itertuples(index=False):
            lines.append(
                f"| {row.factor_a} | {row.factor_b} | {row.n_cells} | "
                f"{row.interaction_ratio:.4f} | {row.max_abs_interaction:.6g} |"
            )
        lines.extend(
            [
                "",
                "> Interaction ratios are descriptive diagnostics of non-additive "
                "specification dependence. They need not sum to one and are not causal effects.",
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation guardrail",
            "",
            "This report characterizes robustness across the specifications supplied by "
            "the researcher. It does not establish that every specification is scientifically "
            "defensible and does not automate substantive interpretation.",
            "",
        ]
    )
    return "\n".join(lines)
