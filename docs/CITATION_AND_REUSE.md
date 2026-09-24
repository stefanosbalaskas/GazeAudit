# Citation, reporting, and reuse guidance

GazeAudit **v0.2.0 is a published software release**. Its GitHub Release and PyPI payload are externally verified, including exact wheel/source-distribution hashes and a clean public-PyPI installation check. The v0.2.0 publication tranche did not include a Zenodo deposit.

See the [v0.2.0 external publication record](EXTERNAL_PUBLICATION_0.2.0.html) and [documentation provenance](reference/site-provenance/) for the current software/documentation identity boundary.

## Citing the software

Use the metadata in the repository root [`CITATION.cff`](../CITATION.cff) and report the **exact installed version** and, when relevant, the **exact GazeAudit commit** used for the analysis.

For v0.2.0, record at minimum:

- software: GazeAudit;
- version: `0.2.0`;
- repository: `stefanosbalaskas/GazeAudit`;
- Python version;
- exact Git commit when the analysis used development functionality beyond the release;
- the frozen protocol fingerprint for any controlled validation or case-study analysis.

GazeAudit does not claim a version-specific Zenodo DOI for v0.2.0. The DOI `10.5281/zenodo.22757340` remains specific to the archived **v0.1.0** release.

Do not infer archival publication from a version string alone. Match any DOI, tag, GitHub Release, PyPI distribution, or archive identifier to the exact software state actually used.

## Reporting a GazeAudit robustness analysis

A scientific report should distinguish the following identities rather than collapsing them into a single version number:

1. **source identity** — dataset version, source-lock fingerprint, or execution-bound source manifest;
2. **protocol identity** — the frozen analytical-choice and decision-rule fingerprint;
3. **execution identity** — exact code commit, runtime/dependency environment, and execution fingerprint;
4. **scientific result identity** — results/scientific fingerprint where defined;
5. **artifact identity** — artifact ID/name plus archive or manifest SHA-256.

The canonical MVP examples are indexed in [`REPRODUCIBILITY_INDEX.json`](REPRODUCIBILITY_INDEX.json) and summarized in [`PUBLICATION_SUMMARY.md`](PUBLICATION_SUMMARY.md). The authoritative outcome matrix is [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md).

## Interpretation language

Use classification terms only according to the rule that generated them. In the canonical validation cases:

- `incomplete` means the declared specification space failed its completeness gate and therefore did not support a robustness classification;
- `robust_negative` means the prespecified negative direction remained stable under the frozen Korthals measurement-error propagation model;
- `materially_fragile` means the Pedrotti endpoint failed the frozen recovery criterion under defensible sampling/missingness perturbations.

These labels are protocol-bound. They are not generic synonyms for nonsignificant, significant, good, bad, reliable, or unreliable.

## Reusing canonical validation records

The archived real-data artifacts are evidence records, not templates to edit in place. If a new study changes the cohort, endpoint, AOIs, detector set, uncertainty model, perturbation grid, missingness mechanism, seed, recovery tolerance, completeness gate, or classification rule, create a new protocol identity and new execution provenance.

Do not overwrite a canonical fingerprint or artifact to make a new analysis appear continuous with an old one.

The GazeBase scientific artifact deliberately excludes raw/sample-level GazeBase data. For Korthals and Pedrotti, source identity and scientific execution are likewise kept as separate provenance layers where the controlled workflow requires that distinction. Users remain responsible for complying with source-dataset access, citation, and licensing requirements.

## Manuscript reproducibility checklist

Before submission or archival, verify that the manuscript or supplement records:

- the GazeAudit version and, where relevant, exact commit;
- the data/source identity used;
- the protocol fingerprint;
- the execution/scientific fingerprint(s), where available;
- the artifact checksum or immutable archival identifier;
- the classification rule and interpretation boundary;
- any optional interoperability packages and their versions;
- whether reported uncertainty is measurement-model-induced, sampling-based, inferential, or another explicitly defined quantity;
- whether the software state was a tagged release or development commit;
- whether every DOI or archive identifier corresponds to the exact version/artifact being cited.

For the package's own scientific-MVP evidence, use the exact identities in the reproducibility index rather than transcribing values from memory.

## Release procedure

The stable-release qualification procedure is documented in [`RELEASE.md`](RELEASE.md). Qualification, GitHub Release publication, PyPI publication, and archival/DOI publication are separate controlled actions.

For v0.2.0, the GitHub Release and PyPI stages are verified. Zenodo remained outside that release tranche.
