"""Built-in sources and schema adapters (examples / extension points).

These show how a website plugs its own data into the generic pipeline.
They are optional — callers can POST arbitrary JSON with no source at all.
"""

from __future__ import annotations

from typing import Any

from risk_eval.pipeline.registry import register_schema, register_source


@register_schema("passthrough")
def passthrough_schema(payload: Any) -> Any:
    """Identity adapter — useful as a documented extension hook."""
    return payload


@register_schema("records_envelope")
def records_envelope_schema(payload: Any) -> Any:
    """If the payload is a bare list, wrap it as ``{"records": [...]}``."""
    if isinstance(payload, list):
        return {"records": payload, "meta": {"schema": "records_envelope"}}
    return payload


@register_source("example_generic")
def example_generic_source() -> dict[str, Any]:
    """Synthetic multi-domain sample — proves the pipeline is not AMD-tied."""
    return {
        "meta": {
            "label": "example_generic",
            "note": "Illustrative mixed signals from an arbitrary site feed.",
        },
        "records": [
            {
                "page": "/checkout",
                "error_rate": 0.12,
                "latency_ms": 2400,
                "risk_level": "elevated",
            },
            {
                "page": "/login",
                "failed_logins": 47,
                "risk_score": 68,
                "exposed": True,
            },
            {
                "page": "/health",
                "uptime_pct": 99.2,
                "quality": 88,
            },
        ],
    }


@register_source("site_map_snapshot")
def site_map_snapshot_source() -> dict[str, Any]:
    """Optional adapter: pull this Django app's map models if present.

    Field names here come from *this* site's models only inside the adapter.
    The core scorer never hardcodes them — it just sees generic features.
    """
    try:
        from mapview.models import CountyImpact, Stream
    except Exception as exc:  # pragma: no cover - import / app loading
        return {
            "meta": {"label": "site_map_snapshot", "error": str(exc)},
            "records": [],
        }

    counties = [
        {
            "entity": "county",
            "name": c.name,
            "state": c.state,
            "severity": c.severity,
            "impaired_miles": c.impaired_miles,
        }
        for c in CountyImpact.objects.all()[:50]
    ]
    streams = [
        {
            "entity": "stream",
            "name": s.name,
            "ph": s.ph,
            "temperature": s.temperature,
            "dissolved_oxygen": s.dissolved_oxygen,
            "turbidity": s.turbidity,
        }
        for s in Stream.objects.all()[:50]
    ]
    return {
        "meta": {
            "label": "site_map_snapshot",
            "note": (
                "Adapter example only — maps local models into generic records. "
                "Swap or delete without touching the core pipeline."
            ),
        },
        "records": counties + streams,
    }
