#reads and writes JSON FIlES

import json
import os
from pathlib import Path

DEFAULT_DATA = {"schema_version": 1, "records": []}


def ensure_json_file(file_path):
    #ensure parent directories and target json file exist
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_json(path, DEFAULT_DATA)

def save_json(file_path, data):
    #save data directly to json file
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file)
            file.write("\n")
        return True
    except OSError as error:
        print(f"[Error] Failed writing to '{path}': {error}")
        return False

def load_json(file_path):
    #load and parse json file with error handling
    path = Path(file_path)
    ensure_json_file(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                save_json(path, DEFAULT_DATA)
                return DEFAULT_DATA
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Error] Failed reading '{path}': {error}")
        return None

