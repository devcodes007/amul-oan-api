"""Stable provenance stamps for telemetry emitted by this service."""

import os
from functools import lru_cache
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, check_output
from typing import Any

CHAT_TELEMETRY_SCHEMA_VERSION = "chat.turn.v1"
CHAT_TELEMETRY_SERVICE = "amul-oan-api"
CHAT_TURN_V1_ROOT = "chat.translation"


@lru_cache(maxsize=1)
def chat_telemetry_release() -> str:
    """Return the deployed Git revision without relying on LANGFUSE_RELEASE."""

    if release := os.getenv("GIT_SHA"):
        return release
    try:
        return check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            stderr=DEVNULL,
            text=True,
        ).strip() or "unknown"
    except (CalledProcessError, FileNotFoundError):
        return "unknown"


def forward_chat_telemetry_metadata() -> dict[str, str]:
    return {
        "amul.schema_version": CHAT_TELEMETRY_SCHEMA_VERSION,
        "service": CHAT_TELEMETRY_SERVICE,
        "release": chat_telemetry_release(),
    }


def chat_turn_v1_metadata(**fields: str) -> dict[str, str]:
    """The complete fixed metadata shape emitted for a chat.turn.v1 root."""

    return {**forward_chat_telemetry_metadata(), **fields}


def chat_turn_v1_input(**fields: Any) -> dict[str, Any]:
    """The trace input shape for chat.turn.v1."""

    return dict(fields)
