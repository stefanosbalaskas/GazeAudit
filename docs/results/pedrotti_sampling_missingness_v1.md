# Pedrotti/de Chambrier sampling + missingness — authoritative result

## Status

This document records the **first scientific execution** of the frozen
Pedrotti/de Chambrier sampling-and-missingness protocol. The outcome is authoritative
for this case study. It was executed only after the protocol, endpoint-blind public
source freeze, independent source-lock binding, scientific implementation, and
archive-before-reveal workflow had been fixed and certified.

No scientific choice in this record was selected or changed after observing the
outcome.

## Immutable provenance

| Field | Value |
|---|---|
| Scientific workflow | `pedrotti-scientific-execution #1` |
| GitHub run | `34793103977` |
| GitHub job | `103820948264` |
| Execution commit | `270d444c599363ebd25f25e8a95f5f3c78e55b02` |
| Execution tree | `0c44a211abc7fa5d22706daad319b0e44036f153` |
| Protocol fingerprint | `efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5` |
| Source-lock fingerprint | `d71949f035ecdf14b9e225b8ca441d291625767dc4a07fa4854882ff2dcae898` |
| Source-manifest fingerprint | `ca676426a01c1d57dda93b62709d4e9040369e4193c0b44353be78d644a33b1f` |
| Zenodo DOI | `10.5281/zenodo.7962917` |
| Zenodo record | `7962917` |

The exact critical execution environment was Python 3.12.14, NumPy 2.5.3, and
pandas 2.3.3.

## Scientific archive

The workflow verified the scientific payload, uploaded the artifact, and only then
executed the reveal step.

| Field | Value |
|---|---|
| Artifact ID | `10328414078` |
| Artifact name | `pedrotti-scientific-execution-v1-270d444c599363ebd25f25e8a95f5f3c78e55b02` |
| Artifact size | 42,170 bytes |
| GitHub artifact SHA256 | `b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5` |
| Independently recomputed ZIP SHA256 | `b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5` |
| Results fingerprint | `5bafe0d1d1d0d054a681cb7136fc4e259c0f75e07d51653acde472c7c6e4dce9` |
| Execution fingerprint | `35dd53da10646400aca657c388f8b77a6a974c555de7efbd6f83faeb970b1eb6` |
| Artifact-manifest fingerprint | `05a986abe8a7be7a7ccbf2bf24b7467a3c623381d05d2dab8f4ae81b0618d661` |

The archive `SHA256SUMS` was independently verified and every declared file matched.
The GitHub-provided artifact digest and independently recomputed ZIP digest are
identical. All 165 individual recovery diagnostics were recomputed from the archived
estimates with zero mismatches, and all nine family-recovery fractions were reproduced.

## Frozen estimand

The endpoint is the participant-balanced **long-minus-short numeric gaze-path-rate
difference**, expressed in pixels per second.

For each participant, trial-level path displacement is divided by the original trial
duration. Short and long numeric trial means are formed within participant, their
difference is computed, and participant contrasts are averaged without weighting at the
study level.

Native missingness is preserved. Path displacement is accumulated only across
consecutive scheduled rows whose two gaze endpoints are finite; gaps are not bridged.

## Reference result

**Reference estimate: `-75.37814047218419` pixels/second.**

The negative direction means that, under this frozen endpoint definition, the long
numeric condition had a lower participant-balanced gaze-path rate than the short numeric
condition.

## Sampling-rate sensitivity

| Target rate | Estimate | Relative deviation | Same sign | Recovered |
|---:|---:|---:|:---:|:---:|
| 500 Hz | -74.56183041024825 | 0.0108295330 | yes | yes |
| 250 Hz | -66.34948502911872 | 0.1197781663 | yes | yes |
| 125 Hz | -47.46801941944103 | 0.3702681026 | yes | no |
| 100 Hz | -46.22977448634684 | 0.3866952117 | yes | no |
| 50 Hz | -20.561785313728368 | 0.7272181937 | yes | no |

Sampling-family recovery is therefore `0.4`.

Downsampling preserved the negative sign at all five target rates, but 125, 100, and
50 Hz exceeded the predeclared 20% relative-deviation tolerance.

## Added-missingness sensitivity

Family recovery fractions were:

| Mechanism | Added missingness | Recovery fraction |
|---|---:|---:|
| MCAR within trial | 1% | 1.00 |
| MCAR within trial | 5% | 1.00 |
| MCAR within trial | 10% | 0.40 |
| MCAR within trial | 20% | 0.00 |
| Single block within trial | 1% | 1.00 |
| Single block within trial | 5% | 0.55 |
| Single block within trial | 10% | 0.40 |
| Single block within trial | 20% | 0.00 |

Each missingness family contains the 20 prespecified deterministic replicates generated
from root seed `20260913`.

## Authoritative classification

**Classification: `materially_fragile`.**

The frozen rule requires strict sign agreement plus no more than 20% relative
deviation for an individual estimate. A family is robust only when its recovery
fraction reaches the prespecified minimum; the full execution is classified
`materially_fragile` when any family reaches the material-fragility ceiling.

The independently recomputed family table contains several recovery fractions at `0.4`
or `0.0`, so the predeclared rule necessarily returns `materially_fragile`.

This classification is about recovery of the **magnitude-and-direction criterion**.
It should not be paraphrased as sign reversal: every sampling-rate estimate remained
negative.

## Inferential boundary

This case study is a robustness/sensitivity audit. It does not provide a population
confidence interval, posterior interval, p-value, or causal effect claim. Its purpose is
to show how strongly the frozen descriptive endpoint depends on sampling resolution and
controlled missingness perturbations.

## Post-outcome scientific freeze

The following may not be changed in response to this result: source cohort; source-file
identity; endpoint or contrast direction; dominant-eye/native-timeline policy; sampling
grid; target rates; missingness mechanisms; missingness fractions; replicate count;
seed derivation; original-duration denominator; 20% relative tolerance; strict-sign
rule; family recovery threshold; material-fragility ceiling; or final classification
logic.

Permitted follow-up is limited to independent artifact verification, deterministic
reproducibility checking without selecting among outcomes, archival/provenance work,
publication reporting, and non-scientific infrastructure maintenance.
