from uuid import uuid4
from datetime import datetime

from models import InventoryRecord, ProcurementDecision

class DataManager:
    
    def __init__(self, repository):
        self._repository = repository

    def add_inventory_record(self, record):
        existing_record = self._repository.fetch_inventory(record.item_id)

        if existing_record is not None:
            return False, f"Duplicate ID: {record.item_id}"

        return self._repository.insert_inventory(record.to_dict())

    def get_inventory_records(self):
        records = self._repository.fetch_all_inventory()

        return [
            InventoryRecord.from_dict(record)
            for record in records
        ]

    def get_inventory_record(self, item_id):
        record = self._repository.fetch_inventory(item_id)

        if record is None:
            return None

        return InventoryRecord.from_dict(record)

    def remove_inventory_record(self, item_id):
        record = self._repository.fetch_inventory(item_id)

        if record is None:
            return False, f"Inventory record not found: {item_id}"

        return self._repository.delete_inventory(item_id)

    def create_procurement_record(self, decision):
        decision.procurement_id = f"PROC-{uuid4().hex[:8].upper()}"
        decision.timestamp = datetime.now().isoformat(timespec="seconds")
        decision.approval_status = "PENDING"
        decision.status_updated = None

        return self._repository.insert_procurement(decision.to_dict())

    def get_procurement_records(self):
        records = self._repository.fetch_all_procurement()

        return[
            ProcurementDecision.from_dict(record)
            for record in records
        ]

    def get_procurement_record(self, procurement_id):
        record = self._repository.fetch_procurement(procurement_id)

        if record is None:
            return None

        return ProcurementDecision.from_dict(record)

    def update_procurement_status(
            self,
            procurement_id,
            status,
            rejection_reason=None
    ):
        valid_statuses = {"APPROVED", "REJECTED", "DEFER"}

        if status not in valid_statuses:
            return False, "Invalid procurement status."

        if status == "REJECTED":
            if not isinstance(rejection_reason, str) or not rejection_reason.strip():
                return False, "Rejection reason is required."

        elif status == "APPROVED":
            if rejection_reason is not None:
                return False, "Rejection reason is only allowed when status is REJECTED."
        
        elif status == "DEFER":
            if rejection_reason is not None:
                return False, "Rejection reason is only allowed when status is REJECTED."
            
            return True, None

        status_updated = datetime.now().isoformat(timespec= "seconds")

        return self._repository.update_procurement_status(
            procurement_id,
            status,
            rejection_reason,
            status_updated
        )

    def delete_procurement_record(self, procurement_id):
        record = self._repository.fetch_procurement(procurement_id)

        if record is None:
            return False, f"Procurement record not found: {procurement_id}"

        return self._repository.delete_procurement(procurement_id)

    def get_procurement_history(self, procurement_id):
        return self._repository.fetch_procurement_history(procurement_id)

    
