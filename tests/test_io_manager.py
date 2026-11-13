# ====================================================
# Run: python -m pytest tests/test_io_manager.py -v
# ====================================================

import pytest
from unittest.mock import patch
from io_manager import IOManager

@pytest.fixture
def io_manager():
    return IOManager()

def test_print_header(io_manager, capsys):
    io_manager.print_header()
    captured = capsys.readouterr()
    assert len(captured.out) > 0

@patch('builtins.input', side_effect=['6'])
def test_get_main_menu_choice(mock_input, io_manager):
    choice = io_manager.get_main_menu_choice()
    assert choice == '6'

@patch('builtins.input', side_effect=['q'])
def test_prompt_inventory_record_cancel(mock_input, io_manager):
    result = io_manager.prompt_inventory_record()
    assert result is None

def test_display_inventory_records_empty(io_manager, capsys):
    io_manager.display_inventory_records([])
    captured = capsys.readouterr()
    assert "No inventory records found" in captured.out

def test_display_inventory_records_populated(io_manager, capsys):
    records = [{"item_id": "ITEM-1", "item_name": "Screws", "category": "Hardware", "current_stock": 100, "operational_notes": "Standard stock"}]
    io_manager.display_inventory_records(records)
    captured = capsys.readouterr()
    assert "Screws" in captured.out
    assert "Hardware" in captured.out

@patch('builtins.input', side_effect=['Y'])
def test_prompt_user_approval_approve(mock_input, io_manager):
    status, reason = io_manager.prompt_user_approval()
    assert status == "APPROVED"
    assert reason is None

@patch('builtins.input', side_effect=['N', 'Out of stock concerns'])
def test_prompt_user_approval_reject(mock_input, io_manager):
    status, reason = io_manager.prompt_user_approval()
    assert status == "REJECTED"
    assert reason == "Out of stock concerns"

@patch('builtins.input', side_effect=['D'])
def test_prompt_user_approval_defer(mock_input, io_manager):
    status, reason = io_manager.prompt_user_approval()
    assert status == "DEFER"
    assert reason is None

def test_display_full_procurement_report(io_manager, capsys):
    inv = {"item_name": "Widget", "category": "Parts", "current_stock": 50, "weekly_usage": 10.0, "lead_time_weeks": 2, "operational_notes": "Stable."}
    ai = {"demand_level": "medium", "demand_trend": "stable", "supply_risk": "low", "operational_importance": "medium", "reason": "Stable demand."}
    res = {"recommended_quantity": 20, "stock_coverage": 5.0, "priority": "MEDIUM", "action": "REORDER"}
    
    io_manager.display_full_procurement_report(inv, ai, res)
    captured = capsys.readouterr()
    assert "Widget" in captured.out
    assert "Stock Coverage:" in captured.out
    assert "REORDER" in captured.out

@patch('builtins.input', side_effect=['1'])
def test_display_previous_recommendations(mock_input, io_manager):
    records = [{"procurement_id": "PROC-12345678", "item_id": "ITEM-1", "action": "REORDER", "approval_status": "PENDING", "timestamp": "2026-10-14T16:54:03"}]
    pid = io_manager.display_previous_recommendations(records)
    assert pid == "PROC-12345678"

@patch('builtins.input', side_effect=['q'])
def test_display_previous_recommendations_cancel(mock_input, io_manager):
    records = [{"procurement_id": "PROC-12345678", "item_id": "ITEM-1", "action": "REORDER", "approval_status": "PENDING", "timestamp": "2026-10-14T16:54:03"}]
    pid = io_manager.display_previous_recommendations(records)
    assert pid is None

def test_display_historical_procurement_report(io_manager, capsys):
    record = {
        "procurement_id": "PROC-87654321",
        "item_id": "ITEM-2",
        "timestamp": "2026-10-14T16:54:03",
        "approval_status": "APPROVED",
        "action": "REORDER",
        "recommended_quantity": 50,
        "priority": "HIGH",
        "inventory_snapshot": {"current_stock": 5},
        "ai_assessment": {"reason": "Urgent need."},
        "analysis_result": {"recommended_quantity": 50}
    }
    io_manager.display_historical_procurement_report(record)
    captured = capsys.readouterr()
    assert "PROC-87654321" in captured.out
    assert "APPROVED" in captured.out

def test_display_procurement_history(io_manager, capsys):
    history = [{"changed_at": "2026-10-14T16:54:03", "event_type": "CREATED", "previous_status": "None", "new_status": "PENDING", "reason": None}]
    io_manager.display_procurement_history(history)
    captured = capsys.readouterr()
    assert "PROCUREMENT STATUS HISTORY" in captured.out
    assert "PENDING" in captured.out

@patch('builtins.input', side_effect=['1', '1', 'Approved by manager'])
def test_prompt_record_action(mock_input, io_manager):
    record = {"approval_status": "PENDING"}
    action, updates = io_manager.prompt_record_action(record)
    assert action == "UPDATE"
    assert updates["approval_status"] == "APPROVED"

# --- Simulation Feature Tests ---

@patch('builtins.input', side_effect=['q'])
def test_prompt_simulation_parameters_cancel(mock_input, io_manager):
    result = io_manager.prompt_simulation_parameters()
    assert result is None

@patch('builtins.input', side_effect=['-5', '12.5', '3'])
def test_prompt_simulation_parameters_invalid_then_valid(mock_input, io_manager):
    # First inputs -5 (invalid usage), then 12.5 (valid usage), then 3 (valid lead time)
    usage, lead_time = io_manager.prompt_simulation_parameters()
    assert usage == 12.5
    assert lead_time == 3

def test_display_simulation_comparison(io_manager, capsys):
    base = {"recommended_quantity": 30, "reorder_point": 25, "safety_stock": 10, "priority": "MEDIUM", "action": "REORDER", "estimated_cost": 300.0}
    sim = {"recommended_quantity": 60, "reorder_point": 40, "safety_stock": 15, "priority": "HIGH", "action": "URGENT REORDER", "estimated_cost": 600.0}
    
    io_manager.display_simulation_comparison(base, sim)
    captured = capsys.readouterr()
    assert "SIMULATION COMPARISON REPORT" in captured.out
    assert "60" in captured.out
    assert "URGENT REORDER" in captured.out