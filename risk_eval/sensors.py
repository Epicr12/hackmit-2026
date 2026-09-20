"""Load AMD sensor data and resolve a user location to nearby readings."""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from django.conf import settings

DATA_PATH = Path(settings.BASE_DIR) / "data" / "amd_sensors.json"
COORD_RE = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)\s*$"
)


@lru_cache(maxsize=1)
def load_dataset() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def resolve_location(location_query: str) -> dict[str, Any]:
    """Map free-text location to coordinates using coords or known WV places."""
    query = location_query.strip()
    if not query:
        raise ValueError("Location is required.")

    coord_match = COORD_RE.match(query)
    if coord_match:
        lat = float(coord_match.group(1))
        lng = float(coord_match.group(2))
        if not (36.0 <= lat <= 41.5 and -85.0 <= lng <= -77.0):
            raise ValueError(
                "Coordinates look outside the Appalachian coverage area. "
                "Try a West Virginia city, county, or lat/lng pair."
            )
        return {
            "query": query,
            "label": f"{lat:.4f}, {lng:.4f}",
            "lat": lat,
            "lng": lng,
            "match_type": "coordinates",
        }

    dataset = load_dataset()
    normalized = query.lower()
    normalized = re.sub(r"\b(wv|west virginia|county|co\.?)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    best_place: dict[str, Any] | None = None
    best_score = 0
    for place in dataset["places"]:
        name = place["name"].lower()
        county = place["county"].lower()
        score = 0
        if normalized == name or normalized == county:
            score = 100
        elif name in normalized or normalized in name:
            score = 80
        elif county in normalized or normalized in county:
            score = 70
        elif any(token and token in name for token in normalized.split()):
            score = 40
        if score > best_score:
            best_score = score
            best_place = place

    # Also allow matching sensor waterway / county names directly.
    if best_score < 70:
        for sensor in dataset["sensors"]:
            waterway = sensor["waterway"].lower()
            county = sensor["county"].lower()
            name = sensor["name"].lower()
            score = 0
            if waterway in normalized or normalized in waterway:
                score = 75
            elif county in normalized:
                score = 65
            elif any(token and token in name for token in normalized.split() if len(token) > 3):
                score = 50
            if score > best_score:
                best_score = score
                best_place = {
                    "name": sensor["name"],
                    "county": sensor["county"],
                    "lat": sensor["lat"],
                    "lng": sensor["lng"],
                }

    if not best_place or best_score < 40:
        raise ValueError(
            "Could not match that location. Try a West Virginia city "
            "(e.g. Morgantown), county (e.g. Tucker), river name, or lat/lng."
        )

    label = best_place["name"]
    if best_place.get("county"):
        label = f"{best_place['name']}, {best_place['county']} County, WV"

    return {
        "query": query,
        "label": label,
        "lat": best_place["lat"],
        "lng": best_place["lng"],
        "match_type": "place",
        "county": best_place.get("county"),
    }


def nearby_sensors(
    lat: float,
    lng: float,
    *,
    limit: int = 5,
    max_km: float = 80.0,
) -> list[dict[str, Any]]:
    sensors = load_dataset()["sensors"]
    ranked: list[dict[str, Any]] = []
    for sensor in sensors:
        distance = haversine_km(lat, lng, sensor["lat"], sensor["lng"])
        if distance > max_km:
            continue
        ranked.append({**sensor, "distance_km": round(distance, 1)})
    ranked.sort(key=lambda item: item["distance_km"])
    return ranked[:limit]


def context_for_assessment(location_query: str) -> dict[str, Any]:
    resolved = resolve_location(location_query)
    sensors = nearby_sensors(resolved["lat"], resolved["lng"])
    if not sensors:
        raise ValueError(
            "No sensor sites found near that location within our coverage area."
        )
    return {
        "location": resolved,
        "sensors": sensors,
        "units": load_dataset()["units"],
    }
