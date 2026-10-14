# & "C:\Users\Alister\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pytest tests/test_logic_manager.py -v
import logic_manager


def test_inventory_requiring_reorder():
    # Hardcoded inventory record
    inventory = {
        "item_id": "INV007",
        "item_name": "Pressure Sensor",
        "current_stock": 18,
        "weekly_usage": 8,
        "lead_time_weeks": 3,
        "operational_notes": "Supplier deliveries have been delayed.",
        "moq": 20,
        "unit_cost": 35.0,
        "budget": 2000.0,
    }

    # Mock AI assessment. No API call is made.
    assessment = {
        "demand_level": "high",
        "demand_trend": "stable",
        "supply_risk": "low",
        "operational_importance": "medium",
        "reason": "Sample assessment for automated testing.",
    }

    result = logic_manager.analyse_inventory(inventory, assessment)

    # Verify expected procurement decisions
    assert result["recommended_quantity"] == 30
    assert result["priority"] == "HIGH"
    assert result["action"] == "URGENT REORDER"
    assert result["reorder_point"] == 32
    assert result["estimated_cost"] == 1050.0
    assert result["budget_escalation"] is False


if __name__ == "__main__":
    test_inventory_requiring_reorder()
    print("All logic_manager tests passed.")
