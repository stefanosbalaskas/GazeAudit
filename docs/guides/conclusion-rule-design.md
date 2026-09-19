---
title: Design conclusion-recovery rules
description: Methodological guidance for declaring GazeAudit reference effects, absolute/relative tolerances, sign recovery, minimum recovery fractions, timing, zero-reference behavior, and publication reporting without circular validation or significance reinterpretation.
kicker: Guide · Conclusion governance
permalink: /docs/guides/conclusion-rule-design/
search_category: Guide
search_keywords: ConclusionRule reference effect tolerance sign recovery robust fragile zero reference circular validation publication audit
---

# Design conclusion-recovery rules

A conclusion-recovery rule translates branch-level endpoint estimates into a **predeclared recovery criterion**.

Use one only when the reference effect itself is scientifically defensible.

For many ordinary real-data analyses, descriptive robustness reporting is preferable to manufacturing a categorical target.

## 1. Start with the reference effect, not the tolerance

Ask:

> What independently defined scientific quantity are the specification estimates supposed to recover?

Strongest settings include:

- synthetic known truth;
- benchmark truth generated independently from the evaluated estimates;
- an external/preregistered reference fixed before robustness inspection.

Weak:

> the mean or median of the same robustness results.

That is circular.

## 2. Record the reference provenance

A useful record states:

- numeric reference value;
- endpoint/unit;
- source;
- timing;
- whether it is known truth or an independently justified real-data target;
- why it can serve as the recovery target.

The package can preserve this record.

It cannot decide that the reference is scientifically valid.

## 3. Declare at least one tolerance

`ConclusionRule` requires:

- relative tolerance;
- absolute tolerance;
- or both.

No tolerance means there is no branch-level error criterion and the runtime raises.

### Absolute tolerance

Useful when an error bound has meaning in the endpoint's own unit.

Example:

> ±5 ms.

### Relative tolerance

Useful when proportional deviation from a non-zero target is meaningful.

Example:

> within 10% of the reference.

Do not choose the tolerance after seeing the error distribution.

## 4. When both tolerances exist, both must pass

Suppose:

```text
reference = 10
estimate = 12
absolute tolerance = 3
relative tolerance = 0.10
```

Absolute error = 2, so the absolute rule passes.

Relative error = 0.20, so the relative rule fails.

The branch is **not tolerance-recovered** because both declared tolerances must be satisfied.

Do not interpret multiple tolerances as alternatives unless you explicitly redesign the scientific rule outside this API.

## 5. Zero reference effects require absolute tolerance

When the reference effect is zero:

- relative error is undefined;
- effect ratio is undefined;
- sign recovery is treated as recovered;
- relative tolerance cannot be evaluated.

Use an absolute tolerance if zero is the scientifically defined reference.

Do not add an arbitrary non-zero epsilon merely to make relative error calculable.

## 6. Sign recovery is separate from tolerance recovery

For a non-zero reference:

```text
reference = +10
estimate = -10
```

Even if a very wide tolerance accepts the absolute/relative error, `require_sign=True` rejects the branch because the direction differs.

With `require_sign=False`, only the tolerance rule is evaluated.

Choose this deliberately.

A same-sign rule is not a significance test.

## 7. Explicitly declare the across-specification threshold

`minimum_recovery_fraction` determines the summary classification.

If:

```text
recovered branches = 4 / 5
recovery fraction = 0.80
minimum = 0.80
```

the summary is `robust` because the fraction is **at or above** the threshold.

If the minimum is `0.81`, the same evidence becomes `fragile`.

This is why the threshold must be fixed independently of the observed recovery fraction.

## 8. Do not confuse Python defaults with scientific recommendations

The runtime dataclass currently has software defaults for:

- `require_sign=True`;
- `minimum_recovery_fraction=0.90`.

Those are API defaults.

They are **not universal scientific recommendations**.

The Conclusion Rule Design Center intentionally requires both choices explicitly so a documentation-side declaration cannot inherit them silently.

## 9. Branch recovery and summary classification are different layers

### Branch layer

`conclusion_recovery_table()` determines, per represented specification:

- absolute error;
- relative error;
- effect ratio;
- sign recovery;
- tolerance recovery;
- conclusion recovery.

### Summary layer

`summarize_conclusion_recovery()` aggregates the represented branch indicators and compares the resulting recovery fraction with the declared minimum.

Do not report only the summary classification.

Preserve the branch table.

## 10. Execution completeness still matters

A recovery fraction computed from successful represented rows does not make unresolved valid branches disappear.

Before applying the conclusion rule, reconstruct:

- declared specifications;
- valid specifications;
- successful finite estimates;
- valid failures;
- non-finite endpoints;
- not-run branches.

If the valid denominator is incomplete, report that limitation before presenting the recovery classification.

## 11. Classification is conditional, not universal

`robust` means:

> recovery fraction met or exceeded the declared threshold for the supplied recovery table and rule.

`fragile` means:

> recovery fraction was below the declared threshold for the supplied recovery table and rule.

Neither label means:

- statistically significant / non-significant;
- scientifically important / unimportant;
- universally robust / universally invalid;
- all omitted analytical choices are irrelevant.

## 12. Keep frozen validation labels separate

GazeAudit's frozen outcomes:

- `incomplete`;
- `robust_negative`;
- `materially_fragile`;

belong to specific frozen protocols.

They are not aliases for generic `ConclusionRule` classifications.

Do not map a new `robust` summary onto `robust_negative`.

## 13. Reviewer-requested conclusion rules need temporal provenance

If a reviewer asks for a recovery criterion after seeing the original result:

- record the request;
- preserve the original evidence layer;
- label the new rule as post-review;
- do not call it preregistered;
- keep the submitted and amended analyses distinct.

A useful later analysis does not become prespecified retroactively.

## 14. Bind the rule into publication evidence

`build_conclusion_audit_bundle()` can bind:

- results;
- reference effect;
- rule;
- endpoint;
- source description;
- metadata;
- deterministic manifest/fingerprints.

This improves reconstructability.

It does not validate the scientific thresholds.

## 15. Report the rule before the classification

Preferred Methods order:

1. reference effect and provenance;
2. tolerance(s);
3. sign requirement;
4. minimum recovery fraction;
5. specification denominator;
6. software/API identity.

Then Results can report:

- branch recovery counts;
- recovery fraction;
- summary classification;
- error summaries;
- execution completeness.

## 16. Reporting examples

### Methods

> Before inspecting robustness outcomes, we defined the reference effect as [value, unit], based on [independent source]. Branch-level recovery required [absolute/relative/both] tolerance of [criterion] and [did/did not] additionally require matching effect direction. The overall rule required at least [fraction] of represented valid specifications to satisfy branch-level recovery.

### Results

> [R] of [N] represented specifications recovered the declared target (recovery fraction = [x]). This [met/did not meet] the predeclared minimum of [threshold], producing the rule-based classification [robust/fragile]. Median absolute error was [x] and maximum absolute error was [y].

### Limitation

> The classification is conditional on the reference effect, tolerance rule, sign policy, recovery threshold, represented specification space, and execution completeness. It does not represent statistical significance, posterior probability, or robustness to untested analysis choices.

## 17. Common mistakes

### Circular reference

**Mistake:** derive the target from the same results.

**Repair:** use independent known truth/reference or remain descriptive.

### Post hoc threshold

**Mistake:** choose a tolerance that makes the observed fraction pass.

**Repair:** preserve the original descriptive result and declare any later rule as post hoc.

### Relative tolerance at zero

**Mistake:** use percentage error relative to zero.

**Repair:** use scientifically justified absolute error.

### Hidden Python defaults

**Mistake:** instantiate `ConclusionRule(relative_tolerance=...)` and treat inherited default sign/fraction values as scientifically justified.

**Repair:** pass all scientific arguments explicitly and document them.

### Classification-only reporting

**Mistake:** report “robust” without reference, tolerance, denominator, or recovery fraction.

**Repair:** report the full rule and evidence.

## 18. Pre-execution checklist

- [ ] endpoint fixed;
- [ ] reference effect independently defined;
- [ ] reference provenance archived;
- [ ] reference unit matches endpoint;
- [ ] at least one tolerance justified;
- [ ] dual-tolerance semantics understood;
- [ ] zero-reference compatibility checked;
- [ ] sign rule explicit;
- [ ] minimum recovery fraction explicit;
- [ ] timing recorded;
- [ ] valid denominator reconstructable;
- [ ] interpretation boundary written;
- [ ] frozen protocol labels kept separate.

## API routes

- [`ConclusionRule`]({{ '/docs/reference/api-pathways/#api-conclusionrule' | relative_url }})
- [`summarize_conclusion_recovery()`]({{ '/docs/reference/api-pathways/#api-summarize-conclusion-recovery' | relative_url }})
- [`build_conclusion_audit_bundle()`]({{ '/docs/reference/api-pathways/#api-build-conclusion-audit-bundle' | relative_url }})
- [`verify_publication_audit_bundle()`]({{ '/docs/reference/api-pathways/#api-verify-publication-audit-bundle' | relative_url }})
- [Conclusion Rule Design Center]({{ '/docs/conclusion-rule/' | relative_url }})
- [Publication audit guide]({{ '/docs/guides/publication-audits/' | relative_url }})

## Worked exercise

Continue to [Conclusion-rule edge cases]({{ '/docs/examples/conclusion-rule-edge-cases/' | relative_url }}) for deterministic examples covering dual tolerances, sign recovery, zero-reference error handling, and threshold equality.
