# =====================================================================
import unittest

from data_manager import build_inventory_record
from data_manager import validate_inventory_record


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


if __name__ == "__main__":
    unittest.main()

# =====================================================================
