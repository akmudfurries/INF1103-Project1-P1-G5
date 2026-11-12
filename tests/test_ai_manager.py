# ====================================================
# Run: python -m pytest tests/test_ai_manager.py -v
# ====================================================

import json

import pytest

from ai_manager import AIManager
from ai_provider import AIProvider
from config import MAX_RETRIES
from models import InventoryRecord, AIAssessment


class FakeAIProvider(AIProvider):
    """Returns predefined replies or raises predefined errors."""

    def __init__(self, responses: list) -> None:
        self.responses = responses
        self.calls = 0

    def generate(self, prompt: str) -> str | None:
        # When replies run out, keep using the final one.
        index = min(self.calls, len(self.responses) - 1)
        response = self.responses[index]
        self.calls += 1

        if isinstance(response, Exception):
            raise response

        return response


@pytest.fixture
def inventory() -> InventoryRecord:
    return InventoryRecord(
        item_id="INV001",
        item_name="Printer Ribbon",
        current_stock=40,
        weekly_usage=10,
        lead_time_weeks=2,
        operational_notes="Usage increased and the supplier was late.",
    )


@pytest.fixture
def valid_answer() -> dict:
    return {
        "demand_level": "high",
        "demand_trend": "increasing",
        "supply_risk": "high",
        "operational_importance": "medium",
        "reason": "Usage increased and the supplier experienced delays.",
    }


@pytest.fixture(autouse=True)
def skip_retry_wait(monkeypatch):
    # Tests check retry behaviour without actually waiting.
    monkeypatch.setattr("ai_manager.time.sleep", lambda seconds: None)


# 1. Valid AI response
def test_valid_response(inventory, valid_answer):
    # Check that spaces and capital letters are normalised.
    valid_answer["demand_level"] = " High "

    provider = FakeAIProvider([json.dumps(valid_answer)])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert error is None
    assert assessment is not None
    assert assessment.demand_level == "high"
    assert assessment.demand_trend == "increasing"
    assert provider.calls == 1


# 2. Invalid JSON response
def test_invalid_json(inventory):
    provider = FakeAIProvider(["This is not JSON"])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert assessment is None
    assert error is not None
    assert "JSON" in error
    assert provider.calls == MAX_RETRIES + 1


# 3. Missing required fields
def test_missing_field(inventory, valid_answer):
    del valid_answer["supply_risk"]

    provider = FakeAIProvider([json.dumps(valid_answer)])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert assessment is None
    assert error is not None
    assert "missing supply_risk" in error
    assert provider.calls == MAX_RETRIES + 1


# 4. Invalid assessment values
def test_invalid_value(inventory, valid_answer):
    valid_answer["demand_level"] = "extreme"

    provider = FakeAIProvider([json.dumps(valid_answer)])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert assessment is None
    assert error is not None
    assert "demand_level has an invalid answer" in error
    assert provider.calls == MAX_RETRIES + 1


# 5. Retry behaviour: first reply fails, next reply succeeds
def test_retry_then_success(inventory, valid_answer):
    provider = FakeAIProvider([
        "Invalid JSON",
        json.dumps(valid_answer),
    ])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert error is None
    assert assessment is not None
    assert assessment.demand_level == "high"
    assert provider.calls == 2


# 6. API communication errors
@pytest.mark.parametrize(
    "message, expected_text, expected_calls",
    [
        (
            "503 UNAVAILABLE",
            "Gemini is busy",
            MAX_RETRIES + 1,
        ),
        (
            "429 rate limit exceeded",
            "AI usage limit reached",
            MAX_RETRIES + 1,
        ),
        (
            "Request timed out",
            "Gemini took too long",
            MAX_RETRIES + 1,
        ),
        (
            "Invalid API key",
            "Check your API key",
            1,
        ),
        (
            "Missing api_key",
            "Check your API key",
            1,
        ),
        (
            "Connection failed",
            "Could not reach AI",
            MAX_RETRIES + 1,
        ),
    ],
)
def test_api_errors(
    inventory,
    message,
    expected_text,
    expected_calls,
):
    provider = FakeAIProvider([RuntimeError(message)])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert assessment is None
    assert error is not None
    assert expected_text in error
    assert provider.calls == expected_calls


# 7. Successful conversion into AIAssessment
def test_conversion_to_assessment(inventory, valid_answer):
    provider = FakeAIProvider([json.dumps(valid_answer)])
    manager = AIManager(provider)

    assessment, error = manager.assess(inventory)

    assert error is None
    assert isinstance(assessment, AIAssessment)
    assert assessment.to_dict() == valid_answer