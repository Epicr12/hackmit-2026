"""Orchestrate ingest → optional schema → scorer for a risk assessment."""

from __future__ import annotations

from typing import Any

from risk_eval.pipeline.ingest import ingest
from risk_eval.pipeline.registry import get_schema, get_scorer, get_source

# Import built-ins so @register_* hooks run.
from risk_eval.pipeline import scorers as _scorers  # noqa: F401
from risk_eval.pipeline import sources as _sources  # noqa: F401


def assess(
    payload: Any | None = None,
    *,
    source: str | None = None,
    schema: str | None = None,
    scorer: str | None = None,
    scorer_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the flexible risk pipeline.

    Provide either ``payload`` (arbitrary JSON-ish data) or ``source`` (a
    registered fetcher). Optionally apply a ``schema`` adapter, then score
    with the named ``scorer`` (default: ``heuristic``).
    """
    if payload is None and not source:
        raise ValueError("provide payload and/or source")

    resolved_source = None
    if source:
        fetch = get_source(source)
        fetched = fetch()
        resolved_source = source
        if payload is None:
            payload = fetched
        elif isinstance(payload, dict) and isinstance(fetched, dict):
            # Merge: explicit payload wins on key conflicts.
            merged = dict(fetched)
            merged.update(payload)
            payload = merged
        # else: caller payload replaces source output entirely when not both dicts

    schema_fn, schema_name = get_schema(schema)
    if schema_fn is not None:
        payload = schema_fn(payload)

    bundle = ingest(payload, label=resolved_source)
    score_fn, scorer_name = get_scorer(scorer)
    result = score_fn(bundle, **(scorer_options or {}))

    return {
        "assessment": result,
        "meta": {
            **bundle.meta,
            "source": resolved_source,
            "schema": schema_name,
            "scorer": scorer_name,
            "record_count": len(bundle.records),
            "feature_count": len(bundle.features),
        },
        "preview": {
            "records_sample": bundle.records[:5],
            "feature_paths_sample": [f.path for f in bundle.features[:20]],
        },
    }
