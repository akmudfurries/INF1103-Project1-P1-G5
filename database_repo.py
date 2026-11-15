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

    #inventory stuff
    def insert_inventory(self, record):
        #insert or replace inventory record dict
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO inventory 
                (item_id, item_name, category, current_stock, weekly_usage, 
                 lead_time_weeks, operational_notes, moq, unit_cost, budget)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("item_id"),
                record.get("item_name"),
                record.get("category", "Uncategorized"),
                record.get("current_stock", 0),
                record.get("weekly_usage", 0.0),
                record.get("lead_time_weeks", 0),
                record.get("operational_notes", ""),
                record.get("moq", 0),
                record.get("unit_cost", 0.0),
                record.get("budget", 0.0)
            ))
            self.conn.commit()
            return True, None
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def fetch_all_inventory(self):
        #fetch inventory records as a list of dict
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetch_inventory(self, item_id):
        #fetch single inventory record
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_inventory(self, item_id):
        #delete inventory record
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
            if cursor.rowcount == 0:
                return False, f"Inventory item {item_id} not found."
            self.conn.commit()
            return True, None
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    # -------------------------
    # Procurement persistence
    # -------------------------

    def _deserialize_procurement(self, row):
        """Convert a SQLite procurement row into a dictionary."""
        record = dict(row)

        json_fields = {
            "inventory_snapshot_json": "inventory_snapshot",
            "ai_assessment_json": "ai_assessment",
            "analysis_result_json": "analysis_result"
        }

        for db_field, model_field in json_fields.items():
            value = record.pop(db_field)
            record[model_field] = json.loads(value) if value is not None else None

        return record

    def insert_procurement(self, record, event_type="CREATED"):
        """Insert a procurement decision and its initial history event."""
        valid_statuses = {"PENDING", "APPROVED", "REJECTED"}
        valid_event_types = {"CREATED", "MIGRATED"}

        status = record.get("approval_status", "PENDING")

        if status not in valid_statuses:
            return False, "Invalid procurement approval status."

        if event_type not in valid_event_types:
            return False, "Invalid procurement history event type."

        if event_type == "CREATED" and status != "PENDING":
            return False, "New procurement records must have PENDING status."

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO procurement (
                    procurement_id,
                    item_id,
                    recommended_quantity,
                    priority,
                    action,
                    approval_status,
                    rejection_reason,
                    timestamp,
                    status_updated,
                    inventory_snapshot_json,
                    ai_assessment_json,
                    analysis_result_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("procurement_id"),
                record.get("item_id"),
                record.get("recommended_quantity"),
                record.get("priority"),
                record.get("action"),
                status,
                record.get("rejection_reason"),
                record.get("timestamp"),
                record.get("status_updated"),
                json.dumps(record.get("inventory_snapshot")),
                json.dumps(record.get("ai_assessment")),
                json.dumps(record.get("analysis_result"))
            ))

            changed_at = datetime.now().isoformat(timespec="seconds")

            cursor.execute("""
                INSERT INTO procurement_history (
                    procurement_id,
                    event_type,
                    previous_status,
                    new_status,
                    reason,
                    changed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                record.get("procurement_id"),
                event_type,
                None,
                status,
                record.get("rejection_reason"),
                changed_at
            ))

            self.conn.commit()
            return True, None

        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def fetch_all_procurement(self):
        """Retrieve all procurement decisions."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT *
            FROM procurement
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()

        return [
            self._deserialize_procurement(row)
            for row in rows
        ]
    
    def fetch_procurement(self, procurement_id):
        """Retrieve one procurement decision by ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM procurement
            WHERE procurement_id = ?
        """, (procurement_id,))

        row = cursor.fetchone()

        return self._deserialize_procurement(row) if row else None

    def update_procurement_status(
        self,
        procurement_id,
        status,
        rejection_reason=None,
        status_updated=None
    ):
        """Update procurement status and record its history atomically."""
        valid_statuses = {"PENDING", "APPROVED", "REJECTED"}

        if status not in valid_statuses:
            return False, "Invalid procurement approval status."

        if status == "REJECTED":
            if not isinstance(rejection_reason, str) or not rejection_reason.strip():
                return False, "Rejection reason is required."
        elif rejection_reason is not None:
            return False, "Rejection reason is only allowed for rejected decisions."

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT approval_status
                FROM procurement
                WHERE procurement_id = ?
            """, (procurement_id,))

            row = cursor.fetchone()

            if row is None:
                return False, f"Procurement record not found: {procurement_id}"

            previous_status = row["approval_status"]

            # Do not create duplicate history events for unchanged statuses.
            if previous_status == status:
                return True, None

            changed_at = datetime.now().isoformat(timespec="seconds")

            cursor.execute("""
                UPDATE procurement
                SET approval_status = ?,
                    rejection_reason = ?,
                    status_updated = ?
                WHERE procurement_id = ?
            """, (
                status,
                rejection_reason,
                status_updated or changed_at,
                procurement_id
            ))

            cursor.execute("""
                INSERT INTO procurement_history (
                    procurement_id,
                    event_type,
                    previous_status,
                    new_status,
                    reason,
                    changed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                procurement_id,
                "STATUS_CHANGED",
                previous_status,
                status,
                rejection_reason,
                changed_at
            ))

            self.conn.commit()
            return True, None

        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def fetch_procurement_history(self, procurement_id):
        """Retrieve procurement history in chronological order."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM procurement_history
            WHERE procurement_id = ?
            ORDER BY changed_at ASC, history_id ASC
        """, (procurement_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_procurement(self, procurement_id):
        """Delete a procurement decision and its associated history."""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM procurement
                WHERE procurement_id = ?
            """, (procurement_id,))

            if cursor.rowcount == 0:
                return False, f"Procurement record not found: {procurement_id}"

            self.conn.commit()
            return True, None

        except Exception as e:
            self.conn.rollback()
            return False, str(e)
