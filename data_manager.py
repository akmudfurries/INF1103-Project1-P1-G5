


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
    action,
    approval_status,
    rejection_reason=None
):
    record = {
        "item_id": item_id,
        "recommended_quantity": recommended_quantity,
        "priority": priority,
        "action": action,
        "approval_status": approval_status,
        "rejection_reason": rejection_reason
    }

    validate_procurement_record(record)

    return record

def validate_procurement_record(record):
    required_fields = [
        "item_id", 
        "recommended_quantity", 
        "priority", 
        "action", 
        "approval_status",
    ]

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

    valid_statuses = {"PENDING", "APPROVED", "REJECTED"}

    if record["approval_status"] not in valid_statuses:
        raise ValueError(
            f"approval_status must be one of {sorted(valid_statuses)}."
        )

    rejection_reason = record.get("rejection_reason")

    if rejection_reason is not None and not isinstance(rejection_reason, str):
        raise ValueError("rejection_reason must be a string or None.")

    if record["approval_status"] == "REJECTED":
        if not rejection_reason or not rejection_reason.strip():
            raise ValueError("A rejection reason is required when status is REJECTED.")

    elif rejection_reason is not None:
        raise ValueError(
            "rejection_reason must be None unless status is REJECTED."
        )
    
    return True

def find_record_by_id(records, record_id, id_field):
    for record in records:
        if record.get(id_field) == record_id:
            return record
    return None

def add_record(records, record, id_field):
    record_id = record.get(id_field)

    if not record_id:
        return False, "Record is missing its ID."

    if find_record_by_id(records, record_id, id_field):
        return False, f"Duplicate ID: {record_id}"

    records.append(record)

    return True, None

def update_record(records, record_id, updates, id_field):
    record = find_record_by_id(records, record_id, id_field)

    if record is None:
        return False, f"Record not found: {record_id}"

    if id_field in updates and updates[id_field] !=  record_id:
        return False, "Record ID cannot be changed."

    record.update(updates)

    return True, None

def update_procurement_record(records, item_id, updates):
    record = find_record_by_id(records, item_id, "item_id")

    if record is None:
        return False, f"Record not found: {item_id}"

    if "item_id" in updates and updates["item_id"] != item_id:
        return False, "Record ID cannot be changed."

    updated_record = record.copy()
    updated_record.update(updates)

    try:
        validate_procurement_record(updated_record)
    except ValueError as error:
        return False, str(error)

    record.update(updates)

    return True, None

def link_procurement_to_item(procurement_record, inventory_records):
    item_id = procurement_record.get("item_id")

    if find_record_by_id(inventory_records, item_id, "item_id"):
        return True, None

    return False, f"Inventory item not found: {item_id}"

def get_records_for_item(records, item_id):
    matching_records = []

    for record in records:
        if record.get("item_id") == item_id:
            matching_records.append(record)
    
    return matching_records

def create_procurement_from_business_rule(item_id, business_rule_output, approval_status, rejection_reason=None):
    return build_procurement_record(
        item_id,
        business_rule_output["recommended_quantity"],
        business_rule_output["priority"],
        business_rule_output["action"],
        approval_status,
        rejection_reason
    )