---
title: Design sampling and missingness sensitivity
description: Methodological guidance for controlled lower-rate gaze representations and added gaze-coordinate missingness in GazeAudit, including baseline missingness, perturbation ranges, reproducible seeds, replication, finite endpoints, interpretation, limitations, and reporting.
kicker: Guide · Controlled sensitivity
permalink: /docs/guides/sampling-missingness-sensitivity/
search_category: Guide
search_keywords: sampling missingness sensitivity downsample target rate MCAR block seed replication retained fraction observed missingness perturbation methodology
---

# Design sampling and missingness sensitivity

Sampling-rate and missingness sensitivity analyses ask whether a **fixed scientific endpoint** changes when the recorded gaze representation is deliberately degraded in a controlled way.

They do not recreate missing observations or simulate another physical eye tracker.

Use the [Sampling & Missingness Sensitivity Center]({{ '/docs/sampling-missingness/' | relative_url }}) to build a no-default plan.

## 1. Start from the canonical representation

Before perturbing anything, preserve:

- source/representation identity;
- timestamp unit;
- mapped participant and trial identifiers;
- original row count;
- observed coordinate missingness;
- declared endpoint;
- temporal evidence layer.

A perturbation analysis is only reconstructable when the baseline is reconstructable.

## 2. Measure observed missingness before adding more

`missingness_mask()` marks a row missing when either mapped `x` or `y` is non-finite.

`summarize_missingness()` reports:

- `n_rows`;
- `n_missing`;
- `missing_fraction`;
- `n_complete`.

```python
from gazeaudit import summarize_missingness

baseline = summarize_missingness(study)
print(baseline)
```

This summary describes the current representation.

It does not identify why gaze is absent.

Do not infer:

- MCAR;
- MAR;
- MNAR;
- blink;
- tracker loss;
- participant disengagement;
- an exclusion rule.

## 3. Treat lower sampling rate as a representation perturbation

`downsample_gaze()` works within each participant × trial stream.

It:

1. validates non-decreasing time;
2. requires finite timestamps;
3. creates a regular target grid from the first to last source timestamp;
4. retains existing rows nearest to that grid;
5. keeps each selected source position only once.

It does **not** interpolate gaze coordinates.

```python
from gazeaudit import downsample_gaze

study_60 = downsample_gaze(
    study,
    60.0,
    timestamp_unit="ms",
)
```

The result is a subset representation of the original recorded rows.

## 4. Do not call downsampling a hardware simulation

A controlled 30-Hz representation does not recreate what a different 30-Hz eye tracker would have recorded.

The perturbation does not model:

- optics;
- firmware;
- calibration;
- sensor noise;
- device-specific sample loss;
- timing jitter;
- gaze-estimation algorithms;
- physical changes to the recorded trajectory.

Preferred language:

> We evaluated sensitivity to a controlled 30-Hz representation of the recorded stream.

Avoid:

> We simulated a 30-Hz tracker.

unless a separate physical/device simulation model actually supports that claim.

## 5. Choose target rates before seeing the endpoint curve

A target-rate set should have a reason.

Possible sources include:

- device-acquisition context;
- planned interoperability with another representation;
- established methodological thresholds;
- preregistered sensitivity bounds;
- design constraints;
- protocol-specific benchmark questions.

Do not choose rates because they preserve the preferred result.

Record the rationale for each range.

## 6. Timestamp unit is part of the perturbation contract

`downsample_gaze()` supports:

- `timestamp_unit="ms"`;
- `timestamp_unit="s"`.

The target interval is calculated from that declaration.

A unit mismatch changes the grid dramatically.

Do not infer timestamp units from column names inside a reproducibility record.

## 7. Report actual retention, not only the target rate

`sampling_sensitivity_curve()` returns:

- `target_hz`;
- `n_rows`;
- `retained_fraction`;
- `estimate`.

```python
from gazeaudit import sampling_sensitivity_curve

curve = sampling_sensitivity_curve(
    study,
    target_rates=[120, 60, 30],
    endpoint=endpoint,
    timestamp_unit="ms",
)
```

Actual retained rows depend on source timing and trial structure.

A target-rate label is not itself the achieved retained fraction.

Report both.

## 8. Sampling curves require a finite common endpoint

Every target representation must evaluate the same scientific endpoint.

The helper converts the endpoint to `float` and rejects non-finite results.

If one target rate cannot produce the endpoint, do not replace it with zero.

Preserve the failure and diagnose the endpoint/representation contract.

## 9. Added missingness operates on currently complete rows

`inject_missingness()` first finds rows where both gaze coordinates are finite.

The requested fraction is applied to those currently complete rows:

```text
n_added = round(requested_fraction × n_currently_complete)
```

Existing missing rows are not candidates for being “masked again.”

This means the requested added fraction and the total observed missing fraction are different quantities.

## 10. Preserve native missingness

The perturbation adds loss.

It does not erase or impute loss that was already present.

Example:

```text
10 total rows
1 native missing row
9 currently complete rows
requested fraction = 0.50
round(0.50 × 9) = 4 added missing rows
final missing rows = 5 / 10
```

The final total missing fraction is 0.50, but that does not mean half of **all rows** were newly masked.

The denominator of the request was the nine complete rows.

## 11. Understand the MCAR benchmark

With `mechanism="mcar"`, GazeAudit selects the requested number of currently complete rows uniformly without replacement.

This is a controlled benchmark perturbation.

It does not prove that empirical eye-tracking missingness is MCAR.

Use language such as:

> We evaluated sensitivity to additional uniformly selected gaze loss.

not:

> The study's missingness was MCAR.

## 12. Understand the block benchmark

With `mechanism="block"`, GazeAudit constructs missingness from contiguous segments within participant × trial streams until approximately the requested number of complete rows is masked; if needed, remaining positions are filled from available complete rows.

This is useful for stress-testing clustered loss.

It is not a generative model of blinks, tracking failures, or participant behavior.

## 13. Preserve a deterministic seed

`inject_missingness()` accepts either:

- an integer seed;
- a NumPy generator;
- `None`.

For a reproducible sensitivity record, use an explicit seed or a governed seed-derivation scheme.

Same study + same mechanism + same fraction + same seed produces the same perturbation.

Seed reproducibility establishes computational identity.

It does not establish that the perturbation is scientifically representative.

## 14. A missingness curve is one draw per fraction per call

`missingness_sensitivity_curve()` initializes one root generator and derives one child seed for every requested fraction.

One function call therefore produces:

```text
fraction 0.00 → one perturbation/endpoint
fraction 0.10 → one perturbation/endpoint
fraction 0.20 → one perturbation/endpoint
...
```

It does not produce a distribution of outcomes at each fraction.

Do not report a single curve as a Monte Carlo interval.

## 15. Add outer replication explicitly when required

If random-realization variability matters, define an outer replication design.

For example:

```python
import pandas as pd

rows = []

for replicate, seed in enumerate(replication_seeds, start=1):
    curve = missingness_sensitivity_curve(
        study,
        fractions=fractions,
        endpoint=endpoint,
        mechanism="mcar",
        rng=seed,
    )
    curve["replicate"] = replicate
    curve["root_seed"] = seed
    rows.append(curve)

replicated = pd.concat(rows, ignore_index=True)
```

Preserve the replicate count and every seed.

Any summary across replicates is a summary of the **declared perturbation design**, not a confidence interval for the empirical scientific effect unless a separate inferential model justifies that interpretation.

## 16. Requested and observed missingness must both be reported

`missingness_sensitivity_curve()` returns:

- `requested_fraction`;
- `mechanism`;
- `observed_missing_fraction`;
- `n_missing`;
- `estimate`.

Observed missingness includes native missingness plus added masking.

Report both requested and observed values.

Do not silently relabel `requested_fraction` as “percentage of all rows missing.”

## 17. Keep sampling and missingness families separate by default

Downsampling and added missingness are different interventions on the representation.

Sampling removes rows according to a regular target grid.

Added missingness retains the row/timestamp structure but masks gaze coordinates.

Unless the protocol explicitly asks about their interaction, run them as separate controlled families.

That keeps interpretation clear:

```text
baseline
├── sampling-rate sensitivity
└── added-missingness sensitivity
```

rather than automatically creating:

```text
sampling rate × added missingness
```

## 18. If a combined design is scientifically justified, declare it explicitly

A combined sampling × missingness experiment can be legitimate.

But then define:

- operation order;
- whether added fractions apply before or after downsampling;
- denominator for the requested fraction;
- seed derivation;
- endpoint;
- complete factor space;
- validity rules;
- interaction interpretation.

Do not let code order become an undocumented scientific decision.

## 19. Do not treat row loss mechanisms as interchangeable

These perturbations answer different questions:

### Lower-rate representation

What happens when fewer source-time samples are retained near a regular grid?

### MCAR added loss

What happens when a requested number of currently complete gaze rows are selected uniformly?

### Block added loss

What happens when additional loss is clustered within participant × trial streams?

A similar retained-row percentage does not make these perturbations scientifically equivalent.

## 20. Separate sensitivity from repair or imputation

`inject_missingness()` creates loss.

It does not repair it.

A sensitivity analysis should not silently introduce interpolation, carry-forward, nearest-neighbor imputation, or another reconstruction algorithm unless that repair is a separate declared factor.

If imputation is scientifically relevant, document and audit it independently.

## 21. Interpret a stable curve cautiously

Suppose the endpoint barely changes across the declared target rates.

You may say:

> The endpoint changed little across the declared controlled lower-rate representations.

Do not infer:

> The endpoint is immune to sampling rate.

The analysis covers only:

- this source representation;
- these target rates;
- this endpoint;
- this downsampling operation.

## 22. Interpret an unstable curve without choosing a preferred perturbation

If the endpoint changes materially as sampling decreases or missingness increases:

- report the pattern;
- identify the declared perturbation range;
- preserve the endpoint;
- investigate mechanism/measurement dependence;
- avoid selecting only the reassuring cells.

Sensitivity is evidence about dependence on representation.

It is not a contest for the “best” target rate or fraction.

## 23. Use the frozen Pedrotti case correctly

The frozen Pedrotti/de Chambrier validation programme uses its own:

- 1000-Hz source representation;
- frozen lower-rate grid;
- native-missingness rule;
- added-missingness fractions;
- mechanisms;
- replicate count;
- seed derivation;
- fixed scientific endpoint;
- recovery and classification rule.

Its canonical outcome is `materially_fragile`.

Those settings and that label are protocol-bound.

Do not copy its rates, fractions, seed, 20% tolerance, or classification thresholds into another study merely because both use eye tracking.

## 24. Reporting checklist

Before reporting controlled sensitivity, verify:

- [ ] baseline source/representation identity recorded;
- [ ] observed missingness summarized before perturbation;
- [ ] endpoint declaration fixed;
- [ ] target rates/fractions justified independently of results;
- [ ] timestamp unit explicit;
- [ ] sampling described as row-retention representation, not hardware simulation;
- [ ] no interpolation falsely implied;
- [ ] missingness mechanism labelled as benchmark perturbation;
- [ ] native missingness preserved;
- [ ] root seed recorded;
- [ ] replication plan explicit when used;
- [ ] requested and observed missingness both reported;
- [ ] sampling and missingness families separated unless combination was explicitly designed;
- [ ] all endpoint values finite or failures preserved;
- [ ] untested perturbation mechanisms/ranges stated.

## 25. Reporting examples

### Methods

> We first quantified observed coordinate missingness in the canonical representation. Sampling sensitivity retained existing observations nearest to prespecified lower-rate grids of [rates] Hz using [unit] timestamps; gaze coordinates were not interpolated. Added-missingness sensitivity was evaluated separately using [MCAR/block] benchmark masking at requested fractions [fractions] with root seed [seed] and [replication plan]. The same declared endpoint was evaluated throughout.

### Results

> At target rates from [high] to [low] Hz, row retention ranged from [fraction] to [fraction] and the endpoint ranged from [min] to [max]. Under [mechanism] added missingness, requested fractions ranged from [x] to [y], total observed missingness ranged from [x] to [y], and the endpoint ranged from [min] to [max]. [Replicate summary, if applicable.]

### Limitation

> The perturbations evaluate controlled representations of the recorded gaze stream. They do not reproduce another tracker's physical measurement process, identify the empirical missingness mechanism, reconstruct unobserved gaze, or provide inferential uncertainty for unrepresented sampling/missingness processes.

## API links

- [`downsample_gaze()`]({{ '/docs/reference/api-pathways/#api-downsample-gaze' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_mask()`]({{ '/docs/reference/api-pathways/#api-missingness-mask' | relative_url }})
- [`summarize_missingness()`]({{ '/docs/reference/api-pathways/#api-summarize-missingness' | relative_url }})
- [`inject_missingness()`]({{ '/docs/reference/api-pathways/#api-inject-missingness' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Sampling & Missingness Sensitivity Center]({{ '/docs/sampling-missingness/' | relative_url }})
- [Machine-readable runtime contract reference]({{ '/assets/sampling-missingness-reference.json' | relative_url }})

## Worked exercise

Continue to [Sampling & missingness design audit]({{ '/docs/examples/sampling-missingness-design-audit/' | relative_url }}) for deterministic, runtime-linked examples of nearest-row downsampling, reproducible MCAR/block masking, native-missingness preservation, requested-versus-observed denominators, and bounded reporting.
