"""Memory-bounded endpoint-blind Korthals protocol-v2 companion intake.

The scientific protocol is unchanged. This module only changes execution topology:
each participant is fully companion-preprocessed, protocol-v2 prepared to the frozen
50-Hz representation, and released before the next participant is loaded. The final
prepared object is then reconstructed deterministically from those participant-local
results. This avoids retaining every participant's canonical 1000-Hz aligned table in
memory at once while preserving the exact participant-separable preparation semantics.
"""

from __future__ import annotations

import gc
import importlib
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from .korthals_execution import (
    KORTHALS_COMPANION_COMMIT,
    PreparedKorthalsData,
    _endpoint_weights,
)
from .korthals_source import (
    _align_companion_preprocessed_participant,
    _canonicalize_companion_participant_identity,
    _require_clean_tables,
    _scope_authoritative_task_trials,
    _validated_data_root,
    _working_directory,
)
from .korthals_v2 import (
    KORTHALS_V1_PROTOCOL_FINGERPRINT,
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_MISSINGNESS_POLICY,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    KorthalsSourceIntakeV2,
    build_korthals_source_manifest_v2,
    prepare_korthals_aligned_data_v2,
)
from .provenance import canonical_json, fingerprint


def combine_korthals_prepared_participants_v2(
    prepared_parts: Sequence[PreparedKorthalsData],
    *,
    expected_participants: Sequence[str],
    source_identity: Mapping[str, Any],
) -> PreparedKorthalsData:
    """Combine participant-local v2 preparation without changing scientific semantics.

    Protocol-v2 preprocessing, validation mapping, fixed-grid sampling, missingness-cell
    removal, and the author exclusion are participant-separable. This combiner therefore
    accepts only single-participant prepared objects, verifies exact cohort coverage,
    concatenates the already-50-Hz rows, and reconstructs the same global provenance
    fields produced by monolithic preparation.
    """

    expected = sorted(str(value) for value in expected_participants)
    if not expected or len(expected) != len(set(expected)):
        raise ValueError("expected_participants must be a non-empty unique sequence")
    if len(prepared_parts) != len(expected):
        raise ValueError("prepared participant count differs from expected cohort")

    supplied_identity = json.loads(canonical_json(source_identity))
    if not isinstance(supplied_identity, dict):
        raise TypeError("source_identity must normalize to an object")

    data_parts: list[pd.DataFrame] = []
    validation_parts: list[pd.DataFrame] = []
    observed: list[str] = []
    zero_trials: list[dict[str, Any]] = []
    incomplete_cells: list[dict[str, Any]] = []

    for prepared in prepared_parts:
        if not isinstance(prepared, PreparedKorthalsData):
            raise TypeError("prepared_parts must contain PreparedKorthalsData values")
        participant_ids = sorted(prepared.data["participant_id"].astype(str).unique().tolist())
        if len(participant_ids) != 1:
            raise ValueError("each prepared part must contain exactly one participant")
        participant_id = participant_ids[0]
        if int(prepared.source_identity.get("participant_count", -1)) != 1:
            raise ValueError("participant-local prepared identity must declare one participant")
        if prepared.source_identity.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            raise ValueError("participant-local prepared object has the wrong case-study identity")
        if (
            prepared.source_identity.get("protocol_fingerprint")
            != KORTHALS_V2_PROTOCOL_FINGERPRINT
        ):
            raise ValueError("participant-local prepared object has the wrong protocol identity")
        if (
            prepared.source_identity.get("missingness_policy")
            != KORTHALS_V2_MISSINGNESS_POLICY
        ):
            raise ValueError("participant-local prepared object has the wrong missingness policy")

        observed.append(participant_id)
        data_parts.append(prepared.data.copy())
        validation_parts.append(prepared.validation_groups.copy())
        zero_trials.extend(prepared.source_identity["zero_finite_scheduled_trials"])
        incomplete_cells.extend(
            prepared.source_identity["sampling_incomplete_matched_cells"]
        )

    if sorted(observed) != expected or len(observed) != len(set(observed)):
        raise ValueError(
            "participant-local prepared objects do not cover the expected cohort exactly"
        )

    data = pd.concat(data_parts, ignore_index=True)
    data = data.sort_values(
        ["participant_id", "trial_number", "scheduled_trial_time", "trial_time"],
        kind="stable",
    ).reset_index(drop=True)
    _endpoint_weights(data)

    validation_groups = pd.concat(validation_parts, ignore_index=True)
    validation_groups = validation_groups.sort_values(
        ["participant_id", "validation_nr"], kind="stable"
    ).reset_index(drop=True)
    if validation_groups["error_group"].duplicated().any():
        raise ValueError("combined validation groups must remain unique")
    used_groups = set(data["error_group"])
    if set(validation_groups["error_group"]) != used_groups:
        raise ValueError("combined validation groups must exactly cover retained error groups")

    participant_ids = sorted(data["participant_id"].astype(str).unique().tolist())
    if participant_ids != expected:
        raise ValueError("every source participant must retain prepared protocol-v2 rows")
    retained_trials = (
        data[["participant_id", "trial_number"]]
        .drop_duplicates()
        .sort_values(["participant_id", "trial_number"], kind="stable")
        .to_dict(orient="records")
    )
    zero_trials = sorted(
        zero_trials,
        key=lambda item: (str(item["participant_id"]), int(item["trial_number"])),
    )
    incomplete_cells = sorted(
        incomplete_cells,
        key=lambda item: (
            str(item["participant_id"]),
            int(item["repetition"]),
            float(item["target_speed"]),
            str(item["target_trajectory"]),
        ),
    )

    identity = {
        **supplied_identity,
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "participant_count": len(participant_ids),
        "participant_fingerprint": fingerprint(participant_ids),
        "retained_trial_count": len(retained_trials),
        "retained_trial_fingerprint": fingerprint(retained_trials),
        "protocol_amendment_from": KORTHALS_V1_PROTOCOL_FINGERPRINT,
        "missingness_policy": KORTHALS_V2_MISSINGNESS_POLICY,
        "zero_finite_scheduled_trial_count": len(zero_trials),
        "zero_finite_scheduled_trials": zero_trials,
        "sampling_incomplete_matched_cell_count": len(incomplete_cells),
        "sampling_incomplete_matched_cells": incomplete_cells,
    }
    return PreparedKorthalsData(
        data=data,
        validation_groups=validation_groups,
        source_identity=identity,
    )


def prepare_korthals_from_companion_v2_streaming(
    data_root: str | Path = "data",
    *,
    participant_factory: Callable[..., Any] | None = None,
    preprocessor_factory: Callable[[], Any] | None = None,
) -> KorthalsSourceIntakeV2:
    """Run canonical companion preprocessing with bounded full-resolution memory.

    Only one participant's canonical full-resolution aligned table is retained at a
    time. Each participant is immediately passed through the unchanged protocol-v2
    preparation function, leaving only its compact frozen 50-Hz representation in the
    accumulator. No source row is interpolated, substituted, or otherwise altered.
    """

    root = _validated_data_root(data_root)
    if root.name != "data":
        raise ValueError("companion intake requires a source directory named exactly 'data'")
    source_manifest = build_korthals_source_manifest_v2(root)

    if participant_factory is None or preprocessor_factory is None:
        participant_module = importlib.import_module("eyemovement_data.participant")
        preprocessor_module = importlib.import_module("eyemovement_data.preprocessor")
        if participant_factory is None:
            participant_factory = participant_module.Participant
        if preprocessor_factory is None:
            preprocessor_factory = preprocessor_module.OriginalPreprocessor

    participants = list(source_manifest["participants"])
    prepared_parts: list[PreparedKorthalsData] = []
    splits: list[tuple[str, str]] = []

    with _working_directory(root.parent):
        relative_root = Path("data")
        for participant_id in participants:
            participant = participant_factory(
                id=participant_id,
                preprocessor=preprocessor_factory(),
            )
            participant.set_clean_data(str(relative_root / "clean"))
            _require_clean_tables(participant_id, participant.clean_data)
            _canonicalize_companion_participant_identity(
                relative_root / "clean",
                participant_id,
                participant.clean_data,
            )
            participant.preprocess_clean_data(
                blink_offset=(50, 50),
                rolling_mean_window=1,
            )
            aligned = _align_companion_preprocessed_participant(
                participant_id,
                participant.preprocessed_data,
            )
            aligned = _scope_authoritative_task_trials(aligned)
            validation = participant.validation_check(str(relative_root / "raw"))
            if not isinstance(validation, pd.DataFrame) or validation.empty:
                raise ValueError(
                    f"participant {participant_id!r} produced no validation summaries"
                )
            split = str(getattr(participant, "subset", "unknown_subset"))
            if split not in {"train", "test"}:
                raise ValueError(
                    f"participant {participant_id!r} has unresolved train/test split"
                )

            local_prepared = prepare_korthals_aligned_data_v2(aligned, validation)
            local_ids = local_prepared.data["participant_id"].astype(str).unique().tolist()
            if local_ids != [participant_id]:
                raise ValueError(
                    f"participant {participant_id!r} local preparation changed identity"
                )
            prepared_parts.append(local_prepared)
            splits.append((participant_id, split))

            # Release full-resolution companion state before loading the next participant.
            del aligned, validation, local_prepared, participant
            gc.collect()

    ordered_splits = tuple(sorted(splits))
    split_records = [
        {"participant_id": participant_id, "split": split}
        for participant_id, split in ordered_splits
    ]
    source_identity = {
        "source_manifest_fingerprint": source_manifest["source_manifest_fingerprint"],
        "source_file_count": source_manifest["file_count"],
        "download_contract": source_manifest["download_contract"],
        "participant_split_fingerprint": fingerprint(split_records),
        "participant_splits": split_records,
    }
    prepared = combine_korthals_prepared_participants_v2(
        prepared_parts,
        expected_participants=participants,
        source_identity=source_identity,
    )
    if prepared.source_identity["participant_count"] != len(participants):
        raise ValueError("prepared participant count differs from source-manifest cohort")
    return KorthalsSourceIntakeV2(
        prepared=prepared,
        source_manifest=source_manifest,
        participant_splits=ordered_splits,
    )
