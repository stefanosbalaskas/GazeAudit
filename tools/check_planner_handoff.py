from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load_json(path: Path, label: str) -> list[dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated {label}: {exc}") from exc
    if not isinstance(payload, list):
        raise SystemExit(f"generated {label} must be a list, got {type(payload).__name__}")
    return payload


def _route_target(site_root: Path, url: str, baseurl: str) -> Path:
    path = url
    if baseurl and path.startswith(baseurl + "/"):
        path = path[len(baseurl) :]
    path = path.lstrip("/")
    target = site_root / path
    return target / "index.html" if url.endswith("/") else target


def verify_planner_handoff(site_root: Path, *, baseurl: str = "/GazeAudit") -> None:
    workflows = _load_json(site_root / "assets/planner-workflow-index.json", "planner workflow index")
    methods = _load_json(site_root / "assets/method-index.json", "method index")
    planner = _load_json(site_root / "assets/planner-index.json", "planner index")

    if len(workflows) != 3:
        raise SystemExit(f"expected exactly 3 planner workflow handoffs, got {len(workflows)}")

    method_ids = {
        item.get("id")
        for item in methods
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }
    planner_methods = {
        method_id
        for item in planner
        if isinstance(item, dict) and isinstance(item.get("methods"), list)
        for method_id in item["methods"]
        if isinstance(method_id, str) and method_id
    }

    required = {"id", "title", "label", "description", "url", "methods"}
    workflow_ids: set[str] = set()
    mapped_methods: list[str] = []
    failures: list[str] = []

    for position, item in enumerate(workflows):
        if not isinstance(item, dict):
            failures.append(f"workflow {position}: expected object")
            continue
        missing = required.difference(item)
        if missing:
            failures.append(f"workflow {position}: missing keys {sorted(missing)}")
            continue

        workflow_id = item["id"]
        if not isinstance(workflow_id, str) or not workflow_id:
            failures.append(f"workflow {position}: invalid id {workflow_id!r}")
        elif workflow_id in workflow_ids:
            failures.append(f"workflow {position}: duplicate id {workflow_id!r}")
        else:
            workflow_ids.add(workflow_id)

        for field in ("title", "label", "description"):
            value = item[field]
            if not isinstance(value, str) or not value.strip():
                failures.append(f"workflow {position}: {field} must be a non-empty string")

        url = item["url"]
        if not isinstance(url, str) or not url.startswith("/docs/workflows/") or not url.endswith("/"):
            failures.append(f"workflow {position}: invalid workflow url {url!r}")
        elif not _route_target(site_root, url, baseurl).is_file():
            failures.append(f"workflow {position}: unresolved workflow url {url!r}")

        workflow_methods = item["methods"]
        if not isinstance(workflow_methods, list) or not workflow_methods or not all(
            isinstance(method_id, str) and method_id for method_id in workflow_methods
        ):
            failures.append(f"workflow {position}: methods must be a non-empty string list")
            continue
        mapped_methods.extend(workflow_methods)
        unknown = set(workflow_methods).difference(method_ids)
        if unknown:
            failures.append(f"workflow {position}: unknown method ids {sorted(unknown)}")

    counts = Counter(mapped_methods)
    duplicated = sorted(method_id for method_id, count in counts.items() if count != 1)
    if duplicated:
        failures.append(f"planner methods must map to exactly one workflow: {duplicated}")

    if set(mapped_methods) != planner_methods:
        missing = sorted(planner_methods.difference(mapped_methods))
        extra = sorted(set(mapped_methods).difference(planner_methods))
        failures.append(f"workflow coverage mismatch: missing={missing}, extra={extra}")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"planner handoff failures ({len(failures)}):\n{preview}{extra}")

    print(
        "PLANNER HANDOFF VERIFY: PASS "
        f"({len(workflows)} workflows, {len(planner_methods)} planner methods)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify generated Audit Planner workflow handoff")
    parser.add_argument("site_root", nargs="?", default="_site", type=Path)
    parser.add_argument("--baseurl", default="/GazeAudit")
    args = parser.parse_args()
    verify_planner_handoff(args.site_root, baseurl=args.baseurl)


if __name__ == "__main__":
    main()
