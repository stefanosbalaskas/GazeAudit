# Controlled GazeBase real-data execution

This procedure executes the scientific protocol frozen in
`gazebase_multidetector_protocol.json`. It is intentionally narrower than a general
GazeAudit tutorial: the dataset subset, external reference, detector space, endpoint,
coverage gate, conclusion rule, and software versions are not command-line choices.

## Frozen execution environment

Use Python 3.12 or 3.13 and install the exact case-study dependencies from the
`gazebase` extra:

```bash
python -m pip install -e ".[gazebase]"
```

The runner independently requires `pymovements==0.28.0` and `pEYES==0.2.2` before
constructing any alternative detector. The installed GazeAudit version must satisfy
the frozen minimum, and the exact executing Git commit is recorded in the execution
manifest.

## Execute from an existing GazeBase checkout

The dataset root must use the normal pymovements GazeBase directory structure. Run:

```bash
gazeaudit-gazebase-run \
  --dataset-root data/GazeBase \
  --output-dir artifacts/gazebase-r1s1-fxs-vs-tex \
  --gazeaudit-commit "$(git rev-parse HEAD)"
```

The command loads only Round 1 / Session 1 / `FXS` + `TEX`, accepts the native
pymovements 0.28 `dataset.fileinfo['gaze']` contract, converts the source DVA
coordinates to pixels through pymovements when needed, preserves the distributed
EyeLink parser labels as the external reference, constructs the reference-defined
fixed cohort, and only then executes the seven predeclared pEYES detectors.

Before detector execution, every selected source CSV is read from
`dataset.paths.raw` and SHA-256 hashed. A deterministic aggregate fingerprint of the
selected relative file paths, byte sizes, and content hashes is added to the source
identity. Changing the bytes of any selected GazeBase recording therefore changes the
execution and publication identities even when filenames remain unchanged.

To let pymovements download and extract the catalog resource first, add `--download`.
This uses the cataloged `GazeBase_v2_0.zip` resource whose MD5 is frozen in the
protocol-bound source identity. The source data themselves are not copied into the
GazeAudit artifact bundle.

## Fail-closed behavior

The command stops without a robustness classification if any frozen prerequisite is
violated. This includes protocol-fingerprint drift, missing or unreadable selected
source files, source-identity drift, dependency version drift, an invalid GazeAudit
commit SHA, an exactly zero EyeLink-reference effect, a changed detector set, or
failure of the 95% finite-participant coverage gate. A detector that fails coverage is
not silently removed.

The CLI exposes no detector-threshold, endpoint, cohort, task, tolerance, coverage, or
recovery-rule options. Changing one of those quantities requires a new protocol version
rather than a command-line override.

## Artifact set

A successful command writes a deterministic artifact directory containing the frozen
protocol, execution manifest, detector parameter manifest, source identity, fixed
cohort, endpoint summary tables, detector coverage/effects/recovery tables, and—only
when the completeness gate passes—the verified publication manifest, specifications,
recovery table, methods paragraph, and Markdown report.

Every scientific file is SHA-256 bound in `artifact_manifest.json`. The complete set is
also covered by `SHA256SUMS`. Raw or sample-level gaze data are deliberately excluded.
This means the case-study outputs can be archived without redistributing GazeBase.

Programmatic verification is available with:

```python
from gazeaudit import verify_gazebase_execution_artifacts

assert verify_gazebase_execution_artifacts(
    "artifacts/gazebase-r1s1-fxs-vs-tex"
)
```

Any changed, deleted, or unbound file causes verification to fail.

## Interpretation lock

The first controlled execution should be archived before outcome-driven code or
protocol changes are considered. A `robust` or `fragile` label applies only to the
predeclared GazeBase dataset and selected source bytes, reference-defined cohort,
R1/S1 task contrast, seven pEYES detector specifications, endpoint, completeness rule,
software versions, and conclusion rule encoded by the frozen protocol fingerprint.
