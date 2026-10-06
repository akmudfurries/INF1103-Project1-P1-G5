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
