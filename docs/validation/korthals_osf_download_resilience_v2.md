# Korthals protocol-v2 OSF download resilience

## Scope

This note records an **endpoint-blind transport hardening only** for the frozen
Korthals et al. (2026) source intake. It does not change the protocol-v2 cohort,
task-trial scope, preprocessing, 50 Hz sampling rule, AOI, pairing, validation
model, Monte Carlo seed/model, endpoint, or classification rule.

The frozen public source remains OSF project `zx7hc`, requested through the
companion implementation as:

```python
download_osf_data(
    raw_clean="both",
    train_test="both",
    participants="all",
    overwrite=False,
)
```

## Triggering infrastructure evidence

`korthals-source-freeze #7` ran on exact certified GazeAudit commit
`0f74b817962f9ff33d5f6a33e34686dfcf661172`.

- Attempt 1 downloaded the complete OSF source and then entered the endpoint-blind
  protocol-v2 intake. The hosted runner later received a shutdown signal and the
  process exited 143. There was no GazeAudit scientific/data traceback.
- The exact same failed job was rerun on the same certified commit. Attempt 2
  reached 73/112 OSF files and then the companion download failed in
  `osfclient.models.file.File.write_to` with HTTP 403. Source intake never began
  on that attempt.

No Korthals scientific endpoint, effect estimate, Monte Carlo result, sign
probability, or classification was executed or inspected in either attempt.

## Why an internal retry must verify files

The frozen companion downloader writes each remote object directly to its final
`data/...` path. With `overwrite=False`, any existing path is skipped without a
local checksum check. Therefore a transfer exception after the destination file
has been opened can leave a partial final-path file that a naive in-process retry
would incorrectly skip.

OSF's documented `osfclient` update/resume workflow similarly relies on remote
file checksums to avoid unnecessarily downloading already-valid local files. The
GazeAudit wrapper preserves the companion's exact selection and path mapping but
adds a fail-closed checksum boundary before allowing a retry.

## Frozen transport-hardening rule

Before the first companion download, GazeAudit inventories the public OSF source
and records each remote path, the exact companion destination, the published MD5
checksum, and the published SHA-256 checksum when exposed by OSF. Duplicate paths
or destinations and missing/invalid required MD5 identities fail closed.

For each attempt:

1. Existing destination files are retained only if their published checksum(s)
   match exactly; mismatched or partial regular files are deleted.
2. The unmodified companion download contract above is invoked.
3. Only the companion transport `RuntimeError` is retryable. Scientific,
   identity, filesystem, and checksum failures are not converted into retries.
4. Before a retry, the public OSF inventory must still equal the baseline
   inventory exactly. Verified completed files are retained; the failed partial
   file is removed; exponential backoff is applied.
5. After a nominally successful download, the public OSF inventory is read again
   and must still equal the baseline. Every expected local file must exist and
   match the remote checksum identity before source intake is allowed to start.

The existing endpoint-blind GazeAudit source manifest subsequently computes the
full frozen SHA-256 identity of the downloaded source. Thus this transport layer
adds resumability without changing which published bytes are admitted.

## Scientific boundary

This change is justified solely by two external execution failures (hosted-runner
shutdown and OSF HTTP 403) observed before a source-freeze artifact existed. It
must not be used to alter any scientific choice after an endpoint result is
revealed. At the time of this amendment, no Korthals endpoint outcome had been
executed or inspected.
