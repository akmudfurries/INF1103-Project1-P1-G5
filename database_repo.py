import sqlite3
import json
from datetime import datetime

class DatabaseRepository:
    def __init__(self, db_path):
        """initialise the database connection and foreign keys."""
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            #foreign key
            self.conn.execute("PRAGMA foreign_keys = ON;")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to database at {db_path}: {e}")

    def initialize(self):
        """create database tables if it doesntexist"""
        cursor = self.conn.cursor()
        try:
            #inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id TEXT PRIMARY KEY,
                    item_name TEXT,
                    category TEXT,
                    current_stock INTEGER,
                    weekly_usage REAL,
                    lead_time_weeks INTEGER,
                    operational_notes TEXT,
                    moq INTEGER,
                    unit_cost REAL,
                    budget REAL
                )
            """)

            #procurement table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procurement (
                    procurement_id TEXT PRIMARY KEY,
                    item_id TEXT,
                    recommended_quantity INTEGER,
                    priority TEXT,
                    action TEXT,
                    approval_status TEXT,
                    rejection_reason TEXT,
                    timestamp TEXT,
                    status_updated TEXT,
                    inventory_snapshot_json TEXT,
                    ai_assessment_json TEXT,
                    analysis_result_json TEXT
                )
            """)

            #procurement history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procurement_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    procurement_id TEXT,
                    event_type TEXT,
                    previous_status TEXT,
                    new_status TEXT,
                    reason TEXT,
                    changed_at TEXT,
                    FOREIGN KEY (procurement_id) REFERENCES procurement(procurement_id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to initialize database tables: {e}")

    def close(self):
        """close the sqlite connection"""
        if self.conn:
            self.conn.close()