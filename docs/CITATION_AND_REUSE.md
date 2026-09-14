# Citation, reporting, and reuse guidance

GazeAudit is currently an **alpha pre-release package**. The repository contains a
scientifically validated MVP and release-qualified `0.1.0.dev20` distributions, but no
stable `0.1.0` tag or formal package publication is implied by those qualification
artifacts.

## Citing the software before the first tagged release

Use the metadata in the repository root [`CITATION.cff`](../CITATION.cff) and report the
**exact GazeAudit commit** used for the analysis. For reproducible manuscripts, also
report the installed package version and the scientific protocol or publication-bundle
fingerprint relevant to the analysis.

A methods or software statement should therefore identify, at minimum:

- software name: GazeAudit;
- repository: `stefanosbalaskas/GazeAudit`;
- exact commit SHA used;
- installed package version;
- Python version;
- the frozen protocol fingerprint for any controlled validation or case-study analysis.

Do not cite the development version as if it were a stable archival release. When a
formal release exists, use the release/DOI metadata supplied for that release and retain
the exact analysis commit when it materially improves reproducibility.

## Reporting a GazeAudit robustness analysis

A scientific report should distinguish the following identities rather than collapsing
them into a single version number:

1. **source identity** — dataset version, source-lock fingerprint, or execution-bound
   source manifest;
2. **protocol identity** — the frozen analytical-choice and decision-rule fingerprint;
3. **execution identity** — exact code commit, runtime/dependency environment, and
   execution fingerprint;
4. **scientific result identity** — results/scientific fingerprint where defined;
5. **artifact identity** — artifact ID/name plus archive or manifest SHA-256.

The canonical MVP examples are indexed in
[`REPRODUCIBILITY_INDEX.json`](REPRODUCIBILITY_INDEX.json) and summarized in
[`PUBLICATION_SUMMARY.md`](PUBLICATION_SUMMARY.md). The authoritative outcome matrix is
[`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md).

## Interpretation language

Use classification terms only according to the rule that generated them. In the
canonical validation cases:

- `incomplete` means the declared specification space failed its completeness gate and
  therefore did not support a robustness classification;
- `robust_negative` means the prespecified negative direction remained stable under the
  frozen Korthals measurement-error propagation model;
- `materially_fragile` means the Pedrotti endpoint failed the frozen recovery criterion
  under defensible sampling/missingness perturbations.

These labels are protocol-bound. They are not generic synonyms for nonsignificant,
significant, good, bad, reliable, or unreliable.

## Reusing canonical validation records

The archived real-data artifacts are evidence records, not templates to edit in place.
If a new study changes the cohort, endpoint, AOIs, detector set, uncertainty model,
perturbation grid, missingness mechanism, seed, recovery tolerance, completeness gate,
or classification rule, create a new protocol identity and new execution provenance.
Do not overwrite a canonical fingerprint or artifact to make a new analysis appear
continuous with an old one.

The GazeBase scientific artifact deliberately excludes raw/sample-level GazeBase data.
For Korthals and Pedrotti, source identity and scientific execution are likewise kept as
separate provenance layers where the controlled workflow requires that distinction.
Users remain responsible for complying with the source datasets' own access, citation,
and licensing requirements.

## Manuscript reproducibility checklist

Before submission or archival, verify that the manuscript or supplement records:

- the GazeAudit version and exact commit;
- the data/source identity used;
- the protocol fingerprint;
- the execution/scientific fingerprint(s), where available;
- the artifact checksum or immutable archival identifier;
- the classification rule and interpretation boundary;
- any optional interoperability packages and their versions;
- whether reported uncertainty is measurement-model-induced, sampling-based,
  inferential, or another explicitly defined quantity.

For the package's own scientific-MVP evidence, use the exact identities in the
reproducibility index rather than transcribing values from memory.

## Release procedure

The stable-release qualification procedure is documented in [`RELEASE.md`](RELEASE.md).
The release-candidate workflow validates tag/version/changelog identity and rebuilds the
candidate distributions, but it deliberately does **not** publish to PyPI or create a
GitHub Release. Publication remains a separate explicit action after successful release
qualification.
