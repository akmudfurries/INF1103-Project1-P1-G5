


def build_inventory_record(
    item_id,
    item_name,
    current_stock,
    weekly_usage,
    lead_time_weeks,
    operational_notes
    ):
    
    record = {
        "item_id": item_id,
        "item_name": item_name,
        "current_stock": current_stock,
        "weekly_usage": weekly_usage,
        "lead_time_weeks": lead_time_weeks,
        "operational_notes": operational_notes
    }

    validate_inventory_record(record)

    return record

def validate_inventory_record(record):
    required_fields = ["item_id", "item_name", "current_stock", "weekly_usage", "lead_time_weeks", "operational_notes"]

    if not isinstance(record, dict):
        raise ValueError("Inventory record must be a dictionary.")

    for field in required_fields:
        if field not in record:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(record["item_id"], str) or not record["item_id"].strip():
        raise ValueError("item_id must be a non-empty string.")

    if not isinstance(record["item_name"], str) or not record["item_name"].strip():
        raise ValueError("item_name must be a non-empty string.")

    if not isinstance(record["current_stock"], int) or isinstance(record["current_stock"], bool):
        raise ValueError("current_stock must be an integer.")

    if record["current_stock"] < 0:
        raise ValueError("current_stock cannot be negative.")

    if not isinstance(record["weekly_usage"], (int, float)) or isinstance(record["weekly_usage"], bool):
        raise ValueError("weekly_usage must be a number.")

    if record["weekly_usage"] < 0:
        raise ValueError("weekly_usage cannot be negative.")

    if not isinstance(record["lead_time_weeks"], int) or isinstance(record["lead_time_weeks"], bool):
        raise ValueError("lead_time_weeks must be an integer.")

    if record["lead_time_weeks"] < 0:
        raise ValueError("lead_time_weeks cannot be negative.")

    if not isinstance(record["operational_notes"], str):
        raise ValueError("operational_notes must be a string.")

    return True 

def build_procurement_record(
    item_id,
    recommended_quantity,
    priority,
    action
):
    record = {
        "item_id": item_id,
        "recommended_quantity": recommended_quantity,
        "priority": priority,
        "action": action
    }

    validate_procurement_record(record)

    return record

def validate_procurement_record(record):
    required_fields = ["item_id", "recommended_quantity", "priority", "action"]

    if not isinstance(record, dict):
        raise ValueError("Procurement record must be a dictionary.")

    for field in required_fields:
        if field not in record:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(record["item_id"], str) or not record["item_id"].strip():
        raise ValueError("item_id must be a non-empty string.")

    if not isinstance(record["recommended_quantity"], int) \
            or isinstance(record["recommended_quantity"], bool):
        raise ValueError("recommended_quantity must be an integer.")

    if record["recommended_quantity"] < 0:
        raise ValueError("recommended_quantity cannot be negative.")

    if not isinstance(record["priority"], str) or not record["priority"].strip():
        raise ValueError("priority must be a non-empty string.")

    if not isinstance(record["action"], str) or not record["action"].strip():
        raise ValueError("action must be a non-empty string.")

    return True

def find_record_by_id(records, record_id, id_field):
    for record in records:
        if record.get(id_field) == record_id:
            return record
    return None