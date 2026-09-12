# Korthals protocol v2: zero-finite matched-cell amendment

## Trigger

The endpoint-blind `korthals-source-freeze #6` run on certified `main` failed before any AOI endpoint, Monte Carlo draw, effect estimate, or classification was executed. The source-readiness guard found one retained task trial with zero finite gaze samples after the already-frozen 50-Hz scheduled-grid selection: participant `88878fe6`, trial `27`.

Protocol v1 is retained unchanged with fingerprint `2b8e8da84182316d08ab173ad7d71a2ff09fc45bd84f875ae548832a288ba291`. Its rule that every retained trial must have at least one finite scheduled sample therefore remains a valid record of the failed v1 source-readiness attempt.

## External evidence check

Before changing any code, the published data descriptor and the exact companion implementation were checked. Korthals, Visser, and Kucharský (2026; DOI `10.1038/s41597-026-06963-4`) define missing data as gaze samples with NA values and report `2.29%` missing data for participant `88878fe6` across trials 1–144. Their technical-validation summary states that data quality is generally good except for participant `21db28aa`, trials 82–144, which they explicitly recommend removing after an unrecalibrated break. The paper also documents that EyeLink blink samples and the 50 ms before/after each blink are set to NA by the default preprocessing.

The frozen companion commit remains `1d7ebec23e3fe20f6db952eefda1a0dd58ae09da`. Its `OriginalPreprocessor` implements that ±50 ms blink masking and does not provide a special exclusion or repair for participant `88878fe6` trial 27. No later upstream companion commit exists at the time of this amendment.

These checks indicate that the source-freeze failure is not an upstream instruction to change blink handling, grid phase, or participant eligibility. It is a conflict between ordinary published missingness and GazeAudit protocol v1's stricter zero-finite-trial readiness rule.

## Version-2 rule

Protocol v2 fingerprint: `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`.

The only scientific amendment is general and symmetric:

- Preserve the exact companion preprocessing, ±50 ms blink mask, target-master alignment, fixed 50-Hz grid, earlier-sample tie rule, validation mapping, AOI, matched-cell definition, participant/study weighting, Monte Carlo settings, and seed.
- After fixed-grid selection, identify task trials with **zero finite selected gaze samples**.
- Do **not** interpolate, substitute a nearby finite sample, move/phase-shift the grid, shorten the blink window, or special-case a participant/trial.
- Instead, mark the affected paired cell structurally unestimable and remove **both** its `moving_circle` and `jumping_circle` members.
- Preserve all unrelated matched cells.
- Every source participant must retain at least one complete matched cell; otherwise preparation fails closed.
- Validation mapping remains fail-closed **before** any missingness-based cell removal, so a zero-finite trial cannot hide an unmapped validation block.
- Record the zero-finite trial identities and removed matched-cell identities in the endpoint-blind source-intake artifact.

This is a paired complete-cell rule, not an outcome-dependent exclusion. It is applied before any scientific effect is computed and is encoded for all participants/trials rather than for the observed `88878fe6`/27 case alone.

## Scientific boundary

At amendment time, no Korthals target-window occupancy effect, Monte Carlo endpoint distribution, sign-stability probability, or final classification had been executed or inspected. The source-freeze workflow remains archive-before-reveal and endpoint-blind.
