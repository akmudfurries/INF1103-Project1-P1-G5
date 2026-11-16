import json
import os
from database_repo import DatabaseRepository

def migrate_json_data(db_path="data/inventory.db", inventory_json_path="data/inventory.json", procurement_json_path="data/procurement_decisions.json"):
    """reads phase 1 json files and imports them safely into sqlite without duplicating data"""
    repo = DatabaseRepository(db_path)
    repo.initialize()

    imported_inv_count = 0
    skipped_inv_count = 0
    imported_proc_count = 0
    skipped_proc_count = 0

    # 1. migrate inventory records
    if os.path.exists(inventory_json_path):
        with open(inventory_json_path, "r") as f:
            try:
                inv_data = json.load(f)
                records = inv_data.get("records", []) if isinstance(inv_data, dict) else inv_data
                for record in records:
                    item_id = record.get("item_id")
                    if repo.fetch_inventory(item_id):
                        skipped_inv_count += 1
                        continue
                    success, err = repo.insert_inventory(record)
                    if success:
                        imported_inv_count += 1
                    else:
                        print(f"Error importing inventory item {item_id}: {err}")
            except Exception as e:
                print(f"Error reading inventory JSON: {e}")
    else:
        print(f"Inventory JSON not found at {inventory_json_path}")

    # 2. migrate procurement decision records
    if os.path.exists(procurement_json_path):
        with open(procurement_json_path, "r") as f:
            try:
                proc_data = json.load(f)
                records = proc_data.get("records", []) if isinstance(proc_data, dict) else proc_data
                for record in records:
                    proc_id = record.get("procurement_id")
                    if repo.fetch_procurement(proc_id):
                        skipped_proc_count += 1
                        continue

                    # insert using event_type="MIGRATED" to preserve original status
                    success, err = repo.insert_procurement(record, event_type="MIGRATED")
                    if success:
                        imported_proc_count += 1
                    else:
                        print(f"Error importing procurement record {proc_id}: {err}")
            except Exception as e:
                print(f"Error reading procurement JSON: {e}")
    else:
        print(f"Procurement JSON not found at {procurement_json_path}")

    repo.close()

    print("--- Migration Summary ---")
    print(f"Inventory Records Imported: {imported_inv_count} | Skipped: {skipped_inv_count}")
    print(f"Procurement Records Imported: {imported_proc_count} | Skipped: {skipped_proc_count}")

if __name__ == "__main__":
    migrate_json_data()