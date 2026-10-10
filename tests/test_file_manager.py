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

def test_load_missing_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        missing = Path(temp_dir) / "missing.json"
        loaded = load_records(missing)
        assert loaded == []

def test_save_invalid():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_data.json"
        assert save_records(file_path, "not a list") is False

def test_corrupted_json():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_data.json"
        #simulage corrupted file
        file_path.write_text("invalid json", encoding="utf-8")
        
        assert load_records(file_path) == []
        #timestamped file generated
        assert list(file_path.parent.glob("*_corrupted_*.json"))
        
        #check if new file is valid
        assert load_records(file_path) == []


if __name__ == "__main__":
    test_save_and_load_records_success()
    test_load_missing_file()
    test_save_invalid()
    test_corrupted_json()
    print("Test passed!")