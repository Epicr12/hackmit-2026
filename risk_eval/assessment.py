"""Call Cursor to produce an AMD risk assessment from nearby sensor data."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from django.conf import settings


ASSESSMENT_PROMPT = """You are assessing Acid Mine Drainage (AMD) exposure risk for a
resident or visitor in West Virginia / Appalachia.

Use ONLY the location and sensor readings provided below. Do not invent extra
sensor values. If data is sparse, say so and lower confidence.

Return ONLY valid JSON (no markdown fences) with this exact shape:
{{
  "risk_level": "low" | "moderate" | "high" | "critical",
  "confidence": "low" | "medium" | "high",
  "headline": "one short sentence",
  "summary": "2-4 sentences explaining the risk in plain language",
  "key_factors": ["bullet", "bullet", "bullet"],
  "recommendations": ["actionable next step", "actionable next step", "actionable next step"],
  "affected_waterways": ["waterway names from the sensor list"]
}}

Risk guidance:
- critical: pH often < 4 and/or very high metals near the user
- high: clear AMD impairment nearby (low pH, elevated Fe/Al/Mn)
- moderate: elevated readings or watch-status sites within range
- low: nearest mainstem/sites look relatively stable

Location context:
{location_json}

Nearby sensor readings (distance_km is approximate):
{sensors_json}

Measurement units:
{units_json}
"""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def run_cursor_assessment(context: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "CURSOR_API_KEY is not set. Export your Cursor API key, then retry."
        )

    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    prompt = ASSESSMENT_PROMPT.format(
        location_json=json.dumps(context["location"], indent=2),
        sensors_json=json.dumps(context["sensors"], indent=2),
        units_json=json.dumps(context["units"], indent=2),
    )

    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model="composer-2.5",
            # Text-only: sensor context is already in the prompt.
            tools=[],
            local=LocalAgentOptions(cwd=str(settings.BASE_DIR / "data")),
        ),
    )

    if result.status == "error":
        raise RuntimeError(
            f"Cursor risk assessment failed (run {getattr(result, 'id', 'unknown')})."
        )

    raw = (result.result or "").strip()
    if not raw:
        raise RuntimeError("Cursor returned an empty assessment.")

    assessment = _extract_json(raw)
    level = str(assessment.get("risk_level", "moderate")).lower()
    if level not in {"low", "moderate", "high", "critical"}:
        level = "moderate"
    assessment["risk_level"] = level
    assessment["raw_text"] = raw
    return assessment
