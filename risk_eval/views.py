"""Views for the flexible risk-assessment pipeline."""

from __future__ import annotations

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from risk_eval.pipeline import assess, list_capabilities


SAMPLE_PAYLOAD = {
    "meta": {"label": "ui_sample"},
    "records": [
        {"feature": "cart_abandonment", "risk_score": 42, "severity": "medium"},
        {"feature": "auth_anomalies", "risk_score": 71, "exposed": True},
        {"feature": "content_health", "quality": 91, "uptime_pct": 99.5},
    ],
}


@ensure_csrf_cookie
def risk_page(request):
    caps = list_capabilities()
    return render(
        request,
        "risk_eval/risk.html",
        {
            "capabilities": caps,
            "sample_payload_json": json.dumps(SAMPLE_PAYLOAD, indent=2),
        },
    )


@require_http_methods(["GET"])
def capabilities_api(request):
    return JsonResponse(list_capabilities())


@csrf_exempt  # hackathon: open JSON API; add auth before any public deploy
@require_http_methods(["GET", "POST"])
def assess_api(request):
    """Assess risk from arbitrary JSON and/or a registered source.

    POST body (all fields optional except that payload and/or source is needed)::

        {
          "payload": { ... arbitrary website data ... },
          "source": "example_generic",
          "schema": "passthrough",
          "scorer": "heuristic",
          "scorer_options": {}
        }

    GET query params: ``source``, ``schema``, ``scorer`` (no body payload).
    """
    try:
        if request.method == "POST":
            try:
                body = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return JsonResponse({"error": "body must be JSON"}, status=400)
            if not isinstance(body, dict):
                return JsonResponse({"error": "JSON body must be an object"}, status=400)

            # Convenience: if the client posts raw website data without wrapping
            # it in {"payload": ...}, treat the whole body as the payload unless
            # it only contains control keys.
            control_keys = {"payload", "source", "schema", "scorer", "scorer_options"}
            if "payload" in body or "source" in body:
                payload = body.get("payload")
                source = body.get("source")
                schema = body.get("schema")
                scorer = body.get("scorer")
                scorer_options = body.get("scorer_options") or {}
            elif set(body) <= control_keys:
                payload = None
                source = body.get("source")
                schema = body.get("schema")
                scorer = body.get("scorer")
                scorer_options = body.get("scorer_options") or {}
            else:
                payload = body
                source = None
                schema = None
                scorer = None
                scorer_options = {}
        else:
            payload = None
            source = request.GET.get("source")
            schema = request.GET.get("schema")
            scorer = request.GET.get("scorer")
            scorer_options = {}

        if payload is None and not source:
            return JsonResponse(
                {
                    "error": "provide JSON payload and/or source",
                    "capabilities": list_capabilities(),
                },
                status=400,
            )

        result = assess(
            payload,
            source=source,
            schema=schema,
            scorer=scorer,
            scorer_options=scorer_options if isinstance(scorer_options, dict) else {},
        )
        return JsonResponse(result)
    except KeyError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception as exc:  # pragma: no cover - unexpected
        return JsonResponse({"error": f"assessment failed: {exc}"}, status=500)
