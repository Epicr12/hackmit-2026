from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .assessment import run_cursor_assessment
from .sensors import context_for_assessment


@require_http_methods(["GET", "POST"])
def risk_page(request):
    if request.method == "GET":
        return render(request, "risk_eval/risk.html", {"mode": "form"})

    location = (request.POST.get("location") or "").strip()
    if not location:
        return render(
            request,
            "risk_eval/risk.html",
            {
                "mode": "form",
                "error": "Enter a location to check AMD risk.",
                "location": location,
            },
            status=400,
        )

    try:
        context = context_for_assessment(location)
        assessment = run_cursor_assessment(context)
    except ValueError as exc:
        return render(
            request,
            "risk_eval/risk.html",
            {
                "mode": "form",
                "error": str(exc),
                "location": location,
            },
            status=400,
        )
    except Exception as exc:
        return render(
            request,
            "risk_eval/risk.html",
            {
                "mode": "form",
                "error": str(exc),
                "location": location,
            },
            status=502,
        )

    return render(
        request,
        "risk_eval/risk.html",
        {
            "mode": "result",
            "location": location,
            "resolved": context["location"],
            "sensors": context["sensors"],
            "assessment": assessment,
        },
    )
