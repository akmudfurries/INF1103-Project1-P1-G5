#reads and writes JSON FIlES

import json
import os
from pathlib import Path

DEFAULT_DATA = {"schema_version": 1, "records": []}


def ensure_json_file(file_path):
    """Ensure parent directories and the target JSON file exist."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_json(path, DEFAULT_DATA)

def save_json(file_path, data):
    """Save data to JSON using atomic temp file replacement."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2,)
            file.write("\n")
        os.replace(temp_path, path)
        return True
    except OSError as error:
        if temp_path.exists():
            temp_path.unlink()
        print(f"[Error] Failed writing to '{path}': {error}")
        return False