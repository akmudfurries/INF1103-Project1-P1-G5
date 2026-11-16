import json
from tempfile import TemporaryDirectory
from pathlib import Path

from database_repo import DatabaseRepository
from migrate_json_to_sqlite import migrate_json_data


def run_migration_tests():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        db_path = str(temp_path / "test_migration.db")
        inv_json = temp_path / "inventory.json"
        proc_json = temp_path / "procurement_decisions.json"

        # setup dummy phase 1 json data files
        dummy_inventory = {
            "records": [
                {
                    "item_id": "INV-MIG-01",
                    "item_name": "Migrated Widget",
                    "category": "Components",
                    "current_stock": 75,
                    "weekly_usage": 12.5,
                    "lead_time_weeks": 2,
                    "operational_notes": "Imported from JSON",
                    "moq": 15,
                    "unit_cost": 25.0,
                    "budget": 1000.0
                }
            ]
        }

        dummy_procurement = {
            "records": [
                {
                    "procurement_id": "PROC-MIG-01",
                    "item_id": "INV-MIG-01",
                    "recommended_quantity": 40,
                    "priority": "HIGH",
                    "action": "BUY",
                    "approval_status": "APPROVED",
                    "rejection_reason": None,
                    "timestamp": "2026-11-01T10:00:00",
                    "status_updated": "2026-11-02T12:00:00",
                    "inventory_snapshot": {"current_stock": 75},
                    "ai_assessment": {"supply_risk": "MEDIUM"},
                    "analysis_result": {"notes": "Approved in Phase 1"}
                }
            ]
        }

        with open(inv_json, "w") as f:
            json.dump(dummy_inventory, f)

        with open(proc_json, "w") as f:
            json.dump(dummy_procurement, f)

        # run initial migration
        print("Running initial migration...")
        migrate_json_data(
            db_path=db_path,
            inventory_json_path=str(inv_json),
            procurement_json_path=str(proc_json)
        )

        repo = DatabaseRepository(db_path)

        #verify inventory record imported correctly
        inv_item = repo.fetch_inventory("INV-MIG-01")
        assert inv_item is not None
        assert inv_item["item_name"] == "Migrated Widget"
        assert inv_item["current_stock"] == 75
        print("PASS: Inventory record migration and persistence")

        #verify procurement record imported with original status
        proc_item = repo.fetch_procurement("PROC-MIG-01")
        assert proc_item is not None
        assert proc_item["approval_status"] == "APPROVED"
        assert proc_item["inventory_snapshot"] == {"current_stock": 75}
        assert proc_item["ai_assessment"] == {"supply_risk": "MEDIUM"}
        assert proc_item["analysis_result"] == {"notes": "Approved in Phase 1"}
        print("PASS: Procurement migration, status preservation, and snapshot deserialization")

        #verify MIGRATED history logging ensures previous_status is None and new_status keeps original status
        history = repo.fetch_procurement_history("PROC-MIG-01")
        assert len(history) == 1
        assert history[0]["event_type"] == "MIGRATED"
        assert history[0]["previous_status"] is None
        assert history[0]["new_status"] == "APPROVED"
        print("PASS: Migration audit history creation")

        repo.close()

        #run second migration to test idempotency and duplicate safety
        print("Running second migration (duplicate safety check)...")
        migrate_json_data(
            db_path=db_path,
            inventory_json_path=str(inv_json),
            procurement_json_path=str(proc_json)
        )

        repo = DatabaseRepository(db_path)
        all_inventory = repo.fetch_all_inventory()
        all_procurement = repo.fetch_all_procurement()

        #vrify no duplicates
        assert len(all_inventory) == 1
        assert len(all_procurement) == 1
        repo.close()
        print("PASS: Idempotency and duplicate-safe migration verification")

        print("\nAll migration tests passed successfully!")


if __name__ == "__main__":
    run_migration_tests()
