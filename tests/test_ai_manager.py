# ====================================================
# Run: python -m pytest tests/test_ai_manager.py -v
# ====================================================

from ai_manager import get_ai_analysis

# A pretend inventory item to send to the AI
item = {"item_name": "Cookie", "operational_notes": "Used a lot this month."}


def fake_prompt(prompt):
    return '{"demand_level": "high", "demand_trend": "increasing", "supply_risk": "low", "operational_importance": "high", "reason": "test"}'

def fake_broken_json(prompt):
    return "this is the json"

def fake_wrong_value(prompt):
    return '{"demand_level": "super duper high", "demand_trend": "increasing", "supply_risk": "low", "operational_importance": "high", "reason": "test"}'

def fake_missing_key(prompt):
    return '{"demand_level": "high", "reason": "test"}'


def test_answer():
    answer, issue = get_ai_analysis(item, ask_function=fake_prompt)
    assert issue == ""
    assert answer["demand_level"] == "high"

def test_broken_json():
    answer, issue = get_ai_analysis(item, ask_function=fake_broken_json)
    assert answer is None
    assert "not valid JSON" in issue

def test_wrong_value():
    answer, issue = get_ai_analysis(item, ask_function=fake_wrong_value)
    assert answer is None
    assert "invalid answer" in issue

def test_missing_key():
    answer, issue = get_ai_analysis(item, ask_function=fake_missing_key)
    assert answer is None
    assert "missing" in issue