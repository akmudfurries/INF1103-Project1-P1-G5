# =====================================================================
# Install pytest: python -m pip install pytest
# Test CMD: pytest -v

import pytest

from data_manager import build_inventory_record
from data_manager import validate_inventory_record
from data_manager import build_procurement_record
from data_manager import validate_procurement_record

from data_manager import find_record_by_id
from data_manager import add_record
from data_manager import update_record
from data_manager import link_procurement_to_item
from data_manager import get_records_for_item
from data_manager import create_procurement_from_business_rule

from file_manager import save_records, load_records

# =====================================================================
# Inventory Record Tests
# =====================================================================

def test_build_valid_inventory_record():
    record = build_inventory_record(
        "INV001",
        "Industrial Printer Ribbon",
        42,
        15,
        2,
        "Demand increased recently."
    )

    assert record["item_id"] == "INV001"
    assert record["current_stock"] == 42
    assert record["weekly_usage"] == 15
    assert record["lead_time_weeks"] == 2


def test_missing_required_field():
    record = {
        "item_id": "INV001",
        "item_name": "Industrial Printer Ribbon",
        "current_stock": 42
    }

    try:
        validate_inventory_record(record)
        assert False, "Expected ValueError for missing required field"
    except ValueError:
        pass


def test_negative_stock():
    try:
        build_inventory_record(
            "INV001",
            "Industrial Printer Ribbon",
            -1,
            15,
            2,
            "Demand increased recently."
        )
        assert False, "Expected ValueError for negative stock"
    except ValueError:
        pass


def test_invalid_item_id():
    try:
        build_inventory_record(
            "",
            "Industrial Printer Ribbon",
            42,
            15,
            2,
            "Demand increased recently."
        )
        assert False, "Expected ValueError for invalid item ID"
    except ValueError:
        pass


# =====================================================================
# Procurement Record Tests
# =====================================================================

def test_build_valid_procurement_record():
    record = build_procurement_record(
        "INV001",
        50,
        "HIGH",
        "REORDER",
        "PENDING"
    )

    assert record["item_id"] == "INV001"
    assert record["recommended_quantity"] == 50
    assert record["priority"] == "HIGH"
    assert record["action"] == "REORDER"
    assert record["approval_status"] == "PENDING"


def test_missing_procurement_field():
    record = {
        "item_id": "INV001",
        "recommended_quantity": 50,
        "priority": "HIGH",
        "approval_status": "PENDING"
    }

    try:
        validate_procurement_record(record)
        assert False, "Expected ValueError for missing procurement field"
    except ValueError:
        pass


def test_negative_recommended_quantity():
    try:
        build_procurement_record(
            "INV001",
            -10,
            "HIGH",
            "REORDER",
            "PENDING"
        )
        assert False, "Expected ValueError for negative quantity"
    except ValueError:
        pass


def test_invalid_procurement_item_id():
    try:
        build_procurement_record(
            "",
            50,
            "HIGH",
            "REORDER",
            "PENDING"
        )
        assert False, "Expected ValueError for invalid item ID"
    except ValueError:
        pass


def test_invalid_priority():
    try:
        build_procurement_record(
            "INV001",
            50,
            "",
            "REORDER",
            "PENDING"
        )
        assert False, "Expected ValueError for invalid priority"
    except ValueError:
        pass


def test_invalid_action():
    try:
        build_procurement_record(
            "INV001",
            50,
            "HIGH",
            "",
            "PENDING"
        )
        assert False, "Expected ValueError for invalid action"
    except ValueError:
        pass

# =====================================================================
# Record Management Tests
# =====================================================================

def test_find_existing_record():
    records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"},
        {"item_id": "INV002", "item_name": "Printer Paper"}
    ]

    result = find_record_by_id(records, "INV002", "item_id")

    assert result["item_name"] == "Printer Paper"


def test_find_missing_record():
    records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"},
        {"item_id": "INV002", "item_name": "Printer Paper"}
    ]

    result = find_record_by_id(records, "INV999", "item_id")

    assert result is None


def test_add_new_record():
    records = [
        {"item_id": "INV1001", "item_name": "Printer Ribbon"}
    ]

    new_record = {
        "item_id": "INV002",
        "item_name": "Printer Paper"
    }

    success, error = add_record(records, new_record, "item_id")

    assert success is True
    assert error is None
    assert len(records) == 2
    assert records[1]["item_id"] == "INV002"


def test_add_duplicate_record():
    records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"}
    ]

    duplicate_record = {
        "item_id": "INV001",
        "item_name": "Printer Paper"
    }

    success, error = add_record(records, duplicate_record, "item_id")

    assert success is False
    assert error == "Duplicate ID: INV001"
    assert len(records) == 1


def test_add_missing_id():
    records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"}
    ]

    missing_id_record = {
        "item_name": "Printer Paper"
    }

    success, error = add_record(records, missing_id_record, "item_id")

    assert success is False
    assert error == "Record is missing its ID."
    assert len(records) == 1

def test_update_existing_record():
    records = [
        {
            "item_id": "INV001",
            "item_name": "Printer Ribbon",
            "current_stock": 42
        }
    ]

    updates = {
        "current_stock": 30
    }

    success, error = update_record(records, "INV001", updates, "item_id")

    assert success is True
    assert error is None
    assert records[0]["current_stock"] == 30

def test_update_missing_record():
    records = [
        {
            "item_id": "INV001",
            "item_name": "Printer Ribbon",
            "current_stock": 42
        }
    ]

    updates = {
        "current_stock": 30
    }

    success, error = update_record(records, "INV999", updates, "item_id")

    assert success is False
    assert error == "Record not found: INV999"
    assert records[0]["current_stock"] == 42

def test_update_record_id():
    records = [
        {
            "item_id": "INV001",
            "item_name": "Printer Ribbon",
            "current_stock": 42
        }
    ]

    updates = {
        "item_id": "INV999"
    }

    success, error = update_record(records, "INV001", updates, "item_id")

    assert success is False
    assert error == "Record ID cannot be changed."
    assert records[0]["item_id"] == "INV001"

# =====================================================================
# Procurement Tests
# =====================================================================

def test_link_procurement_to_existing_item():
    inventory_records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"}
    ]

    procurement_record = {
        "procurement_id": "PRC001",
        "item_id": "INV001",
        "recommended_quantity": 50
    }

    success, error = link_procurement_to_item(
        procurement_record,
        inventory_records
    )

    assert success is True
    assert error is None

def test_link_procurement_to_missing_item():
    inventory_records = [
        {"item_id": "INV001", "item_name": "Printer Ribbon"}
    ]

    procurement_record = {
        "procurement_id": "PRC002",
        "item_id": "INV999",
        "recommended_quantity": 20
    }

    success, error = link_procurement_to_item(
        procurement_record,
        inventory_records
    )

    assert success is False
    assert error == "Inventory item not found: INV999"

def test_get_records_for_existing_item():
    records = [
        {"procurement_id": "PRC001", "item_id": "INV001"},
        {"procurement_id": "PRC002", "item_id": "INV002"},
        {"procurement_id": "PRC003", "item_id": "INV001"}
    ]

    result = get_records_for_item(records, "INV001")

    assert len(result) == 2
    assert result[0]["procurement_id"] == "PRC001"
    assert result[1]["procurement_id"] == "PRC003"

def test_get_records_for_missing_item():
    records = [
        {"procurement_id": "PRC001", "item_id": "INV001"}
    ]

    result = get_records_for_item(records, "INV999")

    assert result == []

def test_get_records_for_missing_item():
    records = [
        {"procurement_id": "PRC001", "item_id": "INV001"}
    ]

    result = get_records_for_item(records, "INV999")

    assert result == []

def test_create_procurement_from_business_rule():
    business_rule_output = {
        "recommended_quantity": 50,
        "priority": "HIGH",
        "action": "REORDER"
    }

    record = create_procurement_from_business_rule(
        "INV001",
        business_rule_output,
        "PENDING"
    )

    assert record["item_id"] == "INV001"
    assert record["recommended_quantity"] == 50
    assert record["priority"] == "HIGH"
    assert record["action"] == "REORDER"
    assert record["approval_status"] == "PENDING"

def test_inventory_record_persistence(tmp_path):
    record = build_inventory_record(
        "INV001",
        "Industrial Printer Ribbon",
        42,
        15,
        2, 
        "Demand increased recently."
    )

    file_path = str(tmp_path / "inventory.json")

    save_records(file_path, [record])

    loaded_records = load_records(file_path)

    assert len(loaded_records) == 1
    assert loaded_records[0] == record

def test_store_approval_status_and_procurement_decision(tmp_path):
    records = [
        build_procurement_record(
            "INV001",
            50,
            "HIGH",
            "REORDER",
            "PENDING"
        )
    ]

    updates = {
        "approval_status": "APPROVED"
    }

    success, error = update_record(
        records,
        "INV001",
        updates,
        "item_id"
    )

    assert success is True
    assert error is None
    assert records[0]["approval_status"] == "APPROVED"

    file_path = str(tmp_path / "procurement.json")

    save_records(file_path, records)

    loaded_records = load_records(file_path)

    assert loaded_records[0]["approval_status"] == "APPROVED"
    assert loaded_records[0]["recommended_quantity"] == 50
    assert loaded_records[0]["action"] == "REORDER"

def test_manage_extended_inventory_data():
    records = []

    extended_record = {
        "item_id": "INV001",
        "item_name": "Industrial Printer Ribbon",
        "current_stock": 42,
        "weekly usage": 15,
        "lead_time_weeks": 2,
        "operational_notes": "Demand increased recently",
        "safety_stock": 15,
        "moq": 50,
        "unit_cost": 12.00,
        "budget": 500.00,
        "stock_coverage": 2.8,
        "reorder_point": 45
    }

    success, error = add_record(
        records, 
        extended_record,
        "item_id"
    )

    assert success is True
    assert error is None

    updates = {
        "moq": 60,
        "budget": 600.00,
        "safety_stock": 20
    }

    success, error = update_record(
        records,
        "INV001",
        updates,
        "item_id"
    )

    assert success is True
    assert error is None

    record = find_record_by_id(
        records,
        "INV001",
        "item_id"
    )

    assert record["moq"] == 60
    assert record["budget"] == 600.00
    assert record["safety_stock"] == 20
    assert record["unit_cost"] == 12.00
    assert record["stock_coverage"] == 2.8
    assert record["reorder_point"] == 45

def test_manage_extended_procurement_data():
    records = [
        build_procurement_record(
            "INV001",
            50,
            "HIGH",
            "REORDER",
            "PENDING"
        )
    ]

    extended_updates = {
        "estimated_cost": 600.00,
        "budget_escalation": True
    }

    success, error= update_record(
        records,
        "INV001",
        extended_updates,
        "item_id"
    )

    assert success is True
    assert error is None

    record = find_record_by_id(
        records,
        "INV001",
        "item_id"
    )

    assert record["estimated_cost"] == 600.00
    assert record["budget_escalation"] is True