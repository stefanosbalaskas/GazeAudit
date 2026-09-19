from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class _ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"a", "link"} and values.get("href"):
            self.references.append(("href", values["href"] or ""))
        if tag in {"img", "script", "source"} and values.get("src"):
            self.references.append(("src", values["src"] or ""))


def _candidate_targets(site_root: Path, source: Path, raw_reference: str, baseurl: str) -> list[Path]:
    split = urlsplit(raw_reference)
    if split.scheme or split.netloc or raw_reference.startswith(("mailto:", "tel:", "javascript:")):
        return []

    path = unquote(split.path)
    if not path:
        return []

    if path.startswith(baseurl + "/") or path == baseurl:
        path = path[len(baseurl) :]

    if path.startswith("/"):
        relative = path.lstrip("/")
        target = site_root / relative
    else:
        target = source.parent / path

    if path.endswith("/"):
        return [target / "index.html"]
    if target.suffix:
        return [target]
    return [target, target.with_suffix(".html"), target / "index.html"]


def _resolves(site_root: Path, source: Path, reference: str, baseurl: str) -> bool:
    candidates = _candidate_targets(site_root, source, f"{baseurl}{reference}", baseurl)
    return bool(candidates) and any(
        candidate.resolve().is_relative_to(site_root.resolve()) and candidate.exists()
        for candidate in candidates
    )


def _verify_search_index(site_root: Path, *, baseurl: str) -> None:
    search_path = site_root / "assets/search-index.json"
    try:
        index = json.loads(search_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated search index: {exc}") from exc

    if not isinstance(index, list) or len(index) < 20:
        raise SystemExit(
            "unexpected documentation search index: "
            f"{type(index).__name__}, entries={len(index) if isinstance(index, list) else 'n/a'}"
        )

    required_keys = {"title", "category", "url", "description", "keywords"}
    urls: set[str] = set()
    failures: list[str] = []
    source = site_root / "index.html"
    for position, item in enumerate(index):
        if not isinstance(item, dict):
            failures.append(f"entry {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"entry {position}: missing keys {sorted(missing)}")
            continue
        url = item["url"]
        if not isinstance(url, str) or not url.startswith("/docs/"):
            failures.append(f"entry {position}: invalid url {url!r}")
            continue
        if url in urls:
            failures.append(f"entry {position}: duplicate url {url!r}")
        urls.add(url)
        candidates = _candidate_targets(site_root, source, f"{baseurl}{url}", baseurl)
        if not candidates or not any(candidate.exists() for candidate in candidates):
            candidate_text = ", ".join(str(path.relative_to(site_root)) for path in candidates)
            failures.append(f"entry {position}: {url!r} -> [{candidate_text}]")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"search index target failures ({len(failures)}):\n{preview}{extra}")


def _verify_method_index(site_root: Path, *, baseurl: str) -> None:
    method_path = site_root / "assets/method-index.json"
    try:
        methods = json.loads(method_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated method index: {exc}") from exc

    if not isinstance(methods, list) or len(methods) != 10:
        raise SystemExit(
            "unexpected method catalog: "
            f"{type(methods).__name__}, entries={len(methods) if isinstance(methods, list) else 'n/a'}"
        )

    required_keys = {
        "id",
        "phase",
        "phase_key",
        "title",
        "question",
        "purpose",
        "functions",
        "guide_url",
        "guide_label",
        "example_url",
        "example_label",
        "plot_url",
        "plot_label",
        "evidence_url",
        "evidence_label",
        "evidence_note",
        "keywords",
    }
    expected_phases = {
        "preflight",
        "governance",
        "measurement",
        "robustness",
        "sensitivity",
        "benchmarking",
        "evidence",
        "integration",
    }
    ids: set[str] = set()
    phases: set[str] = set()
    failures: list[str] = []
    source = site_root / "docs/methods/index.html"

    for position, item in enumerate(methods):
        if not isinstance(item, dict):
            failures.append(f"method {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"method {position}: missing keys {sorted(missing)}")
            continue

        method_id = item["id"]
        if not isinstance(method_id, str) or not method_id:
            failures.append(f"method {position}: invalid id {method_id!r}")
        elif method_id in ids:
            failures.append(f"method {position}: duplicate id {method_id!r}")
        else:
            ids.add(method_id)

        phase = item["phase_key"]
        if not isinstance(phase, str) or phase not in expected_phases:
            failures.append(f"method {position}: invalid phase_key {phase!r}")
        else:
            phases.add(phase)

        functions = item["functions"]
        if not isinstance(functions, list) or not functions or not all(isinstance(name, str) and name for name in functions):
            failures.append(f"method {position}: functions must be a non-empty string list")

        for field in ("guide_url", "example_url", "plot_url"):
            reference = item[field]
            if not isinstance(reference, str) or not reference.startswith("/"):
                failures.append(f"method {position}: invalid {field} {reference!r}")
            elif not _resolves(site_root, source, reference, baseurl):
                failures.append(f"method {position}: unresolved {field} {reference!r}")

        evidence = item["evidence_url"]
        if evidence:
            if not isinstance(evidence, str) or not evidence.startswith("/"):
                failures.append(f"method {position}: invalid evidence_url {evidence!r}")
            elif not _resolves(site_root, source, evidence, baseurl):
                failures.append(f"method {position}: unresolved evidence_url {evidence!r}")
            if not item["evidence_label"]:
                failures.append(f"method {position}: evidence URL requires evidence_label")

    if phases != expected_phases:
        failures.append(f"method phases mismatch: expected {sorted(expected_phases)}, got {sorted(phases)}")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"method index failures ({len(failures)}):\n{preview}{extra}")


def _verify_example_index(site_root: Path, *, baseurl: str) -> None:
    example_path = site_root / "assets/example-index.json"
    try:
        examples = json.loads(example_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated example index: {exc}") from exc

    if not isinstance(examples, list) or len(examples) < 20:
        raise SystemExit(
            "unexpected example catalog: "
            f"{type(examples).__name__}, entries={len(examples) if isinstance(examples, list) else 'n/a'}"
        )

    required_keys = {
        "title",
        "url",
        "description",
        "data",
        "focus",
        "reuse",
        "output",
        "boundary",
    }
    allowed_data = {
        "Synthetic",
        "Demo or user data",
        "Software-only",
        "Documentation-only",
    }
    allowed_focus = {
        "Data & QC",
        "Measurement uncertainty",
        "Robustness & sensitivity",
        "Interpretation & reporting",
        "Documentation & API",
        "Environment",
        "Project lifecycle",
        "Peer review & publication",
        "Reproducibility",
    }
    urls: set[str] = set()
    failures: list[str] = []
    source = site_root / "docs/examples/catalog/index.html"

    for position, item in enumerate(examples):
        if not isinstance(item, dict):
            failures.append(f"example {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"example {position}: missing keys {sorted(missing)}")
            continue

        for field in required_keys:
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(f"example {position}: {field} must be a non-empty string")

        url = item["url"]
        if isinstance(url, str):
            if url in urls:
                failures.append(f"example {position}: duplicate url {url!r}")
            urls.add(url)
            if not url.startswith("/docs/examples/"):
                failures.append(f"example {position}: invalid url {url!r}")
            elif not _resolves(site_root, source, url, baseurl):
                failures.append(f"example {position}: unresolved url {url!r}")

        if item["data"] not in allowed_data:
            failures.append(f"example {position}: invalid data context {item['data']!r}")
        if item["focus"] not in allowed_focus:
            failures.append(f"example {position}: invalid focus {item['focus']!r}")

    if source.is_file():
        catalog_html = source.read_text(encoding="utf-8")
        rendered_cards = catalog_html.count("data-example-card")
        if rendered_cards != len(examples):
            failures.append(
                "example catalog card count mismatch: "
                f"index={len(examples)}, rendered={rendered_cards}"
            )
    else:
        failures.append("example catalog page is missing from generated site")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"example index failures ({len(failures)}):\n{preview}{extra}")


def _verify_qc_issue_reference(site_root: Path) -> None:
    issue_path = site_root / "assets/qc-issue-reference.json"
    try:
        issues = json.loads(issue_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated QC issue reference: {exc}") from exc

    expected_codes = {
        "coordinate_nonfinite",
        "timestamp_nonfinite",
        "identifier_missing",
        "timestamp_duplicate",
        "timestamp_decreasing",
    }
    expected_detail_codes = {
        "x_missing",
        "x_infinite",
        "y_missing",
        "y_infinite",
        "timestamp_missing",
        "timestamp_infinite",
        "participant_missing",
        "trial_missing",
        "timestamp_duplicate",
        "timestamp_decreasing",
    }
    required = {
        "issue_code",
        "label",
        "scope",
        "report_field",
        "summary",
        "detail_codes",
        "inspect",
        "possible_causes",
        "not_infer",
        "next_step",
    }

    if not isinstance(issues, list) or len(issues) != 5:
        raise SystemExit(
            "unexpected QC issue catalog: "
            f"{type(issues).__name__}, entries={len(issues) if isinstance(issues, list) else 'n/a'}"
        )

    failures: list[str] = []
    issue_codes: set[str] = set()
    detail_codes: set[str] = set()

    for position, item in enumerate(issues):
        if not isinstance(item, dict):
            failures.append(f"issue {position}: expected object")
            continue
        missing = required.difference(item)
        if missing:
            failures.append(f"issue {position}: missing keys {sorted(missing)}")
            continue

        issue_code = item["issue_code"]
        if not isinstance(issue_code, str) or not issue_code:
            failures.append(f"issue {position}: invalid issue_code {issue_code!r}")
        elif issue_code in issue_codes:
            failures.append(f"issue {position}: duplicate issue_code {issue_code!r}")
        else:
            issue_codes.add(issue_code)

        if item["scope"] not in {"row", "group"}:
            failures.append(f"issue {position}: invalid scope {item['scope']!r}")

        for field in ("label", "report_field", "summary", "not_infer", "next_step"):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(f"issue {position}: {field} must be a non-empty string")

        for field in ("inspect", "possible_causes"):
            values = item[field]
            if not isinstance(values, list) or not values or not all(
                isinstance(value, str) and value.strip() for value in values
            ):
                failures.append(f"issue {position}: {field} must be a non-empty string list")

        details = item["detail_codes"]
        if not isinstance(details, list) or not details:
            failures.append(f"issue {position}: detail_codes must be a non-empty list")
            continue
        for detail_position, detail in enumerate(details):
            if not isinstance(detail, dict):
                failures.append(
                    f"issue {position} detail {detail_position}: expected object"
                )
                continue
            code = detail.get("code")
            meaning = detail.get("meaning")
            if not isinstance(code, str) or not code:
                failures.append(
                    f"issue {position} detail {detail_position}: invalid code {code!r}"
                )
            else:
                detail_codes.add(code)
            if not isinstance(meaning, str) or not meaning.strip():
                failures.append(
                    f"issue {position} detail {detail_position}: missing meaning"
                )

    if issue_codes != expected_codes:
        failures.append(
            f"QC issue codes mismatch: expected {sorted(expected_codes)}, got {sorted(issue_codes)}"
        )
    if detail_codes != expected_detail_codes:
        failures.append(
            "QC detail codes mismatch: "
            f"expected {sorted(expected_detail_codes)}, got {sorted(detail_codes)}"
        )

    clinic = site_root / "docs/reference/qc-issue-clinic/index.html"
    if not clinic.is_file():
        failures.append("QC issue clinic page is missing from generated site")
    else:
        rendered_cards = clinic.read_text(encoding="utf-8").count("data-qc-issue")
        if rendered_cards != len(issues):
            failures.append(
                "QC issue clinic card count mismatch: "
                f"index={len(issues)}, rendered={rendered_cards}"
            )

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"QC issue reference failures ({len(failures)}):\n{preview}{extra}")


def _verify_readiness_threshold_reference(site_root: Path) -> None:
    reference_path = site_root / "assets/readiness-threshold-reference.json"
    try:
        rules = json.loads(reference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"invalid generated readiness threshold reference: {exc}"
        ) from exc

    expected_names = {
        "max_coordinate_issue_fraction",
        "max_timestamp_issue_fraction",
        "max_identifier_issue_fraction",
        "max_duplicate_timestamp_fraction",
        "max_flagged_trial_fraction",
        "min_rows_per_trial",
        "min_trials_per_participant",
        "require_monotonic_time",
    }
    required = {
        "name",
        "label",
        "value_type",
        "scope",
        "comparator",
        "metric",
        "description",
        "interpretation",
        "boundary",
    }

    if not isinstance(rules, list) or len(rules) != 8:
        raise SystemExit(
            "unexpected readiness threshold catalog: "
            f"{type(rules).__name__}, "
            f"entries={len(rules) if isinstance(rules, list) else 'n/a'}"
        )

    failures: list[str] = []
    names: set[str] = set()
    type_counts = {"fraction": 0, "integer": 0, "boolean": 0}

    for position, item in enumerate(rules):
        if not isinstance(item, dict):
            failures.append(f"readiness rule {position}: expected object")
            continue

        missing = required.difference(item)
        if missing:
            failures.append(
                f"readiness rule {position}: missing keys {sorted(missing)}"
            )
            continue

        name = item["name"]
        if not isinstance(name, str) or not name:
            failures.append(
                f"readiness rule {position}: invalid name {name!r}"
            )
        elif name in names:
            failures.append(
                f"readiness rule {position}: duplicate name {name!r}"
            )
        else:
            names.add(name)

        value_type = item["value_type"]
        if value_type not in type_counts:
            failures.append(
                f"readiness rule {position}: invalid value_type {value_type!r}"
            )
        else:
            type_counts[value_type] += 1

        if item["scope"] not in {
            "trial",
            "participant",
            "trial + participant",
        }:
            failures.append(
                f"readiness rule {position}: invalid scope {item['scope']!r}"
            )

        for field in (
            "label",
            "comparator",
            "metric",
            "description",
            "interpretation",
            "boundary",
        ):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(
                    f"readiness rule {position}: "
                    f"{field} must be a non-empty string"
                )

        if value_type in {"fraction", "integer"}:
            step = item.get("input_step")
            if not isinstance(step, str) or not step:
                failures.append(
                    f"readiness rule {position}: numeric rule requires input_step"
                )

    if names != expected_names:
        failures.append(
            "readiness field names mismatch: "
            f"expected {sorted(expected_names)}, got {sorted(names)}"
        )

    expected_types = {"fraction": 5, "integer": 2, "boolean": 1}
    if type_counts != expected_types:
        failures.append(
            "readiness value-type counts mismatch: "
            f"expected {expected_types}, got {type_counts}"
        )

    center = site_root / "docs/readiness-policy/index.html"
    if not center.is_file():
        failures.append("readiness policy design center is missing")
    else:
        rendered = center.read_text(encoding="utf-8").count(
            "data-readiness-rule"
        )
        if rendered != len(rules):
            failures.append(
                "readiness rule card count mismatch: "
                f"index={len(rules)}, rendered={rendered}"
            )

    if failures:
        preview = "\n".join(failures[:30])
        extra = (
            ""
            if len(failures) <= 30
            else f"\n... and {len(failures) - 30} more"
        )
        raise SystemExit(
            f"readiness threshold reference failures "
            f"({len(failures)}):\n{preview}{extra}"
        )


def _verify_reporting_contract_reference(
    site_root: Path,
    *,
    baseurl: str,
) -> None:
    reference_path = site_root / "assets/reporting-contract-reference.json"
    try:
        contracts = json.loads(reference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"invalid generated reporting contract reference: {exc}"
        ) from exc

    expected_runtime_signals = {
        "pass",
        "review",
        "unassessed",
        "ready_under_policy",
        "review_under_policy",
    }
    allowed_layers = {
        "Structural QC",
        "Readiness",
        "Robustness",
        "Sensitivity",
        "Frozen evidence",
    }
    allowed_kinds = {
        "Runtime status",
        "Interpretation pattern",
        "Protocol-bound evidence label",
    }
    required = {
        "id",
        "layer",
        "kind",
        "signal",
        "runtime_source",
        "meaning",
        "denominator",
        "can_say",
        "cannot_say",
        "methods_template",
        "results_template",
        "limitation_template",
        "guide_url",
        "example_url",
        "api_anchor",
    }

    if not isinstance(contracts, list) or len(contracts) != 11:
        raise SystemExit(
            "unexpected reporting contract catalog: "
            f"{type(contracts).__name__}, "
            f"entries={len(contracts) if isinstance(contracts, list) else 'n/a'}"
        )

    failures: list[str] = []
    ids: set[str] = set()
    runtime_signals: set[str] = set()
    source = site_root / "docs/reporting-center/index.html"

    for position, item in enumerate(contracts):
        if not isinstance(item, dict):
            failures.append(f"reporting contract {position}: expected object")
            continue

        missing = required.difference(item)
        if missing:
            failures.append(
                f"reporting contract {position}: missing keys {sorted(missing)}"
            )
            continue

        contract_id = item["id"]
        if not isinstance(contract_id, str) or not contract_id:
            failures.append(
                f"reporting contract {position}: invalid id {contract_id!r}"
            )
        elif contract_id in ids:
            failures.append(
                f"reporting contract {position}: duplicate id {contract_id!r}"
            )
        else:
            ids.add(contract_id)

        if item["layer"] not in allowed_layers:
            failures.append(
                f"reporting contract {position}: invalid layer {item['layer']!r}"
            )
        if item["kind"] not in allowed_kinds:
            failures.append(
                f"reporting contract {position}: invalid kind {item['kind']!r}"
            )
        if item["kind"] == "Runtime status":
            runtime_signals.add(str(item["signal"]))

        for field in (
            "signal",
            "runtime_source",
            "meaning",
            "denominator",
            "can_say",
            "cannot_say",
            "methods_template",
            "results_template",
            "limitation_template",
        ):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(
                    f"reporting contract {position}: "
                    f"{field} must be a non-empty string"
                )

        for field in ("guide_url", "example_url"):
            reference = item[field]
            if not isinstance(reference, str) or not reference.startswith("/"):
                failures.append(
                    f"reporting contract {position}: invalid {field} {reference!r}"
                )
            elif not _resolves(site_root, source, reference, baseurl):
                failures.append(
                    f"reporting contract {position}: unresolved "
                    f"{field} {reference!r}"
                )

    if runtime_signals != expected_runtime_signals:
        failures.append(
            "reporting runtime signals mismatch: "
            f"expected {sorted(expected_runtime_signals)}, "
            f"got {sorted(runtime_signals)}"
        )

    if source.is_file():
        html = source.read_text(encoding="utf-8")
        rendered = html.count('class="reporting-contract-card"')
        if rendered != len(contracts):
            failures.append(
                "reporting contract card count mismatch: "
                f"index={len(contracts)}, rendered={rendered}"
            )
    else:
        failures.append("reporting center page is missing from generated site")

    if failures:
        preview = "\n".join(failures[:30])
        extra = (
            ""
            if len(failures) <= 30
            else f"\n... and {len(failures) - 30} more"
        )
        raise SystemExit(
            f"reporting contract reference failures "
            f"({len(failures)}):\n{preview}{extra}"
        )


def _verify_endpoint_contract_reference(site_root: Path) -> None:
    reference_path = site_root / "assets/endpoint-contract-reference.json"
    try:
        fields = json.loads(reference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"invalid generated endpoint contract reference: {exc}"
        ) from exc

    expected_names = {
        "endpoint_name",
        "scientific_quantity",
        "unit",
        "contrast_direction",
        "analysis_unit",
        "population_denominator",
        "missingness_policy",
        "nonfinite_policy",
        "transformation",
        "scientific_null",
        "required_inputs",
        "interpretation_boundary",
    }
    expected_required = expected_names - {
        "transformation",
        "scientific_null",
    }
    allowed_types = {"text", "textarea"}
    required_keys = {
        "name",
        "label",
        "value_type",
        "required",
        "purpose",
        "boundary",
    }

    if not isinstance(fields, list) or len(fields) != 12:
        raise SystemExit(
            "unexpected endpoint field catalog: "
            f"{type(fields).__name__}, "
            f"entries={len(fields) if isinstance(fields, list) else 'n/a'}"
        )

    failures: list[str] = []
    names: set[str] = set()
    required_names: set[str] = set()

    for position, item in enumerate(fields):
        if not isinstance(item, dict):
            failures.append(f"endpoint field {position}: expected object")
            continue

        missing = required_keys.difference(item)
        if missing:
            failures.append(
                f"endpoint field {position}: missing keys {sorted(missing)}"
            )
            continue

        name = item["name"]
        if not isinstance(name, str) or not name:
            failures.append(
                f"endpoint field {position}: invalid name {name!r}"
            )
        elif name in names:
            failures.append(
                f"endpoint field {position}: duplicate name {name!r}"
            )
        else:
            names.add(name)

        value_type = item["value_type"]
        if value_type not in allowed_types:
            failures.append(
                f"endpoint field {position}: invalid value_type {value_type!r}"
            )

        required = item["required"]
        if not isinstance(required, bool):
            failures.append(
                f"endpoint field {position}: required must be boolean"
            )
        elif required and isinstance(name, str):
            required_names.add(name)

        for field in ("label", "purpose", "boundary"):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(
                    f"endpoint field {position}: "
                    f"{field} must be a non-empty string"
                )

    if names != expected_names:
        failures.append(
            "endpoint field names mismatch: "
            f"expected {sorted(expected_names)}, got {sorted(names)}"
        )

    if required_names != expected_required:
        failures.append(
            "endpoint required fields mismatch: "
            f"expected {sorted(expected_required)}, "
            f"got {sorted(required_names)}"
        )

    center = site_root / "docs/endpoint-contract/index.html"
    if not center.is_file():
        failures.append("endpoint contract center is missing")
    else:
        rendered = center.read_text(encoding="utf-8").count(
            'class="endpoint-field-card"'
        )
        if rendered != len(fields):
            failures.append(
                "endpoint field card count mismatch: "
                f"index={len(fields)}, rendered={rendered}"
            )

    if failures:
        preview = "\n".join(failures[:30])
        extra = (
            ""
            if len(failures) <= 30
            else f"\n... and {len(failures) - 30} more"
        )
        raise SystemExit(
            f"endpoint contract reference failures "
            f"({len(failures)}):\n{preview}{extra}"
        )


def _verify_specification_declaration_reference(site_root: Path) -> None:
    reference_path = site_root / "assets/specification-declaration-reference.json"
    try:
        fields = json.loads(reference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"invalid generated specification declaration reference: {exc}"
        ) from exc

    expected_names = {
        "space_name",
        "scientific_question",
        "endpoint_reference",
        "decision_timing",
        "validity_mode",
        "validity_rule",
        "reference_specification",
        "failure_policy",
        "interpretation_boundary",
    }
    expected_required = {
        "space_name",
        "scientific_question",
        "endpoint_reference",
        "decision_timing",
        "validity_mode",
        "failure_policy",
        "interpretation_boundary",
    }
    allowed_types = {"text", "textarea", "choice"}
    required_keys = {
        "name",
        "label",
        "value_type",
        "required",
        "purpose",
        "boundary",
    }

    if not isinstance(fields, list) or len(fields) != 9:
        raise SystemExit(
            "unexpected specification declaration catalog: "
            f"{type(fields).__name__}, "
            f"entries={len(fields) if isinstance(fields, list) else 'n/a'}"
        )

    failures: list[str] = []
    names: set[str] = set()
    required_names: set[str] = set()

    for position, item in enumerate(fields):
        if not isinstance(item, dict):
            failures.append(
                f"specification declaration field {position}: expected object"
            )
            continue

        missing = required_keys.difference(item)
        if missing:
            failures.append(
                "specification declaration field "
                f"{position}: missing keys {sorted(missing)}"
            )
            continue

        name = item["name"]
        if not isinstance(name, str) or not name:
            failures.append(
                "specification declaration field "
                f"{position}: invalid name {name!r}"
            )
        elif name in names:
            failures.append(
                "specification declaration field "
                f"{position}: duplicate name {name!r}"
            )
        else:
            names.add(name)

        value_type = item["value_type"]
        if value_type not in allowed_types:
            failures.append(
                "specification declaration field "
                f"{position}: invalid value_type {value_type!r}"
            )

        required = item["required"]
        if not isinstance(required, bool):
            failures.append(
                "specification declaration field "
                f"{position}: required must be boolean"
            )
        elif required and isinstance(name, str):
            required_names.add(name)

        for field in ("label", "purpose", "boundary"):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(
                    "specification declaration field "
                    f"{position}: {field} must be a non-empty string"
                )

    if names != expected_names:
        failures.append(
            "specification declaration field names mismatch: "
            f"expected {sorted(expected_names)}, got {sorted(names)}"
        )

    if required_names != expected_required:
        failures.append(
            "specification declaration required fields mismatch: "
            f"expected {sorted(expected_required)}, "
            f"got {sorted(required_names)}"
        )

    center = site_root / "docs/specification-declaration/index.html"
    if not center.is_file():
        failures.append("specification declaration center is missing")
    else:
        html = center.read_text(encoding="utf-8")
        rendered = html.count('class="spec-declaration-field"')
        if rendered != 8:
            failures.append(
                "specification declaration field card count mismatch: "
                f"expected 8 rendered global fields, got {rendered}"
            )
        if 'id="spec-validity-mode"' not in html:
            failures.append(
                "specification declaration validity-mode select is missing"
            )

    if failures:
        preview = "\n".join(failures[:30])
        extra = (
            ""
            if len(failures) <= 30
            else f"\n... and {len(failures) - 30} more"
        )
        raise SystemExit(
            f"specification declaration reference failures "
            f"({len(failures)}):\n{preview}{extra}"
        )


def _verify_planner_index(site_root: Path, *, baseurl: str) -> None:
    planner_path = site_root / "assets/planner-index.json"
    method_path = site_root / "assets/method-index.json"
    try:
        planner = json.loads(planner_path.read_text(encoding="utf-8"))
        methods = json.loads(method_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated planner index: {exc}") from exc

    if not isinstance(planner, list) or len(planner) != 9:
        raise SystemExit(
            "unexpected planner catalog: "
            f"{type(planner).__name__}, entries={len(planner) if isinstance(planner, list) else 'n/a'}"
        )
    if not isinstance(methods, list):
        raise SystemExit("planner cannot verify against a non-list method catalog")

    method_ids = {
        item["id"] for item in methods
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    }
    required_keys = {"id", "group", "label", "prompt", "methods", "reason"}
    planner_ids: set[str] = set()
    referenced_methods: set[str] = set()
    failures: list[str] = []

    for position, item in enumerate(planner):
        if not isinstance(item, dict):
            failures.append(f"planner rule {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"planner rule {position}: missing keys {sorted(missing)}")
            continue

        rule_id = item["id"]
        if not isinstance(rule_id, str) or not rule_id:
            failures.append(f"planner rule {position}: invalid id {rule_id!r}")
        elif rule_id in planner_ids:
            failures.append(f"planner rule {position}: duplicate id {rule_id!r}")
        else:
            planner_ids.add(rule_id)

        for field in ("group", "label", "prompt", "reason"):
            if not isinstance(item[field], str) or not item[field].strip():
                failures.append(f"planner rule {position}: {field} must be a non-empty string")

        rule_methods = item["methods"]
        if not isinstance(rule_methods, list) or not rule_methods or not all(
            isinstance(method_id, str) and method_id for method_id in rule_methods
        ):
            failures.append(f"planner rule {position}: methods must be a non-empty string list")
            continue
        referenced_methods.update(rule_methods)

    missing_methods = referenced_methods.difference(method_ids)
    if missing_methods:
        failures.append(f"planner methods missing from governed catalog: {sorted(missing_methods)}")

    planner_page = site_root / "docs/planner/index.html"
    if not planner_page.is_file():
        failures.append("planner page is missing from generated site")
    elif not _resolves(site_root, planner_page, "/docs/methods/", baseurl):
        failures.append("planner cannot resolve the Method explorer route")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"planner index failures ({len(failures)}):\n{preview}{extra}")


def verify_site(site_root: Path, *, baseurl: str = "/GazeAudit") -> None:
    if not site_root.is_dir():
        raise SystemExit(f"site root does not exist: {site_root}")

    required = [
        "index.html",
        "docs/index.html",
        "docs/documentation-map/index.html",
        "docs/data-contract/index.html",
        "docs/planner/index.html",
        "docs/methods/index.html",
        "docs/plots/index.html",
        "docs/reference/index.html",
        "docs/reference/api-map/index.html",
        "docs/reference/api-pathways/index.html",
        "docs/reference/qc-issue-clinic/index.html",
        "docs/readiness-policy/index.html",
        "docs/reporting-center/index.html",
        "docs/endpoint-contract/index.html",
        "docs/specification-declaration/index.html",
        "docs/install/index.html",
        "docs/guides/environment-setup/index.html",
        "docs/guides/documentation-authoring/index.html",
        "docs/guides/adapt-examples-to-study/index.html",
        "docs/guides/map-your-table/index.html",
        "docs/guides/data-mapping-provenance/index.html",
        "docs/guides/structural-qc-triage/index.html",
        "docs/guides/readiness-policy-design/index.html",
        "docs/guides/claim-boundary-reporting/index.html",
        "docs/guides/endpoint-definition/index.html",
        "docs/guides/specification-declaration/index.html",
        "docs/examples/install-smoke-check/index.html",
        "docs/examples/documentation-intent-routing/index.html",
        "docs/examples/example-to-study-handoff/index.html",
        "docs/examples/data-contract-valid-invalid/index.html",
        "docs/examples/data-mapping-change-audit/index.html",
        "docs/examples/all-structural-qc-issues/index.html",
        "docs/examples/readiness-policy-design/index.html",
        "docs/examples/reporting-language-rewrite/index.html",
        "docs/examples/endpoint-drift-audit/index.html",
        "docs/examples/specification-denominator-audit/index.html",
        "docs/examples/catalog/index.html",
        "docs/examples/choose-the-right-example/index.html",
        "docs/guides/read-api-reference/index.html",
        "docs/examples/source-api-inspection/index.html",
        "docs/examples/api-call-contracts/index.html",
        "docs/reference/cli-reference/index.html",
        "docs/reference/evidence-vocabulary/index.html",
        "docs/reference/core-api-inventory/index.html",
        "docs/reference/site-provenance/index.html",
        "docs/guides/find-information-fast/index.html",
        "docs/examples/search-to-contract/index.html",
        "docs/examples/function-to-evidence/index.html",
        "docs/case-studies/index.html",
        "docs/case-studies/gazebase-incomplete/index.html",
        "docs/case-studies/korthals-target-tracking/index.html",
        "docs/case-studies/pedrotti-sensitivity/index.html",
        "robots.txt",
        "sitemap.xml",
        "assets/css/site.css",
        "assets/css/enhancements.css",
        "assets/css/gallery.css",
        "assets/css/landing.css",
        "assets/css/methods.css",
        "assets/css/api-pathways.css",
        "assets/css/data-contract.css",
        "assets/css/example-catalog.css",
        "assets/css/qc-issue-clinic.css",
        "assets/css/readiness-policy.css",
        "assets/css/reporting-center.css",
        "assets/css/endpoint-contract.css",
        "assets/css/specification-declaration.css",
        "assets/css/install.css",
        "assets/css/planner.css",
        "assets/js/site.js",
        "assets/js/api-symbol-reference.js",
        "assets/js/data-contract.js",
        "assets/js/example-catalog.js",
        "assets/js/qc-issue-clinic.js",
        "assets/js/readiness-policy.js",
        "assets/js/reporting-center.js",
        "assets/js/endpoint-contract.js",
        "assets/js/specification-declaration.js",
        "assets/js/install-builder.js",
        "assets/js/gallery.js",
        "assets/js/landing.js",
        "assets/js/methods.js",
        "assets/js/planner.js",
        "assets/search-index.json",
        "assets/api-symbol-reference.json",
        "assets/data-mapping-record.schema.json",
        "assets/example-index.json",
        "assets/qc-issue-reference.json",
        "assets/readiness-threshold-reference.json",
        "assets/reporting-contract-reference.json",
        "assets/endpoint-contract-reference.json",
        "assets/specification-declaration-reference.json",
        "assets/method-index.json",
        "assets/planner-index.json",
        "assets/plots/specification-curve-code.svg",
        "assets/plots/trial-readiness.svg",
        "assets/plots/cohort-impact.svg",
        "assets/plots/aoi-probability-profile.svg",
        "assets/plots/threshold-sweep.svg",
        "assets/plots/factor-sensitivity.svg",
        "assets/images/aoi-boundary-uncertainty.svg",
        "assets/images/data-contract-flow.svg",
        "assets/images/specification-curve.svg",
        "assets/images/sensitivity-curves.svg",
        "assets/images/workflow-overview.svg",
        "assets/images/gazebase-completeness.svg",
        "assets/images/korthals-effect.svg",
        "assets/images/pedrotti-sampling-sensitivity.svg",
        "assets/images/pedrotti-missingness-recovery.svg",
    ]
    missing_required = [path for path in required if not (site_root / path).is_file()]
    if missing_required:
        raise SystemExit(f"missing required generated site files: {missing_required}")

    robots = (site_root / "robots.txt").read_text(encoding="utf-8")
    sitemap = (site_root / "sitemap.xml").read_text(encoding="utf-8")
    if "sitemap.xml" not in robots.lower() or "<urlset" not in sitemap:
        raise SystemExit("generated discoverability endpoints are incomplete")

    forbidden = ["src", "tests", "tools", "release", ".github", "pyproject.toml", "README.md"]
    leaked = [path for path in forbidden if (site_root / path).exists()]
    if leaked:
        raise SystemExit(f"repository internals leaked into generated Pages site: {leaked}")

    html_files = sorted(site_root.rglob("*.html"))
    if len(html_files) < 24:
        raise SystemExit(f"unexpectedly small documentation site: {len(html_files)} HTML files")

    failures: list[str] = []
    for html_file in html_files:
        parser = _ReferenceParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for attribute, reference in parser.references:
            if reference.startswith("#"):
                continue
            candidates = _candidate_targets(site_root, html_file, reference, baseurl)
            if not candidates:
                continue
            if not any(
                candidate.resolve().is_relative_to(site_root.resolve()) and candidate.exists()
                for candidate in candidates
            ):
                display = html_file.relative_to(site_root)
                candidate_text = ", ".join(
                    str(path.relative_to(site_root)) if path.is_relative_to(site_root) else str(path)
                    for path in candidates
                )
                failures.append(f"{display}: {attribute}={reference!r} -> [{candidate_text}]")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"broken generated-site references ({len(failures)}):\n{preview}{extra}")

    _verify_search_index(site_root, baseurl=baseurl)
    _verify_example_index(site_root, baseurl=baseurl)
    _verify_qc_issue_reference(site_root)
    _verify_readiness_threshold_reference(site_root)
    _verify_reporting_contract_reference(site_root, baseurl=baseurl)
    _verify_endpoint_contract_reference(site_root)
    _verify_specification_declaration_reference(site_root)
    _verify_method_index(site_root, baseurl=baseurl)
    _verify_planner_index(site_root, baseurl=baseurl)
    print(f"DOCS SITE VERIFY: PASS ({len(html_files)} HTML pages)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the generated GazeAudit documentation site")
    parser.add_argument("site_root", type=Path)
    parser.add_argument("--baseurl", default="/GazeAudit")
    args = parser.parse_args()
    verify_site(args.site_root, baseurl=args.baseurl.rstrip("/"))


if __name__ == "__main__":
    main()
