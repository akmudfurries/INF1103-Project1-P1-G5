import json
import tempfile
import unittest
from pathlib import Path

from file_manager import load_records, save_records


class TestFileManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.test_dir.name) / "test_data.json"

    def tearDown(self):
        self.test_dir.cleanup()

    def test_save_and_load_records_success(self):
        sample_records = [{
            "item_id": "INV001",
            "item_name": "Screw",
            "current_stock": 42,
            "weekly_usage": 17,
            "lead_time_weeks": 2,
            "operational_notes": "Supplier was late thrice."
        }]
        self.assertTrue(save_records(self.file_path, sample_records))

        loaded = load_records(self.file_path)
        self.assertEqual(loaded, sample_records)

    def test_load_nonexistent_file(self):
        non_existent = Path(self.test_dir.name) / "missing.json"
        loaded = load_records(non_existent)
        self.assertEqual(loaded, [])

    def test_save_records_invalid_type(self):
        self.assertFalse(save_records(self.file_path, "not a list"))


if __name__ == "__main__":
    unittest.main()