import json
from pathlib import Path

from app.services import telemetry_stamps
from app.services.telemetry_stamps import (
    CHAT_TELEMETRY_SCHEMA_VERSION,
    CHAT_TELEMETRY_SERVICE,
    CHAT_TURN_V1_ROOT,
    chat_turn_v1_input,
    chat_turn_v1_metadata,
    forward_chat_telemetry_metadata,
)


CONTRACT = Path(__file__).resolve().parents[1] / "telemetry" / "contracts" / "chat.turn.v1.json"


def test_forward_telemetry_metadata_stamps_schema_service_and_release(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "test-release-sha")
    telemetry_stamps.chat_telemetry_release.cache_clear()

    assert forward_chat_telemetry_metadata() == {
        "amul.schema_version": "chat.turn.v1",
        "service": "amul-oan-api",
        "release": "test-release-sha",
    }


def test_forward_telemetry_metadata_marks_an_unknown_release(monkeypatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.setattr(telemetry_stamps, "check_output", lambda *args, **kwargs: "")
    telemetry_stamps.chat_telemetry_release.cache_clear()

    assert forward_chat_telemetry_metadata()["release"] == "unknown"


def test_chat_turn_v1_contract_matches_the_emitted_shape(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "test-release-sha")
    telemetry_stamps.chat_telemetry_release.cache_clear()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    metadata = chat_turn_v1_metadata(
        pipeline="translation",
        channel="web",
        source_lang="gu",
        target_lang="gu",
        user_id="redacted",
        pipeline_profile="oss",
        persona="farmer",
    )
    trace_input = chat_turn_v1_input(
        query="redacted", channel="web", source_lang="gu", target_lang="gu", persona="farmer"
    )

    assert contract["schema_version"] == CHAT_TELEMETRY_SCHEMA_VERSION
    assert contract["root"] == CHAT_TURN_V1_ROOT
    assert set(contract["metadata"]["required"]) == set(metadata)
    assert set(contract["trace_input"]["required"]) == set(trace_input)
    assert metadata["service"] == CHAT_TELEMETRY_SERVICE
