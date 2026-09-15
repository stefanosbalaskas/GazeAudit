"""Temporary branch bootstrap for the analysis-readiness + plot-gallery tranche."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"bootstrap anchor not found in {path}: {old[:80]!r}")
    write(path, text.replace(old, new, 1))


def wire_public_api() -> None:
    path = "src/gazeaudit/__init__.py"
    text = read(path)
    readiness_import = '''from .readiness import (
    ANALYSIS_READINESS_ARTIFACT_SCHEMA,
    ANALYSIS_READINESS_PUBLICATION_LINK_SCHEMA,
    ANALYSIS_READINESS_SCHEMA,
    REPAIR_COMPARISON_SCHEMA,
    AnalysisReadinessReport,
    ReadinessThresholds,
    RepairComparison,
    analysis_readiness_publication_metadata,
    cohort_impact_preview,
    compare_qc_states,
    evaluate_analysis_readiness,
    filter_study_by_readiness,
    participant_qc_summary,
    readiness_pipeline_processor,
    readiness_policy_table,
    trial_qc_summary,
    verify_analysis_readiness_artifacts,
    verify_analysis_readiness_manifest,
    verify_analysis_readiness_report,
    verify_repair_comparison,
    verify_repair_comparison_manifest,
    write_analysis_readiness_artifacts,
)
from .plotting import (
    plot_aoi_probability_profile,
    plot_cohort_impact,
    plot_factor_sensitivity,
    plot_gaze_trajectory,
    plot_participant_readiness,
    plot_policy_tradeoffs,
    plot_qc_issue_profile,
    plot_recovery_matrix,
    plot_repair_comparison,
    plot_sensitivity_curve,
    plot_specification_curve,
    plot_threshold_sweep,
    plot_trial_readiness,
)
'''
    if "from .readiness import (" not in text:
        text = text.replace("from .robustness import (", readiness_import + "from .robustness import (", 1)

    exported = [
        "ANALYSIS_READINESS_ARTIFACT_SCHEMA",
        "ANALYSIS_READINESS_PUBLICATION_LINK_SCHEMA",
        "ANALYSIS_READINESS_SCHEMA",
        "REPAIR_COMPARISON_SCHEMA",
        "AnalysisReadinessReport",
        "ReadinessThresholds",
        "RepairComparison",
        "analysis_readiness_publication_metadata",
        "cohort_impact_preview",
        "compare_qc_states",
        "evaluate_analysis_readiness",
        "filter_study_by_readiness",
        "participant_qc_summary",
        "readiness_pipeline_processor",
        "readiness_policy_table",
        "trial_qc_summary",
        "verify_analysis_readiness_artifacts",
        "verify_analysis_readiness_manifest",
        "verify_analysis_readiness_report",
        "verify_repair_comparison",
        "verify_repair_comparison_manifest",
        "write_analysis_readiness_artifacts",
        "plot_aoi_probability_profile",
        "plot_cohort_impact",
        "plot_factor_sensitivity",
        "plot_gaze_trajectory",
        "plot_participant_readiness",
        "plot_policy_tradeoffs",
        "plot_qc_issue_profile",
        "plot_recovery_matrix",
        "plot_repair_comparison",
        "plot_sensitivity_curve",
        "plot_specification_curve",
        "plot_threshold_sweep",
        "plot_trial_readiness",
    ]
    marker = "\n]\n\n__version__ ="
    if marker not in text:
        raise RuntimeError("__all__ terminator not found")
    prefix, suffix = text.split(marker, 1)
    additions = []
    for name in exported:
        token = f'    "{name}",'
        if token not in prefix:
            additions.append(token)
    if additions:
        prefix += "\n" + "\n".join(additions)
    text = prefix + marker + suffix
    text = text.replace('__version__ = "0.1.0.dev19"', '__version__ = "0.1.0.dev20"')
    write(path, text)


def wire_layout() -> None:
    path = "_layouts/default.html"
    text = read(path)
    if "/assets/css/gallery.css" not in text:
        text = text.replace(
            '<link rel="stylesheet" href="{{ \'/assets/css/enhancements.css\' | relative_url }}">',
            '<link rel="stylesheet" href="{{ \'/assets/css/enhancements.css\' | relative_url }}">\n  <link rel="stylesheet" href="{{ \'/assets/css/gallery.css\' | relative_url }}">',
            1,
        )
    if "Plot gallery" not in text:
        text = text.replace(
            '<a href="{{ \'/docs/examples/\' | relative_url }}">Examples</a>',
            '<a href="{{ \'/docs/examples/\' | relative_url }}">Examples</a>\n        <a href="{{ \'/docs/plots/\' | relative_url }}">Plots</a>',
            1,
        )
        text = text.replace(
            '<a href="{{ \'/docs/examples/\' | relative_url }}">Examples</a>',
            '<a href="{{ \'/docs/examples/\' | relative_url }}">Examples</a>\n      <a href="{{ \'/docs/plots/\' | relative_url }}">Plot gallery</a>',
            1,
        )
        text = text.replace(
            '<a href="{{ \'/docs/examples/end-to-end-robustness/\' | relative_url }}">End-to-end robustness</a>',
            '<a href="{{ \'/docs/examples/end-to-end-robustness/\' | relative_url }}">End-to-end robustness</a>\n            <a href="{{ \'/docs/examples/analysis-readiness/\' | relative_url }}">Analysis readiness</a>\n            <a href="{{ \'/docs/plots/\' | relative_url }}">Plot gallery</a>',
            1,
        )
        text = text.replace(
            '<a href="{{ \'/docs/guides/data-onboarding/\' | relative_url }}">Data onboarding</a>',
            '<a href="{{ \'/docs/guides/data-onboarding/\' | relative_url }}">Data onboarding</a>\n            <a href="{{ \'/docs/guides/analysis-readiness/\' | relative_url }}">Analysis readiness</a>',
            1,
        )
    if "/assets/js/gallery.js" not in text:
        text = text.replace(
            '<script src="{{ \'/assets/js/site.js\' | relative_url }}" defer></script>',
            '<script src="{{ \'/assets/js/site.js\' | relative_url }}" defer></script>\n  <script src="{{ \'/assets/js/gallery.js\' | relative_url }}" defer></script>',
            1,
        )
    write(path, text)


def wire_pages() -> None:
    for path, permalink in (
        ("docs/guides/analysis-readiness.md", "/docs/guides/analysis-readiness/"),
        ("docs/examples/analysis-readiness.md", "/docs/examples/analysis-readiness/"),
    ):
        text = read(path)
        if "permalink:" not in text.split("---", 2)[1]:
            text = text.replace("kicker: ", "permalink: " + permalink + "\nkicker: ", 1)
            write(path, text)

    index = json.loads(read("assets/search-index.json"))
    additions = [
        {
            "title": "Analysis-readiness governance",
            "category": "Guides",
            "url": "/docs/guides/analysis-readiness/",
            "description": "Declare provenance-bound structural-QC policies, preview cohort impact, compare repairs, and expose QC choices to specification analysis.",
            "keywords": "analysis readiness participant trial QC threshold policy cohort impact repair provenance filtering specification",
        },
        {
            "title": "Analysis-readiness example",
            "category": "Examples",
            "url": "/docs/examples/analysis-readiness/",
            "description": "Executable synthetic workflow from structural QC through policy comparison, repair comparison, and specification-space integration.",
            "keywords": "readiness example threshold cohort repair PipelineSpace run_specs",
        },
        {
            "title": "Plot gallery",
            "category": "Visual reference",
            "url": "/docs/plots/",
            "description": "Fourteen deterministic Matplotlib figures generated from executable GazeAudit code.",
            "keywords": "plots gallery matplotlib QC readiness AOI specification sensitivity recovery code generated",
        },
    ]
    urls = {item["url"] for item in index}
    for item in additions:
        if item["url"] not in urls:
            index.append(item)
    write("assets/search-index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n")


def augment_docs() -> None:
    hub = read("docs/index.md")
    if "Plot gallery" not in hub:
        hub = hub.replace(
            "| Map a vendor table and inspect structural QC | [Data onboarding and structural preflight](guides/data-onboarding/) |",
            "| Map a vendor table and inspect structural QC | [Data onboarding and structural preflight](guides/data-onboarding/) |\n| Declare participant/trial readiness policies and preview cohort impact | [Analysis-readiness governance](guides/analysis-readiness/) |\n| Browse reproducible code-generated figures | [Plot gallery](plots/) |",
            1,
        )
        hub += "\n## Code-generated visual reference\n\nThe [plot gallery](plots/) contains 14 deterministic Matplotlib SVGs tied to executable source, including readiness, cohort-impact, repair, specification, sensitivity, AOI, and recovery diagnostics.\n"
        write("docs/index.md", hub)

    api = read("docs/reference/api-map.md")
    if "## Analysis-readiness governance" not in api:
        block = '''## Analysis-readiness governance\n\n| API | Purpose |\n|---|---|\n| `ReadinessThresholds` | Researcher-declared structural-QC policy with no universal package defaults and a deterministic policy fingerprint. |\n| `trial_qc_summary` | Aggregate structural-QC metrics by participant × trial unit. |\n| `participant_qc_summary` | Aggregate trial QC into participant-level summaries. |\n| `evaluate_analysis_readiness` | Evaluate the declared policy and return trial/participant summaries, cohort impact, and provenance. |\n| `cohort_impact_preview` | Inspect filtering consequences without mutating the study. |\n| `filter_study_by_readiness` | Explicitly apply an already evaluated policy at trial or participant scope. |\n| `readiness_policy_table` | Compare cohort consequences across multiple declared policies. |\n| `readiness_pipeline_processor` | Expose readiness policy as an explicit `PipelineSpace` choice. |\n| `compare_qc_states` | Bind before/after structural-QC states and metric deltas without asserting repair validity. |\n| `analysis_readiness_publication_metadata` | Bind policy-relative readiness provenance into publication metadata. |\n| `write_analysis_readiness_artifacts` / `verify_analysis_readiness_artifacts` | Write and verify deterministic readiness evidence. |\n\nPassing a readiness policy means only that the canonical table satisfies that declared structural policy. It is not a universal data-quality score or a scientific-validity judgement.\n\n'''
        api = api.replace("## AOIs and measurement uncertainty\n", block + "## AOIs and measurement uncertainty\n", 1)
    if "## Plotting API" not in api:
        plotting = '''## Plotting API\n\nInstall the optional plotting extra with `python -m pip install "gazeaudit[plot]"`. Public helpers cover structural QC profiles, trial/participant readiness, cohort impact, repair comparison, policy trade-offs, threshold sweeps, specification curves, factor sensitivity, generic sensitivity curves, gaze trajectories with AOI overlays, probabilistic AOI boundary profiles, and recovery matrices. See the [plot gallery]({{ '/docs/plots/' | relative_url }}) for executable examples.\n\n'''
        api = api.replace("## Eye-Tracking-BIDS\n", plotting + "## Eye-Tracking-BIDS\n", 1)
    write("docs/reference/api-map.md", api)

    for path, line in (
        ("docs/guides/index.md", "- [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — declare structural-QC policies, preview cohort impact, and bind provenance.\n"),
        ("docs/examples/index.md", "- [Analysis-readiness example]({{ '/docs/examples/analysis-readiness/' | relative_url }}) — executable policy, cohort-impact, repair, and specification-space workflow.\n- [Plot gallery]({{ '/docs/plots/' | relative_url }}) — 14 deterministic code-generated figures with source links.\n"),
    ):
        text = read(path)
        if "Analysis-readiness" not in text:
            text += "\n" + line
            write(path, text)

    readme = read("README.md")
    if "Plot gallery" not in readme:
        readme += '''\n## Development documentation on `main`\n\nPost-release development now includes provenance-bound analysis-readiness governance and a [code-generated plot gallery](https://stefanosbalaskas.github.io/GazeAudit/docs/plots/) covering QC, cohort impact, repairs, specification curves, sensitivity, AOI geometry, and recovery diagnostics. These additions do not alter the frozen v0.1.0 scientific outcomes.\n'''
        write("README.md", readme)

    landing = read("index.md")
    if "Code-generated plot gallery" not in landing:
        landing += '''\n<section class="section-shell">\n  <p class="eyebrow">Visual methods reference</p>\n  <h2>Code-generated plot gallery</h2>\n  <p>Browse reproducible Matplotlib figures for structural QC, analysis readiness, cohort impact, repairs, specification analysis, sensitivity, AOI geometry, and recovery diagnostics.</p>\n  <p><a class="button secondary" href="{{ '/docs/plots/' | relative_url }}">Open the plot gallery →</a> <a class="button secondary" href="{{ '/docs/guides/analysis-readiness/' | relative_url }}">Analysis-readiness guide →</a></p>\n</section>\n'''
        write("index.md", landing)


def harden_workflow() -> None:
    path = ".github/workflows/plot-gallery.yml"
    text = read(path)
    old = "      - name: Verify committed gallery is reproducible\n        run: git diff --exit-code -- assets/plots\n"
    new = "      - name: Verify committed gallery is reproducible\n        run: |\n          git diff --exit-code -- assets/plots\n          test -z \"$(git status --porcelain --untracked-files=all -- assets/plots)\"\n"
    if old in text:
        text = text.replace(old, new, 1)
        write(path, text)


def main() -> None:
    wire_public_api()
    wire_layout()
    wire_pages()
    augment_docs()
    harden_workflow()
    subprocess.run([sys.executable, "tools/generate_plot_gallery.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
