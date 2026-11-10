from data_manager import DataManager

class FakeRepository:
    def __init__(self):
        self.inventory_records = []
        self.procurement_records = []
        self.procurement_history = []

    def fetch_inventory(self, item_id):
        for record in self.inventory_records:
            if record["item_id"] == item_id:
                return record

        return None

    def fetch_all_inventory(self):
        return self.inventory_records

    def insert_inventory(self, record):
        self.inventory_records.append(record)
        return True, None

    def delete_inventory(self, item_id):
        record = self.fetch_inventory(item_id)

        if record is None:
            return False, f"Inventory record not found: {item_id}"

        self.inventory_records.remove(record)
        return True, None

    def fetch_procurement(self, procurement_id):
        for record in self.procurement_records:
            if record["procurement_id"] == procurement_id:
                return record

        return None

    def fetch_all_procurement(self):
        return self.procurement_records

    def insert_procurement(self, record):
        self.procurement_records.append(record)
        return True, None

    def update_procurement_status(
            self, 
            procurement_id,
            status,
            rejection_reason = None,
            status_updated = None
    ):
        record = self.fetch_procurement(procurement_id)

        if record is None:
            return False, f"Procurement record not found: {procurement_id}"

        previous_status =  record["approval_status"]

        record["approval_status"] = status
        record["rejection_reason"] = rejection_reason
        record["status_updated"] = status_updated

        self.procurement_history.append({
            "procurement_id": procurement_id,
            "previous_status": previous_status,
            "new_status": status,
            "reason": rejection_reason,
            "changed_at": status_updated
        })

        return True, None

    def delete_procurement(self, procurement_id):
        record = self.fetch_procurement(procurement_id)

        if record is None:
            return False, f"Procurement record not found: {procurement_id}"

        self.procurement_records.remove(record)
        return True, None

    def fetch_procurement_history(self, procurement_id):
        return[
            record
            for record in self.procurement_history
            if record["procurement_id"] == procurement_id
        ]

class FakeInventoryRecord:
    def __init__(self, item_id, item_name):
        self.item_id = item_id
        self.item_name = item_name

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "item_name": self.item_name
        }

def test_add_inventory_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    record = FakeInventoryRecord(
        "INV001",
        "Pressure Sensor"
    )

    success, error = data_manager.add_inventory_record(record)

    assert success is True
    assert error is None
    assert len(repository.inventory_records) == 1
    assert repository.inventory_records[0]["item_id"] == "INV001"

def  test_add_duplicate_inventory_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    first_record = FakeInventoryRecord(
        "INVOO1",
        "Pressure Sensor"
    )

    duplicate_record = FakeInventoryRecord(
        "INV001",
        "Another Sensor"
    )

    data_manager.add_inventory_record(first_record)

    success, error = data_manager.add_inventory_record(duplicate_record)

    assert success is False
    assert error == "Duplicate ID: INV001"
    assert len(repository.inventory_records) == 1

def test_get_inventory_records():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    repository.inventory_records = [
        {
            "item_id": "INV001",
            "item_name": "Pressure Sensor",
            "current_stock": 10,
            "weekly_usage": 5,
            "lead_time_weeks": 2,
            "operational_notes": "Critical equipment"
        },
        {
            "item_id": "INV002",
            "item_name": "Printer Ribbonr",
            "current_stock": 20,
            "weekly_usage": 4,
            "lead_time_weeks": 1,
            "operational_notes": "Normal usage"
        }
    ]

    records = data_manager.get_inventory_record()

    assert len(records) == 2
    assert records[0].item_id == "INV001"
    assert records[1].item_id == "INV002"

def test_get_inventory_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)
    
    repository.inventory_records = [
        {
            "item_id": "INV001",
            "item_name": "Pressure Sensor",
            "current_stock": 10,
            "weekly_usage": 5,
            "lead_time_weeks": 2,
            "operational_notes": "Critical equipment"
        }
    ]

    record = data_manager.get_inventory_record("INV001")

    assert record is not None
    assert record.item_id == "INV001"
    assert record.item_name == "Pressure Sensor"

def test_remove_inventory_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    repository.inventory_records = [
        {
            "item_id": "INV001",
            "item_name": "Pressure Sensor",
            "current_stock": 10,
            "weekly_usage": 5,
            "lead_time_weeks": 2,
            "operational_notes": "Critical equipment"
        }
    ]

    success, error = data_manager.remove_inventory_record("INV001")

    assert success is True
    assert error is None
    assert len(repository.inventory_records) == 0

class FakeProcurementDecision:
    def _init_(self, item_id, recommended_quantity, priority, action):
        self.procurement_id = None
        self.item_id = item_id
        self.recommended_quantity = recommended_quantity
        self.priority = priority
        self.action = action
        self.approval_status = None
        self.rejection_reason = None
        self.timestamp = None
        self.status_updated = None

    def to_dict(self):
        return {
            "procurement_id": self.procurement_id,
            "item_id": self.item_id,
            "recommended_quantity": self.recommended_quantity,
            "priority": self.priority,
            "action": self.action,
            "approval_status": self.approval_status,
            "rejection_reason": self.rejection_reason,
            "timestamp": self.timestamp,
            "status_updated": self.status_updated
        }
def test_create_procurement_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    decision = FakeProcurementDecision(
        "INV001",
        20,
        "HIGH",
        "ORDER"
    )

    success, error = data_manager.create_procurement_record(decision)

    assert success is True
    assert error is None
    assert len(repository.procurement_records) == 1

    saved_record = repository.procurement_records[0]

    assert saved_record["procurement_id"].startswith("PROC-")
    assert saved_record["item_id"] == "INV001"
    assert saved_record["approval_status"] == "PENDING"
    assert saved_record["timestamp"] is not None

def test_update_procurement_status():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    repository.procurement_records = [
        {
            "procurement_id": "PROC-12345678",
            "item_id": "INV001",
            "recommended_quantity": 20,
            "priority": "HIGH",
            "action": "ORDER",
            "approval_status": "PENDING",
            "rejection_reason": None,
            "timestamp": "2026-11-10T10:00:00",
            "status_updated": None
        }
    ]

    success, error = data_manager.update_procurement_status(
        "PROC-12345678",
        "APPROVED"
    )

    assert success is True
    assert error is None

    record = repository.procurement_records[0]

    assert record["approval_status"] == "APPROVED"
    assert record["status_updated"] is not None

def test_reject_procurement_with_reason():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    repository.procurement_records = [
        {
            "procurement_id": "PROC-12345678",
            "item_id": "INV001",
            "recommended_quantity": 20,
            "priority": "HIGH",
            "action": "ORDER",
            "approval_status": "PENDING",
            "rejection_reason": None,
            "timestamp": "2026-11-10T10:00:00",
            "status_updated": None          
        }
    ]

    success, error = data_manager.update_procurement_status(
        "PROC-12345678",
        "REJECTED",
        "Budget exceeded"
    )

    assert success is True
    assert error is None

    record = repository.procurement_records[0]

    assert record["approval_status"] == "REJECTED"
    assert record["rejection_reason"] == "Budget exceeded"

def test_reject_procurement_with_reason():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    success, error = data_manager.update_procurement_status(
        "PROC-12345678",
        "REJECTED"
    )

    assert success is False
    assert error == "Rejection reason is required."

def test_delete_procurement_record():
    repository = FakeRepository()
    data_manager = DataManager(repository)
    
    repository.procurement_records = [
        {
            "procurement_id": "PROC-12345678",
            "item_id": "INV001",
            "recommended_quantity": 20,
            "priority": "HIGH",
            "action": "ORDER",
            "approval_status": "PENDING",
            "rejection_reason": None,
            "timestamp": "2026-11-10T10:00:00",
            "status_updated": None          
        }
    ]

    success, error = data_manager.delete_procurement_record(
        "PROC-12345678"
    )

    assert success is True
    assert error is None
    assert len(repository.procurement_records) == 0

def test_get_procurement_history():
    repository = FakeRepository()
    data_manager = DataManager(repository)

    repository.procurement_history = [
        {
            "procurement_id": "PROC-12345678",
            "previous_status": "PENDING",
            "new_status": "APPROVED",
            "reason": None,
            "changed_at": "2026-11-10T11:00:00"
        },
        {
            "procurement_id": "PROC-999999999",
            "previous_status": "PENDING",
            "new_status": "REJECTED",
            "reason": "Too expensive",
            "changed_at": "2026-11-10T12:00:00"
        }
    ]

    history = data_manager.get_procurement_history(
        "PROC-12345678"
    )

    assert len(history) == 1
    assert history[0]["procurement_id"] == "PROC-12345678"
    assert history[0]["previous_status"] == "PENDING"
    assert history[0]["new_status"] == "APPROVED"
