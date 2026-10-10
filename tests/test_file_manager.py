import tempfile
from pathlib import Path
from file_manager import load_records, save_records


def test_save_and_load_records_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_data.json"
        sample_records = [{
            "item_id": "INV007",
            "item_name": "Screw",
            "current_stock": 49,
            "weekly_usage": 13,
            "lead_time_weeks": 2,
            "operational_notes": "Supplier was late thrice."
        }]
        assert save_records(file_path, sample_records) is True
        loaded = load_records(file_path)
        assert loaded == sample_records


if __name__ == "__main__":
    test_save_and_load_records_success()
    print("Test passed!")