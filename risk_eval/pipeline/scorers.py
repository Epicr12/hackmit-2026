"""Default heuristic scorer — domain-agnostic risk prediction from features.

Looks for soft, conventional signals (keys mentioning risk/severity/score/…)
and otherwise summarises numeric spread. It is intentionally simple and
replaceable: register another scorer for ML models or vertical rules.
"""

from __future__ import annotations

import math
import re
from typing import Any

from risk_eval.pipeline.ingest import IngestedBundle
from risk_eval.pipeline.registry import register_scorer

# Soft conventions only — not a fixed schema. Matching is case-insensitive
# against the *leaf* key of a feature path.
_RISKISH = re.compile(
    r"(risk|severity|hazard|threat|danger|score|probability|likelihood|"
    r"impact|exposure|vulnerability|urgency|priority|level)",
    re.I,
)
_BENIGN = re.compile(
    r"(health|safe|ok|good|confidence|quality(?!.*risk))",
    re.I,
)

_LEVELS = (
    (75, "critical", "Critical"),
    (50, "serious", "Serious"),
    (25, "warning", "Elevated"),
    (0, "good", "Healthy"),
)


def level_for(score: float) -> tuple[str, str]:
    """Map a 0–100 score onto the site badge vocabulary."""
    score = max(0.0, min(100.0, float(score)))
    for threshold, key, label in _LEVELS:
        if score >= threshold:
            return key, label
    return "good", "Healthy"


def _leaf(path: str) -> str:
    return path.rsplit(".", 1)[-1].rsplit("[", 1)[0]


def _normalize_number(value: float, leaf: str) -> float | None:
    """Map a numeric observation onto an approximate 0–100 risk contribution."""
    if math.isnan(value) or math.isinf(value):
        return None

    # Explicit unit-ish hints in the key name.
    low = leaf.lower()
    if any(tok in low for tok in ("pct", "percent", "probability", "prob", "likelihood")):
        return max(0.0, min(100.0, value if value > 1.0 else value * 100.0))

    if 0.0 <= value <= 1.0 and _RISKISH.search(leaf):
        return value * 100.0

    if 0.0 <= value <= 100.0:
        return float(value)

    # Unbounded magnitudes: compress with a soft log curve so huge outliers
    # still move the needle without dominating forever.
    return max(0.0, min(100.0, math.log10(abs(value) + 1.0) * 25.0))


@register_scorer("heuristic")
def heuristic_score(bundle: IngestedBundle, **_opts: Any) -> dict[str, Any]:
    """Produce a simple risk assessment from an :class:`IngestedBundle`."""
    contributions: list[tuple[str, float, str]] = []

    for feat in bundle.features:
        leaf = _leaf(feat.path)
        if feat.kind == "number":
            norm = _normalize_number(float(feat.value), leaf)
            if norm is None:
                continue
            if _BENIGN.search(leaf) and not _RISKISH.search(leaf):
                # Treat "health/quality" style metrics as inverse risk.
                norm = 100.0 - norm
                reason = f"{feat.path}={feat.value} (treated as inverse risk)"
            elif _RISKISH.search(leaf):
                reason = f"{feat.path}={feat.value} (risk-like field)"
            else:
                reason = f"{feat.path}={feat.value} (numeric signal)"
            contributions.append((feat.path, norm, reason))
        elif feat.kind == "bool" and _RISKISH.search(leaf):
            norm = 80.0 if feat.value else 10.0
            contributions.append(
                (feat.path, norm, f"{feat.path}={feat.value} (boolean risk flag)")
            )
        elif feat.kind == "text" and _RISKISH.search(leaf):
            text = str(feat.value).strip().lower()
            mapping = {
                "critical": 90.0,
                "high": 75.0,
                "serious": 70.0,
                "medium": 50.0,
                "moderate": 45.0,
                "elevated": 40.0,
                "warning": 40.0,
                "low": 20.0,
                "healthy": 10.0,
                "good": 10.0,
                "none": 5.0,
            }
            if text in mapping:
                contributions.append(
                    (feat.path, mapping[text], f"{feat.path}={feat.value!r} (text level)")
                )

    if not contributions:
        return {
            "score": 0.0,
            "level": "good",
            "level_label": "Healthy",
            "summary": "No scorable signals found in the provided data.",
            "factors": [],
            "record_count": len(bundle.records),
            "feature_count": len(bundle.features),
            "scorer": "heuristic",
        }

    # Prefer risk-like fields when present; otherwise use all numerics.
    preferred = [c for c in contributions if "risk-like" in c[2] or "boolean risk" in c[2] or "text level" in c[2]]
    used = preferred or contributions
    scores = [c[1] for c in used]
    score = sum(scores) / len(scores)
    # Mild uplift when many high signals agree.
    highs = sum(1 for s in scores if s >= 70)
    if highs >= 2:
        score = min(100.0, score + 5.0)

    level, level_label = level_for(score)
    top = sorted(used, key=lambda c: c[1], reverse=True)[:8]
    factors = [
        {"path": path, "contribution": round(val, 2), "detail": detail}
        for path, val, detail in top
    ]

    return {
        "score": round(score, 2),
        "level": level,
        "level_label": level_label,
        "summary": (
            f"Assessed {len(bundle.records)} record(s) / {len(bundle.features)} "
            f"feature(s); {len(used)} signal(s) drove a {level_label.lower()} rating."
        ),
        "factors": factors,
        "record_count": len(bundle.records),
        "feature_count": len(bundle.features),
        "scorer": "heuristic",
    }
