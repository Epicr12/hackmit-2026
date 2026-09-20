"""Registries for pluggable scorers, data sources, and schema adapters.

Register custom pieces at import time (or in AppConfig.ready)::

    from risk_eval.pipeline import register_scorer

    @register_scorer("my_model")
    def score(bundle, **opts):
        ...
"""

from __future__ import annotations

from typing import Any, Callable

SCORERS: dict[str, Callable[..., dict[str, Any]]] = {}
SOURCES: dict[str, Callable[..., Any]] = {}
SCHEMAS: dict[str, Callable[[Any], Any]] = {}

DEFAULT_SCORER = "heuristic"


def register_scorer(name: str):
    """Decorator / helper to register a scorer under ``name``."""

    def decorator(fn: Callable[..., dict[str, Any]]):
        SCORERS[name] = fn
        return fn

    return decorator


def register_source(name: str):
    """Decorator / helper to register a data source under ``name``.

    A source returns raw website data (any JSON-serialisable shape). The
    pipeline then ingests and scores it like any other payload.
    """

    def decorator(fn: Callable[..., Any]):
        SOURCES[name] = fn
        return fn

    return decorator


def register_schema(name: str):
    """Decorator / helper to register a schema adapter under ``name``.

    A schema adapter maps a loosely structured payload into a shape the
    chosen scorer prefers (still domain-agnostic unless you make it so).
    """

    def decorator(fn: Callable[[Any], Any]):
        SCHEMAS[name] = fn
        return fn

    return decorator


def list_capabilities() -> dict[str, Any]:
    return {
        "scorers": sorted(SCORERS),
        "sources": sorted(SOURCES),
        "schemas": sorted(SCHEMAS),
        "default_scorer": DEFAULT_SCORER,
    }


def get_scorer(name: str | None):
    key = name or DEFAULT_SCORER
    try:
        return SCORERS[key], key
    except KeyError as exc:
        raise KeyError(
            f"unknown scorer {key!r}; registered: {sorted(SCORERS)}"
        ) from exc


def get_source(name: str):
    try:
        return SOURCES[name]
    except KeyError as exc:
        raise KeyError(
            f"unknown source {name!r}; registered: {sorted(SOURCES)}"
        ) from exc


def get_schema(name: str | None):
    if not name:
        return None, None
    try:
        return SCHEMAS[name], name
    except KeyError as exc:
        raise KeyError(
            f"unknown schema {name!r}; registered: {sorted(SCHEMAS)}"
        ) from exc
