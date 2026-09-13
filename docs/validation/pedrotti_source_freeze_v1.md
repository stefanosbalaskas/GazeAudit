# Pedrotti endpoint-blind source freeze v1

## Purpose

This tranche implements the source-readiness gate for the frozen Pedrotti/de Chambrier
sampling-rate and missingness sensitivity protocol. Its purpose is to establish an
immutable, independently checkable identity for the public source bytes and the
endpoint-blind structural facts required by the protocol **before any scientific
sensitivity result is evaluated**.

Frozen protocol fingerprint:
`efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5`.

The source is Zenodo record `7962917`, DOI `10.5281/zenodo.7962917`, version `v1`.
The source contract contains the complete published file set: `01.txt` through
`36.txt` plus `readme.txt`.

## Source identity

`pedrotti_source.py` verifies the exact file set and every MD5 value embedded in the
frozen protocol, then records a SHA-256 digest and byte size for every source file.
The deterministic source manifest binds the protocol identity, Zenodo record/version,
and the exact all-participant download contract.

The verifier fails closed if the file set, published MD5 identity, SHA-256 syntax,
source count, download contract, protocol fingerprint, or Zenodo identity changes.

## Endpoint-blind structural intake

The intake checks only facts required to establish source compatibility:

- exactly 36 zero-padded participant files and exactly 96 trials per participant;
- the exact nine-column published schema frozen in the protocol;
- finite, strictly increasing timestamps within every trial;
- one stable `TrialTextShown` label per trial;
- exactly one eye side containing finite published gaze for each participant; and
- at least one short-numeric and one long-numeric trial under the frozen lexical
  numeral classifier.

The resulting summary records row/trial counts, numeric-condition counts, eye-side
counts, and participant identities. It explicitly records
`scientific_endpoint_evaluated: false`. The artifact verifier revalidates these
semantic invariants in addition to cryptographic file checks, so a rewritten summary
cannot become valid merely by recomputing checksums.

This layer does **not** compute the frozen long-minus-short endpoint, lower-rate
perturbations, added-missingness perturbations, recovery fractions, relative
sensitivity, or an overall robustness classification.

## Resumable Zenodo transport

`pedrotti_fetch.py` uses the canonical Zenodo REST record endpoint as its primary
metadata source and requires its filename and MD5 set to equal the frozen protocol
before downloading any source file. Existing files are retained only when their MD5
already matches. Mismatched or partial files are removed before retry, downloads are
written to temporary `.part` paths, and a file is atomically promoted only after its
MD5 matches the frozen identity.

If the REST record endpoint fails with a transport-level error, acquisition may fall
back to the public Zenodo record page for the **same frozen record only**. The fallback
parses the published file table and is accepted only when it independently binds the
frozen DOI, exact record-specific download paths, complete filename set, and every
published MD5 value. Structural or identity failures from a successful REST response
do not fall back. The resulting source bytes remain subject to the same frozen MD5
contract and deterministic source-manifest verification.

Only HTTPS URLs hosted by `zenodo.org` or `www.zenodo.org` are accepted, and content
links must match one of the two record-specific Zenodo file URL shapes used by the REST
API or public record page. The transport reports which metadata path was used and does
not call a scientific endpoint.

## Source-freeze envelope

`pedrotti_freeze.py` wraps a verified intake in a second checksummed provenance layer.
The envelope binds:

- the source-manifest and intake-artifact fingerprints;
- exact GazeAudit execution commit and workflow identity;
- GitHub Actions run identity;
- the frozen protocol and Zenodo record;
- installed GazeAudit package version;
- Python/platform/runner identity; and
- a complete sorted `pip freeze` dependency snapshot.

The outer manifest and every nested file are SHA-256 protected. Verification also
rejects scientific-result fields, preserving the endpoint-blind boundary.

## Controlled workflow

`.github/workflows/pedrotti-source-freeze.yml` is manual (`workflow_dispatch`) and can
execute only from `main`. It recreates the pinned Python 3.12.14 / NumPy 2.5.3 /
pandas 2.3.3 intake environment, downloads and verifies the exact public source,
builds the structural intake, captures the dependency environment, builds and
verifies the outer freeze, and uploads the immutable archive. The transfer log records
whether verified metadata came from `api` or the fail-closed `record_html` fallback.

The workflow follows **archive before reveal**: the source-freeze artifact is uploaded
successfully before the workflow prints the source/freeze fingerprints. The workflow
contains no scientific sensitivity execution step.

## Qualification boundary

CI uses synthetic source fixtures to test the intake/freeze semantics, checksum
binding, semantic tamper resistance, REST-to-record-page metadata fallback, exact
record-specific URL constraints, trusted-link rules, and archive-before-reveal workflow
order. CI does not download or analyze the real Pedrotti/de Chambrier dataset.

At merge time, no real-data endpoint, perturbation estimate, recovery fraction, or
robustness classification has been evaluated by this tranche. After exact-main
certification, the next permitted action is the manually triggered source-freeze run.
Only after that run is independently verified and source-locked may a later tranche
prepare the first outcome-bearing scientific execution.
