# =====================================================================
# Test CMD: python -m unittest discover -s tests -v
import unittest

from data_manager import build_inventory_record
from data_manager import validate_inventory_record
from data_manager import build_procurement_record
from data_manager import validate_procurement_record

from data_manager import find_record_by_id


class TestInventoryRecord(unittest.TestCase):

    def test_build_valid_inventory_record(self):
        record = build_inventory_record(
            "INV001",
            "Industrial Printer Ribbon",
            42,
            15,
            2,
            "Demand increased recently."
        )

        self.assertEqual(record["item_id"], "INV001")
        self.assertEqual(record["current_stock"], 42)
        self.assertEqual(record["weekly_usage"], 15)
        self.assertEqual(record["lead_time_weeks"], 2)

    def test_missing_required_field(self):
        record = {
            "item_id": "INV001",
            "item_name": "Industrial Printer Ribbon",
            "current_stock": 42
        }

        with self.assertRaises(ValueError):
            validate_inventory_record(record)

    def test_negative_stock(self):
        with self.assertRaises(ValueError):
            build_inventory_record(
                "INV001",
                "Industrial Printer Ribbon",
                -1,
                15,
                2,
                "Demand increased recently."
            )

    def test_invalid_item_id(self):
        with self.assertRaises(ValueError):
            build_inventory_record(
                "",
                "Industrial Printer Ribbon",
                42,
                15,
                2,
                "Demand increased recently."
            )


class TestProcurementRecord(unittest.TestCase):

    def test_build_valid_procurement_record(self):
        record = build_procurement_record(
            "INV001",
            50,
            "HIGH",
            "REORDER"
        )

        self.assertEqual(record["item_id"], "INV001")
        self.assertEqual(record["recommended_quantity"], 50)
        self.assertEqual(record["priority"], "HIGH")
        self.assertEqual(record["action"], "REORDER")

    def test_missing_procurement_field(self):
        record = {
            "item_id": "INV001",
            "recommended_quantity": 50,
            "priority": "HIGH"
        }

        with self.assertRaises(ValueError):
            validate_procurement_record(record)

    def test_negative_recommended_quantity(self):
        with self.assertRaises(ValueError):
            build_procurement_record(
                "INV001",
                -10,
                "HIGH",
                "REORDER"
            )

    def test_invalid_procurement_item_id(self):
        with self.assertRaises(ValueError):
            build_procurement_record(
                "",
                50,
                "HIGH",
                "REORDER"
            )

    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            build_procurement_record(
                "INV001",
                50,
                "",
                "REORDER"
            )

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            build_procurement_record(
                "INV001",
                50,
                "HIGH",
                ""
            )

class TestRecordManagement(unittest.TestCase):
    
    def test_find_existing_record(self):
        records = [
            {"item_id": "INV001", "item_name": "Printer Ribbon"},
            {"item_id": "INV002", "item_name": "Printer Paper"}
        ]

        result = find_record_by_id(records, "INV002", "item_id")

        self.assertEqual(result["item_name"], "Printer Paper")
        
if __name__ == "__main__":
    unittest.main()

# =====================================================================
