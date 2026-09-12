# Korthals protocol-v2 memory-bounded source intake

## Scope

This change is an endpoint-blind execution-topology hardening only. It does **not**
change the Korthals protocol-v2 scientific specification, source cohort, author
exclusion, blink handling, 50-Hz sampling rule, validation mapping, AOI geometry,
matched-cell definition, missingness rule, Monte Carlo settings, or interpretation
rule.

## Trigger

`korthals-source-freeze` run `34717445222` was executed on certified main
`59350945f4d68fd074f34aca2be59f072e2862bb`. Both attempt 1 (job `103617111619`)
and attempt 2 (job `103619126663`) successfully completed the checksum-verified
112-file OSF transfer and were then terminated by a GitHub-hosted runner shutdown
signal while the endpoint-blind source-intake step was still preprocessing
participants. No source-freeze artifact was uploaded in either attempt, and no
scientific AOI endpoint, Monte Carlo result, effect estimate, sign probability, or
classification was executed or inspected.

The workflow itself already declared `timeout-minutes: 180`, so the observed shutdown
was not the repository's configured job timeout. The pre-existing intake retained each
participant's full-resolution canonical aligned table until every participant had been
preprocessed and only then reduced the combined source to the frozen 50-Hz
representation. That topology creates unnecessary peak memory pressure even though the
protocol-v2 preparation operations are participant-separable.

## Hardening

The controlled CLI now uses a memory-bounded companion intake:

1. discover and checksum the same complete published source tree;
2. process participants in the same deterministic source-manifest order;
3. for one participant at a time, run the unchanged companion `Participant` +
   `OriginalPreprocessor` path, lexical participant-identity validation, exact
   target-master alignment, tutorial scoping, raw validation extraction, and the
   unchanged protocol-v2 preparation;
4. retain only that participant's already-frozen 50-Hz prepared rows and validation
   groups before releasing its full-resolution companion state;
5. deterministically combine participant-local prepared objects and reconstruct the
   same global source identity, participant/trial fingerprints, zero-finite-trial
   records, and symmetric missing-cell records; and
6. validate global endpoint-weight structure without evaluating AOI membership or any
   scientific endpoint.

A synthetic regression test compares the streamed participant-wise result directly
against monolithic protocol-v2 preparation, including the prepared data frame,
validation-group frame, and complete source-identity object. The fixture includes a
zero-finite trial so the protocol-v2 symmetric matched-cell removal is exercised in
the equivalence test.

## Scientific boundary

The protocol-v2 fingerprint remains
`1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`.
No protocol JSON is modified. No missing gaze is recovered or interpolated. No target
scientific outcome has been evaluated or inspected.
