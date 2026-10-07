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
        "REORDER"
    )

    assert record["item_id"] == "INV001"
    assert record["recommended_quantity"] == 50
    assert record["priority"] == "HIGH"
    assert record["action"] == "REORDER"


def test_missing_procurement_field():
    record = {
        "item_id": "INV001",
        "recommended_quantity": 50,
        "priority": "HIGH"
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
            "REORDER"
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
            "REORDER"
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
            "REORDER"
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
            ""
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
