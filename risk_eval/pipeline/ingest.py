"""Ingest arbitrary / loosely structured website data into a feature bundle.

No fixed domain schema is required. Callers may optionally run a registered
schema adapter first (see :mod:`risk_eval.pipeline.registry`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Feature:
    """One extracted signal from the payload."""

    path: str
    value: Any
    kind: str  # "number" | "bool" | "text" | "null" | "other"


@dataclass
class IngestedBundle:
    """Normalised view of whatever the caller (or a source) provided."""

    records: list[dict[str, Any]] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    raw: Any = None


def ingest(payload: Any, *, label: str | None = None) -> IngestedBundle:
    """Turn arbitrary JSON-ish data into records + flat features.

    Accepted shapes (examples, not exhaustive):
    - ``{"records": [ {...}, ... ], "meta": {...}}``
    - a bare list of objects
    - a single object (treated as one record)
    - nested dicts/lists — leaf values become features with dotted paths
    """
    meta: dict[str, Any] = {}
    if isinstance(payload, dict) and "meta" in payload and isinstance(payload["meta"], dict):
        meta = dict(payload["meta"])
    if label:
        meta.setdefault("label", label)

    records = _extract_records(payload)
    features: list[Feature] = []
    for i, record in enumerate(records):
        prefix = f"records[{i}]" if len(records) > 1 else "record"
        features.extend(_walk(record, prefix))

    # Also walk non-record top-level keys when payload is a wrapped envelope.
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in {"records", "data", "items", "rows", "meta"}:
                continue
            features.extend(_walk(value, key))

    return IngestedBundle(
        records=records,
        features=features,
        meta=meta,
        raw=payload,
    )


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []

    if isinstance(payload, list):
        return [_as_record(item, i) for i, item in enumerate(payload)]

    if isinstance(payload, dict):
        for key in ("records", "data", "items", "rows"):
            if key in payload and isinstance(payload[key], list):
                return [_as_record(item, i) for i, item in enumerate(payload[key])]
        # Single object → one record (minus reserved envelope keys).
        record = {
            k: v
            for k, v in payload.items()
            if k not in {"meta", "schema", "scorer", "source"}
        }
        return [record] if record else []

    return [{"value": payload}]


def _as_record(item: Any, index: int) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    return {"value": item, "_index": index}


def _walk(node: Any, path: str) -> list[Feature]:
    if isinstance(node, dict):
        out: list[Feature] = []
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            out.extend(_walk(value, child))
        return out

    if isinstance(node, list):
        out = []
        for i, value in enumerate(node):
            out.extend(_walk(value, f"{path}[{i}]"))
        return out

    return [Feature(path=path, value=node, kind=_kind(node))]


def _kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "text"
    return "other"
