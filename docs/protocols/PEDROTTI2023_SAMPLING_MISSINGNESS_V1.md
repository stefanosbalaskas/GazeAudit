# Pedrotti 2023 sampling/missingness sensitivity protocol v1

## Status

This is a **pre-analysis, outcome-blind** real-data protocol for GazeAudit's sampling-rate and missingness sensitivity case study. No GazeAudit-derived long-minus-short endpoint, perturbation result, recovery fraction, or robustness classification from this dataset was inspected before these choices were frozen.

Machine-readable protocol: `pedrotti2023_sampling_missingness_v1.json`  
Protocol fingerprint: `efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5`

## Public source

The source is the open EyeLink 1000 raw dataset accompanying de Chambrier et al. (2023), *Reading numbers is harder than reading words: An eye-tracking study* (`10.1016/j.actpsy.2023.103942`). The raw-data description is Pedrotti et al. (2023), *Raw eye tracking data of healthy adults reading aloud words, pseudowords and numerals* (`10.1016/j.dib.2023.109360`). The frozen public-data identity is Zenodo record `10.5281/zenodo.7962917`, version `v1`.

The published data article describes 36 healthy adults, 96 centrally presented reading items per participant, and EyeLink 1000 sampling at 1000 Hz. GazeAudit binds the complete published participant-file set (`01.txt` through `36.txt`) plus `readme.txt`. Every Zenodo-published MD5 value is embedded in the protocol and must match before scientific preprocessing; GazeAudit will additionally build a recursive SHA256 source manifest.

## Why this dataset

The case study is intended to evaluate a methodological question rather than reproduce the authors' original inferential analysis: **does a fixed gaze-path endpoint retain its substantive direction and approximate magnitude when the same source observations are represented at lower sampling rates or subjected to additional controlled gaze loss?** The 1000-Hz raw sample streams provide a high-frequency reference representation, while the published files retain native missing gaze and trial-level stimulus labels.

Selection was based on source suitability before the GazeAudit endpoint was calculated. The original paper's reported behavioral/eye-movement results are not used to choose GazeAudit perturbation settings or classification thresholds.

## Frozen cohort and task subset

All 36 participant files are retained; there is no outcome-based participant exclusion. Participant identity is the zero-padded filename stem.

The analysis uses **numeric stimuli only** because short-versus-long numeral length can be recovered from the published `TrialTextShown` field without importing an external stimulus manifest. A stimulus is numeric only after removing the explicitly permitted thousands-separator characters and then requiring the remainder to contain ASCII digits only. Short numerals contain exactly 4 digits; long numerals contain 8–11 digits. Separator-present and separator-absent variants are pooled within the length condition. Words, pseudowords, and anything that does not satisfy this classifier are outside the estimand.

A participant must contribute at least one analyzable short and one analyzable long numeric trial. Failure of that condition is an incomplete protocol execution, not a reason to redefine the cohort.

## Eye and missing-data representation

The raw files expose left- and right-eye columns. For each participant, GazeAudit will use the single side that contains the published finite gaze samples. It will never average eyes or silently switch eyes. If both sides contain finite gaze or neither does, intake fails closed.

Published missing gaze is preserved as non-finite `x/y`. There is no interpolation, carry-forward, nearest-finite substitution, or pre-perturbation deletion. Timestamps and trial rows remain part of the canonical timeline even when gaze is missing.

## Frozen scientific endpoint

For each numeric trial, GazeAudit computes a **gaze-path-length rate**:

1. traverse scheduled samples in time order;
2. add Euclidean pixel displacement only for consecutive scheduled samples whose two endpoints both have finite `x` and `y`;
3. a missing scheduled sample breaks the path, so displacement is never bridged across missingness;
4. divide the resulting path length by the trial's **unperturbed source duration** from its first to last published timestamp.

The source duration is carried unchanged into every perturbation. This prevents a downsampling boundary shift or injected gaze loss from changing the denominator.

Participant condition estimates are unweighted means of trial rates. The participant contrast is **long numeric minus short numeric**. The study estimate is the unweighted mean of participant contrasts. Units are pixels/second difference. This is a descriptive fixed-cohort estimand; no population p-value or causal claim is planned.

## Sampling-rate perturbation family

The unmodified 1000-Hz published timeline is the reference. Five lower representations are frozen: **500, 250, 125, 100, and 50 Hz**.

Within each participant-by-trial stream, lower-rate representations retain the existing source row nearest to a regular grid anchored at the first source timestamp; exact ties select the earlier row. The full timeline is downsampled before any missing-gaze rows are discarded, and in fact missing rows are retained. Gaze coordinates are never interpolated. Sampling-rate perturbations contain native missingness only and are not combined with newly injected missingness.

## Added-missingness perturbation family

Added missingness is evaluated separately at the native 1000-Hz representation. Two mechanisms are frozen:

- **within-trial MCAR**: mask an exact rounded fraction of currently finite gaze rows uniformly without replacement within each trial;
- **single within-trial block**: choose a valid source-row start and mask the shortest forward contiguous source-time window containing the exact rounded target number of finite gaze samples. Native missing rows inside that interval remain missing and do not count toward the added target.

Fractions are **1%, 5%, 10%, and 20%** of the finite gaze rows available in each trial before added masking. Each mechanism × fraction cell has **20 replicates**. The root seed is **`20260913`**. Child seeds are derived from SHA256 of the frozen root seed and lexical participant/trial/specification key, so results do not depend on iteration order or parallel scheduling.

Only `x/y` are masked. Timestamps, trial labels, source duration, and row order remain unchanged.

## Frozen recovery and classification rule

The reference is the unperturbed 1000-Hz native-missingness study estimate. A perturbed estimate is recovered only when it is finite, has the same strict sign as the nonzero reference, and lies within **20% relative deviation** of the reference.

Sampling-family recovery is the fraction of the five lower-rate estimates that recover. Each missingness mechanism × fraction cell has its own recovery fraction across the 20 replicates.

The overall classification is:

- **`robust`**: every sampling and missingness family recovery is at least `0.90`;
- **`materially_fragile`**: at least one family recovery is at most `0.50`;
- **`mixed`**: every other complete finite result;
- **`indeterminate_reference_zero`**: the unperturbed study estimate is exactly zero;
- **`incomplete`**: a source/cohort/condition/trial-duration/perturbation/endpoint validation required by the protocol fails.

If the reference is exactly zero, GazeAudit will not invent an outcome-responsive scale or tolerance. Recovery fractions are perturbation diagnostics, **not confidence intervals, posterior probabilities, or p-values**.

## Post-outcome boundary

After the first real-data result is archived and revealed, the cohort, numeric classifier, endpoint, source-duration rule, perturbation grid, missingness mechanisms, fractions, replicate count, seed derivation, 20% tolerance, 0.90 robustness threshold, 0.50 fragility threshold, and classification semantics cannot be changed in response to the observed result.

The next gate after this protocol is merged and exact-main certified is **endpoint-blind source intake and source freezing**. No real-data scientific endpoint should be run while that layer is being developed or debugged.
