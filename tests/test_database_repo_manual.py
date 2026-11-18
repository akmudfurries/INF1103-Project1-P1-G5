
from tempfile import TemporaryDirectory
from pathlib import Path

from database_repo import DatabaseRepository


def run_tests():
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        repo = DatabaseRepository(str(db_path))

        try:
            repo.initialize()

            # 1. Create procurement record
            record = {
                "procurement_id": "PROC-TEST001",
                "item_id": "INV007",
                "recommended_quantity": 30,
                "priority": "HIGH",
                "action": "URGENT REORDER",
                "approval_status": "PENDING",
                "rejection_reason": None,
                "timestamp": "2026-11-15T15:00:00",
                "status_updated": None,
                "inventory_snapshot": {"current_stock": 18},
                "ai_assessment": {"supply_risk": "HIGH"},
                "analysis_result": {"reorder_point": 32}
            }

            success, error = repo.insert_procurement(record)
            assert success, error
            print("PASS: Procurement creation")

            # 2. Retrieve procurement and verify JSON fields
            retrieved = repo.fetch_procurement("PROC-TEST001")

            assert retrieved is not None
            assert retrieved["inventory_snapshot"] == {"current_stock": 18}
            assert retrieved["ai_assessment"] == {"supply_risk": "HIGH"}
            assert retrieved["analysis_result"] == {"reorder_point": 32}
            print("PASS: Procurement retrieval and JSON deserialization")

            # 3. Verify initial CREATED history
            history = repo.fetch_procurement_history("PROC-TEST001")

            assert len(history) == 1
            assert history[0]["event_type"] == "CREATED"
            assert history[0]["previous_status"] is None
            assert history[0]["new_status"] == "PENDING"
            print("PASS: Initial procurement history")

            # 4. Approve procurement
            success, error = repo.update_procurement_status(
                "PROC-TEST001",
                "APPROVED",
                None,
                "2026-11-15T15:10:00"
            )

            assert success, error

            history = repo.fetch_procurement_history("PROC-TEST001")

            assert len(history) == 2
            assert history[1]["previous_status"] == "PENDING"
            assert history[1]["new_status"] == "APPROVED"
            print("PASS: Status update and history")

            # 5. Repeat same status, no duplicate history
            success, error = repo.update_procurement_status(
                "PROC-TEST001",
                "APPROVED",
                None,
                "2026-11-15T15:20:00"
            )

            assert success, error

            history = repo.fetch_procurement_history("PROC-TEST001")
            assert len(history) == 2
            print("PASS: Duplicate history prevention")

            # 6. Verify newest-first retrieval method works
            records = repo.fetch_all_procurement()
            assert len(records) == 1
            assert records[0]["procurement_id"] == "PROC-TEST001"
            print("PASS: Retrieve all procurement records")

                        # 8. Test procurement creation rollback
            repo.conn.execute("""
                CREATE TRIGGER fail_created_history
                BEFORE INSERT ON procurement_history
                WHEN NEW.event_type = 'CREATED'
                BEGIN
                    SELECT RAISE(ABORT, 'Forced history failure');
                END;
            """)
            repo.conn.commit()

            failed_record = {
                **record,
                "procurement_id": "PROC-FAIL001"
            }

            success, error = repo.insert_procurement(failed_record)

            assert not success
            assert repo.fetch_procurement("PROC-FAIL001") is None

            repo.conn.execute("DROP TRIGGER fail_created_history")
            repo.conn.commit()

            print("PASS: Procurement creation rollback")

            # 7. Test status update rollback
            repo.conn.execute("""
                CREATE TRIGGER fail_status_history
                BEFORE INSERT ON procurement_history
                WHEN NEW.event_type = 'STATUS_CHANGED'
                BEGIN
                    SELECT RAISE(ABORT, 'Forced history failure');
                END;
            """)
            repo.conn.commit()

            success, error = repo.update_procurement_status(
                "PROC-TEST001",
                "REJECTED",
                "Test rejection",
                "2026-11-15T15:30:00"
            )

            assert not success

            retrieved = repo.fetch_procurement("PROC-TEST001")
            assert retrieved["approval_status"] == "APPROVED"

            history = repo.fetch_procurement_history("PROC-TEST001")
            assert len(history) == 2

            repo.conn.execute("DROP TRIGGER fail_status_history")
            repo.conn.commit()

            print("PASS: Status update rollback")

            # 8. Delete procurement and verify cascade deletion
            success, error = repo.delete_procurement("PROC-TEST001")
            assert success, error

            assert repo.fetch_procurement("PROC-TEST001") is None
            assert repo.fetch_procurement_history("PROC-TEST001") == []
            print("PASS: Procurement deletion and history cascade")

            print("\nAll database repository tests passed.")

            

        finally:
            repo.close()


if __name__ == "__main__":
    run_tests()