"""Flexible risk-assessment pipeline for arbitrary website data.

Public entry point: :func:`assess`.
Extension points: register scorers, sources, and schemas via
:mod:`risk_eval.pipeline.registry`.
"""

from .assess import assess
from .registry import (
    list_capabilities,
    register_schema,
    register_scorer,
    register_source,
)

__all__ = [
    "assess",
    "list_capabilities",
    "register_schema",
    "register_scorer",
    "register_source",
]
