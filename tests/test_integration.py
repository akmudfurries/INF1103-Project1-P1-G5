from tempfile import TemporaryDirectory
from pathlib import Path

from database_repo import DatabaseRepository
from data_manager import DataManager
from models import InventoryRecord, ProcurementDecision

def test_data_manager_integration():
    with TemporaryDirectory() as temp_dir:
        db_path = str(Path(temp_dir) / "integration.db")
        repo = DatabaseRepository(db_path)
        repo.initialize()

        manager = DataManager(repo)

        # 1. Test adding inventory via DataManager
        inv_record = InventoryRecord(
            item_id="INV-INT-01",
            item_name="Integration Widget",
            category="Components",
            current_stock=100,
            weekly_usage=10.0,
            lead_time_weeks=2,
            operational_notes="Integration test record",
            moq=20,
            unit_cost=15.0,
            budget=500.0
        )
        success, err = manager.add_inventory_record(inv_record)
        assert success, err

        fetched_inv = manager.get_inventory_record("INV-INT-01")
        assert fetched_inv is not None
        assert fetched_inv.item_name == "Integration Widget"
        print("PASS: DataManager inventory insertion and retrieval")

        # 2. Test creating procurement record via DataManager
        proc_decision = ProcurementDecision(
            item_id="INV-INT-01",
            recommended_quantity=50,
            priority="HIGH",
            action="REORDER",
            inventory_snapshot={"current_stock": 100},
            ai_assessment={"risk": "LOW"},
            analysis_result={"notes": "Standard reorder"}
        )
        success, err = manager.create_procurement_record(proc_decision)
        assert success, err
        assert proc_decision.procurement_id is not None
        assert proc_decision.approval_status == "PENDING"
        print("PASS: DataManager procurement creation")

        # 3. Test DEFER handling in DataManager (handled locally without hitting repo errors)
        success, err = manager.update_procurement_status(proc_decision.procurement_id, "DEFER")
        assert success is True
        assert err is None
        print("PASS: DataManager DEFER status handling")

        # 4. Test approving procurement status
        success, err = manager.update_procurement_status(proc_decision.procurement_id, "APPROVED")
        assert success, err

        updated_proc = manager.get_procurement_record(proc_decision.procurement_id)
        assert updated_proc.approval_status == "APPROVED"
        print("PASS: DataManager approval status update")

        # 5. Verify history tracking through DataManager
        history = manager.get_procurement_history(proc_decision.procurement_id)
        assert len(history) >= 2  # CREATED + STATUS_CHANGED
        print("PASS: DataManager history tracking")

        # 6. Test inventory removal
        success, err = manager.remove_inventory_record("INV-INT-01")
        assert success, err
        assert manager.get_inventory_record("INV-INT-01") is None
        print("PASS: DataManager inventory deletion")

        repo.close()
        print("\nAll DataManager integration tests passed successfully!")

if __name__ == "__main__":
    test_data_manager_integration()