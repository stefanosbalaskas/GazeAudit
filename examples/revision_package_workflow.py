"""Create and validate a synthetic reviewer-revision provenance package."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from gazeaudit.revision_package import (
    validate_revision_package,
    write_revision_package_skeleton,
)

OUTPUT = Path("revision-package-demo")


def main() -> None:
    """Run a deterministic scaffold -> validate -> break -> repair demonstration."""

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    manifest = write_revision_package_skeleton(
        OUTPUT,
        project_slug="synthetic-review-study",
        review_round=1,
    )
    print("created", manifest["schema"], manifest["manifest_fingerprint"])

    valid = validate_revision_package(OUTPUT)
    print(json.dumps(valid, indent=2, sort_keys=True))

    governed_marker = OUTPUT / "revision/round-1/amendments/README.md"
    governed_marker.unlink()
    broken = validate_revision_package(OUTPUT)
    print(json.dumps(broken, indent=2, sort_keys=True))

    write_revision_package_skeleton(
        OUTPUT,
        project_slug="synthetic-review-study",
        review_round=1,
        overwrite=True,
    )
    repaired = validate_revision_package(OUTPUT)
    print(json.dumps(repaired, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
